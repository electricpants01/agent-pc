# Agent-PC 🖥️🧠

Control your Linux machine with AI from any device — install nothing on the client.

```
┌──────────────────────┐      Tailscale VPN      ┌──────────────────────────────────────┐
│  ANY DEVICE          │◄──────────────────────►│  Linux Server 24/7 (Docker)          │
│                      │    Private mesh net    │                                      │
│ • iPhone (PWA/Safari)│                         │  ┌────────────────────────────────┐  │
│ • iPad               │                         │  │  🧠 Open WebUI (port 3000)     │  │
│ • Mac/PC (browser)   │                         │  │  • Multi-model (GPT, Gemini,   │  │
│ • 🎤 Voice → command │                         │  │    DeepSeek, Claude, Ollama)   │  │
│                      │                         │  │  • Admin panel for API keys    │  │
└──────────────────────┘                         │  │  • Chat + Voice + Streaming    │  │
                                                 │  └──────────────┬─────────────────┘  │
                                                 │                 │                    │
                                                 │  ┌──────────────▼─────────────────┐  │
                                                 │  │  🛠️ Agent-PC (port 8765)      │  │
                                                 │  │  • Tool execution engine       │  │
                                                 │  │  • SSH → host machine          │  │
                                                 │  │  • Read/write files            │  │
                                                 │  │  • Execute commands            │  │
                                                 │  └──────────────┬─────────────────┘  │
                                                 │                 │                    │
                                                 │  ┌──────────────▼─────────────────┐  │
                                                 │  │  💻 Your Linux Machine         │  │
                                                 │  │  • File system                 │  │
                                                 │  │  • Shell commands              │  │
                                                 │  │  • Processes, services, etc.   │  │
                                                 │  └────────────────────────────────┘  │
                                                 │                                      │
                                                 │  ┌────────────────────────────────┐  │
                                                 │  │  🦙 Ollama (optional)          │  │
                                                 │  │  • Private local models        │  │
                                                 │  └────────────────────────────────┘  │
                                                 │                                      │
                                                 │  ┌────────────────────────────────┐  │
                                                 │  │  🔐 Tailscale                  │  │
                                                 │  │  • Private mesh VPN            │  │
                                                 │  └────────────────────────────────┘  │
                                                 └──────────────────────────────────────┘
```

---

## 🚀 Quick Start (Docker)

### Requirements

- **Linux** with Docker and Docker Compose installed
- **Tailscale** installed on host and iPhone (for remote access)
- API key for at least one LLM provider (OpenAI, Gemini, DeepSeek...)

### 1. Clone and Configure

```bash
git clone https://github.com/your-username/agent-pc.git
cd agent-pc
cp .env.docker .env
nano .env  # Edit the variables
```

### 2. Configure SSH (for Agent-PC to run commands on host)

```bash
# Ensure SSH server is installed on the host
sudo apt install openssh-server

# Generate key if you don't have one
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Authorize your own key
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. Start Services

```bash
# Base services (Open WebUI + Agent-PC)
docker compose up -d

# With Ollama (local models)
docker compose --profile ollama up -d

# With Tailscale (VPN)
docker compose --profile tailscale up -d

# All together
docker compose --profile ollama --profile tailscale up -d
```

### 4. Open WebUI

```
http://localhost:3000
```

### 5. Configure Open WebUI

1. Create your admin account (first access)
2. Go to **Admin Panel → Settings → Connections**
3. Add your API keys:
   - OpenAI: `https://api.openai.com/v1` + your API key
   - Google Gemini: your API key
   - DeepSeek: `https://api.deepseek.com/v1` + your API key
   - Ollama (local): `http://ollama:11434`
4. Go to **Admin Panel → Workspace → Functions**
5. Import `open-webui/tools/agent-pc-tools.json`
6. Set the `AUTH_SECRET` variable to match your `.env`

### 6. Configure Tailscale (iPhone access)

```bash
# On the Linux host
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# On your iPhone: install Tailscale from App Store
# Log in with the same account
```

