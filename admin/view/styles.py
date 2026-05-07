#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - Admin Panel Styles
Tập trung tất cả stylesheet để dễ bảo trì
"""

# Main Window Styles
MAIN_WINDOW = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 #1a1f2a, stop:1 #2a2f3a);
    color: #e0e0e0;
}
QWidget {
    background-color: transparent;
    color: #e0e0e0;
}
QLabel {
    color: #e0e0e0;
}
QTextEdit {
    color: #e0e0e0;
}
"""

# Tab Widget Styles
TAB_WIDGET = """
QTabWidget::pane {
    border: 2px solid rgba(0, 255, 170, 40);
    background: rgba(30, 35, 50, 95);
    border-radius: 12px;
    padding: 15px;
}
QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 rgba(0, 255, 170, 35), stop:1 rgba(0, 204, 255, 35));
    color: #ffffff;
    padding: 14px 28px;
    margin-right: 4px;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
    font-weight: 700;
    border: 2px solid rgba(0, 255, 170, 60);
    min-width: 120px;
}
QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 rgba(0, 255, 170, 55), stop:1 rgba(0, 204, 255, 55));
    color: #ffffff;
    border-bottom: 4px solid #00ffaa;
    border: 2px solid rgba(0, 255, 170, 80);
}
QTabBar::tab:hover:!selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 rgba(0, 255, 170, 45), stop:1 rgba(0, 204, 255, 45));
    border: 2px solid rgba(0, 255, 170, 70);
}
"""

# Header Styles
HEADER_FRAME = """
QFrame {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                   stop:0 rgba(0, 255, 170, 25), stop:1 rgba(0, 204, 255, 25));
    border: 2px solid rgba(0, 255, 170, 40);
    border-radius: 15px;
    padding: 15px;
}
"""

HEADER_TITLE = """
QLabel {
    color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                   stop:0 #00ffaa, stop:1 #00ccff);
    font-size: 28px;
    font-weight: 300;
    font-family: 'Segoe UI Light', sans-serif;
    padding: 10px;
}
"""

HEADER_STATUS = """
QLabel {
    color: #00ff88;
    background: rgba(0, 255, 136, 15);
    border: 1px solid rgba(0, 255, 136, 30);
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 12px;
    font-family: 'Segoe UI', sans-serif;
    font-weight: 600;
}
"""

HEADER_TIME = """
QLabel {
    color: #00ccff;
    font-size: 14px;
    font-family: 'Segoe UI', sans-serif;
    padding: 8px;
}
"""

# Footer Styles
FOOTER_FRAME = """
QFrame {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                   stop:0 rgba(0, 255, 170, 20), stop:1 rgba(0, 204, 255, 20));
    border: 1px solid rgba(0, 255, 170, 30);
    border-radius: 10px;
    padding: 12px;
}
"""

FOOTER_INFO = """
QLabel {
    color: rgba(0, 255, 170, 70);
    font-size: 11px;
    font-family: 'Segoe UI', sans-serif;
}
"""

# Table Styles
TABLE_WIDGET = """
QTableWidget {
    background: rgba(30, 35, 50, 95);
    border: 2px solid rgba(0, 255, 170, 40);
    border-radius: 10px;
    gridline-color: rgba(0, 255, 170, 25);
    color: #ffffff;
    selection-background-color: rgba(0, 255, 170, 40);
    outline: none;
    font-size: 14px;
}
QTableWidget::item {
    padding: 15px;
    border-bottom: 1px solid rgba(0, 255, 170, 20);
    color: #ffffff;
    background: transparent;
    font-size: 14px;
}
QTableWidget::item:selected {
    background: rgba(0, 255, 170, 50);
    color: #1a1f2a;
    border: 1px solid rgba(0, 255, 170, 80);
    font-size: 14px;
}
QHeaderView::section {
    background: rgba(0, 255, 170, 20);
    color: #00ffaa;
    padding: 15px;
    border: none;
    font-weight: bold;
    font-size: 15px;
    border-right: 1px solid rgba(0, 255, 170, 30);
}
QHeaderView::section:last {
    border-right: none;
}
"""

# Button Styles
def button_style(color1, color2, hover_color1=None, hover_color2=None):
    """Generate gradient button style"""
    if hover_color1 is None:
        hover_color1 = color1.replace("0.8", "0.9")
        hover_color2 = color2.replace("0.8", "0.9")
    return f"""
QPushButton {{
    padding: 12px 24px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 {color1}, stop:1 {color2});
    border: 2px solid {color1.replace("0.8", "0.9")};
    border-radius: 8px;
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    font-family: 'Segoe UI', sans-serif;
}}
QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 {hover_color1}, stop:1 {hover_color2});
    border: 2px solid {color1.replace("0.8", "1.0")};
}}
"""

