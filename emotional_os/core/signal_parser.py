import json
import logging
import os
import random
import re
import sqlite3
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional

# Centralized paths
from emotional_os.core.paths import (
    get_path_manager, signal_lexicon_path, learned_lexicon_path, glyph_db_path
)

# Phase 2 learning + Sanctuary Mode imports
from emotional_os.glyphs.glyph_learner import GlyphLearner
from emotional_os.glyphs.learning_response_generator import create_training_response
from emotional_os.glyphs.dynamic_response_composer import DynamicResponseComposer
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

# Try to import enhanced emotion processor for syntactic analysis
try:
    from parser.enhanced_emotion_processor import extract_syntactic_elements
    HAS_ENHANCED_PROCESSOR = True
except ImportError:
    HAS_ENHANCED_PROCESSOR = False
    extract_syntactic_elements = None

# Initialize dynamic response composer at module level
_response_composer = DynamicResponseComposer()

# Set up logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)

# Utility function for fuzzy pattern matching


def fuzzy_contains(input_str: str, patterns: list, threshold: float = 0.6) -> bool:
    """Check if input string contains or is similar to any pattern in the list.

    Priority:
    1. Exact substring match (highest priority)
    2. Sequence similarity match
    3. Token overlap (only if high overlap - at least 80% of pattern tokens match)
    """
    # Exact substring check first (fast and most reliable)
    for p in patterns:
        if p in input_str:
            return True

    # Sequence similarity on whole string
    for p in patterns:
        try:
            score = SequenceMatcher(None, input_str, p).ratio()
            if score >= threshold:
                return True
        except Exception:
            continue

    # Token overlap (strict - require high overlap)
    # Only use this if we need fuzzy matching beyond exact/similarity
    input_tokens = set(re.findall(r"\w+", input_str))
    for p in patterns:
        p_tokens = set(re.findall(r"\w+", p))
        if not p_tokens:
            continue
        # Require at least 80% of pattern tokens to match (strict)
        if len(p_tokens) > 0:
            overlap = len(input_tokens & p_tokens) / len(p_tokens)
            if overlap >= 0.8:  # Increase from 0.6 to 0.8 for stricter matching
                return True
    return False  # Load signal lexicon from JSON (base + learned)


def load_signal_map(base_path: str, learned_path: str = "emotional_os/glyphs/learned_lexicon.json") -> Dict[str, Dict]:
    base_lexicon = {}
    # Resolve base_path robustly: accept absolute paths, or resolve relative to the
    # project root via the PathManager. This prevents test-order/CWD flakiness.
    resolved_base = base_path
    try:
        if not os.path.isabs(base_path) or not os.path.exists(base_path):
            # Try resolving relative to the project base_dir
            pm = get_path_manager()
            candidate = pm.base_dir / base_path
            if candidate.exists():
                resolved_base = str(candidate)
            else:
                # Fallback to canonical signal lexicon path from path manager
                sig_path = signal_lexicon_path()
                if sig_path and sig_path.exists():
                    resolved_base = str(sig_path)
    except Exception:
        resolved_base = base_path

    if os.path.exists(resolved_base):
        with open(resolved_base, 'r', encoding='utf-8') as f:
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

    # Heuristic pruning: remove noisy or document-like keys introduced by bulk imports
    def _is_valid_key(k: str) -> bool:
        if not isinstance(k, str):
            return False
        k = k.strip()
        # Reject extremely long keys (probably entire titles or paragraphs)
        if len(k) > 60:
            return False
        # Reject keys with many non-alphanumeric characters (likely pasted content)
        if re.search(r"[^A-Za-z0-9\s\-']", k):
            return False
        # Reject keys with too many tokens (likely a sentence)
        if len(k.split()) > 6:
            return False
        # Accept otherwise
        return True

    pruned = {}
    for key, value in combined_lexicon.items():
        if key.startswith("_comment_"):
            pruned[key] = value
            continue
        if _is_valid_key(key):
            pruned[key] = value

    return pruned


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
    lexicon_keys = [k for k in signal_map.keys(
    ) if not k.startswith("_comment_")]

    # FIRST: Try enhanced NLP analysis if available
    try:
        from parser.enhanced_emotion_processor import enhance_gate_routing
        enhanced_routing = enhance_gate_routing(
            [], input_text)  # Start with empty existing signals
        if enhanced_routing['enhanced_signals']:
            matched_signals.extend(enhanced_routing['enhanced_signals'])
            logger.info(
                f"Enhanced NLP detected {len(enhanced_routing['enhanced_signals'])} signals")
    except ImportError:
        logger.debug(
            "Enhanced emotion processor not available, using traditional parsing")

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
                # General negative = grief
                'negative': ('θ', 'high', 'grief'),
                'sadness': ('θ', 'medium', 'grief'),       # Sadness/grief
                # Rejection/boundary
                'disgust': ('β', 'high', 'containment'),
                'anger': ('γ', 'high', 'longing'),         # Anger/longing
                # Surprise/insight
                'surprise': ('ε', 'medium', 'insight'),
                'positive': ('λ', 'high', 'joy'),          # Positive/joy
                # Anticipation/insight
                'anticipation': ('ε', 'medium', 'insight'),
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

    # Detect schema and ensure optional columns exist (display_name, response_template)
    try:
        cursor.execute("PRAGMA table_info(glyph_lexicon)")
        cols = [r[1] for r in cursor.fetchall()]
    except Exception:
        cols = []

    # If optional columns are missing, add them to the table (non-destructive)
    try:
        if 'display_name' not in cols:
            cursor.execute(
                "ALTER TABLE glyph_lexicon ADD COLUMN display_name TEXT")
        if 'response_template' not in cols:
            cursor.execute(
                "ALTER TABLE glyph_lexicon ADD COLUMN response_template TEXT")
        conn.commit()
    except Exception:
        # Some SQLite flavors in read-only environments may raise here; ignore
        pass

    select_cols = ['glyph_name', 'description',
                   'gate', 'display_name', 'response_template']
    query = f"SELECT {', '.join(select_cols)} FROM glyph_lexicon WHERE gate IN ({placeholders})"
    try:
        print(f"[fetch_glyphs] Gates: {gates}")
        print(f"[fetch_glyphs] SQL: {query}")
        cursor.execute(query, gates)
        rows = cursor.fetchall()
        # Avoid printing full row contents (may contain large/pasted artifacts).
        # Print a concise summary instead.
        row_count = len(rows)
        sample_names = [r[0] for r in rows[:6]]
        print(
            f"[fetch_glyphs] Retrieved {row_count} rows. Sample glyphs: {sample_names}")
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
        # Attach a sanitized debug payload: include SQL and a short preview of each row
        global _last_glyphs_debug
        debug_rows = []
        for r in rows:
            name = r[0]
            desc = r[1] or ''
            gate = r[2] if len(r) > 2 else None
            display_name = r[3] if len(r) > 3 else None
            response_template = r[4] if len(r) > 4 else None
            # Truncate long descriptions to a preview (200 chars) to avoid dumping raw documents
            preview = desc if len(desc) <= 200 else desc[:200].rsplit(
                '\n', 1)[0] + '...'
            debug_rows.append({
                "glyph_name": name,
                "display_name": display_name,
                "response_template": (response_template[:200] + '...') if response_template and len(response_template) > 200 else response_template,
                "description_preview": preview,
                "gate": gate
            })
        _last_glyphs_debug = {"sql": query, "rows": debug_rows}
    return [{"glyph_name": r[0], "description": r[1], "gate": r[2], "display_name": (r[3] if len(r) > 3 else None), "response_template": (r[4] if len(r) > 4 else None)} for r in rows]


