#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - Admin Panel
Giao diện quản trị admin
"""

import sys
import os
import json
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                            QMessageBox, QFrame, QGridLayout, QTabWidget,
                            QListWidget, QListWidgetItem, QTextEdit, 
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QComboBox, QSpinBox, QCheckBox, QFileDialog, QDialog, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QColor, QPalette

# Add current directory to path (go up one level)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class AdminPanel(QMainWindow):
    """Admin Panel Interface"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pop Assistant - Admin Panel")
        self.setGeometry(100, 100, 1200, 800)
        
        # Modern lighter theme with dark text
        self.setStyleSheet("""
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
        """)
        
        # Setup UI
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Create admin panel interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        self.create_header(layout)
        
        # Tab Widget with modern styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
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
        """)
        self.create_tabs()
        layout.addWidget(self.tab_widget)
        
        # Footer
        self.create_footer(layout)
        
    def create_header(self, layout):
        """Create header section"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                               stop:0 #2c3e50, stop:1 #34495e);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title = QLabel("ADMIN PANEL")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #e0e0e0;
            }
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Admin info
        self.admin_info = QLabel("Admin: Administrator")
        self.admin_info.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #e0e0e0;
            }
        """)
        header_layout.addWidget(self.admin_info)
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #e74c3c;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)
        
        layout.addWidget(header_frame)
        
    def create_tabs(self):
        """Create tab widgets"""
        # Users Management Tab
        self.users_tab = QWidget()
        self.create_users_tab()
        self.tab_widget.addTab(self.users_tab, "Quản lý Users")
        
        # Database Management Tab
        self.database_tab = QWidget()
        self.create_database_tab()
        self.tab_widget.addTab(self.database_tab, "Quản lý Database")
        
        # System Settings Tab
        self.settings_tab = QWidget()
        self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "Cài đặt Hệ thống")
        
        # Statistics Tab
        self.stats_tab = QWidget()
        self.create_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "Thống kê")
        
        # Conversations Management Tab
        self.conversations_tab = QWidget()
        self.create_conversations_tab()
        self.tab_widget.addTab(self.conversations_tab, "Quản lý Trò Chuyện")
        
    def create_users_tab(self):
        """Create users management tab"""
        layout = QVBoxLayout(self.users_tab)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["Username", "Password Hash", "Created Date", "Status"])
        
        # Style table
        self.users_table.setStyleSheet("""
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
                background: rgba(0, 255, 170, 50);
                color: #1a1f2a;
                padding: 15px;
                border: none;
                font-weight: bold;
                font-size: 15px;
                border-right: 1px solid rgba(0, 255, 170, 30);
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
        
        # Make table fill the space
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Set row height for larger cells
        self.users_table.verticalHeader().setDefaultSectionSize(50)
        self.users_table.verticalHeader().setMinimumSectionSize(40)
        
        layout.addWidget(self.users_table)
        
        # Control buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        # Add user button
        add_user_btn = QPushButton("Thêm User")
        add_user_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(39, 174, 96, 0.8), stop:1 rgba(34, 153, 84, 0.8));
                border: 2px solid rgba(39, 174, 96, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(46, 204, 113, 0.9), stop:1 rgba(39, 174, 96, 0.9));
                border: 2px solid rgba(46, 204, 113, 1.0);
            }
        """)
        add_user_btn.clicked.connect(self.add_user)
        button_layout.addWidget(add_user_btn)
        
        # Delete user button
        delete_user_btn = QPushButton("Xóa User")
        delete_user_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(231, 76, 60, 0.8), stop:1 rgba(192, 57, 43, 0.8));
                border: 2px solid rgba(231, 76, 60, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(240, 96, 96, 0.9), stop:1 rgba(231, 76, 60, 0.9));
                border: 2px solid rgba(240, 96, 96, 1.0);
            }
        """)
        delete_user_btn.clicked.connect(self.delete_user)
        button_layout.addWidget(delete_user_btn)
        
        # Reset password button
        reset_pwd_btn = QPushButton("🔑 Reset Password")
        reset_pwd_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(243, 156, 18, 0.8), stop:1 rgba(230, 126, 34, 0.8));
                border: 2px solid rgba(243, 156, 18, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(241, 196, 15, 0.9), stop:1 rgba(243, 156, 18, 0.9));
                border: 2px solid rgba(241, 196, 15, 1.0);
            }
        """)
        reset_pwd_btn.clicked.connect(self.reset_password)
        button_layout.addWidget(reset_pwd_btn)
        
        button_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Làm mới")
        refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(52, 152, 219, 0.8), stop:1 rgba(41, 128, 185, 0.8));
                border: 2px solid rgba(52, 152, 219, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(93, 173, 226, 0.9), stop:1 rgba(52, 152, 219, 0.9));
                border: 2px solid rgba(93, 173, 226, 1.0);
            }
        """)
        refresh_btn.clicked.connect(self.load_users)
        button_layout.addWidget(refresh_btn)
        
        layout.addWidget(button_frame)
        
    def create_database_tab(self):
        """Create database management tab"""
        layout = QVBoxLayout(self.database_tab)
        
        # Database info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: rgba(52, 152, 219, 0.1);
                border-radius: 8px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        self.db_info_label = QLabel("Đang tải thông tin database...")
        self.db_info_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #e0e0e0;
                padding: 10px;
            }
        """)
        info_layout.addWidget(self.db_info_label)
        
        layout.addWidget(info_frame)
        
        # Database operations
        ops_frame = QFrame()
        ops_layout = QGridLayout(ops_frame)
        
        # Backup button
        backup_btn = QPushButton("Backup Database")
        backup_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: #27ae60;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        backup_btn.clicked.connect(self.backup_database)
        ops_layout.addWidget(backup_btn, 0, 0)
        
        # Restore button
        restore_btn = QPushButton("📂 Restore Database")
        restore_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: #f39c12;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e67e22;
            }
        """)
        restore_btn.clicked.connect(self.restore_database)
        ops_layout.addWidget(restore_btn, 0, 1)
        
        # Clear old data button
        clear_btn = QPushButton("Xóa dữ liệu cũ")
        clear_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: #e74c3c;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        clear_btn.clicked.connect(self.clear_old_data)
        ops_layout.addWidget(clear_btn, 1, 0)
        
        # Export button
        export_btn = QPushButton("📤 Export Data")
        export_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: #3498db;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        export_btn.clicked.connect(self.export_data)
        ops_layout.addWidget(export_btn, 1, 1)
        
        layout.addWidget(ops_frame)
        
        # Log area
        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)
        
        log_label = QLabel("📋 Operation Log:")
        log_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #e0e0e0;
                margin-bottom: 10px;
            }
        """)
        log_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: rgba(30, 35, 50, 90);
                color: #e0e0e0;
                border: 1px solid rgba(0, 255, 170, 20);
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_frame)
        
    def create_settings_tab(self):
        """Create system settings tab"""
        layout = QVBoxLayout(self.settings_tab)
        
        # Settings form
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background: rgba(52, 152, 219, 0.1);
                border-radius: 8px;
                padding: 20px;
            }
        """)
        settings_layout = QGridLayout(settings_frame)
        
        # Assistant settings
        row = 0
        settings_layout.addWidget(QLabel("Cài đặt Assistant:"), row, 0, 1, 2)
        row += 1
        
        # Auto-start assistant
        self.auto_start_cb = QCheckBox("Tự động khởi động assistant")
        self.auto_start_cb.setChecked(True)
        settings_layout.addWidget(self.auto_start_cb, row, 0, 1, 2)
        row += 1
        
        # Assistant delay
        settings_layout.addWidget(QLabel("Delay khởi tạo (giây):"), row, 0)
        self.assistant_delay = QSpinBox()
        self.assistant_delay.setRange(1, 10)
        self.assistant_delay.setValue(3)
        settings_layout.addWidget(self.assistant_delay, row, 1)
        row += 1
        
        # Audio settings
        settings_layout.addWidget(QLabel("🔊 Cài đặt Audio:"), row, 0, 1, 2)
        row += 1
        
        # Enable speech recognition
        self.speech_recognition_cb = QCheckBox("Bật nhận diện giọng nói")
        self.speech_recognition_cb.setChecked(True)
        settings_layout.addWidget(self.speech_recognition_cb, row, 0, 1, 2)
        row += 1
        
        # Enable text-to-speech
        self.text_to_speech_cb = QCheckBox("Bật phát âm thanh")
        self.text_to_speech_cb.setChecked(True)
        settings_layout.addWidget(self.text_to_speech_cb, row, 0, 1, 2)
        row += 1
        
        # Database settings
        settings_layout.addWidget(QLabel("Cài đặt Database:"), row, 0, 1, 2)
        row += 1
        
        # Auto-backup
        self.auto_backup_cb = QCheckBox("Tự động backup hàng ngày")
        self.auto_backup_cb.setChecked(False)
        settings_layout.addWidget(self.auto_backup_cb, row, 0, 1, 2)
        row += 1
        
        # Data retention days
        settings_layout.addWidget(QLabel("Lưu dữ liệu (ngày):"), row, 0)
        self.data_retention = QSpinBox()
        self.data_retention.setRange(1, 365)
        self.data_retention.setValue(30)
        settings_layout.addWidget(self.data_retention, row, 1)
        row += 1
        
        layout.addWidget(settings_frame)
        
        # Save button
        save_btn = QPushButton("Lưu cài đặt")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: #27ae60;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
    def create_stats_tab(self):
        """Create statistics tab"""
        layout = QVBoxLayout(self.stats_tab)
        
        # Statistics cards
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        
        # Total users
        self.total_users_label = QLabel("0")
        self.total_users_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #3498db;
                background: rgba(52, 152, 219, 0.1);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
            }
        """)
        cards_layout.addWidget(QLabel("Tổng Users:"), 0, 0)
        cards_layout.addWidget(self.total_users_label, 1, 0)
        
        # Total conversations
        self.total_conversations_label = QLabel("0")
        self.total_conversations_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #27ae60;
                background: rgba(39, 174, 96, 0.1);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
            }
        """)
        cards_layout.addWidget(QLabel("Tổng Cuộc trò chuyện:"), 0, 1)
        cards_layout.addWidget(self.total_conversations_label, 1, 1)
        
        # Active sessions
        self.active_sessions_label = QLabel("0")
        self.active_sessions_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #f39c12;
                background: rgba(243, 156, 18, 0.1);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
            }
        """)
        cards_layout.addWidget(QLabel("🔥 Phiên đang hoạt động:"), 0, 2)
        cards_layout.addWidget(self.active_sessions_label, 1, 2)
        
        # Database size
        self.db_size_label = QLabel("0 MB")
        self.db_size_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #e74c3c;
                background: rgba(231, 76, 60, 0.1);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
            }
        """)
        cards_layout.addWidget(QLabel("Kích thước DB:"), 0, 3)
        cards_layout.addWidget(self.db_size_label, 1, 3)
        
        layout.addWidget(cards_frame)
        
        # Refresh button
        refresh_stats_btn = QPushButton("Làm mới thống kê")
        refresh_stats_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: #3498db;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        refresh_stats_btn.clicked.connect(self.load_statistics)
        layout.addWidget(refresh_stats_btn)
        
        layout.addStretch()
        
    def create_header(self, layout):
        """Create header section"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                               stop:0 rgba(0, 255, 170, 25), stop:1 rgba(0, 204, 255, 25));
                border: 2px solid rgba(0, 255, 170, 40);
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("Admin Panel")
        title_label.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                               stop:0 #00ffaa, stop:1 #00ccff);
                font-size: 28px;
                font-weight: 300;
                font-family: 'Segoe UI Light', sans-serif;
                padding: 10px;
            }
        """)
        
        # Status
        self.status_label = QLabel("🟢 System Online")
        self.status_label.setStyleSheet("""
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
        """)
        
        # Time
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: #00ccff;
                font-size: 14px;
                font-family: 'Segoe UI', sans-serif;
                padding: 8px;
            }
        """)
        
        # Update time
        self.update_time()
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        header_layout.addWidget(self.time_label)
        
        layout.addWidget(header_frame)
        
    def create_footer(self, layout):
        """Create footer section"""
        footer_frame = QFrame()
        footer_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                               stop:0 rgba(0, 255, 170, 20), stop:1 rgba(0, 204, 255, 20));
                border: 1px solid rgba(0, 255, 170, 30);
                border-radius: 10px;
                padding: 12px;
            }
        """)
        
        footer_layout = QHBoxLayout(footer_frame)
        
        # Logout button
        logout_btn = QPushButton("� Logout")
        logout_btn.setStyleSheet("""
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
        """)
        logout_btn.clicked.connect(self.close)
        
        # Info label
        info_label = QLabel("Pop Assistant Admin Panel v1.0")
        info_label.setStyleSheet("""
            QLabel {
                color: rgba(0, 255, 170, 70);
                font-size: 11px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        footer_layout.addWidget(info_label)
        footer_layout.addStretch()
        footer_layout.addWidget(logout_btn)
        
        layout.addWidget(footer_frame)
        
        # Update timestamp every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timestamp)
        self.timer.start(1000)
        self.update_timestamp()
        
    def setup_style(self):
        """Setup window style"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #ecf0f1, stop:1 #bdc3c7);
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #34495e;
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #3498db;
            }
            QTabBar::tab:hover {
                background: #2c3e50;
            }
        """)
        
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"📅 {current_time}")
        
    def update_timestamp(self):
        """Update timestamp (legacy method)"""
        self.update_time()
        
    def load_data(self):
        """Load initial data"""
        self.load_users()
        self.load_database_info()
        self.load_statistics()
        
    def load_users(self):
        """Load users from database"""
        try:
            # Load from database instead of JSON
            db_path = os.path.join(os.path.dirname(__file__), '..', 'conversations.db')
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT tenKhachHang, matKhauMaHoa, thoiGianTao FROM users ORDER BY thoiGianTao DESC")
                users = cursor.fetchall()
                
                self.users_table.setRowCount(0)
                
                for username, password_hash, created_date in users:
                    row = self.users_table.rowCount()
                    self.users_table.insertRow(row)
                    
                    self.users_table.setItem(row, 0, QTableWidgetItem(username))
                    # Hiển thị password hash đã masked
                    masked_password = password_hash[:8] + "..." if len(password_hash) > 8 else password_hash
                    self.users_table.setItem(row, 1, QTableWidgetItem(masked_password))
                    self.users_table.setItem(row, 2, QTableWidgetItem(created_date))
                    self.users_table.setItem(row, 3, QTableWidgetItem("✅ Active"))
                
                conn.close()
                self.log_message(f"✅ Đã tải {len(users)} users từ database")
            else:
                self.log_message("⚠️ Database không tồn tại")
                        
        except Exception as e:
            self.log_message(f"Lỗi tải users: {e}")
            
    def load_database_info(self):
        """Load database information"""
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'conversations.db')
            if os.path.exists(db_path):
                # Get database size
                size = os.path.getsize(db_path)
                size_mb = size / (1024 * 1024)
                
                # Get table info
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM conversations")
                total_conversations = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM sessions WHERE thoiGianKetThuc IS NULL")
                active_sessions = cursor.fetchone()[0]
                
                conn.close()
                
                self.db_info_label.setText(
                    f"Database Size: {size_mb:.2f} MB\n"
                    f"Total Conversations: {total_conversations}\n"
                    f"Active Sessions: {active_sessions}"
                )
                
        except Exception as e:
            self.db_info_label.setText(f"Lỗi tải thông tin database: {e}")
            
    def load_statistics(self):
        """Load statistics data"""
        try:
            # Load users count from database
            db_path = os.path.join(os.path.dirname(__file__), '..', 'conversations.db')
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                self.total_users_label.setText(str(total_users))
                
                conn.close()
            
            # Load database stats
            db_path = os.path.join(os.path.dirname(__file__), '..', 'conversations.db')
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM conversations")
                total_conversations = cursor.fetchone()[0]
                self.total_conversations_label.setText(str(total_conversations))
                
                cursor.execute("SELECT COUNT(*) FROM sessions WHERE thoiGianKetThuc IS NULL")
                active_sessions = cursor.fetchone()[0]
                self.active_sessions_label.setText(str(active_sessions))
                
                conn.close()
            
            # Database size
            if os.path.exists("conversations.db"):
                size = os.path.getsize("conversations.db")
                size_mb = size / (1024 * 1024)
                self.db_size_label.setText(f"{size_mb:.2f} MB")
                
        except Exception as e:
            self.log_message(f"Lỗi tải thống kê: {e}")
            
    def add_user(self):
        """Add new user"""
        # Create dialog for adding user
        dialog = QDialog(self)
        dialog.setWindowTitle("Thêm User Mới")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet("""
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
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(39, 174, 96, 0.8), stop:1 rgba(34, 153, 84, 0.8));
                border: 2px solid rgba(39, 174, 96, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(46, 204, 113, 0.9), stop:1 rgba(39, 174, 96, 0.9));
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Username
        username_label = QLabel("Username:")
        username_input = QLineEdit()
        username_input.setPlaceholderText("Nhập username...")
        
        # Password
        password_label = QLabel("Password:")
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_input.setPlaceholderText("Nhập password...")
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        cancel_btn = QPushButton("Hủy")
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        # Add to layout
        layout.addWidget(username_label)
        layout.addWidget(username_input)
        layout.addWidget(password_label)
        layout.addWidget(password_input)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        # Handle buttons
        def save_user():
            username = username_input.text().strip()
            password = password_input.text().strip()
            
            if not username or not password:
                QMessageBox.warning(dialog, "Lỗi", "Vui lòng nhập đầy đủ username và password!")
                return
            
            try:
                # Hash password
                import hashlib
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Save to database
                db_path = os.path.join(os.path.dirname(__file__), '..', 'conversations.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute("SELECT tenKhachHang, matKhauMaHoa FROM users WHERE tenKhachHang = ?", (username,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    # Compare passwords
                    import hashlib
                    input_password_hash = hashlib.sha256(password.encode()).hexdigest()
                    
                    # Chỉ báo lỗi khi trùng CẢ username VÀ password
                    if existing_user[1] == input_password_hash:
                        QMessageBox.warning(dialog, "Lỗi", f"User '{username}' đã tồn tại với cùng mật khẩu!")
                        self.log_message(f"⚠️ User trùng hoàn toàn: {username}")
                        conn.close()
                        return
                    # Nếu trùng username nhưng password khác, vẫn cho tạo mới
                    # (Không làm gì, để đi đến insert)
                
                # Insert new user (cho phép trùng username với password khác)
                from datetime import datetime
                created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                try:
                    cursor.execute(
                        "INSERT INTO users (tenKhachHang, matKhauMaHoa, thoiGianTao) VALUES (?, ?, ?)",
                        (username, password_hash, created_date)
                    )
                    conn.commit()
                    
                    # Verify insertion
                    cursor.execute("SELECT COUNT(*) FROM users WHERE tenKhachHang = ? AND matKhauMaHoa = ?", (username, password_hash))
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        self.log_message(f"✅ Đã thêm user: {username} (hash: {password_hash[:8]}...)")
                        self.load_users()
                        QMessageBox.information(dialog, "Thành công", f"Đã thêm user '{username}' thành công!")
                        dialog.accept()
                    else:
                        QMessageBox.critical(dialog, "Lỗi", f"Không thể thêm user '{username}' vào database!")
                        self.log_message(f"❌ Lỗi thêm user: {username} (insert verification failed)")
                        
                except sqlite3.IntegrityError as e:
                    if "UNIQUE constraint failed" in str(e):
                        QMessageBox.critical(dialog, "Lỗi", f"User '{username}' đã tồn tại với cùng thông tin!")
                        self.log_message(f"❌ User trùng hoàn toàn: {username}")
                    else:
                        QMessageBox.critical(dialog, "Lỗi Database", f"Lỗi database: {e}")
                        self.log_message(f"❌ Lỗi database: {e}")
                except Exception as e:
                    QMessageBox.critical(dialog, "Lỗi", f"Lỗi thêm user: {e}")
                    self.log_message(f"❌ Lỗi hệ thống: {e}")
                
                conn.close()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Lỗi", f"Lỗi thêm user: {e}")
        
        save_btn.clicked.connect(save_user)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Show dialog
        dialog.exec()
        
    def delete_user(self):
        """Delete selected user"""
        current_row = self.users_table.currentRow()
        if current_row >= 0:
            username = self.users_table.item(current_row, 0).text()
            reply = QMessageBox.question(
                self, "Xác nhận", f"Bạn có chắc muốn xóa user '{username}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Delete user logic here
                self.log_message(f"Đã xóa user: {username}")
                self.load_users()
        else:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn user để xóa!")
            
    def reset_password(self):
        """Reset user password"""
        current_row = self.users_table.currentRow()
        if current_row >= 0:
            username = self.users_table.item(current_row, 0).text()
            QMessageBox.information(self, "Thông báo", f"Reset password cho user '{username}' sẽ được triển khai sau!")
        else:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn user để reset password!")
            
    def backup_database(self):
        """Backup database"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backup_conversations_{timestamp}.db"
            
            if os.path.exists("conversations.db"):
                import shutil
                shutil.copy2("conversations.db", backup_file)
                self.log_message(f"✅ Database đã backup thành công: {backup_file}")
                QMessageBox.information(self, "Thành công", f"Database đã backup: {backup_file}")
            else:
                self.log_message("❌ Không tìm thấy file database!")
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy file database!")
                
        except Exception as e:
            self.log_message(f"❌ Lỗi backup database: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi backup database: {e}")
            
    def restore_database(self):
        """Restore database"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Database Files (*.db)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            if files:
                try:
                    import shutil
                    shutil.copy2(files[0], "conversations.db")
                    self.log_message(f"✅ Database đã restore từ: {files[0]}")
                    QMessageBox.information(self, "Thành công", "Database đã restore thành công!")
                    self.load_database_info()
                    self.load_statistics()
                except Exception as e:
                    self.log_message(f"❌ Lỗi restore database: {e}")
                    QMessageBox.critical(self, "Lỗi", f"Lỗi restore database: {e}")
                    
    def clear_old_data(self):
        """Clear old data"""
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn xóa dữ liệu cũ (trước 30 ngày)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect("conversations.db")
                cursor = conn.cursor()
                
                # Delete old conversations
                cursor.execute("""
                    DELETE FROM conversations 
                    WHERE timestamp < datetime('now', '-30 days')
                """)
                
                conn.commit()
                conn.close()
                
                self.log_message("✅ Đã xóa dữ liệu cũ thành công!")
                QMessageBox.information(self, "Thành công", "Đã xóa dữ liệu cũ thành công!")
                self.load_database_info()
                self.load_statistics()
                
            except Exception as e:
                self.log_message(f"❌ Lỗi xóa dữ liệu cũ: {e}")
                QMessageBox.critical(self, "Lỗi", f"Lỗi xóa dữ liệu cũ: {e}")
                
    def export_data(self):
        """Export data to JSON"""
        try:
            conn = sqlite3.connect("conversations.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT maKhachHang, tenKhachHang, matKhauMaHoa, thoiGianTao FROM users ORDER BY thoiGianTao DESC")
            conversations = cursor.fetchall()
            
            cursor.execute("SELECT * FROM sessions")
            sessions = cursor.fetchall()
            
            conn.close()
            
            export_data = {
                "conversations": conversations,
                "sessions": sessions,
                "export_date": datetime.now().isoformat()
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = f"export_data_{timestamp}.json"
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
                
            self.log_message(f"✅ Data đã export thành công: {export_file}")
            QMessageBox.information(self, "Thành công", f"Data đã export: {export_file}")
            
        except Exception as e:
            self.log_message(f"❌ Lỗi export data: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi export data: {e}")
            
    def save_settings(self):
        """Save system settings"""
        settings = {
            "auto_start_assistant": self.auto_start_cb.isChecked(),
            "assistant_delay": self.assistant_delay.value(),
            "speech_recognition": self.speech_recognition_cb.isChecked(),
            "text_to_speech": self.text_to_speech_cb.isChecked(),
            "auto_backup": self.auto_backup_cb.isChecked(),
            "data_retention_days": self.data_retention.value()
        }
        
        try:
            with open("admin_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
                
            self.log_message("✅ Cài đặt đã được lưu thành công!")
            QMessageBox.information(self, "Thành công", "Cài đặt đã được lưu thành công!")
            
        except Exception as e:
            self.log_message(f"❌ Lỗi lưu cài đặt: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi lưu cài đặt: {e}")
            
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def update_timestamp(self):
        """Update timestamp label"""
        # This method is now handled by update_time()
        self.update_time()
        
    def logout(self):
        """Logout from admin panel"""
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn đăng xuất?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
    
    def closeEvent(self, event):
        """Handle window close event - quit application"""
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn thoát Admin Panel?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Get application instance and quit
            app = QApplication.instance()
            if app:
                app.quit()
            event.accept()
        else:
            event.ignore()

    def create_conversations_tab(self):
        """Create conversations management tab"""
        layout = QVBoxLayout(self.conversations_tab)
        
        # Conversations table - same style as users table
        self.conversations_table = QTableWidget()
        self.conversations_table.setColumnCount(4)
        self.conversations_table.setHorizontalHeaderLabels(["User", "Số lượng trò chuyện", "Lần cuối", "Hành động"])
        
        # Style table - exactly like users table
        self.conversations_table.setStyleSheet("""
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
                background: rgba(0, 255, 170, 50);
                color: #1a1f2a;
                padding: 15px;
                border: none;
                font-weight: bold;
                font-size: 15px;
                border-right: 1px solid rgba(0, 255, 170, 30);
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
        
        # Make table fill the space - same as users table
        self.conversations_table.horizontalHeader().setStretchLastSection(True)
        self.conversations_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Set row height for larger cells - same as users table
        self.conversations_table.verticalHeader().setDefaultSectionSize(50)
        self.conversations_table.verticalHeader().setMinimumSectionSize(40)
        
        layout.addWidget(self.conversations_table)
        
        # Control buttons - exactly like users tab
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        # Delete conversation button
        delete_conv_btn = QPushButton("Xóa Trò Chuyện")
        delete_conv_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(231, 76, 60, 0.8), stop:1 rgba(192, 57, 43, 0.8));
                border: 2px solid rgba(231, 76, 60, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(231, 76, 60, 0.9), stop:1 rgba(192, 57, 43, 0.9));
                border: 2px solid rgba(231, 76, 60, 1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(192, 57, 43, 0.7), stop:1 rgba(169, 50, 38, 0.7));
            }
        """)
        delete_conv_btn.clicked.connect(self.delete_conversation)
        button_layout.addWidget(delete_conv_btn)
        
        # Export button
        export_btn = QPushButton("Export CSV")
        export_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(52, 152, 219, 0.8), stop:1 rgba(41, 128, 185, 0.8));
                border: 2px solid rgba(52, 152, 219, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(52, 152, 219, 0.9), stop:1 rgba(41, 128, 185, 0.9));
                border: 2px solid rgba(52, 152, 219, 1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(41, 128, 185, 0.7), stop:1 rgba(31, 95, 150, 0.7));
            }
        """)
        export_btn.clicked.connect(self.export_conversations)
        button_layout.addWidget(export_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Làm Mới")
        refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(155, 89, 182, 0.8), stop:1 rgba(142, 68, 173, 0.8));
                border: 2px solid rgba(155, 89, 182, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(155, 89, 182, 0.9), stop:1 rgba(142, 68, 173, 0.9));
                border: 2px solid rgba(155, 89, 182, 1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(142, 68, 173, 0.7), stop:1 rgba(125, 60, 152, 0.7));
            }
        """)
        refresh_btn.clicked.connect(self.load_demo_conversations)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        layout.addWidget(button_frame)
        
        # Load demo data
        self.load_demo_conversations()
        
        # Enable double-click for detail view (only connect once)
        self.conversations_table.doubleClicked.connect(self.view_user_conversations)
    
    def load_demo_conversations(self):
        """Load real conversations from database - one row per user"""
        try:
            # Connect to database
            db_path = os.path.join(os.path.dirname(__file__), '..', 'conversations.db')
            print(f"Database path: {db_path}")
            
            if not os.path.exists(db_path):
                print("Database file not found!")
                self.conversations_table.setRowCount(1)
                self.conversations_table.setItem(0, 0, QTableWidgetItem("Database không tìm thấy"))
                self.conversations_table.setItem(0, 1, QTableWidgetItem("0 cuộc trò chuyện"))
                self.conversations_table.setItem(0, 2, QTableWidgetItem("Kiểm tra file conversations.db"))
                self.conversations_table.setItem(0, 3, QTableWidgetItem("Tạo database"))
                self.users_data = {"Database không tìm thấy": {"count": 0, "latest_time": None}}
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            users_table_exists = cursor.fetchone()
            
            # Check if conversations table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
            conv_table_exists = cursor.fetchone()
            
            print(f"Users table exists: {users_table_exists}")
            print(f"Conversations table exists: {conv_table_exists}")
            
            # Check actual structure of conversations table
            if conv_table_exists:
                cursor.execute("PRAGMA table_info(conversations)")
                conv_columns = cursor.fetchall()
                print(f"Conversations table columns: {conv_columns}")
                
                cursor.execute("PRAGMA table_info(users)")
                user_columns = cursor.fetchall()
                print(f"Users table columns: {user_columns}")
            
            users_data = []
            
            if users_table_exists and conv_table_exists:
                # Both tables exist, try normal query
                try:
                    # First, check what users actually exist in the database
                    cursor.execute("SELECT DISTINCT tenKhachHang FROM users WHERE tenKhachHang IS NOT NULL AND tenKhachHang != ''")
                    existing_users = cursor.fetchall()
                    print(f"Existing users: {existing_users}")
                    
                    if existing_users:
                        # Check conversations table structure to build correct query
                        cursor.execute("PRAGMA table_info(conversations)")
                        conv_columns_info = cursor.fetchall()
                        conv_columns = [col[1] for col in conv_columns_info]  # Get column names
                        
                        print(f"Available columns in conversations: {conv_columns}")
                        
                        # Build query based on available columns
                        if 'tenKhachHang' in conv_columns and 'thoiGianTao' in conv_columns:
                            # Your database structure - conversations has tenKhachHang directly
                            cursor.execute("""
                                SELECT c.tenKhachHang, COUNT(c.maCuocTroChuyen) as conversation_count, MAX(c.thoiGianTao) as latest_time
                                FROM conversations c
                                WHERE c.tenKhachHang IS NOT NULL AND c.tenKhachHang != ''
                                GROUP BY c.tenKhachHang
                                HAVING COUNT(c.maCuocTroChuyen) > 0
                                ORDER BY c.tenKhachHang
                            """)
                        elif 'userId' in conv_columns and 'thoiGian' in conv_columns:
                            # No id column, use userId for counting - only show users with conversations
                            cursor.execute("""
                                SELECT u.tenKhachHang, COUNT(c.userId) as conversation_count, MAX(c.thoiGian) as latest_time
                                FROM users u 
                                INNER JOIN conversations c ON u.id = c.userId 
                                WHERE u.tenKhachHang IS NOT NULL AND u.tenKhachHang != ''
                                GROUP BY u.tenKhachHang
                                HAVING COUNT(c.userId) > 0
                                ORDER BY u.tenKhachHang
                            """)
                        elif 'userId' in conv_columns:
                            # Only userId column, no time - only show users with conversations
                            cursor.execute("""
                                SELECT u.tenKhachHang, COUNT(c.userId) as conversation_count, NULL as latest_time
                                FROM users u 
                                INNER JOIN conversations c ON u.id = c.userId 
                                WHERE u.tenKhachHang IS NOT NULL AND u.tenKhachHang != ''
                                GROUP BY u.tenKhachHang
                                HAVING COUNT(c.userId) > 0
                                ORDER BY u.tenKhachHang
                            """)
                        else:
                            # Fallback - no valid columns, show nothing
                            users_data = []
                        
                        if users_data == []:
                            users_data = cursor.fetchall()
                        
                        print(f"Users data from normal query: {users_data}")
                    else:
                        # No users in users table, try to get from conversations directly
                        if 'userId' in [col[1] for col in cursor.execute("PRAGMA table_info(conversations)").fetchall()]:
                            cursor.execute("SELECT DISTINCT userId FROM conversations WHERE userId IS NOT NULL")
                            user_ids = cursor.fetchall()
                            print(f"User IDs from conversations: {user_ids}")
                            
                            for (user_id,) in user_ids:
                                if 'id' in conv_columns and 'thoiGian' in conv_columns:
                                    cursor.execute("""
                                        SELECT COUNT(*) as count, MAX(thoiGian) as latest_time
                                        FROM conversations 
                                        WHERE userId = ?
                                    """, (user_id,))
                                elif 'thoiGian' in conv_columns:
                                    cursor.execute("""
                                        SELECT COUNT(*) as count, MAX(thoiGian) as latest_time
                                        FROM conversations 
                                        WHERE userId = ?
                                    """, (user_id,))
                                else:
                                    cursor.execute("""
                                        SELECT COUNT(*) as count, NULL as latest_time
                                        FROM conversations 
                                        WHERE userId = ?
                                    """, (user_id,))
                                
                                result = cursor.fetchone()
                                if result:
                                    count, latest_time = result
                                    # Use userId as name if no user name available
                                    users_data.append((f"User_{user_id}", count, latest_time))
                        
                        print(f"Users data from fallback: {users_data}")
                        
                except sqlite3.Error as e:
                    print(f"SQL Error in query: {e}")
                    # Try simpler queries - just get users without conversations
                    try:
                        cursor.execute("SELECT DISTINCT tenKhachHang FROM users WHERE tenKhachHang IS NOT NULL AND tenKhachHang != ''")
                        existing_users = cursor.fetchall()
                        users_data = [(user[0], 0, None) for user in existing_users]
                        print(f"Fallback users data: {users_data}")
                    except:
                        users_data = []
                    
            elif conv_table_exists:
                # Only conversations table exists
                print("Only conversations table exists")
                try:
                    cursor.execute("SELECT DISTINCT userId FROM conversations WHERE userId IS NOT NULL")
                    user_ids = cursor.fetchall()
                    
                    for (user_id,) in user_ids:
                        cursor.execute("""
                            SELECT COUNT(*) as count, MAX(thoiGian) as latest_time
                            FROM conversations 
                            WHERE userId = ?
                        """, (user_id,))
                        
                        result = cursor.fetchone()
                        if result:
                            count, latest_time = result
                            users_data.append((f"User_{user_id}", count, latest_time))
                            
                except sqlite3.Error as e:
                    print(f"SQL Error in conversations only: {e}")
                    # Just get distinct userIds
                    try:
                        cursor.execute("SELECT DISTINCT userId FROM conversations WHERE userId IS NOT NULL")
                        user_ids = cursor.fetchall()
                        users_data = [(f"User_{user_id}", 0, None) for (user_id,) in user_ids]
                    except:
                        users_data = []
                    
            else:
                print("No valid tables found")
            
            conn.close()
            
            # If still no data, show message with option to create demo data
            if not users_data:
                users_data = [("Không có dữ liệu", 0, None)]
                
                # Add a button to create demo data
                create_demo_btn = QPushButton("Tạo Demo Data")
                create_demo_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                       stop:0 #27ae60, stop:1 #229954);
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 8px 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                       stop:0 #2ecc71, stop:1 #27ae60);
                    }
                """)
                create_demo_btn.clicked.connect(self.create_demo_data)
                
                # Replace the "Double-click để xem chi tiết" with demo button
                self.conversations_table.setCellWidget(0, 3, create_demo_btn)
            
            print(f"Final users data: {users_data}")
            
            self.conversations_table.setRowCount(len(users_data))
            for i, (user, count, latest_time) in enumerate(users_data):
                self.conversations_table.setItem(i, 0, QTableWidgetItem(user))
                self.conversations_table.setItem(i, 1, QTableWidgetItem(f"{count} cuộc trò chuyện"))
                self.conversations_table.setItem(i, 2, QTableWidgetItem(f"Lúc {latest_time}" if latest_time else "Chưa có"))
                if i == 0 and len(users_data) == 1 and user == "Không có dữ liệu":
                    # Keep the demo button
                    pass
                else:
                    self.conversations_table.setItem(i, 3, QTableWidgetItem("Double-click để xem chi tiết"))
            
            # Store user data for detail view
            self.users_data = {user: {"count": count, "latest_time": latest_time} for user, count, latest_time in users_data}
            
        except Exception as e:
            print(f"Error loading user data: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error message in table
            self.conversations_table.setRowCount(1)
            self.conversations_table.setItem(0, 0, QTableWidgetItem("Lỗi database"))
            self.conversations_table.setItem(0, 1, QTableWidgetItem("0 cuộc trò chuyện"))
            self.conversations_table.setItem(0, 2, QTableWidgetItem(f"Lỗi: {str(e)[:50]}..."))
            self.conversations_table.setItem(0, 3, QTableWidgetItem("Kiểm tra console"))
            
            self.users_data = {"Lỗi database": {"count": 0, "latest_time": None}}
    
    def create_demo_data(self):
        """Create demo data in database"""
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'conversations.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if tables exist, create them if not
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tenKhachHang TEXT NOT NULL,
                        email TEXT,
                        password TEXT,
                        createdDate TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("Created users table")
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        userId INTEGER,
                        noiDung TEXT NOT NULL,
                        thoiGian TEXT DEFAULT CURRENT_TIMESTAMP,
                        phanLoai TEXT
                    )
                """)
                print("Created conversations table")
            
            # Insert demo users
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                demo_users = [
                    ("Admin", "admin@popassistant.com", "admin123"),
                    ("Nguyễn Văn An", "an.nguyen@email.com", "user123"),
                    ("Trần Thị Bình", "binh.tran@email.com", "user123"),
                    ("Lê Văn Cường", "cuong.le@email.com", "user123")
                ]
                
                cursor.executemany("""
                    INSERT INTO users (tenKhachHang, email, password)
                    VALUES (?, ?, ?)
                """, demo_users)
                print(f"Inserted {len(demo_users)} demo users")
            
            # Insert demo conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conv_count = cursor.fetchone()[0]
            
            if conv_count == 0:
                # Get user IDs
                cursor.execute("SELECT id, tenKhachHang FROM users")
                users = cursor.fetchall()
                
                demo_conversations = [
                    # Admin conversations
                    (1, "Xin chào, tôi là admin. Tôi cần kiểm tra hệ thống quản lý trò chuyện.", "2024-01-15 09:00:00", "Hệ thống"),
                    (1, "Tính năng quản lý nội dung trò chuyện đang hoạt động tốt.", "2024-01-15 09:05:00", "Hệ thống"),
                    (1, "Đã thêm các tính năng tìm kiếm và lọc theo user.", "2024-01-15 09:10:00", "Hệ thống"),
                    
                    # Nguyễn Văn An conversations
                    (2, "Xin chào, tôi là Nguyễn Văn An. Làm thế nào để sử dụng Pop Assistant?", "2024-01-15 10:30:00", "Hỏi đáp"),
                    (2, "Tôi muốn biết về tính năng nhận dạng giọng nói.", "2024-01-15 10:35:00", "Tính năng"),
                    (2, "Cảm ơn, tôi đã hiểu cách sử dụng.", "2024-01-15 10:45:00", "Phản hồi"),
                    
                    # Trần Thị Bình conversations
                    (3, "Pop Assistant có hỗ trợ tiếng Việt không?", "2024-01-15 11:20:00", "Hỏi đáp"),
                    (3, "Tôi muốn hỏi về cài đặt âm thanh cho ứng dụng.", "2024-01-15 11:25:00", "Cài đặt"),
                    (3, "Âm thanh rất rõ và dễ nghe. Cảm ơn!", "2024-01-15 11:35:00", "Phản hồi"),
                    
                    # Lê Văn Cường conversations
                    (4, "Làm sao để kết nối Pop Assistant với database?", "2024-01-15 14:15:00", "Kỹ thuật"),
                    (4, "Tôi gặp lỗi khi khởi động ứng dụng.", "2024-01-15 14:20:00", "Lỗi"),
                    (4, "Sau khi khởi động lại thì đã ổn.", "2024-01-15 14:30:00", "Phản hồi"),
                ]
                
                cursor.executemany("""
                    INSERT INTO conversations (userId, noiDung, thoiGian, phanLoai)
                    VALUES (?, ?, ?, ?)
                """, demo_conversations)
                print(f"Inserted {len(demo_conversations)} demo conversations")
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Thành công", "Đã tạo demo data thành công!\n\n4 users và 12 conversations đã được thêm vào database.")
            
            # Reload data
            self.load_demo_conversations()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi tạo demo data: {e}")
            print(f"Error creating demo data: {e}")
            import traceback
            traceback.print_exc()
    
    def view_user_conversations(self):
        """View all conversations for a user (called by double-click)"""
        selected_row = self.conversations_table.currentRow()
        if selected_row >= 0:
            user = self.conversations_table.item(selected_row, 0).text()
            
            # Load conversations from database
            try:
                db_path = os.path.join(os.path.dirname(__file__), '..', 'conversations.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check database structure
                cursor.execute("PRAGMA table_info(conversations)")
                conv_columns_info = cursor.fetchall()
                conv_columns = [col[1] for col in conv_columns_info]
                
                conversations = []
                
                # Your database structure - conversations has tenKhachHang directly
                if 'tenKhachHang' in conv_columns and 'thoiGianTao' in conv_columns:
                    cursor.execute("""
                        SELECT c.maCuocTroChuyen, c.tinNhanCuaKhach, c.tinNhanCuaBot, c.thoiGianTao, c.maPhien
                        FROM conversations c
                        WHERE c.tenKhachHang = ?
                        ORDER BY c.thoiGianTao DESC
                    """, (user,))
                    
                    raw_conversations = cursor.fetchall()
                    
                    # Convert to our format
                    for conv_id, customer_msg, bot_msg, time, session in raw_conversations:
                        # Combine customer and bot messages
                        if customer_msg and bot_msg:
                            content = f"Khách: {customer_msg}\n\nBot: {bot_msg}"
                        elif customer_msg:
                            content = f"Khách: {customer_msg}"
                        elif bot_msg:
                            content = f"Bot: {bot_msg}"
                        else:
                            content = "Không có nội dung"
                        
                        conversations.append((conv_id, content, time, "Chat"))
                        
                elif 'userId' in conv_columns:
                    # Try by userId (for User_X format)
                    if user.startswith("User_"):
                        user_id = user.replace("User_", "")
                        cursor.execute("""
                            SELECT id, noiDung, thoiGian, phanLoai
                            FROM conversations 
                            WHERE userId = ?
                            ORDER BY thoiGian DESC
                        """, (user_id,))
                        
                        conversations = cursor.fetchall()
                
                conn.close()
                
            except Exception as e:
                print(f"Error loading conversations for {user}: {e}")
                conversations = []
            
            # Create detail dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Tất cả trò chuyện của {user}")
            dialog.setFixedSize(900, 700)
            dialog.setStyleSheet("""
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
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Header
            header_frame = QFrame()
            header_frame.setStyleSheet("""
                QFrame {
                    background: rgba(0, 255, 170, 10);
                    border: 1px solid rgba(0, 255, 170, 30);
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            header_layout = QVBoxLayout(header_frame)
            
            title_label = QLabel(f"{user} - {len(conversations)} cuộc trò chuyện")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ffaa;")
            header_layout.addWidget(title_label)
            
            summary_label = QLabel(f"Tổng số: {len(conversations)} cuộc trò chuyện")
            summary_label.setStyleSheet("color: #3498db; font-weight: bold;")
            header_layout.addWidget(summary_label)
            
            layout.addWidget(header_frame)
            
            # Create scrollable area for conversations
            scroll_area = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            
            if conversations:
                # Add each conversation
                for i, (conv_id, content, time, classification) in enumerate(conversations):
                    # Conversation frame
                    conv_frame = QFrame()
                    conv_layout = QVBoxLayout(conv_frame)
                    
                    # Conversation header
                    conv_header = QHBoxLayout()
                    
                    conv_id_label = QLabel(f"ID: {conv_id}")
                    conv_id_label.setStyleSheet("color: #00ffaa; font-weight: bold;")
                    conv_header.addWidget(conv_id_label)
                    
                    time_label = QLabel(time)
                    time_label.setStyleSheet("color: #95a5a6; font-size: 10px;")
                    conv_header.addWidget(time_label)
                    
                    if classification:
                        class_label = QLabel(f"[{classification}]")
                        class_label.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 10px;")
                        conv_header.addWidget(class_label)
                    
                    conv_header.addStretch()
                    
                    # Delete button
                    delete_btn = QPushButton("Xóa")
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background: rgba(231, 76, 60, 0.8);
                            color: white;
                            border: none;
                            border-radius: 4px;
                            padding: 4px 8px;
                            font-size: 10px;
                        }
                    """)
                    delete_btn.clicked.connect(lambda checked, cid=conv_id: QMessageBox.information(dialog, "Thông báo", f"Xóa cuộc trò chuyện #{cid}"))
                    conv_header.addWidget(delete_btn)
                    
                    conv_layout.addLayout(conv_header)
                    
                    # Content
                    content_label = QLabel("Nội dung:")
                    content_label.setStyleSheet("font-weight: bold; color: #00ffaa; margin-top: 5px;")
                    conv_layout.addWidget(content_label)
                    
                    content_text = QTextEdit()
                    content_text.setPlainText(content)
                    content_text.setReadOnly(True)
                    content_text.setFixedHeight(100)
                    conv_layout.addWidget(content_text)
                    
                    scroll_layout.addWidget(conv_frame)
            else:
                # No conversations message
                no_conv_label = QLabel("Không có cuộc trò chuyện nào cho user này")
                no_conv_label.setStyleSheet("color: #e74c3c; font-size: 14px; font-weight: bold; padding: 20px;")
                no_conv_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                scroll_layout.addWidget(no_conv_label)
            
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            layout.addWidget(scroll_area)
            
            # Bottom buttons
            button_layout = QHBoxLayout()
            
            export_user_btn = QPushButton("Export User Data")
            export_user_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                   stop:0 rgba(52, 152, 219, 0.8), stop:1 rgba(41, 128, 185, 0.8));
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
            """)
            export_user_btn.clicked.connect(lambda: QMessageBox.information(dialog, "Thông báo", f"Export dữ liệu của {user}"))
            button_layout.addWidget(export_user_btn)
            
            close_btn = QPushButton("Đóng")
            close_btn.clicked.connect(dialog.accept)
            button_layout.addStretch()
            button_layout.addWidget(close_btn)
            
            
            dialog.exec()
        else:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một user")
    
    def delete_conversation(self):
        """Delete selected conversation"""
        selected_row = self.conversations_table.currentRow()
        if selected_row >= 0:
            conv_id = self.conversations_table.item(selected_row, 0).text()
            
            reply = QMessageBox.question(
                self, "Xác nhận", 
                f"Bạn có chắc muốn xóa trò chuyện #{conv_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.conversations_table.removeRow(selected_row)
                QMessageBox.information(self, "Thành công", f"Đã xóa trò chuyện #{conv_id}")
        else:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một cuộc trò chuyện")
    
    def export_conversations(self):
        """Export conversations to CSV"""
        try:
            # Demo data for export
            demo_data = [
                (1, "Admin", "Xin chào, tôi cần hỗ trợ về tính năng quản lý nội dung trò chuyện", "2024-01-15 10:30:00"),
                (2, "User1", "Làm sao để sử dụng tính năng chat trong Pop Assistant?", "2024-01-15 11:00:00"),
                (3, "User2", "Tôi muốn hỏi về cài đặt âm thanh", "2024-01-15 14:20:00"),
                (4, "Admin", "Bạn có thể vào phần Cài đặt > Âm thanh để điều chỉnh", "2024-01-15 14:25:00"),
                (5, "User1", "Cảm ơn, tôi đã tìm thấy và cài đặt thành công", "2024-01-15 15:10:00")
            ]
            
            # Choose save location
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Lưu file", 
                f"conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("ID,User,Nội dung,Thời gian\n")
                    for row in demo_data:
                        # Escape quotes and commas
                        clean_row = []
                        for item in row:
                            if item:
                                clean_item = str(item).replace('"', '""')
                                if ',' in clean_item or '\n' in clean_item:
                                    clean_item = f'"{clean_item}"'
                                clean_row.append(clean_item)
                            else:
                                clean_row.append("")
                        f.write(",".join(clean_row) + "\n")
                
                QMessageBox.information(self, "Thành công", f"Đã xuất {len(demo_data)} bản ghi")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi xuất: {e}")

def create_admin_panel():
    """Create admin panel window"""
    return AdminPanel()

def main():
    """Main function to run admin panel"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Pop Assistant Admin Panel")
    app.setOrganizationName("Pop AI")
    
    # Create admin panel
    admin_panel = AdminPanel()
    admin_panel.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
