import random
from encouragement import EncouragementSystem

# -------------------------
# MAIN BEHAVIOR LOOP
# -------------------------
def update_behavior(pet):
    # If the user is typing, don't tick the state timer
    if pet.chat_input.hasFocus():
        return 

    if pet.current_state == "sleep":
        sleep(pet)
        return
    
    pet.state_timer += 1

    if pet.current_state == "idle":
        idle(pet)

        if pet.state_timer >= pet.state_duration:
            pet.set_state("speak" if random.random() < 0.3 else "walk")
            
    elif pet.current_state == "walk":
        walk(pet)

        if reached_target(pet):
            pet.set_state("idle")

    elif pet.current_state == "speak":
        speak(pet)

        if pet.state_timer >= pet.state_duration:
            pet.text_bubble.hide()
            pet.chat_input.hide()
            pet.set_state("idle")

    elif pet.current_state == "drag":
        drag(pet)


# -------------------------
# IDLE STATE
# -------------------------
def idle(pet):
    # stays still (you can add small idle animation later)
    pass


# -------------------------
# WALK STATE (TARGET BASED)
# -------------------------
def walk(pet):
    x = pet.label.x()
    y = pet.label.y()

    dx = pet.target_x - x
    dy = pet.target_y - y

    step = pet.MAX_SPEED

    # move toward target
    if abs(dx) > step:
        x += step if dx > 0 else -step
    else:
        x = pet.target_x

    if abs(dy) > step:
        y += step if dy > 0 else -step
    else:
        y = pet.target_y

    pet.label.move(x, y)

    # STOP when target reached
    if (
        abs(x - pet.target_x) < 3 and
        abs(y - pet.target_y) < 3
    ):
        pet.set_state("idle")


# -------------------------
# TARGET CHECK
# -------------------------
def reached_target(pet):
    return (
        abs(pet.label.x() - pet.target_x) < 3 and
        abs(pet.label.y() - pet.target_y) < 3
    )
def speak(pet):
    pass

def sleep(pet):
    # Pet stays still. 
    # Animation is handled automatically by update_appearance in pet.py
    pass

def drag(pet):
    # Position is handled by mouse events in pet.py
    pass