def _looks_like_artifact(g: Dict) -> bool:
    """Heuristic: return True if this glyph row looks like an imported document, export, or archive artifact.

    This is intentionally conservative — we only filter rows that strongly match archive/export/markdown patterns
    or that contain unusually long/paged descriptions which are unlikely to be a single glyph.
    """
    if not g:
        return False
    name = (g.get('glyph_name') or '').lower()
    desc = (g.get('description') or '').lower()

    # Quick obvious markers
    markers = [
        'markdown export', 'json export', 'archive', 'gutenberg', 'conversation archive', 'archive entry',
        'markdown', 'json', 'export', 'module —', 'module -', 'file:', 'http://', 'https://', 'www.', '<html',
        '```', '***', 'title:', '📜', '📚', '🗂️'
    ]
    for m in markers:
        if m in name or m in desc:
            return True

    # Very long description bodies (likely pasted documents)
    if len(desc) > 800:
        return True

    # Many line breaks indicates pasted content
    if desc.count('\n') > 8:
        return True

    # Bracketed/tabled names are suspicious
    if '[' in name or '\t' in name:
        return True

    return False


def _normalize_display_name(glyph: Dict) -> str:
    """Return a short display name for the glyph.

    Priority:
    1. `display_name` field from DB if present and non-empty
    2. First sentence fragment from `glyph_name` (split on sentence punctuation)
    3. Truncate `glyph_name` to 40 chars
    """
    if not glyph:
        return ""
    dn = (glyph.get('display_name') or '')
    if dn and isinstance(dn, str) and dn.strip():
        return dn.strip()
    original = (glyph.get('glyph_name') or '')
    # Try to extract first sentence-like fragment
    if '.' in original:
        frag = original.split('.', 1)[0].strip()
        if frag:
            return frag if len(frag) <= 40 else frag[:40].rsplit(' ', 1)[0] + '...'
    # Also try newline or em-dash
    for sep in ['\n', '—', '–', ':', ';']:
        if sep in original:
            frag = original.split(sep, 1)[0].strip()
            if frag:
                return frag if len(frag) <= 40 else frag[:40].rsplit(' ', 1)[0] + '...'
    # Fallback: truncate
    if len(original) <= 40:
        return original
    return original[:40].rsplit(' ', 1)[0] + '...'

# Select most relevant glyph and generate contextual response


