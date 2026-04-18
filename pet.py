import random
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import QEvent, Qt, QPoint, QTimer
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
        self.setup_systems()
        self.setup_text_bubble()
        self.setup_timers()
        self.setup_interaction()
        
        self.installEventFilter(self)
        self.setup_global_listeners()

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
            self.current_encouragement = None
            self.last_speak_state = None
        if new_state not in self.states:
            print(f"Warning: unknown state '{new_state}'")
            return

        # only run when state actually changes
        if self.current_state != new_state:
            self.current_state = new_state

            # reset animation
            self.frame_index = 0
            self.frame_counter = 0

            # reset timing
            self.state_timer = 0

            # assign duration per state
            if new_state == "idle":
                self.state_duration = random.randint(180, 420)

            elif new_state == "walk":
                self.state_duration = random.randint(60, 300)

                # set movement ONCE
                self.MAX_SPEED = 3
                self.dx = random.randint(-self.MAX_SPEED, self.MAX_SPEED)
                self.dy = random.randint(-self.MAX_SPEED, self.MAX_SPEED)
            elif new_state == "speak":
                self.state_duration = random.randint(90, 210)
                self.encouragement.trigger()
            elif new_state == "sleep":
                self.state_duration = 999999 # Stay asleep until woken up
                if hasattr(self, 'text_bubble'):
                    self.text_bubble.hide()

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


    # =========================
    # SYSTEMS
    # =========================
    def setup_systems(self):
        self.encouragement = EncouragementSystem(self)

    # =========================
    # TIMERS
    # =========================
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

    # -------------------------
    # MAIN LOOP
    # -------------------------
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
    # -------------------------
    # APPEARANCE
    # -------------------------
    def update_appearance(self):
        state_data = self.states.get(self.current_state)

        if not state_data:
            print(f"Error: missing state '{self.current_state}'")
            return

        frames = state_data["frames"]

        pixmap = frames[self.frame_index]

        scaled = pixmap.scaled(
            120, 120,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.label.setPixmap(scaled)
        self.label.resize(scaled.size())

        # ---- animation timing ----
        self.frame_counter += 1

        fps = state_data.get("fps", 2)

        if self.frame_counter >= (60 // fps):
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(frames)

    # =========================
    # TEXT BUBBLE
    # =========================
    def setup_text_bubble(self):
        self.text_bubble = QLabel(self)
        self.text_bubble.setWordWrap(True)
        self.text_bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_bubble.setFont(QFont("Arial", 12))
        self.text_bubble.setStyleSheet(
            "color: black; background-color: rgba(255,255,255,0.9); "
            "border-radius: 15px; padding: 10px;"
        )
        self.text_bubble.hide()

    # =========================
    # UI HOOK (used by encouragement system)
    # =========================
    def show_encouragement(self, text):
        self.text_bubble.setText(text)

        bubble_w = self.text_bubble.sizeHint().width()
        bubble_h = self.text_bubble.sizeHint().height()

        self.text_bubble.move(
            self.label.x() + self.label.width() + 10,
            self.label.y() + (self.label.height() - bubble_h) // 2
        )

        self.text_bubble.show()

    # -------------------------
    # EVENTS
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

    def mouseReleaseEvent(self, event):
        self.dragging = False
        if self.current_state != "speak":
            self.encouragement.trigger()

    def resizeEvent(self, event):
        self.label.move(
            (self.width() - self.label.width()) // 2,
            (self.height() - self.label.height()) // 2
        )

