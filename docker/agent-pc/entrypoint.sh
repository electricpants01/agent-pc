#!/bin/bash
# ============================================
# Agent-PC Server — Entrypoint
# ============================================
set -e

echo "┌────────────────────────────────────────┐"
echo "│   🛠️  Agent-PC Server (Tool Engine)     │"
echo "└────────────────────────────────────────┘"
echo ""
echo "  SSH Host  : ${SSH_HOST:-host.docker.internal}:${SSH_PORT:-22}"
echo "  SSH User  : ${SSH_USER:-agentpc}"
echo "  Workspace : ${WORKSPACE_ROOT:-/home/agentpc/workspace}"
echo ""

# Verificar conectividad SSH con el host
echo "🔌 Verificando conexión SSH al host..."
if ssh -o StrictHostKeyChecking=accept-new \
       -o ConnectTimeout=5 \
       -o BatchMode=yes \
       -p "${SSH_PORT:-22}" \
       -i "${SSH_KEY_PATH:-/home/agentpc/.ssh/id_rsa}" \
       "${SSH_USER:-agentpc}@${SSH_HOST:-host.docker.internal}" \
       "echo 'SSH OK'" 2>/dev/null; then
    echo "✅ Conexión SSH al host establecida."
else
    echo "⚠️  No se pudo conectar al host vía SSH."
    echo "   Las herramientas se ejecutarán localmente (contenedor)."
    echo "   Para habilitar SSH: monta ~/.ssh y configura SSH_HOST."
fi

echo ""
echo "🚀 Iniciando servidor FastAPI en ${SERVER_HOST:-0.0.0.0}:${SERVER_PORT:-8765}..."

exec python main.py
