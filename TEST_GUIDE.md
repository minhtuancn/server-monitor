# 🎉 Hướng Dẫn Test Giao Diện Server Monitor

## ✅ Trạng Thái Hiện Tại

### Backend Services (Đang Chạy)
- **API Server**: http://172.22.0.103:9083 ✅
- **Frontend Server**: http://172.22.0.103:9081 ✅
- **Terminal Server**: http://172.22.0.103:9084 ✅
- **WebSocket Server**: http://172.22.0.103:9085 ✅

### Đã Tích Hợp Hoàn Chỉnh
- ✅ **Login Page** (login.html) - i18n đầy đủ
- ✅ **Header Component** - Language switcher + User menu
- ✅ **Sidebar Component** - Navigation menu với 8 ngôn ngữ
- ✅ **Dashboard** (dashboard.html) - Layout mới với dynamic components

## 🚀 Hướng Dẫn Test

### 1. Test Login
```bash
# Mở trình duyệt:
http://172.22.0.103:9081/login.html

# Thông tin đăng nhập:
Username: admin
Password: admin123
```

**Kiểm tra:**
- [ ] Form login hiển thị đúng
- [ ] Nhập username và password
- [ ] Click "Login" thành công
- [ ] Redirect tự động sang dashboard

### 2. Test Dashboard
```bash
# Sau khi login, tự động vào:
http://172.22.0.103:9081/dashboard.html
```

**Kiểm tra:**
- [ ] Header hiển thị đúng (logo, navigation, language switcher, user menu)
- [ ] Sidebar hiển thị đúng (menu items, icons)
- [ ] Stats cards hiển thị (Total Servers, Online, Offline, Warning)
- [ ] Server grid hiển thị danh sách servers
- [ ] Responsive layout hoạt động

### 3. Test Language Switcher
**Trong Dashboard:**
- [ ] Click vào language dropdown (icon 🌐 trên header)
- [ ] Chọn ngôn ngữ khác (English, Tiếng Việt, 中文, 日本語, etc.)
- [ ] Page reload và hiển thị ngôn ngữ mới
- [ ] Check các elements:
  - Dashboard title
  - Stats card labels
  - Button text
  - Sidebar menu items

**8 Ngôn Ngữ Hỗ Trợ:**
1. 🇺🇸 English
2. 🇻🇳 Tiếng Việt
3. 🇨🇳 简体中文
4. 🇯🇵 日本語
5. 🇰🇷 한국어
6. 🇪🇸 Español
7. 🇫🇷 Français
8. 🇩🇪 Deutsch

### 4. Test Sidebar Navigation
**Click vào các menu items:**
- [ ] Dashboard - Reload dashboard page
- [ ] Servers - Navigate to servers list
- [ ] Terminal - Navigate to terminal page
- [ ] User Management (Admin only) - Navigate to users page
- [ ] System Settings (Admin only) - Navigate to settings page

### 5. Test Header Components
**User Menu (Click vào avatar/username):**
- [ ] Dropdown hiển thị
- [ ] Profile link
- [ ] Settings link
- [ ] Change Password button
- [ ] Logout button

**Change Password Modal:**
- [ ] Click "Change Password"
- [ ] Modal hiển thị
- [ ] Form với 3 fields (Current, New, Confirm Password)
- [ ] Validation hoạt động
- [ ] Submit thành công

### 6. Test Responsive Design
**Desktop (>1024px):**
- [ ] Sidebar hiển thị full width
- [ ] Header full width
- [ ] Stats cards 4 columns

**Tablet (768px - 1024px):**
- [ ] Sidebar có thể collapse
- [ ] Stats cards 2 columns

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

