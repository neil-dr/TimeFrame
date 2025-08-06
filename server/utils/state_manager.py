all_modes = ["idle", "listening", "thinking", "speaking"]
mode: str = "idle"  # "idle" | "listening" | "thinking" | "speaking"


def set_mode(_mode: str):
    """
    Will only update mode if it valid
    """
    global mode
    if _mode in all_modes:
        mode = _mode


def get_mode() -> str:
    global mode
    return mode
