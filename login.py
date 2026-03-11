#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - Login Launcher
Chạy giao diện đăng nhập
"""

import sys
import os
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QApplication

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main function to run login application"""
    try:
        print("Starting Pop Assistant...")
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("Pop Assistant Login")
        app.setOrganizationName("Pop AI")
        app.setQuitOnLastWindowClosed(True)  # Tự động quit khi window đóng
        
        # Show login window first
        print("Importing LoginView...")
        from view.login_view import LoginView
        print("LoginView imported successfully")
        
        # Create custom login window that can detect Admin Code
        class LoginWindowWithAdmin(LoginView):
            def __init__(self, admin_callback):
                super().__init__()
                self.admin_callback = admin_callback
                self.alt_count = 0
                
                # Setup key press timer
                self.key_timer = QTimer()
                self.key_timer.timeout.connect(self.clear_keys)
                self.key_timer.setSingleShot(True)
            
            def keyPressEvent(self, event):
                """Handle key press events for Admin Code"""
                key = event.key()
                
                # Detect Alt key
                if key == Qt.Key.Key_Alt:
                    self.alt_count += 1
                    if self.alt_count >= 3:
                        self.admin_callback()  # Call the callback
                        self.alt_count = 0
                    else:
                        # Start timer to clear keys after 2 seconds
                        self.key_timer.start(2000)
                
                super().keyPressEvent(event)
            
            def clear_keys(self):
                """Clear pressed keys"""
                self.alt_count = 0
        
        # Tạo một biến global để giữ admin login
        global admin_login_ref, admin_panel_ref
        admin_login_ref = None
        admin_panel_ref = None
        
        def open_admin_login():
            """Open admin login window"""
            global admin_login_ref
            try:
                print("Opening admin login...")
                from view.admin_login import AdminLoginView
                admin_login = AdminLoginView()
                admin_login.login_success.connect(on_admin_login_success)
                
                # Force add to application and show
                admin_login.show()
                admin_login.raise_()
                admin_login.activateWindow()
                
                # Force process events để admin login thực sự hiển thị
                app.processEvents()
                QTimer.singleShot(100, lambda: None)
                app.processEvents()
                
                # Hide login window SAU KHI admin login đã được show
                login_window.hide()
                
                # Lưu reference để không bị garbage collected
                admin_login_ref = admin_login
                
                print("Admin login window opened successfully")
                
                # Debug: Check widgets immediately
                widgets = QApplication.topLevelWidgets()
                print(f"Widgets immediately after admin login: {len(widgets)}")
                for i, w in enumerate(widgets):
                    is_visible = w.isVisible()
                    title = w.windowTitle() if hasattr(w, 'windowTitle') else 'No Title'
                    w_type = type(w).__name__
                    print(f"  Widget {i}: {title} - {w_type} - Visible: {is_visible}")
                
            except ImportError as e:
                print(f"Lỗi import admin_login: {e}")
                import traceback
                traceback.print_exc()
            except Exception as e:
                print(f"Lỗi mở admin login: {e}")
                import traceback
                traceback.print_exc()
        
        def on_admin_login_success(username):
            """Handle admin login success"""
            global admin_panel_ref
            try:
                print(f"Admin login successful for: {username}")
                from view.admin_panel import create_admin_panel
                admin_panel = create_admin_panel()
                
                # Lưu reference để không bị garbage collected
                admin_panel_ref = admin_panel
                
                # Force show admin panel
                admin_panel.show()
                admin_panel.raise_()
                admin_panel.activateWindow()
                admin_panel.setFocus()
                
                # Force process events để admin panel thực sự hiển thị
                app.processEvents()
                QTimer.singleShot(100, lambda: None)
                app.processEvents()
                
                # Đóng admin login window
                if 'admin_login_ref' in globals() and admin_login_ref:
                    admin_login_ref.close()
                
                print("Admin panel shown successfully")
                
                def on_admin_panel_close():
                    print("Admin panel closed, returning to login...")
                    # Không gọi main() lại, chỉ đóng admin panel
                
                admin_panel.closeEvent = lambda e: (on_admin_panel_close(), e.accept())
                
            except ImportError as e:
                print(f"Lỗi import admin_panel: {e}")
                import traceback
                traceback.print_exc()
            except Exception as e:
                print(f"Lỗi mở admin panel: {e}")
                import traceback
                traceback.print_exc()
        
        # Create login window with admin callback - SẼ ĐƯỢC GÁN SAU
        login_window = None
        
        # Handle login success - create main window after login
        main_window = None
        
        def on_login_success(username):
            nonlocal main_window
            print(f"Login successful: {username}")
            
            try:
                # Import and run main application
                import main
                main_window = main.create_main_window(username)
                
                if main_window is None:
                    print("ERROR: main_window is None!")
                    return
                
                # Show main window with force methods
                main_window.show()
                main_window.raise_()
                main_window.activateWindow()
                main_window.setFocus()
                
                # Close login immediately
                login_window.close()
                
                print("Main window shown successfully")
                
            except ImportError as e:
                print(f"Lỗi import: {e}")
                import traceback
                traceback.print_exc()
                login_window.show()
            except Exception as e:
                print(f"Lỗi khởi tạo giao diện chính: {e}")
                import traceback
                traceback.print_exc()
                login_window.show()
        
        # Bây giờ mới tạo login window với admin callback
        login_window = LoginWindowWithAdmin(open_admin_login)
        
        login_window.login_success.connect(on_login_success)
        
        # Show login window
        print("Showing login window...")
        login_window.show()
        print("Login window shown successfully")
        
        # Run the application
        print("Running application...")
        result = app.exec()
        print(f"Application ended with code: {result}")
        
        # Check final state
        widgets = QApplication.topLevelWidgets()
        print(f"Final widget count: {len(widgets)}")
        
        visible_count = 0
        for widget in widgets:
            if widget.isVisible():
                visible_count += 1
                title = widget.windowTitle() if hasattr(widget, 'windowTitle') else 'No Title'
                print(f"  Visible: {title}")
        
        print(f"Total visible: {visible_count}")
        print("Application exiting normally")
            
    except ImportError as e:
        print("Lỗi: PyQt6 không được cài đặt. Vui lòng cài đặt: pip install PyQt6")
        print(f"Chi tiết lỗi: {e}")
        input("Nhấn Enter để thoát...")
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {e}")
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()
