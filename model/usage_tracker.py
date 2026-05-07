"""Usage Tracker - Theo dõi thời gian sử dụng và ứng dụng"""
import os
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class UsageTracker:
    """Theo dõi thời gian sử dụng và ứng dụng được mở"""
    
    def __init__(self, db_path: str = None):
        # Dùng chung database conversations.db
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'conversations.db')
        self.db_path = db_path
        self._init_db()
        self.session_start = None
        self.current_session_id = None
    
    def _init_db(self):
        """Khởi tạo database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Bảng thời gian sử dụng
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                start_time TEXT,
                end_time TEXT,
                duration_seconds INTEGER,
                tenNguoiDung TEXT
            )
        ''')
        
        # Bảng ứng dụng được mở (legacy)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                timestamp TEXT,
                app_name TEXT,
                action TEXT,
                tenNguoiDung TEXT
            )
        ''')
        
        # Bảng app usage logs (cho habit tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                maNguoiDung INTEGER DEFAULT 1,
                tenUngDung TEXT,
                thoiGianMo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ngay TEXT
            )
        ''')
        
        # Bảng health snapshots
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                timestamp TEXT,
                cpu_percent REAL,
                ram_percent REAL,
                disk_percent REAL,
                temperature REAL,
                tenNguoiDung TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_session(self, user_name: str = "user"):
        """Bắt đầu phiên sử dụng mới"""
        self.session_start = datetime.now()
        self.current_session_id = None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usage_sessions (date, start_time, tenNguoiDung)
            VALUES (?, ?, ?)
        ''', (
            self.session_start.strftime('%Y-%m-%d'),
            self.session_start.strftime('%H:%M:%S'),
            user_name
        ))
        self.current_session_id = cursor.lastrowid
        conn.commit()
        conn.close()
    
    def end_session(self, user_name: str = "user"):
        """Kết thúc phiên sử dụng"""
        if self.session_start is None:
            return
        
        end_time = datetime.now()
        duration = (end_time - self.session_start).total_seconds()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE usage_sessions 
            SET end_time = ?, duration_seconds = ?
            WHERE id = ?
        ''', (
            end_time.strftime('%H:%M:%S'),
            int(duration),
            self.current_session_id
        ))
        conn.commit()
        conn.close()
        
        self.session_start = None
        self.current_session_id = None
    
    def log_app_opened(self, app_name: str, user_name: str = "user"):
        """Ghi log ứng dụng được mở"""
        now = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO app_usage (date, timestamp, app_name, action, tenNguoiDung)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            now.strftime('%Y-%m-%d'),
            now.strftime('%H:%M:%S'),
            app_name,
            'opened',
            user_name
        ))
        conn.commit()
        conn.close()
    
    def log_health_snapshot(self, cpu: float, ram: float, disk: float, 
                           temp: Optional[float], user_name: str = "user"):
        """Ghi log health snapshot"""
        now = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO health_snapshots (date, timestamp, cpu_percent, 
                ram_percent, disk_percent, temperature, tenNguoiDung)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            now.strftime('%Y-%m-%d'),
            now.strftime('%H:%M:%S'),
            cpu,
            ram,
            disk,
            temp,
            user_name
        ))
        conn.commit()
        conn.close()
    
    def get_daily_usage(self, days: int = 7, user_name: str = "user") -> List[Dict]:
        """Lấy thống kê sử dụng theo ngày"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT date, SUM(duration_seconds) as total_seconds,
                   COUNT(*) as session_count
            FROM usage_sessions
            WHERE date >= ? AND tenNguoiDung = ?
            GROUP BY date
            ORDER BY date DESC
        ''', (start_date, user_name))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'date': row[0],
                'hours': round(row[1] / 3600, 2) if row[1] else 0,
                'sessions': row[2]
            }
            for row in results
        ]
    
    def get_top_apps(self, days: int = 7, user_name: str = "user", limit: int = 10) -> List[Tuple[str, int]]:
        """Lấy top ứng dụng được mở nhiều nhất"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT app_name, COUNT(*) as count
            FROM app_usage
            WHERE date >= ? AND tenNguoiDung = ?
            GROUP BY app_name
            ORDER BY count DESC
            LIMIT ?
        ''', (start_date, user_name, limit))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_health_trends(self, days: int = 7, user_name: str = "user") -> Dict:
        """Lấy xu hướng health metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT AVG(cpu_percent), AVG(ram_percent), AVG(disk_percent), AVG(temperature),
                   MAX(cpu_percent), MAX(ram_percent), MAX(disk_percent), MAX(temperature), COUNT(*)
            FROM health_snapshots
            WHERE date >= ? AND tenNguoiDung = ?
        ''', (start_date, user_name))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[8] > 0:  # COUNT(*) > 0
            return {
                'avg_cpu': row[0] or 0,
                'avg_ram': row[1] or 0,
                'avg_disk': row[2] or 0,
                'avg_temp': row[3] if row[3] and row[3] > 0 else None,  # Handle NULL and 0 values
                'max_cpu': row[4] or 0,
                'max_ram': row[5] or 0,
                'max_disk': row[6] or 0,
                'max_temp': row[7] if row[7] and row[7] > 0 else None
            }
        return {}
    
    def get_latest_health(self, user_name: str = "user") -> Dict:
        """Lấy health metrics mới nhất"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cpu_percent, ram_percent, disk_percent, temperature, timestamp
            FROM health_snapshots
            WHERE tenNguoiDung = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (user_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'cpu_percent': row[0] or 0,
                'ram_percent': row[1] or 0,
                'disk_percent': row[2] or 0,
                'temperature': row[3] or 0,
                'timestamp': row[4]
            }
        return {}
    
    def get_top_apps(self, days: int = 7, start_date=None, end_date=None, user_name: str = "user", limit: int = 10):
        """Lấy top ứng dụng được mở nhiều nhất"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Default to last 7 days if no dates provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Convert datetime to string if needed
        if isinstance(start_date, datetime):
            start_date = start_date.strftime('%Y-%m-%d')
        if isinstance(end_date, datetime):
            end_date = end_date.strftime('%Y-%m-%d')
        
        try:
            cursor.execute('''
                SELECT tenUngDung, COUNT(*) as soLanMo, MAX(thoiGianMo) as lanMoCuoi
                FROM app_usage_logs
                WHERE date(thoiGianMo) BETWEEN ? AND ?
                GROUP BY tenUngDung
                ORDER BY soLanMo DESC
                LIMIT ?
            ''', (start_date, end_date, limit))
            
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"[UsageTracker] get_top_apps error: {e}")
            conn.close()
            return []
    
    def get_total_usage_hours(self, days: int = 30, user_name: str = "user") -> float:
        """Lấy tổng số giờ sử dụng"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT SUM(duration_seconds)
            FROM usage_sessions
            WHERE date >= ? AND tenNguoiDung = ?
        ''', (start_date, user_name))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return round(result[0] / 3600, 2)
        return 0.0
    
    def get_weekly_report(self, user_name: str = "user") -> Dict:
        """Tạo báo cáo tuần"""
        # Tuần này
        this_week = self.get_daily_usage(days=7, user_name=user_name)
        total_hours = sum(d['hours'] for d in this_week)
        total_sessions = sum(d['sessions'] for d in this_week)
        
        # Top apps
        top_apps = self.get_top_apps(days=7, user_name=user_name, limit=5)
        
        # Health trends
        health = self.get_health_trends(days=7, user_name=user_name)
        
        # Gợi ý tối ưu
        suggestions = []
        if health.get('avg_ram', 0) > 80:
            suggestions.append("RAM trung bình cao ({}%). Hãy đóng các ứng dụng không cần thiết.".format(health['avg_ram']))
        if health.get('avg_cpu', 0) > 70:
            suggestions.append("CPU thường xuyên cao ({}%). Kiểm tra các process nặng.".format(health['avg_cpu']))
        if health.get('avg_temp', 0) and health['avg_temp'] > 75:
            suggestions.append("Nhiệt độ trung bình cao ({}°C). Kiểm tra quạt tản nhiệt.".format(health['avg_temp']))
        if total_hours > 40:
            suggestions.append("Bạn dùng máy {} giờ/tuần. Hãy nghỉ ngơi đúng giờ!".format(total_hours))
        
        return {
            'total_hours': total_hours,
            'total_sessions': total_sessions,
            'daily_breakdown': this_week,
            'top_apps': top_apps,
            'health': health,
            'suggestions': suggestions
        }


# Singleton instance
_tracker = UsageTracker()

def get_tracker() -> UsageTracker:
    """Get singleton usage tracker instance"""
    return _tracker
