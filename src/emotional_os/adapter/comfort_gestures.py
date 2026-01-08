from typing import List


COMFORT_GESTURES: List[str] = [
	"Take a deep breath.",
	"I'm here for you.",
]


# ASCII variants keyed by broad emotion categories. Tests expect this mapping.
ASCII_COMFORT_MAP = {
    "sadness": ["(；д；)", "(╯︵╰,)"],
    "joy": ["ヽ(＾Д＾)ﾉ", "｡^‿^｡"],
}


def get_random_gesture(seed: int = None) -> str:
	import random
	if seed is not None:
		random.seed(seed)
	return random.choice(COMFORT_GESTURES)


def add_comfort_gesture(emotion_key: str, text: str, position: str = "prepend", session_seed: str = None) -> str:
	"""Attach a comfort gesture to `text`.

	- If `COMFORT_GESTURES_ENABLED` env var is falsy, return `text` unchanged.
	- Prefer ASCII variants from `ASCII_COMFORT_MAP` when available.
	- If `session_seed` is provided, selection is deterministic for testing.
	- `position` controls whether the gesture is prepended or appended.
	"""
	import os
	import random

	enabled = os.environ.get("COMFORT_GESTURES_ENABLED", "true").lower()
	if enabled in ("0", "false", "no"):
		return text

	variants = ASCII_COMFORT_MAP.get(emotion_key) or COMFORT_GESTURES
	if session_seed is not None:
		random.seed(session_seed)
		gesture = random.choice(variants)
	else:
		gesture = random.choice(variants)

	if not text:
		return gesture
	if position == "append":
		return f"{text} {gesture}"
	return f"{gesture} {text}"

