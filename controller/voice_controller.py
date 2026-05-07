"""Voice Controller - Quản lý voice, wake word và sleep mode."""

import threading
import time
from typing import Optional, Callable
from controller.interfaces import IAudioService


class VoiceController:
    def __init__(self, audio_service: IAudioService, view=None):
        self.audio_service = audio_service
        self.view = view
        
        # Wake word
        self.wake_detector = None
        self.wake_word_enabled = True
        self.is_waiting_for_wake = False
        
        # Sleep mode
        self.is_sleeping = False
        self.idle_timeout_seconds = 40
        self.last_interaction_time = time.time()
        
        # Callbacks
        self.on_wake_up = None
        self.on_go_sleep = None
    
    def init_wake_detector(self, wake_detector):
        """Inject wake detector sau khi tạo"""
        self.wake_detector = wake_detector
    
    def start_wake_word_detection(self, wake_up_callback, on_wake_word_callback=None):
        """Bắt đầu lắng nghe wake word."""
        if not self.wake_word_enabled or not self.wake_detector:
            return False
        if self.wake_detector.is_listening:
            return True
        self.wake_detector.start_listening(
            callback=on_wake_word_callback,
            wake_up_callback=wake_up_callback
        )
        return True
    
    def stop_wake_word_detection(self):
        """Dừng lắng nghe wake word."""
        if self.wake_detector and self.wake_detector.is_listening:
            self.wake_detector.stop_listening()
    
    def handle_wake_up(self):
        """Xử lý khi wake word được phát hiện."""
        # DỪNG WAKE WORD DETECTOR TRƯỚC để giải phóng microphone
        self.stop_wake_word_detection()
        self.is_sleeping = False
        self.is_waiting_for_wake = False
        self.last_interaction_time = time.time()
        
        # Nghỉ ngắn để microphone được giải phóng hoàn toàn
        time.sleep(0.5)
        
        if self.on_wake_up:
            self.on_wake_up()
    
    def go_to_sleep(self, manual=False, speak_callback=None):
        """Chuyển sang sleep mode."""
        print(f"[VoiceController] Going to sleep (manual={manual})")
        self.is_sleeping = True
        self.is_waiting_for_wake = True
        
        if manual and speak_callback:
            speak_callback("Tôi sẽ nghỉ ngơi. Hãy gọi tôi khi cần nhé!")
            time.sleep(2)
        
        if self.on_go_sleep:
            self.on_go_sleep()
        
        # Bắt đầu wake word detection để chờ đánh thức
        if self.wake_word_enabled:
            self.start_wake_word_detection(
                wake_up_callback=self.handle_wake_up
            )
    
    def start_idle_monitor(self, on_idle_timeout):
        """Bắt đầu monitor idle time."""
        def check_idle():
            while True:
                time.sleep(5)
                
                if self.audio_service.is_speaking:
                    continue
                
                if not self.is_sleeping and not self.is_waiting_for_wake:
                    idle_time = time.time() - self.last_interaction_time
                    
                    if idle_time > self.idle_timeout_seconds:
                        print(f"[VoiceController] Idle timeout ({idle_time:.0f}s)")
                        if on_idle_timeout:
                            on_idle_timeout()
                        break
        
        threading.Thread(target=check_idle, daemon=True).start()
    
    def get_voice_input(self):
        """Lấy input từ voice."""
        # Chờ bot nói xong
        self.audio_service.wait_until_speaking_done()
        time.sleep(0.3)  # Cooldown
        
        result = self.audio_service.listen()
        if result:
            self.last_interaction_time = time.time()
        else:
            time.sleep(0.2)
        
        return result
    
    def speak(self, text, update_ui=True):
        """Bot nói."""
        self.last_interaction_time = time.time()
        return self.audio_service.speak(text, update_ui=update_ui)
