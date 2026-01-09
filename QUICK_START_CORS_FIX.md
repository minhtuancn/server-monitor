# Quick Start Guide - CORS Fix and Offline Mode

## TL;DR - Hướng dẫn nhanh cho người dùng Việt

### Vấn đề đã được sửa:
✅ Lỗi CORS khi truy cập từ https://mon.go7s.net  
✅ Chạy offline không cần Internet  
✅ Hỗ trợ cả HTTP và HTTPS  

### Cách sử dụng:

#### 1. Chạy trên localhost
```bash
./start-all.sh
# Vào: http://localhost:9081/login.html
```

#### 2. Chạy với domain (ví dụ: https://mon.go7s.net)
```bash
# Bật CORS cho test
echo "CORS_ALLOW_ALL=true" >> .env

# Khởi động
./start-all.sh

# Cấu hình nginx (xem NGINX_PROXY_GUIDE.md)
```

### Kiểm tra:
```bash
# Chạy test tự động
./test-cors-fixes.sh
```

### Tài liệu:
- `HUONG_DAN_TIENG_VIET.md` - Hướng dẫn đầy đủ bằng tiếng Việt
- `NGINX_PROXY_GUIDE.md` - Cấu hình nginx
- `OFFLINE_MODE.md` - Hướng dẫn offline mode

---

## English Quick Start

### Issues Fixed:
✅ CORS errors when accessing from https://mon.go7s.net  
✅ Offline mode (no Internet required)  
✅ Support for both HTTP and HTTPS  

### Usage:

#### 1. Run on localhost
```bash
./start-all.sh
# Access: http://localhost:9081/login.html
```

#### 2. Run with custom domain (e.g., https://mon.go7s.net)
```bash
# Enable CORS for testing
echo "CORS_ALLOW_ALL=true" >> .env

# Start services
./start-all.sh

# Configure nginx (see NGINX_PROXY_GUIDE.md)
```

### Verify:
```bash
# Run automated tests
./test-cors-fixes.sh
```

### Documentation:
- `OFFLINE_MODE.md` - Complete offline mode guide
- `NGINX_PROXY_GUIDE.md` - Nginx reverse proxy setup
- `HUONG_DAN_TIENG_VIET.md` - Vietnamese guide

---

## What Changed?

### Backend
- ✅ CORS now allows any origin on port 9081
- ✅ Support for HTTP and HTTPS
- ✅ Added `CORS_ALLOW_ALL` for testing

### Frontend
- ✅ Font Awesome downloaded locally (no CDN)
- ✅ xterm.js downloaded locally (no CDN)
- ✅ All HTML files updated
- ✅ Auto-detect HTTP/HTTPS protocol

### Benefits
- ⚡ Faster (local assets)
- 🔒 More secure (no external requests)
- 📡 Works offline
- 🌐 Works with any domain/proxy

---

## Troubleshooting

### CORS errors?
```bash
echo "CORS_ALLOW_ALL=true" >> .env
./stop-all.sh && ./start-all.sh
```

### Assets not loading?
```bash
chmod -R 755 frontend/assets/vendor/
```

### Login not working?
```bash
# Check API is running
curl http://localhost:9083/api/health

# View logs
tail -f logs/api.log
```

### 502 Bad Gateway (nginx)?
```bash
# Restart services
./stop-all.sh && ./start-all.sh

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

---

## Verification Checklist

Open browser (F12 → Network tab):

- [ ] No requests to `cdnjs.cloudflare.com`
- [ ] All assets load from `/assets/vendor/`
- [ ] No CORS errors in Console
- [ ] Login works
- [ ] Icons display correctly
- [ ] Terminal works

---

## Security Note

**Development/Testing:**
```bash
CORS_ALLOW_ALL=true  # OK for testing
```

**Production:**
```bash
# Remove CORS_ALLOW_ALL from .env
# System automatically allows port 9081 origins
```

---

## Need Help?

1. Read `HUONG_DAN_TIENG_VIET.md` (Vietnamese)
2. Read `OFFLINE_MODE.md` (English)
3. Read `NGINX_PROXY_GUIDE.md` (Nginx setup)
4. Run `./test-cors-fixes.sh` to check configuration
5. Check logs: `tail -f logs/api.log`
