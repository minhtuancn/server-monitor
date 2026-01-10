# Báo Cáo Triển Khai: Cài Đặt Hệ Thống & Quản Lý Nhóm

**Ngày:** 2026-01-11  
**Tính năng:** Settings UI nâng cấp + Quản lý nhóm (Groups)

---

## 1. Trang Settings Đã Được Nâng Cấp ✅

### Trước đây

- Hiển thị thô tất cả settings dạng key-value
- Không có phân loại
- Thiếu các tính năng định dạng ngày giờ, ngôn ngữ, v.v.

### Sau khi cải tiến

**File:** `/opt/server-monitor/frontend-next/src/app/[locale]/(dashboard)/settings/page.tsx`

**4 Tab chính:**

#### Tab 1: General Settings

- System Name (Tên hệ thống)
- Admin Email
- Timezone (Múi giờ) - 8 lựa chọn:
  - UTC
  - America/New York (EST)
  - America/Los Angeles (PST)
  - Europe/London (GMT)
  - Europe/Paris (CET)
  - Asia/Tokyo (JST)
  - **Asia/Ho Chi Minh (ICT)** ✅
  - Asia/Shanghai (CST)
- Session Timeout (phút)

#### Tab 2: Localization Settings (Bản địa hóa)

- **Default Language** (Ngôn ngữ mặc định):
  - English, Tiếng Việt, Français, Español, Deutsch, 日本語, 한국어, 简体中文
- **Date Format** (Định dạng ngày):
  - YYYY-MM-DD (2026-01-10)
  - DD/MM/YYYY (10/01/2026)
  - MM/DD/YYYY (01/10/2026)
  - DD-MM-YYYY (10-01-2026)
  - YYYY 年 MM 月 DD 日 (2026 年 01 月 10 日)
- **Time Format** (Định dạng giờ):
  - 24-hour (23:59)
  - 12-hour (11:59 PM)
- **Number Format** (Định dạng số):
  - 1,234.56 (Dấu phẩy phân cách nghìn, dấu chấm thập phân)
  - 1.234,56 (Dấu chấm phân cách nghìn, dấu phẩy thập phân)
  - 1 234,56 (Dấu cách phân cách nghìn, dấu phẩy thập phân)
  - 1234.56 (Không phân cách)
- **Currency** (Tiền tệ):
  - USD ($), EUR (€), GBP (£), **VND (₫)** ✅, JPY (¥), CNY (¥)
- **First Day of Week** (Ngày đầu tuần):
  - Sunday, Monday

#### Tab 3: Database Management

- Link đến trang `/settings/database` (đã có sẵn)
- Tính năng: Backup, Restore, Health monitoring

#### Tab 4: Groups Management

- 4 loại nhóm:
  1. **Server Groups** - Phân loại servers (Production, Staging, Development)
  2. **Note Groups** - Phân loại ghi chú theo chủ đề
  3. **Command Snippets** - Phân loại lệnh terminal
  4. **Inventory Groups** - Phân loại thiết bị

---

## 2. Tính Năng Quản Lý Nhóm (Groups) ✅

### Backend Changes

**File:** `/opt/server-monitor/backend/database.py`

**Bảng mới: `groups`**

```sql
CREATE TABLE groups (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL,           -- 'servers', 'notes', 'snippets', 'inventory'
    color TEXT DEFAULT '#1976d2',
    created_by INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(name, type)            -- Tên nhóm không trùng trong cùng loại
)
```

**Bảng mới: `group_memberships`**

```sql
CREATE TABLE group_memberships (
    id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    item_type TEXT NOT NULL,      -- 'server', 'note', 'snippet', 'inventory'
    added_at TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    UNIQUE(group_id, item_id, item_type)
)
```

**File:** `/opt/server-monitor/backend/central_api.py`

**API Endpoints mới:**

1. **GET `/api/groups?type=servers`**

   - Lấy danh sách nhóm (có thể lọc theo type)
   - Trả về: groups với item_count (số lượng items trong nhóm)

