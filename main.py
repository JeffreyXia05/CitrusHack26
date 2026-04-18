import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap


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

        # Drag state (for sprite only)
        self.dragging = False
        self.offset = QPoint()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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