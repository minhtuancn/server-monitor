# Hướng Dẫn Sửa Lỗi CORS và Chế Độ Offline

## Tổng Quan

Tài liệu này hướng dẫn cách sửa lỗi CORS và chạy ứng dụng Server Monitor ở chế độ offline (không cần Internet).

## Các Thay Đổi Đã Thực Hiện

### 1. Sửa Lỗi CORS

**Vấn đề:** Khi truy cập từ https://mon.go7s.net, các yêu cầu API bị lỗi "CORS Failed"

**Giải pháp:**
- Cấu hình CORS tự động cho phép mọi nguồn gốc (origin) trên cổng 9081
- Hỗ trợ cả HTTP và HTTPS
- Cho phép tùy chọn `CORS_ALLOW_ALL=true` trong file `.env` để test

**Cách sử dụng:**

```bash
# Để test với bất kỳ domain nào (chỉ dùng khi phát triển)
echo "CORS_ALLOW_ALL=true" >> .env
./stop-all.sh
./start-all.sh
```

### 2. Chế Độ Offline (Không Cần CDN)

**Vấn đề:** Ứng dụng cần Internet để tải Font Awesome và xterm.js từ CDN

**Giải pháp:**
- Đã tải Font Awesome 6.4.0 về máy → `/frontend/assets/vendor/fontawesome/`
- Đã tải xterm.js 5.3.0 về máy → `/frontend/assets/vendor/xterm/`
- Cập nhật tất cả file HTML để dùng file local thay vì CDN

**Kết quả:**
- ✅ Không cần Internet để chạy ứng dụng
- ✅ Tất cả icon và giao diện hiển thị bình thường
- ✅ Terminal hoạt động offline

### 3. Tự Động Phát Hiện API URL

**Vấn đề:** API URL bị hard-code là `http://`, không hoạt động với HTTPS

**Giải pháp:**
- Cập nhật `auth.js` và `api.js` để tự động phát hiện protocol (HTTP/HTTPS)
- Tự động dùng cùng protocol với frontend
- Hỗ trợ override qua `window.API_BASE_URL`

## Hướng Dẫn Cài Đặt

### 1. Chạy Trên Localhost

```bash
# Clone repository (nếu chưa có)
git clone https://github.com/minhtuancn/server-monitor.git
cd server-monitor

# Tạo file .env (nếu chưa có)
cp .env.example .env

# Sinh secret keys
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))" >> .env
python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(24))" >> .env
python3 -c "import secrets; print('KEY_VAULT_MASTER_KEY=' + secrets.token_urlsafe(32))" >> .env

# Khởi động tất cả services
./start-all.sh

# Truy cập ứng dụng
# Frontend: http://localhost:9081
# API: http://localhost:9083
```

### 2. Chạy Với Nginx Proxy (Domain Tùy Chỉnh)

Nếu bạn muốn dùng domain như `https://mon.go7s.net`, xem file [NGINX_PROXY_GUIDE.md](NGINX_PROXY_GUIDE.md) để biết chi tiết.

**Tóm tắt:**

```bash
# 1. Cấu hình CORS (tùy chọn, chỉ khi cần test)
echo "CORS_ALLOW_ALL=true" >> .env

# 2. Khởi động Server Monitor
./start-all.sh

# 3. Cấu hình Nginx (xem NGINX_PROXY_GUIDE.md)
sudo nano /etc/nginx/sites-available/server-monitor
# (Copy config từ file guide)

# 4. Enable và reload nginx
sudo ln -s /etc/nginx/sites-available/server-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 5. Truy cập qua domain
# https://mon.go7s.net
```

## Kiểm Tra Kết Quả

### 1. Kiểm Tra Offline Mode

```bash
# Mở trình duyệt và vào http://localhost:9081/dashboard.html
# Nhấn F12 để mở DevTools → Tab Network
# Reload trang (Ctrl+R)

# Kiểm tra:
# ✅ Font Awesome tải từ /assets/vendor/fontawesome/
# ✅ KHÔNG có requests đến cdnjs.cloudflare.com
# ✅ Tất cả resources đều status 200
```

### 2. Kiểm Tra CORS

```bash
# Mở Console trong DevTools
# ✅ Không có lỗi "CORS Failed"
# ✅ API requests thành công
```

### 3. Kiểm Tra Login

