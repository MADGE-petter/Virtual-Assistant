import datetime
import json
import os
import re
import sys
import time
import webbrowser

import playsound
import requests
import speech_recognition as sr
from gtts import gTTS
from transformers import pipeline
from youtube_search import YoutubeSearch
try:
    from POP import (
        classify_intent,
        handle_intent,
        get_text as original_get_text,
        get_voice as original_get_voice,
        speak as original_speak,
    )
except ImportError as e:
    print(f"Lỗi import từ POP.py: {e}")
    # Fallback functions if imports fail
    def classify_intent(text):
        print("Mock classify_intent")
        return "unknown"
    def handle_intent(intent, name, text):
        print(f"Mock handle_intent: {intent}")
        return "Mock response"
    def original_get_text():
        print("Mock get_text")
        return 0
    def original_get_voice():
        print("Mock get_voice")
        return "..."
    def original_speak(text):
        print(f"Mock speak: {text}")

# Dữ liệu từ khóa để phân loại ý định
intent_data = {
    "open_website": ["mở trang web", "truy cập", "mở google", "mở youtube", "mở facebook", ".com", "www", "mở"],
    "greeting": ["xin chào", "chào bạn", "hello", "hi"],
    "weather": ["thời tiết", "nhiệt độ", "trời hôm nay"],
    "search": ["tìm kiếm", "tra cứu", "tìm trên google", "search google", "tìm kiếm trên google"],
    "music": ["nghe nhạc", "mở nhạc", "bật nhạc", "chơi nhạc", "phát nhạc"],
    "tell_me": ["kể chuyện", "đọc wikipedia", "nói về"],
    "open_application": ["mở ứng dụng", "chạy phần mềm", "mở app"],
    "close_application": ["đóng ứng dụng", "tắt phần mềm", "đóng app"],
    "list_applications": ["liệt kê ứng dụng", "các ứng dụng đang chạy"],
    "open_file_or_dir": ["mở tệp", "mở thư mục", "mở file", "mở folder", "mở thư mục tải xuống"],
    "list_dir_contents": ["liệt kê nội dung", "xem file", "xem thư mục"],
    "time": ["mấy giờ", "bây giờ là mấy giờ", "hôm nay là ", "thời gian"],
    "system_volume_set": ["đặt âm lượng", "chỉnh âm lượng"],
    "system_volume_get": ["âm lượng hiện tại", "mấy phần trăm âm lượng"],
    "system_volume_toggle_mute": ["tắt tiếng", "bật tiếng", "im lặng"],
    "system_shutdown": ["tắt máy", "tắt máy tính", "shutdown", "tắt"],
    "system_restart": ["khởi động lại máy", "restart máy tính"],
    "system_lock": ["khóa máy", "khóa màn hình", "khóa", "lock"],
    "system_cpu_usage": ["mức sử dụng cpu", "cpu bao nhiêu"],
    "system_ram_usage": ["mức sử dụng ram", "ram bao nhiêu"],
    "system_disk_usage": ["dung lượng ổ đĩa", "ổ đĩa bao nhiêu"],
    "goodbye": ["tạm biệt", "hẹn gặp lại", "bye", "dừng", "thôi"],
}

