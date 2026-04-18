import random
from PyQt6.QtCore import QTimer


ENCOURAGEMENT_WORDS = [
    "You got this!",
    "Keep going!",
    "You're doing great!",
    "Stay strong!",
    "Believe in yourself!",
    "One step at a time!",
    "You can do it!",
    "Never give up!",
    "You're awesome!",
    "Keep pushing!",
    "You're making progress!",
    "Stay positive!",
    "You've got this!",
    "Keep shining!",
    "You're amazing!"
]


class EncouragementSystem:
    def __init__(self, pet):
        self.pet = pet

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_message)

    def start(self):
        self.schedule_next()

    def schedule_next(self):
        delay = random.randint(3000, 15000)
        self.timer.start(delay)

    def show_message(self):
        if self.pet.text_bubble.isVisible():
            self.pet.text_bubble.hide()
            self.schedule_next()
            return

        text = random.choice(ENCOURAGEMENT_WORDS)
        self.pet.show_encouragement(text)

        self.timer.start(3000)
        self.schedule_next()