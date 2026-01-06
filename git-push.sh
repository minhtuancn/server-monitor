#!/bin/bash

###############################################################################
# Git Push Helper Script
# Pushes code to GitHub repository
###############################################################################

echo "======================================================================"
echo "  Pushing to GitHub: https://github.com/minhtuancn/server-monitor"
echo "======================================================================"
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "❌ Error: Not a git repository"
    exit 1
fi

# Show current status
echo "📊 Current Status:"
git status -s
echo ""

# Show what will be pushed
echo "📤 Commits to push:"
git log --oneline origin/main..HEAD 2>/dev/null || git log --oneline -3
echo ""

# Confirm
read -p "🔐 Ready to push to GitHub? You may need to enter credentials. Continue? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Pushing to GitHub..."
    
    # Try to push
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Successfully pushed to GitHub!"
        echo "🌐 View at: https://github.com/minhtuancn/server-monitor"
    else
        echo ""
        echo "❌ Push failed. Common issues:"
        echo ""
        echo "1. Authentication required:"
        echo "   - Use GitHub Personal Access Token as password"
        echo "   - Or configure SSH key"
        echo ""
        echo "2. Remote already has different commits:"
        echo "   git pull origin main --rebase"
        echo "   git push origin main"
        echo ""
        echo "3. First time push to empty repo:"
        echo "   git push -u origin main --force"
    fi
else
    echo "❌ Push cancelled"
fi
