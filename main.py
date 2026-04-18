import random
import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QPen, QFont


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        # Fixed window (NEVER moves)
        # Get screen size
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Load image
        self.pixmap = QPixmap("cube.png").scaled(
            100, 100,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Sprite (cube)
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)
        self.label.setGeometry(50, 50, 100, 100)  # start centered

        # Text bubble label
        self.text_bubble = QLabel(self)
        self.text_bubble.setWordWrap(True)
        self.text_bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_bubble.setStyleSheet("background-color: rgba(255, 255, 255, 0.9); border-radius: 15px; padding: 10px;")
        self.text_bubble.setFont(QFont("Arial", 12))
        self.text_bubble.hide()

        # Drag state (for sprite only)
        self.dragging = False
        self.offset = QPoint()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Encouragement words
        self.encouragement_words = [
            "You got this!",
            "Keep going!",
            "You're doing great!",
            "Stay strong!",
            "Believe in yourself!",
            "One step at a time!",
            "You can do it!",
            "Never give up!",
            "You're awesome!",
            "Keep pushing!",
            "You're making progress!",
            "Stay positive!",
            "You've got this!",
            "Keep shining!",
            "You're amazing!"
        ]

        # Timer for random encouragement
        self.encouragement_timer = QTimer(self)
        self.encouragement_timer.setSingleShot(True)
        self.encouragement_timer.timeout.connect(self.show_random_encouragement)

    def show_random_encouragement(self):
        """Display a random encouragement message next to the cube"""
        if self.text_bubble.isVisible():
            self.text_bubble.hide()
            delay = random.randint(3000, 15000)
            QTimer.singleShot(delay, self.show_random_encouragement)
            return

        word = self.encouragement_words[random.randint(0, len(self.encouragement_words) - 1)]
        self.text_bubble.setText(word)
        
        # Position text bubble next to the cube (to the right)
        bubble_width = self.text_bubble.sizeHint().width()
        bubble_height = self.text_bubble.sizeHint().height()
        
        # Position to the right of the cube with some offset
        self.text_bubble.move(
            self.label.x() + self.label.width() + 10,
            self.label.y() + (self.label.height() - bubble_height) // 2
        )
        self.text_bubble.setStyleSheet("color: black; background-color: rgba(255, 255, 255, 0.9); border-radius: 15px; padding: 10px;")

        self.text_bubble.show()
        self.encouragement_timer.start(3000)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()

    # 👉 CLICK ON LABEL ONLY
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.label.geometry().contains(event.pos()):
                self.dragging = True
                self.offset = event.pos() - self.label.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.pos() - self.offset

            # keep inside window bounds (optional but nice)
            new_x = max(0, min(new_pos.x(), self.width() - self.label.width()))
            new_y = max(0, min(new_pos.y(), self.height() - self.label.height()))

            self.label.move(new_x, new_y)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        # Show encouragement on mouse release
        self.show_random_encouragement()

    def resizeEvent(self, event):
        # Keep label centered when window resizes
        self.label.move(
            (self.width() - self.label.width()) // 2,
            (self.height() - self.label.height()) // 2
        )
        # Reposition text bubble when window resizes
        bubble_width = self.text_bubble.sizeHint().width()
        bubble_height = self.text_bubble.sizeHint().height()
        self.text_bubble.move(
            self.label.x() + self.label.width() + 10,
            self.label.y() + (self.label.height() - bubble_height) // 2
        )

    def closeEvent(self, event):
        self.encouragement_timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())
