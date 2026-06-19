# Agent-PC — Arquitectura del Sistema

## Visión General

Agent-PC es un sistema que permite controlar una máquina Linux remotamente usando IA conversacional desde cualquier dispositivo (iPhone, iPad, navegador). No requiere instalar apps nativas — usa Open WebUI como PWA.

## Diagrama de Arquitectura

```
┌──────────────────────┐      Tailscale VPN      ┌──────────────────────────────────────┐
│  CUALQUIER DISPOSITIVO│◄──────────────────────►│  Linux Server 24/7 (Docker Host)     │
│                      │    Red privada mesh     │                                      │
│ • iPhone (PWA/Safari)│                         │  ┌────────────────────────────────┐  │
│ • iPad               │                         │  │  🧠 Open WebUI (puerto 3000)   │  │
│ • Mac/PC (navegador) │                         │  │  • Panel admin multi-modelo    │  │
│ • 🎤 Voz → comando   │                         │  │  • OpenAI / Gemini / DeepSeek  │  │
│                      │                         │  │  • Claude / Ollama / etc.      │  │
└──────────────────────┘                         │  │  • API OpenAI-compatible        │  │
                                                 │  │  • Functions / Tools pipeline   │  │
                                                 │  │  • Chat + Voz + Streaming      │  │
                                                 │  └──────────────┬─────────────────┘  │
                                                 │                 │ HTTP               │
                                                 │  ┌──────────────▼─────────────────┐  │
                                                 │  │  🛠️ Agent-PC (puerto 8765)    │  │
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
                                                 │  │  💻 Host Machine               │  │
                                                 │  │  • File system (read/write)    │  │
                                                 │  │  • Shell commands              │  │
                                                 │  │  • Directory listing           │  │
                                                 │  │  • File search (grep)          │  │
                                                 │  └────────────────────────────────┘  │
                                                 │                                      │
                                                 │  Servicios Opcionales:               │
                                                 │  ┌────────────────────────────────┐  │
                                                 │  │  🦙 Ollama (puerto 11434)      │  │
                                                 │  │  • Modelos LLM locales         │  │
                                                 │  └────────────────────────────────┘  │
                                                 │  ┌────────────────────────────────┐  │
                                                 │  │  🔐 Tailscale                  │  │
                                                 │  │  • VPN mesh (WireGuard)        │  │
                                                 │  └────────────────────────────────┘  │
                                                 └──────────────────────────────────────┘
```

## Flujo de Datos: Voz del Usuario → Ejecución en Host

```
1. Usuario habla al iPhone
   └→ Safari Web Speech API captura voz

2. Texto enviado a Open WebUI (HTTP POST /api/chat/completions)
   └→ API OpenAI-compatible con API key de Open WebUI

3. Open WebUI procesa con LLM configurado
   └→ El LLM decide si necesita ejecutar herramientas

4. Si necesita herramienta → HTTP POST a Agent-PC (/tool)
   └→ Auth via AUTH_SECRET compartido

5. Agent-PC ejecuta localmente (contenedor)
   └→ O vía SSH al host si está configurado

6. Resultado vuelve: Agent-PC → Open WebUI → LLM formula respuesta
   └→ Respuesta en lenguaje natural enviada al cliente

7. Safari/iPhone muestra texto + opcionalmente lee en voz alta
   └→ AVSpeechSynthesizer (Web Speech API)
```

## Componentes

### Open WebUI
- **Imagen:** `ghcr.io/open-webui/open-webui:main`
- **Rol:** Cerebro multi-modelo, interfaz de usuario (PWA), proxy LLM
- **Puerto:** 3000 → 8080 (interno)
- **Persistencia:** Volumen Docker `open-webui-data`
- **Auth:** Cuentas de usuario locales + API keys por proveedor

### Agent-PC Server (Tool Engine)
- **Imagen:** Dockerfile propio (Python 3.11-slim)
- **Rol:** Ejecutor de herramientas en el host
- **Puerto:** 8765
- **Auth:** `AUTH_SECRET` compartido vía query param

### Herramientas Disponibles

| Herramienta | Descripción | Parámetros |
|-------------|-------------|------------|
| `execute_command` | Ejecutar comando shell | `command: str`, `timeout: int?` |
| `read_file` | Leer archivo | `path: str`, `start_line: int?`, `end_line: int?` |
| `write_file` | Escribir archivo | `path: str`, `content: str` |
| `list_directory` | Listar directorio | `path: str`, `pattern: str?` |
| `search_files` | Buscar en archivos | `pattern: str`, `directory: str?`, `file_pattern: str?` |

## Red

- **Red interna Docker:** `agent-pc-network` (bridge)
- **Comunicación:** Los servicios se alcanzan por nombre de servicio
- **Tailscale:** IPs 100.x.x.x para acceso externo
- **Host gateway:** `host.docker.internal` para SSH desde contenedor al host

## Seguridad

1. **Tailscale VPN:** WireGuard — tráfico encriptado punto a punto
2. **Red Docker aislada:** `agent-pc-network` solo accesible entre servicios
3. **AUTH_SECRET:** Clave compartida Open WebUI ↔ Agent-PC
4. **SSH con clave:** Contenedor Agent-PC accede al host solo con clave autorizada
5. **Sin puertos a internet:** Solo expuesto dentro de tailnet
6. **Workspace restringido:** `WORKSPACE_ROOT` limita el scope de operaciones
