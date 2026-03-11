import os
import sys
import threading
import time
import json
import webbrowser

# Try to import audio libraries with error handling
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    print("Warning: speech_recognition not available")

try:
    import gtts
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("Warning: gtts not available")

try:
    import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False
    print("Warning: playsound not available")
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFrame, QListWidget, 
                            QListWidgetItem, QTextEdit, QScrollArea, QTabWidget, QMenu, QMenuBar, QDialog, QCheckBox, QSpinBox, QSlider, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QPoint
from PyQt6.QtGui import QFont, QColor, QPainter, QRadialGradient, QPen, QBrush, QAction

# Import database module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.conversation_db import ConversationDB

class SoundWaveWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.animation_offset = 0
        self.setMinimumHeight(180)
        self.setMinimumWidth(300)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw sound waves with better design
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # Draw multiple circles with gradient effect
        for i in range(4):
            radius = 20 + (i * 20) + (self.animation_offset % 15)
            alpha = max(0.1, 0.7 - (i * 0.15))
            
            # Create gradient for each circle
            gradient = QRadialGradient(center_x, center_y, radius)
            gradient.setColorAt(0, QColor(0, 255, 136, int(alpha * 255)))
            gradient.setColorAt(0.7, QColor(0, 200, 120, int(alpha * 200)))
            gradient.setColorAt(1, QColor(0, 150, 100, int(alpha * 100)))
            
            painter.setPen(QPen(QColor(0, 255, 136, int(alpha * 255)), 2))
            painter.setBrush(QBrush(gradient))
            
            painter.drawEllipse(center_x - radius, center_y - radius, 
                              radius * 2, radius * 2)
        
        # Central orb
        orb_gradient = QRadialGradient(center_x, center_y, 25)
        orb_gradient.setColorAt(0, QColor(150, 255, 200))
        orb_gradient.setColorAt(0.5, QColor(0, 255, 136))
        orb_gradient.setColorAt(1, QColor(0, 200, 100))
        
        painter.setPen(QPen(QColor(0, 255, 136, 150), 2))
        painter.setBrush(QBrush(orb_gradient))
        painter.drawEllipse(center_x - 25, center_y - 25, 50, 50)
        
        painter.end()
    
    def update_animation(self):
        self.animation_offset += 1
        self.update()

