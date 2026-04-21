import random
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
    def __init__(self, option, settings):
        super().__init__()

        # initialized variables for the pet's behavior, animation, and screen size
        self.frame_counter = 0
        self.frame_index = 0
        self.last_speak_state = None
        self.current_encouragement = None
        self.inactivity_timer = 0
        self.INACTIVITY_LIMIT = 60 * 60 * 10  # 10 seconds at 60fps
        self.dragging = False 
        self.option = option
        self.settings = settings

        # initialization for settings
        self.walk = settings.get("walk", True)
        self.speak = settings.get("speak", True)
        self.sleep = settings.get("sleep", True)

        # states initialization
        self.setup_states()

        # sprite and window setup
        self.setup_sprite()
        self.setup_window()
        
        # systems and gimmicks related stuff
        self.setup_systems() 
        if self.speak:
            self.setup_text_bubble()

        self.setup_timers()
        self.setup_interaction()
        self.setup_global_listeners() 

        # variables for petting
        self.last_mouse_pos = QPoint(0, 0)
        self.mouse_velocity = 0
        self.squish_factor = 1.0 
        self.target_x = 0
        self.target_y = 0
        self.direction = "down"

        self.idle_frame_index = 0

    # --------------------------------------------------------------------------------------------------
    # WINDOW
    # --------------------------------------------------------------------------------------------------
    def setup_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)

        # Updated flages for "true" /always on top behavior
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Window                      # Hides from Taskbar + stays afloat
        )
        
        # This attribute is crucial for transparency and click-through
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        self.show()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)  
        self.label.setMouseTracking(True) 
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        
    # --------------------------------------------------------------------------------------------------
    # STATES
    # --------------------------------------------------------------------------------------------------
    def setup_states(self):
        self.states = load_states(self.option, self.settings)
        self.current_state = "idle"
        self.dx = 0
        self.dy = 0
        self.state_timer = 0
        self.state_duration = random.randint(120, 300)  # frames (2–5 sec at 60fps)
        self.current_state = "idle"
        self.pinned = False
        self.pin_timer = 0
        self.pin_duration = 0
        
    def setup_systems(self):
        if self.speak:
            self.encouragement = EncouragementSystem(self)
            
    def set_state(self, new_state):
        if self.current_state == "speak" and new_state != "speak" and self.speak:
            self.text_bubble.hide()
            if hasattr(self, "chat_input"):
                self.chat_input.hide()
            if hasattr(self, "reply_button"):
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
                self.state_duration = random.randint(180, 60 * 120)  # 3 sec to 1 min
                idle_variants = self.states["idle"]["variants"]
                self.current_idle_frames = random.choice(idle_variants)
            elif new_state == "speak" and self.speak:
                self.state_duration = random.randint(600, 1200)  # 10 sec to 1 min
                self.encouragement.trigger()

            elif new_state == "sleep" and self.sleep:
                self.state_duration = 999999 # Stay asleep until woken up
                sleep_variants = self.states["sleep"]["variants"]
                self.current_sleep_frames = random.choice(sleep_variants)
                self.frame_index = 0
                
                if self.speak:
                    if hasattr(self, 'text_bubble'):
                        self.text_bubble.hide()
            
            elif new_state == "walk" and self.walk:
                self.state_duration = random.randint(60, 300)
                self.MAX_SPEED = 2

                screen = QApplication.primaryScreen().geometry()
                max_x = self.width() - self.label.width()
                max_y = self.height() - self.label.height()

                windows = getattr(self, "obstacles", [])
                self.current_window = get_window_under_pet(self, windows)
                if hasattr(self, "last_direction") and self.last_direction != self.direction:
                    self.frame_index = 0

                self.last_direction = self.direction

                #INSIDE A WINDOW---------------------------------------------------------
                if self.current_window:

                    choice = random.choices(
                        ["stay", "leave"],
                        weights=[0.9, 0.1]   # mostly stay
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
                        weights=[0.1, 0.9] 
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
    
    
    # --------------------------------------------------------------------------------------------------
    # SPRITE
    # --------------------------------------------------------------------------------------------------
    def setup_sprite(self):
        self.label = QLabel(self)
        self.update_appearance()
        screen = QApplication.primaryScreen().geometry()
        center_x = (screen.width() - self.label.width()) // 2
        center_y = (screen.height() - self.label.height()) // 2
        self.label.move(center_x, center_y)


    # --------------------------------------------------------------------------------------------------
    # TIMERS
    # --------------------------------------------------------------------------------------------------
    def setup_timers(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)


    # --------------------------------------------------------------------------------------------------
    # SLEEP RELATED
    # --------------------------------------------------------------------------------------------------
    def on_global_input(self, *args):
        self.inactivity_timer = 0

    def eventFilter(self, obj, event):
        # Detect Mouse Movement, Clicks, or Keyboard Presses
        if event.type() in [
            QEvent.Type.MouseMove, 
            QEvent.Type.MouseButtonPress, 
            QEvent.Type.KeyPress
        ]:
            self.wake_up()
        
        return super().eventFilter(obj, event)


    # tracks mouse for waking up
    def setup_global_listeners(self):
        # Ensure these names match what is in closeEvent
        self.m_listener = pynput_mouse.Listener(on_move=lambda x, y: self.wake_up())
        self.k_listener = pynput_keyboard.Listener(on_press=lambda key: self.wake_up())
        
        self.m_listener.start()
        self.k_listener.start()


    def wake_up(self):
        # change the state from "sleep" to "idle" automatically by resetting timer.
        self.inactivity_timer = 0


    # --------------------------------------------------------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------------------------------------------------------
    def tick(self):

        self.update_obstacles()

        if self.pinned:
            self.pin_timer += 1
            if self.pin_timer >= self.pin_duration:
                self.pinned = False
                self.set_state("idle")  # wake up when pin expires
            return

        if self.dragging:
            # reset timer to stop all other actions while dragging
            self.inactivity_timer = 0
            
            self.update_appearance()
            return
        
        self.inactivity_timer += 1

        # Handle sleep/wake transition
        if self.inactivity_timer >= self.INACTIVITY_LIMIT:
            if self.current_state != "sleep":
                self.set_state("sleep")
        else:
            if self.current_state == "sleep":
                self.set_state("idle")

        if self.current_state != "sleep":
            update_behavior(self, self.walk, self.speak, self.sleep)

        # Update visual frame
        self.update_appearance()


    def closeEvent(self, event):
        # Check if they exist before stopping to prevent errors on early exit
        if hasattr(self, 'm_listener'):
            self.m_listener.stop()
        if hasattr(self, 'k_listener'):
            self.k_listener.stop()
        event.accept()


    # --------------------------------------------------------------------------------------------------
    # APPEARANCE
    # --------------------------------------------------------------------------------------------------
    def update_appearance(self):
        # DRAG STATE OVERRIDE
        # If dragging, freeze on the first frame (index 0)
        if getattr(self, 'dragging', False):
            state_key = "drag"
        else:
            state_key = self.current_state

        state_data = self.states.get(state_key)
        if not state_data:
            self.current_state = "idle"
            return
            
        if self.current_state == "idle":
            if not hasattr(self, "current_idle_frames"):
                self.current_idle_frames = random.choice(state_data["variants"])
                self.idle_frame_index = 0

            frames = self.current_idle_frames

        elif self.current_state == "sleep":
            if not hasattr(self, "current_sleep_frames"):
                self.current_sleep_frames = random.choice(state_data["variants"])
            frames = self.current_sleep_frames

        else:
            frames = state_data.get("frames", [])
            

        if self.current_state == "walk" and not self.dragging:
            frames = state_data["frames"].get(self.direction, state_data["frames"]["down"])

        if not frames:
            return
        
        if self.current_state == "idle":
            pixmap = frames[self.idle_frame_index % len(frames)]
        else:
            pixmap = frames[self.frame_index % len(frames)]

        # tracks mouse
        global_mouse = QCursor.pos()
        local_mouse = self.label.mapFromGlobal(global_mouse)
        
        if not hasattr(self, 'last_mouse_pos'): self.last_mouse_pos = global_mouse
        if not hasattr(self, 'squish_factor'): self.squish_factor = 1.0

        # calculate squish based on velocity
        dx = global_mouse.x() - self.last_mouse_pos.x()
        dy = global_mouse.y() - self.last_mouse_pos.y()
        total_movement = math.sqrt(dx**2 + dy**2)
        self.last_mouse_pos = global_mouse

        # only in idle state (and not while dragging)
        if self.current_state == "idle" and not getattr(self, 'dragging', False):
            in_rub_zone = -20 < local_mouse.x() < 140 and -40 < local_mouse.y() < 60
            if in_rub_zone and total_movement > 5:
                self.squish_factor = max(0.75, self.squish_factor - 0.08)
            else:
                self.squish_factor = min(1.0, self.squish_factor + 0.03)
        else:
            self.squish_factor = min(1.0, self.squish_factor + 0.05)

        target_w = 120
        target_h = int(120 * self.squish_factor)

        scaled = pixmap.scaled(
            target_w, target_h,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.FastTransformation
        )

        self.label.setPixmap(scaled)
        
        top_margin = 120 - target_h
        self.label.setContentsMargins(0, top_margin, 0, 0)
        
        if not hasattr(self, 'animation') or self.animation.state() != QPropertyAnimation.State.Running:
            self.label.resize(120, 120)

        # protect animation timing
        # Only advance the frame animation if NOT dragging
        self.frame_counter += 1
        fps = state_data.get("fps", 2)

        if self.frame_counter >= (60 // fps):
            self.frame_counter = 0

            if self.current_state == "idle":
                self.idle_frame_index += 1

                # finished current idle animation
                if self.idle_frame_index >= len(frames):
                    self.current_idle_frames = random.choice(state_data["variants"])
                    self.idle_frame_index = 0
                    self.frame_counter = -random.randint(10, 60)  # small random delay between idle animations

            else:
                self.frame_index = (self.frame_index + 1) % len(frames)
                
    # --------------------------------------------------------------------------------------------------
    # CHAT UI
    # --------------------------------------------------------------------------------------------------
    def setup_text_bubble(self):
        self.text_bubble = QLabel(self)
        self.text_bubble.setWordWrap(True)
        self.text_bubble.setFont(QFont("Arial", 10))
        self.text_bubble.setStyleSheet(
            "color: black; background-color: rgba(255,255,255,0.9); "
            "border-radius: 10px; padding: 5px;"
        )
        self.text_bubble.hide()

    def show_chat_input(self):
        """Swaps the reply button for the text box."""
        self.reply_button.hide()
        self.chat_input.show()
        self.chat_input.setFocus()

    def handle_chat_input(self):
        user_text = self.chat_input.text().strip()
        if not user_text:
            return

        self.chat_input.clear()
        self.chat_input.hide()

        self.show_encouragement("...")

        try:
            response = self.get_local_response(user_text)
            self.state_duration = random.randint(200, 300)

            QTimer.singleShot(400, lambda: self.show_encouragement(response))

        except Exception as e:
            print(f"Error: {e}")
            self.show_encouragement("Meow... (Something went wrong with my brain!)")
    
    def get_local_response(self, text):
        text = text.lower()

        if "hello" in text or "hi" in text:
            return "Meow! Hi there 🐾"
        elif "how are you" in text:
            return "I'm feline good 😸"
        elif "tired" in text:
            return "You should rest! I'll nap with you 💤"
        elif "sad" in text:
            return "Aww... come here, human 🐱💛"
        elif "bye" in text:
            return "Bye! Don't forget to hydrate 💧"
        else:
            return random.choice([
                "Meow?",
                "I'm just a little cat 🐾",
                "Tell me more!",
                "Purr... interesting...",
                "Hehe 😺"
            ])
        
    def show_encouragement(self, text):
        self.text_bubble.setText(text)
        self.text_bubble.adjustSize()
        
        # Center bubble above cat
        bubble_x = self.label.x() + (self.label.width() - self.text_bubble.width()) // 2

        # Flip below if not enough room above
        if self.label.y() - self.text_bubble.height() - 10 < 0:
            bubble_y = self.label.y() + self.label.height() + 5 # below cat
        else:
            bubble_y = self.label.y() - self.text_bubble.height()  # above cat
        self.text_bubble.move(bubble_x, bubble_y)
        self.text_bubble.show()

    # ------------------------------------------------------------------------------------------
    # INTERACTION
    # ------------------------------------------------------------------------------------------
    def setup_interaction(self):
        self.dragging = False
        self.offset = QPoint()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if the user clicked on the pet label
            if self.label.geometry().contains(event.pos()):
                self.dragging = True
                self.offset = event.pos() - self.label.pos()
                
                if hasattr(self, 'animation'):
                    self.animation.stop() 
                
                self.set_state("drag")

        if event.button() == Qt.MouseButton.RightButton:
            if self.label.geometry().contains(event.pos()):
                if self.pinned == True:
                    self.set_state("idle")
                    self.pinned = False
                else:
                    self.pinned = True
                    self.pin_timer = 0
                    self.pin_duration = 9999
                    
                    self.state_duration = self.pin_duration
                    
                    self.current_state = "idle"  
                    self.set_state("sleep")
                    self.update_appearance()
                    self.state_duration = self.pin_duration

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.pos() - self.offset
            x = max(0, min(new_pos.x(), self.width() - self.label.width()))
            y = max(0, min(new_pos.y(), self.height() - self.label.height()))
            self.label.move(x, y)
            # Update bubble position while dragging
            if self.speak:
                if self.text_bubble.isVisible():
                    self.show_encouragement(self.text_bubble.text())

    def mouseReleaseEvent(self, event):
        self.dragging = False
        if self.current_state != "speak" and self.speak:
            self.encouragement.trigger()
        self.set_state("idle")

    def resizeEvent(self, event):
        self.label.move(
            (self.width() - self.label.width()) // 2,
            (self.height() - self.label.height()) // 2
        )

    # ------------------------------------------------------------------------------------------
    # OBSTACLE AVOIDANCE
    # ------------------------------------------------------------------------------------------
    def update_obstacles(self):
        self.obstacles = get_windows()

    def update_obstacles(self):
        self.obstacles = get_windows()
        self.current_window = get_window_under_pet(self, self.obstacles)
