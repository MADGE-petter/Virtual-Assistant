"""Conversation Controller - Điều phối conversation flow."""
import threading
import time
from typing import Optional, Callable

from controller.interfaces import IAudioService, ISqlService, IActionHandler, IUserController


class ConversationController:
    def __init__(self,
                 audio_service: IAudioService,
                 sql_service: ISqlService,
                 action_handler: IActionHandler,
                 user_controller: IUserController):
        self.audio = audio_service
        self.sql = sql_service
        self.actions = action_handler
        self.user = user_controller
        
        # State
        self._assistant_active = False
        self._session_id: Optional[int] = None
        self._last_input: Optional[str] = None
        
        # Lazy init services
        self._conversation_service = None
        self._memory_service = None
        self._first_greeting_done = False  # Chỉ chào 1 lần khi mở app
    
    def init_intent_service(self):
        """Eager init IntentService to avoid race conditions."""
        if self._conversation_service:
            self._conversation_service.init_intent_service()
    
    # ============================================================
    # SESSION MANAGEMENT 
    # ============================================================
    
    def start_session(self) -> None:
        """Bắt đầu conversation session."""
        user_name = self.user.get_display_name() or "guest"
        self._session_id = self.sql.start_session(user_name)
        print(f"[ConversationController] Session started: {self._session_id}")
    
    def end_session(self) -> None:
        """Kết thúc conversation session."""
        if self._session_id:
            self.sql.end_session(self._session_id)
            print(f"[ConversationController] Session ended: {self._session_id}")
            self._session_id = None
    
    # ============================================================
    # MAIN LOOP 
    # ============================================================
    
    def run_main_loop(self,
                     get_input_callback: Callable[[], Optional[str]],
                     on_idle_callback: Optional[Callable] = None,
                     idle_timeout: int = 15) -> None:
        """Main conversation loop - chỉ điều phối, không xử lý logic.
        
        Args:
            get_input_callback: Function để lấy user input
            on_idle_callback: Function gọi khi idle timeout
            idle_timeout: Số giây idle trước khi trigger callback
        """
        print("[ConversationController] Main loop starting...")
        self._assistant_active = True
        
        last_interaction = time.time()
        
        try:
            while self._assistant_active:
                # Check idle timeout
                idle_time = time.time() - last_interaction
                if idle_time > idle_timeout:
                    if on_idle_callback:
                        on_idle_callback()
                    break
                
                # Get input (delegate to callback)
                user_input = get_input_callback()
                
                if not user_input or user_input in ["...", "", None, 0]:
                    time.sleep(1)
                    continue
                
                # Check for duplicate input
                if user_input == self._last_input:
                    time.sleep(1)
                    continue
                
                self._last_input = user_input
                last_interaction = time.time()
                
                # Check exit
                if self._should_exit(user_input):
                    self._assistant_active = False
                    break
                
                # Delegate processing to ConversationService
                self._process_exchange(user_input)
                
        except Exception as e:
            print(f"[ConversationController] Error in main loop: {e}")
            import traceback
            traceback.print_exc()
        
    
    def run_first_interaction(self,
                              get_input_callback: Callable[[], Optional[str]],
                              speak_callback: Optional[Callable] = None,
                              from_wake_up: bool = False) -> None:
        """Interaction đầu tiên (hỏi tên nếu chưa biết, hoặc chào nếu đã biết)."""
        user_name = self.user.get_display_name()
        
        if user_name == "bạn" or not user_name:
            # Chưa biết tên -> hỏi và đợi input
            greeting = "Chào bạn! Tôi là Pop. Bạn có thể cho tôi biết tên của bạn được không?"
            if speak_callback:
                speak_callback(greeting)
            else:
                self.audio.speak(greeting)
            
            user_input = get_input_callback()
            if user_input and user_input not in ["...", "", None, 0]:
                self._process_exchange(user_input, speak_callback)
        else:
            # Đã biết tên -> chào 1 lần đầu tiên hoặc khi wake up
            if not self._first_greeting_done or from_wake_up:
                if from_wake_up:
                    greeting = f"Pop đây! Chào {user_name}, bạn cần giúp gì?"
                else:
                    greeting = f"Chào {user_name}! Rất vui được gặp lại bạn. Bạn cần mình giúp gì?"
                if speak_callback:
                    speak_callback(greeting)
                else:
                    self.audio.speak(greeting)
                self._first_greeting_done = True
    
    def stop(self) -> None:
        """Dừng main loop."""
        self._assistant_active = False
    
    def set_assistant_active(self, active: bool) -> None:
        """Set assistant active state."""
        self._assistant_active = active
    
    # ============================================================
    # PRIVATE - Service access
    # ============================================================
    
    def _get_conversation_service(self):
        """Lazy init ConversationService."""
        if self._conversation_service is None:
            from service.conversation_service import ConversationService
            self._conversation_service = ConversationService(
                self.audio,
                self.user,
                self.actions
            )
            
            # Inject MemoryService
            if self._memory_service is None:
                from service.memory_service import MemoryService
                self._memory_service = MemoryService(self.sql)
            
            self._conversation_service.init_memory_service(self._memory_service)
        
        return self._conversation_service
    
    def _process_exchange(self, user_input: str, speak_callback: Optional[Callable] = None) -> str:
        """Delegate processing to ConversationService."""
        service = self._get_conversation_service()
        user_name = self.user.get_display_name() or "guest"
        # session_id là integer từ create_session
        session_id = self._session_id if self._session_id else 1
        return service.process_exchange(user_input, speak_callback, user_name, session_id)
    
    def _should_exit(self, user_input: str) -> bool:
        """Check if user wants to exit."""
        service = self._get_conversation_service()
        return service.should_exit(user_input)
