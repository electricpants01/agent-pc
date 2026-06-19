# Agent-PC — Deployment Guide

## Server Requirements

- **Linux** (Ubuntu 22.04+ / Debian 12+ recommended)
- **Docker** 24+ and **Docker Compose** v2+
- **OpenSSH Server** (for tool execution on host)
- **Tailscale** (for remote iPhone access)
- Minimum 4 GB RAM (8 GB if using Ollama)
- 20 GB disk (more if downloading local models)

## Step-by-Step Setup

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in
```

### 2. Clone and Configure

```bash
git clone <repo-url> agent-pc
cd agent-pc
cp .env.docker .env
nano .env
```

Critical `.env` variables:
```ini
WEBUI_SECRET_KEY=<long-random-string>
AUTH_SECRET=<shared-secret>
SSH_USER=<your-username>
WORKSPACE_ROOT=/home/<your-username>
```

### 3. Configure SSH

```bash
sudo apt install -y openssh-server
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 4. Start Services

```bash
# Essentials only
docker compose up -d

# With Ollama (needs more RAM)
docker compose --profile ollama up -d

# With Tailscale VPN
docker compose --profile tailscale up -d

# Verify
docker compose ps
docker compose logs agent-pc
```

### 5. Configure Open WebUI

1. Open `http://<server-ip>:3000`
2. Create admin account
3. **Admin Panel → Settings → Connections:**
   - Add OpenAI: `https://api.openai.com/v1` + API key
   - Add Gemini: Google AI Studio API key
   - Add DeepSeek: `https://api.deepseek.com/v1` + API key
   - If using Ollama: `http://ollama:11434`
4. **Admin Panel → Workspace → Functions:**
   - Import `open-webui/tools/agent-pc-tools.json` (JSON import)
   - OR import `open-webui/tools/agent-pc-tools.py` (Python function import, preferred)
   - Set `AUTH_SECRET` variable

### 6. Configure Tailscale (Remote Access)

```bash
# On server
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# On iPhone: install Tailscale from App Store
# Connect with same account
# Access via http://100.x.x.x:3000
```

## Updating

```bash
git pull
docker compose pull
docker compose build agent-pc
docker compose up -d
```

## Backup and Restore

```bash
# Backup Open WebUI data
docker run --rm -v agent-pc-webui-data:/data -v $(pwd):/backup alpine tar czf /backup/webui-backup.tar.gz -C /data .

# Restore
docker run --rm -v agent-pc-webui-data:/data -v $(pwd):/backup alpine tar xzf /backup/webui-backup.tar.gz -C /data
```

## Troubleshooting

### Agent-PC won't start
```bash
docker compose logs agent-pc
# Check that requirements.txt has no broken deps
```

### SSH not working
```bash
# Test SSH manually from host
ssh -i ~/.ssh/id_rsa $USER@localhost "echo ok"
# Check permissions
chmod 600 ~/.ssh/id_rsa ~/.ssh/authorized_keys
```

### Open WebUI can't reach Agent-PC
```bash
# Verify both on same network
docker compose exec open-webui curl http://agent-pc:8765/health
# Should return {"status":"ok",...}
```

### Tailscale not connecting
```bash
# Check status
tailscale status
# Re-authenticate
sudo tailscale up
```