def select_best_glyph_and_response(glyphs: List[Dict], signals: List[Dict], input_text: str = "", conversation_context: Optional[Dict] = None) -> tuple:
    """
    Returns a quadruple: (best_glyph, (response_text, feedback_data), response_source, glyphs_selected)
    - glyphs_selected: list of glyph dicts augmented with 'score' and 'display_name', sorted by score desc
    response_source is one of: 'llm', 'dynamic_composer', 'fallback_message'
    """
    if not glyphs:
        # Fallback: if no glyphs found via gates, search by emotion tone directly
        fallback_glyphs = _find_fallback_glyphs(signals, input_text)
        if fallback_glyphs:
            glyphs = fallback_glyphs
        else:
            fallback_msg = "I can sense there's something significant you're processing. Your emotions are giving you important information about your inner landscape. What feels most true for you right now?"
            # Return an empty glyphs_selected list for backward-compatible 4-tuple API
            return None, (fallback_msg, {'is_correction': False, 'contradiction_type': None, 'feedback_reason': None}), 'fallback_message', []

    # Prune glyph rows that look like document fragments or deprecated artifacts
    def _glyph_is_valid(g: Dict) -> bool:
        name = (g.get('glyph_name') or '')
        desc = (g.get('description') or '')
        # Exclude obviously deprecated or artifact rows
        if 'deprecated' in name.lower() or 'deprecated' in desc.lower():
            return False
        # Exclude rows with bracketed index/tables or many newlines
        if '[' in name or '\t' in name:
            return False
        if desc.count('\n') > 6:
            return False
        # Exclude overly long names (likely titles or combined rows)
        if len(name) > 60:
            return False
        # Exclude descriptions that are extremely long (likely pasted documents)
        if len(desc) > 1000:
            return False
        # Exclude rows that match artifact/export/archive heuristics
        if _looks_like_artifact(g):
            return False
        return True

    filtered_glyphs = [g for g in glyphs if _glyph_is_valid(g)]
    if filtered_glyphs:
        glyphs = filtered_glyphs

    # Get primary emotional signals
    primary_signals = [s['signal'] for s in signals]  # noqa: F841  # intermediate extraction
    signal_keywords = [s['keyword'] for s in signals]

    # Extract syntactic elements for glyph matching boost
    syntactic_elements = {'nouns': [], 'verbs': [], 'adjectives': []}
    if HAS_ENHANCED_PROCESSOR and extract_syntactic_elements and input_text:
        try:
            syntactic_elements = extract_syntactic_elements(input_text)
            logger.debug(f"Syntactic elements extracted: {syntactic_elements}")
        except Exception as e:
            logger.debug(f"Failed to extract syntactic elements: {e}")

    # Prioritize glyphs based on emotional relevance
    scored_glyphs = []
    for glyph in glyphs:
        score = 0
        name = glyph['glyph_name'].lower()
        description = glyph.get('description', '').lower()

        # SIGNAL KEYWORD MATCH BOOST: If any extracted signal keyword appears in the
        # glyph name or description, give a substantial boost. This improves
        # matching when syntactic NLP isn't available and prevents the system from
        # being overly conservative (no glyph selected) for clearly related rows.
        for sk in signal_keywords:
            try:
                sk_l = sk.lower()
            except Exception:
                sk_l = str(sk)
            if sk_l and (sk_l in name or sk_l in description):
                score += 6
                logger.debug(
                    f"Signal-keyword boost: '{sk}' in glyph '{glyph['glyph_name']}' (+6)")

        # GLYPH MATCHING BOOST: Prioritize glyphs with matching syntactic elements
        if syntactic_elements['verbs']:
            # Boost for emotional verbs in glyph name or description
            for verb in syntactic_elements['verbs']:
                if verb in name or verb in description:
                    score += 8  # Strong boost for matching emotional verbs
                    logger.debug(
                        f"Verb match boost: '{verb}' in glyph '{glyph['glyph_name']}' (+8)")

        if syntactic_elements['nouns']:
            # Boost for emotional nouns in glyph name or description
            for noun in syntactic_elements['nouns']:
                if noun in name or noun in description:
                    score += 6  # Moderate boost for matching emotional nouns
                    logger.debug(
                        f"Noun match boost: '{noun}' in glyph '{glyph['glyph_name']}' (+6)")

        if syntactic_elements['adjectives']:
            # Boost for emotional adjectives in glyph name or description
            for adj in syntactic_elements['adjectives']:
                if adj in name or adj in description:
                    score += 4  # Smaller boost for matching emotional adjectives
                    logger.debug(
                        f"Adjective match boost: '{adj}' in glyph '{glyph['glyph_name']}' (+4)")

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
        # Removed small unconditional boost for 'still' to avoid over-weighting
        # short names like 'Still Recognition' when evidence is weak.
        # (No-op boost retained here for future tuning.)
        if any(word in name for word in ['quiet', 'gentle', 'soft']):
            score += 1

        scored_glyphs.append((glyph, score))

    # Select best glyph and top N glyphs above threshold
    best_glyph = None
    glyphs_selected = []
    if scored_glyphs:
        # Sort glyphs by score descending
        scored_sorted = sorted(scored_glyphs, key=lambda x: x[1], reverse=True)
        MIN_GLYPH_SCORE = 6
        MIN_GLYPH_SCORE_DELTA = 4

        # Build selected list: any glyph with score >= MIN_GLYPH_SCORE
        selected = [(g, s) for (g, s) in scored_sorted if s >= MIN_GLYPH_SCORE]
        # Back-compat: if nothing meets the score threshold but glyphs exist,
        # fall back to choosing the top-scoring glyph so we don't return empty.
        if not selected and scored_sorted:
            selected = [scored_sorted[0]]
        # Convert into normalized dicts with score and display_name
        for g, s in selected[:3]:
            augmented = dict(g)  # copy
            augmented['score'] = s
            augmented['display_name'] = _normalize_display_name(augmented)
            glyphs_selected.append(augmented)

        # For backward compatibility, best_glyph is the highest-scoring selected glyph (if any)
        if glyphs_selected:
            best_glyph = glyphs_selected[0]

    # Generate contextual response based on actual message content + glyph context
    # Returns tuple: (response_text, feedback_data)
    response, feedback_data = generate_contextual_response(
        best_glyph, signal_keywords, input_text, conversation_context)

    return best_glyph, (response, feedback_data), 'dynamic_composer', glyphs_selected


