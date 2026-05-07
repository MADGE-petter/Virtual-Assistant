import sqlite3
import os
from datetime import datetime

class ConversationDB:
    """Database operations for conversations"""
    
    def __init__(self, db_path: str = None):
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conversations.db')
        self.init_database()
    
    def init_database(self):
        """Initialize database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tables are created by migration script
            # Just verify connection
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            if not tables:
                raise Exception("No tables found. Run migration first!")
            
            conn.close()
            
        except Exception as e:
            print(f"Database initialization error: {e}")
            raise
    
    def save_conversation(self, user_id, session_id, user_message, bot_response, intent_type=None):
        """Save a conversation to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Debug: Log what we're saving
            print(f"[ConversationDB] Saving: user={user_id} (type={type(user_id).__name__}), session={session_id} (type={type(session_id).__name__})")
            
            cursor.execute("""
                INSERT INTO conversations (maNguoiDung, maPhien, tinNhanCuaKhach, tinNhanCuaBot, loaiYDo)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, session_id, user_message, bot_response, intent_type))
            
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            print(f"[ConversationDB] Saved successfully, rowid={last_id}")
            
        except Exception as e:
            print(f"[ConversationDB] Error saving conversation: {e}")
            import traceback
            traceback.print_exc()
    
    def get_conversations(self, user_id=None, limit=50):
        """Get conversations from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("""
                    SELECT c.*, u.tenNguoiDung, u.hoTen 
                    FROM conversations c
                    JOIN users u ON c.maNguoiDung = u.maNguoiDung
                    WHERE c.maNguoiDung = ?
                    ORDER BY c.thoiGianTao DESC
                    LIMIT ?
                """, (user_id, limit))
            else:
                cursor.execute("""
                    SELECT c.*, u.tenNguoiDung, u.hoTen 
                    FROM conversations c
                    JOIN users u ON c.maNguoiDung = u.maNguoiDung
                    ORDER BY c.thoiGianTao DESC
                    LIMIT ?
                """, (limit,))
            
            result = cursor.fetchall()
            conn.close()
            
            return result
            
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE tenNguoiDung = ?", (username,))
            result = cursor.fetchone()
            conn.close()
            
            return result
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def create_user(self, username, email=None):
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Schema không có cột email, chỉ insert tenNguoiDung
            cursor.execute("""
                INSERT INTO users (tenNguoiDung)
                VALUES (?)
            """, (username,))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_or_create_user(self, username):
        """Get existing user or create new one"""
        user = self.get_user_by_username(username)
        if user:
            return user[0]  # user_id
        else:
            return self.create_user(username)
    
    def start_session(self, user_id: int = None) -> int:
        """Bắt đầu session mới và trả về session ID (integer)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Nếu user_id là string, convert sang int nếu có thể
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
            elif user_id is None or (isinstance(user_id, str) and not user_id.isdigit()):
                # Guest user - lấy user đầu tiên hoặc tạo guest
                user_id = 1  # Default to first user
            
            cursor.execute("""
                INSERT INTO sessions (maNguoiDung, thoiGianBatDau)
                VALUES (?, ?)
            """, (user_id, datetime.now()))
            
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return session_id
            
        except Exception as e:
            print(f"Error starting session: {e}")
            return 1  # Return default session ID on error
    
    def end_session(self, session_id):
        """End a session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sessions 
                SET thoiGianKetThuc = ?
                WHERE maPhien = ?
            """, (datetime.now(), session_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error ending session: {e}")
    
    def get_user_sessions(self, user_id, limit=20):
        """Get sessions for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM sessions 
                WHERE maNguoiDung = ?
                ORDER BY thoiGianBatDau DESC
                LIMIT ?
            """, (user_id, limit))
            
            result = cursor.fetchall()
            conn.close()
            
            return result
            
        except Exception as e:
            print(f"Error getting sessions: {e}")
            return []
    
    def get_session_conversations(self, session_id, username=None):
        """Get conversations for a session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if username:
                cursor.execute("""
                    SELECT c.tinNhanCuaKhach, c.tinNhanCuaBot, c.thoiGianTao
                    FROM conversations c
                    JOIN sessions s ON c.maPhien = s.maPhien
                    JOIN users u ON s.maNguoiDung = u.maNguoiDung
                    WHERE c.maPhien = ? AND u.tenNguoiDung = ?
                    ORDER BY c.thoiGianTao ASC
                """, (session_id, username))
            else:
                cursor.execute("""
                    SELECT tinNhanCuaKhach, tinNhanCuaBot, thoiGianTao
                    FROM conversations 
                    WHERE maPhien = ?
                    ORDER BY thoiGianTao ASC
                """, (session_id,))
            
            result = cursor.fetchall()
            conn.close()
            
            return result
            
        except Exception as e:
            print(f"Error getting session conversations: {e}")
            return []
    
    def get_all_sessions(self, username, limit=30):
        """Get all sessions for a username"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.maPhien, s.thoiGianBatDau, s.thoiGianKetThuc
                FROM sessions s
                JOIN users u ON s.maNguoiDung = u.maNguoiDung
                WHERE u.tenNguoiDung = ?
                ORDER BY s.thoiGianBatDau DESC
                LIMIT ?
            """, (username, limit))
            
            result = cursor.fetchall()
            conn.close()
            
            return result
            
        except Exception as e:
            print(f"Error getting all sessions: {e}")
            return []
    
    def get_statistics(self, user_id):
        """Get statistics for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) as total_conversations,
                       COUNT(DISTINCT DATE(thoiGianTao)) as total_days,
                       COUNT(DISTINCT maPhien) as total_sessions
                FROM conversations 
                WHERE maNguoiDung = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result if result else (0, 0, 0)
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return (0, 0, 0)
    
    def get_daily_statistics(self, user_id, limit=30):
        """Get daily statistics for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DATE(thoiGianTao) as date,
                       COUNT(*) as conversation_count,
                       COUNT(DISTINCT maPhien) as session_count
                FROM conversations 
                WHERE maNguoiDung = ?
                GROUP BY DATE(thoiGianTao)
                ORDER BY date DESC
                LIMIT ?
            """, (user_id, limit))
            
            result = cursor.fetchall()
            conn.close()
            
            return result
            
        except Exception as e:
            print(f"Error getting daily statistics: {e}")
            return []
    
    def delete_old_conversations(self, days=30):
        """Delete conversations older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM conversations 
                WHERE thoiGianTao < datetime('now', '-{} days')
            """.format(days))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"Deleted {deleted_count} old conversations")
            
        except Exception as e:
            print(f"Error deleting old conversations: {e}")
    
    def get_display_name(self, user_id):
        """Lấy họ tên (tên hiển thị) của user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT hoTen FROM users WHERE maNguoiDung = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result and result[0] else None
        except Exception as e:
            print(f"Error getting display name: {e}")
            return None
    
    def update_display_name(self, user_id, display_name):
        """Cập nhật họ tên (tên hiển thị) cho user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET hoTen = ?, thoiGianCapNhat = CURRENT_TIMESTAMP
                WHERE maNguoiDung = ?
            """, (display_name, user_id))
            
            conn.commit()
            conn.close()
            print(f"Updated display name for user {user_id} to: {display_name}")
            return True
        except Exception as e:
            print(f"Error updating display name: {e}")
            return False
