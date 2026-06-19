# Agent-PC — Guía de Despliegue

## Requisitos del Servidor

- **Linux** (Ubuntu 22.04+ / Debian 12+ recomendado)
- **Docker** 24+ y **Docker Compose** v2+
- **OpenSSH Server** (para tool execution en el host)
- **Tailscale** (para acceso remoto desde iPhone)
- Mínimo 4 GB RAM (8 GB si usas Ollama)
- 20 GB disco (más si descargas modelos locales)

## Instalación Paso a Paso

### 1. Instalar Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar
```

### 2. Clonar y Configurar

```bash
git clone <repo-url> agent-pc
cd agent-pc
cp .env.docker .env
nano .env
```

Variables críticas en `.env`:
```ini
WEBUI_SECRET_KEY=<clave-aleatoria-larga>
AUTH_SECRET=<clave-compartida>
SSH_USER=<tu-usuario>
WORKSPACE_ROOT=/home/<tu-usuario>
```

### 3. Configurar SSH

```bash
sudo apt install -y openssh-server
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 4. Levantar Servicios

```bash
# Solo lo esencial
docker compose up -d

# Con Ollama (necesita más RAM)
docker compose --profile ollama up -d

# Con Tailscale VPN
docker compose --profile tailscale up -d

# Verificar
docker compose ps
docker compose logs agent-pc
```

### 5. Configurar Open WebUI

1. Abrir `http://<ip-servidor>:3000`
2. Crear cuenta admin
3. **Admin Panel → Settings → Connections:**
   - Añadir OpenAI: `https://api.openai.com/v1` + API key
   - Añadir Gemini: API key de Google AI Studio
   - Añadir DeepSeek: `https://api.deepseek.com/v1` + API key
   - Si usas Ollama: `http://ollama:11434`
4. **Admin Panel → Workspace → Functions:**
   - Importar `open-webui/tools/agent-pc-tools.json`
   - Configurar variable `AUTH_SECRET`

### 6. Configurar Tailscale (Acceso Remoto)

```bash
# En el servidor
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# En iPhone: instalar Tailscale desde App Store
# Conectar con la misma cuenta
# Acceder vía http://100.x.x.x:3000
```

## Actualización

```bash
git pull
docker compose pull
docker compose build agent-pc
docker compose up -d
```

## Backup y Restauración

```bash
# Backup de datos de Open WebUI
docker run --rm -v agent-pc-webui-data:/data -v $(pwd):/backup alpine tar czf /backup/webui-backup.tar.gz -C /data .

# Restaurar
docker run --rm -v agent-pc-webui-data:/data -v $(pwd):/backup alpine tar xzf /backup/webui-backup.tar.gz -C /data
```

## Troubleshooting

### Agent-PC no arranca
```bash
docker compose logs agent-pc
# Verificar que requirements.txt no tenga dependencias rotas
```

### SSH no funciona
```bash
# Probar SSH manualmente desde el host
ssh -i ~/.ssh/id_rsa $USER@localhost "echo ok"
# Verificar permisos
chmod 600 ~/.ssh/id_rsa ~/.ssh/authorized_keys
```

### Open WebUI no ve a Agent-PC
```bash
# Verificar que ambos están en la misma red
docker compose exec open-webui curl http://agent-pc:8765/health
# Debe responder {"status":"ok",...}
```

### Tailscale no conecta
```bash
# Verificar estado
tailscale status
# Re-autenticar
sudo tailscale up
```