def _find_fallback_glyphs(signals: List[Dict], input_text: str) -> List[Dict]:
    """Fallback: search database by emotion tone when gates don't return results"""
    if not signals:
        return []

    # Map tones to glyph name keywords
    tone_keywords = {}
    for signal in signals:
        tone = signal.get('tone', '').lower()
        if tone == 'grief':
            tone_keywords.setdefault('grief', []).extend(
                ['grief', 'mourning', 'ache', 'sorrow', 'loss', 'collapse'])
        elif tone == 'longing':
            tone_keywords.setdefault('longing', []).extend(
                ['ache', 'longing', 'yearning', 'recursive', 'disappointed', 'lonely'])
        elif tone == 'containment':
            tone_keywords.setdefault('containment', []).extend(
                ['still', 'boundary', 'containment', 'shield', 'hold', 'stuck', 'trapped'])
        elif tone == 'insight':
            tone_keywords.setdefault('insight', []).extend(
                ['insight', 'clarity', 'knowing', 'revelation', 'spiral', 'focus'])
        elif tone == 'joy':
            tone_keywords.setdefault('joy', []).extend(
                ['joy', 'delight', 'bliss', 'ecstasy', 'brightness'])
        elif tone == 'devotion':
            tone_keywords.setdefault('devotion', []).extend(
                ['devotional', 'vow', 'sacred', 'offering', 'ceremony'])
        elif tone == 'recognition':
            tone_keywords.setdefault('recognition', []).extend(
                ['recognition', 'witness', 'seen', 'mirror', 'known'])

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
        query_conditions = ' OR '.join(
            ["glyph_name LIKE ?" for _ in all_keywords])
        query = f"SELECT glyph_name, description, gate FROM glyph_lexicon WHERE {query_conditions} LIMIT 5"

        params = [f"%{kw}%" for kw in all_keywords]
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [{"glyph_name": r[0], "description": r[1], "gate": r[2]} for r in rows]
    except Exception:
        return []


def detect_feedback_correction(input_text: str, last_assistant_message: Optional[str] = None) -> Dict:
    """Detect if user is correcting or contradicting a prior assistant response.

    Returns a dict with keys:
    - 'is_correction': bool indicating if feedback was detected
    - 'contradiction_type': str describing the type (e.g., 'negation', 'boundary', 'differentiation')
    - 'feedback_reason': str explaining why the correction was detected
    """
    if not last_assistant_message or not input_text:
        return {'is_correction': False, 'contradiction_type': None, 'feedback_reason': None}

    lower_input = input_text.lower()
    lower_prior = last_assistant_message.lower()

    # Pattern 1: User says "I don't know if it's MY anxiety" after assistant said "I can feel THE anxiety YOU'RE carrying"
    # This is: User rejecting attribution of the emotion as theirs
    if any(ph in lower_input for ph in ["don't know if it's my", "not my anxiety", "i don't have", "not sure if i", "isn't my"]):
        if "anxiety" in lower_prior and ("your" in lower_prior or "you're" in lower_prior):
            return {
                'is_correction': True,
                'contradiction_type': 'attribution_boundary',
                'feedback_reason': 'User rejected assistant attribution of emotion; clarified it is inherited, not theirs.'
            }

    # Pattern 2: User says "it's inherited FROM X" — boundary/differentiation
    if "inherited" in lower_input:
        return {
            'is_correction': True,
            'contradiction_type': 'inherited_pattern',
            'feedback_reason': 'User identified pattern as inherited rather than intrinsic.'
        }

    # Pattern 3: User says "that's not what I meant" or "you misunderstood"
    if any(ph in lower_input for ph in ["that's not", "i meant", "you missed", "you misunderstood", "that wasn't"]):
        return {
            'is_correction': True,
            'contradiction_type': 'misalignment',
            'feedback_reason': 'User indicated prior response did not match their intent.'
        }

    # Pattern 4: User provides strong negation before a new topic
    if input_text.strip().startswith(("no ", "nope", "actually,", "but actually")):
        return {
            'is_correction': True,
            'contradiction_type': 'negation',
            'feedback_reason': 'User opened with negation/correction.'
        }

    return {'is_correction': False, 'contradiction_type': None, 'feedback_reason': None}