class PopView(QMainWindow):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.setWindowTitle("Pop Assistant")
        self.setGeometry(100, 100, 450, 650)
        
        # Assistant properties
        self.assistant_active = False
        self.assistant_started = False
        self.user_name = "bạn"
        self.assistant_name = "Pop"
        
        # Database for storing conversations
        self.db = ConversationDB()
        self.current_session_id = None
        
        # History viewer widget
        self.history_widget = None
        
        # Load user data
        self.load_user_name()
        
        # Setup UI
        self.setup_ui()
        
        # Setup animation
        self.setup_animation()
        
        # Auto-start assistant
        QTimer.singleShot(3000, self.start_assistant_thread)
        
        # Show window at end
        self.raise_()
        
        print("PopView initialized successfully")
    
    def create_menu_bar(self):
        """Create menu bar with settings"""
        menubar = QMenuBar(self)
        
        # Settings menu
        settings_menu = QMenu(" Cài đặt", self)
        menubar.addMenu(settings_menu)
        
        # Add settings actions
        settings_action = settings_menu.addAction(" Tùy chỉnh hệ thống")
        settings_action.triggered.connect(self.show_settings_dialog)
        
        # Audio settings
        audio_action = settings_menu.addAction(" Cài đặt âm thanh")
        audio_action.triggered.connect(self.show_audio_dialog)
        
        # Logout
        logout_action = settings_menu.addAction(" Đăng xuất")
        logout_action.triggered.connect(self.logout)
        
        # Usage history
        history_action = settings_menu.addAction(" Lịch sử dụng")
        history_action.triggered.connect(self.show_history_dialog)
        
        # Set menu bar
        self.setMenuBar(menubar)
    
    def show_settings_dialog(self):
        """Hiển thị dialog cài đặt hệ thống"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🔧 Tùy chỉnh hệ thống")
        dialog.setFixedSize(450, 400)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #1a1f2a, stop:1 #2a2f3a);
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
                padding: 5px;
            }
            QCheckBox {
                color: #e0e0e0;
                font-size: 12px;
                padding: 5px;
            }
            QSpinBox {
                background: rgba(30, 35, 50, 90);
                border: 1px solid rgba(0, 255, 170, 40);
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
                font-size: 12px;
            }
            QSlider {
                min-height: 20px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(39, 174, 96, 0.8), stop:1 rgba(34, 153, 84, 0.8));
                border: 2px solid rgba(39, 174, 96, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 16px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Auto start assistant
        auto_start_cb = QCheckBox("🚀 Tự động khởi động assistant")
        auto_start_cb.setChecked(True)
        
        # Assistant delay
        delay_layout = QHBoxLayout()
        delay_label = QLabel("⏱️ Thời gian trễ (ms):")
        delay_spin = QSpinBox()
        delay_spin.setRange(100, 5000)
        delay_spin.setValue(1000)
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(delay_spin)
        delay_layout.addStretch()
        
        # Speech recognition
        speech_cb = QCheckBox("🎤 Nhận dạng giọng nói")
        speech_cb.setChecked(True)
        
        # Text to speech
        tts_cb = QCheckBox("🔊 Đọc văn bản thành giọng nói")
        tts_cb.setChecked(True)
        
        # Volume
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊 Âm lượng:")
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(80)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(volume_slider)
        volume_layout.addStretch()
        
        # Speech rate
        rate_layout = QHBoxLayout()
        rate_label = QLabel("⚡ Tốc độ nói:")
        rate_spin = QSpinBox()
        rate_spin.setRange(50, 200)
        rate_spin.setValue(100)
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(rate_spin)
        rate_layout.addStretch()
        
        # Add widgets to layout
        layout.addWidget(auto_start_cb)
        layout.addLayout(delay_layout)
        layout.addWidget(speech_cb)
        layout.addWidget(tts_cb)
        layout.addLayout(volume_layout)
        layout.addLayout(rate_layout)
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Lưu")
        cancel_btn = QPushButton("❌ Hủy")
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Handle buttons
        def save_settings():
            QMessageBox.information(dialog, "Thành công", "Đã lưu cài đặt!")
            dialog.accept()
        
        save_btn.clicked.connect(save_settings)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def show_audio_dialog(self):
        """Hiển thị dialog cài đặt âm thanh"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Âm thanh")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #1a1f2a, stop:1 #2a2f3a);
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
                padding: 5px;
            }
            QSlider {
                min-height: 20px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(243, 156, 18, 0.8), stop:1 rgba(230, 126, 34, 0.8));
                border: 2px solid rgba(243, 156, 18, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 16px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Volume
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊 Âm lượng chính:")
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(80)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(volume_slider)
        volume_layout.addStretch()
        
        # Speech rate
        rate_layout = QHBoxLayout()
        rate_label = QLabel("⚡ Tốc độ nói:")
        rate_spin = QSpinBox()
        rate_spin.setRange(50, 200)
        rate_spin.setValue(100)
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(rate_spin)
        rate_layout.addStretch()
        
        # Add widgets
        layout.addLayout(volume_layout)
        layout.addLayout(rate_layout)
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Lưu")
        cancel_btn = QPushButton("❌ Hủy")
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Handle buttons
        def save_audio():
            QMessageBox.information(dialog, "Thành công", "Đã lưu cài đặt âm thanh!")
            dialog.accept()
        
        save_btn.clicked.connect(save_audio)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def logout(self):
        """Đăng xuất người dùng hiện tại"""
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn đăng xuất?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Thành công", "Đã đăng xuất thành công!")
            self.close()
    
    def show_history_dialog(self):
        """Hiển thị dialog lịch sử sử dụng"""
        dialog = QDialog(self)
        dialog.setWindowTitle("📜 Lịch sử sử dụng")
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #1a1f2a, stop:1 #2a2f3a);
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
                padding: 5px;
            }
            QTextEdit {
                background: rgba(30, 35, 50, 90);
                border: 1px solid rgba(0, 255, 170, 40);
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
                font-size: 11px;
                font-family: 'Consolas', monospace;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(39, 174, 96, 0.8), stop:1 rgba(34, 153, 84, 0.8));
                border: 2px solid rgba(39, 174, 96, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 16px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        title = QLabel("📜 Lịch sử sử dụng gần đây")
        title.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                               stop:0 #00ffaa, stop:1 #00ccff);
                font-size: 16px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                text-align: center;
                padding: 15px;
            }
        """)
        layout.addWidget(title)
        
        # History text
        history_text = QTextEdit()
        history_text.setReadOnly(True)
        
        # Load usage history (demo data)
        history_data = [
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Đăng nhập thành công",
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Mở cài đặt hệ thống",
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sử dụng tính năng chat",
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Truy cập admin panel"
        ]
        
        history_text.setText("\n".join(history_data))
        layout.addWidget(history_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        clear_btn = QPushButton("🗑️ Xóa lịch")
        close_btn = QPushButton("❌ Đóng")
        
        button_layout.addStretch()
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        # Handle buttons
        def clear_history():
            history_text.clear()
            QMessageBox.information(dialog, "Thành công", "Đã xóa lịch sử sử dụng!")
        
        clear_btn.clicked.connect(clear_history)
        close_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
        
        print("PopView initialized successfully")
    
    def setup_ui(self):
        """Create all UI elements"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set elegant dark background with subtle gradient
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #0f0f1a, stop:1 #1a1a2a);
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Elegant title
        self.status_label = QLabel("Pop Assistant")
        self.status_label.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                               stop:0 #00ffaa, stop:1 #00ccff);
                background: transparent;
                font-size: 32px;
                font-weight: 200;
                font-family: 'Segoe UI Light';
                text-align: center;
                padding: 10px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Enhanced sound wave widget with subtle border
        self.sound_wave_widget = SoundWaveWidget()
        self.sound_wave_widget.setStyleSheet("""
            SoundWaveWidget {
                background: rgba(0, 20, 40, 30);
                border: 1px solid rgba(0, 255, 136, 20);
                border-radius: 15px;
            }
        """)
        main_layout.addWidget(self.sound_wave_widget)
        
        # Elegant conversation display
        self.user_text_label = QLabel("")
        self.user_text_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 220);
                background: rgba(255, 255, 255, 5);
                border: 1px solid rgba(255, 255, 255, 10);
                border-radius: 10px;
                font-size: 16px;
                font-family: 'Segoe UI';
                padding: 15px;
                text-align: center;
            }
        """)
        self.user_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_text_label.setWordWrap(True)
        main_layout.addWidget(self.user_text_label)
        
        self.bot_text_label = QLabel("Sẵn sàng...")
        self.bot_text_label.setStyleSheet("""
            QLabel {
                color: rgba(0, 255, 200, 220);
                background: rgba(0, 255, 136, 5);
                border: 1px solid rgba(0, 255, 136, 20);
                border-radius: 10px;
                font-size: 16px;
                font-family: 'Segoe UI';
                padding: 15px;
                text-align: center;
            }
        """)
        self.bot_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bot_text_label.setWordWrap(True)
        main_layout.addWidget(self.bot_text_label)
        
        # Add stretch for centering
        main_layout.addStretch()
        
        # Add menu button in corner
        self.menu_btn = QPushButton("⋮")
        self.menu_btn.setFixedSize(35, 35)
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 136, 10);
                border: 1px solid rgba(0, 255, 136, 25);
                border-radius: 17px;
                color: #00ff88;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(0, 255, 136, 25);
                border: 1px solid rgba(0, 255, 136, 50);
            }
            QPushButton:pressed {
                background: rgba(0, 255, 136, 35);
            }
        """)
        self.menu_btn.clicked.connect(self.show_menu)
        
        # Position button in top-right corner
        self.menu_btn.setParent(central_widget)
        self.update_menu_button_position()
        
        # Create menu
        self.create_menu()
    
    def setup_animation(self):
        """Setup animation timer"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 20 FPS
    
    def update_animation(self):
        """Update the sound wave animation"""
        if hasattr(self, 'sound_wave_widget'):
            self.sound_wave_widget.update_animation()
    
    def load_user_name(self):
        """Load user name from JSON file"""
        try:
            if os.path.exists("user_data.json"):
                with open("user_data.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_name = data.get('name', 'ban')
                    # Avoid printing Unicode characters to console
                    try:
                        print(f"Loaded user name: {self.user_name}")
                    except UnicodeEncodeError:
                        print("Loaded user name: [Unicode content]")
        except Exception as e:
            try:
                print(f"Error loading user name: {e}")
            except UnicodeEncodeError:
                print("Error loading user name: [Unicode error]")
            self.user_name = "ban"
    
    def save_user_name(self, name):
        """Save user name to JSON file"""
        try:
            data = {'name': name}
            with open("user_data.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            try:
                print(f"Saved user name: {name}")
            except UnicodeEncodeError:
                print("Saved user name: [Unicode content]")
        except Exception as e:
            try:
                print(f"Error saving user name: {e}")
            except UnicodeEncodeError:
                print("Error saving user name: [Unicode error]")
    
    def speak_ui(self, text):
        """UI wrapper for speak function"""
        try:
            # DEBUG: Print assistant response to console
            print(f"Bot: {text}")
            
            # Update UI to show speaking state
            self.bot_text_label.setText(text)
            
            if GTTS_AVAILABLE and PLAYSOUND_AVAILABLE:
                tts = gtts.gTTS(text=text, lang="vi", slow=False)
                tts.save("sound.mp3")
                playsound.playsound("sound.mp3", False)
                os.remove("sound.mp3")
            else:
                print("Audio libraries not available, text-only mode")
            
        except Exception as e:
            print(f"Lỗi phát âm thanh: {e}")
    
    def get_voice_ui(self):
        """UI wrapper for get_voice function"""
        try:
            # Update UI to show listening state
            self.user_text_label.setText("Đang lắng nghe...")
            
            if not SR_AVAILABLE:
                print("Speech recognition not available")
                self.user_text_label.setText("Speech recognition không khả dụng")
                return "..."
            
            # Call speech recognition with more error handling
            r = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    r.pause_threshold = 0.8
                    r.energy_threshold = 250
                    audio = r.listen(source, phrase_time_limit=6, timeout=8)
                
                text = r.recognize_google(audio, language="vi-VN")
                
                # DEBUG: Print user input to console
                print(f"User: {text}")
                
                return text
                if text:
                    self.user_text_label.setText(text)
                    return text
                else:
                    self.user_text_label.setText("Không nhận được giọng nói...")
                    return "..."
            except sr.UnknownValueError:
                self.user_text_label.setText("Pop không nghe rõ...")
                return "..."
            except sr.RequestError as e:
                self.user_text_label.setText("Lỗi nhận diện giọng nói")
                try:
                    print(f"Speech recognition error: {e}")
                except UnicodeEncodeError:
                    print("Speech recognition error: [Unicode error]")
                return "..."
            except sr.RequestError as e:
                self.user_text_label.setText("Lỗi microphone")
                print(f"Microphone error: {e}")
                return "..."
            
        except Exception as e:
            print(f"Lỗi microphone: {e}")
            self.user_text_label.setText("Lỗi microphone")
            return "..."
    
    def classify_intent_simple(self, text):
        """Simple intent classification without AI"""
        text_lower = text.lower()
        
        # Time/Date intents
        time_keywords = ["mấy giờ", "mấy giời", "bao nhiêu giờ", "bây giờ là mấy giờ", "nay là ngày mấy", "hôm nay ngày", "thứ mấy", "hiện tại là ngày", "mấy ngày", "giờ mấy rồi"]
        for keyword in time_keywords:
            if keyword in text_lower:
                return "time"
        
        # Weather intents
        weather_keywords = ["thời tiết", "thoi tiet", "nhiệt độ", "trời", "mưa", "nắng", "celsius", "fahrenheit"]
        for keyword in weather_keywords:
            if keyword in text_lower:
                return "weather"
        
        # Greeting intents
        greeting_keywords = ["xin chào", "chào bạn", "hello", "hi", "chào"]
        for keyword in greeting_keywords:
            if keyword in text_lower:
                return "greeting"
        
        # Search intents
        search_keywords = ["tìm kiếm", "tra cứu", "tìm trên google", "search google", "tìm kiếm trên google", "tìm", "search"]
        for keyword in search_keywords:
            if keyword in text_lower:
                return "search"
        
        # Open website intents
        open_keywords = ["mở", "truy cập", "mở trang web", "google", "youtube", "facebook"]
        for keyword in open_keywords:
            if keyword in text_lower:
                return "open_website"
        
        # Goodbye intents
        goodbye_keywords = ["tạm biệt", "hẹn gặp lại", "bye", "dừng", "thôi", "tắt", "tắt hệ thống", "kết thúc", "close"]
        for keyword in goodbye_keywords:
            if keyword in text_lower:
                return "goodbye"
        
        return "unknown"
    
    def handle_intent_simple(self, intent, name, text):
        """Simple intent handling without AI"""
        if intent == "greeting":
            return f"Chào {name}, tôi là Pop. Bạn cần tôi giúp gì?"
        
        elif intent == "time":
            # Get current time and date
            import datetime
            
            try:
                now = datetime.datetime.now()
                
                content = f"""Bây giờ là {now.hour} giờ {now.minute} phút
