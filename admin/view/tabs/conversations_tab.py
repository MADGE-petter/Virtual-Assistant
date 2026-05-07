#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - Conversations Tab
Tab quản lý trò chuyện
"""

import os
import sqlite3
import csv
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
                            QDialog, QLabel, QTextEdit, QScrollArea, QFileDialog)
from PyQt6.QtCore import Qt
from admin.view.tabs.base_tab import BaseTab
from admin.view.styles import TABLE_WIDGET, BUTTON_RED, BUTTON_BLUE, BUTTON_PURPLE, DIALOG_CONVERSATION, CONVERSATION_HEADER


class ConversationsTab(BaseTab):
    """Tab quản lý trò chuyện"""
    
    def __init__(self, parent=None, log_callback=None):
        super().__init__(parent, log_callback)
        self.users_data = {}
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Conversations table
        self.conversations_table = QTableWidget()
        self.conversations_table.setColumnCount(4)
        self.conversations_table.setHorizontalHeaderLabels(["User", "Số lượng trò chuyện", "Lần cuối", "Hành động"])
        self.conversations_table.setStyleSheet(TABLE_WIDGET)
        self.conversations_table.horizontalHeader().setStretchLastSection(True)
        self.conversations_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.conversations_table.verticalHeader().setDefaultSectionSize(50)
        self.conversations_table.verticalHeader().setMinimumSectionSize(40)
        layout.addWidget(self.conversations_table)
        
        # Control buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        # Delete conversation button
        delete_conv_btn = QPushButton("Xóa Trò Chuyện")
        delete_conv_btn.setStyleSheet(BUTTON_RED)
        delete_conv_btn.clicked.connect(self.delete_conversation)
        button_layout.addWidget(delete_conv_btn)
        
        # Export button
        export_btn = QPushButton("Export CSV")
        export_btn.setStyleSheet(BUTTON_BLUE)
        export_btn.clicked.connect(self.export_conversations)
        button_layout.addWidget(export_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Làm Mới")
        refresh_btn.setStyleSheet(BUTTON_PURPLE)
        refresh_btn.clicked.connect(self.load_data)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        layout.addWidget(button_frame)
        
        # Enable double-click for detail view
        self.conversations_table.doubleClicked.connect(self.view_user_conversations)
    
    def load_data(self):
        """Load conversations from database"""
        try:
            if not os.path.exists(self.db_path):
                self._show_no_data(f"DB không tìm thấy: {self.db_path}")
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            users_data = []
            
            # Check tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            users_table_exists = cursor.fetchone()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
            conv_table_exists = cursor.fetchone()
            
            # Debug
            print(f"[ConversationsTab] DB: {self.db_path}")
            print(f"[ConversationsTab] users table: {users_table_exists}, conversations table: {conv_table_exists}")
            
            if users_table_exists and conv_table_exists:
                # Count data
                cursor.execute("SELECT COUNT(*) FROM conversations")
                conv_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                print(f"[ConversationsTab] conversations: {conv_count}, users: {user_count}")
                
                # Debug: Check sample conversations
                cursor.execute("SELECT maCuocTroChuyen, maNguoiDung, thoiGianTao FROM conversations LIMIT 5")
                sample = cursor.fetchall()
                print(f"[ConversationsTab] Sample conversations: {sample}")
                
                # Get conversations columns
                cursor.execute("PRAGMA table_info(conversations)")
                conv_columns = [col[1] for col in cursor.fetchall()]
                
                if 'maNguoiDung' in conv_columns and 'thoiGianTao' in conv_columns:
                    # LEFT JOIN để lấy tất cả users, kể cả chưa có conversation
                    cursor.execute("""
                        SELECT u.tenNguoiDung, 
                               COUNT(c.maCuocTroChuyen) as conversation_count, 
                               MAX(c.thoiGianTao) as latest_time
                        FROM users u
                        LEFT JOIN conversations c ON c.maNguoiDung = u.maNguoiDung
                        WHERE u.tenNguoiDung IS NOT NULL AND u.tenNguoiDung != ''
                        GROUP BY u.maNguoiDung, u.tenNguoiDung
                        ORDER BY conversation_count DESC, u.tenNguoiDung
                    """)
                    users_data = cursor.fetchall()
                    print(f"[ConversationsTab] Query returned {len(users_data)} users")
                else:
                    print(f"[ConversationsTab] Missing columns. Available: {conv_columns}")
            else:
                print(f"[ConversationsTab] Tables missing - users: {users_table_exists}, conv: {conv_table_exists}")
            
            conn.close()
            
            if not users_data:
                self._show_no_data(f"Không có dữ liệu (conv: {conv_count if 'conv_count' in dir() else '?'}, users: {user_count if 'user_count' in dir() else '?'})")
                return
            
            self._populate_table(users_data)
            
        except Exception as e:
            self.log(f"Error: {e}")
            self._show_no_data(f"Lỗi: {str(e)[:50]}")
    
    def _show_no_data(self, message):
        """Show no data message in table"""
        self.conversations_table.setRowCount(1)
        self.conversations_table.setItem(0, 0, QTableWidgetItem(message))
        self.conversations_table.setItem(0, 1, QTableWidgetItem("0"))
        self.conversations_table.setItem(0, 2, QTableWidgetItem("-"))
        self.conversations_table.setItem(0, 3, QTableWidgetItem("-"))
        self.users_data = {}
    
    def _populate_table(self, users_data):
        """Populate table with user data"""
        self.conversations_table.setRowCount(len(users_data))
        
        for i, (user, count, latest_time) in enumerate(users_data):
            self.conversations_table.setItem(i, 0, QTableWidgetItem(user))
            self.conversations_table.setItem(i, 1, QTableWidgetItem(f"{count} cuộc trò chuyện"))
            self.conversations_table.setItem(i, 2, QTableWidgetItem(f"Lúc {latest_time}" if latest_time else "Chưa có"))
            self.conversations_table.setItem(i, 3, QTableWidgetItem("Double-click để xem chi tiết"))
        
        # Store for detail view
        self.users_data = {user: {"count": count, "latest_time": latest_time} 
                          for user, count, latest_time in users_data}
    
    def view_user_conversations(self):
        """View all conversations for selected user"""
        selected_row = self.conversations_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một user")
            return
        
        user = self.conversations_table.item(selected_row, 0).text()
        
        # Load conversations
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(conversations)")
            conv_columns = [col[1] for col in cursor.fetchall()]
            
            conversations = []
            
            if 'maNguoiDung' in conv_columns and 'thoiGianTao' in conv_columns:
                cursor.execute("""
                    SELECT c.maCuocTroChuyen, c.tinNhanCuaKhach, c.tinNhanCuaBot, c.thoiGianTao, c.maPhien
                    FROM conversations c
                    INNER JOIN users u ON c.maNguoiDung = u.maNguoiDung
                    WHERE u.tenNguoiDung = ?
                    ORDER BY c.thoiGianTao DESC
                """, (user,))
                
                for conv_id, customer_msg, bot_msg, time, session in cursor.fetchall():
                    if customer_msg and bot_msg:
                        content = f"Khách: {customer_msg}\n\nBot: {bot_msg}"
                    elif customer_msg:
                        content = f"Khách: {customer_msg}"
                    elif bot_msg:
                        content = f"Bot: {bot_msg}"
                    else:
                        content = "Không có nội dung"
                    
                    conversations.append((conv_id, content, time, "Chat"))
            
            conn.close()
            
        except Exception as e:
            self.log(f"Error loading conversations: {e}")
            conversations = []
        
        # Show dialog
        self._show_conversation_dialog(user, conversations)
    
    def _show_conversation_dialog(self, user, conversations):
        """Show conversation detail dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Tất cả trò chuyện của {user}")
        dialog.setFixedSize(900, 700)
        dialog.setStyleSheet(DIALOG_CONVERSATION)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet(CONVERSATION_HEADER)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel(f"{user} - {len(conversations)} cuộc trò chuyện")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ffaa;")
        header_layout.addWidget(title_label)
        
        layout.addWidget(header_frame)
        
        # Scrollable area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        if conversations:
            for i, (conv_id, content, time, classification) in enumerate(conversations):
                conv_frame = QFrame()
                conv_layout = QVBoxLayout(conv_frame)
                
                # Header
                conv_header = QHBoxLayout()
                conv_id_label = QLabel(f"ID: {conv_id}")
                conv_id_label.setStyleSheet("color: #00ffaa; font-weight: bold;")
                conv_header.addWidget(conv_id_label)
                
                time_label = QLabel(time)
                time_label.setStyleSheet("color: #95a5a6; font-size: 10px;")
                conv_header.addWidget(time_label)
                conv_header.addStretch()
                
                conv_layout.addLayout(conv_header)
                
                # Content
                content_text = QTextEdit()
                content_text.setPlainText(content)
                content_text.setReadOnly(True)
                content_text.setFixedHeight(100)
                conv_layout.addWidget(content_text)
                
                scroll_layout.addWidget(conv_frame)
        else:
            no_conv_label = QLabel("Không có cuộc trò chuyện nào")
            no_conv_label.setStyleSheet("color: #e74c3c; font-size: 14px; font-weight: bold;")
            no_conv_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            scroll_layout.addWidget(no_conv_label)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Close button
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def delete_conversation(self):
        """Delete selected conversation"""
        selected_row = self.conversations_table.currentRow()
        if selected_row >= 0:
            user = self.conversations_table.item(selected_row, 0).text()
            reply = QMessageBox.question(
                self, "Xác nhận", f"Xóa tất cả trò chuyện của '{user}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    # Get user ID
                    cursor.execute("SELECT maNguoiDung FROM users WHERE tenNguoiDung = ?", (user,))
                    result = cursor.fetchone()
                    if result:
                        user_id = result[0]
                        cursor.execute("DELETE FROM conversations WHERE maNguoiDung = ?", (user_id,))
                        conn.commit()
                        self.log(f"Deleted for: {user}")
                    
                    conn.close()
                    self.load_data()
                except Exception as e:
                    QMessageBox.critical(self, "Lỗi", f"Lỗi xóa: {e}")
        else:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn user!")
    
    def export_conversations(self):
        """Export conversations to CSV"""
        try:
            # Get data
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Lưu file",
                f"conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['User', 'Conversation Count', 'Latest Time'])
                    
                    for row in range(self.conversations_table.rowCount()):
                        user = self.conversations_table.item(row, 0).text()
                        count = self.conversations_table.item(row, 1).text()
                        time = self.conversations_table.item(row, 2).text()
                        writer.writerow([user, count, time])
                
                QMessageBox.information(self, "Thành công", f"Đã xuất dữ liệu ra {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi xuất: {e}")
