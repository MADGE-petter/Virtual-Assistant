#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Habit Tracker - Học thói quen người dùng
Ghi nhớ: thường mở app nào, vào giờ nào, ngày nào trong tuần
"""

import sqlite3
import os
from datetime import datetime, timedelta
from collections import defaultdict


class HabitTracker:
    """Theo dõi và học thói quen người dùng"""
    
    DB_PATH = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'database', 'conversations.db'
    ))
    
    def __init__(self):
        self.init_habits_table()
    
    def init_habits_table(self):
        """Tạo bảng habits nếu chưa có"""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        # Bảng ghi lại mỗi lần mở app
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                maNguoiDung INTEGER,
                tenUngDung TEXT,
                thoiGianMo DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (maNguoiDung) REFERENCES users(maNguoiDung)
            )
        """)
        
        # Bảng thói quen đã học được
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                maNguoiDung INTEGER,
                loaiThoiQuen TEXT,  -- 'app_open', 'website_visit', v.v.
                tenMucTieu TEXT,  -- tên app/website
                gioTrongNgay INTEGER,  -- 0-23
                ngayTrongTuan INTEGER,  -- 0-6 (Mon-Sun)
                tanSuat INTEGER DEFAULT 1,  -- số lần xuất hiện
                doTinCay REAL DEFAULT 0.0,  -- độ tin cậy 0.0-1.0
                lanQuanSatCuoi DATETIME,
                thoiGianTao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (maNguoiDung) REFERENCES users(maNguoiDung)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_app_opened(self, maNguoiDung, tenUngDung):
        """Ghi lại mỗi lần mở app"""
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO app_usage_logs (maNguoiDung, tenUngDung, thoiGianMo)
                VALUES (?, ?, ?)
            """, (maNguoiDung, tenUngDung, datetime.now()))
            
            conn.commit()
            conn.close()
            
            # Cập nhật thói quen
            self._update_habit(maNguoiDung, 'app_open', tenUngDung)
        except Exception:
            pass
    
    def _update_habit(self, maNguoiDung, loaiThoiQuen, tenMucTieu):
        """Cập nhật thói quen dựa trên log mới"""
        now = datetime.now()
        gio = now.hour
        ngay = now.weekday()
        
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        # Kiểm tra xem thói quen này đã có chưa
        cursor.execute("""
            SELECT id, tanSuat FROM user_habits
            WHERE maNguoiDung = ? AND loaiThoiQuen = ? AND tenMucTieu = ?
            AND gioTrongNgay = ? AND ngayTrongTuan = ?
        """, (maNguoiDung, loaiThoiQuen, tenMucTieu, gio, ngay))
        
        result = cursor.fetchone()
        
        if result:
            # Cập nhật tần suất và độ tin cậy
            maThoiQuen, tanSuat = result
            tanSuatMoi = tanSuat + 1
            doTinCay = min(0.95, tanSuatMoi / 10.0)  # Max 0.95 sau 10 lần
            
            cursor.execute("""
                UPDATE user_habits 
                SET tanSuat = ?, doTinCay = ?, lanQuanSatCuoi = ?
                WHERE id = ?
            """, (tanSuatMoi, doTinCay, now, maThoiQuen))
        else:
            # Tạo thói quen mới
            cursor.execute("""
                INSERT INTO user_habits 
                (maNguoiDung, loaiThoiQuen, tenMucTieu, gioTrongNgay, ngayTrongTuan, lanQuanSatCuoi)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (maNguoiDung, loaiThoiQuen, tenMucTieu, gio, ngay, now))
        
        conn.commit()
        conn.close()
    
    def get_user_habits(self, maNguoiDung, doTinCayToiThieu=0.3):
        """Lấy thói quen của user với độ tin cậy tối thiểu"""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT loaiThoiQuen, tenMucTieu, gioTrongNgay, ngayTrongTuan, 
                   tanSuat, doTinCay
            FROM user_habits
            WHERE maNguoiDung = ? AND doTinCay >= ?
            ORDER BY doTinCay DESC, tanSuat DESC
        """, (maNguoiDung, doTinCayToiThieu))
        
        habits = cursor.fetchall()
        conn.close()
        
        return habits
    
    def suggest_based_on_habits(self, maNguoiDung):
        """Gợi ý dựa trên thói quen và thời gian hiện tại"""
        now = datetime.now()
        gioHienTai = now.hour
        ngayHienTai = now.weekday()
        
        # Lấy thói quen phù hợp với khung giờ hiện tại (±1 giờ)
        thoiQuens = self.get_user_habits(maNguoiDung, doTinCayToiThieu=0.5)
        
        goiYs = []
        for loaiThoiQuen, tenMucTieu, gio, ngay, tanSuat, doTinCay in thoiQuens:
            # Kiểm tra nếu đang đúng giờ (hoặc gần đúng giờ)
            if abs(gio - gioHienTai) <= 1 and ngay == ngayHienTai:
                goiYs.append({
                    'loai': loaiThoiQuen,
                    'mucTieu': tenMucTieu,
                    'gioThuong': f"{gio}:00",
                    'doTinCay': doTinCay,
                    'tinNhan': f"Thường mở {tenMucTieu} lúc {gio}:00 (độ tin cậy {doTinCay*100:.0f}%)"
                })
        
        return goiYs
    
    def get_habit_stats(self, maNguoiDung):
        """Thống kê thói quen user"""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        # Tổng số thói quen
        cursor.execute("""
            SELECT COUNT(DISTINCT tenMucTieu), AVG(doTinCay)
            FROM user_habits WHERE maNguoiDung = ?
        """, (maNguoiDung,))
        
        tongThoiQuen, doTinCayTB = cursor.fetchone()
        
        # Top apps
        cursor.execute("""
            SELECT tenMucTieu, COUNT(*) as tanSuat
            FROM user_habits 
            WHERE maNguoiDung = ? AND loaiThoiQuen = 'app_open'
            GROUP BY tenMucTieu
            ORDER BY tanSuat DESC
            LIMIT 5
        """, (maNguoiDung,))
        
        topApps = cursor.fetchall()
        conn.close()
        
        return {
            'tongThoiQuen': tongThoiQuen or 0,
            'doTinCayTrungBinh': doTinCayTB or 0,
            'topUngDung': topApps
        }


# Singleton instance
_habit_tracker = None

def get_habit_tracker():
    """Get or create habit tracker instance"""
    global _habit_tracker
    if _habit_tracker is None:
        _habit_tracker = HabitTracker()
    return _habit_tracker
