import random
from google import genai
from google.genai import types
import math
from PyQt6.QtWidgets import QWidget, QLabel, QApplication, QLineEdit, QPushButton
from PyQt6.QtCore import Qt, QEvent, QPoint, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont, QCursor
from windows import get_windows, get_window_under_pet, get_window_center 


from pynput import mouse as pynput_mouse
from pynput import keyboard as pynput_keyboard

from states import load_states
from behavior import update_behavior
from encouragement import EncouragementSystem

class DesktopPet(QWidget):
    def __init__(self, option):
        super().__init__()

        # 1. Initialize basic variables first
        self.frame_counter = 0
        self.frame_index = 0
        self.last_speak_state = None
        self.current_encouragement = None
        self.inactivity_timer = 0
        self.INACTIVITY_LIMIT = 30 * 60 
        self.dragging = False  # Ensure this exists early
        self.option = option

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

        self.last_mouse_pos = QPoint(0, 0)
        self.mouse_velocity = 0
        self.is_squished = False
        self.squish_factor = 1.0  # 1.0 = normal, 0.8 = squished
        self.target_x = 0
        self.target_y = 0

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

        # Updated Flags for "True" Always-on-top behavior
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |      # Removes title bar
            Qt.WindowType.WindowStaysOnTopHint |     # Forces to front
            Qt.WindowType.SubWindow |                # Helps on some Linux distros
            Qt.WindowType.X11BypassWindowManagerHint | # For Linux/X11
            Qt.WindowType.Window                        # Hides from Taskbar + stays afloat
        )
        
        # This attribute is crucial for transparency and click-through
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # On some systems, the pet still "hides" when you click a window.
        # This line forces the window to be visible.
        self.show()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)  # Add this
        self.label.setMouseTracking(True) # And this for the sprite label
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    # -------------------------
    # STATES
    # -------------------------
    def setup_states(self):
        self.states = load_states(self.option)
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
            elif new_state == "speak":
                self.state_duration = random.randint(250, 400)
                self.encouragement.trigger()

            elif new_state == "sleep":
                self.state_duration = 999999 # Stay asleep until woken up
                if hasattr(self, 'text_bubble'):
                    self.text_bubble.hide()
            
            elif new_state == "walk":
                self.state_duration = random.randint(60, 300)
                self.MAX_SPEED = 2

                max_x = self.width() - self.label.width()
                max_y = self.height() - self.label.height()

                windows = getattr(self, "obstacles", [])
                self.current_window = get_window_under_pet(self, windows)

                #INSIDE A WINDOW---------------------------------------------------------
                if self.current_window:

                    choice = random.choices(
                        ["stay", "leave"],
                        weights=[0.8, 0.2]   # mostly stay
                    )[0]

                    if choice == "stay":
                        w = self.current_window
                        self.target_x = random.randint(w["x1"], w["x2"] - self.label.width())
                        self.target_y = random.randint(w["y1"], w["y2"] - self.label.height())

                    else:  # leave
                        margin = 80
                        w = self.current_window

                        left_max = w["x1"] - margin
                        right_min = w["x2"] + margin

                        options = []
                        if left_max > 0:
                            options.append((0, left_max))
                        if right_min < self.width():
                            options.append((right_min, self.width()))

                        if options:
                            chosen = random.choice(options)
                            self.target_x = random.randint(*chosen)
                        else:
                            self.target_x = random.randint(0, self.width() - self.label.width())

                        self.target_y = random.randint(0, self.height() - self.label.height())

                # OUTSIDE A WINDOW--------------------------------------------------------------
                else:
                    choice = random.choices(
                        ["enter", "free"],
                        weights=[0.5, 0.5]
                    )[0]

                    if choice == "enter" and windows:
                        w = random.choice(windows)
                        self.target_x = random.randint(w["x1"], w["x2"] - self.label.width())
                        self.target_y = random.randint(w["y1"], w["y2"] - self.label.height())

                    else:
                        self.target_x = random.randint(0, self.width() - self.label.width())
                        self.target_y = random.randint(0, self.height() - self.label.height())
                
                self.target_x = max(0, min(self.target_x, max_x))
                self.target_y = max(0, min(self.target_y, max_y))
    
    
    # -------------------------
    # SPRITE
    # -------------------------
    def setup_sprite(self):
        self.label = QLabel(self)
        self.update_appearance()
        screen = QApplication.primaryScreen().geometry()
        center_x = (screen.width() - self.label.width()) // 2
        center_y = (screen.height() - self.label.height()) // 2
        self.label.move(center_x, center_y)


    # -------------------------
    # TIMERS
    # -------------------------
    def setup_timers(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)


    # -------------------------
    # SLEEP RELATED
    # -------------------------
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


    # -------------------------
    # MAIN LOOP
    # -------------------------
    def tick(self):
        self.update_obstacles()

        if not self.dragging:
            self.inactivity_timer += 1

        if self.inactivity_timer >= self.INACTIVITY_LIMIT:
            if self.current_state != "sleep":
                self.set_state("sleep")
        else:
            if self.current_state == "sleep":
                self.set_state("idle")

        if self.current_state != "sleep":
            update_behavior(self)

        self.update_appearance()


    def closeEvent(self, event):
        # Check if they exist before stopping to prevent errors on early exit
        if hasattr(self, 'm_listener'):
            self.m_listener.stop()
        if hasattr(self, 'k_listener'):
            self.k_listener.stop()
        event.accept()


    # -------------------------
    # APPEARANCE
    # -------------------------
    def update_appearance(self):
        state_data = self.states.get(self.current_state)
        if not state_data:
            return

        frames = state_data["frames"]
        pixmap = frames[self.frame_index]

        # tracks mouse
        global_mouse = QCursor.pos()
        local_mouse = self.label.mapFromGlobal(global_mouse)
        
        # space for petting
        in_rub_zone = -20 < local_mouse.x() < 140 and -40 < local_mouse.y() < 60
        
        if not hasattr(self, 'last_mouse_pos'): self.last_mouse_pos = global_mouse
        if not hasattr(self, 'squish_factor'): self.squish_factor = 1.0

        # calculate squish based on velocity
        dx = global_mouse.x() - self.last_mouse_pos.x()
        dy = global_mouse.y() - self.last_mouse_pos.y()
        total_movement = math.sqrt(dx**2 + dy**2)
        
        self.last_mouse_pos = global_mouse

        # only in idle state
        if self.current_state == "idle":
            in_rub_zone = -20 < local_mouse.x() < 140 and -40 < local_mouse.y() < 60
            
            if in_rub_zone and total_movement > 5:
                # squish down when being pet
                self.squish_factor = max(0.75, self.squish_factor - 0.08)
            else:
                self.squish_factor = min(1.0, self.squish_factor + 0.03)
        else:
            # force recovery when not idle
            self.squish_factor = min(1.0, self.squish_factor + 0.05)

        target_w = 120
        target_h = int(120 * self.squish_factor)

        scaled = pixmap.scaled(
            target_w, target_h,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.FastTransformation
        )

        self.label.setPixmap(scaled)
        
        # keep cat's feet vertically position the same
        top_margin = 120 - target_h
        self.label.setContentsMargins(0, top_margin, 0, 0)
        
        if not hasattr(self, 'animation') or self.animation.state() != QPropertyAnimation.State.Running:
            self.label.resize(120, 120)

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
        self.text_bubble.setFont(QFont("Arial", 10))
        self.text_bubble.setStyleSheet(
            "color: black; background-color: rgba(255,255,255,0.9); "
            "border-radius: 10px; padding: 5px;"
        )
        self.text_bubble.hide()

        # Reply Button
        self.reply_button = QPushButton("Reply", self)
        self.reply_button.setFixedWidth(40)
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
        
        try:
            response = self.chat_session.send_message(user_text)
            self.state_timer = 0 
            self.state_duration = random.randint(200, 300) 
            self.show_encouragement(response.text)
        except Exception as e:
            print(f"Error: {e}")
            self.show_encouragement("Meow... (Something went wrong with my brain!)")

    def show_encouragement(self, text):
        self.text_bubble.setText(text)
        self.text_bubble.adjustSize()
        
        # Center bubble above cat
        bubble_x = self.label.x() + (self.label.width() - self.text_bubble.width()) // 2

        # Flip below if not enough room above
        if self.label.y() - self.text_bubble.height() - 10 < 0:
            bubble_y = self.label.y() + self.label.height() + 5 # below cat
            button_y = bubble_y + self.text_bubble.height() + 5
        else:
            bubble_y = self.label.y() - self.text_bubble.height() - 10  # above cat
            button_y = bubble_y + self.text_bubble.height() + 5
        self.text_bubble.move(bubble_x, bubble_y)
        self.text_bubble.show()

        # Center reply button below bubble
        button_x = self.label.x() + (self.label.width() - self.reply_button.width()) // 2
        self.reply_button.move(button_x, button_y)
        self.reply_button.show()
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
        if self.current_state != "speak":
            self.encouragement.trigger()

    def resizeEvent(self, event):
        self.label.move(
            (self.width() - self.label.width()) // 2,
            (self.height() - self.label.height()) // 2
        )

    # -------------------------
    # OBSTACLE AVOIDANCE
    # -------------------------
    def update_obstacles(self):
        self.obstacles = get_windows()


    def set_intent(self, x, y):
        self.intent_x = x
        self.intent_y = y

    
    def is_full_block(self, w):
        return (
            w["x1"] <= 0 and w["y1"] <= 0 and
            w["x2"] >= self.width() and
            w["y2"] >= self.height()
        )

    def update_obstacles(self):
        self.obstacles = get_windows()
        self.current_window = get_window_under_pet(self, self.obstacles)

    def choose_window_intent(self):
        self.update_obstacles()

        windows = self.obstacles
        current = self.current_window

        # -------------------------
        # No windows available
        # -------------------------
        if not windows:
            return "roam", None

        # -------------------------
        # Inside a window
        # -------------------------
        if current:
            intent = random.choices(
                ["stay", "enter", "leave"],
                weights=[0.75, 0.15, 0.10]  # tweak personality here
            )[0]

            # STAY in current window
            if intent == "stay":
                return "stay", current

            # ENTER a different window
            elif intent == "enter":
                others = [w for w in windows if w != current]
                if others:
                    return "enter", random.choice(others)
                return "stay", current

            # LEAVE current window entirely
            elif intent == "leave":
                return "leave", current

        # -------------------------
        # Not inside any window
        # -------------------------
        else:
            intent = random.choices(
                ["enter", "roam"],
                weights=[0.85, 0.15]
            )[0]

            if intent == "enter":
                return "enter", random.choice(windows)

            return "roam", None