import random
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import QEvent, Qt, QPoint, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont
from windows import get_windows, get_window_under_pet, get_window_center 

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

        self.target_x = 0
        self.target_y = 0

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
                self.state_duration = random.randint(60, 300)

            elif new_state == "speak":
                self.state_duration = random.randint(90, 210)
                self.encouragement.trigger()

            elif new_state == "sleep":
                self.state_duration = 999999 # Stay asleep until woken up
                if hasattr(self, 'text_bubble'):
                    self.text_bubble.hide()
            
            elif new_state == "walk":
                self.state_duration = random.randint(60, 300)
                self.MAX_SPEED = 2

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
    # SYSTEMS
    # -------------------------
    def setup_systems(self):
        self.encouragement = EncouragementSystem(self)


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
            print(f"Error: missing state '{self.current_state}'")
            return

        # This ensures 'frames' is defined for the rest of the function
        frames = state_data["frames"]
        pixmap = frames[self.frame_index]

        # Use FastTransformation for crisp pixel art clarity
        scaled = pixmap.scaled(
            120, 120,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )

        self.label.setPixmap(scaled)
        
        # Only resize the label if the movement animation ISN'T running
        # This prevents the pet from 'stuttering' during the sleep crawl
        if not hasattr(self, 'animation') or self.animation.state() != QPropertyAnimation.State.Running:
            self.label.resize(scaled.size())

        # ---- animation timing ----
        self.frame_counter += 1
        fps = state_data.get("fps", 2)

        if self.frame_counter >= (60 // fps):
            self.frame_counter = 0
            # Use the frames variable we defined above
            self.frame_index = (self.frame_index + 1) % len(frames)


    # -------------------------
    # TEXT BUBBLE
    # -------------------------
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


    # -------------------------
    # UI HOOK (used by encouragement system)
    # -------------------------
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