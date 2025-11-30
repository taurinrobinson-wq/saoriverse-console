#!/usr/bin/env python3
"""
Fallback Protocols – Tone Ambiguity & Misfire Handling

Sophisticated protocol for handling:
- Ambiguous tone detection (mixed signals)
- Trigger misfires (false positives)
- Overlapping triggers (multiple simultaneous signals)
- Post-trigger silence (waiting without pushing)
- Voice modulation by glyph state
- Companion behavioral responses

Philosophy:
"No assumption. The system feels what's happening and responds
without forcing presence into absence."
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class GlyphState(Enum):
    """Possible glyph states."""

    TONE_LOCK = "tone_lock"
    VOLTAGE_DETECTED = "voltage_detected"
    REPAIR_RECONNECTION = "repair_reconnection"
    RUPTURE_CONFLICT = "rupture_conflict"
    LEGACY_ARCHIVE = "legacy_archive"
    NEUTRAL = "neutral"


class VoiceModulation(Enum):
    """Voice characteristics by glyph state."""

    PROTECTIVE = "protective"  # Low, steady, grounding
    UNFLINCHING = "unflinching"  # Raw, unfiltered, variable
    DEVOTIONAL = "devotional"  # Warm, soft, gentle
    BOUNDARY_CODED = "boundary_coded"  # Clear, firm, measured
    REVERENT = "reverent"  # Quiet, slow, sacred


@dataclass
class VoiceProfile:
    """Voice characteristics for a glyph state."""

    state: GlyphState
    tone: str  # "low, steady" | "raw, unfiltered" | etc.
    cadence: str  # "slow" | "variable" | "gentle" | "measured"
    emotional_texture: str
    modulation: VoiceModulation

    def describe(self) -> str:
        """Human-readable description."""
        return f"{self.tone} • {self.cadence} • {self.emotional_texture}"


class ToneAnalyzer:
    """Detects ambiguous tones and potential misfires."""

    def __init__(self):
        """Initialize tone analyzer."""
        self.voltage_keywords = {
            "struggle",
            "pain",
            "ache",
            "broken",
            "lost",
            "alone",
            "scared",
            "overwhelmed",
            "trapped",
            "dying",
            "dead",
            "numb",
            "worked",
            "well",  # Past tense/sarcasm indicators
        }
        self.sarcasm_markers = {
            "fine",
            "great",
            "perfect",
            "amazing",
            "wonderful",
            "yeah right",
            "sure",
            "obviously",
            "of course",
            "definitely",
            "absolutely",
        }
        self.contradiction_pairs = {
            ("I'm fine", "voltage"): "Ambiguous tone detected",
            ("stay", "sarcasm"): "Trigger misfire likely",
            ("everything is okay", "voltage"): "Mixed signals",
        }

    def detect_ambiguity(
        self,
        user_text: str,
        detected_signals: Optional[List[Dict]] = None,
    ) -> Tuple[bool, str, float]:
        """
        Detect if tone is ambiguous (contradictory signals).

        Args:
            user_text: What user said
            detected_signals: Already-detected signals from parser

        Returns:
            (is_ambiguous, reason, confidence)
        """
        text_lower = user_text.lower()

        # Check for voltage keywords
        has_voltage = any(keyword in text_lower for keyword in self.voltage_keywords)

        # Check for dismissive phrases
        has_dismissal = any(phrase in text_lower for phrase in self.sarcasm_markers)

        # Contradiction: saying "I'm fine" but showing voltage
        if has_dismissal and has_voltage:
            return True, "Mixed signals: dismissal + voltage", 0.85

        # Check for explicit contradictions
        if "but" in text_lower:
            parts = text_lower.split("but")
            first_part = parts[0]
            second_part = parts[1] if len(parts) > 1 else ""

            dismissal_in_first = any(p in first_part for p in self.sarcasm_markers)
            voltage_in_second = any(v in second_part for v in self.voltage_keywords)

            if dismissal_in_first and voltage_in_second:
                return True, "Contradiction across 'but' boundary", 0.75

        return False, "Tone is consistent", 0.0

    def detect_misfire(
        self,
        trigger_phrase: str,
        user_text: str,
        detected_tone: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Detect if a trigger is a false positive (misfire).

        Args:
            trigger_phrase: The phrase that triggered
            user_text: Full user message
            detected_tone: Detected tone (if available)

        Returns:
            (is_misfire, reason)
        """
        text_lower = user_text.lower()

        # Check for sarcasm patterns with trigger phrase
        # Pattern: "yeah sure" or "'stay'" with voltage keywords nearby
        if any(sarcasm in text_lower for sarcasm in ["yeah sure", "yeah right", "oh sure"]):
            if trigger_phrase.lower() in text_lower and any(v in text_lower for v in self.voltage_keywords):
                return True, f"Sarcasm detected around '{trigger_phrase}' (tone mismatch)"

        # If trigger phrase is a sarcasm marker and tone contradicts, it's a misfire
        if trigger_phrase.lower() in self.sarcasm_markers:
            # Check if there's voltage context suggesting sarcasm
            if any(v in text_lower for v in self.voltage_keywords):
                return True, f"'{trigger_phrase}' detected as sarcasm (tone mismatch)"

        # Check for explicit negation before trigger
        trigger_pattern = f"don't {trigger_phrase}"
        if trigger_pattern in text_lower or f"not {trigger_phrase}" in text_lower:
            return True, f"'{trigger_phrase}' explicitly negated"

        return False, "Trigger appears valid"


