from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QDialog, QLabel
)

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Settings Menu"))

        self.idle_enabled = True
        self.walk_enabled = True
        self.speak_enabled = True
        self.sleep_enabled = True

        self.idle_btn = QPushButton("Idle: ON")
        self.walk_btn = QPushButton("Walk: ON")
        self.speak_btn = QPushButton("Speak: ON")
        self.sleep_btn = QPushButton("Sleep: ON")

        self.idle_btn.clicked.connect(self.toggle_idle)
        self.walk_btn.clicked.connect(self.toggle_walk)
        self.speak_btn.clicked.connect(self.toggle_speak)
        self.sleep_btn.clicked.connect(self.toggle_sleep)

        layout.addWidget(self.idle_btn)
        layout.addWidget(self.walk_btn)
        layout.addWidget(self.speak_btn)
        layout.addWidget(self.sleep_btn)

        self.setLayout(layout)

    def toggle_idle(self):
        self.idle_enabled = not self.idle_enabled
        self.idle_btn.setText(f"Idle: {'ON' if self.idle_enabled else 'OFF'}")

    def toggle_walk(self):
        self.walk_enabled = not self.walk_enabled
        self.walk_btn.setText(f"Walk: {'ON' if self.walk_enabled else 'OFF'}")

    def toggle_speak(self):
        self.speak_enabled = not self.speak_enabled
        self.speak_btn.setText(f"Speak: {'ON' if self.speak_enabled else 'OFF'}")

    def toggle_sleep(self):
        self.sleep_enabled = not self.sleep_enabled
        self.sleep_btn.setText(f"Sleep: {'ON' if self.sleep_enabled else 'OFF'}")