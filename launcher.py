from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QDialog, QLabel
)

from settings import SettingsDialog

class Launcher(QWidget):
    def __init__(self, on_deploy):
        super().__init__()

        self.on_deploy = on_deploy
        self.settings_window = SettingsDialog()
        self.instructions_window = QDialog()
        self.instructions_window.setWindowTitle("Instructions")

        self.setWindowTitle("Launcher")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.deploy_button = QPushButton("Deploy Pet")
        self.deploy_button.clicked.connect(self.deploy)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)

        self.instructions_button = QPushButton("Instructions")
        self.instructions_button.clicked.connect(self.open_instructions)

        layout.addWidget(self.deploy_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.instructions_button)

        self.setLayout(layout)


    def deploy(self):
        option = self.settings_window.get_id()
        settings = self.settings_window.get_final_settings()
        self.on_deploy(option, settings)
        self.deploy_button.setText("Deployed ✔")
        self.deploy_button.setEnabled(False)
        self.hide()


    def open_settings(self):

        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
        self.option = SettingsDialog().get_id()

    def open_instructions(self):
        instructions_layout = QVBoxLayout()
        instructions_layout.addWidget(QLabel("Instructions:"))
        instructions_layout.addWidget(QLabel("1. Click 'Deploy Pet' to see your pet come to life!"))
        instructions_layout.addWidget(QLabel("2. Use the 'Settings' button to customize your pet's behavior and appearance."))
        instructions_layout.addWidget(QLabel("3. Interact with your pet by dragging it or petting it."))
        instructions_layout.addWidget(QLabel("4. Right click on your pet to make it take a nap and right click again to wake it up!"))
        instructions_layout.addWidget(QLabel("5. Leave the screen idle for 30 seconds to see it take a nap!"))
        instructions_layout.addWidget(QLabel("6. Talk to your pet by typing in the chat input when it talks to you!"))
        instructions_layout.addWidget(QLabel("7. Enjoy your new desktop companion!"))

        self.instructions_window.setLayout(instructions_layout)
        self.instructions_window.show()
        self.instructions_window.raise_()
        self.instructions_window.activateWindow()