# Mô hình NLP để phân loại ý định phức tạp hơn
nlp_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def get_voice():
    """Get voice input"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Me: ", end="")  # Yêu cầu người dùng nói
        # Giảm thời gian nghe để phản hồi nhanh hơn
        r.pause_threshold = 0.8  # Giảm từ 1.0 xuống 0.8
        r.energy_threshold = 250  # Giảm từ 300 xuống 250
        audio = r.listen(source, phrase_time_limit=6, timeout=8)  # Giảm từ 8s xuống 6s, từ 10s xuống 8s
        try:
            text = r.recognize_google(audio, language="vi-VN")
            print(text)
            return text
        except sr.UnknownValueError:
            print("...")  # Khi không nhận diện được giọng nói
            return "..."
        except sr.RequestError as e:
            print(f"Lỗi dịch vụ giọng nói: {e}")
            return "Lỗi"
        except Exception as e:
            print(f"Lỗi không xác định khi nhận giọng nói: {e}")
            return "Lỗi"

def get_text():
    """Get text with retry logic"""
    for i in range(3):
        text = get_voice()
        if text and text != 0 and text != "...":
            return text.lower()
        elif i < 2:
            speak("Bot không nghe rõ, bạn có thể nói lại không?")
    speak("Tạm biệt!")
    return 0

def classify_intent_by_keywords(text):
    for intent, keywords in intent_data.items():
        for keyword in keywords:
            if keyword in text:
                return intent
    return "unknown"

def classify_intent(text):
    intent = classify_intent_by_keywords(text)
    if intent != "unknown":
        return intent
    candidate_labels = list(intent_data.keys())
    result = nlp_pipeline(text, candidate_labels)
    # nlp_pipeline có thể trả về một mảng kết quả, lấy kết quả có điểm cao nhất
    return result["labels"][0]

def speak(text):
    print(f"Bot: {text}")
    try:
        tts = gTTS(text=text, lang="vi", slow=False)
        tts.save("sound.mp3")
        playsound.playsound("sound.mp3", False)
        os.remove("sound.mp3")
    except Exception as e:
        print(f"Lỗi khi phát âm thanh: {e}")

# Export functions for use in other modules
__all__ = ['PopModel', 'classify_intent', 'handle_intent', 'get_voice', 'speak', 'intent_data', 'nlp_pipeline']

class PopModel:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
    
    def classify_intent_by_keywords(self, text):
        for intent, keywords in intent_data.items():
            for keyword in keywords:
                if keyword in text:
                    return intent
        return "unknown"
    
    def classify_intent(self, text):
        intent = self.classify_intent_by_keywords(text)
        if intent != "unknown":
            return intent
        candidate_labels = list(intent_data.keys())
        result = nlp_pipeline(text, candidate_labels)
        return result["labels"][0]
    
    def speak(self, text):
        print(f"Bot: {text}")
        original_speak(text)
    
    def handle_intent(self, intent, name, text):
        response = ""
        
        if intent == "greeting":
            response = f"Chào {name}, tôi là Pop. Bạn cần tôi giúp gì?"
        elif intent == "open_website":
            regex = re.search(r"(mở|truy cập)\s+(trang web)?\s*(\S+(?:\.\S+)?|\S+)", text)
            if regex:
                domain = regex.group(3)
                if domain.lower() == "google":
                    domain = "google.com"
                elif domain.lower() == "youtube":
                    domain = "youtube.com"
                elif domain.lower() == "facebook":
                    domain = "facebook.com"
                
                if not domain.startswith("http"):
                    url = "https://" + domain
                else:
                    url = domain
                try:
                    webbrowser.open(url)
                    response = f"Tôi đã mở trang web {domain} cho bạn."
                except Exception as e:
                    response = f"Lỗi khi mở trang web {domain}: {e}"
            else:
                response = "Tôi không thể xác định trang web bạn muốn mở."
        elif intent == "search":
            # Trích xuất nội dung tìm kiếm từ câu - loại bỏ tất cả từ khóa
            regex_patterns = [
                r"(?:tìm kiếm|tra cứu|tìm trên google|search google|tìm kiếm trên google)\s+(.+)",
                r"(?:tôi muốn tìm|tìm giúp tôi)\s+(.+)",
                r"(?:tìm|search)\s+(.+)"
            ]
            
            search_query = None
            for pattern in regex_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    search_query = match.group(1).strip()
                    # Loại bỏ tất cả các từ khóa lệnh
                    search_query = re.sub(r'\b(tìm kiếm|tra cứu|tìm trên google|search google|tìm kiếm trên google|tôi muốn tìm|tìm giúp tôi|tìm|search)\s*', '', search_query, flags=re.IGNORECASE)
                    break
            
            if search_query:
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
                response = f"Tôi đã tìm kiếm {search_query} trên Google."
            else:
                response = "Xin lỗi, tôi không hiểu bạn muốn tìm kiếm gì."
        elif intent == "goodbye":
            response = "Hẹn gặp lại bạn! Chúc bạn một ngày tốt lành."
            return "goodbye_intent_detected"
        else:
            response = "Xin lỗi, tôi không hiểu lệnh của bạn. Bạn có thể nói rõ hơn không?"
        
        self.speak(response)
        time.sleep(1)  # Giảm từ 2s xuống 1s
        return response
