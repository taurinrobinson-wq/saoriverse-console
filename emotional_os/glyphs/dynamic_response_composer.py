#!/usr/bin/env python3
"""
Dynamic Response Composer

Generates emotionally attuned responses through composition rather than templates.
Instead of filling slots in canned responses, this system:

1. Extracts semantic entities (who, what, relationships) from user input
2. Identifies emotional resonance (via NRC, sentiment analysis)
3. Weaves poetic echoes and linguistic patterns that match the emotional contour
4. Constructs grammatically coherent responses that feel freshly generated

Result: No two responses are identical, even for similar emotional states.
"""

import json
import os
import random
import re
import sys
from typing import Dict, List, Optional, Tuple

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

try:
    from parser.semantic_engine import SemanticEngine
    from parser.nrc_lexicon_loader import nrc
    from parser.poetry_database import PoetryDatabase
except ImportError:
    SemanticEngine = None
    nrc = None
    PoetryDatabase = None

try:
    from emotional_os.adapter.response_adapter import translate_system_output
except Exception:
    translate_system_output = None


class DynamicResponseComposer:
    """Compose responses dynamically from linguistic fragments."""

    def __init__(self):
        """Initialize language resources."""
        self.semantic_engine = SemanticEngine() if SemanticEngine else None
        self.poetry_db = PoetryDatabase() if PoetryDatabase else None

        # Default list of canned phrases we often want to suppress
        # when users ask for briefer or less-canned replies.
        self.default_suppressions = [
            "i'm here with you",
            "what you're sharing matters",
            "you get to set the pace",
            "i notice something that matters to you",
            "does any of that resonate for you",
            "i hear you",
            "i'm listening",
            "resonant glyph: none",
            "processed in",
        ]

        # Linguistic patterns for different emotional contexts
        self.opening_moves = {
            "acknowledgment": [
                "I hear you about {entity}.",
                "There's something real in what you're saying about {entity}.",
                "That matters—{entity}.",
                "I'm here with you on {entity}.",
                "You're naming {entity}.",
            ],
            "validation": [
                "What you're describing about {entity} makes sense.",
                "I can hear how real {entity} feels.",
                "The {emotion} you're describing is justified.",
                "What you're feeling makes sense.",
                "That's a real thing to carry.",
            ],
            "curiosity": [
                "Tell me more about {entity}.",
                "What does that feel like for you?",
                "When you say {entity}, what do you mean by that?",
                "Help me understand a bit more about that.",
                "What's one small detail of {entity}?",
            ],
            "connection": [
                "You're not alone in this.",
                "Many people navigate things like this.",
                "What you're naming is deeply human.",
                "{entity} connects to something important in your life.",
                "I hear the feeling you're describing.",
            ],
        }

        self.emotional_bridges = {
            "inherited": [
                "Recognizing a pattern as inherited is the first step to changing it.",
                "You can inherit the pattern without being imprisoned by it.",
                "Naming where it comes from is powerful—that's differentiation.",
                "The fact that you can see it as inherited means you're not identical to it.",
                "Inherited doesn't mean fixed.",
            ],
            "misattribution": [
                "Thank you for clarifying—that distinction matters.",
                "I appreciate you correcting my assumption.",
                "That helps me understand you better.",
                "Let me recalibrate: what you're actually saying is...",
                "That's important—I was missing a layer.",
            ],
            "mental_block": [
                "A mental block is usually where the concept structure doesn't match how your mind works.",
                "The block isn't a character flaw—it's usually a mismatch between presentation and perception.",
                "That friction point often reveals something true about how you think best.",
                "Many brilliant minds hit friction with certain domains.",
                "The block is real, and navigable.",
            ],
            "friction": [
                "That friction is real—when communication styles clash.",
                "Misalignment in how people explain things creates real friction.",
                "That's not a failing on your part—it's a rhythm mismatch.",
                "When someone explains in a way only they can follow, that creates isolation.",
                "The friction you're naming is structural, not personal.",
            ],
        }

        self.movement_language = {
            "toward": [
                "You're moving toward understanding.",
                "There's a direction to what you're describing.",
                "You're building clarity.",
                "What you're doing is a form of becoming.",
                "The movement matters more than arrival.",
            ],
            "through": [
                "You're moving through this.",
                "The path goes through, not around.",
                "That kind of understanding requires passage.",
                "You're traversing something real.",
                "The only way forward is the way through.",
            ],
            "with": [
                "You're carrying this with presence.",
                "Hold it alongside yourself—not as burden.",
                "What you're doing is stewarding this.",
                "You can move with this rather than against it.",
                "Accompaniment is different from carrying alone.",
            ],
        }

        self.closing_moves = {
            "question": [
                "What would shift if you could see {entity} differently?",
                "What do you need to move forward with {entity}?",
                "How does {entity} want to be met?",
                "What would support you with {entity}?",
                "What's the next small step with {entity}?",
            ],
            "permission": [
                "You get to take this at your own pace with {entity}.",
                "There's no rush with {entity}.",
                "You're allowed to feel {emotion} about {entity}.",
                "You get to name what {entity} means to you.",
                "There's no wrong way to move through {entity}.",
            ],
            "commitment": [
                "I'm here with you through {entity}.",
                "We can navigate {entity} together.",
                "Let's walk this with {entity}.",
                "I'm not going anywhere with this.",
                "You're not alone in {entity}.",
            ],
        }

    def _extract_entities_and_emotions(self, text: str) -> Dict:
        """Extract key entities and emotional content from input."""
        result = {
            "entities": [],
            "emotions": [],
            "emotional_words": [],
            "people": [],
            "actions": [],
            "sentiment": None,
        }

        # Extract named entities if spaCy is available
        if self.semantic_engine and self.semantic_engine.loaded:
            result["entities"] = self.semantic_engine.get_noun_chunks(text)
            result["people"] = [ent[0] for ent in self.semantic_engine.extract_entities(
                text) if ent[1] == "PERSON"]
            result["actions"] = self.semantic_engine.extract_verbs(text)

        # Extract emotions using NRC if available
        if nrc:
            try:
                result["emotions"] = nrc.analyze_text(text)
            except:
                pass

        # Extract emotional language patterns
        emotional_keywords = [
            "anxiety", "anxious", "afraid", "fear", "block", "blocked",
            "inherited", "inherited pattern", "Michelle", "frustrated", "mad",
            "struggle", "friction", "communication", "misunderstand",
            "grief", "loss", "sorrow", "joy", "happy", "calm", "peaceful",
            "frustrated", "angry", "hurt", "ashamed", "confused", "clear",
            "isolated", "alone", "understood", "seen", "heard", "validated",
        ]

        text_lower = text.lower()
        for keyword in emotional_keywords:
            if keyword in text_lower:
                result["emotional_words"].append(keyword)

        return result

    def _select_opening(self, entities: List[str], emotions: Dict) -> str:
        """Select and instantiate an appropriate opening move."""
        # Determine which type of opening fits
        if "inherited" in str(emotions) or "inherited" in str(entities):
            opening_type = "acknowledgment"
        elif any(e in str(emotions) for e in ["anger", "frustration", "sadness"]):
            opening_type = "validation"
        else:
            opening_type = random.choice(list(self.opening_moves.keys()))

        # Select a variant
        opening = random.choice(self.opening_moves[opening_type])

        # Fill entity placeholder if present
        entity = entities[0] if entities else None
        entity = self._sanitize_entity(entity)
        opening = opening.replace("{entity}", entity)
        opening = opening.replace("{emotion}", emotions.get(
            "primary", "what you're feeling"))

        return opening

    def _sanitize_entity(self, entity: Optional[str]) -> str:
        """Sanitize extracted entity strings for user-facing text.

        Avoid returning pronouns or single-letter tokens like 'I' which create
        awkward grounding phrases. Return a friendly fallback when input is
        not meaningful.
        """
        if not entity:
            return "what you're experiencing"
        e = str(entity).strip()
        if not e:
            return "what you're experiencing"
        low = e.lower()
        # Avoid single-letter tokens or pronouns
        if low in {'i', 'me', 'my', 'you', 'your', 'yours', 'we', 'us'} or len(low) <= 2:
            return "what you're experiencing"
        return e

    def _postprocess_parts(self, parts: List[str]) -> List[str]:
        """Clean and normalize parts before joining into final text.

        - Trim whitespace
        - Remove very short fragments (<=2 words) unless they contain punctuation
        - Remove fragments that look like templates/placeholders (contain '{' or '}')
        - Remove fragments that are mostly quotes or start/end with mismatched quotes
        - Normalize capitalization and punctuation at sentence end
        - Deduplicate while preserving order
        """
        cleaned: List[str] = []
        seen = set()

        def normalize_sentence(s: str) -> str:
            s = s.strip()
            # Remove surrounding quotes if accidental
            if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
                s = s[1:-1].strip()
            # Avoid returning empty
            if not s:
                return ''
            # Ensure end punctuation
            if s[-1] not in '.!?':
                s = s + '.'
            # Capitalize first char
            s = s[0].upper() + s[1:]
            return s

        for p in parts:
            if not isinstance(p, str):
                continue
            s = p.strip()
            if not s:
                continue
            # Skip placeholder/template-like fragments
            if '{' in s or '}' in s:
                continue
            # Skip fragments that are clearly questions coming from templates
            if re.search(r'\bwhat does\b|\bwhat would\b', s.lower()) and s.count('?') == 0:
                # avoid lines that look like prompt fragments
                continue
            # Skip lines that are too short (likely artifacts). Allow if contains punctuation
            word_count = len(re.findall(r"[a-zA-Z]+", s))
            if word_count <= 2 and not re.search(r'[.!?]', s):
                continue
            # Remove lines that are basically single punctuation or stray quotes
            if all(ch in '"\'\n\r' for ch in s):
                continue

            s_norm = normalize_sentence(s)
            if not s_norm:
                continue
            if s_norm in seen:
                continue
            seen.add(s_norm)
            cleaned.append(s_norm)

        return cleaned

    def _sanitize_poetry_line(self, line: str) -> Optional[str]:
        """Return a single clean sentence from poetry if it's suitable.

        Reject lines that look like templates/questions or are too long/fragmented.
        """
        if not line:
            return None
        s = str(line).strip()
        # Remove surrounding quotes
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            s = s[1:-1].strip()
        # Replace newlines with spaces
        s = ' '.join(s.split())
        # Reject if it contains placeholders or braces
        if '{' in s or '}' in s:
            return None
        # Reject if it's clearly a direct question/template
        if s.lower().startswith(('what ', 'does ', 'is ', 'how ', 'would ')) and s.endswith('?'):
            return None
        # Enforce reasonable length
        if len(s) > 240 or len(s.split()) < 3:
            return None
        # Ensure ends with punctuation
        if not s.endswith(('.', '!', '?')):
            s = s + '.'
        # Capitalize first character
        s = s[0].upper() + s[1:]
        return s

    def _detect_brevity(self, text: str, conversation_context: Optional[Dict] = None) -> bool:
        """Detect whether the user has requested shorter/briefer replies.

        Checks recent text for common brevity requests and also inspects
        conversation_context for explicit flags set elsewhere in the app.
        """
        try:
            if conversation_context and isinstance(conversation_context, dict):
                # session/session-level preferences may use these keys
                if conversation_context.get('prefer_short') or conversation_context.get('user_brevity'):
                    return True

            t = (text or '').lower()
            brevity_patterns = [
                'keep it short', 'keep it shorter', 'shorter', 'short please', 'be brief',
                'keep it brief', 'shorter please', 'keep it concise', 'make it shorter',
                'can you keep it shorter', 'can you keep it short', 'please be brief'
            ]
            for p in brevity_patterns:
                if p in t:
                    return True
        except Exception:
            pass
        return False

    def _shorten_text(self, text: str, max_sentences: int = 2) -> str:
        """Return the first up to `max_sentences` sentences from text, removing
        commonly-repeated reassurance phrases to avoid repetition."""
        if not text:
            return text
        # Remove canned reassurance phrases seen in logs
        for canned in [
            "i'm here with you", "what you're sharing matters", "you won't be rejected or shamed for it",
            "your experience deserves care and gentle attention", "you get to set the pace",
            "if this brings up a lot, we can slow down or focus on one small piece at a time"
        ]:
            try:
                text = text.replace(canned, '')
                text = text.replace(canned.capitalize(), '')
            except Exception:
                pass

        # Split into sentences conservatively
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        chosen = [s.strip() for s in sentences if s.strip()][:max_sentences]
        if not chosen:
            # fallback: return first 120 chars
            return (text or '')[:120].strip()
        result = ' '.join(chosen)
        # Ensure punctuation at end
        if result and result[-1] not in '.!?':
            result = result + '.'
        return result

    def _apply_suppressions(self, text: str, suppress_list: Optional[List[str]] = None) -> str:
        """Remove any phrases in `suppress_list` from `text` (case-insensitive),
        and clean up extra whitespace/punctuation."""
        if not text or not suppress_list:
            return text
        r = text
        for sp in suppress_list:
            try:
                if not sp:
                    continue
                # Build a more robust pattern that strips the phrase even
                # when followed or preceded by punctuation/whitespace.
                pat = re.compile(r"(?i)\b" + re.escape(sp) +
                                 r"\b[\s\.,;:!?\-]*")
                r = pat.sub('', r)
            except Exception:
                try:
                    r = r.replace(sp, '')
                except Exception:
                    pass
        # Remove excessive whitespace and fix repeated punctuation
        r = re.sub(r'\s{2,}', ' ', r).strip()
        r = re.sub(r'\s+,', ',', r)
        # Trim leading/trailing punctuation left behind
        r = r.strip(' ,;:.')
        # Ensure sentence punctuation at end
        if r and r[-1] not in '.!?':
            r = r + '.'
        return r

    def _extract_stop_phrases(self, text: str) -> List[str]:
        """Parse user instructions like 'stop saying: "I'm here with you"' and return phrases to suppress."""
        if not text:
            return []
        t = text.lower()
        results: List[str] = []
        # Patterns like: stop saying: "phrase" or stop saying phrase
        m = re.findall(r"stop saying[:\s]+\"([^\"]+)\"", t)
        for g in m:
            results.append(g.strip())
        m2 = re.findall(r"stop saying[:\s]+'([^']+)'", t)
        for g in m2:
            results.append(g.strip())
        # fallback: 'stop saying X' where X is short phrase up to 6 words
        m3 = re.findall(r"stop saying\s+([a-zA-Z0-9\s]{1,80})", t)
        for g in m3:
            # filter obvious false positives
            g = g.strip()
            if len(g.split()) <= 10:
                results.append(g)
        # dedupe
        seen = []
        out = []
        for r in results:
            if r and r not in seen:
                seen.append(r)
                out.append(r)
        return out

    def _weave_poetry(self, text: str, emotions: Dict, glyphs: Optional[List[Dict]] = None, extracted: Optional[Dict] = None) -> Optional[str]:
        """Find and weave poetic echoes that match emotional contour."""
        if not self.poetry_db or not emotions:
            return None

        # Ensure glyphs/extracted are usable
        glyphs = glyphs or []
        extracted = extracted or {}

        # How many top glyph snippets to include in poetry/snippet composition.
        # Default to a small number to keep composed replies concise.
        top_n = min(3, max(1, len(glyphs)))
        # Map detected emotions to poetry categories
        primary_emotion = list(emotions.keys())[0] if emotions else None

        if not primary_emotion:
            return None

        # Get poetry matching the emotion
        poetry_lines = self.poetry_db.POETRY_COLLECTION.get(
            primary_emotion, [])
        if not poetry_lines:
            return None

        # Helper: map some activation symbols to human words
        sig_map = {
            'γ': 'longing', 'θ': 'relief', 'λ': 'tension', 'ζ': 'strain', 'χ': 'tenderness',
            'η': 'stillness', 'ξ': 'curiosity', 'μ': 'acceptance', 'ν': 'distance', 'β': 'difficulty',
            'ψ': 'rest', 'φ': 'vigilance', 'τ': 'restlessness', 'ο': 'calm', 'π': 'pressure',
            'σ': 'softness', 'ρ': 'weight', 'κ': 'constraint', 'δ': 'rupture', 'ω': 'completion',
            'ι': 'smallness', 'α': 'openness', 'ε': 'confusion'
        }

        # Small in-file stopword set to avoid an external NLTK dependency
        STOPWORDS = {
            'in', 'of', 'and', 'the', 'a', 'an', 'to', 'for', 'with', 'on', 'at', 'by', 'from',
            'is', 'are', 'that', 'this', 'it', 'as', 'be', 'was', 'were'
        }

        def _clean_phrase(phrase: str) -> str:
            if not phrase:
                return ''
            tokens = [t.strip().lower()
                      for t in re.findall(r"[a-zA-Z]+", phrase)]
            meaningful = [t for t in tokens if t and t not in STOPWORDS]
            return ' '.join(meaningful)

        def _glyph_intensity(g: Dict) -> int:
            gates = g.get('gates') or g.get('gate')
            if not gates:
                acts = g.get('activation_signals') or []
                return len(acts) if isinstance(acts, list) else (1 if acts else 0)
            return len(gates) if isinstance(gates, list) else 1

        def _glyph_primary_words(g: Dict) -> List[str]:
            acts = g.get('activation_signals') or []
            words = []
            for a in acts:
                if isinstance(a, str):
                    for ch in re.split(r'[;,\s]+', a):
                        if not ch:
                            continue
                        mapped = sig_map.get(ch.strip(), None)
                        if mapped:
                            words.append(mapped)
            if not words:
                name = g.get('glyph_name') or ''
                words = [t for t in re.findall(r"[a-zA-Z]+", name.lower())][:5]
            # Clean and dedupe
            cleaned = []
            for w in words:
                cw = _clean_phrase(w)
                if cw and cw not in cleaned:
                    cleaned.append(cw)
            return cleaned[:3]

        # Sentence template pools to add variation
        openers = [
            "I'm sensing",
            "There's a feeling of",
            "It sounds like you're carrying",
            "I hear",
            "This feels like"
        ]

        connectors = [
            "which seems important.",
            "and that may be part of what's shaping this.",
            "which could be worth staying with for a moment.",
            "and that feels connected to what you're describing.",
            "which might be tied to your experience right now."
        ]

        question_closers = [
            "Does any of that land for you?",
            "Is that on the right track?",
            "Does that resonate at all?",
            "If that feels right, tell me a bit more."
        ]

        # Rank glyphs by optional score and intensity
        ranked = sorted(glyphs, key=lambda g: (
            g.get('score', 0), _glyph_intensity(g)), reverse=True)

        parts: List[str] = []

        # Optional confidence-based summary using the top glyph
        dominant = ranked[0] if ranked else None
        if dominant and dominant.get('glyph_name'):
            summary_name = _clean_phrase(dominant.get(
                'glyph_name')) or dominant.get('glyph_name')
            parts.append(
                f"It seems the strongest theme here is {summary_name}.")

        # Opening move: grounded in detected entities/emotions
        opening = self._select_opening(extracted.get(
            'entities', []), extracted.get('emotions', {}))
        parts.append(opening)

        # Snippets from top glyphs with varied templates
        seen_snippets = set()
        snippet_count = 0
        for g in ranked:
            if snippet_count >= top_n:
                break
            gname = g.get('glyph_name') or ''
            gdesc = g.get('description') or ''
            intensity = _glyph_intensity(g)
            primary_words = _glyph_primary_words(g)

            # Build the phrase representing the glyph's core
            if primary_words:
                phrase = ', '.join(primary_words)
            else:
                phrase = _clean_phrase(gname) or gname

            # Choose varied opener + connector
            opener = random.choice(openers)
            connector = random.choice(connectors)

            # Grounding to entity or neutral 'this'
            entity = extracted.get('entities', [None])[0]
            grounding_ref = self._sanitize_entity(entity) or "this"

            # Compose snippet with intensity-aware phrasing
            if intensity >= 5:
                snippet = f"{opener} a strong sense of {phrase}, {connector}"
            else:
                snippet = f"{opener} {phrase}, {connector}"

            # Append grounding if sensible and not redundant
            if grounding_ref and grounding_ref.lower() not in snippet.lower():
                snippet = f"{snippet[:-1]} — that seems connected to {grounding_ref}."

            # Clean up whitespace and capitalization
            snippet = snippet.strip()

            if snippet in seen_snippets:
                continue
            seen_snippets.add(snippet)
            parts.append(snippet)
            snippet_count += 1

        # Optionally include a short poetry echo drawn from the available
        # `poetry_lines` for the detected primary emotion. We avoid calling
        # `_weave_poetry` recursively here (which previously caused infinite
        # recursion) and instead sanitize a candidate poetry line directly.
        if dominant:
            poetry_line = None
            for candidate in poetry_lines:
                p = self._sanitize_poetry_line(candidate)
                if p:
                    poetry_line = p
                    break
            if poetry_line:
                parts.append(poetry_line)

        # Curious closing question to invite user response
        closing_q = random.choice(question_closers)
        parts.append(closing_q)

        # Post-process parts: normalize sentences, dedupe and remove tiny fragments
        final_parts: List[str] = []
        seen = set()
        for p in parts:
            if not p or not isinstance(p, str):
                continue
            s = p.strip()
            # Normalize spacing
            s = ' '.join(s.split())
            # Ensure capitalization and punctuation
            if s and s[0].islower():
                s = s[0].upper() + s[1:]
            if s and not s.endswith(('.', '?', '!')):
                s = s + '.'
            # Avoid very short fragments
            if len(s) < 8:
                continue
            if s in seen:
                continue
            final_parts.append(s)
            seen.add(s)

        # If the last part is a generic question repeated, collapse duplicates
        if len(final_parts) >= 2 and final_parts[-1].lower() == final_parts[-2].lower():
            final_parts = final_parts[:-1]

        return "\n\n".join(final_parts)

        # 5. Closing move informed by glyph intensity, but phrased to person's situation
        if intensity_level <= 2:
            closing_move = "permission"
        elif intensity_level >= 8:
            closing_move = "commitment"
        else:
            closing_move = random.choice(["question", "permission"])

        entity = entities[0] if entities else "this"
        closing_template = random.choice(self.closing_moves[closing_move])
        closing = closing_template.replace("{entity}", entity)
        closing = closing.replace("{emotion}", list(emotions.keys())[
                                  0] if emotions else "what you feel")
        parts.append(closing)

        return " ".join(parts)

    def _glyph_to_emotion_category(self, glyph_name: str) -> Optional[str]:
        """Map glyph names to poetry emotion categories."""
        glyph_lower = glyph_name.lower() if glyph_name else ""

        emotion_map = {
            "still insight": "joy",
            "grief": "sadness",
            "ache": "sadness",
            "clarity": "joy",
            "joy": "joy",
            "peace": "joy",
            "stillness": "joy",
            "loss": "sadness",
            "mourning": "sadness",
            "yearning": "sadness",
            "longing": "sadness",
            "anger": "anger",
            "rage": "anger",
            "frustration": "anger",
            "shame": "sadness",
            "fear": "fear",
            "anxiety": "fear",
            "trust": "joy",
            "devotion": "joy",
            "recognition": "joy",
            "love": "joy",
        }

        for key, emotion in emotion_map.items():
            if key in glyph_lower:
                return emotion

        return None

    def _build_glyph_aware_response(
        self,
        glyph: Optional[Dict],
        entities: List[str],
        emotions: Dict,
        feedback_type: Optional[str] = None,
        input_text: str = "",
        extracted: Optional[Dict] = None,
    ) -> str:
        """
        Build a response grounded in the glyph's meaning and emotional signal.

        Args:
            glyph: Full glyph dict with name, description, emotional_signal, gates
            entities: Extracted entities from user input
            emotions: Detected emotions from user input
            feedback_type: Type of user correction if any
            input_text: User's original or combined input text
            extracted: Full extraction dict from _extract_entities_and_emotions

        Returns:
            Dynamically composed response anchored in glyph
        """
        parts = []

        # 1. Opening that acknowledges the entity and/or glyph tone
        opening = self._select_opening(entities, emotions)
        parts.append(opening)

        # 2. If there's feedback (correction), use bridging language
        if feedback_type:
            bridges = self.emotional_bridges.get(feedback_type) or []
            if bridges:
                bridge = random.choice(bridges)
                parts.append(bridge)

        # 3. Build middle: contextual movement language grounded in glyph
        if glyph:
            glyph_name = glyph.get('glyph_name', '')
            glyph_desc = glyph.get('description', '')

            # Use glyph description as inspiration for movement
            if glyph_desc:
                parts.append(glyph_desc)
            elif "block" in input_text.lower():
                movement = random.choice(self.movement_language["through"])
                parts.append(movement)
            elif "inherited" in input_text.lower():
                movement = random.choice(self.movement_language["with"])
                parts.append(movement)
        else:
            # Fallback when no glyph provided
            if "block" in input_text.lower():
                movement = random.choice(self.movement_language["through"])
            elif "inherited" in input_text.lower():
                movement = random.choice(self.movement_language["with"])
            else:
                movement = random.choice(
                    list(self.movement_language.values())[0])
            parts.append(movement)

        # 4. Weave poetry if available
        poetry_emotion = None
        if glyph:
            poetry_emotion = self._glyph_to_emotion_category(
                glyph.get('glyph_name', ''))

        poetry_emotions = {poetry_emotion: 0.8} if poetry_emotion else emotions
        poetry_line = self._weave_poetry(input_text, poetry_emotions, [glyph] if glyph else None, extracted or {
            'entities': entities, 'emotions': emotions})
        if poetry_line:
            parts.append(poetry_line)

        # 5. Closing move (question or commitment) calibrated by glyph intensity
        entity = self._sanitize_entity(entities[0] if entities else "this")

        # Determine closing type from glyph intensity if available
        closing_type = "question"
        if glyph:
            gates = glyph.get('gates') or glyph.get('gate')
            if gates:
                intensity = len(gates) if isinstance(gates, list) else 1
                if intensity <= 2:
                    closing_type = "permission"
                elif intensity >= 8:
                    closing_type = "commitment"

        closing_template = random.choice(self.closing_moves[closing_type])
        closing = closing_template.replace("{entity}", entity)
        closing = closing.replace("{emotion}", list(emotions.keys())[
                                  0] if emotions else "what you feel")
        parts.append(closing)

        return " ".join(parts)

    def _build_contextual_response(
        self,
        entities: List[str],
        emotions: Dict,
        feedback_type: Optional[str] = None,
        input_text: str = "",
    ) -> str:
        """Build contextual response acknowledging specific entities and emotions."""
        parts = []

        # 1. Opening that acknowledges the entity
        opening = self._select_opening(entities, emotions)
        parts.append(opening)

        # 2. If there's feedback (correction), use bridging language
        if feedback_type:
            bridges = self.emotional_bridges.get(feedback_type) or []
            if bridges:
                bridge = random.choice(bridges)
                parts.append(bridge)

        # 3. Build middle: contextual movement language
        if "block" in input_text.lower():
            movement = random.choice(self.movement_language["through"])
        elif "inherited" in input_text.lower():
            movement = random.choice(self.movement_language["with"])
        else:
            movement = random.choice(list(self.movement_language.values())[0])

        parts.append(movement)

        # 4. Weave poetry if available
        poetry_line = self._weave_poetry(input_text, emotions, None, {
                                         'entities': entities, 'emotions': emotions})
        if poetry_line:
            parts.append(poetry_line)

        # 5. Closing move (question or commitment)
        entity = entities[0] if entities else "this"
        closing_template = random.choice(self.closing_moves["question"])
        closing = closing_template.replace("{entity}", entity)
        closing = closing.replace("{emotion}", list(emotions.keys())[
                                  0] if emotions else "what you feel")
        parts.append(closing)

        return " ".join(parts)

    def compose_response(
        self,
        input_text: str,
        glyph: Optional[Dict] = None,
        feedback_detected: bool = False,
        feedback_type: Optional[str] = None,
        conversation_context: Optional[Dict] = None,
    ) -> str:
        """
        Compose a dynamic response that feels freshly generated, not templated.
        Response is grounded in the glyph's meaning and emotional signal.

        Args:
            input_text: User's message
            glyph: Full glyph dict with name, description, emotional_signal, gates
            feedback_detected: Whether user is correcting prior response
            feedback_type: Type of correction (inherited_pattern, misattribution, etc.)
            conversation_context: Prior messages, responses, etc.

        Returns:
            Dynamically composed response grounded in glyph
        """
        # Build a combined text that includes recent user context (if provided)
        # so the composer can detect mixed or evolving emotions across turns.
        combined_text = input_text
        try:
            if conversation_context and isinstance(conversation_context, dict):
                # Look for common conversation context shapes used by the UI/parser
                prev_user = None
                if 'last_user_message' in conversation_context:
                    prev_user = conversation_context.get('last_user_message')
                elif 'previous_user_message' in conversation_context:
                    prev_user = conversation_context.get(
                        'previous_user_message')
                else:
                    # Try to extract from messages/history lists
                    msgs = conversation_context.get(
                        'messages') or conversation_context.get('history')
                    if isinstance(msgs, list) and msgs:
                        # Find the last user message in the list
                        for m in reversed(msgs):
                            if isinstance(m, dict) and m.get('role') in ('user', 'User'):
                                prev_user = m.get('content') or m.get(
                                    'text') or m.get('user')
                                break
                            # older formats store entries as {'user':..., 'assistant':...}
                            if isinstance(m, dict) and 'user' in m and m.get('user'):
                                prev_user = m.get('user')
                                break
                if prev_user:
                    # prepend previous user text to detect cross-turn emotional combinations
                    combined_text = f"{prev_user.strip()} {input_text.strip()}"
        except Exception:
            # Defensive: if context parsing fails, fall back to input_text
            combined_text = input_text

        # Extract linguistic features from the combined text (captures cross-turn cues)
        extracted = self._extract_entities_and_emotions(combined_text)
        # Detect if user asked for brevity and shorten the final output when appropriate
        brief = self._detect_brevity(combined_text, conversation_context)

        # Build core response anchored in glyph
        response = self._build_glyph_aware_response(
            glyph=glyph,
            entities=extracted["entities"],
            emotions=extracted["emotions"],
            feedback_type=feedback_type if feedback_detected else None,
            input_text=combined_text,
            extracted=extracted,
        )

        if brief:
            try:
                # When a session-level prefer_short is set, enforce stricter
                # single-sentence behavior so the reply is concise.
                if conversation_context and isinstance(conversation_context, dict) and conversation_context.get('prefer_short'):
                    # pick a single short sentence (1) and apply suppressions
                    brief_resp = self._shorten_text(response, max_sentences=1)
                    # merge default suppressions + conversation suppressions
                    supp = list(self.default_suppressions)
                    try:
                        sess = conversation_context.get(
                            'suppress_phrases') or []
                        if isinstance(sess, list):
                            supp += [s for s in sess if s]
                    except Exception:
                        pass
                    if supp:
                        brief_resp = self._apply_suppressions(brief_resp, supp)
                    return brief_resp
                return self._shorten_text(response, max_sentences=2)
            except Exception:
                return response

        # Respect explicit 'stop saying' requests persisted in conversation_context
        try:
            stop_phrases = []
            # Extract anything said in this message
            try:
                stop_phrases += self._extract_stop_phrases(combined_text)
            except Exception:
                pass

            # Merge any session/conversation-level suppressions
            if conversation_context and isinstance(conversation_context, dict):
                try:
                    sess_suppress = conversation_context.get(
                        'suppress_phrases') or []
                    if isinstance(sess_suppress, list):
                        stop_phrases += [s for s in sess_suppress if s]
                except Exception:
                    pass

            # Deduplicate
            seen = []
            merged = []
            for s in stop_phrases:
                if s and s not in seen:
                    seen.append(s)
                    merged.append(s)

            if merged:
                # Merge default suppressions too
                merged_all = list(self.default_suppressions) + merged
                return self._apply_suppressions(response, merged_all)
        except Exception:
            pass

        return response

    def compose_message_aware_response(
        self,
        input_text: str,
        message_content: Dict,
        glyph: Optional[Dict] = None,
    ) -> str:
        """
        Compose response addressing the PERSON'S specific content.

        Glyph used invisibly to calibrate tone/intensity, but response feels
        personalized to their actual situation, not a glyph category.

        Example message_content:
        {
            "math_frustration": True,
            "mental_block": True,
            "person_involved": "Michelle",
            "communication_friction": True,
        }
        """
        parts = []

        # Determine tone intensity from glyph (used invisibly)
        intensity = 1
        if glyph:
            gate_data = glyph.get("gates") or glyph.get("gate")
            if gate_data:
                gates_list = gate_data if isinstance(
                    gate_data, list) else [gate_data]
                intensity = len(gates_list)

        # Respond to their actual content, not a glyph category
        if message_content.get("math_frustration"):
            parts.append(
                "You're not alone—many brilliant people have genuine friction with math, "
                "especially when it's presented in a way that doesn't match how their mind naturally works."
            )

        if message_content.get("communication_friction"):
            person = message_content.get("person_involved", "someone")
            parts.append(
                f"When {person} explains something in a way that only they can follow, "
                "that creates real isolation. That's not a failing on your part—it's a rhythm mismatch."
            )

        if message_content.get("mental_block"):
            parts.append(
                "Mental blocks are usually where the concept structure doesn't match your natural thinking pattern. "
                "That's not fixed—it's just a mismatch to navigate."
            )

        if message_content.get("inherited_pattern"):
            parts.append(
                "And when something comes from somewhere else—from someone we're close to—"
                "we can end up carrying their pattern without it being ours to carry."
            )

        # Reflection question calibrated to intensity
        main_struggle = [k for k, v in message_content.items() if v]
        if main_struggle:
            # High intensity = more commitment, low intensity = gentler question
            if intensity >= 8:
                question = f"I'm here to work through {main_struggle[0].replace('_', ' ')} with you."
            else:
                question = f"What would it feel like to approach {main_struggle[0].replace('_', ' ')} differently?"
            parts.append(question)

        return " ".join(parts)

    def compose_multi_glyph_response(
        self,
        input_text: str,
        glyphs: List[Dict],
        feedback_detected: bool = False,
        feedback_type: Optional[str] = None,
        conversation_context: Optional[Dict] = None,
        top_n: int = 5,
    ) -> str:
        """
        Compose a single, nuanced response from multiple glyphs.

        This method accepts a ranked list of glyph dictionaries (preferably the
        top-N candidates) and weaves their tones, implied voltages, and gate
        intensities into a single composed reply. It avoids canned single-glyph
        responses by blending short, focused snippets derived from each glyph
        and grounding them in the user's input.
        """
        # Combine recent context like compose_response does
        combined_text = input_text
        try:
            if conversation_context and isinstance(conversation_context, dict):
                prev_user = None
                if 'last_user_message' in conversation_context:
                    prev_user = conversation_context.get('last_user_message')
                elif 'previous_user_message' in conversation_context:
                    prev_user = conversation_context.get(
                        'previous_user_message')
                else:
                    msgs = conversation_context.get(
                        'messages') or conversation_context.get('history')
                    if isinstance(msgs, list) and msgs:
                        for m in reversed(msgs):
                            if isinstance(m, dict) and m.get('role') in ('user', 'User'):
                                prev_user = m.get('content') or m.get(
                                    'text') or m.get('user')
                                break
                            if isinstance(m, dict) and 'user' in m and m.get('user'):
                                prev_user = m.get('user')
                                break
                if prev_user:
                    combined_text = f"{prev_user.strip()} {input_text.strip()}"
        except Exception:
            combined_text = input_text

        # Early strict brevity enforcement: if the session explicitly
        # requests short replies, return a deterministic single-sentence
        # reply before composing multi-part responses. This avoids the
        # composer assembling multiple fragments that are then shortened
        # and may still include canned lines.
        try:
            if conversation_context and isinstance(conversation_context, dict) and conversation_context.get('prefer_short'):
                # Prefer a glyph-grounded one-line summary when glyphs exist
                summary_words = []
                for g in (glyphs or [])[:2]:
                    try:
                        summary_words.extend(_glyph_primary_words(g))
                    except Exception:
                        pass
                if summary_words:
                    reply = f"I hear you. ({', '.join(summary_words[:6])})"
                else:
                    reply = "I hear you."

                # Apply default + session suppressions before returning
                merged = list(self.default_suppressions)
                try:
                    sess = conversation_context.get('suppress_phrases') or []
                    if isinstance(sess, list):
                        merged += [s for s in sess if s]
                except Exception:
                    pass

                if merged:
                    reply = self._apply_suppressions(reply, merged)

                return self._shorten_text(reply, max_sentences=1)
        except Exception:
            pass

        # Extract entities/emotions for grounding
        extracted = self._extract_entities_and_emotions(combined_text)

        # Limit glyphs to top_n
        glyphs = glyphs[:top_n] if glyphs else []

        # Helper: map some activation symbols to human words
        sig_map = {
            'γ': 'longing', 'θ': 'relief', 'λ': 'tension', 'ζ': 'strain', 'χ': 'tenderness',
            'η': 'stillness', 'ξ': 'curiosity', 'μ': 'acceptance', 'ν': 'distance', 'β': 'difficulty',
            'ψ': 'rest', 'φ': 'vigilance', 'τ': 'restlessness', 'ο': 'calm', 'π': 'pressure',
            'σ': 'softness', 'ρ': 'weight', 'κ': 'constraint', 'δ': 'rupture', 'ω': 'completion',
            'ι': 'smallness', 'α': 'openness', 'ε': 'confusion'
        }

        def _glyph_intensity(g: Dict) -> int:
            gates = g.get('gates') or g.get('gate')
            if not gates:
                # fallback to number of activation signals
                acts = g.get('activation_signals') or []
                return len(acts) if isinstance(acts, list) else (1 if acts else 0)
            return len(gates) if isinstance(gates, list) else 1

        def _glyph_primary_words(g: Dict) -> List[str]:
            acts = g.get('activation_signals') or []
            words = []
            for a in acts:
                if isinstance(a, str):
                    # activation signals may be comma-separated
                    for ch in re.split(r'[;,\s]+', a):
                        if not ch:
                            continue
                        mapped = sig_map.get(ch.strip(), None)
                        if mapped:
                            words.append(mapped)
            # fallback: include glyph name tokens
            if not words:
                name = g.get('glyph_name') or ''
                words = [t for t in re.findall(r"[a-zA-Z]+", name.lower())][:3]
            return words

        # Rank glyphs by intensity (and optional provided score)
        ranked = sorted(glyphs, key=lambda g: (
            g.get('score', 0), _glyph_intensity(g)), reverse=True)

        parts: List[str] = []

        # Opening move: use dominant glyph to pick tone
        dominant = ranked[0] if ranked else None
        opening = self._select_opening(extracted.get(
            'entities', []), extracted.get('emotions', {}))
        parts.append(opening)

        # If the user requested brevity, produce a concise reply: a short
        # acknowledgment plus a one-line, glyph-grounded summary.
        brief = self._detect_brevity(combined_text, conversation_context)
        if brief:
            try:
                summary_words = []
                for g in ranked[:2]:
                    summary_words.extend(_glyph_primary_words(g))
                summary_words = [w for w in summary_words if w]
                if summary_words:
                    brief_line = f"I hear you. ({', '.join(summary_words[:6])})"
                else:
                    brief_line = "I hear you."

                # Collect stop-phrases from message + session
                stop_phrases = []
                try:
                    stop_phrases += self._extract_stop_phrases(combined_text)
                except Exception:
                    pass
                try:
                    if conversation_context and isinstance(conversation_context, dict):
                        sess_suppress = conversation_context.get(
                            'suppress_phrases') or []
                        if isinstance(sess_suppress, list):
                            stop_phrases += [s for s in sess_suppress if s]
                except Exception:
                    pass

                bl = brief_line
                # If session-level prefer_short is set, enforce stricter brevity
                if conversation_context and isinstance(conversation_context, dict) and conversation_context.get('prefer_short'):
                    merged = list(self.default_suppressions) + \
                        list(dict.fromkeys(stop_phrases))
                    if merged:
                        bl = self._apply_suppressions(bl, merged)
                    return self._shorten_text(bl, max_sentences=1)

                # Otherwise, apply only the discovered stop_phrases
                if stop_phrases:
                    bl = self._apply_suppressions(
                        bl, list(dict.fromkeys(stop_phrases)))
                return self._shorten_text(bl, max_sentences=1)
            except Exception:
                return self._shorten_text(opening, max_sentences=1)

        # Prefer using the response adapter to translate glyphs into
        # plain-language summary and short snippets. Fallback to older
        # snippet composition if the adapter is not available.
        if translate_system_output:
            try:
                adapter_input = {
                    'glyphs': glyphs,
                    'extracted': extracted,
                    'context': conversation_context,
                }
                adapter_out = translate_system_output(
                    adapter_input, top_n=top_n, user_context=conversation_context)
                # summary may be a short phrase like 'recurring ache'
                summary = adapter_out.get('summary')
                snippets = adapter_out.get('snippets') or []
                tone = adapter_out.get('tone') or 'neutral'
                invitation = adapter_out.get('invitation') or None

                if summary:
                    parts.append(f"I notice {summary}.")

                for s in snippets:
                    # Ensure we don't duplicate the summary line
                    if s and s not in parts:
                        parts.append(s)

                # Use adapter invitation as a closing move if provided
                if invitation:
                    parts.append(invitation)

                # Post-process composed parts (clean fragments, punctuation, dedupe)
                try:
                    processed = self._postprocess_parts(parts)
                    if processed:
                        result = "\n\n".join(processed)
                        # Apply default + session-level suppressions before returning
                        try:
                            sess = conversation_context.get('suppress_phrases') if conversation_context and isinstance(
                                conversation_context, dict) else []
                            merged = list(
                                self.default_suppressions) + (sess or [])
                            if merged:
                                result = self._apply_suppressions(
                                    result, merged)
                        except Exception:
                            pass
                        return result
                except Exception:
                    # If postprocessing fails, continue to fall back to default
                    pass

            except Exception:
                # Adapter failed — fall back to inline snippets below
                pass
        else:
            # Snippets from top glyphs (short, non-redundant)
            seen_snippets = set()
            snippet_count = 0
            for g in ranked:
                if snippet_count >= top_n:
                    break
                gname = g.get('glyph_name') or ''
                gdesc = g.get('description') or g.get('glyph', '') or ''
                intensity = _glyph_intensity(g)
                primary_words = _glyph_primary_words(g)

                # Compose a concise snippet
                if intensity >= 5:
                    tone = f"There's a strong sense of {' and '.join(primary_words)} around {gname}."
                else:
                    tone = f"I notice a thread of {' and '.join(primary_words)} in what you're describing." if primary_words else f"I notice echoes of {gname}."

                # Ground to user's specific content when possible
                entity = extracted.get('entities', [None])[0]
                if entity:
                    grounding = f"That connects to {entity}."
                else:
                    grounding = "That seems connected to what you're carrying."

                snippet = f"{tone} {grounding}"

                # Avoid near-duplicate snippets
                if snippet in seen_snippets:
                    continue
                seen_snippets.add(snippet)
                parts.append(snippet)
                snippet_count += 1

        # Optionally weave a single poetic echo from dominant glyph
        if dominant:
            poetry_emotion = self._glyph_to_emotion_category(
                dominant.get('glyph_name', ''))
            poetry_line = self._weave_poetry(combined_text, {
                                             poetry_emotion: 0.8} if poetry_emotion else extracted.get('emotions', {}))
            if poetry_line:
                parts.append(poetry_line)

        # Final closing calibrated by average intensity
        if ranked:
            avg_intensity = int(sum(_glyph_intensity(g)
                                for g in ranked) / max(1, len(ranked)))
        else:
            avg_intensity = 1

        if avg_intensity <= 2:
            closing_move = "permission"
        elif avg_intensity >= 8:
            closing_move = "commitment"
        else:
            closing_move = "question"

        raw_entity = extracted.get('entities', [None])[0] or 'this'
        entity = self._sanitize_entity(raw_entity)
        closing_template = random.choice(self.closing_moves[closing_move])
        closing = closing_template.replace("{entity}", entity)
        closing = closing.replace("{emotion}", list(extracted.get('emotions', {}).keys())[
                                  0] if extracted.get('emotions') else "what you feel")
        parts.append(closing)

        # Join parts into a single composed response
        result = "\n\n".join(parts)
        # Apply any conversation/session-level suppressions before returning
        try:
            sess = conversation_context.get('suppress_phrases') if conversation_context and isinstance(
                conversation_context, dict) else []
            # Always include the curated default suppressions to avoid
            # frequently-repeated canned lines; merge with any session
            # suppressions provided by the UI.
            merged = list(self.default_suppressions) + (sess or [])

            if merged:
                result = self._apply_suppressions(result, merged)
        except Exception:
            pass

        return result
