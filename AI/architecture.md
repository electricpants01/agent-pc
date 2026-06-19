# Agent-PC — System Architecture

## Overview

Agent-PC is a system for controlling a Linux machine remotely using conversational AI from any device (iPhone, iPad, browser). No native apps required — uses Open WebUI as a PWA.

## Architecture Diagram

```
┌──────────────────────┐      Tailscale VPN      ┌──────────────────────────────────────┐
│  ANY DEVICE          │◄──────────────────────►│  Linux Server 24/7 (Docker Host)     │
│                      │    Private mesh net    │                                      │
│ • iPhone (PWA/Safari)│                         │  ┌────────────────────────────────┐  │
│ • iPad               │                         │  │  Open WebUI (port 3000)        │  │
│ • Mac/PC (browser)   │                         │  │  • Multi-model admin panel     │  │
│ • Voice → command    │                         │  │  • OpenAI / Gemini / DeepSeek  │  │
│                      │                         │  │  • Claude / Ollama / etc.      │  │
└──────────────────────┘                         │  │  • OpenAI-compatible API        │  │
                                                 │  │  • Functions / Tools pipeline   │  │
                                                 │  │  • Chat + Voice + Streaming    │  │
                                                 │  └──────────────┬─────────────────┘  │
                                                 │                 │ HTTP               │
                                                 │  ┌──────────────▼─────────────────┐  │
                                                 │  │  Agent-PC (port 8765)          │  │
                                                 │  │  • FastAPI (Python 3.11)       │  │
                                                 │  │  • Tool execution engine       │  │
                                                 │  │  • Endpoints:                  │  │
                                                 │  │    GET  /health                │  │
                                                 │  │    GET  /tools?secret=         │  │
                                                 │  │    POST /tool?secret=          │  │
                                                 │  │  • Auth: shared secret         │  │
                                                 │  └──────────────┬─────────────────┘  │
                                                 │                 │ SSH                │
                                                 │  ┌──────────────▼─────────────────┐  │
                                                 │  │  Host Machine                  │  │
                                                 │  │  • File system (read/write)    │  │
                                                 │  │  • Shell commands              │  │
                                                 │  │  • Directory listing           │  │
                                                 │  │  • File search (grep)          │  │
                                                 │  └────────────────────────────────┘  │
                                                 │                                      │
                                                 │  Optional Services:                  │
                                                 │  ┌────────────────────────────────┐  │
                                                 │  │  Ollama (port 11434)            │  │
                                                 │  │  • Local LLM models             │  │
                                                 │  │  • Full privacy                 │  │
                                                 │  └────────────────────────────────┘  │
                                                 │  ┌────────────────────────────────┐  │
                                                 │  │  Tailscale                      │  │
                                                 │  │  • VPN mesh (WireGuard)        │  │
                                                 │  │  • IPs 100.x.x.x               │  │
                                                 │  └────────────────────────────────┘  │
                                                 └──────────────────────────────────────┘
```

## Data Flow: User Voice → Host Execution

```
1. User speaks to iPhone
   └→ Safari Web Speech API captures voice

2. Text sent to Open WebUI (HTTP POST /api/chat/completions)
   └→ OpenAI-compatible API with Open WebUI API key

3. Open WebUI processes with configured LLM
   └→ LLM decides whether to use tools

4. If tool needed → HTTP POST to Agent-PC (/tool)
   └→ Auth via shared AUTH_SECRET

5. Agent-PC executes locally (container)
   └→ Or via SSH to host if configured

6. Result flows back: Agent-PC → Open WebUI → LLM formulates response
   └→ Natural language response sent to client

7. Safari/iPhone displays text + optionally reads aloud
   └→ Web Speech API
```

## Components

### Open WebUI
- **Image:** `ghcr.io/open-webui/open-webui:main`
- **Role:** Multi-model brain, user interface (PWA), LLM proxy
- **Port:** 3000 → 8080 (internal)
- **Persistence:** Docker volume `open-webui-data`
- **Auth:** Local user accounts + per-provider API keys

### Agent-PC Server (Tool Engine)
- **Image:** Custom Dockerfile (Python 3.11-slim)
- **Role:** Executes tools on the host
- **Port:** 8765
- **Auth:** `AUTH_SECRET` shared via query param

### Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `execute_command` | Execute shell command | `command: str`, `timeout: int?` |
| `read_file` | Read file | `path: str`, `start_line: int?`, `end_line: int?` |
| `write_file` | Write file | `path: str`, `content: str` |
| `list_directory` | List directory | `path: str`, `pattern: str?` |
| `search_files` | Search in files | `pattern: str`, `directory: str?`, `file_pattern: str?` |

## Network

- **Internal Docker network:** `agent-pc-network` (bridge)
- **Communication:** Services reachable by service name
- **Tailscale:** IPs 100.x.x.x for external access
- **Host gateway:** `host.docker.internal` for SSH from container to host

## Security

1. **Tailscale VPN:** WireGuard — point-to-point encrypted traffic
2. **Isolated Docker network:** `agent-pc-network` only accessible between services
3. **AUTH_SECRET:** Shared key Open WebUI ↔ Agent-PC
4. **SSH with key:** Agent-PC container accesses host only with authorized key
5. **No internet-exposed ports:** Only accessible within tailnet
6. **Restricted workspace:** `WORKSPACE_ROOT` limits operation scope
