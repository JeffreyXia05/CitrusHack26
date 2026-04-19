from PyQt6.QtWidgets import (
    QButtonGroup, QRadioButton, QWidget, QPushButton, QVBoxLayout, QDialog, QLabel
)

# ------------------------------------------------------------------------------------------
# CUSTOMIZABLE SETTINGS
# ------------------------------------------------------------------------------------------
class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")
        self.setFixedSize(500, 300)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Settings Menu"))

        self.idle_enabled = True
        self.walk_enabled = True
        self.speak_enabled = True
        self.sleep_enabled = True
        self.weirdWalk_enabled = False

        self.idle_btn = QPushButton("Idle: ON")
        self.walk_btn = QPushButton("Walk: ON")
        self.speak_btn = QPushButton("Speak: ON")
        self.sleep_btn = QPushButton("Sleep: ON")
        self.weirdWalk_btn = QPushButton("Weird Walk: OFF")

        self.idle_btn.clicked.connect(self.toggle_idle)
        self.walk_btn.clicked.connect(self.toggle_walk)
        self.speak_btn.clicked.connect(self.toggle_speak)
        self.sleep_btn.clicked.connect(self.toggle_sleep)
        self.weirdWalk_btn.clicked.connect(self.toggle_weirdWalk)

        layout.addWidget(self.idle_btn)
        layout.addWidget(self.walk_btn)
        layout.addWidget(self.speak_btn)
        layout.addWidget(self.sleep_btn)
        layout.addWidget(self.weirdWalk_btn)
        layout.addWidget(QLabel("Cat Color"))

        color = [
            ("Black", 1),
            ("Orange", 2),
            ("White", 3)
        ]

        self.color_group = QButtonGroup(self)
        self.color_group.buttonClicked.connect(self.update_id)

        for name, color_id in color:
            radio = QRadioButton(name)
            radio.setProperty("id", color_id)
            
            layout.addWidget(radio)
            self.color_group.addButton(radio)

        self.color_group.buttons()[0].setChecked(True)
        self.option = 1

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

    def toggle_weirdWalk(self):
        self.weirdWalk_enabled = not self.weirdWalk_enabled
        self.weirdWalk_btn.setText(f"Weird Walk: {'ON' if self.weirdWalk_enabled else 'OFF'}")

    def update_id(self, button):
        self.option = button.property("id")

    def get_id(self):
        return self.option