#!/bin/bash
# ============================================
# Agent-PC Server — Entrypoint
# ============================================
set -e

echo "┌────────────────────────────────────────┐"
echo "│   Agent-PC Server (Tool Engine)         │"
echo "└────────────────────────────────────────┘"
echo ""
echo "  SSH Host  : ${SSH_HOST:-host.docker.internal}:${SSH_PORT:-22}"
echo "  SSH User  : ${SSH_USER:-agentpc}"
echo "  Workspace : ${WORKSPACE_ROOT:-/home/agentpc/workspace}"
echo ""

# Verify SSH connectivity to host
echo "Checking SSH connection to host..."
if ssh -o StrictHostKeyChecking=accept-new \
       -o ConnectTimeout=5 \
       -o BatchMode=yes \
       -p "${SSH_PORT:-22}" \
       -i "${SSH_KEY_PATH:-/home/agentpc/.ssh/id_rsa}" \
       "${SSH_USER:-agentpc}@${SSH_HOST:-host.docker.internal}" \
       "echo 'SSH OK'" 2>/dev/null; then
    echo "SSH connection to host established."
else
    echo "Could not connect to host via SSH."
    echo "   Tools will run locally (inside container)."
    echo "   To enable SSH: mount ~/.ssh and configure SSH_HOST."
fi

echo ""
echo "Starting FastAPI server on ${SERVER_HOST:-0.0.0.0}:${SERVER_PORT:-8765}..."

exec python main.py
