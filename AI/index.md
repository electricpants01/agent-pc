# Agent-PC — AI Agent Documentation

Structured documentation for AI agents (Cline, Cursor, Copilot, etc.) to quickly understand the project.

## Index

| File | Content |
|------|---------|
| [`architecture.md`](architecture.md) | Complete system architecture, diagrams, data flow, components, security |
| [`development.md`](development.md) | Development guide: project structure, stack, commands, how to add tools |
| [`deployment.md`](deployment.md) | Deployment guide: requirements, step-by-step setup, backup, troubleshooting |
| [`conventions.md`](conventions.md) | Conventions: languages, code style, Docker, git, file naming |

## Agent Rules

| Folder | Audience |
|--------|----------|
| [`.clinerules/`](../.clinerules/) | Cline (VS Code extension) |
| [`.cursor/rules/`](../.cursor/rules/) | Cursor IDE |

## Recommended Reading Order for a New Agent

1. **`architecture.md`** — Understand what the system does and how
2. **`development.md`** — Know where everything lives
3. **`conventions.md`** — Follow the project rules
4. **`deployment.md`** — Get it running

## TL;DR

- **Agent-PC** = control Linux remotely via conversational AI
- **Open WebUI** (Docker, port 3000) = multi-model brain + PWA interface
- **Agent-PC Server** (Docker, port 8765) = tool executor (NO LLM)
- **Tailscale Serve** (host-native) = HTTPS VPN for iPhone access via `tailscale serve`
- **Notes Prompt** = `open-webui/notes-prompt.md` — perpetual AI context (like `.cursorrules` for Open WebUI)
- **Tools** = execute_command, read_file, write_file, list_directory, search_files
- **Tool files** = `open-webui/tools/agent-pc-tools.json` (JSON import) + `agent-pc-tools.py` (Python function import)
- **Auth** = AUTH_SECRET shared between Open WebUI and Agent-PC
- **Code** = Python 3.11 + FastAPI, English for code, English for comments
