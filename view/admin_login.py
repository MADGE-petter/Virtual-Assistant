#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - Admin Login Panel
Giao diện đăng nhập admin với Konami Code
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QDialog, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                            QMessageBox, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette
import hashlib

# Add current directory to path (go up one level)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class AdminLoginView(QDialog):
    """Admin Login Interface"""
    login_success = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 Admin Assistant")
        self.setFixedSize(400, 550)  # Giống login thường
        
        # Key tracking
        self.pressed_keys = []
        self.ctrl_count = 0  # Đếm số lần Ctrl
        
        # Setup UI
        self.setup_ui()
        self.setup_style()
        
        # Setup key press timer
        self.key_timer = QTimer()
        self.key_timer.timeout.connect(self.clear_keys)
        self.key_timer.setSingleShot(True)
        
    def setup_ui(self):
        """Create admin login interface exactly like login view"""
        # Main layout - giống hệt login thường
        layout = QVBoxLayout(self)
        layout.setSpacing(35)  # Giống login thường
        layout.setContentsMargins(50, 80, 50, 80)  # Giống login thường
        
        # Title - giống hệt login thường
        title = QLabel("Admin Assistant")
        title.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                               stop:0 #00ffaa, stop:1 #00ccff);
                font-size: 32px;
                font-weight: 300;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                text-align: center;
                padding: 20px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Password field - giống hệt login thường
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Mật khẩu admin")
        self.password_input.setStyleSheet("""
            QLineEdit {
                background: rgba(25, 25, 45, 180);
                border: 1px solid rgba(0, 255, 136, 40);
                border-radius: 10px;
                padding: 12px;
                color: rgba(255, 255, 255, 240);
                font-size: 15px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                min-width: 200px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(0, 255, 136, 80);
                background: rgba(25, 25, 45, 220);
                color: rgba(255, 255, 255, 240);
            }
        """)
        layout.addWidget(self.password_input)
        
        # Login button - giống hệt login thường
        login_btn = QPushButton("Đăng nhập")
        login_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 136, 20);
                border: 1px solid rgba(0, 255, 136, 50);
                border-radius: 10px;
                padding: 12px 25px;
                color: rgba(0, 255, 136, 240);
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
            QPushButton:hover {
                background: rgba(0, 255, 136, 40);
                border: 1px solid rgba(0, 255, 136, 80);
                color: rgba(0, 255, 136, 255);
            }
            QPushButton:pressed {
                background: rgba(0, 255, 136, 60);
                color: rgba(0, 255, 136, 255);
            }
        """)
        login_btn.clicked.connect(self.admin_login)
        layout.addWidget(login_btn)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                font-size: 14px;
                margin-top: 10px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def admin_login(self):
        """Handle admin login"""
        try:
            password = self.password_input.text().strip()
            
            if not password:
                self.status_label.setText("Vui lòng nhập mật khẩu admin!")
                return
            
            # Load admin password from config
            stored_hash = self.get_admin_password_hash()
            
            # Hash input password
            input_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Debug
            print(f"Input password: {password}")
            print(f"Input hash: {input_hash}")
            print(f"Stored hash: {stored_hash}")
            
            # Verify password
            if input_hash == stored_hash:
                self.status_label.setText("Đăng nhập admin thành công!")
                self.login_success.emit("admin")
                QTimer.singleShot(1000, self.close)
            else:
                self.status_label.setText("Sai mật khẩu admin!")
                
        except Exception as e:
            print(f"Lỗi đăng nhập admin: {e}")
            self.status_label.setText("Lỗi đăng nhập!")
    
    def get_admin_password_hash(self):
        """Get admin password hash from database"""
        import sqlite3
        import os
        
        try:
            # Database path
            db_path = os.path.join(os.path.dirname(__file__), '..', 'conversations.db')
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get admin password hash
            cursor.execute('SELECT matKhauMaHoa FROM admin_users WHERE tenAdmin = ?', ('admin',))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return result[0]
            else:
                # Default password hash (admin123)
                return hashlib.sha256("admin123".encode()).hexdigest()
                
        except Exception as e:
            print(f"Lỗi đọc database: {e}")
            # Default password hash
            return hashlib.sha256("admin123".encode()).hexdigest()
    
    def clear_keys(self):
        """Clear pressed keys"""
        self.pressed_keys = []
        self.status_label.setText("")
    
    def setup_style(self):
        """Apply style exactly like login view"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #0f0f1a, stop:1 #1a1a2a);
            }
            QLineEdit {
                background: rgba(25, 25, 45, 180);
                border: 1px solid rgba(0, 255, 136, 40);
                border-radius: 10px;
                padding: 12px;
                color: rgba(255, 255, 255, 240);
                font-size: 15px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                min-width: 200px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(0, 255, 136, 80);
                background: rgba(25, 25, 45, 220);
            }
            QPushButton {
                background: rgba(0, 255, 136, 20);
                border: 1px solid rgba(0, 255, 136, 50);
                border-radius: 10px;
                padding: 12px 25px;
                color: rgba(0, 255, 136, 240);
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
            QPushButton:hover {
                background: rgba(0, 255, 136, 40);
                border: 1px solid rgba(0, 255, 136, 80);
                color: rgba(0, 255, 136, 255);
            }
            QPushButton:pressed {
                background: rgba(0, 255, 136, 60);
                color: rgba(0, 255, 136, 255);
            }
            QLabel {
                color: rgba(255, 255, 255, 220);
                font-size: 15px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                padding: 5px;
            }
        """)
    
    def keyPressEvent(self, event):
        """Handle key press events for Ctrl detection"""
        key = event.key()
        
        # Detect Ctrl key
        if key == Qt.Key.Key_Control:
            self.ctrl_count += 1
            if self.ctrl_count >= 3:
                self.open_change_password_dialog()
                self.ctrl_count = 0
            else:
                # Start timer to clear count after 2 seconds
                self.key_timer.start(2000)
        else:
            # Clear count if other key pressed
            self.ctrl_count = 0
        
        super().keyPressEvent(event)
    
    def open_change_password_dialog(self):
        """Open dialog to change admin password (không cần mật khẩu hiện tại)"""
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        
        # Hiển thị thông báo
        reply = QMessageBox.question(
            self, "Đổi Mật Khẩu Admin", 
            "Bạn muốn đổi mật khẩu admin?\n\nĐây là tính năng khôi phục mật khẩu khi quên.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            new_password, ok = QInputDialog.getText(
                self, "Đổi Mật Khẩu Admin", "Nhập mật khẩu admin mới:", 
                QLineEdit.EchoMode.Password
            )
            
            if ok and new_password:
                confirm_password, ok = QInputDialog.getText(
                    self, "Đổi Mật Khẩu Admin", "Xác nhận mật khẩu mới:", 
                    QLineEdit.EchoMode.Password
                )
                
                if ok and confirm_password:
                    if new_password == confirm_password:
                        if len(new_password) >= 4:
                            self.save_new_password(new_password)
                            self.status_label.setText("✅ Đổi mật khẩu thành công!")
                        else:
                            self.status_label.setText("❌ Mật khẩu phải có ít nhất 4 ký tự!")
                    else:
                        self.status_label.setText("❌ Mật khẩu xác nhận không khớp!")
    
    def save_new_password(self, new_password):
        """Save new admin password to database"""
        import sqlite3
        import os
        import hashlib
        
        try:
            # Database path
            db_path = os.path.join(os.path.dirname(__file__), '..', 'conversations.db')
            
            # Hash the new password
            new_hash = hashlib.sha256(new_password.encode()).hexdigest()
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Update admin password
            cursor.execute('''
                UPDATE admin_users 
                SET matKhauMaHoa = ?, thoiGianCapNhat = CURRENT_TIMESTAMP 
                WHERE tenAdmin = ?
            ''', (new_hash, 'admin'))
            
            conn.commit()
            conn.close()
            
            print("Password updated successfully in database!")
            
        except Exception as e:
            print(f"Lỗi lưu mật khẩu: {e}")
            self.status_label.setText("Lỗi lưu mật khẩu!")
    
    def clear_keys(self):
        """Clear pressed keys"""
        self.pressed_keys = []
        self.ctrl_count = 0
        self.status_label.setText("")
    
    def setup_style(self):
        """Apply style exactly like login view"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #0f0f1a, stop:1 #1a1a2a);
            }
            QLineEdit {
                background: rgba(25, 25, 45, 180);
                border: 1px solid rgba(0, 255, 136, 40);
                border-radius: 10px;
                padding: 12px;
                color: rgba(255, 255, 255, 240);
                font-size: 15px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                min-width: 200px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(0, 255, 136, 80);
                background: rgba(25, 25, 45, 220);
            }
            QPushButton {
                background: rgba(0, 255, 136, 20);
                border: 1px solid rgba(0, 255, 136, 50);
                border-radius: 10px;
                padding: 12px 25px;
                color: rgba(0, 255, 136, 240);
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
            QPushButton:hover {
                background: rgba(0, 255, 136, 40);
                border: 1px solid rgba(0, 255, 136, 80);
                color: rgba(0, 255, 136, 255);
            }
            QPushButton:pressed {
                background: rgba(0, 255, 136, 60);
                color: rgba(0, 255, 136, 255);
            }
            QLabel {
                color: rgba(255, 255, 255, 220);
                font-size: 15px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                padding: 5px;
            }
        """)
    
def keyPressEvent(self, event):
    """Handle key press events for Konami Code"""
    key = event.key()
    key_text = ""
    
    # Map keys to Konami sequence
    if key == Qt.Key.Key_Up:
        key_text = "up"
    elif key == Qt.Key.Key_Down:
        key_text = "down"
    elif key == Qt.Key.Key_Left:
        key_text = "left"
    elif key == Qt.Key.Key_Right:
        key_text = "right"
    elif key == Qt.Key.Key_B:
        key_text = "b"
    elif key == Qt.Key.Key_A:
        key_text = "a"
    
    if key_text:
        self.konami_detector.add_key(key_text)
        self.pressed_keys.append(key_text)
        
        # Start timer to clear keys after 5 seconds
        self.key_timer.start(5000)
        
        # Show pressed keys (for debugging)
        if len(self.pressed_keys) <= 10:
            self.status_label.setText("Keys: " + " → ".join(self.pressed_keys))
    
    super().keyPressEvent(event)
    
    def clear_keys(self):
        """Clear pressed keys"""
        self.pressed_keys = []
        self.status_label.setText("")
    
    def show_admin_panel(self):
        """Show admin panel directly"""
        self.login_success.emit("admin")
        self.close()
    
    def admin_login(self):
        """Handle admin login"""
        try:
            password = self.password_input.text().strip()
            
            if not password:
                self.status_label.setText("Vui lòng nhập mật khẩu admin!")
                return
            
            # Default admin password
            if password == "admin123":
                self.status_label.setText("Đăng nhập admin thành công!")
                self.login_success.emit("admin")
                QTimer.singleShot(1000, self.close)
            else:
                self.status_label.setText("Sai mật khẩu admin!")
                
        except Exception as e:
            print(f"Lỗi đăng nhập admin: {e}")
            self.status_label.setText("Lỗi đăng nhập!")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ff4444;
                font-size: 14px;
                margin-top: 10px;
            }
        """)
    
def show_error(self, message):
    """Show error message"""
    self.status_label.setText("❌ " + message)
    self.status_label.setStyleSheet("""
        QLabel {
            color: #ff4444;
            font-size: 14px;
            margin-top: 10px;
        }
    """)
    
def show_success(self, message):
    """Show success message"""
    self.status_label.setText("✅ " + message)
    self.status_label.setStyleSheet("""
        QLabel {
            color: #4caf50;
            font-size: 14px;
            margin-top: 10px;
        }
    """)
    self.status_label.setStyleSheet("""
            QLabel {
                color: #4caf50;
                font-size: 14px;
                margin-top: 10px;
            }
        """)

def main():
    """Main function to run admin login"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Pop Assistant Admin")
    app.setOrganizationName("Pop AI")
    
    # Create admin login window
    admin_login = AdminLoginView()
    admin_login.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
