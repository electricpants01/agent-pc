# ============================================
# Agent-PC Server Configuration
# ============================================
# Tool execution engine — no LLM client.
# Open WebUI handles all LLM logic.
# ============================================
import os
from dotenv import load_dotenv

load_dotenv()

# --- Server ---
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8765"))

# --- Workspace ---
# Root directory the agent is allowed to operate in
WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", os.path.expanduser("~"))

# --- Security ---
# Shared secret for authentication between Open WebUI and Agent-PC
AUTH_SECRET = os.getenv("AUTH_SECRET", "agent-pc-local-secret-change-me")

# --- SSH (for executing commands on the real host) ---
SSH_HOST = os.getenv("SSH_HOST", "host.docker.internal")
SSH_PORT = int(os.getenv("SSH_PORT", "22"))
SSH_USER = os.getenv("SSH_USER", os.environ.get("USER", "root"))
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", os.path.expanduser("~/.ssh/id_rsa"))
# Fall back to local execution if SSH is unavailable
FALLBACK_TO_LOCAL = os.getenv("FALLBACK_TO_LOCAL", "true").lower() == "true"