Hôm nay là ngày {now.day} tháng {now.month} năm {now.year}
Thứ hôm nay là {now.strftime('%A')}"""
                
                # Speak và chờ user nghe xong
                self.speak_ui(content)
                time.sleep(5)  # Chờ 5 giây để user nghe xong
                return content
                
            except Exception as e:
                return "Xin lỗi, tôi không thể lấy thông tin thời gian ngay bây giờ."
        
        elif intent == "weather":
            # Exact copy of your working weather function
            import requests
            import datetime
            
            try:
                # Hỏi địa điểm trước
                self.speak_ui("Bạn muốn xem thời tiết ở đâu ạ!")
                time.sleep(3)
                
                # Lấy địa điểm từ user
                city = self.get_text_ui()
                if not city:
                    self.speak_ui("Không có thành phố nào được cung cấp!")
                    return
                
                # Gọi API
                api_key = "fe8d8c65cf345889139d8e545f57819a"
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                response = requests.get(url)
                data = response.json()
                
                if data["cod"] != "404":
                    city_res = data["main"]
                    current_temp = city_res["temp"]
                    current_pressure = city_res["pressure"]
                    current_humidity = city_res["humidity"]
                    sun_time  = data["sys"]
                    sun_rise = datetime.datetime.fromtimestamp(sun_time["sunrise"])
                    sun_set = datetime.datetime.fromtimestamp(sun_time["sunset"])
                    weather_desc = data["weather"][0]["description"]
                    now = datetime.datetime.now()
                    content = f"""
        Hôm nay là ngày {now.day} tháng {now.month} năm {now.year}
        Mặt trời mọc vào {sun_rise.hour} giờ {sun_rise.minute} phút
        Mặt trời lặn vào {sun_set.hour} giờ {sun_set.minute} phút
        Nhiệt độ trung bình là {current_temp} độ C
        Áp suất không khí là {current_pressure} hPa
        Độ ẩm là {current_humidity}%.
        Trời hôm nay {weather_desc}.
        """
                    self.speak_ui(content)
                    time.sleep(25)  
                    return content
                else:
                    self.speak_ui("Không tìm thấy thành phố!")
                    return "Không tìm thấy thành phố!"
                    
            except Exception as e:
                return "Xin lỗi, tôi không thể lấy thông tin thời tiết ngay bây giờ."
        
        elif intent == "search":
            # Extract search query
            import re
            patterns = [
                r"(?:tìm kiếm|tra cứu|tìm trên google|search google|tìm kiếm trên google)\s+(.+)",
                r"(?:tôi muốn tìm|tìm giúp tôi)\s+(.+)",
                r"(?:tìm|search)\s+(.+)"
            ]
            
            search_query = None
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    search_query = match.group(1).strip()
                    # Remove command words
                    search_query = re.sub(r'\b(tìm kiếm|tra cứu|tìm trên google|search google|tìm kiếm trên google|tôi muốn tìm|tìm giúp tôi|tìm|search)\s*', '', search_query, flags=re.IGNORECASE)
                    break
            
            if search_query:
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
                return f"Tôi đã tìm kiếm {search_query} trên Google."
            else:
                return "Xin lỗi, tôi không hiểu bạn muốn tìm kiếm gì."
        
        elif intent == "open_website":
            # Extract domain
            import re
            domain_match = re.search(r"(?:mở|truy cập)\s+(?:trang web)?\s*(\S+)", text, re.IGNORECASE)
            if domain_match:
                domain = domain_match.group(1).strip().lower()
                
                # Common domains
                if domain == "google":
                    domain = "google.com"
                elif domain == "youtube":
                    domain = "youtube.com"
                elif domain == "facebook":
                    domain = "facebook.com"
                
                if not domain.startswith("http"):
                    url = f"https://{domain}"
                else:
                    url = domain
                
                webbrowser.open(url)
                return f"Tôi đã mở trang web {domain} cho bạn."
            else:
                return "Tôi không thể xác định trang web bạn muốn mở."
        
        elif intent == "goodbye":
            return "Hẹn gặp lại bạn! Chúc bạn một ngày tốt lành."
        
        else:
            return "Xin lỗi, tôi không hiểu lệnh của bạn. Bạn có thể nói rõ hơn không?"
    
        
    def start_assistant_thread(self):
        """Start assistant in background thread"""
        if not self.assistant_started:
            self.assistant_started = True
            self.assistant_active = True
            self.assistant_thread = threading.Thread(target=self._run_assistant_logic, daemon=True)
            self.assistant_thread.start()
        else:
            # Assistant was started before but is now inactive, allow restart
            self.status_label.setText("Đang khởi động lại...")
            self.assistant_active = True
            threading.Thread(target=self._run_assistant_logic, daemon=True).start()
    
    def _run_assistant_logic(self):
        """Main assistant logic loop"""
        try:
            # Start new session
            self.current_session_id = self.db.start_session(self.user_name)
            
            # DEBUG: Print session start
            print(f"Session: {self.user_name}")
            
            # Check if we already know user's name
            if self.user_name != "bạn":
                welcome_msg = f"Chào mừng trở lại {self.user_name}!"
                self.speak_ui(welcome_msg)
                self.db.save_conversation(self.user_name, "(session_start)", welcome_msg, self.current_session_id)
                time.sleep(1.3)
            else:
                # First time, ask for name
                self.speak_ui(f"Xin chào, tôi là {self.assistant_name}. Bạn tên là gì nhỉ?")
                name_input = self.get_text_ui()
                if name_input and name_input != "...":
                    self.user_name = name_input
                    self.save_user_name(name_input)
                    welcome_msg = f"Chào bạn {self.user_name}."
                    self.speak_ui(welcome_msg)
                    self.db.save_conversation(self.user_name, f"Tên tôi là {name_input}", welcome_msg, self.current_session_id)
                else:
                    self.speak_ui(f"Tôi không nghe rõ tên bạn. Chúng ta sẽ bắt đầu lại khi bạn nhấn mic.")
                    self.assistant_active = False
                    return
            
            # Main interaction loop
            while self.assistant_active:
                # Kiểm tra lại assistant_active trước khi speak
                if not self.assistant_active:
                    break
                    
                self.speak_ui("Bạn cần tôi làm gì?")
                time.sleep(1)
                
                # Kiểm tra lại sau sleep
                if not self.assistant_active:
                    break
                
                text = self.get_voice_ui()
                
                if not text or text == 0:
                    self.assistant_active = False
                    break
                
                # Kiểm tra lại trước khi xử lý
                if not self.assistant_active:
                    break
                
                # Call simple intent classification
                intent = self.classify_intent_simple(text)
                response = self.handle_intent_simple(intent, self.user_name, text)
                
                # DEBUG: Print intent classification
                print(f"Intent: {intent}")
                
                if response:
                    self.bot_text_label.setText(response)
                    self.speak_ui(response)
                    
                    # Save conversation to database
                    self.db.save_conversation(self.user_name, text, response, self.current_session_id)
                    
                    # Trigger goodbye
                    if intent == "goodbye":
                        print(f"Session end")
                        self.db.end_session(self.current_session_id)
                        QTimer.singleShot(2000, self.close)  # Auto-close after goodbye
                
                # Add delay between interactions to prevent rapid cycling
                time.sleep(1)
            
            # Final goodbye message after loop ends
        except Exception as e:
            print(f"Lỗi trong assistant logic: {e}")
            self.assistant_active = False
    
    def get_text_ui(self):
        """Get text with retry logic"""
        for i in range(3):
            text = self.get_voice_ui()
            if text and text != 0 and text != "...":
                return text.lower()
            elif i < 2:
                self.speak_ui(f"{self.assistant_name} không nghe rõ, bạn có thể nói lại không?")
        self.speak_ui("Tạm biệt!")
        self.close()  # Auto-close when assistant ends
        return 0
    
    def create_menu(self):
        """Tạo menu với 3 lựa chọn"""
        self.menu = QMenu(self)
        self.menu.setStyleSheet("""
            QMenu {
                background: rgba(20, 20, 35, 200);
                border: 1px solid rgba(0, 255, 136, 40);
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                background: transparent;
                color: #00ffaa;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: 600;
            }
            QMenu::item:selected {
                background: rgba(0, 255, 136, 30);
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background: rgba(0, 255, 136, 20);
                margin: 5px 10px;
            }
        """)
        
        # Thêm các hành động (không icon)
        personal_action = QAction("Cá nhân", self)
        personal_action.triggered.connect(self.show_personal_info)
        self.menu.addAction(personal_action)
        
        settings_action = QAction("Cài đặt", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        self.menu.addAction(settings_action)
        
        audio_action = QAction("Âm thanh", self)
        audio_action.triggered.connect(self.show_audio_dialog)
        self.menu.addAction(audio_action)
        
        history_action = QAction("Lịch sử trò chuyện", self)
        history_action.triggered.connect(self.show_history_dialog)
        self.menu.addAction(history_action)
        
        self.menu.addSeparator()
        
        signout_action = QAction("Sign out", self)
        signout_action.triggered.connect(self.sign_out)
        self.menu.addAction(signout_action)
    
    def show_menu(self):
        """Hiển thị menu tại vị trí nút"""
        if hasattr(self, 'menu_btn') and hasattr(self, 'menu'):
            # Lấy vị trí của nút
            btn_pos = self.menu_btn.mapToGlobal(QPoint(0, 0))
            # Hiển thị menu bên dưới nút
            menu_x = btn_pos.x() + self.menu_btn.width() - self.menu.sizeHint().width()
            menu_y = btn_pos.y() + self.menu_btn.height() + 5
            self.menu.exec(QPoint(menu_x, menu_y))
    
    def update_menu_button_position(self):
        """Cập nhật vị trí nút menu ở góc trên bên phải"""
        if hasattr(self, 'menu_btn'):
            self.menu_btn.move(self.width() - 45, 15)
    
    def show_settings_dialog(self):
        """Hiển thị dialog cài đặt hệ thống"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Cài đặt")
        dialog.setFixedSize(450, 400)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #1a1f2a, stop:1 #2a2f3a);
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
                padding: 5px;
            }
            QCheckBox {
                color: #e0e0e0;
                font-size: 12px;
                padding: 5px;
            }
            QSpinBox {
                background: rgba(30, 35, 50, 90);
                border: 1px solid rgba(0, 255, 170, 40);
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
                font-size: 12px;
            }
            QSlider {
                min-height: 20px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(39, 174, 96, 0.8), stop:1 rgba(34, 153, 84, 0.8));
                border: 2px solid rgba(39, 174, 96, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 16px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Auto start assistant
        auto_start_cb = QCheckBox("🚀 Tự động khởi động assistant")
        auto_start_cb.setChecked(True)
        
        # Assistant delay
        delay_layout = QHBoxLayout()
        delay_label = QLabel("⏱️ Thời gian trễ (ms):")
        delay_spin = QSpinBox()
        delay_spin.setRange(100, 5000)
        delay_spin.setValue(1000)
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(delay_spin)
        delay_layout.addStretch()
        
        # Speech recognition
        speech_cb = QCheckBox("🎤 Nhận dạng giọng nói")
        speech_cb.setChecked(True)
        
        # Text to speech
        tts_cb = QCheckBox("🔊 Đọc văn bản thành giọng nói")
        tts_cb.setChecked(True)
        
        # Volume
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊 Âm lượng:")
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(80)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(volume_slider)
        volume_layout.addStretch()
        
        # Speech rate
        rate_layout = QHBoxLayout()
        rate_label = QLabel("⚡ Tốc độ nói:")
        rate_spin = QSpinBox()
        rate_spin.setRange(50, 200)
        rate_spin.setValue(100)
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(rate_spin)
        rate_layout.addStretch()
        
        # Add widgets to layout
        layout.addWidget(auto_start_cb)
        layout.addLayout(delay_layout)
        layout.addWidget(speech_cb)
        layout.addWidget(tts_cb)
        layout.addLayout(volume_layout)
        layout.addLayout(rate_layout)
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Lưu")
        cancel_btn = QPushButton("❌ Hủy")
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Handle buttons
        def save_settings():
            QMessageBox.information(dialog, "Thành công", "Đã lưu cài đặt!")
            dialog.accept()
        
        save_btn.clicked.connect(save_settings)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def show_audio_dialog(self):
        """Hiển thị dialog cài đặt âm thanh"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Âm thanh")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #1a1f2a, stop:1 #2a2f3a);
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
                padding: 5px;
            }
            QSlider {
                min-height: 20px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 rgba(243, 156, 18, 0.8), stop:1 rgba(230, 126, 34, 0.8));
                border: 2px solid rgba(243, 156, 18, 0.9);
                border-radius: 8px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 16px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Volume
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊 Âm lượng chính:")
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(80)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(volume_slider)
        volume_layout.addStretch()
        
        # Speech rate
        rate_layout = QHBoxLayout()
        rate_label = QLabel("⚡ Tốc độ nói:")
        rate_spin = QSpinBox()
        rate_spin.setRange(50, 200)
        rate_spin.setValue(100)
        rate_layout.addWidget(rate_label)
        rate_layout.addWidget(rate_spin)
        rate_layout.addStretch()
        
        # Add widgets
        layout.addLayout(volume_layout)
        layout.addLayout(rate_layout)
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Lưu")
        cancel_btn = QPushButton("❌ Hủy")
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Handle buttons
        def save_audio():
            QMessageBox.information(dialog, "Thành công", "Đã lưu cài đặt âm thanh!")
            dialog.accept()
        
        save_btn.clicked.connect(save_audio)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def show_personal_info(self):
        """Hiển thị thông tin cá nhân"""
        from PyQt6.QtWidgets import QMessageBox
        
        msg_box = QMessageBox(self)
        msg_box.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #0f0f1a, stop:1 #1a1a2a);
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background: rgba(0, 255, 136, 20);
                border: 1px solid rgba(0, 255, 136, 50);
                border-radius: 6px;
                padding: 8px 16px;
                color: #00ff88;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: rgba(0, 255, 136, 40);
            }
        """)
        
        # Lấy thống kê người dùng
        try:
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) as total_conversations,
                       COUNT(DISTINCT DATE(timestamp)) as total_days,
                       COUNT(DISTINCT session_id) as total_sessions
                FROM conversations 
                WHERE user_name = ?
            """, (self.user_name,))
            
            stats = cursor.fetchone()
            conn.close()
            
            info_text = f"""Tên người dùng: {self.user_name}

