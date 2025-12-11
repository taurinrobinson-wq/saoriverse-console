"""
Prosody Planner - Maps Glyph Intent to Speech Prosody

Converts FirstPerson glyph signals (voltage, tone, certainty, etc.) into
SSML prosody directives for natural, emotionally-congruent text-to-speech.

Glyph Intent Schema:
- voltage: "low" | "medium" | "high" → maps to rate (slow/normal/fast) & volume
- tone: "negative" | "neutral" | "positive" → maps to pitch (low/medium/high)
- certainty: "low" | "neutral" | "high" → maps to intonation contour
- energy: float (0.0-1.0) → overall intensity
- hesitation: bool → adds pauses/stretches
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ProsodyPlanner:
    """Maps glyph signals into prosody controls for TTS"""

    def __init__(self):
        """Initialize prosody mappings"""
        self.rate_map = {
            "low": "slow",
            "medium": "medium",
            "high": "fast",
        }
        
        self.pitch_map = {
            "negative": "low",
            "neutral": "medium",
            "positive": "high",
        }
        
        self.volume_map = {
            "low": "soft",
            "medium": "medium",
            "high": "loud",
        }
        
        self.contour_map = {
            "low": "rising",      # uncertain, questioning
            "neutral": "neutral",  # neutral intonation
            "high": "falling",     # confident, declarative
        }

    def plan(self, text: str, glyph_intent: Optional[Dict[str, Any]] = None) -> str:
        """
        Convert glyph intent into SSML-marked text with prosody controls

        Args:
            text: Plain response text
            glyph_intent: Dict with keys:
                - voltage: "low" | "medium" | "high"
                - tone: "negative" | "neutral" | "positive"
                - certainty: "low" | "neutral" | "high"
                - energy: float (0.0-1.0)
                - hesitation: bool
                - phoneme_stretch: float (1.0 = normal)

        Returns:
            SSML string with prosody tags applied
        """
        if glyph_intent is None:
            glyph_intent = {}

        # Extract intent parameters with defaults
        voltage = glyph_intent.get("voltage", "medium")
        tone = glyph_intent.get("tone", "neutral")
        certainty = glyph_intent.get("certainty", "neutral")
        energy = glyph_intent.get("energy", 0.5)
        hesitation = glyph_intent.get("hesitation", False)
        phoneme_stretch = glyph_intent.get("phoneme_stretch", 1.0)

        # Map to prosody dimensions
        rate = self.rate_map.get(voltage, "medium")
        pitch = self.pitch_map.get(tone, "medium")
        volume = self.volume_map.get(voltage, "medium")
        contour = self.contour_map.get(certainty, "neutral")

        # Adjust rate based on energy
        if energy > 0.7:
            rate = "fast" if rate != "slow" else rate
        elif energy < 0.3:
            rate = "slow" if rate != "fast" else rate

        # Build SSML with prosody tags
        ssml = text

        # Add hesitation markers if needed
        if hesitation:
            # Insert pauses at natural breaks (periods, commas)
            import re
            ssml = re.sub(r'([.!?,;])', r'\1<break time="250ms"/>', ssml)

        # Wrap in prosody tag
        prosody_attrs = [
            f"rate='{rate}'",
            f"pitch='{pitch}'",
            f"volume='{volume}'",
        ]

        # Add phoneme stretch if provided
        if phoneme_stretch != 1.0:
            prosody_attrs.append(f"duration='{phoneme_stretch * 100}%'")

        ssml = f"<prosody {' '.join(prosody_attrs)}>{ssml}</prosody>"

        logger.debug(
            f"Prosody planned: voltage={voltage}, tone={tone}, certainty={certainty}, "
            f"energy={energy:.2f}, hesitation={hesitation}"
        )
        logger.debug(f"SSML: {ssml[:100]}...")

        return ssml

    def plan_for_chunks(self, chunks: list, glyph_intent: Optional[Dict[str, Any]] = None) -> list:
        """
        Apply prosody planning to a list of text chunks

        Args:
            chunks: List of text strings
            glyph_intent: Glyph intent dict (applies to all chunks)

        Returns:
            List of SSML-marked chunks
        """
        return [self.plan(chunk, glyph_intent) for chunk in chunks]

    def adjust_prosody_for_emphasis(self, text: str, emphasis_indices: list) -> str:
        """
        Add emphasis markup to specific chunks

        Args:
            text: Base text
            emphasis_indices: List of word indices to emphasize

        Returns:
            SSML with emphasis tags
        """
        words = text.split()
        for idx in emphasis_indices:
            if 0 <= idx < len(words):
                words[idx] = f"<emphasis level='strong'>{words[idx]}</emphasis>"
        return " ".join(words)

    def get_prosody_summary(self, glyph_intent: Optional[Dict[str, Any]] = None) -> str:
        """
        Get human-readable prosody summary for logging

        Args:
            glyph_intent: Glyph intent dict

        Returns:
            Summary string
        """
        if glyph_intent is None:
            glyph_intent = {}

        voltage = glyph_intent.get("voltage", "medium")
        tone = glyph_intent.get("tone", "neutral")
        certainty = glyph_intent.get("certainty", "neutral")
        energy = glyph_intent.get("energy", 0.5)

        rate = self.rate_map.get(voltage, "medium")
        pitch = self.pitch_map.get(tone, "medium")
        contour = self.contour_map.get(certainty, "neutral")

        return (
            f"Rate={rate}, Pitch={pitch}, Contour={contour}, "
            f"Energy={energy:.1f}, Voltage={voltage}"
        )
