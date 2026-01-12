#!/bin/bash

###############################################################################
# Frontend Wrapper Script
# Keeps stdin open to prevent Next.js 16 dev server from exiting
###############################################################################

# Load nvm for Node.js 20
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
nvm use default > /dev/null 2>&1 || nvm use 20 > /dev/null 2>&1

# Change to frontend directory
cd "$(dirname "$0")/../frontend-next" || exit 1

# Keep stdin open by reading from /dev/null in a loop
# This prevents Next.js from detecting closed stdin and exiting
exec 0</dev/null

# Run Next.js dev server
# The 'exec' replaces the shell with the node process
exec npm run dev
