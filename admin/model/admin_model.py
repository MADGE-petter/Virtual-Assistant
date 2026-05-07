#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - Admin Model
Quản lý dữ liệu và business logic cho admin panel
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import hashlib


class AdminModel:
    """Model layer cho Admin Panel - quản lý dữ liệu và business logic"""
    
    def __init__(self, db_path: str = None):
        """Khởi tạo AdminModel
        
        Args:
            db_path: Đường dẫn đến database SQLite
        """
        if db_path is None:
            # Dùng chung database với main app
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'conversations.db')
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Khởi tạo bảng admin_users nếu chưa tồn tại"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Kiểm tra bảng admin_users đã tồn tại chưa
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_users'")
                if not cursor.fetchone():
                    # Tạo bảng admin_users theo schema gốc
                    cursor.execute('''
                        CREATE TABLE admin_users (
                            maAdmin INTEGER PRIMARY KEY AUTOINCREMENT,
                            tenAdmin TEXT NOT NULL UNIQUE,
                            matKhauMaHoa TEXT NOT NULL,
                            email TEXT,
                            thoiGianTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            thoiGianCapNhat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                else:
                    # Migration: thêm cột email nếu chưa tồn tại
                    cursor.execute("PRAGMA table_info(admin_users)")
                    columns = [col[1] for col in cursor.fetchall()]
                    if 'email' not in columns:
                        cursor.execute("ALTER TABLE admin_users ADD COLUMN email TEXT")
                        print("Đã thêm cột email vào bảng admin_users")
                
                # Tạo bảng system_logs nếu chưa tồn tại
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_logs'")
                if not cursor.fetchone():
                    cursor.execute('''
                        CREATE TABLE system_logs (
                            maLog INTEGER PRIMARY KEY AUTOINCREMENT,
                            level TEXT,
                            message TEXT,
                            module TEXT,
                            thoiGianTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    print("Đã tạo bảng system_logs")
                
                conn.commit()
                
                # Tạo admin mặc định nếu chưa có
                self._create_default_admin()
                
        except Exception as e:
            print(f"Lỗi khởi tạo database admin: {e}")
    
    def _create_default_admin(self):
        """Tạo tài khoản admin mặc định"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Kiểm tra admin đã tồn tại chưa
                cursor.execute("SELECT COUNT(*) FROM admin_users WHERE tenAdmin = 'admin'")
                if cursor.fetchone()[0] == 0:
                    # Tạo admin mặc định: admin/admin123
                    password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                    cursor.execute('''
                        INSERT INTO admin_users (tenAdmin, matKhauMaHoa, email)
                        VALUES (?, ?, ?)
                    ''', ('admin', password_hash, 'admin@popassistant.local'))
                    
                    # Log tạo admin (bỏ qua nếu lỗi)
                    try:
                        cursor.execute('''
                            INSERT INTO system_logs (level, message, module)
                            VALUES (?, ?, ?)
                        ''', ('INFO', 'Tạo tài khoản admin mặc định', 'AUTH'))
                    except:
                        pass
                    
                    conn.commit()
                    print("Đã tạo tài khoản admin mặc định: admin/admin123")
                    
        except Exception as e:
            print(f"Lỗi tạo admin mặc định: {e}")
    
    def verify_admin_login(self, username: str, password: str) -> Optional[Dict]:
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute('''
                    SELECT maAdmin, tenAdmin, email
                    FROM admin_users 
                    WHERE tenAdmin = ? AND matKhauMaHoa = ?
                ''', (username, password_hash))
                
                result = cursor.fetchone()
                if result:
                    # Cập nhật last login
                    cursor.execute('''
                        UPDATE admin_users 
                        SET thoiGianCapNhat = CURRENT_TIMESTAMP 
                        WHERE maAdmin = ?
                    ''', (result[0],))
                    
                    # Log đăng nhập thành công
                    cursor.execute('''
                        INSERT INTO system_logs (level, message, module, user_id)
                        VALUES (?, ?, ?, ?)
                    ''', ('INFO', f'Admin {username} đăng nhập thành công', 'AUTH', result[0]))
                    
                    conn.commit()
                    
                    return {
                        'id': result[0],
                        'username': result[1],
                        'email': result[2],
                        'role': 'admin'
                    }
                else:
                    # Log đăng nhập thất bại
                    cursor.execute('''
                        INSERT INTO system_logs (level, message, module)
                        VALUES (?, ?, ?)
                    ''', ('WARNING', f'Đăng nhập thất bại: {username}', 'AUTH'))
                    
                    conn.commit()
                    return None
                    
        except Exception as e:
            print(f"Lỗi xác thực admin: {e}")
            return None
    
    def get_user_statistics(self) -> Dict:
      
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tổng số người dùng - sử dụng bảng users
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                # Users hoạt động trong 7 ngày - sử dụng bảng conversations
                cursor.execute('''
                    SELECT COUNT(DISTINCT maNguoiDung) 
                    FROM conversations 
                    WHERE thoiGianTao >= datetime('now', '-7 days')
                ''')
                active_users = cursor.fetchone()[0]
                
                # Users hoạt động trong 30 ngày
                cursor.execute('''
                    SELECT COUNT(DISTINCT maNguoiDung) 
                    FROM conversations 
                    WHERE thoiGianTao >= datetime('now', '-30 days')
                ''')
                monthly_users = cursor.fetchone()[0]
                
                # Tổng số sessions - sử dụng bảng sessions
                cursor.execute("SELECT COUNT(*) FROM sessions")
                total_sessions = cursor.fetchone()[0]
                
                # Tổng số conversations
                cursor.execute("SELECT COUNT(*) FROM conversations")
                total_conversations = cursor.fetchone()[0]
                
                return {
                    'total_users': total_users or 0,
                    'active_users_7d': active_users or 0,
                    'active_users_30d': monthly_users or 0,
                    'total_sessions': total_sessions or 0,
                    'total_conversations': total_conversations or 0
                }
                
        except Exception as e:
            print(f"Lỗi lấy thống kê người dùng: {e}")
            return {}
    
    def get_conversation_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
       
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COALESCE(u.tenNguoiDung, 'Unknown') as tenNguoiDung, 
                           COALESCE(c.tinNhanCuaKhach, '') as tinNhanCuaKhach, 
                           COALESCE(c.tinNhanCuaBot, '') as tinNhanCuaBot, 
                           COALESCE(c.thoiGianTao, datetime('now')) as thoiGianTao, 
                           COALESCE(c.maPhien, '') as maPhien
                    FROM conversations c
                    LEFT JOIN users u ON c.maNguoiDung = u.maNguoiDung
                    ORDER BY COALESCE(c.thoiGianTao, datetime('now')) DESC 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
                
                columns = ['user_name', 'user_input', 'bot_response', 'created_at', 'session_id']
                results = []
                
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
                
        except Exception as e:
            print(f"Lỗi lấy lịch sử trò chuyện: {e}")
            return []
    
    
    
    
    
    def export_data(self, data_type: str, start_date: str = None, end_date: str = None) -> str:
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{data_type}_export_{timestamp}.csv"
            filepath = os.path.join(os.path.dirname(__file__), '..', '..', 'exports', filename)
            
            # Tạo thư mục exports nếu chưa có
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if data_type == 'conversations':
                    query = '''
                        SELECT u.tenNguoiDung, c.tinNhanCuaKhach, c.tinNhanCuaBot, c.thoiGianTao, c.maPhien
                        FROM conversations c
                        LEFT JOIN users u ON c.maNguoiDung = u.maNguoiDung
                    '''
                    params = []
                    
                    if start_date and end_date:
                        query += ' WHERE c.thoiGianTao BETWEEN ? AND ?'
                        params = [start_date, end_date]
                    
                    query += ' ORDER BY c.thoiGianTao'
                    
                elif data_type == 'users':
                    query = '''
                        SELECT tenNguoiDung, 
                               thoiGianTao,
                               (SELECT MAX(thoiGianTao) FROM conversations WHERE maNguoiDung = u.maNguoiDung) as last_interaction,
                               (SELECT COUNT(*) FROM conversations WHERE maNguoiDung = u.maNguoiDung) as total_interactions
                        FROM users u
                        ORDER BY thoiGianTao
                    '''
                    params = []
                    
                elif data_type == 'logs':
                    query = '''
                        SELECT level, message, module, created_at
                        FROM system_logs
                    '''
                    params = []
                    
                    if start_date and end_date:
                        query += ' WHERE created_at BETWEEN ? AND ?'
                        params = [start_date, end_date]
                    
                    query += ' ORDER BY created_at'
                
                cursor.execute(query, params)
                
                # Export to CSV
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    if data_type == 'conversations':
                        writer.writerow(['User', 'User Input', 'Bot Response', 'Created At', 'Session ID'])
                    elif data_type == 'users':
                        writer.writerow(['User Name', 'Created At', 'Last Interaction', 'Total Interactions'])
                    elif data_type == 'logs':
                        writer.writerow(['Level', 'Message', 'Module', 'Created At'])
                    
                    # Write data
                    writer.writerows(cursor.fetchall())
            
            # Log export
            self.add_system_log('INFO', f'Export dữ liệu: {data_type} -> {filename}', 'EXPORT')
            
            return filepath
            
        except Exception as e:
            print(f"Lỗi export dữ liệu: {e}")
            return None
    
    def cleanup_old_data(self, days: int = 30) -> int:
     
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Xóa conversations cũ
                cursor.execute('''
                    DELETE FROM conversations 
                    WHERE thoiGianTao < datetime('now', '-{} days')
                '''.format(days))
                conversations_deleted = cursor.rowcount
                
                # Xóa logs cũ (chỉ giữ INFO và WARNING)
                cursor.execute('''
                    DELETE FROM system_logs 
                    WHERE created_at < datetime('now', '-{} days') AND level = 'INFO'
                '''.format(days))
                logs_deleted = cursor.rowcount
                
                conn.commit()
                
                total_deleted = conversations_deleted + logs_deleted
                
                # Log cleanup
                self.add_system_log('INFO', f'Dọn dẹp dữ liệu cũ: xóa {total_deleted} bản ghi', 'CLEANUP')
                
                return total_deleted
                
        except Exception as e:
            print(f"Lỗi dọn dẹp dữ liệu cũ: {e}")
            return 0
