import random
from encouragement import EncouragementSystem

def update_behavior(pet):
    # If the user is typing, don't tick the state timer
    if pet.chat_input.isVisible():
        return 

    pet.state_timer += 1

    if pet.current_state == "idle":
        idle(pet)

        if pet.state_timer >= pet.state_duration:
            pet.set_state("speak" #if random.random() < 0.3 else "walk")
            )
    elif pet.current_state == "walk":
        walk(pet)

        if pet.state_timer >= pet.state_duration:
            pet.set_state("idle")

    elif pet.current_state == "speak":
        speak(pet)

        if pet.state_timer >= pet.state_duration:
            pet.set_state("idle")


def idle(pet):

    pet.label.move(
        pet.label.x() + 0,
        pet.label.y() + 0
    )

def walk(pet): #consider implimenting weighted wandering AI (chooses destination)
    x = pet.label.x()
    y = pet.label.y()

    # move pet
    x += pet.dx
    y += pet.dy

    # screen bounds (bounce)
    max_x = pet.width() - pet.label.width()
    max_y = pet.height() - pet.label.height()

    if x <= 0 or x >= max_x:
        pet.dx *= -1

    if y <= 0 or y >= max_y:
        pet.dy *= -1

    pet.label.move(x, y)

def speak(pet):
    pass