def polish_ai_reply(text: str) -> str:
	"""Minimal reply polishing used by tests.

	Behavior:
	- If the reply exactly matches a generic fallback, replace it with a
	  more specific alternative chosen deterministically/randomly.
	- Collapse duplicate adjacent blocks separated by blank lines.
	- Preserve long responses unchanged.
	"""
	import random

	if text is None:
		return ""

	s = text.strip()

	# If exact generic fallback, substitute one of the preferred alternatives
	generic_fallbacks = {"I'm here to listen.": [
		"I hear you, tell me more when you're ready.",
		"I'm listening. What's coming up for you right now?",
		"Thank you for sharing. I'm here to listen and support you.",
	]}

	if s in generic_fallbacks:
		return random.choice(generic_fallbacks[s])

	# Preserve long replies (heuristic: more than 140 chars)
	if len(s) > 140:
		return s

	# Collapse duplicate adjacent paragraphs separated by blank lines
	parts = [p.strip() for p in s.split("\n\n") if p.strip()]
	if not parts:
		return ""

	collapsed = []
	for p in parts:
		if not collapsed or p != collapsed[-1]:
			collapsed.append(p)

	result = "\n\n".join(collapsed)
	return result

__all__ = ["polish_ai_reply"]