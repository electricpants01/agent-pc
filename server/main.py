# ============================================
# Agent-PC Server — Tool Execution Engine 🛠️
# ============================================
"""
Servidor simplificado que expone herramientas para Open WebUI.
Open WebUI maneja todo el LLM (chat, streaming, multi-modelo).
Agent-PC solo ejecuta herramientas en la máquina host.

Endpoints:
  - GET  /health           → health check
  - GET  /tools            → lista herramientas (OpenAI format)
  - POST /tool             → ejecutar una herramienta
  - GET  /openapi.json     → OpenAPI spec para Open WebUI Tools
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
    """Request para ejecutar una herramienta."""
    name: str
    args: dict = {}


# ---- Auth helper ----
def auth_check(secret: str):
    if secret != config.AUTH_SECRET:
        raise HTTPException(status_code=403, detail="Secreto inválido.")


# ---- App ----
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Agent-PC Tool Engine iniciado en {config.SERVER_HOST}:{config.SERVER_PORT}")
    print(f"   Workspace : {config.WORKSPACE_ROOT}")
    print(f"   SSH Host  : {config.SSH_HOST}:{config.SSH_PORT}")
    print(f"   Herramientas: {', '.join(t['function']['name'] for t in TOOL_DEFINITIONS)}")
    yield
    print("👋 Agent-PC Server detenido.")


app = FastAPI(title="Agent-PC Tool Engine", version="2.0.0", lifespan=lifespan)


# ---- REST endpoints ----
@app.get("/health")
async def health():
    """Health check para Docker y monitoreo."""
    return {
        "status": "ok",
        "timestamp": time.time(),
        "tools_available": len(TOOL_DEFINITIONS),
    }


@app.get("/tools")
async def list_tools(secret: str = ""):
    """Listar herramientas en formato OpenAI function-calling.
    Open WebUI puede importar estas definiciones."""
    auth_check(secret)
    return {"tools": TOOL_DEFINITIONS}


@app.post("/tool")
async def call_tool(req: ToolExecuteRequest, secret: str = ""):
    """Ejecutar una herramienta. Open WebUI llama este endpoint
    cuando el LLM decide usar una función."""
    auth_check(secret)
    print(f"🔧 Tool: {req.name}({json.dumps(req.args, ensure_ascii=False)[:100]})")
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
