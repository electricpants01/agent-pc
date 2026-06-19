# Agent-PC 🖥️🧠

Controla tu máquina Linux con IA desde cualquier dispositivo — sin instalar nada en el cliente.

```
┌──────────────────────┐      Tailscale VPN      ┌──────────────────────────────────────┐
│  CUALQUIER DISPOSITIVO│◄──────────────────────►│  Linux Server 24/7 (Docker)          │
│                      │    Red privada mesh     │                                      │
│ • iPhone (PWA/Safari)│                         │  ┌────────────────────────────────┐  │
│ • iPad               │                         │  │  🧠 Open WebUI (puerto 3000)   │  │
│ • Mac/PC (navegador) │                         │  │  • Multi-modelo (GPT, Gemini,  │  │
│ • 🎤 Voz → comando   │                         │  │    DeepSeek, Claude, Ollama)   │  │
│                      │                         │  │  • Panel admin para API keys   │  │
└──────────────────────┘                         │  │  • Chat + Voz + Streaming      │  │
                                                 │  └──────────────┬─────────────────┘  │
                                                 │                 │                    │
                                                 │  ┌──────────────▼─────────────────┐  │
                                                 │  │  🛠️ Agent-PC (puerto 8765)    │  │
                                                 │  │  • Tool execution engine       │  │
                                                 │  │  • SSH → host machine          │  │
                                                 │  │  • Lee/escribe archivos        │  │
                                                 │  │  • Ejecuta comandos            │  │
                                                 │  └──────────────┬─────────────────┘  │
                                                 │                 │                    │
                                                 │  ┌──────────────▼─────────────────┐  │
                                                 │  │  💻 Tu Máquina Linux           │  │
                                                 │  │  • File system                 │  │
                                                 │  │  • Shell commands              │  │
                                                 │  │  • Procesos, servicios, etc.   │  │
                                                 │  └────────────────────────────────┘  │
                                                 │                                      │
                                                 │  ┌────────────────────────────────┐  │
                                                 │  │  🦙 Ollama (opcional)          │  │
                                                 │  │  • Modelos locales privados    │  │
                                                 │  └────────────────────────────────┘  │
                                                 │                                      │
                                                 │  ┌────────────────────────────────┐  │
                                                 │  │  🔐 Tailscale                  │  │
                                                 │  │  • VPN mesh privada            │  │
                                                 │  └────────────────────────────────┘  │
                                                 └──────────────────────────────────────┘
```

## 🚀 Instalación Rápida (Docker)

### Requisitos

- **Linux** con Docker y Docker Compose instalados
- **Tailscale** instalado en el host y en tu iPhone (para acceso remoto)
- API key de al menos un proveedor LLM (OpenAI, Gemini, DeepSeek...)

### 1. Clonar y configurar

```bash
git clone https://github.com/tu-usuario/agent-pc.git
cd agent-pc
cp .env.docker .env
nano .env  # Edita las variables
```

### 2. Configurar SSH (para que Agent-PC ejecute comandos en el host)

```bash
# Asegúrate de tener servidor SSH en el host
sudo apt install openssh-server

# Genera una clave si no tienes
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Autoriza tu propia clave
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. Levantar los servicios

```bash
# Servicios base (Open WebUI + Agent-PC)
docker compose up -d

# Con Ollama (modelos locales)
docker compose --profile ollama up -d

# Con Tailscale (VPN)
docker compose --profile tailscale up -d

# Todo junto
docker compose --profile ollama --profile tailscale up -d
```

### 4. Abrir Open WebUI

```
http://localhost:3000
```

### 5. Configurar Open WebUI

1. Crea tu cuenta admin (primer acceso)
2. Ve a **Admin Panel → Settings → Connections**
3. Añade tus API keys:
   - OpenAI: `https://api.openai.com/v1` + tu API key
   - Google Gemini: tu API key
   - DeepSeek: `https://api.deepseek.com/v1` + tu API key
   - Ollama (local): `http://ollama:11434`
4. Ve a **Admin Panel → Workspace → Functions**
5. Importa `open-webui/tools/agent-pc-tools.json`
6. Configura la variable `AUTH_SECRET` con el mismo valor de tu `.env`

