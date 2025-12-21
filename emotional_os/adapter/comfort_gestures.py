ASCII_COMFORT_MAP = {
    "hug": "(hugs)",
    "tap": "(gentle tap)",
}

def add_comfort_gesture(text: str, gesture: str = "hug") -> str:
    return text + " " + ASCII_COMFORT_MAP.get(gesture, "")
