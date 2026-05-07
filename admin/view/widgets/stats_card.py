#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - Stats Card Widget
Widget hiển thị thống kê dạng card
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt


class StatsCard(QFrame):
    """Widget hiển thị số liệu thống kê dạng card"""
    
    def __init__(self, title, color, parent=None):
        super().__init__(parent)
        self.title = title
        self.color = color
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setup_ui()
    
    def setup_ui(self):
        # Card style with border
        self.setStyleSheet(f"""
            QFrame {{
                background: rgba(30, 35, 50, 80);
                border: 2px solid {self.color};
                border-radius: 15px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-size: 14px; color: #b0b0b0;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Value label
        self.value_label = QLabel("0")
        self.value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 36px;
                font-weight: bold;
                color: {self.color};
                padding: 10px;
            }}
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
    
    def set_value(self, value):
        """Cập nhật giá trị hiển thị"""
        self.value_label.setText(str(value))
