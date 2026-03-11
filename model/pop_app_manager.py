import os
import platform
import subprocess
import time

import psutil

# Danh sách các đường dẫn ứng dụng phổ biến trên Windows
# Bạn có thể mở rộng danh sách này dựa trên các ứng dụng bạn muốn điều khiển
COMMON_APP_PATHS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",  # Office 2016/365
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "notepad": r"C:\Windows\System32\notepad.exe",
    "calculator": r"C:\Windows\System32\calc.exe",
    "zalo": r"C:\Users\NGUYEN ANH TUAN\AppData\Local\Programs\Zalo\Zalo.exe",  # Ví dụ, cần cập nhật user
    "code": r"C:\Users\ADMIN\AppData\Local\Programs\Microsoft VS Code\Code.exe",  # VS Code
}


def open_application(app_name: str):
    """
    Mở một ứng dụng bằng tên hoặc đường dẫn.
    app_name: Tên phổ biến của ứng dụng (ví dụ: "chrome") hoặc đường dẫn đầy đủ đến tệp .exe.
    """
    app_name_lower = app_name.lower()

    if app_name_lower in COMMON_APP_PATHS:
        path = COMMON_APP_PATHS[app_name_lower]
        if os.path.exists(path):
            try:
                os.startfile(path)
                return f"Đã mở {app_name}."
            except Exception as e:
                return f"Lỗi khi mở {app_name}: {e}"
        else:
            return f"Không tìm thấy {app_name} tại đường dẫn đã cấu hình: {path}."
    elif os.path.exists(app_name):  # Nếu người dùng cung cấp đường dẫn đầy đủ
        try:
            os.startfile(app_name)
            return f"Đã mở ứng dụng từ đường dẫn {app_name}."
        except Exception as e:
            return f"Lỗi khi mở ứng dụng từ đường dẫn {app_name}: {e}"
    else:
        return f"Không tìm thấy ứng dụng {app_name}. Vui lòng cung cấp tên hoặc đường dẫn hợp lệ."


def close_application(app_name: str):
    """
    Đóng một ứng dụng đang chạy bằng tên tiến trình.
    app_name: Tên của ứng dụng hoặc tiến trình (ví dụ: "chrome", "notepad").
    """
    app_name_lower = app_name.lower()
    found_and_closed = False

    # Chuyển đổi tên thân thiện thành tên tiến trình thực tế nếu biết
    process_name_map = {
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "notepad": "notepad.exe",
        "calculator": "calculator.exe",
        "zalo": "zalo.exe",
        "code": "code.exe",  # VS Code
        "vlc": "vlc.exe",
    }

    target_process_name = process_name_map.get(
        app_name_lower, app_name_lower
    )  # Mặc định dùng tên app_name_lower

    for proc in psutil.process_iter(["pid", "name"]):
        if target_process_name in proc.info["name"].lower():
            try:
                p = psutil.Process(proc.info["pid"])
                p.terminate()
                p.wait(timeout=3)  # Chờ tiến trình kết thúc
                if p.is_running():
                    p.kill()  # Buộc dừng nếu vẫn chạy
                found_and_closed = True
                print(
                    f"Đã đóng tiến trình: {proc.info['name']} (PID: {proc.info['pid']})"
                )
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                print(
                    f"Lỗi khi đóng tiến trình {proc.info['name']} (PID: {proc.info['pid']}): {e}"
                )

    if found_and_closed:
        return f"Đã đóng ứng dụng {app_name}."
    else:
        return f"Không tìm thấy ứng dụng {app_name} đang chạy."


def list_running_applications():
    """
    Liệt kê các ứng dụng đang chạy.
    """
    running_apps = []
    for proc in psutil.process_iter(["pid", "name", "status"]):
        try:
            # Lọc bớt các tiến trình hệ thống để tập trung vào ứng dụng người dùng
            if proc.info["status"] == psutil.STATUS_RUNNING and proc.info[
                "name"
            ] not in ["System Idle Process", "System"]:
                running_apps.append(proc.info["name"])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    unique_apps = sorted(list(set(running_apps)))
    if unique_apps:
        return (
            "Các ứng dụng đang chạy bao gồm: "
            + ", ".join(unique_apps[:10])
            + (" và nhiều ứng dụng khác." if len(unique_apps) > 10 else ".")
        )
    else:
        return "Không có ứng dụng nào đang chạy (ngoại trừ các tiến trình hệ thống)."


if __name__ == "__main__":
    print("--- Thử nghiệm chức năng quản lý ứng dụng ---")

    # print(open_application("chrome"))
    # time.sleep(5) # Cho Chrome có thời gian mở
    # print(close_application("chrome"))

    print(open_application("notepad"))
    time.sleep(2)
    print(close_application("notepad"))

    print(
        open_application(r"C:\Windows\System32\mspaint.exe")
    )  # Mở Paint bằng đường dẫn
    time.sleep(2)
    print(close_application("mspaint"))  # Đóng Paint bằng tên tiến trình

    print(list_running_applications())
