import os
from PyQt6.QtGui import QPixmap

BASE_DIR = os.path.dirname(__file__)
ASSETS = os.path.join(BASE_DIR, "assets")


def load_states():
    return {
        "idle": {
            "frames": [
                QPixmap(os.path.join(ASSETS, "idleCube.png")),
                #QPixmap(os.path.join(ASSETS, "idle2.png")),
                #QPixmap(os.path.join(ASSETS, "idle3.png")),
            ],
            "fps": 2
        },

        "walk": {
            "frames": [
                QPixmap(os.path.join(ASSETS, "walkCube.png")),
                #QPixmap(os.path.join(ASSETS, "walk2.png")),
                #QPixmap(os.path.join(ASSETS, "walk3.png")),
            ],
            "fps": 6
        },

        "speak": {
            "frames": [
                QPixmap(os.path.join(ASSETS, "speakCube.png")),
                #QPixmap(os.path.join(ASSETS, "speak2.png")),
            ],
            "fps": 3
        },

        "sleep": {
            "frames": [
                QPixmap(os.path.join(ASSETS, "sleepCube.png")),
                #QPixmap(os.path.join(ASSETS, "sleep2.png")),
            ],
            "fps": 1
        },
    }