import random
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QFont

from states import load_states
from behavior import update_behavior
from encouragement import EncouragementSystem

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        self.setup_window()
        self.setup_states()
        self.setup_sprite()
        self.setup_text_bubble()
        self.setup_systems()
        self.setup_timers()
        self.setup_interaction()

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
        self.timer.start(3000)

    # -------------------------
    # MAIN LOOP
    # -------------------------
    def tick(self):
        update_behavior(self)
        self.update_appearance()

    # -------------------------
    # APPEARANCE
    # -------------------------
    def update_appearance(self):
        pixmap = self.states.get(self.current_state)

        if not pixmap or pixmap.isNull():
            print(f"Error: Could not load '{self.current_state}' image.")
            return

        scaled = pixmap.scaled(
            120, 120,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.label.setPixmap(scaled)
        self.label.resize(scaled.size())

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

    def closeEvent(self, event):
        self.encouragement_timer.stop()