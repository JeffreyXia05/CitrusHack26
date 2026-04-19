import random
from google import genai
from google.genai import types # Needed for system instructions
from PyQt6.QtWidgets import QWidget, QLabel, QApplication, QLineEdit, QPushButton
from PyQt6.QtCore import Qt, QEvent, QPoint, QTimer
from PyQt6.QtGui import QFont

from pynput import mouse as pynput_mouse
from pynput import keyboard as pynput_keyboard

from states import load_states
from behavior import update_behavior
from encouragement import EncouragementSystem

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        # 1. Initialize basic variables first
        self.frame_counter = 0
        self.frame_index = 0
        self.last_speak_state = None
        self.current_encouragement = None
        self.inactivity_timer = 0
        self.INACTIVITY_LIMIT = 30 * 60 
        self.dragging = False  # Ensure this exists early

        # 2. Setup DATA (This must come before visuals)
        self.setup_states()    # This creates self.states and self.current_state

        # 3. Setup VISUALS (Now update_appearance will work)
        self.setup_sprite()    # Creates self.label and calls update_appearance
        self.setup_window()    # Configures the window and mouse tracking
        
        # 4. Setup EVERYTHING ELSE
        self.setup_systems()  # Fixed: No longer contains nested functions
        self.setup_text_bubble()
        self.setup_timers()
        self.setup_interaction()
        
        self.installEventFilter(self)
        self.setup_global_listeners() 

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
        self.setMouseTracking(True)  # Add this
        self.label.setMouseTracking(True) # And this for the sprite label
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.label.setMouseTracking(True)
    # -------------------------
    # STATES
    # -------------------------
    def setup_states(self):
        self.states = load_states()
        self.current_state = "idle"
        self.dx = 0
        self.dy = 0
        self.state_timer = 0
        self.state_duration = random.randint(120, 300)  # frames (2–5 sec at 60fps approx)
        self.current_state = "idle"

    def set_state(self, new_state):
        if self.current_state == "speak" and new_state != "speak":
            self.text_bubble.hide()
            self.chat_input.hide() 
            self.reply_button.hide()
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
            elif new_state == "sleep":
                self.state_duration = 999999 # Stay asleep until woken up
                if hasattr(self, 'text_bubble'):
                    self.text_bubble.hide()

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

    # =========================
    # SLEEP RELATED
    # =========================

    def on_global_input(self, *args):
        # This is called whenever ANYTHING happens on the computer
        # Since this runs in a background thread, we reset the timer safely
        self.inactivity_timer = 0
        
        # If the pet is sleeping, we need to wake it up
        # Note: We don't change UI here directly because this is a different thread
        # The tick() function will handle the state switch next frame

    def eventFilter(self, obj, event):
        # Detect Mouse Movement, Clicks, or Keyboard Presses
        if event.type() in [
            QEvent.Type.MouseMove, 
            QEvent.Type.MouseButtonPress, 
            QEvent.Type.KeyPress
        ]:
            self.wake_up()
        
        return super().eventFilter(obj, event)

    def setup_global_listeners(self):
        # Ensure these names match what is in closeEvent
        self.m_listener = pynput_mouse.Listener(on_move=lambda x, y: self.wake_up())
        self.k_listener = pynput_keyboard.Listener(on_press=lambda key: self.wake_up())
        
        self.m_listener.start()
        self.k_listener.start()

    def wake_up(self):
        # This resets the timer. The tick() function will see this 
        # and change the state from "sleep" to "idle" automatically.
        self.inactivity_timer = 0

    def tick(self):
        # 1. Increment inactivity timer
        if not self.dragging:
            self.inactivity_timer += 1

        # 2. Check for Sleep Trigger
        if self.inactivity_timer >= self.INACTIVITY_LIMIT:
            if self.current_state != "sleep":
                self.set_state("sleep")
        else:
            # If the timer was reset by global input, wake up!
            if self.current_state == "sleep":
                self.set_state("idle")

        # 3. Process Behavior (Only if not sleeping)
        if self.current_state != "sleep":
            update_behavior(self)
            
        # 4. Final Visual Render
        self.update_appearance()

    def closeEvent(self, event):
        # Check if they exist before stopping to prevent errors on early exit
        if hasattr(self, 'm_listener'):
            self.m_listener.stop()
        if hasattr(self, 'k_listener'):
            self.k_listener.stop()
        event.accept()
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

        # Reply Button
        self.reply_button = QPushButton("Reply", self)
        self.reply_button.setFixedWidth(60)
        self.reply_button.setStyleSheet(
            "background-color: #eee; color: black; border-radius: 5px; font-size: 10px;"
        )
        self.reply_button.hide()
        self.reply_button.clicked.connect(self.show_chat_input)

        self.chat_input = QLineEdit(self)
        self.chat_input.setPlaceholderText("Reply...")
        self.chat_input.setStyleSheet("background: white; color: black; border: 1px solid #ccc; border-radius: 5px;")
        self.chat_input.setFixedWidth(120)
        self.chat_input.hide()
        self.chat_input.returnPressed.connect(self.handle_chat_input)

    def show_chat_input(self):
        """Swaps the reply button for the text box."""
        self.reply_button.hide()
        self.chat_input.show()
        self.chat_input.setFocus()

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

        self.reply_button.move(
            self.label.x() + (self.label.width() // 2) - 30,
            self.label.y() - 10 
        )
        self.reply_button.show()
        
        # Ensure input box is hidden initially
        self.chat_input.hide()

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