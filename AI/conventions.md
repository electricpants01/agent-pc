# Agent-PC — Project Conventions

## Language

- **Code:** English (variables, functions, classes)
- **Comments and docstrings:** English
- **Documentation:** English
- **Commits:** English (conventional commits)

## Python

### Style
- PEP 8 (4 spaces, snake_case, PascalCase for classes)
- Type hints where they add clarity
- Google-style docstrings

### Tools
- Each tool returns dict with `{"ok": bool, ...}`
- Errors: `{"ok": false, "error": "description"}`
- Synchronous functions (FastAPI runs them in thread pool)

### Configuration
- Environment variables via `python-dotenv`
- `.env` file is NOT committed (in `.gitignore`)
- `.env.example` and `.env.docker` as templates

## Docker

- Images based on `python:3.11-slim-bookworm`
- Non-root user (`agentpc`) in containers
- Health checks on all services
- Volumes with explicit names (`agent-pc-*`)
- Dedicated bridge network (`agent-pc-network`)

## Open WebUI

- Tools in `open-webui/tools/` in JSON format
- API keys configured from admin panel (never in files)
- Functions use HTTP POST to `http://agent-pc:8765/tool`

## Git

### Branches
- `main` — production
- `dev` — development
- `feat/<name>` — new features

### Commits (Conventional Commits)
```
feat: add tool for process management
fix: fix timeout in execute_command
docs: update README with new architecture
refactor: simplify main.py
chore: update dependencies
```

## File Naming

- `docker-compose.yml` — orchestration
- `.env.docker` — Docker env template
- `Dockerfile` — container image
- `entrypoint.sh` — startup script
- `tools.py` — tool definitions
- `config.py` — configuration
- `main.py` — FastAPI entry point
