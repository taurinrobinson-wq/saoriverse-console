import json
import os
import re
import sqlite3
from datetime import datetime
from difflib import SequenceMatcher
from typing import Dict, List, Optional

# Phase 2 learning + Sanctuary Mode imports
from emotional_os.glyphs.glyph_learner import GlyphLearner
from emotional_os.glyphs.learning_response_generator import create_training_response
from emotional_os.safety import (
    SANCTUARY_MODE,
    ensure_sanctuary_response,
    is_sensitive_input,
    sanitize_for_storage,
)

# Try to import NRC lexicon for better emotion detection
try:
    from parser.nrc_lexicon_loader import nrc
    HAS_NRC = True
except ImportError:
    HAS_NRC = False
    nrc = None

# Load signal lexicon from JSON (base + learned)
def load_signal_map(base_path: str, learned_path: str = "emotional_os/glyphs/learned_lexicon.json") -> Dict[str, Dict]:
	base_lexicon = {}
	if os.path.exists(base_path):
		with open(base_path, 'r', encoding='utf-8') as f:
			base_lexicon = json.load(f)

	learned_lexicon = {}
	if os.path.exists(learned_path):
		try:
			with open(learned_path, 'r', encoding='utf-8') as f:
				learned_lexicon = json.load(f)
		except Exception:
			pass

	# Ensure all entries are dictionaries
	for key, value in base_lexicon.items():
		if isinstance(value, str):
			base_lexicon[key] = {
				"signal": value,
				"voltage": "medium",
				"tone": "unknown"
			}

	for key, value in learned_lexicon.items():
		if isinstance(value, str):
			learned_lexicon[key] = {
				"signal": value,
				"voltage": "medium",
				"tone": "unknown"
			}

	combined_lexicon = base_lexicon.copy()
	combined_lexicon.update(learned_lexicon)
	return combined_lexicon

def fuzzy_match(word: str, lexicon_keys: List[str], threshold: float = 0.6) -> Optional[str]:
	"""Find best fuzzy match in lexicon, returns matching key if similarity > threshold"""
	best_match = None
	best_score = threshold

	for key in lexicon_keys:
		# Skip comment entries
		if key.startswith("_comment_"):
			continue

		score = SequenceMatcher(None, word.lower(), key.lower()).ratio()
		if score > best_score:
			best_score = score
			best_match = key

	return best_match

# Extract signals using fuzzy matching
def parse_signals(input_text: str, signal_map: Dict[str, Dict]) -> List[Dict]:
	lowered = input_text.lower()
	matched_signals = []
	lexicon_keys = [k for k in signal_map.keys() if not k.startswith("_comment_")]

	# First pass: exact word boundary matching in signal_lexicon
	for keyword, metadata in signal_map.items():
		if keyword.startswith("_comment_"):
			continue
		if re.search(rf"\b{re.escape(keyword)}\b", lowered) or keyword in lowered:
			if not isinstance(metadata, dict):
				metadata = {}
			matched_signals.append({
				"keyword": keyword,
				"signal": metadata.get("signal", "unknown"),
				"voltage": metadata.get("voltage", "medium"),
				"tone": metadata.get("tone", "unknown")
			})

	# Second pass: Use NRC lexicon if available for richer emotion detection
	if HAS_NRC and nrc and nrc.loaded:
		nrc_emotions = nrc.analyze_text(input_text)
		if nrc_emotions and not matched_signals:
			# Map NRC emotions to signal voltages
			nrc_to_signal = {
				'trust': ('β', 'medium', 'containment'),  # Boundary/trust
				'fear': ('θ', 'high', 'grief'),            # Fear/grief
				'negative': ('θ', 'high', 'grief'),        # General negative = grief
				'sadness': ('θ', 'medium', 'grief'),       # Sadness/grief
				'disgust': ('β', 'high', 'containment'),   # Rejection/boundary
				'anger': ('γ', 'high', 'longing'),         # Anger/longing
				'surprise': ('ε', 'medium', 'insight'),    # Surprise/insight
				'positive': ('λ', 'high', 'joy'),          # Positive/joy
				'anticipation': ('ε', 'medium', 'insight'),# Anticipation/insight
				'joy': ('λ', 'high', 'joy'),               # Joy
			}

			# Find strongest emotion from NRC
			top_emotion = max(nrc_emotions.items(), key=lambda x: x[1])[0]
			if top_emotion in nrc_to_signal:
				signal, voltage, tone = nrc_to_signal[top_emotion]
				matched_signals.append({
					"keyword": top_emotion,
					"signal": signal,
					"voltage": voltage,
					"tone": tone
				})

	# Third pass: fuzzy matching for unmatched single words
	if not matched_signals:
		words = re.findall(r'\b\w+\b', lowered)
		for word in words:
			if len(word) > 3:  # Only match words longer than 3 chars
				fuzzy_key = fuzzy_match(word, lexicon_keys, threshold=0.65)
				if fuzzy_key:
					metadata = signal_map.get(fuzzy_key, {})
					if not isinstance(metadata, dict):
						metadata = {}
					matched_signals.append({
						"keyword": fuzzy_key,
						"signal": metadata.get("signal", "unknown"),
						"voltage": metadata.get("voltage", "medium"),
						"tone": metadata.get("tone", "unknown")
					})
					break  # Use first good fuzzy match

	return matched_signals