2. **GET `/api/groups/:id`**

   - Lấy thông tin 1 nhóm cụ thể
   - Trả về: group details với item_count

3. **POST `/api/groups`**

   - Tạo nhóm mới
   - Body: `{name, description, type, color}`
   - Validation: type phải là 'servers', 'notes', 'snippets', hoặc 'inventory'

4. **PUT `/api/groups/:id`**

   - Cập nhật nhóm
   - Body: `{name, description, color}`

5. **DELETE `/api/groups/:id`**
   - Xóa nhóm (items không bị xóa, chỉ xóa nhóm)
   - Cascade delete group_memberships

### Frontend UI

**File:** `/opt/server-monitor/frontend-next/src/app/[locale]/(dashboard)/settings/groups/page.tsx`

**Tính năng:**

- 4 tabs cho 4 loại nhóm
- Bảng hiển thị:
  - Color box (màu nhóm)
  - Name (tên nhóm)
  - Description (mô tả)
  - Items count (số lượng items)
  - Created date
  - Actions (Edit, Delete)
- Dialog thêm/sửa nhóm:
  - Tên nhóm (bắt buộc)
  - Mô tả
  - **Color picker** với 10 màu preset:
    - Blue, Green, Orange, Red, Purple
    - Light Blue, Deep Orange, Deep Purple, Pink, Teal
- Validation: Tên nhóm không được trùng trong cùng loại

---

## 3. Cấu Trúc Route Mới

```
/settings
  ├─ Tab 1: General (System name, timezone, session timeout)
  ├─ Tab 2: Localization (Language, date format, time format, number format)
  ├─ Tab 3: Database → Link to /settings/database
  └─ Tab 4: Groups → Link to /settings/groups

/settings/groups?type=servers
  ├─ Tab 1: Server Groups
  ├─ Tab 2: Note Groups
  ├─ Tab 3: Command Snippets
  └─ Tab 4: Inventory Groups
```

---

## 4. Hướng Dẫn Sử Dụng

### Cấu hình Settings

```bash
# 1. Truy cập Settings
http://localhost:9081/en/settings

# 2. Tab General
- Đặt tên hệ thống: "Server Monitor - Production"
- Chọn timezone: Asia/Ho Chi Minh
- Click "Save General Settings"

# 3. Tab Localization
- Default Language: Tiếng Việt
- Date Format: DD/MM/YYYY
- Number Format: 1.234,56
- Currency: VND (₫)
- Click "Save Localization Settings"
```

### Quản lý nhóm (Groups)

```bash
# 1. Từ Settings → Tab Groups → Click vào loại nhóm muốn quản lý

# 2. Tạo Server Groups
http://localhost:9081/en/settings/groups?type=servers
- Click "Add Group"
- Name: "Production Servers"
- Description: "All production environment servers"
- Color: Chọn màu xanh lá (#2e7d32)
- Click "Create"

# 3. Tạo thêm nhóm khác
- Staging Servers (màu cam)
- Development Servers (màu xanh dương)
- Database Servers (màu đỏ)
- Web Servers (màu tím)

# 4. Tương tự cho Note Groups, Command Snippets, Inventory Groups
```

---

## 5. Kiểm Tra Database

```bash
# Kiểm tra bảng groups
sqlite3 data/servers.db
SELECT * FROM groups;

# Kết quả mong đợi:
# id | name                | description                  | type      | color     | created_by | created_at
# 1  | Production Servers  | All production environment   | servers   | #2e7d32   | 1          | 2026-01-11...
# 2  | Staging Servers     | Staging environment          | servers   | #ed6c02   | 1          | 2026-01-11...
# 3  | System Commands     | System administration        | snippets  | #1976d2   | 1          | 2026-01-11...

# Kiểm tra settings
SELECT * FROM settings WHERE key LIKE 'default_language' OR key LIKE 'timezone';
```

---

