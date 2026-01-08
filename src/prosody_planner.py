"""Sprint 2: Prosody Planning

Converts glyph emotional signals (voltage, tone, attunement) into prosody directives
for natural, intent-driven voice synthesis.

Architecture:
  Glyph Signals (voltage, tone, attunement, certainty)
    ↓
  Signal Bucketing (Low/Medium/High bands)
    ↓
  Prosody Mapping (rate, pitch, energy, emphasis, pause, contour)
    ↓
  Guardrail Application (smooth transitions, prevent uncanny valley)
    ↓
  Prosody Plan (SSML-like directives for TTS engine)
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ArousalBand(Enum):
    """Arousal level bands."""
    LOW = "low"        # Calm, slow, soft
    MEDIUM = "medium"  # Normal
    HIGH = "high"      # Energetic, fast, loud


class ValenceBand(Enum):
    """Valence level bands."""
    NEGATIVE = "negative"  # Sad, dark, lower pitch
    NEUTRAL = "neutral"    # Neutral
    POSITIVE = "positive"  # Happy, bright, higher pitch


class CertaintyBand(Enum):
    """Certainty level bands."""
    LOW = "low"        # Uncertain, questioning (rising pitch)
    MEDIUM = "medium"  # Moderate confidence
    HIGH = "high"      # Confident, assertive (falling pitch)


@dataclass
class GlyphSignals:
    """Emotional signals from glyph."""
    text: str
    voltage: float              # 0-1, arousal/intensity
    tone: str                   # e.g., "excited", "calm", "sad"
    emotional_attunement: float  # 0-1, empathy level
    certainty: float            # 0-1, confidence in response
    valence: float              # 0-1, negative to positive (optional)


@dataclass
class ProsodyPlan:
    """Prosody directives for TTS engine."""

    # Rate control (0.5 = half speed, 1.0 = normal, 1.5 = 1.5x speed)
    speaking_rate: float

    # Pitch shift in semitones (-12 to +12)
    pitch_shift_semitones: float

    # Energy/loudness multiplier (0.5 = quiet, 1.0 = normal, 1.5 = loud)
    energy_level: float

    # Emphasis tokens (which words to stress)
    emphasis_tokens: List[str]

    # Terminal contour ("falling", "rising", "mid")
    terminal_contour: str

    # Pause strategy ("short", "normal", "long")
    pause_strategy: str

    # Voice style ("formal", "casual", "warm", "professional")
    voice_style: str

    # Smoothing parameters
    transition_duration_ms: float  # How long to fade rate/pitch changes
    max_rate_change_per_second: float  # Cap rate acceleration
    max_pitch_change_per_second_semitones: float  # Cap pitch acceleration


class ProsodyPlanner:
    """Convert glyph signals to prosody plan."""

    def __init__(self):
        """Initialize prosody planner with default guardrails."""
        # Guardrails to prevent uncanny valley
        self.max_rate_change = 0.15  # ±15% per second
        self.max_pitch_change = 2.0  # ±2 semitones per second
        self.min_transition_ms = 150  # Min fade time
        self.max_transition_ms = 250  # Max fade time

    def plan_from_glyph(self, glyph_signals: GlyphSignals) -> ProsodyPlan:
        """
        Convert glyph signals to prosody plan.

        Args:
            glyph_signals: Emotional signals from glyph

        Returns:
            ProsodyPlan with all directives
        """
        # Step 1: Bucket signals into bands
        arousal_band = self._bucket_voltage(glyph_signals.voltage)
        valence_band = self._bucket_valence(glyph_signals.valence
                                            if glyph_signals.valence >= 0
                                            else self._infer_valence_from_tone(glyph_signals.tone))
        certainty_band = self._bucket_certainty(glyph_signals.certainty)

        # Step 2: Map to prosody features
        speaking_rate = self._rate_from_arousal(arousal_band)
        pitch_shift = self._pitch_from_valence(valence_band)
        energy = self._energy_from_arousal(arousal_band)

        # Step 3: Determine emphasis and terminal contour
        emphasis_tokens = self._emphasis_from_attunement(
            glyph_signals.text,
            glyph_signals.emotional_attunement
        )
        terminal_contour = self._terminal_from_certainty(certainty_band)
        pause_strategy = self._pause_from_certainty(certainty_band)

        # Step 4: Determine voice style
        voice_style = self._style_from_formality(glyph_signals.certainty)

        # Step 5: Create plan
        plan = ProsodyPlan(
            speaking_rate=speaking_rate,
            pitch_shift_semitones=pitch_shift,
            energy_level=energy,
            emphasis_tokens=emphasis_tokens,
            terminal_contour=terminal_contour,
            pause_strategy=pause_strategy,
            voice_style=voice_style,
            transition_duration_ms=self._transition_from_certainty(
                certainty_band),
            max_rate_change_per_second=self.max_rate_change,
            max_pitch_change_per_second_semitones=self.max_pitch_change,
        )

        # Step 6: Apply guardrails
        plan = self._apply_guardrails(plan)

        return plan

    # ========== BUCKETING ==========

    def _bucket_voltage(self, voltage: float) -> ArousalBand:
        """Bucket voltage (0-1) into arousal band."""
        voltage = np.clip(voltage, 0, 1)
        if voltage < 0.33:
            return ArousalBand.LOW
        elif voltage < 0.67:
            return ArousalBand.MEDIUM
        else:
            return ArousalBand.HIGH

    def _bucket_valence(self, valence: float) -> ValenceBand:
        """Bucket valence (0-1) into valence band."""
        valence = np.clip(valence, 0, 1)
        if valence < 0.33:
            return ValenceBand.NEGATIVE
        elif valence < 0.67:
            return ValenceBand.NEUTRAL
        else:
            return ValenceBand.POSITIVE

    def _bucket_certainty(self, certainty: float) -> CertaintyBand:
        """Bucket certainty (0-1) into certainty band."""
        certainty = np.clip(certainty, 0, 1)
        if certainty < 0.33:
            return CertaintyBand.LOW
        elif certainty < 0.67:
            return CertaintyBand.MEDIUM
        else:
            return CertaintyBand.HIGH

    def _infer_valence_from_tone(self, tone: str) -> float:
        """Quick valence inference from tone string."""
        positive_tones = {"happy", "excited",
                          "enthusiastic", "energetic", "cheerful"}
        negative_tones = {"sad", "angry", "frustrated", "anxious", "upset"}

        tone_lower = tone.lower()

        if any(t in tone_lower for t in positive_tones):
            return 0.7
        elif any(t in tone_lower for t in negative_tones):
            return 0.2
        else:
            return 0.5

    # ========== MAPPING TO PROSODY ==========

    def _rate_from_arousal(self, arousal: ArousalBand) -> float:
        """
        Map arousal to speaking rate multiplier.

        Low arousal → slow, soft (0.8x normal)
        Medium arousal → normal (1.0x)
        High arousal → fast, energetic (1.3x)
        """
        return {
            ArousalBand.LOW: 0.8,
            ArousalBand.MEDIUM: 1.0,
            ArousalBand.HIGH: 1.3,
        }[arousal]

    def _pitch_from_valence(self, valence: ValenceBand) -> float:
        """
        Map valence to pitch shift (semitones).

        Negative valence → lower pitch, darker timbre
        Neutral valence → normal pitch
        Positive valence → higher pitch, brighter timbre
        """
        return {
            ValenceBand.NEGATIVE: -2,
            ValenceBand.NEUTRAL: 0,
            ValenceBand.POSITIVE: +2,
        }[valence]

    def _energy_from_arousal(self, arousal: ArousalBand) -> float:
        """
        Map arousal to energy/loudness.

        Low arousal → quiet (0.7x normal)
        Medium arousal → normal (1.0x)
        High arousal → loud (1.3x)
        """
        return {
            ArousalBand.LOW: 0.7,
            ArousalBand.MEDIUM: 1.0,
            ArousalBand.HIGH: 1.3,
        }[arousal]

    def _emphasis_from_attunement(self, text: str,
                                  attunement: float) -> List[str]:
        """
        Determine which words to emphasize based on empathy level.

        High attunement (>0.7) → emphasize emotional words, names, commitments
        Medium attunement → balanced emphasis
        Low attunement → minimal emphasis
        """
        attunement = np.clip(attunement, 0, 1)

        if attunement > 0.7:
            # High empathy: find and emphasize emotional/important words
            return self._find_empathetic_tokens(text)
        elif attunement > 0.3:
            # Medium empathy: balanced approach
            return self._find_neutral_emphasis_tokens(text)
        else:
            # Low empathy: minimal emphasis
            return []

    def _terminal_from_certainty(self, certainty: CertaintyBand) -> str:
        """
        Map certainty to sentence-final contour.

        Certain → falling pitch at end (assertive)
        Uncertain → rising pitch at end (questioning)
        Medium → mid-level
        """
        return {
            CertaintyBand.LOW: "rising",
            CertaintyBand.MEDIUM: "mid",
            CertaintyBand.HIGH: "falling",
        }[certainty]

    def _pause_from_certainty(self, certainty: CertaintyBand) -> str:
        """
        Map certainty to pause strategy.

        Uncertain → short pauses (quick recovery, less confident)
        Confident → longer pauses (thoughtful, deliberate)
        """
        return {
            CertaintyBand.LOW: "short",
            CertaintyBand.MEDIUM: "normal",
            CertaintyBand.HIGH: "long",
        }[certainty]

    def _style_from_formality(self, certainty: float) -> str:
        """
        Determine voice style from formality (approximated by certainty).

        High certainty → professional, formal
        Medium certainty → conversational, warm
        Low certainty → gentle, uncertain
        """
        certainty = np.clip(certainty, 0, 1)

        if certainty > 0.7:
            return "professional"
        elif certainty > 0.3:
            return "warm"
        else:
            return "gentle"

    def _transition_from_certainty(self, certainty: CertaintyBand) -> float:
        """Fade time for prosody transitions (ms)."""
        return {
            CertaintyBand.LOW: 200,      # Quicker transitions when uncertain
            CertaintyBand.MEDIUM: 200,   # Normal
            CertaintyBand.HIGH: 250,     # Slightly longer for emphasis
        }[certainty]

    # ========== TOKEN FINDING ==========

    def _find_empathetic_tokens(self, text: str) -> List[str]:
        """Find words worthy of empathetic emphasis."""
        emotional_keywords = {
            "you", "your", "feel", "feeling", "understand", "care",
            "help", "support", "love", "important", "grateful", "thank",
            "name", "sorry", "apologize", "forgive", "friend",
        }

        words = text.lower().split()
        emphasized = [w for w in words if w in emotional_keywords]

        return emphasized[:3]  # Limit to top 3 to avoid over-emphasis

    def _find_neutral_emphasis_tokens(self, text: str) -> List[str]:
        """Find naturally important tokens (e.g., content words)."""
        # Rough heuristic: longer words are often more important
        words = text.split()
        # Take longer words (>6 chars)
        important = [w for w in words if len(w) > 6]

        return important[:2]  # Max 2 emphasized words

    # ========== GUARDRAILS ==========

    def _apply_guardrails(self, plan: ProsodyPlan) -> ProsodyPlan:
        """
        Apply guardrails to prevent uncanny valley.

        Rules:
        1. Cap rate changes to ±15% per second
        2. Cap pitch changes to ±2 semitones per second
        3. Fade transitions over 150-250ms
        4. Prevent extreme values (rate 0.5-2.0x, pitch -12 to +12)
        5. Ensure style matches prosody (e.g., formal → slower rate)
        """
        # Rule 1-2: Already set via max_*_change_per_second
        # Rule 3: Ensure transition duration is reasonable
        plan.transition_duration_ms = np.clip(
            plan.transition_duration_ms,
            self.min_transition_ms,
            self.max_transition_ms
        )

        # Rule 4: Clamp values to reasonable ranges
        plan.speaking_rate = np.clip(plan.speaking_rate, 0.5, 2.0)
        plan.pitch_shift_semitones = np.clip(
            plan.pitch_shift_semitones, -12, 12)
        plan.energy_level = np.clip(plan.energy_level, 0.3, 1.5)

        # Rule 5: Ensure style-prosody consistency
        plan = self._enforce_style_consistency(plan)

        return plan

    def _enforce_style_consistency(self, plan: ProsodyPlan) -> ProsodyPlan:
        """Ensure prosody matches declared voice style."""
        if plan.voice_style == "professional":
            # Professional: moderate rate, stable pitch
            plan.speaking_rate = np.clip(plan.speaking_rate, 0.85, 1.15)
            plan.energy_level = np.clip(plan.energy_level, 0.9, 1.1)

        elif plan.voice_style == "gentle":
            # Gentle: slower, softer, more rise at ends
            plan.speaking_rate = np.clip(plan.speaking_rate, 0.5, 0.9)
            plan.energy_level = np.clip(plan.energy_level, 0.3, 0.8)
            if plan.terminal_contour == "falling":
                plan.terminal_contour = "rising"

        elif plan.voice_style == "warm":
            # Warm: natural, conversational
            pass  # No special constraints

        return plan


class ProsodyExplainer:
    """Explain prosody decisions for debugging/tuning."""

    @staticmethod
    def explain_plan(glyph_signals: GlyphSignals,
                     plan: ProsodyPlan) -> str:
        """
        Generate human-readable explanation of prosody plan.

        Args:
            glyph_signals: Input signals
            plan: Generated prosody plan

        Returns:
            Explanation string
        """
        lines = [
            "🎙️ Prosody Plan Explanation:",
            "",
            f"Input Signals:",
            f"  • Voltage (arousal): {glyph_signals.voltage:.1%}",
            f"  • Tone: {glyph_signals.tone}",
            f"  • Emotional attunement: {glyph_signals.emotional_attunement:.1%}",
            f"  • Certainty: {glyph_signals.certainty:.1%}",
            "",
            f"Prosody Directives:",
            f"  • Speaking rate: {plan.speaking_rate:.2f}x normal"
            f" → {'slower' if plan.speaking_rate < 1.0 else 'faster' if plan.speaking_rate > 1.0 else 'normal'}",
            f"  • Pitch shift: {plan.pitch_shift_semitones:+.0f} semitones"
            f" → {'lower, darker' if plan.pitch_shift_semitones < 0 else 'higher, brighter' if plan.pitch_shift_semitones > 0 else 'normal'}",
            f"  • Energy level: {plan.energy_level:.2f}x"
            f" → {'quieter' if plan.energy_level < 1.0 else 'louder' if plan.energy_level > 1.0 else 'normal'}",
            f"  • Voice style: {plan.voice_style}",
            f"  • Terminal contour: {plan.terminal_contour}"
            f" → {'questioning' if plan.terminal_contour == 'rising' else 'assertive' if plan.terminal_contour == 'falling' else 'neutral'}",
            f"  • Pause strategy: {plan.pause_strategy}",
            f"  • Emphasized words: {', '.join(plan.emphasis_tokens) if plan.emphasis_tokens else '(none)'}",
            "",
            f"Effect:",
        ]

        # Add interpretation
        if plan.speaking_rate > 1.2 and plan.energy_level > 1.2:
            lines.append("  → Fast, energetic, enthusiastic")
        elif plan.speaking_rate < 0.9 and plan.energy_level < 0.9:
            lines.append("  → Slow, soft, gentle")
        elif plan.terminal_contour == "rising":
            lines.append("  → Questioning tone, uncertainty")
        elif plan.terminal_contour == "falling":
            lines.append("  → Confident, assertive")
        else:
            lines.append("  → Conversational, balanced")

        return "\n".join(lines)


# Example usage and testing
if __name__ == "__main__":
    planner = ProsodyPlanner()
    explainer = ProsodyExplainer()

    # Example 1: Excited, confident response
    signals1 = GlyphSignals(
        text="I'm so excited to help you with this!",
        voltage=0.8,
        tone="excited",
        emotional_attunement=0.7,
        certainty=0.9,
        valence=0.8,
    )

    plan1 = planner.plan_from_glyph(signals1)
    print(explainer.explain_plan(signals1, plan1))
    print("\n" + "="*60 + "\n")

    # Example 2: Concerned, uncertain response
    signals2 = GlyphSignals(
        text="I'm not sure if this is the right approach...",
        voltage=0.3,
        tone="anxious",
        emotional_attunement=0.6,
        certainty=0.3,
        valence=0.3,
    )

    plan2 = planner.plan_from_glyph(signals2)
    print(explainer.explain_plan(signals2, plan2))
