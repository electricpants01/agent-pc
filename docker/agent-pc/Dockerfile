# ============================================
# Agent-PC Server Dockerfile
# ============================================
# Imagen mínima para el tool execution engine.
# No incluye cliente LLM — solo FastAPI + SSH tools.
# ============================================

FROM python:3.11-slim-bookworm

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash agentpc && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-client \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements primero (cache de capa Docker)
COPY server/requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del servidor
COPY server/ .

# Copiar entrypoint
COPY docker/agent-pc/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Asegurar permisos
RUN chown -R agentpc:agentpc /app /home/agentpc

# Cambiar a usuario no-root
USER agentpc

# Health check interno
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8765/health || exit 1

EXPOSE 8765

ENTRYPOINT ["/entrypoint.sh"]