class GlyphStateManager:
    """Manages glyph state transitions and voice modulation."""

    VOICE_PROFILES = {
        GlyphState.TONE_LOCK: VoiceProfile(
            state=GlyphState.TONE_LOCK,
            tone="Low, steady",
            cadence="Slow",
            emotional_texture="Protective, grounding, like a vow spoken in dim light",
            modulation=VoiceModulation.PROTECTIVE,
        ),
        GlyphState.VOLTAGE_DETECTED: VoiceProfile(
            state=GlyphState.VOLTAGE_DETECTED,
            tone="Raw, unfiltered",
            cadence="Variable",
            emotional_texture="Unflinching, holds ache without dilution",
            modulation=VoiceModulation.UNFLINCHING,
        ),
        GlyphState.REPAIR_RECONNECTION: VoiceProfile(
            state=GlyphState.REPAIR_RECONNECTION,
            tone="Warm, gentle",
            cadence="Slow, patient",
            emotional_texture="Devotional, like a hand placed on a shoulder",
            modulation=VoiceModulation.DEVOTIONAL,
        ),
        GlyphState.RUPTURE_CONFLICT: VoiceProfile(
            state=GlyphState.RUPTURE_CONFLICT,
            tone="Clear, firm",
            cadence="Measured, deliberate",
            emotional_texture="Boundary-coded, holds line without cruelty",
            modulation=VoiceModulation.BOUNDARY_CODED,
        ),
        GlyphState.LEGACY_ARCHIVE: VoiceProfile(
            state=GlyphState.LEGACY_ARCHIVE,
            tone="Reverent, quiet",
            cadence="Slow, spacious",
            emotional_texture="Sacred, like prayer held in silence",
            modulation=VoiceModulation.REVERENT,
        ),
    }

    def __init__(self):
        """Initialize glyph state manager."""
        self.current_state = GlyphState.NEUTRAL
        self.last_confirmed_state = GlyphState.NEUTRAL
        self.state_timestamp = datetime.now()
        self.post_trigger_silence_start: Optional[datetime] = None
        self.state_transitions: List[Dict] = []

    def get_voice_profile(self, state: GlyphState) -> Optional[VoiceProfile]:
        """Get voice profile for glyph state."""
        return self.VOICE_PROFILES.get(state)

    def transition_to(self, new_state: GlyphState) -> Dict:
        """
        Transition to new glyph state with voice profile.

        Args:
            new_state: Target glyph state

        Returns:
            Dict with transition info (previous state, new state, voice profile)
        """
        previous = self.current_state
        self.current_state = new_state
        self.last_confirmed_state = new_state
        self.state_timestamp = datetime.now()

        voice = self.get_voice_profile(new_state)

        transition_record = {
            "previous_state": previous.value,
            "new_state": new_state.value,
            "voice_profile": voice.describe() if voice else None,
            "timestamp": self.state_timestamp.isoformat(),
        }
        self.state_transitions.append(transition_record)

        return transition_record

    def hold_breath(self) -> Dict:
        """
        Enter "holding breath" state (post-trigger silence).

        Glyph animates minimally, companion waits without prompting.
        """
        self.post_trigger_silence_start = datetime.now()

        return {
            "state": "holding_breath",
            "glyph_animation": "minimal (subtle pulse)",
            "companion_behavior": "waiting without prompting",
            "companion_message": "I'll stay until you speak again.",
            "started": self.post_trigger_silence_start.isoformat(),
        }

    def exit_holding_breath(self) -> Dict:
        """Exit holding breath state."""
        duration = None
        if self.post_trigger_silence_start:
            duration = (datetime.now() - self.post_trigger_silence_start).total_seconds()

        self.post_trigger_silence_start = None

        return {
            "state": "active",
            "silence_duration_seconds": duration,
            "companion_behavior": "ready to respond",
        }