# Predefined button styles
BUTTON_GREEN = button_style(
    "rgba(39, 174, 96, 0.8)", "rgba(34, 153, 84, 0.8)",
    "rgba(46, 204, 113, 0.9)", "rgba(39, 174, 96, 0.9)"
)

BUTTON_RED = button_style(
    "rgba(231, 76, 60, 0.8)", "rgba(192, 57, 43, 0.8)",
    "rgba(240, 96, 96, 0.9)", "rgba(231, 76, 60, 0.9)"
)

BUTTON_BLUE = button_style(
    "rgba(52, 152, 219, 0.8)", "rgba(41, 128, 185, 0.8)",
    "rgba(93, 173, 226, 0.9)", "rgba(52, 152, 219, 0.9)"
)

BUTTON_ORANGE = button_style(
    "rgba(243, 156, 18, 0.8)", "rgba(230, 126, 34, 0.8)",
    "rgba(241, 196, 15, 0.9)", "rgba(243, 156, 18, 0.9)"
)

BUTTON_PURPLE = button_style(
    "rgba(155, 89, 182, 0.8)", "rgba(142, 68, 173, 0.8)",
    "rgba(155, 89, 182, 0.9)", "rgba(142, 68, 173, 0.9)"
)

BUTTON_LOGOUT = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 #e74c3c, stop:1 #c0392b);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 12px;
    font-family: 'Segoe UI', sans-serif;
    font-weight: 600;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 #ff6b6b, stop:1 #ff5252);
}
"""

# Card/Info Frame Styles
INFO_FRAME = """
QFrame {
    background: rgba(52, 152, 219, 0.1);
    border-radius: 8px;
    padding: 15px;
}
"""

INFO_LABEL = """
QLabel {
    font-size: 14px;
    color: #e0e0e0;
    padding: 10px;
}
"""

LOG_TEXT = """
QTextEdit {
    background: rgba(30, 35, 50, 90);
    color: #e0e0e0;
    border: 1px solid rgba(0, 255, 170, 20);
    border-radius: 6px;
    padding: 8px;
    font-family: 'Consolas', monospace;
    font-size: 12px;
}
"""

# Stats Card Styles
def stats_card_style(color):
    """Generate stats card style with specific color"""
    return f"""
QLabel {{
    font-size: 36px;
    font-weight: bold;
    color: {color};
    background: {color.replace("#", "rgba(") + ", 0.1)" if not color.startswith("rgba") else color};
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}}
"""

STATS_CARD_BLUE = stats_card_style("#3498db")
STATS_CARD_GREEN = stats_card_style("#27ae60")
STATS_CARD_ORANGE = stats_card_style("#f39c12")
STATS_CARD_RED = stats_card_style("#e74c3c")

# Dialog Styles
DIALOG_MAIN = """
QDialog {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 #1a1f2a, stop:1 #2a2f3a);
    color: #e0e0e0;
}
QLabel {
    color: #e0e0e0;
    font-size: 12px;
}
QLineEdit {
    background: rgba(30, 35, 50, 90);
    border: 1px solid rgba(0, 255, 170, 40);
    border-radius: 6px;
    padding: 8px;
    color: #e0e0e0;
    font-size: 12px;
}
"""

DIALOG_CONVERSATION = """
QDialog {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 #1e2332, stop:1 #2a3142);
    color: #00ffaa;
}
QLabel {
    color: #00ffaa;
    font-size: 12px;
    padding: 5px;
}
QTextEdit {
    background: rgba(30, 35, 50, 95);
    border: 2px solid rgba(0, 255, 170, 40);
    border-radius: 8px;
    padding: 10px;
    color: #00ffaa;
    font-size: 12px;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 #00ffaa, stop:1 #00cc88);
    color: #1e2332;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 #00ffbb, stop:1 #00dd99);
}
QScrollArea {
    background: transparent;
    border: none;
}
QFrame {
    background: rgba(30, 35, 50, 95);
    border: 1px solid rgba(0, 255, 170, 30);
    border-radius: 8px;
    padding: 10px;
    margin: 5px;
}
"""

CONVERSATION_HEADER = """
QFrame {
    background: rgba(0, 255, 170, 10);
    border: 1px solid rgba(0, 255, 170, 30);
    border-radius: 8px;
    padding: 15px;
}
"""
