import os
import random
from PyQt6.QtGui import QPixmap

BASE_DIR = os.path.dirname(__file__)
ASSETS = os.path.join(BASE_DIR, "assets")


def load_states(option):
    # -------------------------
    # SELECT SPRITE SHEET
    # -------------------------
    if option == 1:
        sheet_path = os.path.join(ASSETS, "cat 1.png")
    elif option == 2:
        sheet_path = os.path.join(ASSETS, "cat 2.png")
    elif option == 3:
        sheet_path = os.path.join(ASSETS, "cat 3.png")
    else:
        raise ValueError(f"Invalid option: {option}")

    if not os.path.exists(sheet_path):
        print(f"Error: Could not find {sheet_path}")
        return {}

    full_sheet = QPixmap(sheet_path)

    TILE_SIZE = 32  # each frame is 32x32

    # -------------------------
    # FRAME SLICER
    # -------------------------
    def get_frames(row, frame_count):
        frames = []
        for i in range(frame_count):
            x = i * TILE_SIZE
            y = row * TILE_SIZE
            frame = full_sheet.copy(x, y, TILE_SIZE, TILE_SIZE)
            frames.append(frame)
        return frames

    # -------------------------
    # IDLE (single row animation)
    # -------------------------
    idle_variants = [
        get_frames(row=0, frame_count=1) * 4 + get_frames(row=32, frame_count=8) + get_frames(row=0, frame_count=6),
        get_frames(row=0, frame_count=1) * 4 + get_frames(row=20, frame_count=8) + get_frames(row=33, frame_count=8),
        get_frames(row=0, frame_count=1) * 2 + get_frames(row=36, frame_count=8) * 2,
        get_frames(row=0, frame_count=1) * 4 + get_frames(row=39, frame_count=11) * 2,
        get_frames(row=0, frame_count=1) * 4 + get_frames(row=40, frame_count=11) * 2,
        get_frames(row=0, frame_count=1) * 1 + get_frames(row=37, frame_count=8) + get_frames(row=29, frame_count=3) + get_frames(row=0, frame_count=6)

        
    ]
    # -------------------------
    # WALK (8 directions)
    # -------------------------
    walk_frames = {
        "down": get_frames(row=4, frame_count=4),
        "down_left": get_frames(row=8, frame_count=6),
        "left": get_frames(row=7, frame_count=8),
        "up_left": get_frames(row=11, frame_count=6),
        "up": get_frames(row=5, frame_count=4),
        "up_right": get_frames(row=10, frame_count=6),
        "right": get_frames(row=6, frame_count=6),
        "down_right": get_frames(row=9, frame_count=6),
    }

    # -------------------------
    # SLEEP
    # -------------------------
    sleep_variants = [
        get_frames(row=12, frame_count=2),
        get_frames(row=13, frame_count=2),
        get_frames(row=14, frame_count=2),
        get_frames(row=15, frame_count=2),
        get_frames(row=16, frame_count=2),
        get_frames(row=17, frame_count=2),
        get_frames(row=18, frame_count=2),
        get_frames(row=19, frame_count=2)
    ]

    # -------------------------
    # SPEAK / SITTING ANIMATION
    # -------------------------
    speak_frames = get_frames(row=32, frame_count=8)

    # -------------------------
    # DRAG (when user drags the pet around)
    # -------------------------
    drag_frames = get_frames(row=43, frame_count=1)

    # -------------------------
    # RETURN STATE DICTIONARY
    # -------------------------
    return {
        "idle": {
            "variants": idle_variants,
            "fps": 4
        },
        "walk": {
            "frames": walk_frames, 
            "fps": 12
        },
        "sleep": {
            "variants": sleep_variants,
            "fps": 1
        },
        "speak": {
            "frames": speak_frames,
            "fps": 4
        },
        "drag": {
            "frames": drag_frames,
            "fps": 1
        }


    }

