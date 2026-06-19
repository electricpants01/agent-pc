# Agent-PC — Guía de Desarrollo

## Estructura del Proyecto

```
agent-pc/
├── docker-compose.yml           ← Orquestación de servicios
├── .env.docker                  ← Variables de entorno para Docker
├── docker/
│   └── agent-pc/
│       ├── Dockerfile           ← Imagen Python del tool engine
│       └── entrypoint.sh        ← Script de arranque
├── server/                      ← Agent-PC Server (Python)
│   ├── main.py                  ← FastAPI app (3 endpoints)
│   ├── tools.py                 ← Definición e implementación de tools
│   ├── config.py                ← Configuración desde env vars
│   ├── requirements.txt         ← Dependencias Python
│   ├── .env.example             ← Ejemplo de configuración
│   ├── agent.py                 ← [LEGACY] Cliente LLM (ya no usado)
│   ├── setup.sh                 ← [LEGACY] Instalación sin Docker
│   └── agent-pc.service         ← [LEGACY] Servicio systemd
├── open-webui/
│   └── tools/
│       └── agent-pc-tools.json  ← Tools para importar en Open WebUI
├── ios/                         ← [LEGACY] App iOS SwiftUI (backup)
├── AI/                          ← Documentación para agentes AI
│   ├── architecture.md
│   ├── development.md
│   ├── deployment.md
│   └── conventions.md
├── .clinerules/                 ← Reglas para Cline
├── .cursor/rules/               ← Reglas para Cursor
└── README.md                    ← Documentación principal
```

## Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|-----------|--------|
| Contenedores | Docker + Docker Compose | 3.9+ |
| LLM Brain | Open WebUI | latest (main) |
| Tool Engine | Python + FastAPI | 3.11, 0.115.6 |
| SSH | asyncssh | 2.19.0 |
| VPN | Tailscale (WireGuard) | latest |
| Modelos locales | Ollama | latest |
| Cliente | PWA (Web Speech API) | Navegador moderno |

## Comandos Útiles

### Desarrollo Local

```bash
# Instalar dependencias
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Correr servidor en desarrollo
cp .env.example .env
python main.py

# Probar endpoints
curl http://localhost:8765/health
curl "http://localhost:8765/tools?secret=agent-pc-local-secret-change-me"
curl -X POST "http://localhost:8765/tool?secret=agent-pc-local-secret-change-me" \
  -H "Content-Type: application/json" \
  -d '{"name": "execute_command", "args": {"command": "echo hello"}}'
```

### Docker

```bash
# Build y levantar
docker compose up -d --build

# Solo agent-pc (para desarrollo rápido)
docker compose up -d agent-pc

# Ver logs
docker compose logs -f agent-pc
docker compose logs -f open-webui

# Reconstruir tras cambios
docker compose build agent-pc
docker compose up -d --force-recreate agent-pc

# Bajar todo
docker compose down

# Con perfiles
docker compose --profile ollama --profile tailscale up -d

# Limpiar volúmenes
docker compose down -v
```

## Añadir Nuevas Herramientas

1. Definir el schema en `server/tools.py` → `TOOL_DEFINITIONS`
2. Implementar la función `tool_<nombre>()`
3. Registrar en `TOOL_MAP`
4. Añadir a `open-webui/tools/agent-pc-tools.json`
5. Reconstruir: `docker compose build agent-pc && docker compose up -d`
6. Reimportar tools en Open WebUI Admin Panel

## Convenciones de Código

- **Idioma:** Variables/funciones en inglés, comentarios/docstrings en español
- **Python:** PEP 8, type hints cuando sea útil
- **Herramientas:** Cada tool retorna `{"ok": bool, ...}` 
- **Errores:** `{"ok": false, "error": "mensaje"}`
- **Streaming:** Ya no se usa en Agent-PC (Open WebUI lo maneja)