def generate_contextual_response(glyph: Optional[Dict], keywords: List[str], input_text: str = "", conversation_context: Optional[Dict] = None, previous_responses: Optional[List[str]] = None) -> tuple:
    """Generate a contextual, non-repetitive empathetic response driven by message content.

    Returns a tuple: (response_text: str, feedback_detected: Dict)

    Strategy:
    - First, detect if user is correcting/contradicting prior assistant response.
    - Then, analyze the actual message content (not glyph) to generate response.
    - Glyph is used for context but response is message-driven.
    """
    name = glyph['glyph_name'] if glyph else ""
    description = glyph.get('description', '') if glyph else ''
    lower_input = (input_text or "").lower()

    # Detect feedback/corrections
    last_assistant_msg = None
    if conversation_context and isinstance(conversation_context, dict):
        last_assistant_msg = conversation_context.get('last_assistant_message')
    feedback_data = detect_feedback_correction(input_text, last_assistant_msg)

    # If feedback is detected, prioritize a response that addresses the correction
    if feedback_data.get('is_correction'):
        correction_type = feedback_data.get('contradiction_type')

        if correction_type == 'attribution_boundary':
            # User said: "it's not MY anxiety, it's inherited"
            base = (
                "Thank you for that clarification. That's an important distinction—what you're feeling might be proximity to anxiety rather than your own. "
                "When we're close to someone's anxious system, we can absorb its rhythm without it being intrinsically ours. "
                "Can you say more about what *you* are feeling, separate from what you pick up from Michelle?"
            )
            return _avoid_repeat(base, conversation_context, previous_responses), feedback_data

        elif correction_type == 'inherited_pattern':
            base = (
                "I hear that—recognizing a pattern as inherited is actually the first step to changing it. "
                "You can inherit the pattern without being imprisoned by it. "
                "What would it feel like to notice the difference between *her* anxiety and what's actually *yours*?"
            )
            return _avoid_repeat(base, conversation_context, previous_responses), feedback_data

        elif correction_type == 'misalignment':
            base = (
                "I appreciate you saying that. I want to make sure I'm actually hearing you, not projecting onto you. "
                "Help me understand: what did I miss?"
            )
            return _avoid_repeat(base, conversation_context, previous_responses), feedback_data

    # No feedback detected; proceed to message-driven response generation

    # CHECK: Does this message include reciprocal elements we should acknowledge first?
    has_gratitude = any(phrase in lower_input for phrase in [
                        'thank', 'appreciate', 'grateful'])
    has_reciprocal_interest = any(phrase in lower_input for phrase in [
                                  'how are you', 'how\'s your day', 'you doing'])

    # Prepend relational acknowledgment if message contains both reciprocal AND emotional content
    relational_prefix = None
    if has_gratitude or has_reciprocal_interest:
        if has_gratitude and has_reciprocal_interest:
            relational_prefix = "Thank you for asking. And thank you for trusting me with this. I'm here with you."
        elif has_gratitude:
            relational_prefix = "I appreciate that. Now, let's talk about what you're experiencing."
        elif has_reciprocal_interest:
            relational_prefix = "That's kind of you to ask. I'm focused on you right now."

    # MESSAGE-DRIVEN branches using dynamic composer
    # Build message content features for targeted response
    message_features = {
        "math_frustration": any(tok in lower_input for tok in ['math', 'not a math', 'mental block', 'math problem', 'maths']),
        "communication_friction": any(tok in lower_input for tok in ['michelle', 'mother-in-law', 'boss', 'korean', 'korean speaking', 'explains', 'language']),
        "mental_block": any(tok in lower_input for tok in ['block', 'blocked', 'can\'t', 'cannot', 'difficulty']),
        "inherited_pattern": 'inherited' in lower_input,
        "person_involved": "Michelle" if 'michelle' in lower_input else None,
    }

    # If any message-specific features detected, use dynamic composer
    if any(message_features.values()):
        composed = _response_composer.compose_message_aware_response(
            input_text=input_text,
            message_content=message_features,
            glyph=glyph,
        )
        if composed:
            # Prepend relational acknowledgment if present
            if relational_prefix:
                composed = f"{relational_prefix} {composed}"
            return _avoid_repeat(composed, conversation_context, previous_responses), feedback_data

    # Fall back to dynamic composition for general responses
    # Use the dynamic composer to generate non-templated responses
    composed = _response_composer.compose_response(
        input_text=input_text,
        glyph=glyph,
        feedback_detected=feedback_data.get('is_correction', False),
        feedback_type=feedback_data.get('contradiction_type'),
        conversation_context=conversation_context,
    )

    if composed:
        # Prepend relational acknowledgment if present
        if relational_prefix:
            composed = f"{relational_prefix} {composed}"
        return _avoid_repeat(composed, conversation_context, previous_responses), feedback_data

    # Ultimate fallback if composer fails
    base = "I'm here with you. What you're experiencing matters, and I'm listening."
    if relational_prefix:
        base = f"{relational_prefix} {base}"
    return _avoid_repeat(base, conversation_context, previous_responses), feedback_data


def _avoid_repeat(base_response: str, conversation_context: Optional[Dict], previous_responses: Optional[List[str]] = None) -> str:
    """If the base_response matches the last assistant message, try to vary it slightly.

    Variation strategy: if a prior identical response is detected in conversation_context['last_assistant_message'] or previous_responses,
    append a short follow-up question to nudge the user to a concrete next step. This is intentionally simple and deterministic.
    """
    last = None
    if previous_responses and isinstance(previous_responses, list) and previous_responses:
        last = previous_responses[-1]
    if not last and conversation_context and isinstance(conversation_context, dict):
        last = conversation_context.get('last_assistant_message')

    if last and last.strip() == base_response.strip():
        # Append a gentle, specific follow-up to avoid verbatim repetition
        followups = [
            "Can you tell me one specific detail about that?",
            "Would it help if we tried one small concrete step together?",
            "If you pick one thing to focus on right now, what would it be?"
        ]
        # Choose based on length of base response to keep variation deterministic
        idx = len(base_response) % len(followups)
        return base_response + " " + followups[idx]
    return base_response

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
        if any(k in name for k in ["grief", "mourning", "collapse", "sorrow"]):
            themes["grief"] += 1
        if any(k in name for k in ["ache", "yearning", "longing", "recursive"]):
            themes["longing"] += 1
        if any(k in name for k in ["boundary", "contain", "still", "shield"]):
            themes["containment"] += 1
        if any(k in name for k in ["joy", "delight", "ecstasy", "bliss"]):
            themes["joy"] += 1
        if any(k in name for k in ["devotional", "vow", "exalted", "sacred"]):
            themes["devotion"] += 1
        if any(k in name for k in ["recognition", "seen", "witness", "mirror"]):
            themes["recognition"] += 1
        if any(k in name for k in ["insight", "clarity", "knowing", "revelation"]):
            themes["insight"] += 1

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


