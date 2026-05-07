#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pop Assistant - Health Tab
Tab Health Monitoring và App Usage Analytics (Per User)
"""

import os
import sqlite3
import re
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QGroupBox, QProgressBar, QTableWidget, QTableWidgetItem,
    QPushButton, QFrame, QHeaderView, QGridLayout, QMenu, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from admin.view.tabs.base_tab import BaseTab
from admin.view.styles import BUTTON_BLUE, TABLE_WIDGET


class HealthTab(BaseTab):
    """Tab Health Monitoring - Theo dõi sức khỏe từng user"""
    
    def __init__(self, parent=None, log_callback=None):
        super().__init__(parent, log_callback)
        self._users_loaded = False
        self._load_users()
        self.load_data()
    
    def setup_ui(self):
        # Check if widget already has layout
        if self.layout() is None:
            main_layout = QVBoxLayout(self)
        else:
            main_layout = self.layout()

        # ===== SCROLL AREA =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Container chứa toàn bộ UI
        container = QWidget()
        layout = QVBoxLayout(container)

        # === MODE SELECTOR ===
        mode_frame = QFrame()
        mode_layout = QHBoxLayout(mode_frame)
        
        self.system_btn = QPushButton(" System Health")
        self.system_btn.setCheckable(True)
        self.system_btn.setChecked(True)
        self.system_btn.clicked.connect(lambda: self.switch_mode('system'))
        
        self.user_btn = QPushButton("👤 User Analytics")
        self.user_btn.setCheckable(True)
        self.user_btn.clicked.connect(lambda: self.switch_mode('user'))
        
        mode_layout.addWidget(self.system_btn)
        mode_layout.addWidget(self.user_btn)
        mode_layout.addStretch()
        
        # === MODE 1: SYSTEM HEALTH ===
        self.system_frame = QGroupBox("🖥️System Health - Real-time Metrics")
        system_layout = QGridLayout(self.system_frame)

        self.cpu_label = QLabel("CPU: --%")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setMaximum(100)

        self.ram_label = QLabel("RAM: --%")
        self.ram_bar = QProgressBar()
        self.ram_bar.setMaximum(100)

        self.disk_label = QLabel("Disk: --%")
        self.disk_bar = QProgressBar()
        self.disk_bar.setMaximum(100)

        self.temp_label = QLabel("Nhiệt độ: --°C")
        self.temp_bar = QProgressBar()
        self.temp_bar.setMaximum(100)

        system_layout.addWidget(self.cpu_label, 0, 0)
        system_layout.addWidget(self.cpu_bar, 0, 1)
        system_layout.addWidget(self.ram_label, 1, 0)
        system_layout.addWidget(self.ram_bar, 1, 1)
        system_layout.addWidget(self.disk_label, 2, 0)
        system_layout.addWidget(self.disk_bar, 2, 1)
        system_layout.addWidget(self.temp_label, 3, 0)
        system_layout.addWidget(self.temp_bar, 3, 1)

        # === MODE 2: USER ANALYTICS ===
        self.user_frame = QGroupBox("� User Analytics")
        user_layout = QVBoxLayout(self.user_frame)
        
        # User selection
        user_select_frame = QFrame()
        user_select_layout = QHBoxLayout(user_select_frame)
        
        self.user_combo = QComboBox()
        self.user_combo.setMinimumWidth(250)
        self.user_combo.setMaxVisibleItems(10)
        self.user_combo.setEditable(False)
        self.user_combo.setEnabled(True)
        self.user_combo.currentIndexChanged.connect(self.on_user_changed)
        
        user_select_layout.addWidget(QLabel("Người dùng:"))
        user_select_layout.addWidget(self.user_combo, 1)
        user_select_layout.addStretch()
        
        # User metrics
        metrics_frame = QGroupBox("📊 User Metrics")
        metrics_layout = QGridLayout(metrics_frame)
        
        self.session_count_label = QLabel("Sessions: --")
        self.command_count_label = QLabel("Commands: --")
        self.conversation_count_label = QLabel("Conversations: --")
        self.active_time_label = QLabel("Active Time: --")
        
        metrics_layout.addWidget(QLabel("Sessions:"), 0, 0)
        metrics_layout.addWidget(self.session_count_label, 0, 1)
        metrics_layout.addWidget(QLabel("Commands:"), 1, 0)
        metrics_layout.addWidget(self.command_count_label, 1, 1)
        metrics_layout.addWidget(QLabel("Conversations:"), 2, 0)
        metrics_layout.addWidget(self.conversation_count_label, 2, 1)
        metrics_layout.addWidget(QLabel("Active Time:"), 3, 0)
        metrics_layout.addWidget(self.active_time_label, 3, 1)
        
        # App usage table
        apps_frame = QGroupBox("🖥️ App Usage")
        apps_layout = QVBoxLayout(apps_frame)
        
        self.apps_table = QTableWidget()
        self.apps_table.setMinimumHeight(250)
        self.apps_table.setColumnCount(4)
        self.apps_table.setHorizontalHeaderLabels(["Ứng dụng", "Số lần mở", "Thời gian (phút)", "Lần cuối"])
        self.apps_table.horizontalHeader().setStretchLastSection(True)
        self.apps_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        apps_layout.addWidget(self.apps_table)
        
        user_layout.addWidget(user_select_frame)
        user_layout.addWidget(metrics_frame)
        user_layout.addWidget(apps_frame)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Làm mới")
        refresh_btn.setStyleSheet(BUTTON_BLUE)
        refresh_btn.clicked.connect(self.load_data)
        
        # ===== ADD TO CONTAINER =====
        layout.addWidget(mode_frame)
        layout.addWidget(self.system_frame)
        layout.addWidget(self.user_frame)
        layout.addWidget(refresh_btn)
        layout.addStretch()
        
        # Initially hide user frame
        self.user_frame.hide()
        
        # Gắn container vào scroll
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
    
    def switch_mode(self, mode):
        """Switch between System Health and User Analytics modes"""
        if mode == 'system':
            self.system_btn.setChecked(True)
            self.user_btn.setChecked(False)
            self.system_frame.show()
            self.user_frame.hide()
            self.log("Switched to System Health mode")
            self.load_system_health()
        elif mode == 'user':
            self.system_btn.setChecked(False)
            self.user_btn.setChecked(True)
            self.system_frame.hide()
            self.user_frame.show()
            self.log("Switched to User Analytics mode")
            self.load_user_analytics()
    
    def load_data(self):
        """Load data based on current mode"""
        try:
            if self.system_frame.isVisible():
                self.load_system_health()
            else:
                self.load_user_analytics()
        except Exception as e:
            self.log(f"Error: {e}")
    
    def load_system_health(self):
        """Load real-time system health metrics (always system, not user-dependent)"""
        try:
            self._load_health_stats()
        except Exception as e:
            self.log(f"System health error: {e}")
    
    def load_user_analytics(self):
        """Load user analytics data"""
        try:
            # Get selected user
            if hasattr(self, 'user_combo'):
                user_id = self.user_combo.itemData(self.user_combo.currentIndex())
                username = self.user_combo.itemText(self.user_combo.currentIndex())
                clean_username = username.replace("👤 ", "").replace(" ", "")
                
                if user_id is not None:
                    self._load_user_metrics(user_id, clean_username)
                else:
                    self.log("Please select a user")
            else:
                self.log("User combo not available")
        except Exception as e:
            self.log(f"User analytics error: {e}")
    
    def _load_health_stats(self):
        """Load current health metrics - real-time from psutil if no DB data"""
        try:
            self.log("Loading health stats...")
            from model.usage_tracker import UsageTracker
            import psutil
            
            tracker = UsageTracker()
            
            # Try to get from DB first
            self.log("Trying to get health data from database...")
            health_data = tracker.get_latest_health()
            self.log(f"DB health data result: {health_data}")
            
            # If no DB data, get real-time from psutil
            if not health_data:
                self.log("No DB health data, using real-time psutil")
                
                # Try to get temperature from TemperatureMonitor
                temp = 0
                try:
                    from model.temperature_monitor import get_cpu_temperature_auto
                    temp_str = get_cpu_temperature_auto()
                    self.log(f"Temperature string: {temp_str}")
                    # Extract temperature number from string like "Nhiệt độ CPU: 45.5°C"
                    import re
                    temp_match = re.search(r'(\d+\.?\d*)', temp_str)
                    if temp_match:
                        temp = float(temp_match.group(1))
                        self.log(f"Got temperature: {temp}°C")
                    else:
                        self.log(f"Could not parse temperature from: {temp_str}")
                except Exception as e:
                    self.log(f"Temperature monitor error: {e}")
                    temp = 0
                
                health_data = {
                    'cpu_percent': psutil.cpu_percent(interval=0.5),
                    'ram_percent': psutil.virtual_memory().percent,
                    'disk_percent': self._get_c_drive_usage(),
                    'temperature': temp
                }
                self.log(f"Real-time health data: {health_data}")
            
            if health_data:
                cpu = health_data.get('cpu_percent', 0)
                ram = health_data.get('ram_percent', 0)
                disk = health_data.get('disk_percent', 0)
                temp = health_data.get('temperature', 0)
                
                self.log(f"Updating UI - CPU: {cpu}, RAM: {ram}, Disk: {disk}, Temp: {temp}")
                
                self.cpu_label.setText(f"CPU: {cpu:.1f}%")
                self.cpu_bar.setValue(int(cpu))
                self._set_bar_color(self.cpu_bar, cpu)
                
                self.ram_label.setText(f"RAM: {ram:.1f}%")
                self.ram_bar.setValue(int(ram))
                self._set_bar_color(self.ram_bar, ram)
                
                self.disk_label.setText(f"Disk: {disk:.1f}%")
                self.disk_bar.setValue(int(disk))
                self._set_bar_color(self.disk_bar, disk)
                
                self.temp_label.setText(f"Nhiệt độ: {temp:.1f}°C")
                self.temp_bar.setValue(int(min(temp, 100)))
                self._set_bar_color(self.temp_bar, temp, threshold=70)
                
                self.log("Health stats updated successfully")
            else:
                self.log("No health data available")
                
        except Exception as e:
            self.log(f"Health stats error: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_health_trends(self, username=None):
        """Load health trends for last 7 days"""
        try:
            from model.usage_tracker import UsageTracker
            tracker = UsageTracker()
            
            # Clean username by removing icons
            user_name = (username or "user").replace("👤 ", "").replace("📊 ", "")
            trends = tracker.get_health_trends(days=7, user_name=user_name)
            
            if trends:
                self.trends_labels['avg_cpu'].setText(f"{trends.get('avg_cpu', 0):.1f}%")
                self.trends_labels['avg_ram'].setText(f"{trends.get('avg_ram', 0):.1f}%")
                self.trends_labels['avg_disk'].setText(f"{trends.get('avg_disk', 0):.1f}%")
                self.trends_labels['max_cpu'].setText(f"{trends.get('max_cpu', 0):.1f}%")
                self.trends_labels['max_ram'].setText(f"{trends.get('max_ram', 0):.1f}%")
            else:
                for key in self.trends_labels:
                    self.trends_labels[key].setText("--%")
                    
        except Exception as e:
            self.log(f"Health trends error: {e}")
    
    def _set_bar_color(self, bar, value, threshold=80):
        """Set progress bar color based on value"""
        if value < threshold * 0.5:
            bar.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")  # Green
        elif value < threshold:
            bar.setStyleSheet("QProgressBar::chunk { background-color: #f39c12; }")  # Yellow
        else:
            bar.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")  # Red
    
    def _load_app_usage_stats(self, username=None):
        """Load app usage statistics"""
        try:
            from model.usage_tracker import UsageTracker
            tracker = UsageTracker()
            
            # Get top apps - filter by user if username provided
            if username:
                apps = tracker.get_top_apps(days=7, user_name=username, limit=10)
            else:
                apps = tracker.get_top_apps(days=7, limit=10)
            
            self.apps_table.setRowCount(len(apps))
            
            for row, app in enumerate(apps):
                app_name = QTableWidgetItem(app.get('app_name', 'Unknown'))
                open_count = QTableWidgetItem(str(app.get('open_count', 0)))
                total_time = QTableWidgetItem(f"{app.get('total_time', 0)} phút")
                last_opened = QTableWidgetItem(app.get('last_opened', 'Never'))
                
                self.apps_table.setItem(row, 0, app_name)
                self.apps_table.setItem(row, 1, open_count)
                self.apps_table.setItem(row, 2, total_time)
                self.apps_table.setItem(row, 3, last_opened)
                
        except Exception as e:
            self.log(f"App usage error: {e}")
    
    def _get_c_drive_usage(self) -> float:
        """Get C: drive usage percentage"""
        try:
            import psutil
            for part in psutil.disk_partitions():
                if part.mountpoint == 'C:\\' or part.device == 'C:\\':
                    return psutil.disk_usage(part.mountpoint).percent
            # Fallback: use first available drive
            for part in psutil.disk_partitions():
                if part.fstype:
                    try:
                        return psutil.disk_usage(part.mountpoint).percent
                    except:
                        continue
            return 0
        except Exception as e:
            print(f"[HealthTab] Error getting disk usage: {e}")
            return 0
    
    def _load_users(self):
        """Load users into dropdown"""
        # Prevent double loading
        if hasattr(self, '_users_loaded') and self._users_loaded:
            print("[HealthTab] Users already loaded, skipping")
            return
            
        try:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   '..', '..', '..', 'database', 'conversations.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT maNguoiDung, tenNguoiDung FROM users ORDER BY tenNguoiDung")
            users = cursor.fetchall()
            
            print(f"[HealthTab] Loaded {len(users)} users from DB")
            
            # Use QComboBox for user selection
            self.user_combo.blockSignals(True)
            
            self.user_combo.clear()
            self.user_combo.addItem("📊 Tổng quan hệ thống", None)

            for user_id, username in users:
                self.user_combo.addItem(f"👤 {username}", user_id)
                print(f"[HealthTab] Added user: {username} (id={user_id})")

            self.user_combo.blockSignals(False)
            
            # Combo updated
            print(f"[HealthTab] Combo updated with {self.user_combo.count()} items")
            self._users_loaded = True
            
            # Delay visibility fix to ensure UI is fully loaded
            QTimer.singleShot(100, self._fix_combo_visibility)
            
            conn.close()
            self.log(f"Đã tải {len(users)} người dùng")
        except Exception as e:
            self.log(f"Error loading users: {e}")
            import traceback
            traceback.print_exc()
    
    def on_user_changed(self, index):
        user_id = self.user_combo.itemData(index)
        name = self.user_combo.itemText(index)

        print(f"[HealthTab] Selected: {name} (id={user_id})")

        # Load user analytics when user changes
        if self.user_frame.isVisible():
            clean_username = name.replace("👤 ", "").replace(" ", "")
            self._load_user_metrics(user_id, clean_username)
    
    def _load_user_metrics(self, user_id: int, username: str):
        """Load user analytics metrics"""
        try:
            from model.usage_tracker import UsageTracker
            from admin.model.admin_model import AdminModel
            import sqlite3
            
            tracker = UsageTracker()
            admin_model = AdminModel()
            
            # Load app usage
            self._load_app_usage_stats(username=username)
            print(f"[HealthTab] Loaded app usage for {username}")
            
            # Load usage hours (active time)
            usage_hours = tracker.get_total_usage_hours(days=30, user_name=username)
            print(f"[HealthTab] Usage hours for {username}: {usage_hours}")
            if usage_hours > 1:
                hours = int(usage_hours)
                minutes = int((usage_hours - hours) * 60)
                self.active_time_label.setText(f"Active Time: {hours}h {minutes}m")
            else:
                minutes = int(usage_hours * 60)
                self.active_time_label.setText(f"Active Time: {minutes}m")
            
            # Load conversation count
            try:
                conv_count = admin_model.get_conversation_count_by_user(user_id)
                print(f"[HealthTab] Conversation count for {username}: {conv_count}")
                self.conversation_count_label.setText(f"Conversations: {conv_count}")
            except Exception as e:
                print(f"[HealthTab] Error loading conversations: {e}")
                self.conversation_count_label.setText("Conversations: --")
            
            # Load daily usage for session count approximation
            daily_usage = tracker.get_daily_usage(days=30, user_name=username)
            session_count = len(daily_usage) if daily_usage else 0
            print(f"[HealthTab] Daily usage count for {username}: {session_count}")
            self.session_count_label.setText(f"Sessions: {session_count}")
            
            # Load command count (placeholder - would need command logging)
            self.command_count_label.setText("Commands: --")
            
            print(f"[HealthTab] Final labels:")
            print(f"  Sessions: {self.session_count_label.text()}")
            print(f"  Commands: {self.command_count_label.text()}")
            print(f"  Conversations: {self.conversation_count_label.text()}")
            print(f"  Active Time: {self.active_time_label.text()}")
            
            self.log(f"Loaded analytics for {username}")
            
        except Exception as e:
            self.log(f"Error loading user metrics: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_user_health(self, user_id: int, username: str):
        """Load health stats for specific user"""
        try:
            from model.usage_tracker import UsageTracker
            tracker = UsageTracker()
            
            # Clean username by removing icons
            clean_username = username.replace("👤 ", "").replace(" ", "")
            
            # Debug: try different username variations
            print(f"[HealthTab] Looking for user: '{clean_username}'")
            health_data = tracker.get_latest_health(user_name=clean_username)
            
            if not health_data:
                # Try with 'user' as fallback
                print(f"[HealthTab] No data for '{clean_username}', trying 'user'")
                health_data = tracker.get_latest_health(user_name="user")
                
            if not health_data:
                # Try with None (system overview)
                print(f"[HealthTab] No data for 'user', trying None (system)")
                health_data = tracker.get_latest_health(user_name=None)
            
            if health_data:
                self.cpu_label.setText(f"CPU: {health_data.get('cpu_percent', 0):.1f}% ({username})")
                self.ram_label.setText(f"RAM: {health_data.get('ram_percent', 0):.1f}%")
                self.disk_label.setText(f"Disk: {health_data.get('disk_percent', 0):.1f}%")
                self.temp_label.setText(f"Nhiệt độ: {health_data.get('temperature', 0):.1f}°C")
                
                # Load trends for this user
                self._load_health_trends(username=username)
            else:
                # No data for this user
                self.cpu_label.setText(f"CPU: --% (Chưa có dữ liệu)")
                self.ram_label.setText("RAM: --%")
                self.disk_label.setText("Disk: --%")
                self.temp_label.setText("Nhiệt độ: --°C")
                self.log(f"Chưa có dữ liệu sức khỏe cho {username}")
                
                # Load trends for this user anyway
                self._load_health_trends(username=username)
                
        except Exception as e:
            self.log(f"Error loading user health: {e}")
    
    def _fix_combo_visibility(self):
        """Fix combo visibility after UI is fully loaded"""
        try:
            # Debug parent hierarchy
            print(f"[HealthTab] Combo parent: {self.user_combo.parent()}")
            print(f"[HealthTab] User frame parent: {getattr(self, 'user_frame', None)}")
            if hasattr(self, 'user_frame'):
                print(f"[HealthTab] User frame parent: {self.user_frame.parent()}")
            
            self.user_combo.setVisible(True)
            self.user_combo.show()
            self.user_combo.raise_()
            self.user_combo.update()
            self.user_combo.repaint()
            
            # Also try raising the user frame
            if hasattr(self, 'user_frame'):
                self.user_frame.raise_()
            
            print(f"[HealthTab] Combo visibility fix: enabled={self.user_combo.isEnabled()}, visible={self.user_combo.isVisible()}")
            
            # Try forcing combo to show with different methods
            self.user_combo.setMinimumSize(250, 30)
            self.user_combo.resize(250, 30)
            
        except Exception as e:
            print(f"[HealthTab] Error fixing visibility: {e}")
    
    
