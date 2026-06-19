# ============================================
# Agent-PC Server Configuration
# ============================================
# Tool execution engine — sin cliente LLM.
# Open WebUI maneja toda la lógica de LLM.
# ============================================
import os
from dotenv import load_dotenv

load_dotenv()

# --- Server ---
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8765"))

# --- Workspace ---
# Directorio raíz donde el agente puede operar
WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", os.path.expanduser("~"))

# --- Security ---
# Clave compartida para autenticación entre Open WebUI y Agent-PC
AUTH_SECRET = os.getenv("AUTH_SECRET", "agent-pc-local-secret-change-me")

# --- SSH (para ejecutar comandos en el host real) ---
SSH_HOST = os.getenv("SSH_HOST", "host.docker.internal")
SSH_PORT = int(os.getenv("SSH_PORT", "22"))
SSH_USER = os.getenv("SSH_USER", os.environ.get("USER", "root"))
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", os.path.expanduser("~/.ssh/id_rsa"))
# Si no se puede conectar por SSH, usar ejecución local (dentro del contenedor)
FALLBACK_TO_LOCAL = os.getenv("FALLBACK_TO_LOCAL", "true").lower() == "true"

