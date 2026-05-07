"""
Alert Manager - Orchestrator chính
"""

import threading
import time
from typing import Callable, Optional, List

from .types import Alert, AlertLevel, AlertThreshold
from .notifier import AlertNotifier
from .checker import CPUMonitor, RAMMonitor, DiskMonitor, TempMonitor, BatteryMonitor


class AlertManager:
    """Quản lý và điều phối hệ thống cảnh báo"""
    
    # Ngưỡng mặc định
    DEFAULT_THRESHOLDS = {
        'cpu': AlertThreshold('cpu', warning=80.0, critical=95.0),
        'ram': AlertThreshold('ram', warning=85.0, critical=95.0),
        'disk': AlertThreshold('disk', warning=85.0, critical=90.0, danger=95.0),
        'battery': AlertThreshold('battery', warning=20.0, critical=10.0),
        'temperature': AlertThreshold('temperature', warning=70.0, critical=80.0, danger=90.0)
    }
    
    WELLNESS_SETTINGS = {
        'night_start_hour': 23,
        'night_end_hour': 2,
        'rest_suggestions': [
            "Bạn đã làm việc khuya rồi đấy. Nên nghỉ ngơi để giữ sức khỏe nhé!",
            "Khuya rồi! Hãy để mắt và cơ thể nghỉ ngơi nhé.",
            "Bạn có thấy mệt không? Nên ngủ sớm để mai còn làm việc.",
        ]
    }
    
    def __init__(self, audio_service=None, ui_callback: Optional[Callable] = None, 
                 check_interval: int = 60, user_name: str = "bạn"):
        self.audio_service = audio_service
        self.ui_callback = ui_callback
        self.user_name = user_name
        
        # Cấu hình
        self.thresholds = dict(self.DEFAULT_THRESHOLDS)
        self.check_interval = check_interval
        self._wellness_enabled = True
        self._is_sleeping = False
        
        # Trạng thái
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._alerts: List[Alert] = []
        self._last_alert_time: dict = {}
        self._last_wellness_alert: Optional[float] = None
        
        # Khởi tạo notifier và monitors
        self.notifier = AlertNotifier(audio_service, ui_callback)
        self.monitors = [
            CPUMonitor(self.thresholds['cpu']),
            RAMMonitor(self.thresholds['ram']),
            DiskMonitor(self.thresholds['disk']),
            TempMonitor(self.thresholds['temperature']),
            BatteryMonitor(self.thresholds['battery'])
        ]
    
    def start_monitoring(self):
        """Bắt đầu giám sát"""
        if self._running:
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """Dừng giám sát"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Vòng lặp giám sát chính"""
        while self._running:
            try:
                # Kiểm tra từng monitor
                for monitor in self.monitors:
                    alert, is_recovery = monitor.check()
                    
                    if alert and self._should_alert(alert.metric):
                        self._alerts.append(alert)
                        self._last_alert_time[alert.metric] = time.time()
                        self.notifier.notify(alert)
                    
                    elif is_recovery:
                        metric = monitor.threshold.metric
                        # Lấy giá trị hiện tại cho message
                        from datetime import datetime
                        self.notifier.speak_recovery(metric, f"{metric.upper()} đã trở lại bình thường")
                
                # Kiểm tra wellness
                self._check_wellness()
                
                time.sleep(self.check_interval)
                
            except Exception:
                time.sleep(self.check_interval)
    
    def _should_alert(self, metric: str) -> bool:
        """Kiểm tra cooldown 5 phút giữa các cảnh báo cùng loại"""
        if metric not in self._last_alert_time:
            return True
        return time.time() - self._last_alert_time[metric] > 300
    
    def _check_wellness(self):
        """Nhắc nghỉ ngơi khi khuya"""
        if not self._wellness_enabled or self._is_sleeping:
            return
            
        from datetime import datetime
        current_hour = datetime.now().hour
        settings = self.WELLNESS_SETTINGS
        
        if settings['night_start_hour'] <= current_hour or current_hour < settings['night_end_hour']:
            # Kiểm tra đã nhắc trong 30 phút chưa
            if self._last_wellness_alert:
                if time.time() - self._last_wellness_alert < 1800:
                    return
            
            import random
            msg = random.choice(settings['rest_suggestions'])
            self._last_wellness_alert = time.time()
            
            if self.audio_service:
                try:
                    self.audio_service.speak(msg)
                except:
                    pass
    
    # Public API
    def set_sleep_mode(self, enabled: bool):
        self._is_sleeping = enabled
    
    def reset_wellness_timers(self):
        pass
    
    def enable_wellness(self, enabled: bool = True):
        self._wellness_enabled = enabled
    
    def get_active_alerts(self) -> List[Alert]:
        return [a for a in self._alerts if not a.acknowledged]
    
    def acknowledge_alert(self, alert_id: str):
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                break
    
    def get_system_status(self) -> dict:
        import psutil
        try:
            battery = psutil.sensors_battery()
            battery_info = {
                'percent': battery.percent if battery else None,
                'plugged': battery.power_plugged if battery else None
            }
        except:
            battery_info = {'percent': None, 'plugged': None}
        
        return {
            'cpu': psutil.cpu_percent(interval=0.5),
            'ram': psutil.virtual_memory().percent,
            'disk': {p.mountpoint: psutil.disk_usage(p.mountpoint).percent 
                    for p in psutil.disk_partitions(all=False) 
                    if psutil.disk_usage(p.mountpoint)},
            'battery': battery_info,
            'active_alerts': len(self.get_active_alerts())
        }
    
    def clear_all_alerts(self):
        self._alerts.clear()
        self._last_alert_time.clear()


# Singleton
_alert_manager: Optional[AlertManager] = None

def get_alert_manager(audio_service=None, ui_callback=None) -> AlertManager:
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager(audio_service, ui_callback)
    return _alert_manager
