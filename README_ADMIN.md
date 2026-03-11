# 🔐 Pop Assistant - Admin Panel

## Tổng quan

Hệ thống quản trị Pop Assistant với giao diện admin đầy đủ tính năng, được bảo vệ bằng **Admin Code**.

## 🎮 Cách truy cập Admin Panel

### Method 1: Admin Code (Ẩn)
1. Mở ứng dụng Pop Assistant (`python login.py`)
2. Tại màn hình đăng nhập, nhấn **3 lần phím Alt** liên tiếp:
   ```
   Alt + Alt + Alt (trong 2 giây)
   ```
3. Admin login panel sẽ tự động mở

### Method 2: Direct Access
```bash
python admin_login.py
```

## 🔑 Mật khẩu Admin

- **Default Password**: `admin123`
- **Hoặc**: Nhập mã admin trong admin login panel

## 📋 Chức năng Admin Panel

### 👥 Quản lý Users
- Xem danh sách tất cả users
- Thêm user mới
- Xóa user
- Reset password
- Xem trạng thái user

### 💾 Quản lý Database
- **Backup Database**: Tạo bản sao lưu
- **Restore Database**: Khôi phục từ bản sao
- **Xóa dữ liệu cũ**: Xóa dữ liệu trước 30 ngày
- **Export Data**: Xuất dữ liệu ra JSON
- **View Database Info**: Thông tin kích thước, số lượng bản ghi

### ⚙️ Cài đặt Hệ thống
- **Assistant Settings**:
  - Tự động khởi động assistant
  - Thời gian delay khởi tạo
- **Audio Settings**:
  - Bật/tắt nhận diện giọng nói
  - Bật/tắt phát âm thanh
- **Database Settings**:
  - Tự động backup hàng ngày
  - Thời gian lưu dữ liệu

### 📊 Thống kê
- Tổng số users
- Tổng số cuộc trò chuyện
- Số phiên đang hoạt động
- Kích thước database
- Real-time updates

## 🛠️ Cấu trúc File

```
TLA/
├── login.py              # Main login với Konami Code
├── admin_login.py        # Admin login interface
├── admin_panel.py        # Admin panel chính
├── admin_config.json     # Cấu hình admin
├── admin_settings.json   # Cài đặt hệ thống
└── users.json           # Database users
```

## 🔧 Cài đặt Admin

### Tạo mật khẩu admin mới:
```python
import hashlib
password = "your_password"
hashed = hashlib.sha256(password.encode()).hexdigest()
print(hashed)
```

### Cập nhật `admin_config.json`:
```json
{
    "admin_hash": "your_hashed_password_here"
}
```

## 🎨 Giao diện

### Admin Login
- Dark theme với màu đỏ chủ đạo
- Input password với placeholder
- Konami Code hint
- Status messages

### Admin Panel
- Modern dark theme
- Tab-based interface
- Real-time statistics
- Operation logs
- Responsive design

## 🚀 Sử dụng

### 1. Khởi động ứng dụng
```bash
python login.py
```

### 2. Nhập Konami Code
```
↑ ↑ ↓ ↓ ← → ← → B A
```

### 3. Đăng nhập admin
- Nhập `admin123` hoặc mật khẩu đã cấu hình

### 4. Sử dụng các tính năng
- Quản lý users
- Backup/restore database
- Thay đổi cài đặt
- Xem thống kê

## 🔒 Bảo mật

- **Konami Code**: Chỉ người biết có thể truy cập
- **Password Protection**: Mật khẩu được hash bằng SHA-256
- **Session Management**: Auto logout khi không hoạt động
- **Access Control**: Chỉ admin có thể truy cập

## 📝 Logs

Tất cả operations được ghi lại trong:
- Admin panel operation log
- System console logs
- Database audit trails

## 🔄 Backup Tự động

Cấu hình trong admin panel:
- Enable/disable auto backup
- Set backup frequency
- Choose backup location
- Retention policy

## 🐛 Troubleshooting

### Konami Code không hoạt động:
- Kiểm tra đang ở màn hình login
- Nhập đúng sequence: ↑↑↓↓←→←→BA
- Sử dụng phím mũi tên và B, A

### Không thể đăng nhập admin:
- Kiểm tra mật khẩu default: `admin123`
- Kiểm tra file `admin_config.json`
- Reset mật khẩu nếu cần

### Database errors:
- Kiểm tra file `conversations.db` tồn tại
- Kiểm tra permissions
- Thử backup/restore thủ công

## 📞 Hỗ trợ

Contact admin hoặc check documentation để biết thêm chi tiết.

---

**⚠️ WARNING**: Chỉ admin system mới nên truy cập admin panel. Đừng chia sẻ Konami Code và mật khẩu admin!
