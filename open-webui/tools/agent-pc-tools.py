"""
title: Agent-PC Tools
author: Agent-PC
version: 1.0.0
description: |
  Tools for controlling the Linux host machine.
  Connects to the Agent-PC Tool Engine via HTTP.
  Supports: execute_command, read_file, write_file, list_directory, search_files.
"""

import json

import requests

AGENT_PC_URL = "http://agent-pc:8765"
AUTH_SECRET = "58d3aa9867a181ef1627a7ab23770075"


def _call_agent_pc(tool_name: str, args: dict) -> dict:
    """Forward a tool call to the Agent-PC server and return the result."""
    try:
        response = requests.post(
            f"{AGENT_PC_URL}/tool",
            params={"secret": AUTH_SECRET},
            json={"name": tool_name, "args": args},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"ok": False, "error": "Agent-PC server unreachable. Is it running?"}
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Agent-PC server timed out."}
    except Exception as e:
        return {"ok": False, "error": str(e)}


class Tools:
    async def execute_command(
        self,
        command: str,
        timeout: int = 30,
        __event_emitter__=None,
    ) -> str:
        """
        Execute a shell command on the Linux host machine.
        Use for system operations like checking disk space, listing processes,
        installing packages, etc.

        :param command: The shell command to execute (e.g. 'df -h', 'ls -la /home', 'ps aux')
        :param timeout: Timeout in seconds (default: 30, max: 120)
        :return: JSON string with stdout, stderr, and return code.
        """
        result = _call_agent_pc("execute_command", {"command": command, "timeout": timeout})
        return json.dumps(result)

    async def read_file(
        self,
        path: str,
        start_line: int = None,
        end_line: int = None,
        __event_emitter__=None,
    ) -> str:
        """
        Read the contents of a file from the host.
        For large files, specify start_line and end_line.

        :param path: Absolute path of the file to read (e.g. '/home/user/project/main.py')
        :param start_line: Starting line (1-based, optional)
        :param end_line: Ending line (1-based, optional)
        :return: JSON string with the file content.
        """
        args = {"path": path}
        if start_line is not None:
            args["start_line"] = start_line
        if end_line is not None:
            args["end_line"] = end_line
        result = _call_agent_pc("read_file", args)
        return json.dumps(result)

    async def write_file(
        self,
        path: str,
        content: str,
        __event_emitter__=None,
    ) -> str:
        """
        Write or create a file on the host. Creates parent directories if they don't exist.

        :param path: Absolute path of the file to write
        :param content: Content to write to the file
        :return: JSON string confirming the write operation.
        """
        result = _call_agent_pc("write_file", {"path": path, "content": content})
        return json.dumps(result)

    async def list_directory(
        self,
        path: str,
        pattern: str = None,
        __event_emitter__=None,
    ) -> str:
        """
        List the contents of a directory on the host.

        :param path: Absolute path of the directory to list
        :param pattern: Optional glob pattern (e.g. '*.py', '*.md')
        :return: JSON string with directory listing.
        """
        args = {"path": path}
        if pattern is not None:
            args["pattern"] = pattern
        result = _call_agent_pc("list_directory", args)
        return json.dumps(result)

    async def search_files(
        self,
        pattern: str,
        directory: str = None,
        file_pattern: str = None,
        __event_emitter__=None,
    ) -> str:
        """
        Search for files containing a text pattern (uses grep).

        :param pattern: Regex pattern or text to search for
        :param directory: Directory to search in (default: workspace root)
        :param file_pattern: File filter (e.g. '*.py', '*.md')
        :return: JSON string with matching lines.
        """
        args = {"pattern": pattern}
        if directory is not None:
            args["directory"] = directory
        if file_pattern is not None:
            args["file_pattern"] = file_pattern
        result = _call_agent_pc("search_files", args)
        return json.dumps(result)
