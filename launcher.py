from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QDialog, QLabel
)

from settings import SettingsDialog

class Launcher(QWidget):
    def __init__(self, on_deploy):
        super().__init__()

        self.on_deploy = on_deploy
        self.settings_window = SettingsDialog()

        self.setWindowTitle("Launcher")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.deploy_button = QPushButton("Deploy Pet")
        self.deploy_button.clicked.connect(self.deploy)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)

        layout.addWidget(self.deploy_button)
        layout.addWidget(self.settings_button)

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