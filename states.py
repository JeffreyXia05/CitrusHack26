import os
from PyQt6.QtGui import QPixmap

BASE_DIR = os.path.dirname(__file__)
ASSETS = os.path.join(BASE_DIR, "assets")

def load_states():
    # Path to your master sheet from itch.io
    # Change 'cat_sheet.png' to the exact name of your file
    sheet_path = os.path.join("assets", "cat 1.png")
    
    if not os.path.exists(sheet_path):
        print(f"Error: Could not find {sheet_path}")
        return {}

    full_sheet = QPixmap(sheet_path)
    TILE_SIZE = 32  # Each cat is 32x32

    def get_frames(row, frame_count):
        """Slices a specific row from the sprite sheet."""
        frames = []
        for i in range(frame_count):
            # QPixmap.copy(x, y, width, height)
            x = i * TILE_SIZE
            y = row * TILE_SIZE
            frame = full_sheet.copy(x, y, TILE_SIZE, TILE_SIZE)
            frames.append(frame)
        return frames

    # Map your rows to the kitty animations
    # Note: You may need to change the row numbers (0, 1, 2) 
    # depending on which cat/animation you want from the sheet.

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

# def load_states():
#     return {
#         "idle": {
#             "frames": [
#                 QPixmap(os.path.join(ASSETS, "idleCube.png")),
#                 #QPixmap(os.path.join(ASSETS, "idle2.png")),
#                 #QPixmap(os.path.join(ASSETS, "idle3.png")),
#             ],
#             "fps": 2
#         },

#         "walk": {
#             "frames": [
#                 QPixmap(os.path.join(ASSETS, "walkCube.png")),
#                 #QPixmap(os.path.join(ASSETS, "walk2.png")),
#                 #QPixmap(os.path.join(ASSETS, "walk3.png")),
#             ],
#             "fps": 6
#         },

#         "speak": {
#             "frames": [
#                 QPixmap(os.path.join(ASSETS, "speakCat.png")),
#                 #QPixmap(os.path.join(ASSETS, "speak2.png")),
#             ],
#             "fps": 3
#         },

#         "sleep": {
#             "frames": [
#                 QPixmap(os.path.join(ASSETS, "sleepCube.png")),
#                 #QPixmap(os.path.join(ASSETS, "sleep2.png")),
#             ],
#             "fps": 1
#         },
#     }

