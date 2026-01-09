# 🧪 Server Monitor - Test Guide

**Version:** 2.0.0  
**Last Updated:** 2026-01-07

This guide covers testing procedures for both backend and frontend components.

---

## 📋 Overview

### Testing Stack

**Backend:**
- Python pytest
- Coverage: 23/25 tests (92%)
- Security scan: bandit

**Frontend:**
- TypeScript + ESLint
- Production build test
- Manual smoke testing (see SMOKE_TEST_CHECKLIST.md)

---

## 🐍 Backend Testing

### Prerequisites

```bash
cd tests
pip3 install -r requirements.txt
```

### Running Tests

**All Tests:**
```bash
cd tests
python3 -m pytest -v
```

**API Tests Only:**
```bash
python3 -m pytest test_api.py -v
```

**Security Tests Only:**
```bash
python3 -m pytest test_security.py -v
```

**With Coverage:**
```bash
python3 -m pytest --cov=../backend --cov-report=html
```

### Test Categories

#### 1. Authentication Tests (5 tests)
```bash
python3 -m pytest test_api.py::TestAuthentication -v
```

Tests:
- Login with valid credentials
- Login with invalid credentials
- Token verification
- Logout
- Session expiration

#### 2. Server CRUD Tests (5 tests)
```bash
python3 -m pytest test_api.py::TestServerCRUD -v
```

Tests:
- List servers
- Add new server
- Get server details
- Update server
- Delete server

#### 3. Export Tests (2 tests)
```bash
python3 -m pytest test_api.py::TestExport -v
```

Tests:
- Export servers to CSV
- Export servers to JSON

#### 4. Security Tests (6 tests)
```bash
python3 -m pytest test_security.py -v
```

Tests:
- Rate limiting (general)
- Rate limiting (login)
- Security headers
- Input validation (IP addresses)
- Input validation (ports)
- CORS headers

### Expected Results

```
test_api.py::TestAuthentication::test_login_success          PASSED
test_api.py::TestAuthentication::test_login_failure          PASSED
test_api.py::TestAuthentication::test_verify_token           PASSED
test_api.py::TestAuthentication::test_logout                 PASSED
test_api.py::TestAuthentication::test_session_expiry         PASSED
test_api.py::TestServerCRUD::test_list_servers              PASSED
test_api.py::TestServerCRUD::test_add_server                PASSED
test_api.py::TestServerCRUD::test_get_server                PASSED
test_api.py::TestServerCRUD::test_update_server             PASSED
test_api.py::TestServerCRUD::test_delete_server             PASSED
test_api.py::TestExport::test_export_csv                    PASSED
test_api.py::TestExport::test_export_json                   PASSED
test_security.py::TestSecurity::test_rate_limiting           PASSED
test_security.py::TestSecurity::test_login_rate_limiting     PASSED
test_security.py::TestSecurity::test_security_headers        PASSED
test_security.py::TestSecurity::test_input_validation_ip     PASSED
test_security.py::TestSecurity::test_input_validation_port   PASSED
test_security.py::TestSecurity::test_cors                    PASSED

====================== 23 passed in 5.23s ======================
```

### Security Scanning

```bash
# Install bandit
pip install bandit

# Run security scan
bandit -r ../backend -x tests --severity-level medium -f txt
```

---

## ⚛️ Frontend Testing (Next.js)

### Prerequisites

```bash
cd frontend-next
npm ci
```

### Linting

```bash
# Run ESLint
npm run lint

# Auto-fix linting issues
npm run lint -- --fix
```

### Type Checking

```bash
# TypeScript compilation check
npx tsc --noEmit
```

### Build Test

```bash
# Build for production
npm run build

# Expected output:
# ✓ Compiled successfully
# ✓ Collecting page data
# ✓ Generating static pages
# ✓ Finalizing page optimization
```

### Development Server

```bash
# Start dev server
npm run dev

# Server starts on http://localhost:9081
```

### Production Server

```bash
# Build first
npm run build

# Start production server
npm run start
```

---

## 🔍 Manual Testing

### Comprehensive Smoke Testing

For detailed manual testing procedures, see **[SMOKE_TEST_CHECKLIST.md](SMOKE_TEST_CHECKLIST.md)**

