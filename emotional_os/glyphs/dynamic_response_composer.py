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


class DynamicResponseComposer:
    """Compose responses dynamically from linguistic fragments."""

    def __init__(self):
        """Initialize language resources."""
        self.semantic_engine = SemanticEngine() if SemanticEngine else None
        self.poetry_db = PoetryDatabase() if PoetryDatabase else None

        # Linguistic patterns for different emotional contexts
        self.opening_moves = {
            "acknowledgment": [
                "I hear {entity}.",
                "There's something real in what you're saying about {entity}.",
                "That matters—{entity}.",
                "I'm listening to {entity}.",
                "You're naming {entity}.",
            ],
            "validation": [
                "{entity} is real.",
                "That's true—{entity}.",
                "The {emotion} you're describing is justified.",
                "What you're feeling makes sense.",
                "{entity} is a legitimate thing to carry.",
            ],
            "curiosity": [
                "Tell me more about {entity}.",
                "What does {entity} feel like?",
                "When you say {entity}, what does that mean?",
                "Help me understand {entity}.",
                "What's the weight of {entity}?",
            ],
            "connection": [
                "You're not alone in {entity}.",
                "Many people navigate {entity}.",
                "The struggle with {entity}—that's deeply human.",
                "{entity} connects you to something universal.",
                "Your {emotion} around {entity} is witnessed.",
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
        entity = entities[0] if entities else "what you're experiencing"
        opening = opening.replace("{entity}", entity)
        opening = opening.replace("{emotion}", emotions.get(
            "primary", "what you're feeling"))

        return opening

    def _weave_poetry(self, text: str, emotions: Dict) -> Optional[str]:
        """Find and weave poetic echoes that match emotional contour."""
        if not self.poetry_db or not emotions:
            return None

        # Map detected emotions to poetry categories
        primary_emotion = list(emotions.keys())[0] if emotions else None

        if not primary_emotion:
            return None

        # Get poetry matching the emotion
        poetry_lines = self.poetry_db.POETRY_COLLECTION.get(
            primary_emotion, [])
        if not poetry_lines:
            return None

        # Select a poem and extract a line
        poem = random.choice(poetry_lines)
        lines = [line.strip() for line in poem.split('\n') if line.strip()]

        if not lines:
            return None

        # Pick a line that's short and impactful (not too long)
        short_lines = [l for l in lines if 8 < len(l.split()) < 15]
        if short_lines:
            return random.choice(short_lines)

        return random.choice(lines[:3]) if len(lines) > 0 else None

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
        Build response focused on the PERSON'S situation, not the glyph system.

        Glyph is used invisibly for:
        - Tone calibration (gate-based intensity)
        - Emotional validation (aligned with emotional_signal)
        - Poetry selection (via emotional category)
        - Entity relationship weighting

        But the response should feel like it's about the person's actual situation,
        not about emotional categories or glyph descriptions.
        """
        parts = []

        # Determine intensity level from glyph (invisible to user)
        intensity_level = 1
        if glyph:
            gate_data = glyph.get("gates") or glyph.get("gate")
            if gate_data:
                gates_list = gate_data if isinstance(
                    gate_data, list) else [gate_data]
                intensity_level = len(gates_list)

        # 1. Validate the specific struggle the person is naming
        # Extract what they're actually struggling with from the message
        lower_input = input_text.lower()

        # Nuanced handling: detect mixed or contrasting emotions (e.g., exhausted + joyful)
        fatigue_words = ['exhaust', 'exhausted', 'tired', 'fatigue', 'weary']
        joy_words = ['joy', 'joyful', 'happy', 'glad', 'delighted']

        has_fatigue = any(w in lower_input for w in fatigue_words)
        has_joy = any(w in lower_input for w in joy_words)

        if has_fatigue and has_joy:
            # Acknowledge complex, co-occurring emotions explicitly
            parts.append(
                "It makes sense that you can feel tired and yet also find moments of joy — both can be true at once. "
                "Holding those together is hard, and it's okay to notice both."
            )
        elif any(word in lower_input for word in ['math', 'anxiety', 'mental block', 'can\'t']):
            # They're naming a specific cognitive struggle
            parts.append(
                "That friction you're naming is real. Many people experience genuine resistance in certain domains.")
        elif any(word in lower_input for word in ['inherited', 'from', 'mother', 'parent']):
            # They're recognizing a pattern they carry from someone else
            parts.append(
                "Recognizing where something comes from—that's a form of clarity. Naming it is the first step to seeing yourself separately from it.")
        elif any(word in lower_input for word in ['misunderstood', 'not what i meant', 'explains', 'understands me']):
            # They're describing a relationship or communication mismatch
            parts.append(
                "When someone explains things in a way that only they can follow, that creates real isolation. That's not a failing on your part.")
        else:
            # Generic validation that honors the emotional weight
            parts.append(
                "What you're sharing matters. There's something real here.")

        # 2. Add feedback-specific response if correcting prior statement
        if feedback_type:
            bridges = self.emotional_bridges.get(feedback_type) or []
            if bridges:
                bridge = random.choice(bridges)
                parts.append(bridge)

        # 3. Reflect back the specific people/entities they mentioned
        if extracted:
            people = extracted.get("people", [])
            if people:
                person = people[0]
                # Use appropriate movement language based on glyph intensity
                movement_category = "through" if intensity_level < 5 else "with"
                movement = random.choice(
                    self.movement_language[movement_category])
                parts.append(f"With {person}, {movement.lower()}")

        # 4. Poetry weaving (glyph emotion category used invisibly)
        if glyph:
            glyph_name = glyph.get("glyph_name", "")
            poetry_emotion = self._glyph_to_emotion_category(glyph_name)
            poetry_line = self._weave_poetry(
                input_text, {poetry_emotion: 0.8} if poetry_emotion else emotions)
            if poetry_line:
                parts.append(f"As someone once wrote: \"{poetry_line}\"")

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
        poetry_line = self._weave_poetry(input_text, emotions)
        if poetry_line:
            parts.append(f"As someone once wrote: \"{poetry_line}\"")

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

        # Build core response anchored in glyph
        response = self._build_glyph_aware_response(
            glyph=glyph,
            entities=extracted["entities"],
            emotions=extracted["emotions"],
            feedback_type=feedback_type if feedback_detected else None,
            input_text=combined_text,
            extracted=extracted,
        )

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
