import os
from PyQt6.QtGui import QPixmap


BASE_DIR = os.path.dirname(__file__)
ASSETS = os.path.join(BASE_DIR, "assets")

def load_states(option):
    # Change 'cat_sheet.png' to the exact name of your file

    if option == 1:
        sheet_path = os.path.join("assets", "cat 1.png")
    elif option == 2:
        sheet_path = os.path.join("assets", "cat 2.png")
    elif option == 3:
        sheet_path = os.path.join("assets", "cat 3.png")

    if not os.path.exists(sheet_path):
        print(f"Error: Could not find {sheet_path}")
        return {}

    full_sheet = QPixmap(sheet_path)
    TILE_SIZE = 32  

    def get_frames(row, frame_count):
        """Slices a specific row from the sprite sheet."""
        frames = []
        for i in range(frame_count):
            x = i * TILE_SIZE
            y = row * TILE_SIZE
            frame = full_sheet.copy(x, y, TILE_SIZE, TILE_SIZE)
            frames.append(frame)
        return frames

    idle_frames = (get_frames(row=0, frame_count=1) * 6) + get_frames(row=36, frame_count=8)

    return {
        "idle": {
            "frames": idle_frames,
            "fps": 3
        },
        "walk": {
            "frames": get_frames(row=1, frame_count=8),
            "fps": 12
        },
        "sleep": {
            "frames": get_frames(row=12, frame_count=2),
            "fps": 1
        },
        "speak": {
            "frames": get_frames(row=32, frame_count=8), # Sitting/Idle while speaking
            "fps": 4
        }
    }

