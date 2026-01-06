#!/bin/bash

#################################################################
# Multi-Server Monitoring System - Start Script
# Khởi động Central Server cho multi-server monitoring
#################################################################

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Multi-Server Monitoring System - Central Server          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  Warning: Running as root. Consider using a non-root user."
fi

# Navigate to backend directory
cd "$(dirname "$0")/backend" || exit 1

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Check paramiko
if ! python3 -c "import paramiko" 2>/dev/null; then
    echo "📦 Installing required dependencies..."
    pip3 install -r requirements.txt || {
        echo "❌ Failed to install dependencies"
        exit 1
    }
fi

echo "✅ Dependencies OK"

# Check if central server port is available
PORT=9083
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Port $PORT is already in use"
    echo "   Run: lsof -i :$PORT"
    echo "   To kill: kill -9 \$(lsof -t -i:$PORT)"
    exit 1
fi

echo "✅ Port $PORT is available"

# Initialize database
echo "📊 Initializing database..."
python3 database.py || {
    echo "⚠️  Warning: Database initialization returned non-zero"
}

# Check SSH key
SSH_KEY="$HOME/.ssh/id_rsa"
if [ ! -f "$SSH_KEY" ]; then
    echo "⚠️  SSH private key not found at $SSH_KEY"
    echo "   Generate one with: ssh-keygen -t rsa -b 4096"
    echo "   Or specify custom key path when adding servers"
fi

if [ ! -f "$SSH_KEY.pub" ]; then
    echo "⚠️  SSH public key not found at $SSH_KEY.pub"
else
    echo "✅ SSH key found"
    echo "📋 Your public key (copy this to remote servers):"
    echo "────────────────────────────────────────────────────────"
    cat "$SSH_KEY.pub"
    echo "────────────────────────────────────────────────────────"
fi

echo ""
echo "🚀 Starting Central Monitoring Server..."
echo ""

# Start the server
python3 central_api.py
