import sys
from PyQt6.QtWidgets import QApplication
from pet import DesktopPet
from launcher import Launcher

class AppController:
    def __init__(self):
        self.pet = None

    def deploy_pet(self):
        if self.pet is None:
            self.pet = DesktopPet()
            self.pet.show()

def main():
    app = QApplication(sys.argv)

    controller = AppController()
    launcher = Launcher(on_deploy=controller.deploy_pet)
    launcher.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()