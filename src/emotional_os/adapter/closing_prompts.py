from typing import List


CLOSING_PROMPTS: List[str] = [
	"Is there anything else I can help with?",
	"Would you like to continue or wrap up?",
]


def random_closing_prompt(seed: int = None) -> str:
	import random
	if seed is not None:
		random.seed(seed)
	return random.choice(CLOSING_PROMPTS)
