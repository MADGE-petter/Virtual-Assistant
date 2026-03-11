#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - PyQt6 Interface
Trợ lý giọng nói thông minh với giao diện hiện đại
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_main_window(username):
    """Create main window with username"""
    try:
        print(f"Creating main window for user: {username}")
        from view.pop_view import PopView
        main_window = PopView(None)
        main_window.user_name = username  # Set username
        
        print(f"Main window created successfully")
        return main_window
    except Exception as e:
        print(f"Error creating main window: {e}")
        import traceback
        traceback.print_exc()
        return None
