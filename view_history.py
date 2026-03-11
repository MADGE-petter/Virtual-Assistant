#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - History Viewer Launcher
Chạy trình xem lịch sử trò chuyện
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main function to run history viewer"""
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("Pop Assistant History")
        app.setOrganizationName("Pop AI")
        
        # Create and show history viewer
        from view.history_viewer import HistoryViewer
        window = HistoryViewer()
        window.show()
        
        # Run the application
        sys.exit(app.exec())
        
    except ImportError as e:
        print("Lỗi: PyQt6 không được cài đặt. Vui lòng cài đặt: pip install PyQt6")
        print(f"Chi tiết lỗi: {e}")
        input("Nhấn Enter để thoát...")
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {e}")
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()
