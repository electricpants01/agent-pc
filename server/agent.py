# ============================================
# AI Agent — LLM loop with tool calling
# ============================================
import json
from typing import AsyncGenerator

from openai import AsyncOpenAI

import config
from tools import SYSTEM_PROMPT, TOOL_DEFINITIONS, execute_tool

# Build the OpenAI-compatible client once
_llm_cfg = config.get_llm_config()
_client = AsyncOpenAI(
    api_key=_llm_cfg["api_key"],
    base_url=_llm_cfg["base_url"],
)

MODEL = _llm_cfg["model"]
MAX_TOOL_ROUNDS = 10  # safety limit


def _build_messages(user_text: str, history: list[dict] = None) -> list[dict]:
    """Build the message list for the LLM call."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_text})
    return messages


async def run_agent_stream(
    user_text: str, history: list[dict] = None
) -> AsyncGenerator[str, None]:
    """
    Run the AI agent loop with streaming.
    Yields SSE-style events:
      - "text: ..." for streamed text chunks
      - "tool: <json>" when a tool is being called
      - "tool_result: <json>" when a tool result is available
      - "error: ..." on errors
      - "[DONE]" when complete
    """
    messages = _build_messages(user_text, history)
    rounds = 0

    while rounds < MAX_TOOL_ROUNDS:
        rounds += 1
        try:
            stream = await _client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                stream=True,
            )

            # --- Accumulate the assistant response & detect tool calls ---
            full_content = ""
            tool_calls_acc: dict[int, dict] = {}  # index -> {id, name, args_str}

            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta is None:
                    continue

                # Text
                if delta.content:
                    full_content += delta.content
                    yield f"text: {delta.content}"

                # Tool calls (streamed as fragments; accumulate)
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_acc:
                            tool_calls_acc[idx] = {
                                "id": tc.id or "",
                                "name": "",
                                "args_str": "",
                            }
                        if tc.id:
                            tool_calls_acc[idx]["id"] = tc.id
                        if tc.function:
                            if tc.function.name:
                                tool_calls_acc[idx]["name"] = tc.function.name
                            if tc.function.arguments:
                                tool_calls_acc[idx]["args_str"] += tc.function.arguments

            # --- If the assistant produced tool calls, execute them ---
            if tool_calls_acc:
                # Add assistant message with tool_calls to history
                assistant_msg = {"role": "assistant", "content": full_content or None}
                tc_list = []
                for idx in sorted(tool_calls_acc.keys()):
                    tc = tool_calls_acc[idx]
                    tc_list.append({
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": tc["args_str"],
                        },
                    })
                assistant_msg["tool_calls"] = tc_list
                messages.append(assistant_msg)

                # Execute each tool and yield results
                for idx in sorted(tool_calls_acc.keys()):
                    tc = tool_calls_acc[idx]
                    tool_info = json.dumps({
                        "id": tc["id"],
                        "name": tc["name"],
                        "arguments": tc["args_str"],
                    })
                    yield f"tool: {tool_info}"

                    try:
                        args = json.loads(tc["args_str"]) if tc["args_str"].strip() else {}
                    except json.JSONDecodeError:
                        args = {}
                    result = execute_tool(tc["name"], args)
                    result_json = json.dumps(result, ensure_ascii=False)
                    yield f"tool_result: {result_json}"

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result_json,
                    })

                # Continue the loop — the LLM will process the tool results
                continue

            # --- No tool calls → final response, done ---
            # Append the assistant message
            messages.append({"role": "assistant", "content": full_content})
            yield "[DONE]"
            return

        except Exception as e:
            yield f"error: {str(e)}"
            yield "[DONE]"
            return

    # Safety limit reached
    yield "error: Demasiadas rondas de herramientas. Posible loop."
    yield "[DONE]"
