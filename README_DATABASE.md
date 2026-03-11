# Pop Assistant - Database Module

## 📚 Mô tả

Module database giúp lưu trữ và quản lý lịch sử các cuộc trò chuyện với Pop Assistant.

## 🗄️ Cấu trúc Database

### Bảng `conversations`
- `id`: ID tự động tăng
- `user_name`: Tên người dùng
- `user_message`: Tin nhắn của người dùng
- `bot_response`: Phản hồi của trợ lý
- `timestamp`: Thời gian tạo
- `session_id`: ID phiên trò chuyện

### Bảng `sessions`
- `session_id`: ID phiên (khóa chính)
- `user_name`: Tên người dùng
- `start_time`: Thời gian bắt đầu
- `end_time`: Thời gian kết thúc

## 🚀 Cách sử dụng

### 1. Chạy Pop Assistant (có lưu database)
```bash
python main.py
```
- Mọi cuộc trò chuyện sẽ tự động được lưu vào `conversations.db`

### 2. Xem lịch sử trò chuyện
```bash
python view_history.py
```
- Giao diện hiện đại để xem các phiên trò chuyện
- Chọn phiên để xem chi tiết nội dung
- Tính năng làm mới và xóa dữ liệu cũ

## 📁 File Structure

```
TLA/
├── main.py                    # Chạy Pop Assistant
├── view_history.py           # Xem lịch sử
├── conversations.db          # Database file (tự động tạo)
├── database/
│   └── conversation_db.py    # Module database
└── view/
    ├── pop_view.py          # Giao diện chính
    └── history_viewer.py    # Giao diện xem lịch sử
```

## 🔧 Tính năng

### Pop Assistant (main.py)
- ✅ Tự động lưu mọi cuộc trò chuyện
- ✅ Quản lý phiên trò chuyện
- ✅ Lưu thông tin người dùng
- ✅ Ghi lại thời gian tương tác

### History Viewer (view_history.py)
- ✅ Xem danh sách các phiên trò chuyện
- ✅ Xem chi tiết nội dung từng phiên
- ✅ Làm mới dữ liệu
- ✅ Xóa dữ liệu cũ (>30 ngày)
- ✅ Giao diện hiện đại, tối giản

## 💾 Dữ liệu được lưu

1. **Thông tin người dùng**: Tên và các phiên trò chuyện
2. **Nội dung chat**: Mọi tin nhắn và phản hồi
3. **Thời gian**: Thời gian chính xác của từng tương tác
4. **Phiên**: Phân loại các cuộc trò chuyện theo phiên

## 🛠️ Kỹ thuật

- **Database**: SQLite3 (không cần cài đặt)
- **Framework**: PyQt6
- **Encoding**: UTF-8 (hỗ trợ tiếng Việt)
- **Auto-cleanup**: Tự động xóa dữ liệu cũ

## 🔒 Bảo mật

- Database lưu local, không upload lên server
- Mã hóa không cần thiết cho dữ liệu chat thông thường
- Có thể xóa thủ công file `conversations.db` nếu cần

## 📝 Lưu ý

- Database tự động tạo khi chạy lần đầu
- File `conversations.db` sẽ được tạo trong thư mục gốc
- Backup database định kỳ để tránh mất dữ liệu
- Có thể mở file DB bằng các SQLite viewer để kiểm tra

## 🐛 Troubleshooting

### Lỗi encoding
```python
# Đã xử lý trong code với UTF-8 encoding
# Nếu vẫn lỗi, kiểm tra locale hệ thống
```

### Database không tạo được
- Kiểm tra quyền ghi thư mục
- Đảm bảo SQLite3 đã được cài đặt
- Xóa file `conversations.db` và chạy lại

### Không xem được lịch sử
- Kiểm tra file `conversations.db` có tồn tại
- Chạy lại Pop Assistant để tạo dữ liệu mẫu
- Kiểm tra import path trong `history_viewer.py`
