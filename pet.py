import random
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QFont
from windows import get_windows, get_window_under_pet, get_window_center 

from states import load_states
from behavior import update_behavior
from encouragement import EncouragementSystem

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        self.frame_counter = 0
        self.frame_index = 0

        self.setup_window()
        self.setup_states()
        self.setup_sprite()
        self.setup_text_bubble()
        self.setup_systems()
        self.setup_timers()
        self.setup_interaction()

        self.target_x = 0
        self.target_y = 0

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

    def set_state(self, new_state):
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

            elif self.current_state == "walk":
                self.state_duration = random.randint(60, 300)

                self.MAX_SPEED = 2

                # pick a random destination
                windows = getattr(self, "obstacles", [])
                current_window = get_window_under_pet(self, windows)

                if current_window:
                    choice = random.choices(
                        ["leave", "stay"],
                        weights=[0.3, 0.7]
                    )[0]
                else:
                    choice = random.choices(
                        ["enter", "free"],
                        weights=[0.5, 0.5]
                    )[0]
                # -------------------------
                # ENTER WINDOW
                # -------------------------
                if choice == "enter" and windows:
                    w = random.choice(windows)

                    self.target_x = random.randint(w["x1"], w["x2"] - self.label.width())
                    self.target_y = random.randint(w["y1"], w["y2"] - self.label.height())

                # -------------------------
                # LEAVE WINDOW
                # -------------------------
                elif choice == "leave" and current_window:
                    margin = 80

                    left_max = current_window["x1"] - margin
                    right_min = current_window["x2"] + margin

                    options = []

                    # LEFT side (only if valid)
                    if left_max > 0:
                        options.append((0, left_max))

                    # RIGHT side (only if valid)
                    if right_min < self.width():
                        options.append((right_min, self.width()))

                    # fallback if no valid options
                    if not options:
                        self.target_x = random.randint(0, self.width() - self.label.width())
                    else:
                        chosen = random.choice(options)
                        self.target_x = random.randint(chosen[0], chosen[1])

                    # Y can stay normal
                    self.target_y = random.randint(0, self.height() - self.label.height())

                    self.target_y = random.randint(0, self.height())

                # -------------------------
                # FREE WALK
                # -------------------------
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

    # -------------------------
    # MAIN LOOP
    # -------------------------
    def tick(self):
        update_behavior(self)
        self.update_obstacles()
        self.update_appearance()

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
