# ============================================
# Agent-PC Server Dockerfile
# ============================================
# Minimal image for the tool execution engine.
# No LLM client — only FastAPI + SSH tools.
# ============================================

FROM python:3.11-slim-bookworm

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash agentpc && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-client \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (Docker layer caching)
COPY server/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server/ .

# Copy entrypoint
COPY docker/agent-pc/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Ensure permissions
RUN chown -R agentpc:agentpc /app /home/agentpc

# Switch to non-root user
USER agentpc

# Internal health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8765/health || exit 1

EXPOSE 8765

ENTRYPOINT ["/entrypoint.sh"]
