import win32gui

PET_TITLE_KEYWORD = "python3"

# ------------------------------------------------------------------------------------------
#  WINDOW MANAGEMENT
# ------------------------------------------------------------------------------------------
def get_windows():
    windows = []

    def enum_handler(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd)
        if not title.strip():
            return

        # ignore own app window
        if PET_TITLE_KEYWORD in title or title == "Settings" or title == "Windows Input Experience" or title == "Windows Shell Experience Host" or title == "Program Manager":
            return

        rect = win32gui.GetWindowRect(hwnd)

        # ignore zero-size windows 
        if rect[2] - rect[0] < 50 or rect[3] - rect[1] < 50:
            return

        windows.append({
            "title": title,
            "x1": rect[0],
            "y1": rect[1],
            "x2": rect[2],
            "y2": rect[3],
        })

    win32gui.EnumWindows(enum_handler, None)
    return windows


def get_window_under_pet(pet, windows):
    px1 = pet.label.x()
    py1 = pet.label.y()
    px2 = px1 + pet.label.width()
    py2 = py1 + pet.label.height()

    for w in windows:
        if (
            px1 >= w["x1"] and px2 <= w["x2"] and
            py1 >= w["y1"] and py2 <= w["y2"]
        ):
            return w

    return None

def get_window_center(w):
    return (
        (w["x1"] + w["x2"]) // 2,
        (w["y1"] + w["y2"]) // 2
    )