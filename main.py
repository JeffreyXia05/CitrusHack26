import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Remove the window frame and title bar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        
        # 2. Make the background invisible
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 3. Add your sprite image
        self.label = QLabel(self)
        self.pixmap = QPixmap("cube.png")  # Replace with your filename
        self.label.setPixmap(self.pixmap)
        
        # Resize window to fit the image
        self.resize(self.pixmap.width(), self.pixmap.height())
        
        # Starting position
        self.curr_pos = QPoint(100, 100)
        self.move(self.curr_pos)

    def mousePressEvent(self, event):
        # This allows you to click and drag the pet manually
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