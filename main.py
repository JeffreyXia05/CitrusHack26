import sys
from PyQt6.QtWidgets import QApplication
from pet import DesktopPet
from launcher import Launcher

class AppController:
    def __init__(self):
        self.pet = None

    # deploy the pet with the color option
    def deploy_pet(self, option):
        if self.pet is None:
            self.pet = DesktopPet(option)
            self.pet.show()

def main():
    app = QApplication(sys.argv)

    controller = AppController()
    # calls launcher
    launcher = Launcher(on_deploy=controller.deploy_pet)
    launcher.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()