# Map signals to ECM gates
def evaluate_gates(signals: List[Dict]) -> List[str]:
	ecm_gates = {
		"Gate 2": ["β", "θ"],
		"Gate 4": ["γ", "θ"],
		"Gate 5": ["λ", "ε", "δ"],
		"Gate 6": ["α", "Ω", "ε"],
		"Gate 9": ["α", "β", "γ", "δ", "ε", "Ω", "θ"],
		"Gate 10": ["θ"]
	}

	activated = []
	for gate, required in ecm_gates.items():
		if any(s["signal"] in required for s in signals):
			activated.append(gate)
	return activated

# Retrieve glyphs from SQLite
def fetch_glyphs(gates: List[str], db_path: str = 'glyphs.db') -> List[Dict]:
	if not gates:
		return []

	gates = [str(g) for g in gates]
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	placeholders = ','.join('?' for _ in gates)
	query = f"SELECT glyph_name, description, gate FROM glyph_lexicon WHERE gate IN ({placeholders})"
	try:
		print(f"[fetch_glyphs] Gates: {gates}")
		print(f"[fetch_glyphs] SQL: {query}")
		cursor.execute(query, gates)
		rows = cursor.fetchall()
		print(f"[fetch_glyphs] Rows: {rows}")
	except sqlite3.OperationalError as e:
		print(f"SQLite error: {e}")
		rows = []
	finally:
		conn.close()

	# For debug: attach SQL and rows to result if called from parse_input
	import inspect
	stack = inspect.stack()
	# Attach debug info to a global for UI debug drawer if called from parse_input
	if any('parse_input' in s.function for s in stack):
		global _last_glyphs_debug
		_last_glyphs_debug = {"sql": query, "rows": rows}
	return [{"glyph_name": r[0], "description": r[1], "gate": r[2]} for r in rows]

# Select most relevant glyph and generate contextual response
def select_best_glyph_and_response(glyphs: List[Dict], signals: List[Dict], input_text: str = "") -> tuple:
	if not glyphs:
		# Fallback: if no glyphs found via gates, search by emotion tone directly
		fallback_glyphs = _find_fallback_glyphs(signals, input_text)
		if fallback_glyphs:
			glyphs = fallback_glyphs
		else:
			return None, "I can sense there's something significant you're processing. Your emotions are giving you important information about your inner landscape. What feels most true for you right now?"

	# Get primary emotional signals
	primary_signals = [s['signal'] for s in signals]
	signal_keywords = [s['keyword'] for s in signals]

	# Prioritize glyphs based on emotional relevance
	scored_glyphs = []
	for glyph in glyphs:
		score = 0
		name = glyph['glyph_name'].lower()

		# Score based on emotional match
		if any(word in signal_keywords for word in ['overwhelmed', 'overwhelming', 'changes', 'shifting', 'uncertain']):
			if 'spiral' in name and 'containment' in name:
				score += 15  # "Spiral Containment" perfect for overwhelm with change
			elif 'containment' in name or 'boundary' in name:
				score += 12
			elif 'still' in name and 'ache' in name:
				score += 10  # "Still Ache" for processing difficulty
			elif 'clarity' in name or 'insight' in name:
				score += 8
		elif any(word in signal_keywords for word in ['anxious', 'anxiety', 'nervous', 'worry', 'stressed', 'racing']):
			if 'still' in name and 'insight' in name:
				score += 15  # "Still Insight" perfect for anxiety
			elif 'clarity' in name or 'insight' in name:
				score += 12
			elif 'still' in name and 'grief' not in name:
				score += 10
			elif 'containment' in name or 'boundary' in name:
				score += 8
		elif any(word in signal_keywords for word in ['sad', 'grief', 'mourning', 'loss', 'sad']):
			if 'grief' in name or 'mourning' in name:
				score += 10
		elif any(word in signal_keywords for word in ['angry', 'frustrated', 'rage', 'anger']):
			if 'ache' in name or 'longing' in name:
				score += 10
		elif any(word in signal_keywords for word in ['happy', 'joy', 'excited', 'delight']):
			if 'joy' in name or 'bliss' in name:
				score += 10
		elif any(word in signal_keywords for word in ['ashamed', 'shame', 'embarrassed', 'humiliated']):
			if 'boundary' in name or 'containment' in name:
				score += 10
			elif 'still' in name:
				score += 8
		elif any(word in signal_keywords for word in ['disappointed', 'failed', 'failure']):
			if 'ache' in name or 'longing' in name:
				score += 10
			elif 'recognition' in name or 'witness' in name:
				score += 8
		elif any(word in signal_keywords for word in ['broken', 'trap', 'trapped', 'stuck']):
			if 'containment' in name or 'boundary' in name or 'still' in name:
				score += 10

		# Prefer simpler, more accessible glyphs
		if any(word in name for word in ['still', 'quiet', 'gentle', 'soft']):
			score += 5

		scored_glyphs.append((glyph, score))

	# Select best glyph
	best_glyph = max(scored_glyphs, key=lambda x: x[1])[0] if scored_glyphs else None

	# Generate contextual response based on glyph and emotions
	response = generate_contextual_response(best_glyph, signal_keywords, input_text)

	return best_glyph, response

