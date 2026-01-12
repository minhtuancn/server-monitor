# 🐙 Hướng Dẫn Kích Hoạt GitHub MCP trên LXC 231

## 📋 Tổng Quan

**LXC 231** là container dành riêng cho **Git operations** và **GitHub integration**. Để sử dụng GitHub MCP tạo Pull Request tự động, bạn cần:

1. ✅ Cài đặt GitHub CLI (`gh`)
2. ✅ Xác thực với GitHub token
3. ✅ Cấu hình Git
4. ✅ Test kết nối

---

## 🚀 Bước 1: SSH vào LXC 231

```bash
# Từ máy host, SSH vào LXC 231
ssh root@172.22.0.231

# Hoặc nếu đang ở LXC 230
ssh root@172.22.0.231
```

**Kiểm tra môi trường:**
```bash
# Check hostname
hostname
# Kết quả: lxc231 hoặc github-mcp

# Check IP
ip addr show eth0
# Kết quả: inet 172.22.0.231/24
```

---

## 🔧 Bước 2: Cài Đặt GitHub CLI

### Option A: Cài qua Package Manager (Recommended)

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install gh -y

# Verify installation
gh --version
# Kết quả mong đợi: gh version 2.x.x
```

### Option B: Cài từ Source (Nếu Option A không work)

```bash
# Download latest release
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

sudo apt update
sudo apt install gh
```

---

## 🔑 Bước 3: Xác Thực với GitHub Token

### 3.1: Tạo GitHub Personal Access Token (Nếu chưa có)

1. Truy cập: https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Cấu hình token:
   - **Note**: `server-monitor-lxc231-mcp`
   - **Expiration**: 90 days (hoặc No expiration)
   - **Scopes** (chọn các quyền sau):
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
     - ✅ `write:packages` (Upload packages)
     - ✅ `read:org` (Read org membership)
4. Click **Generate token**
5. **LƯU LẠI TOKEN** (chỉ hiện 1 lần): `ghp_xxxxxxxxxxxxxxxxxxxx`

### 3.2: Xác Thực GitHub CLI với Token

```bash
# Method 1: Interactive authentication
gh auth login

# Chọn các options:
# ? What account do you want to log into? → GitHub.com
# ? What is your preferred protocol for Git operations? → HTTPS
# ? Authenticate Git with your GitHub credentials? → Yes
# ? How would you like to authenticate GitHub CLI? → Paste an authentication token

# Paste token vừa tạo: ghp_xxxxxxxxxxxxxxxxxxxx
```

**Hoặc Method 2: Set token trực tiếp**

```bash
# Set token as environment variable
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

# Authenticate
echo "$GITHUB_TOKEN" | gh auth login --with-token

# Verify authentication
gh auth status
```

**Kết quả mong đợi:**
```
✓ Logged in to github.com as minhtuancn (...)
✓ Git operations for github.com configured to use https protocol.
✓ Token: ghp_************************************
```

---

## ⚙️ Bước 4: Cấu Hình Git

```bash
# Set git user (thay YOUR_NAME và YOUR_EMAIL)
git config --global user.name "minhtuancn"
git config --global user.email "your.email@example.com"

# Enable credential helper
git config --global credential.helper store

# Verify configuration
git config --global --list
```

**Kết quả mong đợi:**
```
user.name=minhtuancn
user.email=your.email@example.com
credential.helper=store
```

---

## 🧪 Bước 5: Test GitHub MCP

### 5.1: Clone Repository

```bash
# Create workspace directory
mkdir -p /opt/workspace
cd /opt/workspace

# Clone server-monitor repository
# (Thay YOUR_GITHUB_USERNAME bằng username của bạn)
gh repo clone YOUR_GITHUB_USERNAME/server-monitor

# Hoặc dùng git clone
git clone https://github.com/YOUR_GITHUB_USERNAME/server-monitor.git

cd server-monitor
```

### 5.2: Test Git Push (Dry Run)

```bash
# Check current branch
git branch -a

# Create test branch
git checkout -b test-github-mcp

# Create dummy file
echo "Test GitHub MCP on LXC 231" > test-mcp.txt
git add test-mcp.txt
git commit -m "test: GitHub MCP connection"

# Push to GitHub (this will test authentication)
git push -u origin test-github-mcp
```

**Nếu thành công:**
```
Enumerating objects: 4, done.
Counting objects: 100% (4/4), done.
Writing objects: 100% (3/3), 302 bytes | 302.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0)
To https://github.com/YOUR_USERNAME/server-monitor.git
 * [new branch]      test-github-mcp -> test-github-mcp
