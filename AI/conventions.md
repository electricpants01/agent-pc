# Agent-PC — Convenciones del Proyecto

## Idiomas

- **Código:** Inglés (variables, funciones, clases)
- **Comentarios y docstrings:** Español
- **Documentación:** Español
- **Commits:** Inglés (conventional commits)

## Python

### Estilo
- PEP 8 (4 espacios, snake_case, PascalCase para clases)
- Type hints donde aporten claridad
- Docstrings en formato Google-style

### Herramientas (Tools)
- Cada tool retorna un dict con `{"ok": bool, ...}`
- Errores: `{"ok": false, "error": "descripción"}`
- Funciones síncronas (FastAPI las ejecuta en thread pool)

### Configuración
- Variables de entorno vía `python-dotenv`
- Archivo `.env` NO se commitea (está en `.gitignore`)
- `.env.example` y `.env.docker` como templates

## Docker

- Imágenes basadas en `python:3.11-slim-bookworm`
- Usuario no-root (`agentpc`) en contenedores
- Health checks en todos los servicios
- Volúmenes con nombres explícitos (`agent-pc-*`)
- Red bridge dedicada (`agent-pc-network`)

## Open WebUI

- Tools en `open-webui/tools/` en formato JSON
- Configuración de API keys desde el panel admin (nunca en archivos)
- Funciones usan HTTP POST a `http://agent-pc:8765/tool`

## Git

### Ramas
- `main` — producción
- `dev` — desarrollo
- `feat/<nombre>` — features nuevas

### Commits (Conventional Commits)
```
feat: añadir tool para gestionar procesos
fix: corregir timeout en execute_command
docs: actualizar README con nueva arquitectura
refactor: simplificar main.py
chore: actualizar dependencias
```

## Nombrado de Archivos

- `docker-compose.yml` — orquestación
- `.env.docker` — template de variables Docker
- `Dockerfile` — imagen de contenedor
- `entrypoint.sh` — script de entrada
- `tools.py` — definición de herramientas
- `config.py` — configuración
- `main.py` — punto de entrada FastAPI
