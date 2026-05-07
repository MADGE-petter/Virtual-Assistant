"""SQL/Database Service module - Quản lý database operations."""

import os
import sys
import sqlite3

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.conversation_db import ConversationDB


class SqlService:
    
    def __init__(self, db_path=None):
       
        if db_path is None:
            self.db = ConversationDB()
        else:
            self.db = ConversationDB(db_path)
        self.current_session_id = None
        
    def get_connection(self):
        """Lấy database connection."""
        import sqlite3
        return sqlite3.connect(self.db.db_path)
        
    def start_session(self, user_name):
       
        self.current_session_id = self.db.start_session(user_name)
        return self.current_session_id
    
    def end_session(self, session_id=None):
        
        sid = session_id or self.current_session_id
        if sid:
            self.db.end_session(sid)
            if sid == self.current_session_id:
                self.current_session_id = None
    
    def save_conversation(self, user_name, user_msg, bot_response, session_id=None):
       
        sid = session_id or self.current_session_id
        
        # Lấy hoặc tạo user_id từ username
        user_id = self.db.get_or_create_user(user_name)
        
        self.db.save_conversation(user_id, sid, user_msg, bot_response)
    
    def get_session_conversations(self, session_id):
        
        return self.db.get_session_conversations(session_id)
    
    def get_all_sessions(self, user_name):
      
        return self.db.get_all_sessions(user_name)
    
    def get_user_stats(self, user_name):
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) as total_conversations,
                       COUNT(DISTINCT DATE(thoiGianTao)) as total_days,
                       COUNT(DISTINCT maPhien) as total_sessions
                FROM conversations c
                JOIN users u ON c.maNguoiDung = u.maNguoiDung
                WHERE u.tenNguoiDung = ?
            """, (user_name,))
            
            stats = cursor.fetchone()
            conn.close()
            
            return {
                'total_conversations': stats[0],
                'total_days': stats[1],
                'total_sessions': stats[2],
                'avg_per_day': stats[0] / max(stats[1], 1)
            }
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return None
    
    def get_daily_stats(self, user_name, limit=30):
       
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DATE(thoiGianTao) as date,
                       COUNT(*) as conversation_count,
                       COUNT(DISTINCT maPhien) as session_count
                FROM conversations c
                JOIN users u ON c.maNguoiDung = u.maNguoiDung
                WHERE u.tenNguoiDung = ?
                GROUP BY DATE(thoiGianTao)
                ORDER BY date DESC
                LIMIT ?
            """, (user_name, limit))
            
            stats = cursor.fetchall()
            conn.close()
            return stats
        except Exception as e:
            print(f"Error getting daily stats: {e}")
            return []
    
    def get_first_use_date(self, user_name):
       
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT MIN(c.thoiGianTao) FROM conversations c
                JOIN users u ON c.maNguoiDung = u.maNguoiDung
                WHERE u.tenNguoiDung = ?
            """, (user_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return result[0].replace('T', ' ')[:19]
            return "Chưa có dữ liệu"
        except:
            return "Không xác định"
    
    def delete_old_conversations(self, days=30):
       
        self.db.delete_old_conversations(days)
    
    def get_statistics(self, user_name):
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) as total_conversations,
                       COUNT(DISTINCT DATE(thoiGianTao)) as total_days,
                       COUNT(DISTINCT maPhien) as total_sessions
                FROM conversations c
                JOIN users u ON c.maNguoiDung = u.maNguoiDung
                WHERE u.tenNguoiDung = ?
            """, (user_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result if result else (0, 0, 0)
        except:
            return (0, 0, 0)
    
    def get_daily_statistics(self, user_name, limit=30):
       
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DATE(thoiGianTao) as date,
                       COUNT(*) as conversation_count,
                       COUNT(DISTINCT maPhien) as session_count
                FROM conversations c
                JOIN users u ON c.maNguoiDung = u.maNguoiDung
                WHERE u.tenNguoiDung = ?
                GROUP BY DATE(thoiGianTao)
                ORDER BY date DESC
                LIMIT ?
            """, (user_name, limit))
            
            result = cursor.fetchall()
            conn.close()
            
            return result
        except:
            return []
    
    def clear_history(self, user_name=None):
       
        self.db.clear_history(user_name)
    
    def get_most_recent_user(self):
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tenNguoiDung 
                FROM users 
                WHERE tenNguoiDung != 'bạn'
                ORDER BY maNguoiDung DESC 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting most recent user: {e}")
            return None
    
    def update_user_name(self, old_name, new_name, session_id=None):
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Tạo hoặc lấy user ID cho tên mới
            cursor.execute("SELECT maNguoiDung FROM users WHERE tenNguoiDung = ?", (new_name,))
            user_result = cursor.fetchone()
            
            if not user_result:
                # Tạo user mới
                cursor.execute("INSERT INTO users (tenNguoiDung) VALUES (?)", (new_name,))
                new_user_id = cursor.lastrowid
            else:
                new_user_id = user_result[0]
            
            if session_id:
                # Cập nhật conversations trong session hiện tại
                cursor.execute("""
                    UPDATE conversations 
                    SET maNguoiDung = ? 
                    WHERE maPhien = ?
                """, (new_user_id, session_id))
                
                # Cập nhật session
                cursor.execute("""
                    UPDATE sessions 
                    SET maNguoiDung = ? 
                    WHERE maPhien = ?
                """, (new_user_id, session_id))
            
            conn.commit()
            conn.close()
            print(f"Đã cập nhật tên từ '{old_name}' thành '{new_name}' (session: {session_id})")
        except Exception as e:
            print(f"Error updating user name: {e}")
