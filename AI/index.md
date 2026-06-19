# Agent-PC — Documentación para Agentes AI

Esta carpeta contiene documentación estructurada para que agentes de IA (Cline, Cursor, Copilot, etc.) comprendan rápidamente el proyecto.

## Índice

| Archivo | Contenido |
|---------|-----------|
| [`architecture.md`](architecture.md) | Arquitectura completa del sistema, diagramas, flujo de datos, componentes, seguridad |
| [`development.md`](development.md) | Guía de desarrollo: estructura del proyecto, stack, comandos, cómo añadir tools |
| [`deployment.md`](deployment.md) | Guía de despliegue: requisitos, instalación paso a paso, backup, troubleshooting |
| [`conventions.md`](conventions.md) | Convenciones: idiomas, estilo de código, git, Docker, nombrado de archivos |

## Reglas para Agentes

| Carpeta | Audiencia |
|---------|-----------|
| [`.clinerules/`](../.clinerules/) | Cline (VS Code extension) |
| [`.cursor/rules/`](../.cursor/rules/) | Cursor IDE |

## Lectura Recomendada para un Nuevo Agente

1. **`architecture.md`** — Entender qué hace el sistema y cómo
2. **`development.md`** — Saber dónde está cada cosa
3. **`conventions.md`** — Seguir las reglas del proyecto
4. **`deployment.md`** — Ponerlo en marcha

## Resumen Rápido (TL;DR)

- **Agent-PC** = controla Linux remotamente con IA conversacional
- **Open WebUI** (Docker, puerto 3000) = cerebro multi-modelo + interfaz PWA
- **Agent-PC Server** (Docker, puerto 8765) = ejecutor de herramientas (NO LLM)
- **Tailscale** = VPN para acceso desde iPhone
- **Tools** = execute_command, read_file, write_file, list_directory, search_files
- **Auth** = AUTH_SECRET compartido entre Open WebUI y Agent-PC
- **Código** = Python 3.11 + FastAPI, inglés para variables, español para comentarios
