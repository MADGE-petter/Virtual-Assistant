import os
import subprocess
import psutil

# ===============================
# ÂM LƯỢNG HỆ THỐNG
# ===============================

def _get_volume_interface():
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    devices = AudioUtilities.GetSpeakers()

    interface = devices.Activate(
        IAudioEndpointVolume._iid_,
        CLSCTX_ALL,
        None
    )

    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume


def get_system_volume():
    try:
        volume = _get_volume_interface()
        level = int(volume.GetMasterVolumeLevelScalar() * 100)
        return f"Âm lượng hiện tại {level}%"
    except Exception as e:
        return f"Lỗi lấy âm lượng: {e}"


def set_system_volume(value):
    try:
        volume = _get_volume_interface()

        value = max(0, min(value, 100))
        volume.SetMasterVolumeLevelScalar(value / 100, None)

        return f"Đã đặt âm lượng {value}%"
    except Exception as e:
        return f"Lỗi âm lượng: {e}"


def volume_up(step=10):
    try:
        volume = _get_volume_interface()

        current = volume.GetMasterVolumeLevelScalar()
        new = min(current + step / 100, 1)

        volume.SetMasterVolumeLevelScalar(new, None)

        return "Đã tăng âm lượng"
    except Exception as e:
        return f"Lỗi: {e}"


def volume_down(step=10):
    try:
        volume = _get_volume_interface()

        current = volume.GetMasterVolumeLevelScalar()
        new = max(current - step / 100, 0)

        volume.SetMasterVolumeLevelScalar(new, None)

        return "Đã giảm âm lượng"
    except Exception as e:
        return f"Lỗi: {e}"


# ===============================
# CPU / RAM / DISK
# ===============================

def get_cpu_usage():
    cpu = psutil.cpu_percent(interval=1)
    return f"CPU đang sử dụng {cpu}%"


def get_ram_usage():
    ram = psutil.virtual_memory()
    return f"RAM sử dụng {ram.percent}%"


def get_disk_usage(path="C:\\"):
    disk = psutil.disk_usage(path)
    return f"Ổ đĩa {path} sử dụng {disk.percent}%"


# ===============================
# PIN
# ===============================

def get_battery():
    try:
        battery = psutil.sensors_battery()

        if battery is None:
            return "Máy không có pin"

        percent = battery.percent
        plugged = battery.power_plugged

        if plugged:
            status = "Đang sạc"
        else:
            status = "Đang dùng pin"

        return f"Pin {percent}% - {status}"

    except:
        return "Không đọc được pin"


# ===============================
# NHIỆT ĐỘ
# ===============================

def get_cpu_temperature():
    """Lấy nhiệt độ CPU - thử nhiều phương pháp"""
    methods_tried = []
    
    try:
        # 1. Thử psutil sensors_temperatures (Linux, một số Windows)
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current:
                        return f"Nhiệt độ {name}: {entry.current:.1f}°C"
        methods_tried.append("psutil sensors")
    except Exception as e:
        methods_tried.append(f"psutil: {e}")
    
    try:
        # 2. Thử WMI trên Windows - phương pháp phổ biến nhất
        import wmi
        w = wmi.WMI(namespace="root\\wmi")
        temperature_info = w.MSAcpi_ThermalZoneTemperature()
        if temperature_info:
            # Đơn vị là 1/10 Kelvin, chuyển sang Celsius
            temp_kelvin = temperature_info[0].CurrentTemperature / 10.0
            temp_celsius = temp_kelvin - 273.15
            return f"Nhiệt độ hệ thống: {temp_celsius:.1f}°C (WMI)"
        methods_tried.append("WMI: No data")
    except Exception as e:
        methods_tried.append(f"WMI: {e}")
    
    try:
        # 3. Thử WMI qua Win32_PerfFormattedData (một số máy có)
        import wmi
        w = wmi.WMI()
        # Thử đọc từ WMI khác
        try:
            temps = w.Win32_TemperatureProbe()
            if temps:
                for temp in temps:
                    if temp.CurrentReading:
                        return f"Nhiệt độ: {temp.CurrentReading}°C (TemperatureProbe)"
        except:
            pass
        methods_tried.append("WMI TemperatureProbe: No data")
    except:
        methods_tried.append("WMI Win32: failed")
    
    try:
        # 4. Thử đọc từ LibreHardwareMonitor (LHM)
        import wmi
        try:
            w = wmi.WMI(namespace="root\\LibreHardwareMonitor")
            sensors = w.Sensor()
            for sensor in sensors:
                if "Temperature" in str(sensor.SensorType) and "CPU" in str(sensor.Name):
                    return f"Nhiệt độ {sensor.Name}: {sensor.Value:.1f}°C (LHM)"
        except:
            pass
        methods_tried.append("LibreHardwareMonitor: Not running")
    except:
        pass
    
    try:
        # 5. Thử đọc từ OpenHardwareMonitor (OHM) - namespace khác
        import wmi
        try:
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            sensors = w.Sensor()
            for sensor in sensors:
                if "Temperature" in str(sensor.SensorType) and "CPU" in str(sensor.Name):
                    return f"Nhiệt độ {sensor.Name}: {sensor.Value:.1f}°C (OHM)"
        except:
            pass
        methods_tried.append("OpenHardwareMonitor: Not running")
    except:
        pass
    
    # Không đọc được
    return f"Không đọc được nhiệt độ. Đã thử: {', '.join(methods_tried)}. Hãy cài LibreHardwareMonitor và chạy nó."