```

### 5.3: Test GitHub CLI PR Creation

```bash
# Create test PR
gh pr create \
  --title "Test: GitHub MCP on LXC 231" \
  --body "Testing automated PR creation from LXC 231" \
  --head test-github-mcp \
  --base main

# List PRs
gh pr list

# Close test PR (cleanup)
gh pr close test-github-mcp --delete-branch
```

---

## 🎯 Bước 6: Sử Dụng GitHub MCP cho Server Monitor

### 6.1: Clone/Update Project Repository

```bash
cd /opt/workspace

# If not cloned yet
gh repo clone YOUR_GITHUB_USERNAME/server-monitor

# Or update existing repo
cd server-monitor
git fetch --all
git pull origin main
```

### 6.2: Add Remote từ LXC 230 (Development Container)

**Trên LXC 230 (nơi bạn đang code):**

```bash
cd /opt/server-monitor

# Add LXC 231 as remote (for pushing)
git remote add lxc231 root@172.22.0.231:/opt/workspace/server-monitor

# Or set up SSH key-based authentication
ssh-copy-id root@172.22.0.231

# Push branch to LXC 231
git push lxc231 feature/mobile-responsive-accessibility-e2e-tests
```

**Trên LXC 231:**

```bash
cd /opt/workspace/server-monitor

# Checkout the branch
git checkout feature/mobile-responsive-accessibility-e2e-tests

# Push to GitHub
git push -u origin feature/mobile-responsive-accessibility-e2e-tests

# Create PR using gh CLI
gh pr create \
  --title "feat: Mobile Responsive Design + ARIA Accessibility + E2E Tests" \
  --body-file /opt/server-monitor/PULL_REQUEST_TEMPLATE.md \
  --head feature/mobile-responsive-accessibility-e2e-tests \
  --base main
```

---

## 🔄 Bước 7: Tự Động Hóa Workflow (Optional)

### 7.1: Tạo Script Push & PR

**Trên LXC 231, tạo file `/usr/local/bin/create-pr.sh`:**

```bash
#!/bin/bash
set -e

# Configuration
REPO_PATH="/opt/workspace/server-monitor"
BRANCH_NAME="$1"
PR_TITLE="$2"
PR_BODY_FILE="${3:-/opt/server-monitor/PULL_REQUEST_TEMPLATE.md}"

# Validate arguments
if [ -z "$BRANCH_NAME" ] || [ -z "$PR_TITLE" ]; then
  echo "Usage: create-pr.sh <branch-name> <pr-title> [pr-body-file]"
  exit 1
fi

# Navigate to repository
cd "$REPO_PATH"

# Fetch latest changes
echo "📥 Fetching latest changes..."
git fetch --all

# Checkout branch
echo "🔀 Checking out branch: $BRANCH_NAME"
git checkout "$BRANCH_NAME"

# Pull latest commits
echo "⬇️ Pulling latest commits..."
git pull origin "$BRANCH_NAME" || echo "Branch does not exist on remote yet"

# Push to GitHub
echo "⬆️ Pushing to GitHub..."
git push -u origin "$BRANCH_NAME"

# Create PR
echo "🚀 Creating pull request..."
if [ -f "$PR_BODY_FILE" ]; then
  gh pr create \
    --title "$PR_TITLE" \
    --body-file "$PR_BODY_FILE" \
    --head "$BRANCH_NAME" \
    --base main
else
  gh pr create \
    --title "$PR_TITLE" \
    --body "Automated PR creation from LXC 231" \
    --head "$BRANCH_NAME" \
    --base main
fi

# Get PR URL
PR_URL=$(gh pr view "$BRANCH_NAME" --json url -q .url)
echo "✅ Pull request created: $PR_URL"
```

**Cấp quyền thực thi:**

```bash
chmod +x /usr/local/bin/create-pr.sh
```

**Sử dụng:**

```bash
# From LXC 231
create-pr.sh feature/mobile-responsive-accessibility-e2e-tests \
  "feat: Mobile Responsive Design + ARIA Accessibility + E2E Tests" \
  /opt/server-monitor/PULL_REQUEST_TEMPLATE.md
