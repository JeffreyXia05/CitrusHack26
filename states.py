from PyQt6.QtGui import QPixmap

def load_states():
    return {
        "idle": QPixmap("assets/idleCube.png"),
        "walk": QPixmap("assets/walkCube.png"),
        "speak": QPixmap("assets/speakCube.png"),
        "sleep": QPixmap("assets/sleepCube.png"),
        #idea pick up, talk, sleep
    }