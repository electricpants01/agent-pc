# ============================================
# Agent-PC Server — Tool Execution Engine
# ============================================
"""
Minimal server that exposes tools for Open WebUI.
Open WebUI handles all LLM logic (chat, streaming, multi-model).
Agent-PC only executes tools on the host machine.

Endpoints:
  - GET  /health           → health check
  - GET  /tools            → list tools (OpenAI format)
  - POST /tool             → execute a tool
"""
import json
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import config
from tools import TOOL_DEFINITIONS, execute_tool


# ---- Pydantic models ----
class ToolExecuteRequest(BaseModel):
    """Request to execute a tool."""
    name: str
    args: dict = {}


# ---- Auth helper ----
def auth_check(secret: str):
    if secret != config.AUTH_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret.")


# ---- App ----
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Agent-PC Tool Engine started on {config.SERVER_HOST}:{config.SERVER_PORT}")
    print(f"   Workspace : {config.WORKSPACE_ROOT}")
    print(f"   SSH Host  : {config.SSH_HOST}:{config.SSH_PORT}")
    print(f"   Tools: {', '.join(t['function']['name'] for t in TOOL_DEFINITIONS)}")
    yield
    print("Agent-PC Server stopped.")


app = FastAPI(title="Agent-PC Tool Engine", version="2.0.0", lifespan=lifespan)


# ---- REST endpoints ----
@app.get("/health")
async def health():
    """Health check for Docker and monitoring."""
    return {
        "status": "ok",
        "timestamp": time.time(),
        "tools_available": len(TOOL_DEFINITIONS),
    }


@app.get("/tools")
async def list_tools(secret: str = ""):
    """List tools in OpenAI function-calling format.
    Open WebUI can import these definitions."""
    auth_check(secret)
    return {"tools": TOOL_DEFINITIONS}


@app.post("/tool")
async def call_tool(req: ToolExecuteRequest, secret: str = ""):
    """Execute a tool. Open WebUI calls this endpoint
    when the LLM decides to use a function."""
    auth_check(secret)
    print(f"Tool: {req.name}({json.dumps(req.args, ensure_ascii=False)[:100]})")
    result = execute_tool(req.name, req.args)
    return result


# ---- CLI entry point ----
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        log_level="info",
    )