```

### 7.2: SSH Command từ LXC 230

**Trên LXC 230, bạn có thể chạy:**

```bash
# Push và tạo PR một lệnh
ssh root@172.22.0.231 "bash -c '\
  cd /opt/workspace/server-monitor && \
  git fetch --all && \
  git checkout feature/mobile-responsive-accessibility-e2e-tests && \
  git pull origin feature/mobile-responsive-accessibility-e2e-tests || true && \
  git push -u origin feature/mobile-responsive-accessibility-e2e-tests && \
  gh pr create --title \"feat: Mobile Responsive + ARIA + E2E Tests\" --body-file PULL_REQUEST_TEMPLATE.md --head feature/mobile-responsive-accessibility-e2e-tests --base main
'"
```

---

## 📊 Kiểm Tra Trạng Thái MCP Servers

### Tất Cả MCPs trong Dự Án:

| LXC | MCP Server | Purpose | Status | Port |
|-----|------------|---------|--------|------|
| **230** | Filesystem MCP | File operations, code editing | ✅ Active | - |
| **231** | GitHub MCP | Git operations, PR creation | ⏳ Setup needed | - |
| **232** | Database MCP | PostgreSQL, SQLite operations | ✅ Available | 5432 |
| **233** | Playwright MCP | E2E testing, screenshots | ✅ Active | - |
| **234** | Monitoring MCP | Cockpit, system monitoring | ✅ Active | 9090 |

### Kiểm Tra Từng MCP:

```bash
# LXC 230 - Filesystem MCP
ssh root@172.22.0.230 "ls -la /opt/server-monitor"

# LXC 231 - GitHub MCP
ssh root@172.22.0.231 "gh auth status"

# LXC 232 - Database MCP
ssh root@172.22.0.232 "psql --version && sqlite3 --version"

# LXC 233 - Playwright MCP
ssh root@172.22.0.233 "npx playwright --version"

# LXC 234 - Monitoring MCP
curl http://172.22.0.234:9090
```

---

## ✅ Checklist Hoàn Thành

**Sau khi làm theo hướng dẫn, check các items sau:**

- [ ] GitHub CLI installed (`gh --version`)
- [ ] GitHub token authenticated (`gh auth status`)
- [ ] Git configured (`git config --global --list`)
- [ ] Test repository cloned
- [ ] Test branch pushed successfully
- [ ] Test PR created and closed
- [ ] Server-monitor repository accessible
- [ ] Feature branch pushed to GitHub
- [ ] PR creation script working

---

## 🐛 Troubleshooting

### Issue 1: `gh: command not found`

```bash
# Reinstall GitHub CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh
```

### Issue 2: Authentication failed

```bash
# Re-authenticate
gh auth logout
gh auth login

# Or use token directly
export GITHUB_TOKEN="your_token_here"
echo "$GITHUB_TOKEN" | gh auth login --with-token
```

### Issue 3: Permission denied (publickey)

```bash
# Generate SSH key on LXC 231
ssh-keygen -t ed25519 -C "lxc231-github-mcp"

# Add to GitHub: https://github.com/settings/keys
cat ~/.ssh/id_ed25519.pub

# Test SSH connection
ssh -T git@github.com
```

### Issue 4: Repository not found

```bash
# Check repository URL
gh repo view YOUR_USERNAME/server-monitor

# Clone with correct URL
gh repo clone YOUR_USERNAME/server-monitor
```

---

## 🎯 Next Steps - Tạo PR cho Server Monitor

**Bây giờ bạn đã setup xong GitHub MCP, hãy:**

1. **Push branch to GitHub:**
```bash
ssh root@172.22.0.231
cd /opt/workspace/server-monitor
git checkout feature/mobile-responsive-accessibility-e2e-tests
git push -u origin feature/mobile-responsive-accessibility-e2e-tests
```

2. **Create Pull Request:**
```bash
gh pr create \
  --title "feat: Mobile Responsive Design + ARIA Accessibility + E2E Testing Infrastructure" \
  --body-file PULL_REQUEST_TEMPLATE.md
```

3. **Verify PR created:**
```bash
gh pr list
gh pr view feature/mobile-responsive-accessibility-e2e-tests --web
```

---

## 📚 Related Documentation

- [GITHUB_PR_GUIDE.md](../../GITHUB_PR_GUIDE.md) - Step-by-step guide for creating pull requests
- [PULL_REQUEST_TEMPLATE.md](../../PULL_REQUEST_TEMPLATE.md) - PR template
- [AGENTS.md](../../AGENTS.md) - Development guidelines
- [DEPLOYMENT.md](../../docs/getting-started/DEPLOYMENT.md) - Deployment guide

---

**Created**: 2026-01-12  
**Last Updated**: 2026-01-12  
**Maintainer**: Server Monitor Team