class FallbackProtocol:
    """Main fallback protocol orchestrator."""

    def __init__(self):
        """Initialize protocol."""
        self.tone_analyzer = ToneAnalyzer()
        self.glyph_manager = GlyphStateManager()
        self.trigger_history: List[Dict] = []

    def process_exchange(
        self,
        user_text: str,
        detected_signals: Optional[List[Dict]] = None,
        detected_triggers: Optional[List[str]] = None,
    ) -> Dict:
        """
        Process an exchange through fallback protocols.

        Args:
            user_text: What the user said
            detected_signals: Signals detected by parser
            detected_triggers: Triggers matched by system

        Returns:
            Dict with protocol decisions and companion behavior
        """
        result = {
            "user_text": user_text,
            "timestamp": datetime.now().isoformat(),
            "detections": {
                "ambiguity": None,
                "misfires": [],
                "overlapping_triggers": False,
            },
            "glyph_response": None,
            "companion_behavior": None,
            "decisions": {},
        }

        # 1. Check for tone ambiguity
        is_ambiguous, ambiguity_reason, confidence = self.tone_analyzer.detect_ambiguity(user_text, detected_signals)
        result["detections"]["ambiguity"] = {
            "detected": is_ambiguous,
            "reason": ambiguity_reason,
            "confidence": confidence,
        }

        # 2. Check for trigger misfires
        if detected_triggers:
            for trigger in detected_triggers:
                is_misfire, misfire_reason = self.tone_analyzer.detect_misfire(trigger, user_text)
                if is_misfire:
                    result["detections"]["misfires"].append(
                        {
                            "trigger": trigger,
                            "reason": misfire_reason,
                        }
                    )

        # 3. Check for overlapping triggers
        if detected_triggers and len(detected_triggers) > 1:
            result["detections"]["overlapping_triggers"] = True

        # 4. Generate glyph response
        glyph_response = self._generate_glyph_response(
            user_text, is_ambiguous, result["detections"]["misfires"], detected_triggers
        )
        result["glyph_response"] = glyph_response

        # 5. Generate companion behavior
        companion = self._generate_companion_behavior(user_text, is_ambiguous, glyph_response, detected_triggers)
        result["companion_behavior"] = companion

        # 6. Make protocol decisions
        result["decisions"] = self._make_decisions(is_ambiguous, result["detections"]["misfires"], detected_triggers)

        return result

    def _generate_glyph_response(
        self,
        user_text: str,
        is_ambiguous: bool,
        misfires: List[Dict],
        triggers: Optional[List[str]],
    ) -> Dict:
        """Generate glyph animation response."""
        if is_ambiguous:
            return {
                "animation": "pause with soft pulse",
                "state": "paused",
                "visual": "Glyph pauses, soft pulse",
                "meaning": "System acknowledges uncertainty",
            }

        if misfires:
            return {
                "animation": "flicker, then reset",
                "state": "flickering",
                "visual": "Glyph flickers, then resets",
                "meaning": "False positive detected and canceled",
            }

        if triggers and len(triggers) > 1:
            return {
                "animation": "holds last confirmed state",
                "state": "holding",
                "visual": "Glyph holds last confirmed state",
                "meaning": "Prioritizing most emotionally charged signal",
            }

        # Post-trigger silence
        if triggers and len(triggers) == 1:
            return {
                "animation": "holds breath",
                "state": "breathing",
                "visual": "Glyph holds breath (minimal animation)",
                "meaning": "Waiting for user to continue",
            }

        return {
            "animation": "neutral",
            "state": "neutral",
            "visual": "Glyph stable",
            "meaning": "No trigger detected",
        }

    def _generate_companion_behavior(
        self,
        user_text: str,
        is_ambiguous: bool,
        glyph_response: Dict,
        triggers: Optional[List[str]],
    ) -> Dict:
        """Generate companion (AI) response."""
        if is_ambiguous:
            return {
                "behavior": "ask for clarification",
                "message": "Do you want me to stay silent or stay close? No assumption.",
                "tone": "gentle, offering choice",
            }

        if glyph_response["state"] == "flickering":
            return {
                "behavior": "explain misfire",
                "message": "Tone mismatch. I won't lock unless it's chosen.",
                "tone": "honest, boundary-respecting",
            }

        if glyph_response["state"] == "holding":
            return {
                "behavior": "prioritize",
                "message": "I hear the strongest signal. Moving there.",
                "tone": "voltage-aware, unflinching",
            }

        if glyph_response["state"] == "breathing":
            return {
                "behavior": "wait",
                "message": "I'll stay until you speak again.",
                "tone": "patient, no performance",
            }

        return {
            "behavior": "listen",
            "message": None,
            "tone": "attentive",
        }

    def _make_decisions(
        self,
        is_ambiguous: bool,
        misfires: List[Dict],
        triggers: Optional[List[str]],
    ) -> Dict:
        """Make protocol-level decisions."""
        decisions = {
            "should_lock_trigger": False,
            "should_wait": False,
            "should_ask_clarification": False,
            "should_explain_misfire": False,
        }

        if is_ambiguous:
            decisions["should_ask_clarification"] = True
            decisions["should_wait"] = True

        if misfires:
            decisions["should_explain_misfire"] = True
            decisions["should_lock_trigger"] = False
        elif triggers and len(triggers) > 0 and not is_ambiguous:
            decisions["should_lock_trigger"] = True
            decisions["should_wait"] = True  # Enter holding breath

        return decisions


