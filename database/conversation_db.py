#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversation Database Module
Quản lý lưu trữ lịch sử cuộc trò chuyện
"""

import sqlite3
import os
import sys
from datetime import datetime
import json

# Set console encoding for Vietnamese support - completely disabled to avoid PyQt6 crashes
# if sys.platform == "win32" and not hasattr(sys, 'frozen'):
#     try:
#         import codecs
#         # Only apply if we're in a console environment
#         if sys.stdout.isatty():
#             sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
#             sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
#     except:
#         # If encoding fails, continue without it
#         pass

class ConversationDB:
    def __init__(self, db_path="conversations.db"):
        """Khởi tạo database"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Tạo bảng conversations nếu chưa tồn tại"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Set UTF-8 encoding for Vietnamese support
            cursor.execute("PRAGMA encoding = 'UTF-8'")
            
            # Tạo bảng conversations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    maCuocTroChuyen INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenKhachHang TEXT NOT NULL,
                    tinNhanCuaKhach TEXT NOT NULL,
                    tinNhanCuaBot TEXT NOT NULL,
                    thoiGianTao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    maPhien TEXT
                )
            ''')
            
            # Tạo bảng sessions để theo dõi các phiên trò chuyện
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    maPhien TEXT PRIMARY KEY,
                    tenKhachHang TEXT NOT NULL,
                    thoiGianBatDau DATETIME DEFAULT CURRENT_TIMESTAMP,
                    thoiGianKetThuc DATETIME
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Database initialized successfully")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def start_session(self, user_name):
        """Bắt đầu một phiên trò chuyện mới"""
        try:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (maPhien, tenKhachHang)
                VALUES (?, ?)
            ''', (session_id, user_name))
            
            conn.commit()
            conn.close()
            return session_id
            
        except Exception as e:
            print(f"Error starting session: {e}")
            return None
    
    def end_session(self, session_id):
        """Kết thúc phiên trò chuyện"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions 
                SET thoiGianKetThuc = CURRENT_TIMESTAMP 
                WHERE maPhien = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error ending session: {e}")
    
    def save_conversation(self, user_name, user_message, bot_response, session_id=None):
        """Lưu một cuộc hội thoại vào database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ensure UTF-8 encoding
            cursor.execute("PRAGMA encoding = 'UTF-8'")
            
            cursor.execute('''
                INSERT INTO conversations (tenKhachHang, tinNhanCuaKhach, tinNhanCuaBot, maPhien)
                VALUES (?, ?, ?, ?)
            ''', (user_name, user_message, bot_response, session_id))
            
            conn.commit()
            conn.close()
            print(f"Đã lưu cuộc trò chuyện: {user_message[:50]}...")
            
        except Exception as e:
            print(f"Lỗi lưu cuộc trò chuyện: {e}")
    
    def get_recent_conversations(self, user_name, limit=10):
        """Lấy các cuộc hội thoại gần đây của người dùng"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT tinNhanCuaKhach, tinNhanCuaBot, thoiGianTao 
                FROM conversations 
                WHERE tenKhachHang = ? 
                ORDER BY thoiGianTao DESC 
                LIMIT ?
            ''', (user_name, limit))
            
            conversations = cursor.fetchall()
            conn.close()
            return conversations
            
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def get_session_conversations(self, session_id):
        """Lấy tất cả cuộc hội thoại trong một phiên"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT tinNhanCuaKhach, tinNhanCuaBot, thoiGianTao 
                FROM conversations 
                WHERE maPhien = ? 
                ORDER BY thoiGianTao ASC
            ''', (session_id,))
            
            conversations = cursor.fetchall()
            conn.close()
            return conversations
            
        except Exception as e:
            print(f"Error getting session conversations: {e}")
            return []
    
    def get_all_sessions(self, user_name):
        """Lấy tất cả các phiên của người dùng"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT maPhien, thoiGianBatDau, thoiGianKetThuc 
                FROM sessions 
                WHERE tenKhachHang = ? 
                ORDER BY thoiGianBatDau DESC
            ''', (user_name,))
            
            sessions = cursor.fetchall()
            conn.close()
            return sessions
            
        except Exception as e:
            print(f"Error getting sessions: {e}")
            return []
    
    def delete_old_conversations(self, days=30):
        """Xóa các cuộc hội thoại cũ hơn số ngày chỉ định"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM conversations 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days))
            
            cursor.execute('''
                DELETE FROM sessions 
                WHERE start_time < datetime('now', '-{} days')
            '''.format(days))
            
            conn.commit()
            conn.close()
            print(f"Deleted conversations older than {days} days")
            
        except Exception as e:
            print(f"Error deleting old conversations: {e}")

# Test function
if __name__ == "__main__":
    db = ConversationDB()
    
    # Test creating a session
    session_id = db.start_session("Người dùng test")
    print(f"Bắt đầu phiên: {session_id}")
    
    # Test saving conversations with Vietnamese content
    db.save_conversation("Người dùng test", "Xin chào Pop", "Chào bạn, tôi là Pop. Tôi có thể giúp gì cho bạn?", session_id)
    db.save_conversation("Người dùng test", "Hôm nay thời tiết ở Hà Nội thế nào?", "Xin lỗi, tôi không có thông tin thời tiết. Bạn có thể kiểm tra ứng dụng thời tiết.", session_id)
    db.save_conversation("Người dùng test", "Cảm ơn nhé", "Không có gì! Nếu cần giúp đỡ gì nữa, cứ nói nhé!", session_id)
    
    # Test retrieving conversations
    conversations = db.get_recent_conversations("Người dùng test")
    print("Các cuộc trò chuyện gần đây:")
    for conv in conversations:
        print(f"Người dùng: {conv[0]}")
        print(f"Pop: {conv[1]}")
        print(f"Thời gian: {conv[2]}")
        print("-" * 50)
    
    # End session
    db.end_session(session_id)
    print("Phiên đã kết thúc")