Thống kê sử dụng:
• Tổng số cuộc trò chuyện: {stats[0]}
• Số ngày sử dụng: {stats[1]}
• Số phiên trò chuyện: {stats[2]}
• Trung bình mỗi ngày: {stats[0]/max(stats[1], 1):.1f} cuộc

Phiên hiện tại: {self.current_session_id or 'Chưa bắt đầu'}

Ngày bắt đầu sử dụng: {self.get_first_use_date()}
"""
            
        except Exception as e:
            info_text = f"Tên người dùng: {self.user_name}\n\nKhông thể tải thống kê\nLỗi: {str(e)}"
        
        msg_box.setText(info_text)
        msg_box.exec()
    
    def get_first_use_date(self):
        """Lấy ngày đầu tiên sử dụng"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT MIN(timestamp) FROM conversations WHERE user_name = ?
            """, (self.user_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return result[0].replace('T', ' ')[:19]
            else:
                return "Chưa có dữ liệu"
        except:
            return "Không xác định"
    
    def sign_out(self):
        """Đăng xuất và đóng ứng dụng"""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 
            'Xác nhận đăng xuất',
            'Bạn có chắc chắn muốn đăng xuất?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Kết thúc phiên hiện tại
            if self.current_session_id:
                self.db.end_session(self.current_session_id)
            
            self.close()  # Đóng ứng dụng
    
    def resizeEvent(self, event):
        """Xử lý khi cửa sổ thay đổi kích thước"""
        super().resizeEvent(event)
        self.update_menu_button_position()
    
    def closeEvent(self, event):
        """Handle window close event"""
        print("Window closing - stopping assistant...")
        self.assistant_active = False
        
        # Đảm bảo assistant thread dừng hoàn toàn
        if hasattr(self, 'assistant_thread'):
            self.assistant_thread.join(timeout=2)
        
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
        
        # Database không cần close vì không có connection mở
        print("Assistant stopped successfully")
        super().closeEvent(event)
    
    def show_history(self):
        """Hiển thị cửa sổ lịch sử trò chuyện"""
        if self.history_widget is None:
            self.history_widget = HistoryWindow(self.db, self.user_name)
        self.history_widget.show()
        self.history_widget.raise_()
        self.history_widget.activateWindow()

class HistoryWindow(QMainWindow):
    def __init__(self, db, user_name):
        super().__init__()
        self.db = db
        self.user_name = user_name
        self.init_ui()
        self.load_statistics()
    
    def init_ui(self):
        """Khởi tạo giao diện lịch sử"""
        self.setWindowTitle("📚 Lịch sử trò chuyện - Pop Assistant")
        self.setGeometry(200, 200, 900, 700)
        
        # Set modern dark theme
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                               stop:0 #0f0f1a, stop:1 #1a1a2a);
            }
            QTabWidget::pane {
                border: 1px solid rgba(0, 255, 136, 30);
                background: rgba(20, 20, 35, 100);
                border-radius: 10px;
            }
            QTabBar::tab {
                background: rgba(0, 255, 136, 20);
                color: #00ff88;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: rgba(0, 255, 136, 40);
                border: 1px solid rgba(0, 255, 136, 60);
            }
            QListWidget {
                background: rgba(20, 20, 35, 200);
                border: 1px solid rgba(0, 255, 136, 30);
                border-radius: 10px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background: rgba(0, 255, 136, 30);
            }
            QTextEdit {
                background: rgba(25, 25, 45, 180);
                border: 1px solid rgba(0, 255, 136, 40);
                border-radius: 10px;
                padding: 15px;
                color: white;
                font-size: 14px;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QPushButton {
                background: rgba(0, 255, 136, 20);
                border: 1px solid rgba(0, 255, 136, 50);
                border-radius: 8px;
                padding: 8px 16px;
                color: #00ff88;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(0, 255, 136, 40);
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel(f"📚 Lịch sử trò chuyện của {self.user_name}")
        title.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                               stop:0 #00ffaa, stop:1 #00ccff);
                font-size: 20px;
                font-weight: 300;
                text-align: center;
                padding: 15px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: Thống kê
        self.stats_tab = QWidget()
        self.setup_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "📊 Thống kê")
        
        # Tab 2: Lịch sử chi tiết
        self.history_tab = QWidget()
        self.setup_history_tab()
        self.tab_widget.addTab(self.history_tab, "📝 Chi tiết")
        
        main_layout.addWidget(self.tab_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Làm mới")
        refresh_btn.clicked.connect(self.refresh_data)
        button_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("🗑️ Xóa cũ (>30 ngày)")
        clear_btn.clicked.connect(self.clear_old_data)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
    
    def setup_stats_tab(self):
        """Thiết lập tab thống kê"""
        layout = QVBoxLayout(self.stats_tab)
        
        # Statistics display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(200)
        layout.addWidget(self.stats_text)
        
        # Daily statistics list
        daily_label = QLabel("📅 Thống kê theo ngày:")
        daily_label.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        layout.addWidget(daily_label)
        
        self.daily_stats_list = QListWidget()
        layout.addWidget(self.daily_stats_list)
    
    def setup_history_tab(self):
        """Thiết lập tab lịch sử chi tiết"""
        layout = QHBoxLayout(self.history_tab)
        
        # Left side - Sessions list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        sessions_label = QLabel("📅 Các phiên trò chuyện:")
        sessions_label.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        left_layout.addWidget(sessions_label)
        
        self.sessions_list = QListWidget()
        self.sessions_list.itemClicked.connect(self.load_session_conversations)
        left_layout.addWidget(self.sessions_list)
        
        layout.addWidget(left_widget)
        
        # Right side - Conversation content
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        content_label = QLabel("💬 Nội dung trò chuyện:")
        content_label.setStyleSheet("""
            QLabel {
                color: #00ccff;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        right_layout.addWidget(content_label)
        
        self.conversation_text = QTextEdit()
        self.conversation_text.setReadOnly(True)
        right_layout.addWidget(self.conversation_text)
        
        layout.addWidget(right_widget)
    
    def load_statistics(self):
        """Tải thống kê"""
        try:
            # Get all conversations for statistics
            conn = self.db.db_path
            import sqlite3
            
            db_conn = sqlite3.connect(conn)
            cursor = db_conn.cursor()
            
            # Total statistics
            cursor.execute("""
                SELECT COUNT(*) as total_conversations,
                       COUNT(DISTINCT DATE(timestamp)) as total_days,
                       COUNT(DISTINCT session_id) as total_sessions
                FROM conversations 
                WHERE user_name = ?
            """, (self.user_name,))
            
            total_stats = cursor.fetchone()
            
            # Daily statistics
            cursor.execute("""
                SELECT DATE(timestamp) as date,
                       COUNT(*) as conversation_count,
                       COUNT(DISTINCT session_id) as session_count
                FROM conversations 
                WHERE user_name = ?
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 30
            """, (self.user_name,))
            
            daily_stats = cursor.fetchall()
            db_conn.close()
            
            # Display total statistics
            stats_text = f"""📊 Thống kê tổng quan:

• Tổng số cuộc trò chuyện: {total_stats[0]}
• Số ngày sử dụng: {total_stats[1]}
• Số phiên trò chuyện: {total_stats[2]}
• Trung bình mỗi ngày: {total_stats[0]/max(total_stats[1], 1):.1f} cuộc trò chuyện
"""
            
            self.stats_text.setPlainText(stats_text)
            
            # Display daily statistics
            self.daily_stats_list.clear()
            for date, conv_count, sess_count in daily_stats:
                item_text = f"📅 {date}: {conv_count} câu hỏi, {sess_count} phiên"
                item = QListWidgetItem(item_text)
                self.daily_stats_list.addItem(item)
                
        except Exception as e:
            print(f"Error loading statistics: {e}")
    
    def load_session_conversations(self, item):
        """Tải nội dung cuộc trò chuyện của phiên được chọn"""
        try:
            session_id = item.data(Qt.ItemDataRole.UserRole)
            conversations = self.db.get_session_conversations(session_id)
            
            content = f"📅 Phiên trò chuyện: {session_id}\n"
            content += "=" * 50 + "\n\n"
            
            for conv in conversations:
                user_msg, bot_response, timestamp = conv
                time_str = timestamp.replace('T', ' ')[:19] if timestamp else "Unknown"
                
                content += f"⏰ {time_str}\n"
                content += f"👤 Bạn: {user_msg}\n"
                content += f"🤖 Pop: {bot_response}\n"
                content += "-" * 30 + "\n\n"
            
            self.conversation_text.setPlainText(content)
            
        except Exception as e:
            print(f"Error loading conversations: {e}")
            self.conversation_text.setPlainText("Lỗi khi tải cuộc trò chuyện")
    
    def refresh_data(self):
        """Làm mới dữ liệu"""
        self.load_statistics()
        self.load_sessions()
        print("Data refreshed")
    
    def load_sessions(self):
        """Tải danh sách phiên"""
        try:
            sessions = self.db.get_all_sessions(self.user_name)
            
            self.sessions_list.clear()
            
            for session in sessions:
                session_id, start_time, end_time = session
                start_str = start_time.replace('T', ' ')[:19] if start_time else "Unknown"
                end_str = end_time.replace('T', ' ')[:19] if end_time else "Đang hoạt động"
                
                item_text = f"📝 {start_str} - {end_str}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, session_id)
                self.sessions_list.addItem(item)
                
        except Exception as e:
            print(f"Error loading sessions: {e}")
    
    def clear_old_data(self):
        """Xóa dữ liệu cũ"""
        try:
            self.db.delete_old_conversations(30)
            self.refresh_data()
            print("Old conversations deleted")
        except Exception as e:
            print(f"Error deleting old data: {e}")
