import json
import os
import threading
import time
import webbrowser

class PopController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.assistant_active = False
        self.assistant_started = False
        self.user_name = "bạn"
        self.assistant_name = "Pop"
        self.user_data_file = "user_data.json"
        
        # Set up controller callbacks
        self.setup_callbacks()
        
        # Load user data
        self.load_user_name()
    
    def setup_callbacks(self):
        # Connect view events to controller methods
        self.view.on_start_stop_click = self.on_start_stop_click
        self.view.on_mic_click = self.on_mic_click
        self.view.on_exit_click = self.on_exit_click
    
    def load_user_name(self):
        """Load user name from file if exists"""
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_name = data.get('name', 'bạn')
                    print(f"Đã tải tên người dùng: {self.user_name}")
        except Exception as e:
            print(f"Lỗi khi tải tên người dùng: {e}")
            self.user_name = "bạn"
    
    def save_user_name(self, name):
        """Save user name to file"""
        try:
            data = {'name': name}
            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Đã lưu tên người dùng: {name}")
        except Exception as e:
            print(f"Lỗi khi lưu tên người dùng: {e}")
    
    def on_start_stop_click(self):
        if not self.assistant_started:
            # First time starting
            self.view.update_status(f"{self.assistant_name} đang hoạt động...", "yellow")
            self.assistant_active = True
            self.assistant_started = True
            threading.Thread(target=self._run_assistant_logic, daemon=True).start()
        else:
            # Assistant was started before but is now inactive, allow restart
            self.view.update_status("Đang khởi động lại...", "orange")
            self.assistant_active = True
            threading.Thread(target=self._run_assistant_logic, daemon=True).start()
    
    def on_mic_click(self):
        if not self.assistant_active:
            self.view.update_status("Vui lòng bắt đầu trợ lý trước!", "red")
            return
        
        # Manual voice input
        threading.Thread(target=self._manual_voice_input, daemon=True).start()
    
    def on_exit_click(self):
        self.assistant_active = False
        self.view.destroy_window_after_delay(1000)
    
    def speak_ui(self, text):
        """UI-aware speak function"""
        # Set speaking state for animation
        self.view.set_speaking_state(True)
        self.view.set_listening_state(False)
        
        # Update UI
        display_text = text.replace("Bot:", f"{self.assistant_name}:") if text.startswith("Bot:") else text
        self.view.update_bot_text(display_text)
        
        # Call model speak function
        self.model.speak(text)
        
        # Clear bot text after delay
        speech_delay = max(3000, len(text) * 120)
        self.view.clear_bot_text_after_delay(speech_delay)
        
        # Reset speaking state after delay
        def reset_speaking():
            self.view.set_speaking_state(False)
        self.view.master.after(speech_delay, reset_speaking)
    
    def get_voice_ui(self):
        """UI-aware voice input function"""
        # Wait until bot finishes speaking
        while self.view.is_speaking:
            time.sleep(0.1)
        
        # Add delay to ensure echo has dissipated
        time.sleep(2.0)
        
        # Set listening state
        self.view.set_listening_state(True)
        self.view.set_speaking_state(False)
        
        # Update UI
        self.view.update_status("Bắt đầu nói...", "orange")
        time.sleep(0.5)
        self.view.update_status("Đang nghe...", "red")
        self.view.update_user_text("")
        self.view.update_mic_icon(True)
        
        # Get voice input
        text = self.model.get_voice()
        
        # Reset listening state
        self.view.set_listening_state(False)
        self.view.update_mic_icon(False)
        
        # Update UI with recognized text
        if text and text != "..." and text != "Lỗi":
            display_text = text if text != 0 else "Không nhận diện được giọng nói."
            self.view.update_user_text(f"Bạn nói: {display_text}")
        
        return text
    
    def get_text_ui(self):
        """Get text with retry logic"""
        for i in range(3):
            text = self.get_voice_ui()
            if text and text != 0 and text != "...":
                return text.lower()
            elif i < 2:
                self.speak_ui(f"{self.assistant_name} không nghe rõ, bạn có thể nói lại không?")
        
        self.speak_ui("Tạm biệt!")
        if self.view.window_exists():
            self.view.destroy_window_after_delay(5000)
        return 0
    
    def _manual_voice_input(self):
        """Handle manual voice input from mic button"""
        text = self.get_voice_ui()
        if text and text != 0 and text != "...":
            intent = self.model.classify_intent(text)
            action_result = self.model.handle_intent(intent, self.user_name, text)
            self._handle_action_result(action_result, text)
    
    def _run_assistant_logic(self):
        """Main assistant logic loop"""
        # Check if we already know user's name
        if self.user_name != "bạn":
            self.speak_ui(f"Chào mừng trở lại {self.user_name}!")
            time.sleep(1)
        else:
            # First time, ask for name
            self.speak_ui(f"Xin chào, tôi là {self.assistant_name}. Bạn tên là gì nhỉ?")
            time.sleep(1)
            
            name_input = self.get_text_ui()
            if name_input and name_input != 0:
                self.user_name = name_input
                self.save_user_name(name_input)
                self.speak_ui(f"Chào bạn {self.user_name}.")
            else:
                self.speak_ui(f"Tôi không nghe rõ tên bạn. Chúng ta sẽ bắt đầu lại khi bạn nhấn mic.")
                self.assistant_active = False
                return
        
        # Main interaction loop
        while self.view.window_exists() and self.assistant_active:
            self.speak_ui("Bạn cần tôi làm gì?")
            time.sleep(5)
            
            text = self.get_text_ui()
            
            if not text or text == 0:
                self.assistant_active = False
                break
            
            intent = self.model.classify_intent(text)
            action_result = self.model.handle_intent(intent, self.user_name, text)
            self._handle_action_result(action_result, text)
            
            if not self.view.window_exists():
                break
            
            time.sleep(1)
        
        # Final goodbye message
        self.speak_ui("Hẹn gặp lại bạn! Chúc bạn một ngày tốt lành.")
        self.assistant_active = False
        if self.view.window_exists():
            self.view.destroy_window_after_delay(2000)
    
    def _handle_action_result(self, action_result, original_text):
        """Handle special action results"""
        if action_result == "goodbye_intent_detected":
            self.assistant_active = False
            return
        elif action_result == "need_search_query":
            self.speak_ui("Bạn muốn tìm kiếm gì trên Google?")
            time.sleep(3)
            search_query = self.get_text_ui()
            if search_query and search_query != 0 and search_query != "...":
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
                self.speak_ui(f"Tôi đã tìm kiếm {search_query} trên Google.")
            else:
                self.speak_ui("Không có gì để tìm kiếm!")
            return
        elif action_result and "google.com" in action_result.lower():
            self.speak_ui("Bạn muốn tìm kiếm gì trên Google?")
            time.sleep(3)
            search_query = self.get_text_ui()
            if search_query and search_query != 0 and search_query != "...":
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
                self.speak_ui(f"Tôi đã tìm kiếm {search_query} trên Google.")
            else:
                self.speak_ui("Không có gì để tìm kiếm!")
            return