def get_temperature_alert():
    """Kiểm tra nhiệt độ và trả về mức độ cảnh báo"""
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return None, "Không đọc được nhiệt độ"
            
        max_temp = 0
        hottest_sensor = ""
        
        for name, entries in temps.items():
            for entry in entries:
                if entry.current and entry.current > max_temp:
                    max_temp = entry.current
                    hottest_sensor = name
                    
        # Ngưỡng nhiệt độ
        if max_temp >= 90:
            return "danger", f"Nhiệt độ {hottest_sensor} rất cao: {max_temp}°C - Nguy hiểm!"
        elif max_temp >= 80:
            return "critical", f"Nhiệt độ {hottest_sensor} cao: {max_temp}°C - Cần làm mát!"
        elif max_temp >= 70:
            return "warning", f"Nhiệt độ {hottest_sensor}: {max_temp}°C - Đang nóng"
        else:
            return "normal", f"Nhiệt độ {hottest_sensor}: {max_temp}°C - Bình thường"
            
    except:
        return None, "Không hỗ trợ đọc nhiệt độ"


# ===============================
# ĐỘ SÁNG
# ===============================

def get_brightness():
    try:
        import screen_brightness_control as sbc

        brightness = sbc.get_brightness(display=0)[0]

        return f"Độ sáng hiện tại {brightness}%"

    except Exception as e:
        return f"Lỗi độ sáng: {e}"


def set_brightness(value):
    try:
        import screen_brightness_control as sbc

        value = max(0, min(value, 100))

        sbc.set_brightness(value)

        return f"Đã đặt độ sáng {value}%"

    except Exception as e:
        return f"Lỗi độ sáng: {e}"


def brightness_up(step=10):
    try:
        import screen_brightness_control as sbc

        current = sbc.get_brightness(display=0)[0]
        new = min(current + step, 100)

        sbc.set_brightness(new)

        return "Đã tăng độ sáng"

    except Exception as e:
        return f"Lỗi: {e}"


def brightness_down(step=10):
    try:
        import screen_brightness_control as sbc

        current = sbc.get_brightness(display=0)[0]
        new = max(current - step, 0)

        sbc.set_brightness(new)

        return "Đã giảm độ sáng"

    except Exception as e:
        return f"Lỗi: {e}"


# ===============================
# WIFI
# ===============================

def wifi_on():
    try:
        subprocess.run(
            ["netsh", "interface", "set", "interface", "Wi-Fi", "enabled"],
            capture_output=True
        )
        return "WiFi đã bật"
    except:
        return "Không bật được WiFi"


def wifi_off():
    try:
        subprocess.run(
            ["netsh", "interface", "set", "interface", "Wi-Fi", "disabled"],
            capture_output=True
        )
        return "WiFi đã tắt"
    except:
        return "Không tắt được WiFi"


# ===============================
# NGUỒN MÁY
# ===============================

def shutdown():
    os.system("shutdown /s /t 1")
    return "Đang tắt máy"


def restart():
    os.system("shutdown /r /t 1")
    return "Đang khởi động lại"


def lock():
    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    return "Đã khóa máy"


# ===============================
# TEST
# ===============================

if __name__ == "__main__":

    import comtypes
    comtypes.CoInitialize()

    print("---- TEST SYSTEM ----")

    print(get_cpu_usage())
    print(get_ram_usage())
    print(get_disk_usage())

    print(get_battery())
    print(get_system_volume())
    print(get_brightness())
    
    print("\n---- TEMPERATURE ----")
    print(get_cpu_temperature())
    level, msg = get_temperature_alert()
    print(f"Alert: {level} - {msg}")

    comtypes.CoUninitialize()