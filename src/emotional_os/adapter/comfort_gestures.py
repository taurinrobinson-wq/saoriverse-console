from typing import List


COMFORT_GESTURES: List[str] = [
	"Take a deep breath.",
	"I'm here for you.",
]


def get_random_gesture(seed: int = None) -> str:
	import random
	if seed is not None:
		random.seed(seed)
	return random.choice(COMFORT_GESTURES)
