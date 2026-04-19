import random
import math

# ------------------------------------------------------------------------------------------
# MAIN BEHAVIOR LOOP
# -------------------------
def update_behavior(pet, idleBool, walkBool, speakBool, sleepBool):
    # If the user is typing, don't tick the state timer
    if speakBool:
        if pet.chat_input.hasFocus():
            return 

    if pet.current_state == "sleep" and sleepBool:
        sleep(pet)
        return
    
    pet.state_timer += 1

    if pet.current_state == "idle" and idleBool:
        idle(pet)

        if pet.state_timer >= pet.state_duration:
            pet.set_state("speak" if random.random() < 0.4 else "walk") #testing
            
            
    elif pet.current_state == "walk" and walkBool:
        walk(pet)

        if reached_target(pet):
            pet.set_state("idle")

    elif pet.current_state == "speak" and speakBool:
        speak(pet)

        if pet.state_timer >= pet.state_duration:
            pet.text_bubble.hide()
            pet.chat_input.hide()
            pet.set_state("idle")


# ------------------------------------------------------------------------------------------
# IDLE STATE
# ------------------------------------------------------------------------------------------
def idle(pet):
    pass


# ------------------------------------------------------------------------------------------
# WALK STATE (TARGET BASED)
# ------------------------------------------------------------------------------------------
def walk(pet):
    if getattr(pet, 'pinned', False):
        return
    
    x = pet.label.x()
    y = pet.label.y()

    dx = pet.target_x - x
    dy = pet.target_y - y

    pet.direction = get_direction(dx, dy)

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

    # stop when target reached
    if (
        abs(x - pet.target_x) < 3 and
        abs(y - pet.target_y) < 3
    ):
        pet.set_state("idle")

# gets direction of sprite
def get_direction(dx, dy):
    angle = math.atan2(dy, dx)
    if -math.pi/8 <= angle < math.pi/8:
        return "right"
    elif math.pi/8 <= angle < 3*math.pi/8:
        return "down_right"
    elif 3*math.pi/8 <= angle < 5*math.pi/8:
        return "down"
    elif 5*math.pi/8 <= angle < 7*math.pi/8:
        return "down_left"
    elif 7*math.pi/8 <= angle or angle < -7*math.pi/8:
        return "left"
    elif -7*math.pi/8 <= angle < -5*math.pi/8:
        return "up_left"
    elif -5*math.pi/8 <= angle < -3*math.pi/8:
        return "up"
    else:
        return "up_right"
    
# ------------------------------------------------------------------------------------------
# TARGET CHECK
# ------------------------------------------------------------------------------------------
def reached_target(pet):
    return (
        abs(pet.label.x() - pet.target_x) < 3 and
        abs(pet.label.y() - pet.target_y) < 3
    )
def speak(pet):
    pass

def sleep(pet):
    pass
