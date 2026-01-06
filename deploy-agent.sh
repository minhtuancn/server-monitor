#!/bin/bash

#################################################################
# Quick Agent Deployment Script
# Deploy monitoring agent to remote server via SSH
#################################################################

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           Deploy Monitoring Agent to Remote Server        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <user@host> [port] [agent_port]"
    echo ""
    echo "Examples:"
    echo "  $0 root@192.168.1.100"
    echo "  $0 root@192.168.1.100 22 8083"
    echo ""
    exit 1
fi

USER_HOST=$1
SSH_PORT=${2:-22}
AGENT_PORT=${3:-8083}

AGENT_FILE="$(dirname "$0")/backend/agent.py"
REMOTE_PATH="/opt/monitoring_agent.py"

if [ ! -f "$AGENT_FILE" ]; then
    echo "❌ Agent file not found: $AGENT_FILE"
    exit 1
fi

echo "📦 Agent file: $AGENT_FILE"
echo "🎯 Target: $USER_HOST:$SSH_PORT"
echo "📡 Agent will run on port: $AGENT_PORT"
echo ""

# Test SSH connection
echo "🔐 Testing SSH connection..."
if ! ssh -p $SSH_PORT -o ConnectTimeout=5 $USER_HOST "echo 'Connection OK'" 2>/dev/null; then
    echo "❌ SSH connection failed"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Make sure SSH is running on remote server"
    echo "  2. Check if your SSH key is authorized:"
    echo "     ssh-copy-id -p $SSH_PORT $USER_HOST"
    echo "  3. Manually test: ssh -p $SSH_PORT $USER_HOST"
    exit 1
fi

echo "✅ SSH connection successful"
echo ""

# Check if Python3 is available on remote server
echo "🐍 Checking Python3 on remote server..."
if ! ssh -p $SSH_PORT $USER_HOST "which python3" >/dev/null 2>&1; then
    echo "❌ Python3 not found on remote server"
    echo "   Install it first: apt-get install python3 (Debian/Ubuntu)"
    exit 1
fi

PYTHON_VERSION=$(ssh -p $SSH_PORT $USER_HOST "python3 --version" 2>&1)
echo "✅ $PYTHON_VERSION"
echo ""

# Upload agent script
echo "📤 Uploading agent script to $REMOTE_PATH..."
if scp -P $SSH_PORT "$AGENT_FILE" "$USER_HOST:$REMOTE_PATH"; then
    echo "✅ Upload successful"
else
    echo "❌ Upload failed"
    exit 1
fi

# Make executable
echo "🔧 Setting permissions..."
ssh -p $SSH_PORT $USER_HOST "chmod +x $REMOTE_PATH"

# Check if agent is already running
echo "🔍 Checking if agent is already running..."
if ssh -p $SSH_PORT $USER_HOST "lsof -i:$AGENT_PORT" >/dev/null 2>&1; then
    echo "⚠️  Agent is already running on port $AGENT_PORT"
    read -p "   Stop and restart? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ssh -p $SSH_PORT $USER_HOST "kill \$(lsof -t -i:$AGENT_PORT) 2>/dev/null" || true
        sleep 2
    fi
fi

# Start agent
echo "🚀 Starting agent..."
ssh -p $SSH_PORT $USER_HOST "nohup python3 $REMOTE_PATH > /tmp/agent.log 2>&1 &" &
sleep 3

# Verify agent is running
echo "✓ Verifying agent status..."
if ssh -p $SSH_PORT $USER_HOST "curl -s http://localhost:$AGENT_PORT/api/health" >/dev/null 2>&1; then
    echo "✅ Agent is running successfully!"
    echo ""
    echo "───────────────────────────────────────────────────────────"
    echo "✨ Deployment Complete!"
    echo "───────────────────────────────────────────────────────────"
    echo "Agent URL: http://$USER_HOST:$AGENT_PORT/api/health"
    echo ""
    echo "Test with: curl http://localhost:$AGENT_PORT/api/all"
    echo ""
    echo "To add to Central Server, use the Web UI or:"
    echo "  curl -X POST http://localhost:9083/api/servers \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{ \\"
    echo "      \"name\": \"My Server\", \\"
    echo "      \"host\": \"'$(echo $USER_HOST | cut -d'@' -f2)'\", \\"
    echo "      \"username\": \"'$(echo $USER_HOST | cut -d'@' -f1)'\", \\"
    echo "      \"port\": $SSH_PORT, \\"
    echo "      \"agent_port\": $AGENT_PORT, \\"
    echo "      \"description\": \"LXC Container\", \\"
    echo "      \"ssh_key_path\": \"~/.ssh/id_rsa\" \\"
    echo "    }'"
    echo "───────────────────────────────────────────────────────────"
else
    echo "❌ Agent failed to start"
    echo ""
    echo "Check logs on remote server:"
    echo "  ssh -p $SSH_PORT $USER_HOST 'cat /tmp/agent.log'"
    exit 1
fi
