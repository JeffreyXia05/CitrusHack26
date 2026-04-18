import random
from google import genai # Updated import
from google.genai import types # Needed for system instructions
from PyQt6.QtWidgets import QWidget, QLabel, QApplication, QLineEdit
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QFont

from states import load_states
from behavior import update_behavior
from encouragement import EncouragementSystem

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        self.frame_counter = 0
        self.frame_index = 0
        self.last_speak_state = None
        self.current_encouragement = None

        self.setup_window()
        self.setup_states()
        self.setup_sprite()
        self.setup_systems()  # Fixed: No longer contains nested functions
        self.setup_text_bubble()
        self.setup_timers()
        self.setup_interaction()

    # -------------------------
    # SYSTEMS
    # -------------------------
    def setup_systems(self):
        import os
        from dotenv import load_dotenv
        load_dotenv()
        # Configure Gemini
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
        )
        # 2. Define the persona using a Config object
        self.chat_config = types.GenerateContentConfig(
            system_instruction="You are a digital cat. You start by giving encouragement. "
                               "If the user talks back, be a cat: use puns, 'meow', and stay brief."
        )
        
        # 3. Start the chat session
        self.chat_session = self.client.chats.create(model="gemini-2.5-flash-lite", config=self.chat_config)
        
        self.encouragement = EncouragementSystem(self)
    

    # -------------------------
    # WINDOW
    # -------------------------
    def setup_window(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def setup_states(self):
        self.states = load_states()
        self.current_state = "idle"
        self.dx = 0
        self.dy = 0
        self.state_timer = 0
        self.state_duration = random.randint(120, 300)

    def set_state(self, new_state):
        if self.current_state == "speak" and new_state != "speak":
            self.text_bubble.hide()
            self.chat_input.hide() # Added: Hide input when leaving speak state
            self.current_encouragement = None
            self.last_speak_state = None
            
        if new_state not in self.states:
            return

        if self.current_state != new_state:
            self.current_state = new_state
            self.frame_index = 0
            self.frame_counter = 0
            self.state_timer = 0

            if new_state == "idle":
                self.state_duration = random.randint(180, 420)
            elif new_state == "walk":
                self.state_duration = random.randint(60, 300)
                self.MAX_SPEED = 3
                self.dx = random.randint(-self.MAX_SPEED, self.MAX_SPEED)
                self.dy = random.randint(-self.MAX_SPEED, self.MAX_SPEED)
            elif new_state == "speak":
                self.state_duration = random.randint(150, 300) # Slightly longer for chat
                self.encouragement.trigger()

    def setup_sprite(self):
        self.label = QLabel(self)
        self.update_appearance()
        screen = QApplication.primaryScreen().geometry()
        center_x = (screen.width() - self.label.width()) // 2
        center_y = (screen.height() - self.label.height()) // 2
        self.label.move(center_x, center_y)

    def setup_timers(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

    def tick(self):
        update_behavior(self)
        self.update_appearance()

    def update_appearance(self):
        state_data = self.states.get(self.current_state)
        if not state_data: return

        frames = state_data["frames"]
        pixmap = frames[self.frame_index]
        scaled = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.label.setPixmap(scaled)
        self.label.resize(scaled.size())

        self.frame_counter += 1
        fps = state_data.get("fps", 2)
        if self.frame_counter >= (60 // fps):
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(frames)

    # -------------------------
    # CHAT UI
    # -------------------------
    def setup_text_bubble(self):
        self.text_bubble = QLabel(self)
        self.text_bubble.setWordWrap(True)
        self.text_bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_bubble.setFont(QFont("Arial", 10))
        self.text_bubble.setStyleSheet(
            "color: black; background-color: rgba(255,255,255,0.9); "
            "border-radius: 10px; padding: 5px;"
        )
        self.text_bubble.hide()

        self.chat_input = QLineEdit(self)
        self.chat_input.setPlaceholderText("Reply...")
        self.chat_input.setStyleSheet("background: white; border: 1px solid #ccc; border-radius: 5px;")
        self.chat_input.setFixedWidth(120)
        self.chat_input.hide()
        self.chat_input.returnPressed.connect(self.handle_chat_input)

    def handle_chat_input(self):
        user_text = self.chat_input.text()
        if not user_text: return
        
        self.chat_input.clear()
        self.show_encouragement("...") 
        
        # 4. Use the new send_message syntax
        try:
            response = self.chat_session.send_message(user_text)
            # Accessing the text via .text attribute
            self.show_encouragement(response.text)
        except Exception as e:
            print(f"Error: {e}")
            self.show_encouragement("Meow... (Something went wrong with my brain!)")

    def show_encouragement(self, text):
        self.text_bubble.setText(text)
        self.text_bubble.adjustSize()
        
        # Position bubble above the cat
        self.text_bubble.move(
            self.label.x(),
            self.label.y() - self.text_bubble.height() - 10
        )
        self.text_bubble.show()

        # Position input below the bubble
        self.chat_input.move(self.label.x(), self.label.y() + self.label.height() + 5)
        self.chat_input.show()
        self.chat_input.setFocus()

    # -------------------------
    # INTERACTION
    # -------------------------
    def setup_interaction(self):
        self.dragging = False
        self.offset = QPoint()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.label.geometry().contains(event.pos()):
                self.dragging = True
                self.offset = event.pos() - self.label.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.pos() - self.offset
            x = max(0, min(new_pos.x(), self.width() - self.label.width()))
            y = max(0, min(new_pos.y(), self.height() - self.label.height()))
            self.label.move(x, y)
            # Update bubble position while dragging
            if self.text_bubble.isVisible():
                self.show_encouragement(self.text_bubble.text())

    def mouseReleaseEvent(self, event):
        self.dragging = False