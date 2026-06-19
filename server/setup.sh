#!/bin/bash
# ============================================
# Agent-PC Server Setup para Linux
# ============================================
set -e

echo "🔧 Instalando Agent-PC Server..."

# 1. Paquetes del sistema
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# 2. Entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Dependencias Python
pip install -r requirements.txt

# 4. Configuración
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Edita el archivo .env con tu API key y configuración."
    echo "   nano .env"
fi

# 5. Instalar como servicio systemd (opcional)
echo ""
echo "¿Quieres instalar el servicio systemd para arranque automático? (s/n)"
read -r answer
if [ "$answer" = "s" ]; then
    # Ajustar rutas en el archivo de servicio
    CURRENT_USER=$(whoami)
    SCRIPT_DIR=$(pwd)
    sed -i "s|tu-usuario|$CURRENT_USER|g" agent-pc.service
    sed -i "s|/home/tu-usuario/agent-pc/server|$SCRIPT_DIR|g" agent-pc.service

    sudo cp agent-pc.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable agent-pc
    sudo systemctl start agent-pc
    echo "✅ Servicio instalado. Estado:"
    sudo systemctl status agent-pc --no-pager
else
    echo "🚀 Para iniciar manualmente:"
    echo "   source venv/bin/activate"
    echo "   python main.py"
fi

echo ""
echo "✅ Instalación completada!"
echo "📍 El servidor corre en http://$(hostname -I | awk '{print $1}'):8765"
