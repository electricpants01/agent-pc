# Agent-PC — Cline Rules

## Project Identity

- **Name:** Agent-PC
- **Type:** AI-powered remote Linux control system
- **Language:** Python 3.11 (server), Docker Compose (orchestration)
- **Framework:** FastAPI (tool engine), Open WebUI (LLM brain)

## Architecture Rules

1. Agent-PC server is a **TOOL EXECUTION ENGINE ONLY** — no LLM client, no chat endpoints
2. Open WebUI handles ALL LLM logic (chat, streaming, multi-model, tool calling)
3. Communication: Open WebUI → HTTP POST → Agent-PC `/tool` endpoint
4. Authentication between services: `AUTH_SECRET` shared secret via query param
5. SSH from container to host for command execution (with local fallback)

## Code Conventions

- **Variables/functions/classes:** English
- **Comments/docstrings:** Spanish
- **PEP 8** with 4-space indentation
- Type hints where they add clarity
- Tool functions return `{"ok": bool, ...}` dict
- Errors return `{"ok": false, "error": "message"}`

## File Locations

- `server/main.py` — FastAPI app (3 endpoints: health, tools, tool)
- `server/tools.py` — Tool definitions + implementations
- `server/config.py` — Environment variable configuration
- `docker-compose.yml` — Service orchestration
- `docker/agent-pc/Dockerfile` — Container image
- `open-webui/tools/` — Open WebUI function definitions
- `AI/` — Project documentation for AI agents
- `ios/` — Legacy SwiftUI app (not actively maintained)

## Key Constraints

- **NO** `openai` library in server — removed in v2.0
- **NO** WebSocket or chat endpoints in Agent-PC server
- **NO** hardcoded API keys — use env vars or Open WebUI admin panel
- **NO** direct `subprocess` from container to host without SSH as option
- Docker volumes MUST use named volumes (not bind mounts for data)

## When Adding Features

1. New tools: add to `TOOL_DEFINITIONS` + `TOOL_MAP` in `tools.py`
2. Update `open-webui/tools/agent-pc-tools.json`
3. Rebuild: `docker compose build agent-pc && docker compose up -d`
4. Re-import tools in Open WebUI admin panel

## When Modifying Docker

1. Update `docker-compose.yml` for service changes
2. Update `docker/agent-pc/Dockerfile` for dependencies
3. Update `.env.docker` for new variables
4. Test: `docker compose up -d --build`
5. Verify health: `curl http://localhost:8765/health`

## Testing

```bash
# Local testing (no Docker)
cd server && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && python main.py

# Test endpoints
curl http://localhost:8765/health
curl "http://localhost:8765/tools?secret=agent-pc-local-secret-change-me"
curl -X POST "http://localhost:8765/tool?secret=agent-pc-local-secret-change-me" \
  -H "Content-Type: application/json" \
  -d '{"name":"execute_command","args":{"command":"echo test"}}'
```