def _find_fallback_glyphs(signals: List[Dict], input_text: str) -> List[Dict]:
	"""Fallback: search database by emotion tone when gates don't return results"""
	if not signals:
		return []

	# Map tones to glyph name keywords
	tone_keywords = {}
	for signal in signals:
		tone = signal.get('tone', '').lower()
		if tone == 'grief':
			tone_keywords.setdefault('grief', []).extend(['grief', 'mourning', 'ache', 'sorrow', 'loss', 'collapse'])
		elif tone == 'longing':
			tone_keywords.setdefault('longing', []).extend(['ache', 'longing', 'yearning', 'recursive', 'disappointed', 'lonely'])
		elif tone == 'containment':
			tone_keywords.setdefault('containment', []).extend(['still', 'boundary', 'containment', 'shield', 'hold', 'stuck', 'trapped'])
		elif tone == 'insight':
			tone_keywords.setdefault('insight', []).extend(['insight', 'clarity', 'knowing', 'revelation', 'spiral', 'focus'])
		elif tone == 'joy':
			tone_keywords.setdefault('joy', []).extend(['joy', 'delight', 'bliss', 'ecstasy', 'brightness'])
		elif tone == 'devotion':
			tone_keywords.setdefault('devotion', []).extend(['devotional', 'vow', 'sacred', 'offering', 'ceremony'])
		elif tone == 'recognition':
			tone_keywords.setdefault('recognition', []).extend(['recognition', 'witness', 'seen', 'mirror', 'known'])

	if not tone_keywords:
		return []

	# Search database for glyphs matching tone keywords
	try:
		db_path = "emotional_os/glyphs/glyphs.db"
		if not os.path.exists(db_path):
			return []

		conn = sqlite3.connect(db_path)
		cursor = conn.cursor()

		# Build OR query for all tone keywords
		all_keywords = []
		for kw_list in tone_keywords.values():
			all_keywords.extend(kw_list)

		# Search for glyphs with names containing any keyword
		query_conditions = ' OR '.join(["glyph_name LIKE ?" for _ in all_keywords])
		query = f"SELECT glyph_name, description, gate FROM glyph_lexicon WHERE {query_conditions} LIMIT 5"

		params = [f"%{kw}%" for kw in all_keywords]
		cursor.execute(query, params)
		rows = cursor.fetchall()
		conn.close()

		return [{"glyph_name": r[0], "description": r[1], "gate": r[2]} for r in rows]
	except Exception:
		return []