### 6. Configurar Tailscale (acceso desde iPhone)

```bash
# En el host Linux
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# En tu iPhone: instala Tailscale desde App Store
# Inicia sesión con la misma cuenta
```

Ahora puedes acceder desde Safari en tu iPhone:
```
http://100.x.x.x:3000  (IP de Tailscale de tu servidor)
```

**Tip:** En Safari iPhone, pulsa Compartir → "Añadir a pantalla de inicio" para tenerlo como app.

---

## 🛠️ Agent-PC Server (Tool Engine)

El servidor Agent-PC ahora es **solo un motor de ejecución de herramientas**. Open WebUI maneja toda la lógica de LLM.

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/tools?secret=...` | Lista herramientas (OpenAI format) |
| POST | `/tool?secret=...` | Ejecutar herramienta |

### Herramientas disponibles

| Herramienta | Descripción |
|-------------|-------------|
| `execute_command` | Ejecutar comandos shell en el host |
| `read_file` | Leer archivos del host |
| `write_file` | Escribir/crear archivos en el host |
| `list_directory` | Listar directorios |
| `search_files` | Buscar en archivos (grep) |

### Probar el servidor

```bash
# Health check
curl http://localhost:8765/health

# Listar herramientas
curl "http://localhost:8765/tools?secret=agent-pc-local-secret-change-me"

# Ejecutar un comando
curl -X POST "http://localhost:8765/tool?secret=agent-pc-local-secret-change-me" \
  -H "Content-Type: application/json" \
  -d '{"name": "execute_command", "args": {"command": "df -h"}}'
```

---

## 📱 Usar desde iPhone (sin compilar nada)

1. Instala **Tailscale** en tu iPhone desde la App Store
2. Conéctate a tu tailnet (misma cuenta que el servidor)
3. Abre Safari y ve a `http://<ip-tailscale-de-tu-server>:3000`
4. Pulsa **Compartir → Añadir a pantalla de inicio**
5. ¡Listo! Tienes Agent-PC como una app en tu home screen

### ¿Por qué no necesitas una app nativa?

Open WebUI es una **PWA** (Progressive Web App):
- ✅ Funciona en cualquier navegador moderno
- ✅ Soporte de voz nativo (Web Speech API de Safari)
- ✅ Se instala en la pantalla de inicio como una app real
- ✅ Chat streaming en tiempo real
- ✅ Multi-modelo (cambia entre GPT, Gemini, DeepSeek, Ollama)
- ✅ Historial de conversaciones
- ✅ Sin compilar, sin Xcode, sin App Store

---

## 🏗️ Arquitectura

```
docker-compose.yml
├── open-webui (puerto 3000)    ← Cerebro multi-modelo
│   ├── OpenAI API
│   ├── Gemini API
│   ├── DeepSeek API
│   └── Ollama (local)
├── agent-pc (puerto 8765)      ← Tool execution engine
│   └── SSH → Host machine
├── ollama (puerto 11434)       ← Modelos locales [opcional]
└── tailscale                   ← VPN mesh [opcional]
```

---

## 🛡️ Seguridad

- **Tailscale VPN**: todo el tráfico va encriptado por WireGuard
- **Red interna Docker**: los servicios se comunican en red aislada
- **AUTH_SECRET**: autenticación entre Open WebUI y Agent-PC
- **SSH con clave**: el contenedor accede al host solo vía SSH autorizado
- **Sin puertos expuestos a internet**: solo dentro de la tailnet

---

## 🗺️ Roadmap

- [x] Docker Compose con Open WebUI + Agent-PC + Ollama
- [x] Tool execution vía SSH al host
- [x] Tailscale VPN para acceso remoto
- [x] PWA para iPhone (cero código)
- [ ] MCP (Model Context Protocol) para Agent-PC
- [ ] Historial persistente con backups
- [ ] Notificaciones push vía Open WebUI
- [ ] Integración con Google Calendar, Gmail, etc.
- [ ] Siri Shortcuts para comandos rápidos