```bash
# 1. Vào http://localhost:9081/login.html
# 2. Nhập username/password
# 3. Xem tab Network:
#    - POST đến /api/auth/login
#    - Status 200 (hoặc 401 nếu sai mật khẩu)
#    - Không có lỗi CORS
```

## Xử Lý Lỗi

### Lỗi: "CORS Failed"

```bash
# Giải pháp 1: Enable CORS_ALLOW_ALL
echo "CORS_ALLOW_ALL=true" >> .env
./stop-all.sh
./start-all.sh

# Giải pháp 2: Kiểm tra API đang chạy
curl http://localhost:9083/api/health

# Giải pháp 3: Xem log
tail -f logs/api.log
```

### Lỗi: Assets Không Tải (404)

```bash
# Kiểm tra file tồn tại
ls -la frontend/assets/vendor/fontawesome/css/
ls -la frontend/assets/vendor/xterm/lib/

# Set lại permissions
chmod -R 755 frontend/assets/vendor/

# Xóa cache trình duyệt và reload
```

### Lỗi: Login Không Thành Công

```bash
# Kiểm tra JWT_SECRET trong .env
grep JWT_SECRET .env

# Xem log API
tail -f logs/api.log

# Test API trực tiếp
curl -X POST http://localhost:9083/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'
```

### Lỗi: 502 Bad Gateway (Khi Dùng Nginx)

```bash
# Kiểm tra services đang chạy
curl http://localhost:9081
curl http://localhost:9083/api/health

# Restart services
./stop-all.sh
./start-all.sh

# Xem log nginx
sudo tail -f /var/log/nginx/error.log
```

## Cấu Trúc Thư Mục Assets

```
frontend/assets/vendor/
├── fontawesome/
│   ├── css/
│   │   └── all.min.css        # Font Awesome CSS
│   └── webfonts/
│       ├── fa-solid-900.woff2  # Font files
│       └── ...
└── xterm/
    ├── css/
    │   └── xterm.css           # xterm.js CSS
    ├── lib/
    │   └── xterm.js            # xterm.js library
    ├── addon-fit/
    │   └── xterm-addon-fit.js  # Fit addon
    └── addon-web-links/
        └── xterm-addon-web-links.js  # Web links addon
```

## Tính Năng Mới

### 1. CORS Linh Hoạt
- Tự động cho phép mọi origin trên cổng 9081
- Hỗ trợ cả HTTP và HTTPS
- Có thể enable `CORS_ALLOW_ALL` cho testing

### 2. Offline Mode
- Tất cả dependencies đã được download
- Không cần kết nối Internet
- Giảm thời gian load trang

### 3. Auto-detect Protocol
- Tự động dùng HTTP hoặc HTTPS tùy frontend
- Hỗ trợ reverse proxy (nginx, apache)
- Linh hoạt với mọi deployment

## Cấu Hình Bảo Mật (Production)

```bash
# 1. Tắt CORS_ALLOW_ALL (đừng dùng trong production)
# Xóa hoặc comment dòng CORS_ALLOW_ALL trong .env

# 2. Dùng HTTPS
# Cấu hình SSL certificate (Let's Encrypt)

# 3. Firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 9081/tcp  # Chặn truy cập trực tiếp
sudo ufw deny 9083/tcp
sudo ufw deny 9084/tcp
sudo ufw deny 9085/tcp

# 4. Secret keys mạnh
# Sinh lại secrets trong .env với độ dài lớn hơn
```

## Hỗ Trợ

Nếu gặp vấn đề:

1. Xem file log: `tail -f logs/api.log`
2. Kiểm tra console trình duyệt (F12)
3. Đọc [OFFLINE_MODE.md](OFFLINE_MODE.md) để biết thêm chi tiết
4. Đọc [NGINX_PROXY_GUIDE.md](NGINX_PROXY_GUIDE.md) cho cấu hình nginx

## Kết Luận

Với các thay đổi này:
- ✅ Sửa được lỗi CORS khi dùng domain khác
- ✅ Chạy được offline không cần Internet
- ✅ Hỗ trợ cả HTTP và HTTPS
- ✅ Linh hoạt với reverse proxy

**Lưu ý:** Khi deploy production, nhớ:
- Tắt `CORS_ALLOW_ALL`
- Dùng HTTPS
- Bảo mật các secret keys
- Cấu hình firewall