def generate_contextual_response(glyph: Optional[Dict], keywords: List[str], input_text: str = "") -> str:
	name = glyph['glyph_name'] if glyph else ""
	description = glyph.get('description', '') if glyph else ''

	# Overwhelm/change responses
	if any(word in keywords for word in ['overwhelmed', 'overwhelming', 'changes', 'shifting', 'uncertain']):
		return "You're navigating a lot of moving pieces right now. When life shifts in multiple directions at once, it makes sense to feel overwhelmed. This isn't about weakness—it's about being human in the face of complexity. What feels like the most important piece to focus on first?"

	# Anxiety/stress responses
	if any(word in keywords for word in ['anxious', 'anxiety', 'nervous', 'worry', 'stressed', 'racing']):
		return "I can feel the anxiety you're carrying. When our minds race like this, it often helps to find a still point. The energy you're feeling - that's your system preparing you, even if it feels overwhelming right now. What if we could transform this racing energy into focused readiness?"

	# Sadness/grief responses
	if any(word in keywords for word in ['sad', 'grief', 'mourning', 'loss']):
		return "There's a heaviness you're holding, and it deserves to be witnessed. Grief moves at its own pace - not the pace we think it should. Your sorrow is valid and it's okay to feel the full weight of it."

	# Anger/frustration responses
	if any(word in keywords for word in ['angry', 'frustrated', 'rage', 'anger']):
		return "I can sense the intensity of what you're feeling. Anger often carries important information about our boundaries and values. What is this feeling trying to tell you about what matters to you?"

	# Joy/happiness responses
	if any(word in keywords for word in ['happy', 'joy', 'excited', 'delight']):
		return "There's brightness in what you're sharing. Joy deserves to be fully felt and celebrated. Let yourself receive this good feeling completely."

	# Shame/embarrassment responses
	if any(word in keywords for word in ['ashamed', 'shame', 'embarrassed', 'humiliated']):
		return "What you're feeling is deeply human. Shame often carries a message about our worth—but shame is a liar about that. You deserve compassion, especially from yourself. What would it feel like to offer yourself the same grace you'd give to someone you love?"

	# Disappointment/failure responses
	if any(word in keywords for word in ['disappointed', 'failed', 'failure']):
		return "I can sense the disappointment you're carrying. Unmet expectations can cut deep. But this moment of 'not succeeding' doesn't define your worth or your capability. What do you need to hear right now?"

	# Trapped/stuck responses
	if any(word in keywords for word in ['trapped', 'trap', 'stuck', 'broken']):
		return "Feeling trapped is exhausting. That sense of being locked in can feel so heavy. But you're here, you're aware, and you're reaching out—those are already signs of movement. What feels like the smallest possible shift you could make?"

	# Loneliness/misunderstanding responses
	if any(word in keywords for word in ['lonely', 'alone', 'nobody', 'understand']):
		return "Loneliness can make us feel so disconnected. But the very fact that you're trying to be understood shows there's a part of you still reaching out. You don't have to be alone in this. I'm here."

	# Strength/resilience doubts
	if any(word in keywords for word in ['strong', 'doubt', 'doubting']):
		return "Doubting your strength is actually part of being human. The very fact that you keep showing up despite your doubts? That's strength. You've likely already survived things you didn't think you could handle."

	# Growth/healing responses
	if any(word in keywords for word in ['learning', 'healing', 'proud', 'grateful', 'come far', 'letting go']):
		return "There's something beautiful in what you're sharing. Growth isn't linear, but the fact that you're noticing this moment of learning? That matters. You're building something real within yourself."

	# Default empathetic response
	return "I can sense there's something significant you're processing. Your emotions are giving you important information about your inner landscape. What feels most true for you right now?"

# Generate ritual prompt
def generate_simple_prompt(glyph: Dict) -> str:
	if not glyph:
		return ""
	return f"Would you like to take a moment to honor this feeling with the essence of '{glyph['glyph_name']}'?"

# Generate voltage response based on theme density
def generate_voltage_response(glyphs: List[Dict], conversation_context: Optional[Dict] = None) -> str:
	themes = {
		"grief": 0, "longing": 0, "containment": 0,
		"joy": 0, "devotion": 0, "recognition": 0, "insight": 0
	}

	for g in glyphs:
		name = g["glyph_name"].lower()
		if any(k in name for k in ["grief", "mourning", "collapse", "sorrow"]): themes["grief"] += 1
		if any(k in name for k in ["ache", "yearning", "longing", "recursive"]): themes["longing"] += 1
		if any(k in name for k in ["boundary", "contain", "still", "shield"]): themes["containment"] += 1
		if any(k in name for k in ["joy", "delight", "ecstasy", "bliss"]): themes["joy"] += 1
		if any(k in name for k in ["devotional", "vow", "exalted", "sacred"]): themes["devotion"] += 1
		if any(k in name for k in ["recognition", "seen", "witness", "mirror"]): themes["recognition"] += 1
		if any(k in name for k in ["insight", "clarity", "knowing", "revelation"]): themes["insight"] += 1

	dominant = sorted(themes.items(), key=lambda x: x[1], reverse=True)
	top_themes = [t[0] for t in dominant if t[1] > 0][:2]

	if top_themes == ["grief", "containment"]:
		return "You're holding a lot right now—and doing it with care. It's okay to feel the weight of it."

	if top_themes == ["grief", "longing"]:
		return "Deep grief mixed with yearning—that's the territory of profound loss."

	if top_themes == ["longing", "devotion"]:
		return "There's something you care about deeply, maybe even painfully. That kind of longing is sacred."

	if top_themes == ["joy", "recognition"]:
		return "You're being seen in your joy. Let it land."

	if top_themes == ["grief", "recognition"]:
		return "You're being seen in your sorrow. That kind of witnessing matters."

	return "You're carrying something layered. Let's sit with it and see what wants to be named."