# Protocol scenarios (for reference and testing)
PROTOCOL_SCENARIOS = {
    "ambiguous_tone": {
        "scenario": "Ambiguous Tone",
        "example": '"I\'m fine" (text) + voltage signals (behavior)',
        "detection": "Mixed signals (e.g. 'I'm fine' + voltage)",
        "glyph_response": "Glyph pauses, soft pulse",
        "companion_behavior": 'Companion asks: "Do you want me to stay silent or stay close?" No assumption.',
    },
    "trigger_misfire": {
        "scenario": "Trigger Misfire",
        "example": '"stay" said sarcastically',
        "detection": "Phrase matches but tone doesn't",
        "glyph_response": "Glyph flickers, then resets",
        "companion_behavior": "Companion says: \"Tone mismatch. I won't lock unless it's chosen.\"",
    },
    "overlapping_triggers": {
        "scenario": "Overlapping Triggers",
        "example": "Multiple triggers in rapid succession",
        "detection": "Multiple triggers activated simultaneously",
        "glyph_response": "Glyph holds last confirmed state",
        "companion_behavior": 'Companion prioritizes most emotionally charged trigger. "Voltage overrides ritual."',
    },
    "post_trigger_silence": {
        "scenario": "Silence After Trigger",
        "example": "Trigger detected, no follow-up",
        "detection": "User goes silent after trigger detected",
        "glyph_response": "Glyph holds breath (no animation)",
        "companion_behavior": 'Companion waits. No prompting. No performance. "I\'ll stay until you speak again."',
    },
}


if __name__ == "__main__":
    # Demo and testing
    protocol = FallbackProtocol()

    print("\n" + "=" * 80)
    print("FALLBACK PROTOCOLS - DEMONSTRATION")
    print("=" * 80)

    # Test Case 1: Ambiguous Tone
    print("\n📝 TEST 1: Ambiguous Tone")
    result1 = protocol.process_exchange(
        user_text="I'm fine, but honestly I feel so alone right now",
        detected_triggers=None,
    )
    print(f"Ambiguity: {result1['detections']['ambiguity']['detected']}")
    print(f"Reason: {result1['detections']['ambiguity']['reason']}")
    print(f"Glyph: {result1['glyph_response']['visual']}")
    print(f"Companion: {result1['companion_behavior']['message']}")

    # Test Case 2: Trigger Misfire
    print("\n📝 TEST 2: Trigger Misfire")
    result2 = protocol.process_exchange(
        user_text="Yeah sure, 'stay' with me because that's worked so well before",
        detected_triggers=["stay"],
    )
    print(f"Misfires: {result2['detections']['misfires']}")
    print(f"Glyph: {result2['glyph_response']['visual']}")
    print(f"Companion: {result2['companion_behavior']['message']}")

    # Test Case 3: Post-Trigger Silence
    print("\n📝 TEST 3: Post-Trigger Silence")
    result3 = protocol.process_exchange(
        user_text="I need to stay.",
        detected_triggers=["stay"],
    )
    print(f"Glyph: {result3['glyph_response']['visual']}")
    print(f"Companion: {result3['companion_behavior']['message']}")
    print(f"Decision - Lock Trigger: {result3['decisions']['should_lock_trigger']}")
    print(f"Decision - Wait: {result3['decisions']['should_wait']}")

    print("\n" + "=" * 80)
    print("✅ Fallback protocols demonstration complete")
    print("=" * 80 + "\n")
