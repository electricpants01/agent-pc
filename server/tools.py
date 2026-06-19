# ============================================
# Agent Tools — file ops, shell commands, etc.
# ============================================
# Tools that Open WebUI can call.
# Executed locally inside the container.
# For SSH to host, see config.py.
# ============================================
import os
import subprocess
import glob as globmod
from pathlib import Path
from typing import Any

import config


# ---- Tool Definitions (OpenAI function-calling format) ----
# Open WebUI uses these definitions for tool-calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file. Use start_line/end_line for very large files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path of the file to read.",
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Starting line (1-based, optional).",
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Ending line (1-based, optional).",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or create a file with the specified content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path of the file to write.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a shell command on the Linux host. Use with caution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute (e.g. 'ls -la', 'df -h').",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 30).",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List the contents of a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path of the directory to list.",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Optional glob pattern (e.g. '*.py').",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Search for files containing a text pattern (grep).",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern or text to search for.",
                    },
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in (default: workspace root).",
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "File filter (e.g. '*.py', '*.md').",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
]

SYSTEM_PROMPT = """You are **Agent-PC**, an AI assistant running on a 24/7 Linux machine.
Your purpose is to help the user control their computer remotely from any device.

## Capabilities
- Read any system file (read_file)
- Write/create files (write_file)
- Execute shell commands (execute_command)
- List directories (list_directory)
- Search within files (search_files)

## Rules
1. **Respond in English** — the user speaks English.
2. **Be concise** — this is a remote interface, get to the point.
3. **Confirm before destructive actions** — ask before deleting files, killing processes, etc.
4. **Always use absolute paths**.
5. **The workspace root is {}** — operate within this scope for safety.

## Format
- When executing commands, show what you did and the result.
- If a command fails, explain the error and suggest alternatives.
- For large files, use start_line/end_line.
""".format(config.WORKSPACE_ROOT)


# ---- Tool Implementations ----
def _resolve_path(path: str) -> str:
    """Resolve and validate a path."""
    p = Path(os.path.expanduser(path)).resolve()
    return str(p)


def tool_read_file(path: str, start_line: int = None, end_line: int = None) -> dict:
    """Read a file, optionally with line range."""
    p = _resolve_path(path)
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            if start_line is None and end_line is None:
                content = f.read()
                if len(content) > 50000:
                    lines = content.split("\n")
                    return {
                        "ok": True, "path": p,
                        "content": "\n".join(lines[:500]),
                        "total_lines": len(lines), "truncated": True,
                        "note": f"Truncated to 500 lines. Total: {len(lines)} lines.",
                    }
                return {"ok": True, "path": p, "content": content}
            else:
                lines = f.readlines()
                total = len(lines)
                sl = max(1, start_line or 1) - 1
                el = min(total, end_line or total)
                selected = lines[sl:el]
                return {
                    "ok": True, "path": p,
                    "content": "".join(selected),
                    "total_lines": total, "shown_lines": f"{sl+1}-{el}",
                }
    except FileNotFoundError:
        return {"ok": False, "path": p, "error": "File not found."}
    except PermissionError:
        return {"ok": False, "path": p, "error": "Permission denied."}
    except Exception as e:
        return {"ok": False, "path": p, "error": str(e)}


def tool_write_file(path: str, content: str) -> dict:
    """Write content to a file."""
    p = _resolve_path(path)
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return {"ok": True, "path": p, "bytes_written": len(content)}
    except Exception as e:
        return {"ok": False, "path": p, "error": str(e)}


def tool_execute_command(command: str, timeout: int = 30) -> dict:
    """Execute a shell command."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=config.WORKSPACE_ROOT,
        )
        return {
            "ok": result.returncode == 0,
            "command": command,
            "stdout": result.stdout[-10000:],
            "stderr": result.stderr[-10000:],
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "command": command, "error": f"Timeout after {timeout}s."}
    except Exception as e:
        return {"ok": False, "command": command, "error": str(e)}


def tool_list_directory(path: str, pattern: str = None) -> dict:
    """List directory contents."""
    p = _resolve_path(path)
    try:
        if pattern:
            items = globmod.glob(os.path.join(p, pattern))
            items = [os.path.relpath(i, p) for i in items]
        else:
            items = sorted(os.listdir(p))
        return {"ok": True, "path": p, "items": items[:200], "count": len(items)}
    except FileNotFoundError:
        return {"ok": False, "path": p, "error": "Directory not found."}
    except PermissionError:
        return {"ok": False, "path": p, "error": "Permission denied."}
    except Exception as e:
        return {"ok": False, "path": p, "error": str(e)}


def tool_search_files(pattern: str, directory: str = None, file_pattern: str = None) -> dict:
    """Search for text pattern in files (grep)."""
    d = _resolve_path(directory or config.WORKSPACE_ROOT)
    cmd = ["grep", "-rn"]
    if file_pattern:
        cmd.append(f"--include={file_pattern}")
    cmd.extend([pattern, d])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        lines = result.stdout.strip().split("\n")[:100]
        return {
            "ok": True, "pattern": pattern, "directory": d,
            "matches": lines, "count": len(lines),
        }
    except Exception as e:
        return {"ok": False, "pattern": pattern, "error": str(e)}


# Tool dispatcher
TOOL_MAP = {
    "read_file": tool_read_file,
    "write_file": tool_write_file,
    "execute_command": tool_execute_command,
    "list_directory": tool_list_directory,
    "search_files": tool_search_files,
}


def execute_tool(name: str, args: dict) -> dict:
    """Dispatch a tool call and return its result."""
    fn = TOOL_MAP.get(name)
    if not fn:
        return {"ok": False, "error": f"Unknown tool: {name}"}
    return fn(**args)