Key areas to test:
- Authentication flows
- Dashboard functionality  
- Real-time WebSocket updates
- Terminal WebSocket
- Server CRUD operations
- Settings pages
- User management (admin)
- Role-based access control
- Exports (CSV/JSON)

### Quick Smoke Test (5 minutes)

```bash
# 1. Start all services
./start-all.sh

# 2. Start frontend
cd frontend-next
npm run build && npm run start

# 3. Open browser
open http://localhost:9081

# 4. Test checklist:
# - [ ] Login (admin/admin123)
# - [ ] Dashboard loads
# - [ ] Add server works
# - [ ] Real-time metrics update
# - [ ] Terminal opens
# - [ ] Export CSV works
# - [ ] Logout works
```

---

## 🚀 CI/CD Testing

### GitHub Actions Workflows

**Backend CI** (.github/workflows/ci.yml):
```yaml
- Lint Python code (flake8)
- Run unit tests (pytest)
- Security scan (bandit)
```

**Frontend CI** (.github/workflows/frontend-ci.yml):
```yaml
- Lint TypeScript (ESLint)
- Build Next.js app
- Verify build artifacts
```

### Triggering CI

```bash
# Push to main or develop branch
git push origin main

# Or create pull request
git checkout -b feature/new-feature
git push origin feature/new-feature
# Create PR on GitHub
```

### CI Status

Check status at:
- https://github.com/minhtuancn/server-monitor/actions

---

## 🐛 Troubleshooting Tests

### Backend Tests Failing

**Issue: Database errors**
```bash
# Reinitialize test database (from project root)
python3 -c "import sys; sys.path.insert(0, 'backend'); import database; database.init_database()"
```

**Issue: Port already in use**
```bash
# Kill existing processes
pkill -f central_api.py
pkill -f websocket_server.py
pkill -f terminal.py
```

**Issue: Import errors**
```bash
# Ensure backend dependencies installed (from project root)
pip3 install -r backend/requirements.txt
```

### Frontend Tests Failing

**Issue: Build fails**
```bash
# Clear cache
cd frontend-next
rm -rf .next node_modules
npm install
npm run build
```

**Issue: Lint errors**
```bash
# Auto-fix lint issues
npm run lint -- --fix
```

**Issue: Type errors**
```bash
# Check types
npx tsc --noEmit
# Fix type errors in code
```

---

## 📊 Test Coverage Reports

### Backend Coverage

```bash
cd tests
python3 -m pytest --cov=../backend --cov-report=html

# View report
open htmlcov/index.html
```

### Current Coverage

- **Overall:** 82%
- **Authentication:** 95%
- **Server Management:** 88%
- **Security:** 76%
- **Exports:** 90%

---

## ✅ Test Checklist Before Release

### Backend
- [ ] All pytest tests pass
- [ ] Security scan shows no critical issues
- [ ] Coverage > 80%
- [ ] No flake8 errors (E9, F63, F7, F82)

### Frontend
- [ ] ESLint passes with no errors
- [ ] TypeScript compilation succeeds
- [ ] Production build completes
- [ ] Smoke test checklist completed

### Integration
- [ ] Login/logout flow works
- [ ] WebSocket connections stable
- [ ] Terminal works end-to-end
- [ ] RBAC enforced correctly
- [ ] No console errors in browser
- [ ] No memory leaks (check DevTools)

### Documentation
- [ ] CHANGELOG.md updated
- [ ] README.md reflects current state
- [ ] DEPLOYMENT.md accurate
- [ ] SMOKE_TEST_CHECKLIST.md complete

---

## 🎯 Testing Best Practices

1. **Test Early, Test Often:** Run tests before committing
2. **Write Tests First:** For new features, write tests first (TDD)
3. **Keep Tests Independent:** No test should depend on another
4. **Use Descriptive Names:** Test names should describe what they test
5. **Mock External Dependencies:** Don't hit real servers in tests
6. **Clean Up After Tests:** Always clean up test data
7. **Run Full Suite Before PR:** Ensure nothing breaks

---

## 📝 Adding New Tests

### Backend Test Template

