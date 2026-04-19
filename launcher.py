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
        self.on_deploy(option)
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
        instructions_layout.addWidget(QLabel("This virtual cat will wander around your screen, exploring your various windows and applications."))
        instructions_layout.addWidget(QLabel("He may even talk to you sometimes, giving you encouragement or just random cat thoughts!"))
        instructions_layout.addWidget(QLabel("Sometimes, it likes to take in the view (and maybe do some self care), so don't be alarmed if you see it just sitting there staring at your screen."))
        instructions_layout.addWidget(QLabel("Occasionally, they may be tired and take a nap, especially if you leave your your computer for a while."))
        instructions_layout.addWidget(QLabel("Feel free to wake it up, it may not show it but PCat loves your presence!"))
        instructions_layout.addWidget(QLabel("That being said, it can be a little pesky, so if you need to scoot it over, left click on it and drag it away!"))
        instructions_layout.addWidget(QLabel("They won't mind, in fact, they loves the attention! Of course, it may only pesker you more, so put 'em to bed by right clicking it."))
        instructions_layout.addWidget(QLabel("Don't forget to give him a good pet every once in a while! A good squishing can go a long way in keeping your cat happy and active!"))
        instructions_layout.addWidget(QLabel("If you need to change your PCat to fit your computer vibe, head to the settings tab in the launcher to change sprites, behavior, and more!"))
        instructions_layout.addWidget(QLabel("Of course, sometimes you need your space, and PCat understands. To send PCat home, just left click him once and press the esacape key!"))

        self.instructions_window.setLayout(instructions_layout)
        self.instructions_window.show()
        self.instructions_window.raise_()
        self.instructions_window.activateWindow()