Now access from Safari on your iPhone:
```
http://100.x.x.x:3000  (your server's Tailscale IP)
```

**Tip:** In Safari on iPhone, press Share → "Add to Home Screen" to install it as an app.

---

## 🛠️ Agent-PC Server (Tool Engine)

The Agent-PC server is now **only a tool execution engine**. Open WebUI handles all LLM logic.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/tools?secret=...` | List tools (OpenAI format) |
| POST | `/tool?secret=...` | Execute a tool |

### Available Tools

| Tool | Description |
|------|-------------|
| `execute_command` | Execute shell commands on the host |
| `read_file` | Read files from the host |
| `write_file` | Write/create files on the host |
| `list_directory` | List directory contents |
| `search_files` | Search files (grep) |

### Test the Server

```bash
# Health check
curl http://localhost:8765/health

# List tools
curl "http://localhost:8765/tools?secret=agent-pc-local-secret-change-me"

# Execute a command
curl -X POST "http://localhost:8765/tool?secret=agent-pc-local-secret-change-me" \
  -H "Content-Type: application/json" \
  -d '{"name": "execute_command", "args": {"command": "df -h"}}'
```

---

## 📱 Use from iPhone (no compiling required)

1. Install **Tailscale** on your iPhone from the App Store
2. Connect to your tailnet (same account as the server)
3. Open Safari and go to `http://<your-server-tailscale-ip>:3000`
4. Tap **Share → Add to Home Screen**
5. Done! Agent-PC appears as an app on your home screen

### Why don't you need a native app?

Open WebUI is a **PWA** (Progressive Web App):
- ✅ Works in any modern browser
- ✅ Native voice support (Web Speech API in Safari)
- ✅ Installs to home screen like a real app
- ✅ Real-time chat streaming
- ✅ Multi-model (switch between GPT, Gemini, DeepSeek, Ollama)
- ✅ Conversation history
- ✅ No compiling, no Xcode, no App Store

---

## 🏗️ Architecture

```
docker-compose.yml
├── open-webui (port 3000)    ← Multi-model brain
│   ├── OpenAI API
│   ├── Gemini API
│   ├── DeepSeek API
│   └── Ollama (local)
├── agent-pc (port 8765)      ← Tool execution engine
│   └── SSH → Host machine
├── ollama (port 11434)       ← Local models [optional]
└── tailscale                 ← VPN mesh [optional]
```

### Why Docker?

- ✅ **Zero host dependencies** — only Docker needed
- ✅ **One-command updates**: `docker compose pull && docker compose up -d`
- ✅ **Isolation**: LLM and tool engine run in separate environments
- ✅ **Portability**: works on any Linux with Docker

### Why Open WebUI?

- ✅ **Admin panel for API key management** — no file editing
- ✅ **Native support for 10+ providers** (OpenAI, Gemini, DeepSeek, Claude, Ollama, etc.)
- ✅ **OpenAI-compatible API** — any existing client works
- ✅ **PWA** — use from any device without installing anything
- ✅ **Tool pipeline** — delegates execution to Agent-PC server

---

## 🛡️ Security

- **Tailscale VPN**: all traffic is encrypted via WireGuard
- **Isolated Docker network**: `agent-pc-network` only accessible between services
- **AUTH_SECRET**: authentication between Open WebUI and Agent-PC
- **SSH with key**: container accesses host only via authorized SSH
- **No internet-exposed ports**: only accessible within tailnet
- **Restricted workspace**: `WORKSPACE_ROOT` limits operation scope

---

## 🗺️ Roadmap

- [x] Docker Compose with Open WebUI + Agent-PC + Ollama
- [x] Tool execution via SSH to host
- [x] Tailscale VPN for remote access
- [x] PWA for iPhone (zero code)
- [ ] MCP (Model Context Protocol) for Agent-PC
- [ ] Persistent history with backups
- [ ] Push notifications via Open WebUI
- [ ] Integration with Google Calendar, Gmail, etc.
- [ ] Siri Shortcuts for quick commands
