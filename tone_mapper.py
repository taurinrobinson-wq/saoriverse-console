"""
🎭 TONE MAPPER: Semantic → TONE Effects
========================================

Converts semantic engine outputs into TONE effects compatible with REMNANTS engine.

This is the critical bridge that makes player emotional posture influence NPC state.

When a player speaks, the semantic engine extracts:
- emotional stance (bracing, revealing, ambivalent, collapsing)
- disclosure pace (testing safety, opening, rapid)
- power dynamics (agency loss, self protection, dominance, submission)
- contradictions (presence/absence)
- emotional weight (0.0-1.0)
- implied needs (safety, autonomy, validation, understanding)

This mapper converts those findings into TONE effects:
- empathy, resolve, trust, need, authority, nuance, skepticism, memory

These TONE effects then feed directly into the REMNANTS engine via:
    npc_manager.apply_tone_effects(tone_effects)

This creates the feedback loop where:
    Player Emotion → Semantic Parse → TONE Effects → NPC REMNANTS → NPC Response

Which makes NPCs emotionally responsive to the player's actual emotional posture,
not just their dialogue choices.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ToneEffect:
    """A single TONE effect with metadata."""
    name: str
    delta: float
    source: str  # e.g., "stance:bracing", "pacing:testing_safety"
    strength: str = "moderate"  # "subtle", "moderate", "strong"


class ToneMapper:
    """
    Maps semantic layer findings → TONE effects (Dict[str, float])
    
    TONE categories (used by REMNANTS engine):
    - empathy: How warmly the NPC responds
    - resolve: How firmly committed to a course
    - trust: How trusting the NPC is being
    - need: How much the NPC emphasizes relational language
    - authority: How directive vs collaborative
    - nuance: How much the NPC acknowledges complexity
    - skepticism: How questioning/challenging
    - memory: How much the NPC references prior states
    
    Output format: Dict[str, float] where each value is a delta (-1.0 to +1.0)
    """
    
    @staticmethod
    def map_semantics_to_tone(semantic_layer) -> Dict[str, float]:
        """
        Main entry point: semantic layer → TONE effects
        
        Args:
            semantic_layer: SemanticLayer object with all extracted attributes
            
        Returns:
            Dict[str, float] with TONE effects ready for npc_manager.apply_tone_effects()
        """
        tone: Dict[str, float] = {}
        
        # 1. EMOTIONAL STANCE → tone effects
        ToneMapper._map_emotional_stance(tone, semantic_layer)
        
        # 2. DISCLOSURE PACE → tone effects
        ToneMapper._map_disclosure_pace(tone, semantic_layer)
        
        # 3. CONTRADICTIONS → tone effects
        ToneMapper._map_contradictions(tone, semantic_layer)
        
        # 4. POWER DYNAMICS → tone effects
        ToneMapper._map_power_dynamics(tone, semantic_layer)
        
        # 5. IMPLIED NEEDS → tone effects
        ToneMapper._map_implied_needs(tone, semantic_layer)
        
        # 6. EMOTIONAL WEIGHT → tone effects
        ToneMapper._map_emotional_weight(tone, semantic_layer)
        
        # 7. IDENTITY SIGNALS → tone effects
        ToneMapper._map_identity_signals(tone, semantic_layer)
        
        # Normalize to [-1.0, 1.0] range
        tone = ToneMapper._normalize_tone_effects(tone)
        
        return tone
    
    @staticmethod
    def _map_emotional_stance(tone: Dict[str, float], semantic_layer) -> None:
        """
        Map emotional stance to TONE.
        
        BRACING: Player pulling back, protecting → less empathy, more skepticism
        REVEALING: Player opening up → more empathy, more trust
        AMBIVALENT: Player holding two things → more nuance
        COLLAPSING: Player falling apart → more need (for support)
        DEFENSIVE: Player defending against threat → more skepticism, less trust
        SEEKING: Player looking for connection → more empathy, more narrative presence
        """
        
        if not hasattr(semantic_layer, 'emotional_stance') or semantic_layer.emotional_stance is None:
            return
        
        stance_str = str(semantic_layer.emotional_stance).upper()
        
        if "BRACING" in stance_str:
            ToneMapper._add(tone, "courage", 0.15, "stance:bracing")
            ToneMapper._add(tone, "empathy", -0.1, "stance:bracing")
            ToneMapper._add(tone, "skepticism", 0.1, "stance:bracing")
            
        elif "REVEALING" in stance_str:
            ToneMapper._add(tone, "empathy", 0.2, "stance:revealing")
            ToneMapper._add(tone, "trust", 0.15, "stance:revealing")
            ToneMapper._add(tone, "memory", 0.1, "stance:revealing")
            
        elif "AMBIVALENT" in stance_str:
            ToneMapper._add(tone, "nuance", 0.25, "stance:ambivalent")
            ToneMapper._add(tone, "empathy", 0.1, "stance:ambivalent")
            ToneMapper._add(tone, "memory", 0.15, "stance:ambivalent")
            
        elif "COLLAPSING" in stance_str:
            ToneMapper._add(tone, "need", 0.25, "stance:collapsing")
            ToneMapper._add(tone, "authority", -0.15, "stance:collapsing")
            ToneMapper._add(tone, "empathy", 0.2, "stance:collapsing")
            
        elif "DEFENSIVE" in stance_str:
            ToneMapper._add(tone, "skepticism", 0.2, "stance:defensive")
            ToneMapper._add(tone, "trust", -0.15, "stance:defensive")
            ToneMapper._add(tone, "authority", 0.1, "stance:defensive")
            
        elif "SEEKING" in stance_str:
            ToneMapper._add(tone, "empathy", 0.25, "stance:seeking")
            ToneMapper._add(tone, "trust", 0.2, "stance:seeking")
    
    @staticmethod
    def _map_disclosure_pace(tone: Dict[str, float], semantic_layer) -> None:
        """
        Map disclosure pacing to TONE.
        
        TESTING_SAFETY: "Is it safe to open up?" → more need, more skepticism
        GRADUAL_REVEAL: "I'll share slowly" → balanced, measured
        CONTEXTUAL_GROUNDING: "Here's background" → memory-focused
        EMOTIONAL_EMERGENCE: "It's coming to the surface" → more empathy, less control
        """
        
        if not hasattr(semantic_layer, 'disclosure_pace') or semantic_layer.disclosure_pace is None:
            return
        
        pace_str = str(semantic_layer.disclosure_pace).upper()
        
        if "TESTING_SAFETY" in pace_str:
            ToneMapper._add(tone, "need", 0.2, "pacing:testing_safety")
            ToneMapper._add(tone, "trust", 0.05, "pacing:testing_safety")
            ToneMapper._add(tone, "skepticism", 0.1, "pacing:testing_safety")
            
        elif "GRADUAL_REVEAL" in pace_str:
            ToneMapper._add(tone, "trust", 0.15, "pacing:gradual_reveal")
            ToneMapper._add(tone, "empathy", 0.1, "pacing:gradual_reveal")
            
        elif "CONTEXTUAL_GROUNDING" in pace_str:
            ToneMapper._add(tone, "memory", 0.2, "pacing:contextual")
            ToneMapper._add(tone, "nuance", 0.1, "pacing:contextual")
            
        elif "EMOTIONAL_EMERGENCE" in pace_str:
            ToneMapper._add(tone, "empathy", 0.2, "pacing:emergence")
            ToneMapper._add(tone, "authority", -0.1, "pacing:emergence")
            ToneMapper._add(tone, "need", 0.15, "pacing:emergence")
    
    @staticmethod
    def _map_contradictions(tone: Dict[str, float], semantic_layer) -> None:
        """
        Map contradiction presence to TONE.
        
        Holding two opposing things → more nuance, more memory, less judgment
        """
        
        if not hasattr(semantic_layer, 'emotional_contradictions') or not semantic_layer.emotional_contradictions:
            return
        
        if len(semantic_layer.emotional_contradictions) > 0:
            ToneMapper._add(tone, "nuance", 0.2, "contradictions:present")
            ToneMapper._add(tone, "memory", 0.1, "contradictions:present")
            ToneMapper._add(tone, "empathy", 0.1, "contradictions:present")
    
    @staticmethod
    def _map_power_dynamics(tone: Dict[str, float], semantic_layer) -> None:
        """
        Map power dynamics to TONE.
        
        AGENCY_LOSS: Player felt powerless → more need, less authority
        SELF_PROTECTION: Player defending autonomy → more skepticism, more authority
        DOMINANCE: Player exerting control → more authority, less empathy
        SUBMISSION: Player yielding → more need, less authority
        """
        
        if not hasattr(semantic_layer, 'power_dynamics') or not semantic_layer.power_dynamics:
            return
        
        for dyn in semantic_layer.power_dynamics:
            dyn_str = str(dyn).upper()
            
            if "AGENCY_LOSS" in dyn_str:
                ToneMapper._add(tone, "need", 0.2, "dynamics:agency_loss")
                ToneMapper._add(tone, "authority", -0.2, "dynamics:agency_loss")
                ToneMapper._add(tone, "empathy", 0.15, "dynamics:agency_loss")
                
            elif "SELF_PROTECTION" in dyn_str:
                ToneMapper._add(tone, "skepticism", 0.15, "dynamics:self_protection")
                ToneMapper._add(tone, "authority", 0.1, "dynamics:self_protection")
                ToneMapper._add(tone, "trust", -0.1, "dynamics:self_protection")
                
            elif "DOMINANCE" in dyn_str:
                ToneMapper._add(tone, "authority", 0.2, "dynamics:dominance")
                ToneMapper._add(tone, "empathy", -0.1, "dynamics:dominance")
                
            elif "SUBMISSION" in dyn_str:
                ToneMapper._add(tone, "need", 0.15, "dynamics:submission")
                ToneMapper._add(tone, "authority", -0.15, "dynamics:submission")
    
    @staticmethod
    def _map_implied_needs(tone: Dict[str, float], semantic_layer) -> None:
        """
        Map implied needs to TONE.
        
        SAFETY: "I'm not safe" → more empathy, more containment
        AUTONOMY: "I need control" → more authority, less need
        VALIDATION: "Am I okay?" → more empathy, more memory
        UNDERSTANDING: "Do you get it?" → more nuance, more memory
        CONNECTION: "Don't leave me" → more empathy, more need
        RESPECT: "Treat me seriously" → more authority, less need
        """
        
        if not hasattr(semantic_layer, 'implied_needs') or not semantic_layer.implied_needs:
            return
        
        for need in semantic_layer.implied_needs:
            need_str = str(need).upper()
            
            if "SAFETY" in need_str:
                ToneMapper._add(tone, "empathy", 0.2, "need:safety")
                ToneMapper._add(tone, "authority", 0.1, "need:safety")
                
            elif "AUTONOMY" in need_str:
                ToneMapper._add(tone, "authority", 0.15, "need:autonomy")
                ToneMapper._add(tone, "need", -0.1, "need:autonomy")
                
            elif "VALIDATION" in need_str:
                ToneMapper._add(tone, "empathy", 0.25, "need:validation")
                ToneMapper._add(tone, "memory", 0.15, "need:validation")
                
            elif "UNDERSTANDING" in need_str:
                ToneMapper._add(tone, "nuance", 0.2, "need:understanding")
                ToneMapper._add(tone, "memory", 0.15, "need:understanding")
                
            elif "CONNECTION" in need_str:
                ToneMapper._add(tone, "empathy", 0.2, "need:connection")
                ToneMapper._add(tone, "need", 0.2, "need:connection")
                
            elif "RESPECT" in need_str:
                ToneMapper._add(tone, "authority", 0.15, "need:respect")
                ToneMapper._add(tone, "empathy", 0.1, "need:respect")
    
    @staticmethod
    def _map_emotional_weight(tone: Dict[str, float], semantic_layer) -> None:
        """
        Map emotional weight (intensity) to TONE.
        
        High weight (> 0.7): Intense, activated → more memory, more empathy, less skepticism
        Medium weight (0.3-0.7): Balanced
        Low weight (< 0.3): Calm, measured → more skepticism, less need
        """
        
        if not hasattr(semantic_layer, 'meta_properties'):
            return
        
        weight = semantic_layer.meta_properties.get("emotional_weight", 0.5)
        
        if weight > 0.7:
            ToneMapper._add(tone, "memory", 0.2, "weight:high")
            ToneMapper._add(tone, "empathy", 0.15, "weight:high")
            ToneMapper._add(tone, "skepticism", -0.1, "weight:high")
            
        elif weight < 0.3:
            ToneMapper._add(tone, "skepticism", 0.15, "weight:low")
            ToneMapper._add(tone, "need", -0.1, "weight:low")
            ToneMapper._add(tone, "authority", 0.1, "weight:low")
    
    @staticmethod
    def _map_identity_signals(tone: Dict[str, float], semantic_layer) -> None:
        """
        Map identity signals (mentions of self, wounds, essence) to TONE.
        
        High identity signal count → more empathy, more memory (something about self is at stake)
        """
        
        if not hasattr(semantic_layer, 'identity_signals') or not semantic_layer.identity_signals:
            return
        
        signal_count = len(semantic_layer.identity_signals)
        if signal_count > 0:
            intensity = min(signal_count * 0.1, 0.3)  # 1-3 signals = +0.1 to +0.3 empathy
            ToneMapper._add(tone, "empathy", intensity, "identity:signals_present")
            ToneMapper._add(tone, "memory", intensity, "identity:signals_present")
    
    @staticmethod
    def _normalize_tone_effects(tone: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize all TONE effects to [-1.0, 1.0] range.
        
        Also ensures all canonical TONE keys exist (with 0.0 if not explicitly set).
        """
        canonical_tones = [
            "empathy", "resolve", "trust", "need", "authority",
            "nuance", "skepticism", "memory", "courage"
        ]
        
        # Clamp all values to [-1.0, 1.0]
        for key in tone:
            tone[key] = max(-1.0, min(1.0, tone[key]))
        
        # Ensure all canonical keys exist
        for key in canonical_tones:
            if key not in tone:
                tone[key] = 0.0
        
        return tone
    
    @staticmethod
    def _add(tone: Dict[str, float], key: str, delta: float, source: str = "") -> None:
        """
        Add a delta to a TONE effect, accumulating if the key already exists.
        
        Args:
            tone: The tone effects dict
            key: The TONE category (e.g., "empathy")
            delta: The amount to add (-1.0 to +1.0)
            source: Source of this effect (for debugging)
        """
        if key not in tone:
            tone[key] = 0.0
        tone[key] += delta
