"""PopController - Facade điều phối chính."""
import threading
import sys
import os
sys.path.append(os.path.dirname(__file__))

from PyQt6.QtCore import pyqtSignal, QObject

# Services
from action import ActionHandler
from service.AudioService import AudioService
from model.Sql import SqlService
from service.wake_word import WakeWordDetector
from service.user_service import UserService
from service.alert_service import AlertManager
from service.analytics_service import get_analytics_service

# Sub-controllers
from controller.voice_controller import VoiceController
from controller.user_controller import UserController
from controller.system_controller import SystemController
from controller.conversation_controller import ConversationController


class PopController(QObject):
    """Facade controller - chỉ điều phối, không xử lý logic chi tiết."""
    
    # Signal để wake up từ thread khác (thread-safe)
    wakeUpRequested = pyqtSignal()
    
    def __init__(self, view=None, model=None, login_username=None):
        super().__init__()
        self.view = view
        self.login_username = login_username
        
        # State
        self._started = False
        self._active = False
        
        # === KHỞI TẠO SERVICES ===
        self.audio = AudioService(view)
        self.sql = SqlService()
        self.actions = ActionHandler(self.audio, view)
        
        # User service
        self._user_svc = UserService(self.sql)
        if login_username:
            self._user_svc.login_name = login_username
            # Only load display_name if exists, don't fallback to login_username
            # Bot will ask for name if display_name is None
            loaded_name = self._user_svc.get_display_name_by_login(login_username)
            if loaded_name and loaded_name != "bạn":
                self._user_svc.display_name = loaded_name
            # else: leave as None so bot asks for name
        
        # Alert & Analytics - only use display_name if set, otherwise "bạn"
        user_name = getattr(self._user_svc, 'display_name', None) or "bạn"
        self._alert_mgr = AlertManager(self.audio, self._on_alert, 30, user_name)
        self._analytics = get_analytics_service(user_name or "user")
        self._analytics.start()
        
        # === KHỞI TẠO SUB-CONTROLLERS ===
        self.wake_detector = WakeWordDetector(self.audio, view)
        self.voice = VoiceController(self.audio)
        self.voice.init_wake_detector(self.wake_detector)
        self.user = UserController(self._user_svc, self.sql)
        self.system = SystemController(self._alert_mgr, self._analytics)
        self.conversation = ConversationController(self.audio, self.sql, self.actions, self.user)
        
        # === SETUP CALLBACKS ===
        self.voice.on_wake_up = self._request_wake_up
        self.voice.on_go_sleep = self._on_go_sleep
        self.wakeUpRequested.connect(self._do_wake_up)
        
        # Inject controller vào view (view không cần biết services)
        if view:
            view.set_controller(self)
    
    # ============================================================
    # PUBLIC API
    # ============================================================
    
    def start(self):
        """Khởi động assistant."""
        if self._started:
            self._active = True
            return
        
        self._started = True
        self._active = True
        self.conversation.set_assistant_active(True)
        
        # Init intent service early to avoid race conditions
        self.conversation.init_intent_service()
        
        self.system.start_monitoring(self.user.get_display_name())
        self._enter_active_mode()
    
    def stop(self):
        """Dừng assistant."""
        self._active = False
        self.conversation.set_assistant_active(False)
        self.voice.stop_wake_word_detection()
        self.system.stop_monitoring()
        self.conversation.end_session()
    
    def sleep(self, manual=True):
        """Vào sleep mode."""
        self.voice.go_to_sleep(manual, self.audio.speak)
    
    def wake(self):
        """Thức dậy từ sleep."""
        self.voice.handle_wake_up()
    
    # ============================================================
    # DELEGATE METHODS 
    # ============================================================
    
    def speak(self, text):
        """Bot nói."""
        return self.voice.speak(text, update_ui=True)
    
    def listen(self):
        """Bot nghe."""
        return self.voice.get_voice_input()
    
    # ============================================================
    # PRIVATE 
    # ============================================================
    
    def _request_wake_up(self):
        """Callback từ VoiceController khi wake word detected."""
        self.wakeUpRequested.emit()
    
    def _activate_view(self):
        """Activate and show main window (helper to avoid duplication)."""
        if self.view:
            self.view.show()
            self.view.raise_()
            self.view.activateWindow()
    
    def _do_wake_up(self):
        """Thực hiện wake up trên main thread."""
        self.system.set_sleep_mode(False)
        self.system.reset_wellness_timers()
        
        self._activate_view()
        self._start_conversation(from_wake_up=True)
    
    def _on_go_sleep(self):
        """Callback khi vào sleep."""
        self.system.set_sleep_mode(True)
        if self.view:
            self.view.hide()
    
    def _on_idle(self):
        """Callback khi idle timeout."""
        self.sleep(manual=False)
    
    def _on_alert(self, alert_data):
        """Callback khi có alert."""
        if self.view:
            self.view.show_alert_notification(alert_data)
    
    def _on_gesture(self, gesture_type):
        """Callback từ gesture service."""
        self.handle_gesture(gesture_type)
    
    # ============================================================
    # PRIVATE - Conversation management
    # ============================================================
    
    def _enter_active_mode(self):
        """Vào active mode - hiện app và bắt đầu conversation."""
        self._activate_view()
        self.system.reset_wellness_timers()
        self._start_conversation()
        self.voice.start_idle_monitor(self._on_idle)
    
    def _start_conversation(self, from_wake_up: bool = False):
        """Bắt đầu conversation thread."""
        threading.Thread(target=self._run_conversation, args=(from_wake_up,), daemon=True).start()
    
    def _run_conversation(self, from_wake_up: bool = False):
        """Conversation main loop."""
        try:
            self.conversation.start_session()
            self.conversation.run_first_interaction(
                get_input_callback=self.voice.get_voice_input,
                speak_callback=self.audio.speak,
                from_wake_up=from_wake_up
            )
            self.conversation.run_main_loop(
                get_input_callback=self.voice.get_voice_input,
                on_idle_callback=lambda: self.sleep(manual=False),
                idle_timeout=45
            )
        except Exception as e:
            print(f"[PopController] Conversation error: {e}")
            import traceback
            traceback.print_exc()
    
    # ============================================================
    # LEGACY COMPATIBILITY
    # ============================================================
    
    @property
    def assistant_active(self):
        return self._active
    
    @property  
    def assistant_started(self):
        return self._started
    
    def set_wake_word_enabled(self, enabled):
        """Legacy."""
        self.voice.wake_word_enabled = enabled
    
    def classify_intent_simple(self, text):
        """Legacy."""
        from service.intern import IntentClassifier
        return IntentClassifier.classify(text)