# Main parser function
def parse_input(input_text: str, lexicon_path: str, db_path: str = 'glyphs.db', conversation_context: Optional[Dict] = None, user_id: Optional[str] = None) -> Dict:
	signal_map = load_signal_map(lexicon_path)
	signals = parse_signals(input_text, signal_map)
	gates = evaluate_gates(signals)
	glyphs = fetch_glyphs(gates, db_path)
	# Pull debug info from global if available
	debug_sql = ""
	debug_glyph_rows = []
	try:
		from emotional_os.glyphs import signal_parser
		if hasattr(signal_parser, '_last_glyphs_debug'):
			debug_sql = signal_parser._last_glyphs_debug.get("sql", "")
			debug_glyph_rows = signal_parser._last_glyphs_debug.get("rows", [])
	except Exception:
		pass
	# Select best glyph and generate contextual response
	best_glyph, contextual_response = select_best_glyph_and_response(glyphs, signals, input_text)
	ritual_prompt = generate_simple_prompt(best_glyph)

	# If no glyph matched, trigger learning pipeline to generate a candidate and craft a training response
	learning_payload = None
	if best_glyph is None and GlyphLearner and create_training_response:
		try:
			learner = GlyphLearner(db_path=db_path if db_path else "emotional_os/glyphs/glyphs.db")
			candidate = learner.analyze_input_for_glyph_generation(
				input_text=input_text,
				signals=signals,
				user_hash=None
			)
			# Sanitize source input before logging to storage
			if candidate.get("metadata"):
				candidate["metadata"]["source_input"] = sanitize_for_storage(candidate["metadata"].get("source_input", input_text))
			# Log candidate for review/learning
			learner.log_glyph_candidate(candidate)
			# Compose a training-oriented response
			emotional_tone = signals[0].get('tone', 'unknown') if signals else 'unknown'
			analysis = {
				"primary_tone": emotional_tone,
				"emotional_terms": candidate.get("emotional_terms", {}),
				"nrc_analysis": candidate.get("nrc_analysis", {}),
			}
			training_response = create_training_response(
				glyph_candidate=candidate,
				original_input=input_text,
				signals=signals,
				emotional_analysis=analysis
			)
			contextual_response = training_response or contextual_response
			learning_payload = {
				"candidate": {
					"glyph_name": candidate.get("glyph_name"),
					"description": candidate.get("description"),
					"gates": candidate.get("gates"),
					"confidence_score": candidate.get("confidence_score"),
				},
				"analysis": analysis,
			}
		except Exception:
			# If learning pipeline fails, retain the original contextual response
			pass

	# Sanctuary Mode: ensure compassionate handling for sensitive content
	primary_tone = signals[0].get('tone', 'unknown') if signals else 'unknown'
	if SANCTUARY_MODE or is_sensitive_input(input_text):
		contextual_response = ensure_sanctuary_response(
			input_text=input_text,
			base_response=contextual_response,
			tone=primary_tone
		)

	return {
		"timestamp": datetime.now().isoformat(),
		"input": input_text,
		"signals": signals,
		"gates": gates,
		"glyphs": glyphs,
		"best_glyph": best_glyph,
		"ritual_prompt": ritual_prompt,
		"voltage_response": contextual_response,  # Now contains the smart contextual response
		"debug_sql": debug_sql,
		"debug_glyph_rows": debug_glyph_rows,
		"learning": learning_payload
	}

# Example usage
if __name__ == "__main__":
	input_text = input("Enter emotional input: ")
	result = parse_input(input_text, "velonix_lexicon.json")
	print(json.dumps(result, indent=2, ensure_ascii=False))
