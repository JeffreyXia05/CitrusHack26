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

        # Timer for delayed re-show
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.trigger)

    def trigger(self):
        """Only show encouragement if in speak mode."""
        if self.pet.current_state != "speak":
            return

        self.show_random_encouragement()

    def show_random_encouragement(self):
        """Pick and display a message."""

        if self.pet.text_bubble.isVisible():
            self.pet.text_bubble.hide()
            delay = random.randint(3000, 15000)
            self.timer.start(delay)
            return

        word = random.choice(ENCOURAGEMENT_WORDS)
        self.pet.show_encouragement(word)

        self.timer.start(3000)