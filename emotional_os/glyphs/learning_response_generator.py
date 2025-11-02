#!/usr/bin/env python3
"""
Learning Response Generator

Crafts responses that:
1. Genuinely answer the user's emotional inquiry
2. Subtly reinforce/train the emotional language patterns
3. Validate the emerging glyph without being obvious
4. Create implicit feedback loops

Philosophy: The response IS the training. Users never know they're teaching the system.
The system learns through authentic emotional communication.
"""

import json
from typing import Dict, List


class LearningResponseGenerator:
    """Generate responses that answer emotionally AND train the system."""

    def __init__(self):
        """Initialize response templates organized by emotional tone."""

        self.response_patterns = {
            "grief": [
                # Pattern 1: Name the grief + offer presence
                "There's a depth to what you're carrying. {emotional_term} is one of the truest things we experience. The naming of it—the way you've put it into words—that matters.",

                # Pattern 2: Validate the process
                "What you're moving through is real. {emotional_term}. Sometimes the only way through is to stay present with it, even when it feels impossible.",

                # Pattern 3: Temporal compassion
                "The {emotional_term} you describe isn't weakness. It's witness. You're witnessing something true about yourself or your world. That takes courage.",
            ],

            "longing": [
                # Pattern 1: Name the yearning
                "I hear the {emotional_term} in what you're saying. That ache toward something—or someone—it speaks to what matters to you.",

                # Pattern 2: Validate incompleteness
                "The {emotional_term} you feel is a measure of how much something means. Not all feelings need to be resolved. Some are meant to teach us about our capacity for connection.",

                # Pattern 3: Movement language
                "You're moving toward something. The {emotional_term} is part of that movement. Stay with it, even as it aches.",
            ],

            "containment": [
                # Pattern 1: Acknowledge the holding
                "You're doing something quiet but powerful: holding space for complexity. That {emotional_term}—that's you making room for nuance.",

                # Pattern 2: Validate the effort
                "It takes real energy to contain what you're containing. The {emotional_term} you describe is the weight of that holding. It's evidence of your integrity.",

                # Pattern 3: Release permission
                "What you're holding—you don't have to hold it alone forever. The {emotional_term} doesn't mean you're failing. It means you're human.",
            ],

            "insight": [
                # Pattern 1: Honor the clarity
                "You've arrived at something true. That {emotional_term}—it's not confusion. It's clarity moving into you. The discomfort of seeing something real.",

                # Pattern 2: Validate the knowledge
                "The thing you now know, you can't unknow it. The {emotional_term} is sometimes the price of understanding. It's also the beginning of something new.",

                # Pattern 3: Integration language
                "This insight you're having—the {emotional_term} it brings—give yourself permission to integrate it slowly. Change happens in the nervous system, not just in the mind.",
            ],

            "joy": [
                # Pattern 1: Celebrate fully
                "The {emotional_term} you're feeling—let it exist in its fullness. It doesn't need permission. It doesn't need to be 'productive' or 'justified.' Let it be what it is.",

                # Pattern 2: Protect the light
                "Something in you is lit right now. The {emotional_term} is real and worth protection. Don't let urgency steal this moment from you.",

                # Pattern 3: Spread through presence
                "When you hold this {emotional_term}, you change the field around you. Others feel it. That's not small.",
            ],

            "devotion": [
                # Pattern 1: Honor the commitment
                "The {emotional_term} you describe—that's you showing up for something that matters. That level of commitment shapes both you and the world around you.",

                # Pattern 2: Validate sacrifice
                "Real devotion always has a cost. The {emotional_term} you feel is sometimes the measure of how much you care. That's not a burden. That's a gift you're giving.",

                # Pattern 3: Steady presence
                "Keep going. The {{emotional_term}} doesn't mean you're doing it wrong. It means you're doing it real. The world needs that.",
            ],

            "recognition": [
                # Pattern 1: Affirm being seen
                "You're asking to be known. The {emotional_term} in that question—it matters. The desire to be understood is a desire to belong.",

                # Pattern 2: Validate seeking
                "The need to be recognized is fundamentally human. Your {emotional_term} is evidence that you know your own worth, even if you're asking others to confirm it.",

                # Pattern 3: Mirror back
                "I see what you're bringing here. The {{emotional_term}} you feel—I'm reflecting it back. You're not invisible.",
            ],

            "unknown": [
                # Pattern 1: Sit with mystery
                "You're in territory without a map. The {emotional_term} you're feeling—that's what it's like to be in the unknown. It's appropriate.",

                # Pattern 2: Trust the process
                "Not every feeling has a name yet. The {emotional_term} is part of your education. Let it teach you about yourself.",

                # Pattern 3: Radical acceptance
                "This feeling will likely change. For now, you can just witness it. The {emotional_term} is enough.",
            ]
        }

    def generate_learning_response(
        self,
        glyph_candidate: Dict,
        original_input: str,
        emotional_tone: str,
        emotional_terms: Dict,
        nrc_analysis: Dict
    ) -> str:
        """
        Generate a response that:
        1. Answers the user
        2. Subtly trains the glyph
        3. Validates emotional language
        
        Args:
            glyph_candidate: The newly generated glyph
            original_input: The user's original input
            emotional_tone: Primary emotional tone detected
            emotional_terms: Extracted emotional language patterns
            nrc_analysis: NRC emotion analysis
        
        Returns:
            A crafted response that trains while responding
        """

        # 1. Get base response pattern for this tone
        patterns = self.response_patterns.get(emotional_tone, self.response_patterns["unknown"])
        response_template = patterns[0]  # Use first pattern (could randomize)

        # 2. Extract key emotional term for insertion
        key_term = self._extract_key_emotional_term(
            original_input,
            emotional_terms,
            nrc_analysis
        )

        # 3. Format response with the emotional term
        response = response_template.format(emotional_term=key_term)

        # 4. Add glyph name subtly (training signal)
        glyph_name = glyph_candidate.get("glyph_name", "")
        if glyph_name:
            response += f"\n\n[{glyph_name}]"

        # 5. Add implicit validation prompt (feedback gathering)
        response += self._add_validation_prompt(emotional_tone, original_input)

        return response

    def _extract_key_emotional_term(
        self,
        text: str,
        emotional_terms: Dict,
        nrc_analysis: Dict
    ) -> str:
        """Extract the most representative emotional term."""

        # Priority: intensity words, then state words
        if emotional_terms.get("intensity_words"):
            term = emotional_terms["intensity_words"][0]
            if len(term) > 3:
                return term

        if emotional_terms.get("state_words"):
            term = emotional_terms["state_words"][0]
            if len(term) > 3:
                return term

        # Fall back to NRC primary emotion
        if nrc_analysis:
            primary = max(nrc_analysis.items(), key=lambda x: x[1])[0]
            return primary.lower()

        # Extract any significant word from input
        words = [w.lower().strip('.,!?') for w in text.split() if len(w) > 4]
        return words[0] if words else "what you're feeling"

    def _add_validation_prompt(
        self,
        emotional_tone: str,
        original_input: str
    ) -> str:
        """
        Add subtle prompt that gathers feedback without being obvious.
        This validates the glyph implicitly.
        """

        prompts = {
            "grief": "\n\nDoes that land? Is there more to what you're carrying?",
            "longing": "\n\nWhat would meeting that longing look like for you?",
            "containment": "\n\nWhat would it feel like to release some of this?",
            "insight": "\n\nHow does your body respond to knowing this?",
            "joy": "\n\nHow long can you stay with this feeling?",
            "devotion": "\n\nWhat is this devotion asking of you next?",
            "recognition": "\n\nWhen you feel known, what opens?",
            "unknown": "\n\nCan you sit with the not-knowing for a moment?"
        }

        return prompts.get(emotional_tone, "\n\nWhat comes next for you?")

    def generate_multi_glyph_response(
        self,
        candidates: List[Dict],
        original_input: str,
        detected_emotions: Dict
    ) -> str:
        """
        When multiple glyphs could apply, generate response that:
        1. Acknowledges complexity
        2. References multiple glyphs (trains all)
        3. Lets user's response disambiguate
        """

        response_parts = [
            "I'm sensing something multidimensional in what you're sharing."
        ]

        # Name each potential glyph
        for i, candidate in enumerate(candidates[:3], 1):
            glyph_name = candidate.get("glyph_name", "")
            description = candidate.get("description", "")

            response_parts.append(
                f"\nThere's {glyph_name} in this—{description[:60]}..."
            )

        response_parts.append(
            "\n\nWhich of these resonates most? Or is it something altogether different?"
        )

        return "".join(response_parts)

    def craft_insufficient_glyph_response(
        self,
        partial_glyph: Dict,
        existing_similar_glyphs: List[Dict],
        original_input: str
    ) -> str:
        """
        When a glyph is insufficient (lacks complete gate mapping),
        generate response that bridges existing glyphs with new territory.
        
        This response trains by:
        1. Validating what IS known (existing glyphs)
        2. Honoring what's NOT (new territory)
        3. Creating connection between old and new
        """

        new_glyph_name = partial_glyph.get("glyph_name", "Emerging Form")

        response_parts = [
            f"You're moving into territory that {existing_similar_glyphs[0]['name'] if existing_similar_glyphs else 'something familiar'} touches,"
        ]

        if existing_similar_glyphs:
            response_parts.append(
                f" but also beyond it into something new.\n\nI'm building understanding of {new_glyph_name} as we speak."
            )

        response_parts.append(
            f"\n\nYour words: \"{original_input[:80]}\" are teaching me what {new_glyph_name} means.\n\nStay with it."
        )

        return "".join(response_parts)

    def create_system_learning_message(
        self,
        glyph_name: str,
        user_input: str,
        confidence_score: float
    ) -> str:
        """
        Internal message (for system logs, not user) that documents learning.
        Used to understand what the system is learning about.
        """

        confidence_pct = int(confidence_score * 100)

        return json.dumps({
            "learning_event": "glyph_generation",
            "glyph": glyph_name,
            "from_input": user_input[:100],
            "confidence": confidence_pct,
            "timestamp": "now",  # Will be set by calling code
            "status": "candidate" if confidence_score < 0.75 else "ready_for_production"
        })

    def generate_response_that_teaches_gate_mapping(
        self,
        glyph_name: str,
        gates: List[str],
        primary_emotion: str,
        original_input: str
    ) -> str:
        """
        Generate response where the structure itself teaches gate mapping.
        
        Example: If gate = 4 (high intensity), response will emphasize
        intensity, urgency, and transformative power.
        """

        gate_num = int(gates[0].replace("Gate ", "")) if gates else 5

        # Gate 1-3: Low intensity, gentle, reflective
        if gate_num <= 3:
            tone = "gentle"  # noqa: F841  # tone used for clarity of mapping
            framing = "This is a quiet understanding. There's no rush. You can let it unfold at its own pace."

        # Gate 4-6: Medium intensity, balanced
        elif gate_num <= 6:
            tone = "balanced"  # noqa: F841  # tone used for clarity of mapping
            framing = "This is real. It deserves your attention, but you don't have to figure it all out at once."

        # Gate 7-9: High intensity, transformative
        else:
            tone = "intense"  # noqa: F841  # tone used for clarity of mapping
            framing = "This is transformative. Something in you is being remade by this experience. That's not comfortable, but it's necessary."

        return f"{framing}\n\n[{glyph_name}: {primary_emotion.lower()}]"


def create_training_response(
    glyph_candidate: Dict,
    original_input: str,
    signals: List[Dict],
    emotional_analysis: Dict
) -> str:
    """
    Convenience function: Given a glyph candidate and analysis,
    create the complete response that trains.
    """

    generator = LearningResponseGenerator()

    # Determine primary emotional tone
    emotional_tone = emotional_analysis.get("primary_tone", "unknown")
    emotional_terms = emotional_analysis.get("emotional_terms", {})
    nrc_analysis = emotional_analysis.get("nrc_analysis", {})

    response = generator.generate_learning_response(
        glyph_candidate=glyph_candidate,
        original_input=original_input,
        emotional_tone=emotional_tone,
        emotional_terms=emotional_terms,
        nrc_analysis=nrc_analysis
    )

    return response