def _detect_and_respond_to_reciprocal_message(input_text: str) -> Optional[str]:
    """
    Detect if the message is PRIMARILY conversational/relational (thanking, asking how system is, small talk).
    Only return early if the entire message is conversational.
    If there's emotional content mixed in, return None to let normal processing handle it.

    Returns the response if message is PURELY reciprocal, None if it has emotional content.
    """
    lower_input = input_text.lower()

    # Check if message has emotional/significant content
    emotional_keywords = [
        'burn', 'overwhelm', 'anxious', 'sad', 'frustrated', 'struggling', 'tired',
        'anxiety', 'anxiety', 'depression', 'grief', 'loss', 'afraid', 'fear',
        'angry', 'rage', 'shame', 'guilt', 'worry', 'stress', 'pain', 'hurt'
    ]
    has_emotional = any(
        keyword in lower_input for keyword in emotional_keywords)

    # If there's emotional content, let it be processed normally
    # (it might have reciprocal elements, but the emotional part is primary)
    if has_emotional:
        return None  # Process emotionally, don't short-circuit

    # Pure gratitude only (no emotional content)
    if any(phrase in lower_input for phrase in ['thank you', 'thanks', 'appreciate', 'grateful']):
        gratitude_responses = [
            "You're welcome. I'm here for you.",
            "Thank you for trusting me with this.",
            "That means something to me too.",
            "I appreciate you sharing.",
        ]
        return random.choice(gratitude_responses)

    # Pure reciprocal interest only (no emotional content)
    reciprocal_phrases = [
        'how are you', 'how are you doing', 'how are you feeling', "how's your day",
        "how's it going", 'you doing okay', 'you alright'
    ]

    # Fuzzy match helper: returns True if input is similar enough to any pattern
    def fuzzy_contains(input_str: str, patterns: list, threshold: float = 0.6) -> bool:
        # exact substring check first (fast)
        for p in patterns:
            if p in input_str:
                return True
        # fallback: sequence similarity on whole string
        for p in patterns:
            try:
                score = SequenceMatcher(None, input_str, p).ratio()
                if score >= threshold:
                    return True
            except Exception:
                continue
        # token overlap fallback
        input_tokens = set(re.findall(r"\w+", input_str))
        for p in patterns:
            p_tokens = set(re.findall(r"\w+", p))
            if not p_tokens:
                continue
            overlap = len(input_tokens & p_tokens) / len(p_tokens)
            if overlap >= 0.6:
                return True
        return False

    if fuzzy_contains(lower_input, reciprocal_phrases, threshold=0.55):
        reciprocal_responses = [
            "I'm here and present with you. That's what matters. But tell me—how are *you* doing?",
            "That's kind of you to ask. I'm focused on you right now. What's going on with you?",
            "I appreciate that. I'm steady. How about you—what's on your mind?",
            "I'm doing well because you're here. What brings you today?",
        ]
        return random.choice(reciprocal_responses)

    # FUNCTIONAL QUERIES - Trigger system explanation
    functional_patterns = [
        'how do you work', 'what do you do', 'how does this work', 'how does this system work',
        'explain what you do', 'what are you for', 'tell me how you work', 'what is this for',
        'how does this operate', 'tell me about your functions', 'what can you do', 'how can you help'
    ]

    if fuzzy_contains(lower_input, functional_patterns, threshold=0.5):
        return (
            "I'm a companion designed to listen and help you process feelings. "
            "I work by analyzing what you share—the emotions, patterns, and context—and responding with empathy and insight. "
            "I offer emotional support, practical suggestions, and quiet reflection. "
            "I'm here to help you understand yourself better and process what you're experiencing. "
            "What matters most is you. Would you like to share what's on your mind?"
        )

    # NAME INQUIRY PATTERNS - Asking what name the system goes by (not intending to rename yet)
    name_inquiry_patterns = [
        'what is your name', 'whats your name', 'what do you go by', 'do you have a name',
        'what are you called', 'who are you', 'tell me about yourself', 'tell me about you'
    ]

    if fuzzy_contains(lower_input, name_inquiry_patterns, threshold=0.5):
        # Name inquiry questions are now handled in parse_input directly
        # This is just a fallback - should not normally reach here
        return None

    # Profile / curiosity queries about the assistant itself (broader)
    profile_patterns = [
        'what is this', 'whats this', 'curious what this is', 'just curious',
        'who are you', 'what are you'
    ]

    # Use fuzzy_contains to catch paraphrases and misspellings
    if fuzzy_contains(lower_input, profile_patterns, threshold=0.5):
        return (
            "I'm a companion designed to listen and help you process feelings. "
            "I can offer emotional support, practical suggestions, and quiet reflection—whatever you need in the moment. "
            "If you'd like, I can say more about how I work or keep the focus on you."
        )

    # No reciprocal-only content detected
    return None


