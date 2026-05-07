"""
Alert Notifier - Xử lý thông báo cảnh báo
"""

from datetime import datetime, timedelta
from typing import Callable, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Alert


class AlertNotifier:
    """Xử lý phát âm thanh và hiển thị cảnh báo"""
    
    def __init__(self, audio_service=None, ui_callback: Optional[Callable] = None):
        self.audio_service = audio_service
        self.ui_callback = ui_callback
        self._recovery_cooldown: Dict[str, datetime] = {}
    
    def speak_alert(self, alert: 'Alert'):
        """Phát âm thanh cảnh báo"""
        if not self.audio_service:
            return
            
        try:
            prefix = ""
            if alert.level.value == "danger":
                prefix = "Cảnh báo nguy hiểm! "
            elif alert.level.value == "critical":
                prefix = "Cảnh báo! "
            elif alert.level.value == "warning":
                prefix = "Lưu ý: "
            
            self.audio_service.speak(prefix + alert.message)
        except Exception:
            pass
    
    def speak_recovery(self, metric: str, message: str):
        """Thông báo khi hệ thống phục hồi"""
        # Kiểm tra cooldown (5 phút)
        now = datetime.now()
        if metric in self._recovery_cooldown:
            if now - self._recovery_cooldown[metric] < timedelta(minutes=5):
                return
        
        self._recovery_cooldown[metric] = now
        
        if self.audio_service:
            try:
                self.audio_service.speak(f"✓ {message}")
            except Exception:
                pass
    
    def show_ui(self, alert: 'Alert'):
        """Hiển thị cảnh báo lên UI"""
        if self.ui_callback:
            try:
                self.ui_callback(alert)
            except Exception:
                pass
    
    def notify(self, alert: 'Alert'):
        """Thông báo đầy đủ (voice + UI)"""
        self.speak_alert(alert)
        self.show_ui(alert)
