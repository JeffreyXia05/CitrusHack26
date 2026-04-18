import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QMainWindow
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QPixmap


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        # Fixed window (NEVER moves)
        # Get screen size
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Load image
        self.states = {
            "idle": QPixmap("cube.png"),
            "walk": QPixmap("cube.png"),
            "speak": QPixmap("cube.png"),
            #idea pick up, talk, sleep
        }
        self.current_state = "idle"
        self.pixmap = self.states[self.current_state]

        # Sprite (cube)
        self.label = QLabel(self)
        self.update_appearance()
        self.label.setGeometry(50, 50, 100, 100)  # start centered

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_appearance)
        self.timer.start(3000)  # update every second

        self.move(200, 200)
        self.show()

        # Drag state (for sprite only)
        self.dragging = False
        self.offset = QPoint()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def update_appearance(self):
        image_path = self.states.get(self.current_state, "cube.png")
        self.pixmap = QPixmap(image_path)
        self.label.setPixmap(self.pixmap)

        if self.pixmap.isNull():
            print(f"Failed to load image: {image_path}")
            return

        scaled_pixmap = self.pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)
        self.label.setGeometry(self.label.x(), self.label.y(), scaled_pixmap.width(), scaled_pixmap.height()) 
        self.label.resize(scaled_pixmap.size())
        self.setFixedSize(self.label.size())
    
    def update_behavior(self):
        """The logic that picks a new state."""
        # Randomly choose a new state
        possible_states = list(self.states.keys())
        self.current_state = random.choice(possible_states)
        
        self.update_appearance()
        print(f"Pet is now: {self.current_state}")

        # Optional: Add small random movement
        if self.current_state == "IDLE":
            self.move(self.x() + random.randint(-5, 5), self.y() + random.randint(-5, 5))



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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())