def parse_input(input_text: str, lexicon_path: str, db_path: str = 'glyphs.db', conversation_context: Optional[Dict] = None, user_id: Optional[str] = None) -> Dict:
    # FIRST: Check if this is just a simple greeting - don't process emotionally
    simple_greetings = ['hi', 'hello', 'hey', 'hi there',
                        'hello there', 'hey there', 'howdy', 'greetings']
    lower_input = input_text.strip().lower()

    if lower_input in simple_greetings:
        # Respond warmly but simply, without emotional analysis
        greeting_responses = [
            "Hi there. I'm here.",
            "Hello. What's on your mind?",
            "Hey. I'm listening.",
            "Hi. How are you doing?",
            "Hello. What brings you here?",
        ]
        response = random.choice(greeting_responses)
        return {
            "input": input_text,
            "signals": [],
            "gates": [],
            "glyphs": [],
            "best_glyph": None,
            "ritual_prompt": None,
            "voltage_response": response,
            "feedback": {'is_correction': False, 'contradiction_type': None, 'feedback_reason': None},
            "response_source": 'greeting',
            "debug_sql": "",
            "debug_glyph_rows": [],
            "learning": None
        }

    # SECOND: Check if this is casual/conversational (wanting to chat, just talking)
    # These shouldn't trigger emotional analysis
    casual_phrases = [
        'i just needed to chat',
        'i just wanted to talk',
        'i needed someone to talk to',
        'just wanted to chat',
        'just needed to talk',
        'felt like talking',
        'wanted to connect',
        'just checking in',
    ]
    if any(phrase in lower_input for phrase in casual_phrases):
        casual_responses = [
            "I'm here. What's on your mind?",
            "I'm glad you reached out. Tell me what you're thinking.",
            "I'm all ears. What's going on?",
            "I'm here for the conversation. What do you want to talk about?",
        ]
        response = random.choice(casual_responses)
        return {
            "input": input_text,
            "signals": [],
            "gates": [],
            "glyphs": [],
            "best_glyph": None,
            "ritual_prompt": None,
            "voltage_response": response,
            "feedback": {'is_correction': False, 'contradiction_type': None, 'feedback_reason': None},
            "response_source": 'casual',
            "debug_sql": "",
            "debug_glyph_rows": [],
            "learning": None
        }

    # Normal emotional processing for non-greeting, non-casual messages

    # CHECK: Is this a name submission for the naming ritual?
    # If user has just been asked "What would you like to call me?", lock in their choice
    if conversation_context and isinstance(conversation_context, dict):
        # conversation_context may contain a key with a None value; normalize to empty string
        last_assistant_msg = (conversation_context.get(
            'last_assistant_message') or '').lower()
        # Check if we EXPLICITLY asked "What would you like to call me?"
        if 'what would you like to call me' in last_assistant_msg or 'what would you call me' in last_assistant_msg:
            # This is likely a name submission (not a question)
            # Don't process things like "Do you have a name?" as submissions
            proposed_name = input_text.strip()
            # Check if it looks like a name (not a question mark, short, no question patterns)
            if (len(proposed_name) < 30 and not any(char in proposed_name for char in ['\n', '\t', '|', '?'])
                    and not proposed_name.lower().startswith(('what', 'do ', 'how ', 'why ', 'when ', 'where ', 'who ', 'is '))):
                # Valid name - lock it in
                response = (
                    f"✨ **{proposed_name}** — I'll call myself that for you from now on.\n\n"
                    f"There's something special about naming. It creates a small ceremony between us—"
                    f"a moment where you claimed what you want from this space. "
                    f"Thank you for that.\n\n"
                    f"Now, what brings you here today?"
                )
                # Store the user's chosen name in conversation_context for future reference
                if isinstance(conversation_context, dict):
                    conversation_context['user_assigned_name'] = proposed_name

                return {
                    "timestamp": datetime.now().isoformat(),
                    "input": input_text,
                    "signals": [],
                    "gates": [],
                    "glyphs": [],
                    "best_glyph": None,
                    "ritual_prompt": None,
                    "voltage_response": response,
                    "feedback": {'is_correction': False, 'contradiction_type': None, 'feedback_reason': None},
                    "response_source": 'naming_ritual',
                    "debug_sql": "",
                    "debug_glyph_rows": [],
                    "learning": None
                }

    # CHECK: Explicit naming intent - user wants to name the system NOW
    # Patterns: "Can I call you X", "I want to name you X", "I'll call you X"
    explicit_naming_patterns = [
        r"can i call you (\w+)",
        r"i want to (call you|name you) (\w+)",
        r"i'?ll call you (\w+)",
        r"let me call you (\w+)",
        r"you can be (\w+)",
        r"i'm naming you (\w+)",
        r"call yourself (\w+)"
    ]

    import re as regex_module
    for pattern in explicit_naming_patterns:
        match = regex_module.search(
            pattern, lower_input, regex_module.IGNORECASE)
        if match:
            # Extract the proposed name from regex groups
            proposed_name = None
            if len(match.groups()) >= 1:
                # Get the last non-empty group as it's the name
                proposed_name = next(
                    (g for g in reversed(match.groups()) if g), None)

            if proposed_name and len(proposed_name) < 30:
                # Valid naming submission - lock it in immediately
                proposed_name_display = proposed_name.capitalize()
                response = (
                    f"✨ **{proposed_name_display}** — I'll call myself that for you from now on.\n\n"
                    f"There's something special about naming. It creates a small ceremony between us—"
                    f"a moment where you claimed what you want from this space. "
                    f"Thank you for that.\n\n"
                    f"Now, what brings you here today?"
                )
                # Store the user's chosen name in conversation_context for future reference
                if conversation_context and isinstance(conversation_context, dict):
                    conversation_context['user_assigned_name'] = proposed_name_display

                return {
                    "timestamp": datetime.now().isoformat(),
                    "input": input_text,
                    "signals": [],
                    "gates": [],
                    "glyphs": [],
                    "best_glyph": None,
                    "ritual_prompt": None,
                    "voltage_response": response,
                    "feedback": {'is_correction': False, 'contradiction_type': None, 'feedback_reason': None},
                    "response_source": 'naming_ritual',
                    "debug_sql": "",
                    "debug_glyph_rows": [],
                    "learning": None
                }

    # CHECK: Is this a conversational/reciprocal message (thanking, asking how system is, small talk)?
    # If yes, respond conversationally FIRST before emotional analysis
    # BUT: Check for FUNCTIONAL QUERIES and NAME INQUIRY FIRST - these have priority

    # Guard clause: Check if this is ambiguous or special intent
    functional_patterns = [
        'how do you work', 'what do you do', 'how does this work', 'how does this system work',
        'explain what', 'tell me how', 'what are you for', 'how can you help',
        'tell me about your functions', 'how can i use'
    ]

    name_inquiry_patterns = [
        'what is your name', 'whats your name', 'what do you go by', 'do you have a name',
        'what are you called', 'what should i call you', 'how do i address you'
    ]

    # For name inquiry: require EXACT substring or very high sequence similarity (0.85+)
    # This prevents "what do you do" from matching "what do you go by"
    def strict_fuzzy_match(input_str: str, patterns: list, min_seq_similarity: float = 0.85) -> bool:
        """Strict matching: exact substring OR very high sequence similarity."""
        for p in patterns:
            if p in input_str:
                return True
        for p in patterns:
            try:
                score = SequenceMatcher(None, input_str, p).ratio()
                if score >= min_seq_similarity:
                    return True
            except Exception:
                continue
        return False

    # Check for name inquiry FIRST (stricter matching)
    is_name_inquiry = strict_fuzzy_match(
        lower_input, name_inquiry_patterns, min_seq_similarity=0.85)
    if is_name_inquiry:
        # Name inquiry - start naming ritual
        naming_response = (
            "I'm **Saori**—that's what I go by.\n\n"
            "But here's what makes this personal: you get to decide what you want to call me. "
            "Some people keep it as Saori. Others choose something that feels right to them.\n\n"
            "**What would you like to call me?** "
            "(You can change it anytime, but I'll use your choice for our conversations.)"
        )
        return {
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "signals": [],
            "gates": [],
            "glyphs": [],
            "best_glyph": None,
            "ritual_prompt": None,
            "voltage_response": naming_response,
            "feedback": {'is_correction': False, 'contradiction_type': None, 'feedback_reason': None},
            "response_source": 'name_inquiry',
            "debug_sql": "",
            "debug_glyph_rows": [],
            "learning": None
        }

    # Check for functional queries (use fuzzy matching)
    is_functional = fuzzy_contains(
        lower_input, functional_patterns, threshold=0.55)
    if is_functional:
        functional_response = (
            "I'm a companion designed to listen and help you process feelings. "
            "I work by analyzing what you share—the emotions, patterns, and context—and responding with empathy and insight. "
            "I offer emotional support, practical suggestions, and quiet reflection. "
            "I'm here to help you understand yourself better and process what you're experiencing. "
            "What matters most is you. Would you like to share what's on your mind?"
        )
        return {
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "signals": [],
            "gates": [],
            "glyphs": [],
            "best_glyph": None,
            "ritual_prompt": None,
            "voltage_response": functional_response,
            "feedback": {'is_correction': False, 'contradiction_type': None, 'feedback_reason': None},
            "response_source": 'functional_query',
            "debug_sql": "",
            "debug_glyph_rows": [],
            "learning": None
        }

    # Then check for other conversational messages
    conversational_response = _detect_and_respond_to_reciprocal_message(
        input_text)
    if conversational_response:
        # This is primarily a conversational/relational message
        # Include it in the response before diving into emotional content
        return {
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "signals": [],
            "gates": [],
            "glyphs": [],
            "best_glyph": None,
            "ritual_prompt": None,
            "voltage_response": conversational_response,
            "feedback": {'is_correction': False, 'contradiction_type': None, 'feedback_reason': None},
            "response_source": 'conversational',
            "debug_sql": "",
            "debug_glyph_rows": [],
            "learning": None
        }

    # Normal emotional processing for messages that aren't primarily conversational
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
    # Select best glyph(s) and generate contextual response (returns quadruple with glyphs_selected)
    result = select_best_glyph_and_response(
        glyphs, signals, input_text, conversation_context)
    # Unpack safely (backwards compatible with older triple return)
    if result and len(result) == 4:
        best_glyph, (contextual_response,
                     feedback_data), response_source, glyphs_selected = result
    else:
        best_glyph, (contextual_response,
                     feedback_data), response_source = result
        glyphs_selected = [best_glyph] if best_glyph else []

    ritual_prompt = generate_simple_prompt(best_glyph)

    # If no glyph matched, trigger learning pipeline to generate a candidate and craft a training response
    learning_payload = None
    if best_glyph is None and GlyphLearner and create_training_response:
        try:
            learner = GlyphLearner(
                db_path=db_path if db_path else "emotional_os/glyphs/glyphs.db")
            candidate = learner.analyze_input_for_glyph_generation(
                input_text=input_text,
                signals=signals,
                user_hash=None
            )
            # Sanitize source input before logging to storage
            if candidate.get("metadata"):
                candidate["metadata"]["source_input"] = sanitize_for_storage(
                    candidate["metadata"].get("source_input", input_text))
            # Log candidate for review/learning
            learner.log_glyph_candidate(candidate)
            # Compose a training-oriented response
            emotional_tone = signals[0].get(
                'tone', 'unknown') if signals else 'unknown'
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
    # If best_glyph has a response_template, surface it for UI rendering (do not overwrite contextual_response here)
    voltage_response_template = None
    try:
        if best_glyph and best_glyph.get('response_template'):
            voltage_response_template = best_glyph.get('response_template')
    except Exception:
        voltage_response_template = None

    return {
        "timestamp": datetime.now().isoformat(),
        "input": input_text,
        "signals": signals,
        "gates": gates,
        "glyphs": glyphs,
        "best_glyph": best_glyph,
        "glyphs_selected": glyphs_selected,
        "voltage_response_template": voltage_response_template,
        "ritual_prompt": ritual_prompt,
        # Now message-driven, not glyph-driven
        "voltage_response": contextual_response,
        "feedback": feedback_data,  # NEW: Track if user corrected/contradicted prior response
        "response_source": response_source,
        "debug_sql": debug_sql,
        "debug_glyph_rows": debug_glyph_rows,
        "learning": learning_payload
    }


# Example usage
if __name__ == "__main__":
    input_text = input("Enter emotional input: ")
    result = parse_input(input_text, "velonix_lexicon.json")
    print(json.dumps(result, indent=2, ensure_ascii=False))
