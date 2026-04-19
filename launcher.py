from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QDialog, QLabel
)

from settings import SettingsDialog

# ------------------------------------------------------------------------------------------
#  LAUNCHER
# ------------------------------------------------------------------------------------------
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
        instructions_layout.addWidget(QLabel("Thank you for using PCat! Here are some tips to get you started:"))
        instructions_layout.addWidget(QLabel("This virtual cat will explore your computer and sometimes take in the view (or maybe do some self care)")),
        instructions_layout.addWidget(QLabel("It may even talk to you sometimes, giving you encouragement or just random cat thoughts!")),
        instructions_layout.addWidget(QLabel("When it does so, give it some love by responding in the chat box! It loves attention and will respond to your messages!")),
        instructions_layout.addWidget(QLabel("Occasionally, it may grow bored if you leave it alone and choose to take a nap. No wories, it will wake up whwen you come back!")),
        instructions_layout.addWidget(QLabel("If PCat is in the way, right click to put it to bed for a little while. Also, don't forget to pet it every once in a while!")),
        instructions_layout.addWidget(QLabel("If you need to change your PCat to fit your computer vibe, head to the settings tab in the launcher to change sprites, behavior, and more!"))
        instructions_layout.addWidget(QLabel("Of course, sometimes you need your space, and PCat understands. To send PCat home, just left click him once and press the esacape key!"))

        self.instructions_window.setLayout(instructions_layout)
        self.instructions_window.show()
        self.instructions_window.raise_()
        self.instructions_window.activateWindow()