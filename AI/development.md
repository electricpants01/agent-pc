# Agent-PC — Development Guide

## Project Structure

```
agent-pc/
├── docker-compose.yml           ← Service orchestration
├── .env.docker                  ← Docker environment variables
├── docker/
│   └── agent-pc/
│       ├── Dockerfile           ← Python image for tool engine
│       └── entrypoint.sh        ← Startup script
├── server/                      ← Agent-PC Server (Python)
│   ├── main.py                  ← FastAPI app (3 endpoints)
│   ├── tools.py                 ← Tool definitions + implementations
│   ├── config.py                ← Env var configuration
│   ├── requirements.txt         ← Python dependencies
│   ├── .env.example             ← Config template
│   ├── agent.py                 ← [LEGACY] LLM client (no longer used)
│   ├── setup.sh                 ← [LEGACY] Non-Docker install
│   └── agent-pc.service         ← [LEGACY] systemd service
├── open-webui/
│   ├── notes-prompt.md          ← Notes prompt template (AI context for Open WebUI)
│   └── tools/
│       ├── agent-pc-tools.json  ← Tool definitions (JSON import)
│       └── agent-pc-tools.py   ← Tool functions (Python import, preferred)
├── ios/                         ← [LEGACY] SwiftUI iOS app (backup)
├── AI/                          ← AI agent documentation
│   ├── index.md
│   ├── architecture.md
│   ├── development.md
│   ├── deployment.md
│   └── conventions.md
├── .clinerules/                 ← Cline rules
├── .cursor/rules/               ← Cursor IDE rules
└── README.md                    ← Main documentation
```

## Tech Stack

| Component | Technology | Version |
|------------|-----------|--------|
| Containers | Docker + Docker Compose | 3.9+ |
| LLM Brain | Open WebUI | latest (main) |
| Tool Engine | Python + FastAPI | 3.11, 0.115.6 |
| SSH | asyncssh | 2.19.0 |
| HTTP client | httpx | 0.28.1 |
| VPN | Tailscale Serve (host-native, WireGuard) | latest |
| Local models | Ollama | latest |
| Client | PWA (Web Speech API) | Modern browser |

## Useful Commands

### Local Development

```bash
# Install dependencies
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run server in development
cp .env.example .env
python main.py

# Test endpoints
curl http://localhost:8765/health
curl "http://localhost:8765/tools?secret=agent-pc-local-secret-change-me"
curl -X POST "http://localhost:8765/tool?secret=agent-pc-local-secret-change-me" \
  -H "Content-Type: application/json" \
  -d '{"name": "execute_command", "args": {"command": "echo hello"}}'
```

### Docker

```bash
# Build and start
docker compose up -d --build

# Just agent-pc (for quick dev)
docker compose up -d agent-pc

# View logs
docker compose logs -f agent-pc
docker compose logs -f open-webui

# Rebuild after changes
docker compose build agent-pc
docker compose up -d --force-recreate agent-pc

# Stop everything
docker compose down

# With Ollama profile
docker compose --profile ollama up -d

# Clean volumes
docker compose down -v
```

## Adding New Tools

1. Define schema in `server/tools.py` → `TOOL_DEFINITIONS`
2. Implement `tool_<name>()` function
3. Register in `TOOL_MAP`
4. Add to `open-webui/tools/agent-pc-tools.json` (JSON import)
5. Add to `open-webui/tools/agent-pc-tools.py` (Python function import, preferred)
6. Rebuild: `docker compose build agent-pc && docker compose up -d`
7. Re-import tools in Open WebUI Admin Panel

## Code Conventions

- **Language:** English for code, docstrings, and comments
- **Python:** PEP 8, type hints where useful
- **Tools:** Each tool returns `{"ok": bool, ...}`
- **Errors:** `{"ok": false, "error": "message"}`
- **Streaming:** No longer used in Agent-PC (Open WebUI handles it)

## Known Issues / Tech Debt

These items exist in the current codebase and should be addressed:

| # | Issue | Location | Action |
|---|-------|----------|--------|
| 1 | **Hardcoded AUTH_SECRET** | `open-webui/tools/agent-pc-tools.py:16` | Replace with `os.getenv("AUTH_SECRET")` |
| 2 | **Spanish comments/strings** | `server/requirements.txt` (lines 2-4), `server/agent.py` (line 148), `server/setup.sh` (multiple) | Translate all to English per convention |
| 3 | **Legacy agent.py still exists** | `server/agent.py` | Remove or fully isolate; currently imports `openai` which violates "NO openai library" rule |
| 4 | **Legacy setup.sh / service files** | `server/setup.sh`, `server/agent-pc.service` | Either remove (Docker is the only install method) or update to English |
| 5 | **Workspace bind mount** | `docker-compose.yml:58` | Uses host bind mount (`${WORKSPACE_ROOT}`) for workspace — this is intentional for SSH access but diverges from the "named volumes only" rule for data volumes |

### Priority
1. **P0 — Security:** Fix hardcoded AUTH_SECRET (#1) — secrets in source code are a leak risk
2. **P1 — Cleanup:** Remove or isolate `agent.py` (#3) — violates architectural rules
3. **P2 — Convention:** Translate Spanish to English (#2, #4)
