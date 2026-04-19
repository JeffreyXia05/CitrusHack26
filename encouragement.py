import random
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QFont
from voice import VoiceManager #delete this


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
    "You're amazing!",
    "Go go go!!!",
    "I'm itchy"
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
        """Pick a message and open the chat input."""
        if self.pet.text_bubble.isVisible():
            self.pet.text_bubble.hide()
            self.pet.chat_input.hide() # Hide input when bubble closes
            self.timer.start(random.randint(3000, 15000))
            return

        word = random.choice(ENCOURAGEMENT_WORDS)
        if self.pet.current_state == "speak":
            self.pet.show_encouragement(word)

            if hasattr(self.pet, 'voice_manager'): #delete this
                self.pet.voice_manager.say(word)
            
            # Show the chat input right below the bubble
            self.pet.chat_input.move(
                self.pet.text_bubble.x(), 
                self.pet.text_bubble.y() + self.pet.text_bubble.height() + 5
            )
            self.pet.chat_input.setFixedWidth(self.pet.text_bubble.width())
            self.pet.chat_input.setFocus()
