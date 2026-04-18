import random

def update_behavior(pet):
    pet.current_state = random.choice(list(pet.states.keys()))

    if pet.current_state == "idle":
        idle(pet)

def idle(pet):
    dx = random.randint(-5, 5)
    dy = random.randint(-5, 5)
    pet.label.move(pet.label.x() + dx, pet.label.y() + dy)