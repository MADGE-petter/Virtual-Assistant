#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - PyQt6 Interface
Trợ lý giọng nói thông minh với giao diện hiện đại
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_main_window(username):
    """Create main window with proper MVC structure."""
    try:
        print(f"Creating main window for user: {username}")

        from view.pop_view import PopView
        from controller.pop_controller import PopController
        view = PopView()
        view.user_name = username
        controller = PopController(view, login_username=username)
        controller.start()
        return view
    except Exception as e:
        print(f"Error creating main window: {e}")
        import traceback
        traceback.print_exc()
        return None
