import os
import platform
import subprocess
import time
import psutil


# --- Điều khiển âm lượng (Chỉ dành cho Windows) ---
if platform.system() == "Windows":
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        from ctypes import cast, POINTER
    except ImportError:
        print(
            "Cảnh báo: Không thể import pycaw. Các chức năng điều khiển âm lượng sẽ không hoạt động."
        )
        AudioUtilities = None


def set_system_volume(volume: int):
    """
    Đặt âm lượng hệ thống (chỉ Windows).
    volume: phần trăm âm lượng (0-100).
    """
    if platform.system() != "Windows" or AudioUtilities is None:
        return "Tính năng điều khiển âm lượng chỉ hỗ trợ trên Windows và yêu cầu pycaw."

    try:
        devices = AudioUtilities.GetDefaultAudioEndpoint()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        volume_interface = cast(interface, POINTER(IAudioEndpointVolume))

        # Đặt âm lượng theo thang từ 0.0 đến 1.0
        volume_interface.SetMasterVolumeLevelScalar(volume / 100.0, None)
        return f"Đã đặt âm lượng hệ thống thành {volume}%."
    except Exception as e:
        return f"Lỗi khi đặt âm lượng: {e}"


def get_system_volume():
    """
    Lấy âm lượng hệ thống hiện tại (chỉ Windows).
    """
    if platform.system() != "Windows" or AudioUtilities is None:
        return "Tính năng điều khiển âm lượng chỉ hỗ trợ trên Windows và yêu cầu pycaw."

    try:
        devices = AudioUtilities.GetDefaultAudioEndpoint()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        volume_interface = cast(interface, POINTER(IAudioEndpointVolume))

        current_volume = int(volume_interface.GetMasterVolumeLevelScalar() * 100)
        return f"Âm lượng hệ thống hiện tại là {current_volume}%."
    except Exception as e:
        return f"Lỗi khi lấy âm lượng: {e}"


def toggle_mute_system_volume():
    """
    Bật/tắt tiếng âm lượng hệ thống (chỉ Windows).
    """
    if platform.system() != "Windows" or AudioUtilities is None:
        return "Tính năng điều khiển âm lượng chỉ hỗ trợ trên Windows và yêu cầu pycaw."

    try:
        devices = AudioUtilities.GetDefaultAudioEndpoint()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        volume_interface = cast(interface, POINTER(IAudioEndpointVolume))

        current_mute = volume_interface.GetMute()
        volume_interface.SetMute(not current_mute, None)
        if not current_mute:
            return "Đã tắt tiếng hệ thống."
        else:
            return "Đã bật tiếng hệ thống."
    except Exception as e:
        return f"Lỗi khi bật/tắt tiếng: {e}"


# --- Điều khiển nguồn máy tính ---
def shutdown_computer():
    """Tắt máy tính."""
    if platform.system() == "Windows":
        os.system("shutdown /s /t 1")
        return "Đang tắt máy tính..."
    elif platform.system() == "Linux" or platform.system() == "Darwin":  # macOS
        os.system("sudo shutdown -h now")
        return "Đang tắt máy tính..."
    else:
        return "Hệ điều hành không được hỗ trợ để tắt máy."


def restart_computer():
    """Khởi động lại máy tính."""
    if platform.system() == "Windows":
        os.system("shutdown /r /t 1")
        return "Đang khởi động lại máy tính..."
    elif platform.system() == "Linux" or platform.system() == "Darwin":  # macOS
        os.system("sudo shutdown -r now")
        return "Đang khởi động lại máy tính..."
    else:
        return "Hệ điều hành không được hỗ trợ để khởi động lại máy tính."


def lock_computer():
    """Khóa máy tính."""
    if platform.system() == "Windows":
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        return "Đang khóa máy tính."
    elif platform.system() == "Linux":
        # Cần một công cụ khóa màn hình cụ thể (ví dụ: gnome-screensaver-command, xdg-screensaver)
        # Đây là một ví dụ, có thể không hoạt động trên tất cả các môi trường Linux
        subprocess.run(["xdg-screensaver", "lock"])
        return "Đang khóa màn hình Linux (cần cấu hình)."
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(
            [
                "/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession",
                "-suspend",
            ]
        )
        return "Đang khóa máy tính macOS."
    else:
        return "Hệ điều hành không được hỗ trợ để khóa máy tính."


# --- Giám sát hệ thống ---
def get_cpu_usage():
    """Lấy phần trăm sử dụng CPU."""
    cpu_percent = psutil.cpu_percent(interval=1)  # Lấy dữ liệu trong 1 giây
    return f"Mức sử dụng CPU hiện tại là {cpu_percent}%."


def get_ram_usage():
    """Lấy phần trăm và chi tiết sử dụng RAM."""
    vm = psutil.virtual_memory()
    total = vm.total / (1024**3)  # Tổng RAM tính bằng GB
    used = vm.used / (1024**3)  # RAM đã dùng tính bằng GB
    percent = vm.percent
    return (
        f"Mức sử dụng RAM hiện tại là {percent}%. "
        f"Đã dùng {used:.2f} GB trên tổng số {total:.2f} GB."
    )


def get_disk_usage(path="C:\\"):
    """Lấy phần trăm sử dụng ổ đĩa cho một đường dẫn cụ thể (mặc định là ổ C: trên Windows)."""
    if not os.path.exists(path):
        return f"Đường dẫn '{path}' không tồn tại."

    disk_usage = psutil.disk_usage(path)
    total = disk_usage.total / (1024**3) # Tổng dung lượng tính bằng GB
    used = disk_usage.used / (1024**3)   # Dung lượng đã dùng tính bằng GB
    percent = disk_usage.percent
    return (
        f"Ổ đĩa {path} đang được sử dụng {percent}% dung lượng. "
        f"Đã dùng {used:.2f} GB trên tổng số {total:.2f} GB."
    )


if __name__ == "__main__":
    print("--- Thử nghiệm chức năng hệ thống ---")
    print(get_cpu_usage())
    print(get_ram_usage())
    print(get_disk_usage("C:\\")) # Thay đổi ổ đĩa nếu cần

    # Cẩn thận khi thử các chức năng này!
    # print(set_system_volume(50))
    # time.sleep(1)
    # print(get_system_volume())
    # time.sleep(1)
    # print(toggle_mute_system_volume())
    # time.sleep(1)
    # print(toggle_mute_system_volume())

    # print(lock_computer())
    # print(shutdown_computer()) # Cẩn thận: sẽ tắt máy!
    # print(restart_computer()) # Cẩn thận: sẽ khởi động lại máy!
