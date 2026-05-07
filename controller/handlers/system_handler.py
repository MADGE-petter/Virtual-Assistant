"""System Handler - Xử lý điều khiển hệ thống (âm lượng, độ sáng, nguồn, monitoring, network)."""

import re
import time
import psutil
from controller.handlers.base_handler import BaseHandler
from model.pop_system_utils import get_temperature_alert
from model.temperature_monitor import get_cpu_temperature_auto


class SystemHandler(BaseHandler):
    """Handler for system control queries."""
    
    def handle(self, text):
        """Xử lý điều khiển hệ thống."""
        try:
            from model.pop_system_utils import (
                set_system_volume, get_system_volume,
                shutdown, restart, lock,
                get_cpu_usage, get_ram_usage, get_disk_usage,
                set_brightness, get_brightness,
                wifi_on, wifi_off
            )
            
            text_lower = text.lower()
            
            # Volume control with set/adjust/increase/decrease
            if "âm lượng" in text_lower:
                # Xử lý tăng/giảm trước
                if any(k in text_lower for k in ["tăng", "to hơn", "lớn hơn"]):
                    try:
                        current = self._extract_number(get_system_volume(), 50)
                        new_val = min(100, current + 20)
                        return set_system_volume(new_val)
                    except:
                        return set_system_volume(70)
                
                if any(k in text_lower for k in ["giảm", "nhỏ hơn", "bé hơn", "nhỏ lại"]):
                    try:
                        current = self._extract_number(get_system_volume(), 50)
                        new_val = max(0, current - 20)
                        return set_system_volume(new_val)
                    except:
                        return set_system_volume(30)
                
                # Đặt/chỉnh giá trị cụ thể
                return self._handle_numeric_control(
                    text_lower, text, set_system_volume, get_system_volume, "âm lượng"
                )
            
            if any(k in text_lower for k in ["độ sáng", "tăng sáng", "giảm sáng", "sáng hơn", "tối hơn"]):
                return self._handle_brightness(text_lower, text, set_brightness, get_brightness)
            
            # Power control
            if "tắt máy" in text_lower:
                return "Cảnh báo! Máy tính sẽ tắt sau 5 giây. Hủy lệnh? (Nói 'hủy' để ngừng)"
            if "khởi động lại" in text_lower:
                return "Cảnh báo! Máy tính sẽ khởi động lại sau 5 giây. Hủy lệnh? (Nói 'hủy' để ngừng)"
            if "khóa máy" in text_lower or "khóa màn hình" in text_lower:
                return lock()
            
            # System monitoring
            for keyword, getter in [("cpu", get_cpu_usage), ("ram", get_ram_usage), ("ổ đĩa", get_disk_usage), ("disk", get_disk_usage)]:
                if keyword in text_lower:
                    return self.speak_and_return(getter(), wait=2)
            
            # Full system status query
            if any(k in text_lower for k in ["trạng thái hệ thống", "tổng quan", "system status", "hiện trạng máy", "tình trạng máy", "tình trạng hệ thống", "hệ thống"]):
                return self._get_full_system_status()
            
            # Temperature check
            if any(k in text_lower for k in ["nhiệt độ", "temperature", "nóng", "máy nóng", "nhiệt độ máy", "kiểm tra nhiệt độ"]):
                return self._handle_temperature()
            
            # Toggle controls (wifi/bluetooth)
            if "wifi" in text_lower:
                return self._handle_toggle(text_lower, wifi_on, wifi_off, "WiFi")
            
            if "bluetooth" in text_lower:
                return self._handle_toggle(text_lower, lambda: "Đã bật Bluetooth", lambda: "Đã tắt Bluetooth", "Bluetooth")
            
            return "Tôi không hiểu lệnh điều khiển hệ thống."
            
        except ImportError:
            return "Thư viện pop_system_utils không khả dụng."
        except Exception as e:
            return f"Lỗi khi điều khiển hệ thống: {e}"
    
    @staticmethod
    def _extract_number(text, default=None):
        """Trích xuất số từ text."""
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else default
    
    def _handle_numeric_control(self, text_lower, text, setter, getter, name):
        """Xử lý điều khiển số (âm lượng/độ sáng)."""
        if "đặt" in text_lower or "chỉnh" in text_lower:
            value = self._extract_number(text)
            if value is None:
                return f"Vui lòng nói rõ mức {name} (ví dụ: đặt {name} 50)."
            if 0 <= value <= 100:
                return setter(value)
            return f"{name.capitalize()} phải từ 0 đến 100."
        return self.speak_and_return(getter(), wait=2)
    
    def _handle_brightness(self, text_lower, text, setter, getter):
        """Xử lý điều khiển độ sáng với tăng/giảm."""
        if "tăng sáng" in text_lower or "sáng hơn" in text_lower:
            try:
                current_num = self._extract_number(getter(), 50)
                return setter(min(100, current_num + 20))
            except:
                return setter(80)
        
        if "giảm sáng" in text_lower or "tối hơn" in text_lower:
            try:
                current_num = self._extract_number(getter(), 50)
                return setter(max(0, current_num - 20))
            except:
                return setter(30)
        
        return self._handle_numeric_control(text_lower, text, setter, getter, "độ sáng")
    
    def _handle_toggle(self, text_lower, on_func, off_func, name):
        """Xử lý bật/tắt (wifi, bluetooth)."""
        if "bật" in text_lower:
            return on_func()
        if "tắt" in text_lower:
            return off_func()
        return f"{name} status"
    
    def _handle_temperature(self):
        """Xử lý truy vấn nhiệt độ - tự động khởi động OHM nếu cần."""
        try:
            # Dùng get_cpu_temperature_auto - tự động khởi động OHM nếu chưa chạy
            temp_result = get_cpu_temperature_auto()
            
            # Parse xem có đọc được không
            match = re.search(r'(\d+\.?\d*)°C', temp_result)
            if match:
                temp = float(match.group(1))
                if temp >= 75:
                    return self.speak_and_return(f"Nhiệt độ đang cao: {temp:.0f} độ C. Bạn nên kiểm tra quạt tản nhiệt.", wait=3)
                else:
                    return self.speak_and_return(f"Nhiệt độ hiện tại là {temp:.0f} độ C. Máy đang hoạt động bình thường.", wait=3)
            else:
                # Không đọc được - thông báo rõ ràng và hướng dẫn
                message = "Xin lỗi, tôi không đọc được nhiệt độ máy. Để đọc được nhiệt độ, bạn cần cài đặt OpenHardwareMonitor trong thư mục tools của bot."
                return self.speak_and_return(message, wait=6)
        except Exception as e:
            print(f"[ERROR] Temperature check failed: {e}")
            return self.speak_and_return("Xin lỗi, tôi không đọc được nhiệt độ máy lúc này.", wait=3)
    
    def _get_full_system_status(self):
        """Lấy tổng trạng thái hệ thống đầy đủ."""
        try:
            # CPU
            cpu = psutil.cpu_percent(interval=0.5)
            # RAM
            ram = psutil.virtual_memory()
            # Disk
            disk_info = []
            for p in psutil.disk_partitions(all=False):
                try:
                    d = psutil.disk_usage(p.mountpoint)
                    disk_info.append(f"{p.mountpoint} {d.percent:.0f}%")
                except:
                    continue
            # Battery
            battery = psutil.sensors_battery()
            
            # Temperature - dùng auto (tự động khởi động OHM nếu cần)
            temp_msg = ""
            max_temp = 0
            try:
                temp_result = get_cpu_temperature_auto()
                print(f"[DEBUG] Temperature raw result: {temp_result}")
                # Parse nhiệt độ từ kết quả
                match = re.search(r'(\d+\.?\d*)°C', temp_result)
                if match:
                    max_temp = float(match.group(1))
                    temp_msg = f". Nhiệt độ {max_temp:.0f}°C"
                    print(f"[DEBUG] Parsed temperature: {max_temp}°C")
                else:
                    print(f"[DEBUG] No temperature match in: {temp_result}")
            except Exception as e:
                print(f"[DEBUG] Temperature error: {e}")
            
            # Build message
            msg = f"CPU {cpu:.0f}%, RAM {ram.percent:.0f}%"
            if disk_info:
                msg += f". Ổ đĩa: {', '.join(disk_info[:2])}"
            if battery:
                msg += f". Pin {battery.percent:.0f}%"
                if battery.power_plugged:
                    msg += " (đang sạc)"
            msg += temp_msg
            
            # Add warnings
            warnings = []
            if cpu > 80:
                warnings.append("CPU đang cao")
            if ram.percent > 85:
                warnings.append("RAM gần đầy")
            if battery and not battery.power_plugged and battery.percent < 20:
                warnings.append("Pin yếu cần sạc")
            if max_temp and max_temp >= 75:
                warnings.append(f"Nhiệt độ cao {max_temp:.0f}°C")
                
            if warnings:
                msg += f". Cảnh báo: {', '.join(warnings)}"
            else:
                msg += ". Hệ thống ổn định"
                
            return self.speak_and_return(msg, wait=3)
            
        except Exception as e:
            return f"Không thể đọc trạng thái hệ thống: {e}"
