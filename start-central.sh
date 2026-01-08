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

# Navigate to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Check for virtual environment and activate it
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "✅ Found virtual environment, activating..."
    source "$SCRIPT_DIR/venv/bin/activate"
    PYTHON_CMD="python3"
elif [ -d "$SCRIPT_DIR/.venv" ]; then
    echo "✅ Found virtual environment (.venv), activating..."
    source "$SCRIPT_DIR/.venv/bin/activate"
    PYTHON_CMD="python3"
else
    echo "⚠️  No virtual environment found. Using system Python."
    echo "   For Python 3.12+, create a venv first: python3 -m venv venv"
    PYTHON_CMD="python3"
fi

# Navigate to backend directory
cd "$SCRIPT_DIR/backend" || exit 1

# Check Python3
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

echo "✅ Python3 found: $($PYTHON_CMD --version)"

# Check paramiko
if ! $PYTHON_CMD -c "import paramiko" 2>/dev/null; then
    echo "📦 Installing required dependencies..."
    pip install -r requirements.txt || {
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
$PYTHON_CMD database.py || {
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
$PYTHON_CMD central_api.py
