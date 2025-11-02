import json
import os
from typing import Dict


class LexiconLearner:
	"""
	Learns new emotional patterns and language from conversations
	to build a medium language model without using AI
	"""
	def _load_lexicon(self, path: str) -> Dict[str, str]:
		"""Load lexicon from JSON file"""
		if os.path.exists(path):
			try:
				with open(path, 'r', encoding='utf-8') as f:
					return json.load(f)
			except Exception as e:
				print(f"Error loading {path}: {e}")
		return {}

	def _load_pattern_history(self) -> Dict:
		"""Load pattern learning history"""
		if os.path.exists(self.pattern_history_path):
			try:
				with open(self.pattern_history_path, 'r', encoding='utf-8') as f:
					return json.load(f)
			except Exception:
				pass
		return {
			'learned_patterns': [],
			'effectiveness_scores': {},
			'pattern_frequencies': {},
			'last_updated': None
		}

	def __init__(self, base_lexicon_path: str = "emotional_os/glyphs/signal_lexicon.json"):
		self.base_lexicon_path = base_lexicon_path
		self.learned_lexicon_path = "emotional_os/glyphs/learned_lexicon.json"
		self.pattern_history_path = "emotional_os/glyphs/pattern_history.json"
		self.base_lexicon = self._load_lexicon(base_lexicon_path)
		self.learned_lexicon = self._load_lexicon(self.learned_lexicon_path)
		self.pattern_history = self._load_pattern_history()
		# Emotional pattern templates
		self.emotional_patterns = {
			'feeling_expressions': [
				r'i feel (\w+)',
				r'feeling (\w+)',
				r'i\'m (\w+)',
				r'makes me (\w+)',
				r'i\'m experiencing (\w+)'
			],
			'intensity_modifiers': [
				r'very (\w+)',
				r'extremely (\w+)',
				r'deeply (\w+)',
				r'slightly (\w+)',
				r'intensely (\w+)'
			],
			'emotional_metaphors': [
				r'like a (\w+)',
				r'feels like (\w+)',
				r'reminds me of (\w+)',
				r'similar to (\w+)'
			]
		}
	# ...rest of migrated code unchanged...
