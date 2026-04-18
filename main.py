import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap


class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()

        # Remove window frame & keep on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Load image (FIXED filename)
        self.pixmap = QPixmap("cube.png")

        # Resize here
        self.pixmap = self.pixmap.scaled(
            120, 120,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.pixmap.size())
        self.label.move(0, 0)

        self.setFixedSize(self.pixmap.size())
        print("Loaded:", not self.pixmap.isNull())  # debug

        # Label setup
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.pixmap.size())
        self.label.move(0, 0)

        # Match window size exactly to image
        self.setFixedSize(self.pixmap.size())

        # Optional: only clickable on visible pixels
        # (comment out if it causes issues)
        # self.setMask(self.pixmap.mask())

        # Starting position
        self.move(100, 100)

        # Allow keyboard focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.activateWindow()
        self.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())