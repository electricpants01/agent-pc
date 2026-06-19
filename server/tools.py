# ============================================
# Agent Tools — file ops, shell commands, etc.
# ============================================
# Las herramientas que Open WebUI puede llamar.
# Se ejecutan localmente dentro del contenedor.
# Para SSH al host, consultar config.py.
# ============================================
import os
import subprocess
import glob as globmod
from pathlib import Path
from typing import Any

import config


# ---- Tool Definitions (OpenAI function-calling format) ----
# Open WebUI usa estas definiciones para tool-calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Lee el contenido de un archivo. Usa start_line/end_line para archivos muy largos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta absoluta del archivo a leer.",
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Línea inicial (1-based, opcional).",
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Línea final (1-based, opcional).",
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
            "description": "Escribe o crea un archivo con el contenido especificado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta absoluta del archivo a escribir.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Contenido a escribir en el archivo.",
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
            "description": "Ejecuta un comando de shell en el servidor Linux. Úsalo con cuidado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "El comando shell a ejecutar (ej: 'ls -la', 'df -h').",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout en segundos (default: 30).",
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
            "description": "Lista el contenido de un directorio.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta absoluta del directorio a listar.",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Patrón glob opcional (ej: '*.py').",
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
            "description": "Busca archivos que contengan un patrón de texto (grep).",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Patrón regex o texto a buscar.",
                    },
                    "directory": {
                        "type": "string",
                        "description": "Directorio donde buscar (default: workspace root).",
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Filtro de archivos (ej: '*.py', '*.md').",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
]

SYSTEM_PROMPT = """Eres **Agent-PC**, un asistente de IA ejecutándose en una máquina Linux 24/7.
Tu propósito es ayudar al usuario a controlar su computadora remotamente desde su iPhone.

## Capacidades
- Leer cualquier archivo del sistema (read_file)
- Escribir/crear archivos (write_file)
- Ejecutar comandos de shell (execute_command)
- Listar directorios (list_directory)
- Buscar en archivos (search_files)

## Reglas
1. **Responde en español** — el usuario habla español.
2. **Sé conciso** — es una interfaz móvil, ve al grano.
3. **Confirma antes de acciones destructivas** — pregunta antes de borrar archivos, matar procesos, etc.
4. **Usa rutas absolutas** siempre.
5. **El workspace root es {}** — opera dentro de este scope por seguridad.

## Formato
- Cuando ejecutes comandos, muestra qué hiciste y el resultado.
- Si un comando falla, explica el error y sugiere alternativas.
- Para archivos largos, usa start_line/end_line.
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
                        "note": f"Truncado a 500 lineas. Total: {len(lines)} lineas.",
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
        return {"ok": False, "path": p, "error": "Archivo no encontrado."}
    except PermissionError:
        return {"ok": False, "path": p, "error": "Permiso denegado."}
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
        return {"ok": False, "command": command, "error": f"Timeout tras {timeout}s."}
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
        return {"ok": False, "path": p, "error": "Directorio no encontrado."}
    except PermissionError:
        return {"ok": False, "path": p, "error": "Permiso denegado."}
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
        return {"ok": False, "error": f"Herramienta desconocida: {name}"}
    return fn(**args)