```python
# tests/test_new_feature.py
import pytest
from backend import central_api

class TestNewFeature:
    def test_feature_success(self):
        # Arrange
        ...
        
        # Act
        result = feature_function()
        
        # Assert
        assert result == expected
    
    def test_feature_failure(self):
        # Test error cases
        ...
```

### Frontend Testing (Future)

Consider adding:
- Jest for unit tests
- React Testing Library for component tests
- Playwright/Cypress for E2E tests

---

**Last Updated:** 2026-01-07

**Mobile (<768px):**
- [ ] Sidebar collapse mặc định
- [ ] Toggle sidebar button xuất hiện
- [ ] Stats cards 1 column

## 🔍 Test API Endpoints

### Test Login API
```bash
curl -X POST http://172.22.0.103:9083/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Kết quả mong đợi:**
```json
{
  "success": true,
  "token": "eyJ...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "permissions": ["*"]
  }
}
```

### Test Get Servers
```bash
# Lấy token từ login response
TOKEN="eyJ..."

curl -X GET http://172.22.0.103:9083/api/servers \
  -H "Authorization: Bearer $TOKEN"
```

### Test Get Users (Admin Only)
```bash
curl -X GET http://172.22.0.103:9083/api/users \
  -H "Authorization: Bearer $TOKEN"
```

## 🐛 Troubleshooting

### Nếu Login Không Hoạt Động:
1. Check API server đang chạy:
   ```bash
   ps aux | grep central_api
   ```

2. Check logs:
   ```bash
   tail -f /opt/server-monitor-dev/logs/api.log
   ```

3. Test API trực tiếp bằng curl (xem trên)

### Nếu i18n Không Hiển Thị:
1. Mở Developer Tools (F12)
2. Check Console tab có lỗi không
3. Check Network tab - file .json có load không:
   - `/assets/locales/en.json`
   - `/assets/locales/vi.json`
   - etc.

4. Check localStorage:
   ```javascript
   localStorage.getItem('language')
   ```

### Nếu Components Không Load:
1. Check Network tab trong DevTools
2. Verify files tồn tại:
   ```bash
   ls -la /opt/server-monitor-dev/frontend/components/
   ```

3. Check console errors

### Nếu Sidebar Không Hiển Thị:
1. Check CSS variables trong themes.css
2. Verify components.css loaded
3. Check app-main class có `with-sidebar`

## 📊 Các Trang Đã Hoàn Thành

| Trang | Layout | i18n | Components | Status |
|-------|--------|------|------------|--------|
| login.html | ✅ | ✅ | N/A | ✅ Done |
| dashboard.html | ✅ | ✅ | ✅ | ✅ Done |
| users.html | ⏳ | ⏳ | ⏳ | 🔄 In Progress |
| settings.html | ⏳ | ⏳ | ⏳ | 🔄 In Progress |

## 🎯 Next Steps

1. **Update users.html:**
   - Remove old header HTML
   - Add dynamic component loading
   - Use new layout classes
   - Add more data-i18n attributes

2. **Update settings.html:**
   - Same as users.html
   - Integrate with new layout

3. **Continue Phase 2 Features:**
   - SSL/Domain Management
   - Notification System
   - Server Notes with Markdown
   - Enhanced Server Grouping

## 📝 Quick Command Reference

```bash
# Start all services
cd /opt/server-monitor-dev
./start-all.sh

# Stop all services
./stop-dev.sh

# Check service status
ps aux | grep -E "(central_api|status_webserver)"

# View API logs
tail -f logs/api.log

# View frontend logs
tail -f logs/webserver.log

# Git status
git status

# Commit changes
git add -A && git commit -m "message" && git push
```

## ✅ Test Checklist

Hoàn thành các bước sau để verify hệ thống:

- [ ] Login thành công với admin/admin123
- [ ] Dashboard hiển thị đúng với header + sidebar
- [ ] Language switcher hoạt động (test 2-3 ngôn ngữ)
- [ ] Sidebar navigation hoạt động
- [ ] User menu dropdown hoạt động
- [ ] Stats cards hiển thị số liệu
- [ ] Server grid hiển thị servers
- [ ] Logout hoạt động
- [ ] Responsive design OK trên mobile/tablet
- [ ] Console không có lỗi JavaScript

**Nếu tất cả các bước trên PASS → Sẵn sàng tiếp tục Phase 2!** 🎉

