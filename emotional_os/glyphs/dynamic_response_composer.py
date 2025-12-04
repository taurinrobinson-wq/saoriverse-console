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
from typing import Any, Dict, List, Optional, Tuple, cast

import numpy as np

from emotional_os.feedback.reward_model import RewardModel
from emotional_os.glyphs import tone as tone_module

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

try:
    from parser.nrc_lexicon_loader import nrc
    from parser.poetry_database import PoetryDatabase
    from parser.semantic_engine import SemanticEngine
except ImportError:
    from typing import Any, Optional

    SemanticEngine: Optional[Any] = None  # type: ignore
    nrc: Optional[Any] = None  # type: ignore
    PoetryDatabase: Optional[Any] = None  # type: ignore

try:
    from emotional_os.adapter.response_adapter import translate_system_output
except Exception:
    translate_system_output = None  # type: ignore

try:
    from emotional_os.glyphs.punctuation_cleaner import get_cleaner as get_punctuation_cleaner
except Exception:
    get_punctuation_cleaner = None  # type: ignore


class DynamicResponseComposer:
    """Compose responses dynamically from linguistic fragments."""

    def __init__(self, reward_model: Optional[RewardModel] = None):
        """Initialize language resources.

        Args:
            reward_model: optional `RewardModel` instance used to re-rank
                candidate responses when available.
        """
        # runtime language resources (may be None when parsers aren't available)
        self.semantic_engine: Optional[Any] = (
            SemanticEngine() if (SemanticEngine is not None and callable(SemanticEngine)) else None
        )
        self.poetry_db: Optional[Any] = (
            PoetryDatabase() if (PoetryDatabase is not None and callable(PoetryDatabase)) else None
        )
        # Maintain a rolling tone history to adapt clarifiers over turns
        self.tone_history: List[str] = []
        # Optional reward model used for re-ranking candidate responses
        self.reward_model: Optional[RewardModel] = reward_model

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

    def _extract_entities_and_emotions(self, text: str) -> Dict[str, Any]:
        """Extract key entities and emotional content from input.

        NOTE: historically this returned a list for `emotions` in some code
        paths. Downstream methods expect a mapping (emotion->score). Ensure
        we always return a dict here by coercing list results from any
        external analyzer into a dict where each detected emotion maps to
        a default weight of 1.0.
        """
        result: Dict[str, Any] = {
            "entities": [],
            "emotions": {},
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
        if nrc is not None:
            try:
                analysis = nrc.analyze_text(text)
                # Coerce list-style results into a dict of {emotion: weight}
                if isinstance(analysis, dict):
                    result["emotions"] = analysis
                elif isinstance(analysis, list):
                    # map each listed emotion to a default weight
                    result["emotions"] = {str(e): 1.0 for e in analysis}
                else:
                    # unexpected type: keep default empty dict
                    pass
            except Exception:
                # Keep defensive behaviour: don't let analyzer exceptions
                # break extraction; downstream code will handle empty dicts.
                pass

        # Extract emotional language patterns
        emotional_keywords = [
            "anxiety",
            "anxious",
            "afraid",
            "fear",
            "block",
            "blocked",
            "inherited",
            "inherited pattern",
            "Michelle",
            "frustrated",
            "mad",
            "struggle",
            "friction",
            "communication",
            "misunderstand",
            "grief",
            "loss",
            "sorrow",
            "joy",
            "happy",
            "calm",
            "peaceful",
            "frustrated",
            "angry",
            "hurt",
            "ashamed",
            "confused",
            "clear",
            "isolated",
            "alone",
            "understood",
            "seen",
            "heard",
            "validated",
        ]

        text_lower = text.lower()
        for keyword in emotional_keywords:
            if keyword in text_lower:
                result["emotional_words"].append(keyword)

        return result

    def _select_opening(self, entities: List[str], emotions: Dict[str, Any]) -> str:
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
        if low in {"i", "me", "my", "you", "your", "yours", "we", "us"} or len(low) <= 2:
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
                return ""
            # Ensure end punctuation
            if s[-1] not in ".!?":
                s = s + "."
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
            if "{" in s or "}" in s:
                continue
            # Skip fragments that are clearly questions coming from templates
            if re.search(r"\bwhat does\b|\bwhat would\b", s.lower()) and s.count("?") == 0:
                # avoid lines that look like prompt fragments
                continue
            # Skip lines that are too short (likely artifacts). Allow if contains punctuation
            word_count = len(re.findall(r"[a-zA-Z]+", s))
            if word_count <= 2 and not re.search(r"[.!?]", s):
                continue
            # Remove lines that are basically single punctuation or stray quotes
            if all(ch in "\"'\n\r" for ch in s):
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
        s = " ".join(s.split())
        # Reject if it contains placeholders or braces
        if "{" in s or "}" in s:
            return None
        # Reject if it's clearly a direct question/template
        if s.lower().startswith(("what ", "does ", "is ", "how ", "would ")) and s.endswith("?"):
            return None
        # Enforce reasonable length
        if len(s) > 240 or len(s.split()) < 3:
            return None
        # Ensure ends with punctuation
        if not s.endswith((".", "!", "?")):
            s = s + "."
        # Capitalize first character
        s = s[0].upper() + s[1:]
        return s

    def _weave_poetry(
        self,
        text: str,
        emotions: Dict[str, Any],
        glyphs: Optional[List[Dict[str, Any]]] = None,
        extracted: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Find and weave poetic echoes that match emotional contour."""
        if not self.poetry_db or not emotions:
            return None

        # Ensure glyphs/extracted are usable
        glyphs = glyphs or []
        extracted = extracted or {}

        # How many top glyph snippets to include in poetry/snippet composition.
        # Default to a small number to keep composed replies concise.
        glyphs = glyphs or []
        extracted = extracted or {}
        top_n: int = min(3, max(1, len(glyphs)))
        # Map detected emotions to poetry categories
        primary_emotion: Optional[str] = list(
            emotions.keys())[0] if emotions else None

        if not primary_emotion:
            return None

        # Get poetry matching the emotion
        poetry_lines: List[str] = self.poetry_db.POETRY_COLLECTION.get(
            primary_emotion, []) if (self.poetry_db and hasattr(self.poetry_db, "POETRY_COLLECTION")) else []
        if not poetry_lines:
            return None

        # Helper: map some activation symbols to human words
        sig_map = {
            "γ": "longing",
            "θ": "relief",
            "λ": "tension",
            "ζ": "strain",
            "χ": "tenderness",
            "η": "stillness",
            "ξ": "curiosity",
            "μ": "acceptance",
            "ν": "distance",
            "β": "difficulty",
            "ψ": "rest",
            "φ": "vigilance",
            "τ": "restlessness",
            "ο": "calm",
            "π": "pressure",
            "σ": "softness",
            "ρ": "weight",
            "κ": "constraint",
            "δ": "rupture",
            "ω": "completion",
            "ι": "smallness",
            "α": "openness",
            "ε": "confusion",
        }

        # Small in-file stopword set to avoid an external NLTK dependency
        STOPWORDS = {
            "in",
            "of",
            "and",
            "the",
            "a",
            "an",
            "to",
            "for",
            "with",
            "on",
            "at",
            "by",
            "from",
            "is",
            "are",
            "that",
            "this",
            "it",
            "as",
            "be",
            "was",
            "were",
        }

        def _clean_phrase(phrase: Optional[str]) -> str:
            if not phrase:
                return ""
            tokens = [t.strip().lower()
                      for t in re.findall(r"[a-zA-Z]+", str(phrase))]
            meaningful = [t for t in tokens if t and t not in STOPWORDS]
            return " ".join(meaningful)

        def _glyph_intensity(g: Dict) -> int:
            gates = g.get("gates") or g.get("gate")
            if not gates:
                acts = g.get("activation_signals") or []
                return len(acts) if isinstance(acts, list) else (1 if acts else 0)
            return len(gates) if isinstance(gates, list) else 1

        def _glyph_primary_words(g: Dict) -> List[str]:
            acts = g.get("activation_signals") or []
            words = []
            for a in acts:
                if isinstance(a, str):
                    for ch in re.split(r"[;,\s]+", a):
                        if not ch:
                            continue
                        mapped = sig_map.get(ch.strip(), None)
                        if mapped:
                            words.append(mapped)
            if not words:
                name = g.get("glyph_name") or ""
                words = [t for t in re.findall(r"[a-zA-Z]+", name.lower())][:5]
            # Clean and dedupe
            cleaned = []
            for w in words:
                cw = _clean_phrase(w)
                if cw and cw not in cleaned:
                    cleaned.append(cw)
            return cleaned[:3]

        # Sentence template pools to add variation
        openers = ["I'm sensing", "There's a feeling of",
                   "It sounds like you're carrying", "I hear", "This feels like"]

        connectors = [
            "which seems important.",
            "and that may be part of what's shaping this.",
            "which could be worth staying with for a moment.",
            "and that feels connected to what you're describing.",
            "which might be tied to your experience right now.",
        ]

        question_closers = [
            "Does any of that land for you?",
            "Is that on the right track?",
            "Does that resonate at all?",
            "If that feels right, tell me a bit more.",
        ]

        # Rank glyphs by optional score and intensity
        ranked: List[Dict[str, Any]] = sorted(glyphs, key=lambda g: (
            g.get("score", 0), _glyph_intensity(g)), reverse=True)

        parts: List[str] = []

        # Optional confidence-based summary using the top glyph
        dominant = ranked[0] if ranked else None
        if dominant and dominant.get("glyph_name"):
            summary_name = _clean_phrase(dominant.get(
                "glyph_name")) or dominant.get("glyph_name")
            parts.append(
                f"It seems the strongest theme here is {summary_name}.")

        # Opening move: grounded in detected entities/emotions
        opening = self._select_opening(extracted.get(
            "entities", []), extracted.get("emotions", {}))
        parts.append(opening)

        # Snippets from top glyphs with varied templates
        seen_snippets = set()
        snippet_count = 0
        for g in ranked:
            if snippet_count >= top_n:
                break
            gname = g.get("glyph_name") or ""
            gdesc = g.get("description") or ""
            intensity = _glyph_intensity(g)
            primary_words = _glyph_primary_words(g)

            # Build the phrase representing the glyph's core
            if primary_words:
                phrase = ", ".join(primary_words)
            else:
                phrase = _clean_phrase(gname) or gname

            # Choose varied opener + connector
            opener = random.choice(openers)
            connector = random.choice(connectors)

            # Grounding to entity or neutral 'this'
            entity = extracted.get("entities", [None])[0]
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
            s = " ".join(s.split())
            # Ensure capitalization and punctuation
            if s and s[0].islower():
                s = s[0].upper() + s[1:]
            if s and not s.endswith((".", "?", "!")):
                s = s + "."
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

    def _glyph_to_plain_summary(self, g: Dict) -> str:
        """Return a short, plain-language summary of a glyph suitable for user-facing text.

        This translates internal glyph fields (activation signals, glyph_name,
        description) into a readable fragment like "a recurring ache of nervous
        energy" or "a quiet, persistent wanting".
        """
        if not isinstance(g, dict):
            return ""

        name = (g.get("glyph_name") or "").strip()
        desc = (g.get("description") or "").strip()

        # Derive primary words from activation_signals if present
        acts = g.get("activation_signals") or []
        if isinstance(acts, str):
            acts = re.split(r"[;,\s]+", acts)
        primary_words = []
        for a in acts:
            if not a:
                continue
            # remove non-letter chars and map if single symbols
            token = re.sub(r"[^a-zA-Z]", " ", str(a)).strip().lower()
            if token:
                primary_words.extend(token.split())

        # Prefer description when it's human-readable
        if desc:
            # Ensure description is a short sentence fragment
            frag = desc
            if frag and not frag.endswith((".", "!", "?")):
                frag = frag.strip()
            return frag

        # Otherwise build from primary words or glyph name
        if primary_words:
            # pick up to three meaningful words
            words = [w for w in primary_words if len(w) > 2][:3]
            if words:
                return " ".join(words)

        if name:
            return name

        return ""

    def _smooth_fragments_to_sentence(self, fragments: List[str]) -> str:
        """Turn a list of short fragments into one smooth, human sentence.

        Basic rules:
        - Clean fragments and remove duplicates.
        - Use commas and an 'and' before the last item.
        - Prepend articles ('a') for fragments that look like noun phrases.
        - Ensure sentence starts with a lowercase continuation (caller may
          prepend a lead-in) or return a full sentence.
        """
        if not fragments:
            return ""

        # Normalize fragments
        seen = set()
        clean = []
        for f in fragments:
            if not f or not isinstance(f, str):
                continue
            s = " ".join(f.split()).strip()
            if not s:
                continue
            # remove trailing punctuation
            if s[-1] in ".!?":
                s = s[:-1]
            if s in seen:
                continue
            seen.add(s)
            clean.append(s)

        if not clean:
            return ""

        def _ensure_article(s: str) -> str:
            # If the fragment starts with an article or 'the' or pronoun, keep it
            low = s.lower()
            if low.startswith(("a ", "an ", "the ", "my ", "your ", "their ", "our ")):
                return s
            # If fragment looks like verb-first, don't add article
            if re.match(r"^(is|are|feels|seems|has|have|notice|noticing)\b", low):
                return s
            # If fragment starts with an adjective or noun, add 'a'
            # Simple heuristic: if first token length > 2, prefix 'a '
            first = low.split()[0]
            if len(first) > 2:
                return "a " + s
            return s

        enriched = [_ensure_article(s) for s in clean]

        if len(enriched) == 1:
            return enriched[0]
        if len(enriched) == 2:
            return f"{enriched[0]} and {enriched[1]}"
        # 3+ fragments
        return ", ".join(enriched[:-1]) + ", and " + enriched[-1]

    def _needs_clarifying_question(self, extracted: Dict, fragments: List[str], input_text: str = "") -> bool:
        """Decide whether we should ask a clarifying question instead of
        asserting a multi-glyph synthesis.

        Trigger when we lack entities, when fragments are empty or too vague,
        or when the user's message is short and we need more context.
        """
        # If we have at least one good fragment and some emotional words, proceed
        if fragments and extracted.get("emotional_words"):
            return False

        # If fragments exist but are single-word tokens only, ask for clarification
        if fragments:
            token_counts = [len(re.findall(r"[a-zA-Z]+", f))
                            for f in fragments]
            if all(tc <= 1 for tc in token_counts):
                return True

        # If we have any named entities or people, we can proceed without clarification
        if extracted.get("entities") or extracted.get("people"):
            return False

        # If no emotional words detected and no entities, ask a clarifying question
        if not extracted.get("emotional_words") and not extracted.get("entities"):
            return True

        # If the user's message is very short (few words) and we lack entities,
        # ask for clarification to invite more context.
        try:
            if input_text and len(input_text.split()) <= 6 and not extracted.get("entities"):
                return True
        except Exception:
            pass

        return False

    def _make_clarifying_question(self, input_text: str, extracted: Dict) -> str:
        """Build a short rephrase + invitation asking the user to elaborate.

        This implementation updates the composer's tone history and selects a
        clarifier template from the `tone` module so clarifiers adapt to the
        user's recent tone within a rolling window.
        """
        # Update tone state using the composer's rolling history
        try:
            tone_state = tone_module.update_tone_state(
                self.tone_history, input_text)
            clarifier = tone_module.get_clarifier(tone_state)
        except Exception:
            # Fall back to previous behavior if tone module fails
            echo = input_text.strip()
            if len(echo) > 120:
                echo = echo[:117].rsplit(" ", 1)[0] + "..."
            emo = ""
            if extracted.get("emotional_words"):
                emo = extracted["emotional_words"][0]
            if emo:
                clarifier = f"I hear you're feeling {emo}. Do you want to tell me a bit more about that?"
            else:
                clarifier = "I hear you. Do you want to tell me more about what's behind that?"

        # If we have an explicit detected emotion, try to include it in the
        # clarifier when the template doesn't already mention an emotion.
        try:
            if extracted.get("emotional_words"):
                emo = str(extracted["emotional_words"][0]).strip()
                if emo:
                    clar_low = clarifier.lower()
                    # If the clarifier already mentions the specific emotion, leave it
                    if emo.lower() in clar_low:
                        pass
                    else:
                        # Prefer to replace vague phrasing like "feeling that way" with the detected emotion
                        replaced = False
                        for vague in ("feeling that way", "feeling that", "feeling this", "feeling so", "feeling it"):
                            if vague in clar_low:
                                # perform a case-smart replacement
                                clarifier = re.sub(
                                    re.escape(vague), f"feeling {emo}", clarifier, flags=re.IGNORECASE)
                                replaced = True
                                break

                        # If no vague phrase to replace, and the clarifier doesn't already include an emotion
                        # then prepend a short acknowledgement to make the detected emotion explicit.
                        if not replaced:
                            clarifier = f"I hear you're feeling {emo}. " + clarifier
        except Exception:
            pass

        return clarifier

    def _stage_for_learning(self, extracted: Dict, input_text: str, glyphs: Optional[List[Dict]] = None) -> None:
        """Append a minimal learning record to `learning/staged_glyphs.jsonl`.

        This is gated by the environment variable `ENABLE_GLYPH_LEARNING`.
        The record includes timestamp, user input, extracted features and
        top glyph summaries so later processes can ingest/stage them for
        lexicon/glyph updates.
        """
        if os.environ.get("ENABLE_GLYPH_LEARNING") != "1":
            return

        try:
            os.makedirs("learning", exist_ok=True)
            outp = os.path.join("learning", "staged_glyphs.jsonl")
            record = {
                "ts": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                "input_text": input_text,
                "extracted": extracted,
                "glyphs": [
                    {"glyph_name": g.get("glyph_name"), "description": g.get("description")} for g in (glyphs or [])
                ],
            }
            with open(outp, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            # Never raise from learning staging
            return

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
        
        NEW APPROACH (Phase 12.1): Respond to actual content, not templates.
        Listen to what the user said, extract the emotional core, respond naturally.

        Args:
            glyph: Full glyph dict with name, description, emotional_signal, gates
            entities: Extracted entities from user input
            emotions: Detected emotions from user input
            feedback_type: Type of user correction if any
            input_text: User's original or combined input text
            extracted: Full extraction dict from _extract_entities_and_emotions

        Returns:
            Natural, conversational response grounded in what the user said
        """
        if not input_text:
            return "I'm here to listen. What's on your mind?"
        
        lower_input = input_text.lower()
        
        # Detect what the user is actually talking about and respond to THAT
        
        # Overwhelm/burden/holding too much
        if any(word in lower_input for word in ["overwhelm", "fragile", "breaking", "heavy", "heavy load", "too much", "drowning"]):
            return f"I hear you. Sounds like you're holding a lot right now. What feels heaviest?"
        
        # Sacred/meaningful/precious moments
        if any(word in lower_input for word in ["sacred", "precious", "meaningful", "special moment", "moved"]):
            if "child" in lower_input or "hug" in lower_input or "touch" in lower_input:
                return f"Those moments with people we love hit different. Sounds like that was really special. Want to say more about it?"
            else:
                return f"You're sensing something significant. What made that moment feel so precious?"
        
        # Relief/rest/break
        if any(word in lower_input for word in ["done", "finally", "relief", "break", "quiet", "rest", "peace"]):
            if "work" in lower_input or "finished" in lower_input:
                return f"Yeah, what a relief. Sounds like you've been carrying a lot. How are you wanting to spend this quiet time?"
            else:
                return f"That pause matters. What does this quiet feel like after everything?"
        
        # Grief/loss/sadness
        if any(word in lower_input for word in ["grief", "loss", "lost", "miss", "sad", "mourning"]):
            return f"That's real. Loss takes up space. What do you need right now?"
        
        # Joy/celebration/good news
        if any(word in lower_input for word in ["happy", "excited", "celebrating", "wonderful", "amazing", "loved"]):
            return f"That's something to feel. Let it land. What's the story there?"
        
        # Vulnerability/scared/uncertain
        if any(word in lower_input for word in ["scared", "afraid", "uncertain", "vulnerable", "unsafe", "exposed"]):
            return f"That takes courage to name. You're not alone in that. What would help right now?"
        
        # Frustration/anger
        if any(word in lower_input for word in ["frustrated", "angry", "furious", "mad", "rage"]):
            return f"That frustration is telling you something. What's underneath it?"
        
        # Default: reflect the emotion back empathetically
        if emotions:
            primary_emotion = list(emotions.keys())[0] if emotions else None
            if primary_emotion == "sadness":
                return f"That sadness is real. I'm here with you in it. What do you need?"
            elif primary_emotion == "joy":
                return f"I hear the lightness in that. Let it in. Tell me more."
            elif primary_emotion == "anger":
                return f"That anger is saying something important. What's it about?"
            elif primary_emotion == "fear":
                return f"That fear makes sense. You're not wrong to feel it. What scares you most?"
            elif primary_emotion == "trust":
                return f"That trust is beautiful. How does it feel?"
            elif primary_emotion == "anticipation":
                return f"You're sensing something ahead. What are you anticipating?"
        
        # Last resort: genuinely open listening
        return f"I hear you. What's the feeling underneath all that?"
    
    def _extract_glyph_concepts(self, glyph_desc: str) -> List[str]:
        """Extract key emotional/conceptual elements from glyph description."""
        if not glyph_desc:
            return []
        
        # Key concepts we look for in glyph descriptions
        concept_keywords = {
            "stillness": ["still", "quiet", "calm", "stillness"],
            "witnessing": ["witness", "seen", "gaze", "recognition", "mirror"],
            "ache": ["ache", "longing", "yearning", "sorrow"],
            "containment": ["boundary", "contain", "hold", "shield"],
            "transformation": ["shift", "spiral", "revelation", "insight"],
            "devotion": ["sacred", "vow", "devotional", "offering"],
            "joy": ["joy", "delight", "bliss", "celebration"],
            "grief": ["grief", "mourning", "collapse"],
        }
        
        concepts_found = []
        desc_lower = glyph_desc.lower()
        for concept, keywords in concept_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                concepts_found.append(concept)
        
        return concepts_found[:3]  # Return top 3 concepts
    
    def _generate_glyph_wisdom(self, glyph_name: str, glyph_desc: str, concepts: List[str], input_text: str) -> str:
        """Generate a response that incorporates glyph wisdom and concepts.
        
        This is the PRIMARY differentiator - each glyph generates different wisdom
        based on its name, description, and detected concepts.
        
        Focus on conversational, direct language rather than poetic phrasing.
        """
        if not glyph_desc and not glyph_name:
            return ""
        
        # Build glyph-specific wisdom based on glyph name and concepts
        # These are direct, conversational statements that reflect the glyph's essence
        
        glyph_name_lower = glyph_name.lower()
        
        # Map glyph names to specific, differentiated wisdom
        # Using conversational, grounded language
        glyph_specific_wisdom = {
            "still recognition": "Being seen for what you're actually experiencing matters.",
            "still insight": "Sometimes clarity comes when you pause.",
            "still ache": "You're holding this, and that's okay.",
            "euphoric yearning": "What you're longing for says something real about you.",
            "ache in equilibrium": "The pain you feel is balanced—you're managing it.",
            "ache of recognition": "It helps to be understood in your pain.",
            "devotional ache": "Your care matters, even when it costs you.",
            "jubilant mourning": "You can feel sadness and aliveness at the same time.",
            "grief in stillness": "Your grief gets to exist without needing to be busy.",
            "grief of recognition": "Being acknowledged in your loss changes something.",
            "contained longing": "Your need is real and you're not drowning in it.",
            "recursive ache": "The patterns you're seeing are actually helpful to notice.",
            "reverent ache": "What you feel is meaningful.",
            "exalted mourning": "Your loss doesn't diminish who you are.",
            "boundary containment": "You're protecting what matters.",
            "spiral containment": "The complexity you're in has a structure.",
            "clarity insight": "You're understanding something real.",
            "focus insight": "Where you're putting your attention is important.",
        }
        
        # Check if glyph name matches known glyphs
        for glyph_key, wisdom in glyph_specific_wisdom.items():
            if glyph_key in glyph_name_lower:
                return wisdom
        
        # If no exact match, build from concepts
        if concepts:
            concept = concepts[0]
            wisdom_templates = {
                "stillness": "Pausing can be its own kind of action.",
                "witnessing": "Being seen helps.",
                "ache": "The pain you feel connects to something you care about.",
                "containment": "You're holding this.",
                "transformation": "Something is shifting.",
                "devotion": "Your commitment matters.",
                "joy": "Let this moment in.",
                "grief": "Your grief is real.",
            }
            if concept in wisdom_templates:
                return wisdom_templates[concept]
        
        # Last resort: use first sentence of glyph description
        if glyph_desc:
            sentences = glyph_desc.split(". ")
            if sentences and sentences[0]:
                return sentences[0] + "."
        
        return ""

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
                                         "entities": entities, "emotions": emotions})
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
                if "last_user_message" in conversation_context:
                    prev_user = conversation_context.get("last_user_message")
                elif "previous_user_message" in conversation_context:
                    prev_user = conversation_context.get(
                        "previous_user_message")
                else:
                    # Try to extract from messages/history lists
                    msgs = conversation_context.get(
                        "messages") or conversation_context.get("history")
                    if isinstance(msgs, list) and msgs:
                        # Find the last user message in the list
                        for m in reversed(msgs):
                            if isinstance(m, dict) and m.get("role") in ("user", "User"):
                                prev_user = m.get("content") or m.get(
                                    "text") or m.get("user")
                                break
                            # older formats store entries as {'user':..., 'assistant':...}
                            if isinstance(m, dict) and "user" in m and m.get("user"):
                                prev_user = m.get("user")
                                break
                if prev_user:
                    # prepend previous user text to detect cross-turn emotional combinations
                    combined_text = f"{prev_user.strip()} {input_text.strip()}"
        except Exception:
            # Defensive: if context parsing fails, fall back to input_text
            combined_text = input_text

        # Extract linguistic features from the combined text (captures cross-turn cues)
        extracted = self._extract_entities_and_emotions(combined_text)

        # Build core response anchored in glyph
        response = self._build_glyph_aware_response(
            glyph=glyph,
            entities=extracted["entities"],
            emotions=extracted["emotions"],
            feedback_type=feedback_type if feedback_detected else None,
            input_text=combined_text,
            extracted=extracted,
        )

        # Clean em dashes and apply style-appropriate punctuation
        # DISABLED: The punctuation cleaner was causing responses to become generic/repetitive
        # by replacing meaningful closings with rotation bank entries. The response is already
        # well-formed from _build_glyph_aware_response.
        # if get_punctuation_cleaner:
        #     try:
        #         cleaner = get_punctuation_cleaner()
        #         glyph_name = glyph.get("glyph_name") if glyph else None
        #         response = cleaner.process_response(response, glyph_name, diversify=False, timeout=1.0)
        #     except Exception as e:
        #         import logging
        #         logging.debug(f"Punctuation cleaning failed: {e}")
        
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

        result = " ".join(parts)
        
        # Clean em dashes and apply style-appropriate punctuation
        # DISABLED: See compose_response() for explanation
        # if get_punctuation_cleaner:
        #     try:
        #         cleaner = get_punctuation_cleaner()
        #         glyph_name = glyph.get("glyph_name") if glyph else None
        #         result = cleaner.process_response(result, glyph_name, diversify=False, timeout=1.0)
        #     except Exception as e:
        #         import logging
        #         logging.debug(f"Punctuation cleaning failed: {e}")
        
        return result

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
                if "last_user_message" in conversation_context:
                    prev_user = conversation_context.get("last_user_message")
                elif "previous_user_message" in conversation_context:
                    prev_user = conversation_context.get(
                        "previous_user_message")
                else:
                    msgs = conversation_context.get(
                        "messages") or conversation_context.get("history")
                    if isinstance(msgs, list) and msgs:
                        for m in reversed(msgs):
                            if isinstance(m, dict) and m.get("role") in ("user", "User"):
                                prev_user = m.get("content") or m.get(
                                    "text") or m.get("user")
                                break
                            if isinstance(m, dict) and "user" in m and m.get("user"):
                                prev_user = m.get("user")
                                break
                if prev_user:
                    combined_text = f"{prev_user.strip()} {input_text.strip()}"
        except Exception:
            combined_text = input_text

        # Extract entities/emotions for grounding
        extracted = self._extract_entities_and_emotions(combined_text)

        # Limit glyphs to top_n
        glyphs = glyphs[:top_n] if glyphs else []

        # Helper: map some activation symbols to human words
        sig_map = {
            "γ": "longing",
            "θ": "relief",
            "λ": "tension",
            "ζ": "strain",
            "χ": "tenderness",
            "η": "stillness",
            "ξ": "curiosity",
            "μ": "acceptance",
            "ν": "distance",
            "β": "difficulty",
            "ψ": "rest",
            "φ": "vigilance",
            "τ": "restlessness",
            "ο": "calm",
            "π": "pressure",
            "σ": "softness",
            "ρ": "weight",
            "κ": "constraint",
            "δ": "rupture",
            "ω": "completion",
            "ι": "smallness",
            "α": "openness",
            "ε": "confusion",
        }

        def _glyph_intensity(g: Dict) -> int:
            gates = g.get("gates") or g.get("gate")
            if not gates:
                # fallback to number of activation signals
                acts = g.get("activation_signals") or []
                return len(acts) if isinstance(acts, list) else (1 if acts else 0)
            return len(gates) if isinstance(gates, list) else 1

        def _glyph_primary_words(g: Dict) -> List[str]:
            acts = g.get("activation_signals") or []
            words = []
            for a in acts:
                if isinstance(a, str):
                    # activation signals may be comma-separated
                    for ch in re.split(r"[;,\s]+", a):
                        if not ch:
                            continue
                        mapped = sig_map.get(ch.strip(), None)
                        if mapped:
                            words.append(mapped)
            # fallback: include glyph name tokens
            if not words:
                name = g.get("glyph_name") or ""
                words = [t for t in re.findall(r"[a-zA-Z]+", name.lower())][:3]
            return words

        # Rank glyphs by intensity (and optional provided score)
        ranked = sorted(glyphs, key=lambda g: (
            g.get("score", 0), _glyph_intensity(g)), reverse=True)

        parts: List[str] = []

        # Opening move: use dominant glyph to pick tone
        dominant = ranked[0] if ranked else None
        opening = self._select_opening(extracted.get(
            "entities", []), extracted.get("emotions", {}))
        parts.append(opening)

        # Prepare readable fragments for the top glyphs so clarifying
        # heuristics and synthesis can use them consistently.
        top_glyphs = ranked[:top_n]
        fragments = []
        for g in top_glyphs:
            frag = self._glyph_to_plain_summary(g)
            if frag:
                fragments.append(frag)

        # If we lack enough context to synthesize a confident multi-glyph
        # summary, ask a clarifying question before attempting adapter-based
        # or fragment-based synthesis. This invites the user to elaborate and
        # prevents regurgitating low-confidence summaries.
        try:
            if self._needs_clarifying_question(extracted, fragments, combined_text):
                question = self._make_clarifying_question(
                    combined_text, extracted)
                reply = f"{opening} {question}"
                try:
                    self._stage_for_learning(extracted, combined_text, glyphs)
                except Exception:
                    pass
                return reply
        except Exception:
            # Fail-safe: continue into synthesis if clarifying logic errors
            pass

        # If we have readable fragments, add a smoothed summary early so
        # downstream adapter processing or the final postprocessor sees a
        # human-friendly lead sentence.
        try:
            if fragments:
                summary_frag = self._smooth_fragments_to_sentence(fragments)
                if summary_frag:
                    parts.append(
                        f"I'm noticing {summary_frag} in what you're sharing.")
        except Exception:
            pass

        # Prefer using the response adapter to translate glyphs into
        # plain-language summary and short snippets. Fallback to older
        # snippet composition if the adapter is not available.
        if translate_system_output is not None:
            try:
                adapter_input = {
                    "glyphs": glyphs,
                    "extracted": extracted,
                    "context": conversation_context,
                }
                adapter_out = translate_system_output(
                    adapter_input, top_n=top_n, user_context=conversation_context)
                # summary may be a short phrase like 'recurring ache'
                summary = adapter_out.get("summary")
                snippets = adapter_out.get("snippets") or []
                tone = adapter_out.get("tone") or "neutral"
                invitation = adapter_out.get("invitation") or None

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
                        return "\n\n".join(processed)
                except Exception:
                    # If postprocessing fails, continue to fall back to default
                    pass

            except Exception:
                # Adapter failed — fall back to inline snippets below
                pass
        else:
            # Synthesize a cohesive, plain-language summary from the top glyphs.
            # Aim: produce one short paragraph that translates glyph metadata into
            # conversational language rather than regurgitating internal tokens.

            # Build an overall smoothed summary sentence from fragments
            if fragments:
                summary_frag = self._smooth_fragments_to_sentence(fragments)
                if summary_frag:
                    parts.append(
                        f"I'm noticing {summary_frag} in what you're sharing.")

                # Add one-sentence elaborations for the top one or two glyphs (concise)
                for g in top_glyphs[:2]:
                    name = g.get("glyph_name") or ""
                    desc = g.get("description") or ""
                    if desc:
                        parts.append(f"For example, {desc.strip()}")
                    elif name:
                        parts.append(
                            f"For example, {name} seems relevant here.")
            else:
                # Fallback to a gentle generic opener
                parts.append(
                    "I'm noticing some themes in what you're sharing.")

            # Optionally stage for learning (env-gated) when we have fragments
            try:
                self._stage_for_learning(extracted, input_text, top_glyphs)
            except Exception:
                pass

        # Optionally weave a single poetic echo from dominant glyph
        if dominant:
            poetry_emotion = self._glyph_to_emotion_category(
                dominant.get("glyph_name", ""))
            poetry_line = self._weave_poetry(
                combined_text, {poetry_emotion: 0.8} if poetry_emotion else extracted.get(
                    "emotions", {})
            )
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

        raw_entity = extracted.get("entities", [None])[0] or "this"
        entity = self._sanitize_entity(raw_entity)
        closing_template = random.choice(self.closing_moves[closing_move])
        closing = closing_template.replace("{entity}", entity)
        closing = closing.replace(
            "{emotion}", list(extracted.get("emotions", {}).keys())[
                0] if extracted.get("emotions") else "what you feel"
        )
        parts.append(closing)

        # Post-process assembled parts for punctuation/capitalization and return
        try:
            processed = self._postprocess_parts(parts)
            if processed:
                return "\n\n".join(processed)
        except Exception:
            pass

        # Fallback: Join parts into a single composed response
        return "\n\n".join(parts)

    def compose(self, candidates: List[Dict]) -> str:
        """
        Rank and select from a list of textual candidate responses using the
        optional `RewardModel`.

        Each candidate is expected to be a dict with keys:
          - "text": the candidate response string
          - "features": numeric vector (list or numpy array) representing
                        features used by the reward model

        If no `RewardModel` is provided, the method falls back to returning
        the first candidate's text (or an empty string if no candidates).
        """
        if not candidates:
            return ""

        if not self.reward_model:
            return candidates[0].get("text", "")

        scored = []
        for c in candidates:
            try:
                feats = np.asarray(c.get("features", []), dtype=float)
            except Exception:
                feats = np.asarray([], dtype=float)

            try:
                score = float(self.reward_model.score(
                    feats)) if feats.size else 0.0
            except Exception:
                score = 0.0

            scored.append((c.get("text", ""), score))

        # choose the candidate with the highest score
        best = max(scored, key=lambda x: x[1])
        return best[0]