## 6. Tính Năng Sẽ Triển Khai Tiếp (Phase 2)

### Gắn Items vào Groups

1. **Server Groups:**

   - Thêm dropdown "Group" vào form Add/Edit Server
   - Hiển thị group badge trên server card
   - Filter servers theo group trên dashboard

2. **Note Groups:**

   - Dropdown group khi tạo note
   - Color-coded notes theo group
   - Filter notes theo group

3. **Command Snippet Groups:**

   - Dropdown category → group
   - Organized sidebar theo groups
   - Quick filter

4. **Inventory Groups:**
   - Phân loại thiết bị (Hardware, Software, Network)
   - Filter inventory theo group

### API Endpoints Phase 2

```
POST /api/groups/:id/members
  Body: {item_id, item_type}

DELETE /api/groups/:id/members/:item_id

GET /api/groups/:id/members
  Response: [{item_id, item_type, item_details}]
```

---

## 7. Files Modified Summary

### Backend (2 files)

1. `backend/database.py`

   - Thêm bảng `groups`
   - Thêm bảng `group_memberships`

2. `backend/central_api.py`
   - GET `/api/groups` (với filter ?type=)
   - GET `/api/groups/:id`
   - POST `/api/groups`
   - PUT `/api/groups/:id`
   - DELETE `/api/groups/:id`

### Frontend (2 files)

1. `frontend-next/src/app/[locale]/(dashboard)/settings/page.tsx`

   - Thay thế hoàn toàn với 4 tabs
   - General, Localization, Database, Groups

2. `frontend-next/src/app/[locale]/(dashboard)/settings/groups/page.tsx` (MỚI)
   - 4 tabs cho 4 loại groups
   - CRUD interface với color picker

---

## 8. Migration Notes

### Automatic Database Migration

- Bảng `groups` và `group_memberships` sẽ tự động tạo khi restart backend
- Không cần chạy SQL thủ công

### No Breaking Changes

- Settings cũ vẫn hoạt động (backward compatible)
- Groups là tính năng mới, không ảnh hưởng code cũ

---

## 9. Testing Checklist

```bash
✅ Settings page loads without errors
✅ General tab: Timezone selector works
✅ Localization tab: All dropdowns work
✅ Database tab: Link to /settings/database works
✅ Groups tab: 4 cards displayed correctly
✅ Groups page: 4 tabs work
✅ Create group: Form validation works
✅ Edit group: Pre-fills data correctly
✅ Delete group: Confirmation dialog appears
✅ Color picker: 10 colors selectable
✅ Item count: Shows 0 for new groups
✅ Unique constraint: Can't create duplicate group names in same type
```

---

## 10. Copilot Prompt cho Phase 2

```
Phase 2: Gắn items vào groups

1. Server Groups:
   - Thêm cột group_id vào bảng servers
   - Thêm dropdown "Group" trong form Add/Edit Server
   - Hiển thị group badge màu trên server card
   - Thêm filter "Group" trên dashboard
   - API: GET /api/servers?group_id=1

2. Note Groups:
   - Thêm cột group_id vào bảng server_notes
   - Dropdown group khi create/edit note
   - Color-coded note cards theo group.color
   - Filter notes theo group

3. Command Snippets:
   - Replace category field với group_id
   - Organized sidebar theo groups
   - API: GET /api/snippets?group_id=3

4. Inventory Groups:
   - Thêm group classification
   - Filter inventory items
   - Group-based reports
```

---

**Kết luận:**  
✅ Settings page đã được nâng cấp với đầy đủ tính năng định dạng ngày giờ, ngôn ngữ, số, tiền tệ  
✅ Hệ thống quản lý nhóm hoàn chỉnh với backend + frontend  
✅ Sẵn sàng cho Phase 2: Gắn items vào groups

**Lỗi Settings đã được sửa:** Trang settings bây giờ có UI hoàn chỉnh thay vì chỉ hiển thị raw key-value pairs.
