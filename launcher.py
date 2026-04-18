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

        # placeholder settings (you can expand later)
        layout.addWidget(QLabel("• Idle"))


        self.setLayout(layout)

class Launcher(QWidget):
    def __init__(self, on_deploy):
        super().__init__()

        self.on_deploy = on_deploy

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

        self.settings_window = None

    def deploy(self):
        self.on_deploy()
        self.deploy_button.setText("Deployed ✔")
        self.deploy_button.setEnabled(False)
        self.hide()

    def open_settings(self):
        # create once, reuse later
        if self.settings_window is None:
            self.settings_window = SettingsDialog()

        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()