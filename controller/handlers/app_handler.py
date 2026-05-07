"""App Handler - Xử lý mở website và ứng dụng."""

import webbrowser
import os
import subprocess
from datetime import datetime
from service.intern import extract_domain, extract_app_name
from service.app_scanner import AppScanner


def log_app_opened(app_name: str, user_id: int = 1):
    """Log ứng dụng được mở qua analytics service và habit tracker"""
    try:
        from service.analytics_service import get_analytics_service
        analytics = get_analytics_service()
        analytics.log_app_opened(app_name)
    except Exception as e:
        print(f"[AppHandler] Analytics log error: {e}")
    
    # Log cho habit tracker (học thói quen)
    try:
        from database.habit_tracker import get_habit_tracker
        habit_tracker = get_habit_tracker()
        habit_tracker.log_app_opened(user_id, app_name)
        print(f"[HabitTracker] Logged: {app_name} at {datetime.now().strftime('%H:%M')}")
    except Exception as e:
        print(f"[AppHandler] Habit tracker error: {e}")


class AppHandler:
    """Handler for opening websites and applications."""
    
    def __init__(self, audio_service=None, view=None):
        self.audio_service = audio_service
        self.view = view
        self.app_scanner = AppScanner()
    
    def set_audio_service(self, audio_service):
        self.audio_service = audio_service
    
    def set_view(self, view):
        self.view = view
    
    def set_user_name(self, name):
        pass
    
    def handle_website(self, text):
        """Xử lý mở website."""
        domain = extract_domain(text)
        
        if domain:
            webbrowser.open(domain)
            return f"Tôi đã mở trang web cho bạn."
        else:
            return "Tôi không thể xác định trang web bạn muốn mở."
    
    def handle_app(self, text):
        """Xử lý mở ứng dụng bằng cách tìm trong danh sách đã cài."""
        try:
            # Trích xuất tên app từ text
            app_name = extract_app_name(text)
            
            if not app_name:
                return "Tôi không hiểu bạn muốn mở ứng dụng nào."
            
            print(f"[AppHandler] Looking for app: '{app_name}'")
            
            # Tìm app trong danh sách đã cài
            found_name, found_path = self.app_scanner.find_app(app_name)
            
            if found_path:
                print(f"[AppHandler] Found: '{found_name}' at '{found_path}'")
                
                # Mở app
                if found_path.endswith('.lnk'):
                    os.startfile(found_path)
                elif os.path.isdir(found_path):
                    # Tìm exe trong thư mục
                    for item in os.listdir(found_path):
                        if item.endswith('.exe'):
                            exe_path = os.path.join(found_path, item)
                            subprocess.Popen([exe_path], shell=True)
                            break
                else:
                    subprocess.Popen([found_path], shell=True)
                
                # Log app mở
                log_app_opened(found_name)
                
                return f"Tôi đã mở {found_name}."
            else:
                # Thử dùng Windows Search/Run
                try:
                    subprocess.Popen(["start", "", app_name], shell=True)
                    return f"Tôi đang thử mở {app_name}."
                except:
                    return f"Tôi không tìm thấy ứng dụng '{app_name}' trên máy của bạn."
            
        except Exception as e:
            print(f"[AppHandler Error] {e}")
            return f"Lỗi khi mở ứng dụng: {str(e)}"
