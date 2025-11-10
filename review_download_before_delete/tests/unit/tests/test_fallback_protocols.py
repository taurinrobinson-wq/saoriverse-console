#!/usr/bin/env python3
"""
Comprehensive tests for Fallback Protocols system.
"""

import pytest
from emotional_os.safety.fallback_protocols import (
    FallbackProtocol, ToneAnalyzer, GlyphStateManager, GlyphState
)


class TestToneAnalyzer:
    """Test tone ambiguity and misfire detection."""
    
    def setup_method(self):
        self.analyzer = ToneAnalyzer()
    
    def test_ambiguous_tone_detection(self):
        """Test detection of mixed signals (dismissal + voltage)."""
        is_ambiguous, reason, confidence = self.analyzer.detect_ambiguity(
            "I'm fine, but honestly I feel so alone right now"
        )
        assert is_ambiguous is True
        assert "Mixed signals" in reason
        assert confidence > 0.7
    
    def test_consistent_tone_detection(self):
        """Test consistent tone (may have positive energy which is sometimes flagged as dismissal)."""
        is_ambiguous, reason, confidence = self.analyzer.detect_ambiguity(
            "I'm doing okay, having a decent day"
        )
        # This should be consistent - no dismissive markers with voltage
        assert is_ambiguous is False
        assert confidence == 0.0
    
    def test_voltage_keywords_detection(self):
        """Test detection of voltage (emotional pain) keywords."""
        is_ambiguous, reason, confidence = self.analyzer.detect_ambiguity(
            "I'm broken inside, struggling with pain"
        )
        # Without dismissal, should not be ambiguous
        assert is_ambiguous is False
    
    def test_contradiction_across_but(self):
        """Test detection of contradiction across 'but' boundary."""
        is_ambiguous, reason, confidence = self.analyzer.detect_ambiguity(
            "Everything seems perfect, but I feel deeply alone"
        )
        assert is_ambiguous is True
        # Either "Contradiction" or "Mixed signals" indicates ambiguity
        assert "Contradiction" in reason or "Mixed signals" in reason
    
    def test_trigger_misfire_sarcasm(self):
        """Test detection of sarcastic trigger."""
        is_misfire, reason = self.analyzer.detect_misfire(
            "stay",
            "Yeah sure, 'stay' with me because that's worked so well before"
        )
        assert is_misfire is True
        assert "Sarcasm" in reason or "tone mismatch" in reason
    
    def test_trigger_misfire_negation(self):
        """Test detection of explicitly negated trigger."""
        is_misfire, reason = self.analyzer.detect_misfire(
            "go",
            "I don't go anywhere without you"
        )
        assert is_misfire is True
        assert "negated" in reason
    
    def test_trigger_valid(self):
        """Test valid trigger (no misfire)."""
        is_misfire, reason = self.analyzer.detect_misfire(
            "stay",
            "Please stay with me"
        )
        assert is_misfire is False
        assert "valid" in reason


class TestGlyphStateManager:
    """Test glyph state transitions and voice profiles."""
    
    def setup_method(self):
        self.manager = GlyphStateManager()
    
    def test_initial_state(self):
        """Test initial neutral state."""
        assert self.manager.current_state == GlyphState.NEUTRAL
        assert self.manager.last_confirmed_state == GlyphState.NEUTRAL
    
    def test_voice_profile_retrieval(self):
        """Test getting voice profiles for all states."""
        for state in GlyphState:
            if state != GlyphState.NEUTRAL:
                profile = self.manager.get_voice_profile(state)
                assert profile is not None
                assert profile.state == state
                assert profile.tone
                assert profile.cadence
                assert profile.emotional_texture
    
    def test_state_transition(self):
        """Test transitioning to a new state."""
        transition = self.manager.transition_to(GlyphState.TONE_LOCK)
        
        assert transition["previous_state"] == GlyphState.NEUTRAL.value
        assert transition["new_state"] == GlyphState.TONE_LOCK.value
        assert self.manager.current_state == GlyphState.TONE_LOCK
        assert len(self.manager.state_transitions) == 1
    
    def test_multiple_transitions(self):
        """Test multiple state transitions."""
        self.manager.transition_to(GlyphState.TONE_LOCK)
        self.manager.transition_to(GlyphState.VOLTAGE_DETECTED)
        self.manager.transition_to(GlyphState.REPAIR_RECONNECTION)
        
        assert self.manager.current_state == GlyphState.REPAIR_RECONNECTION
        assert len(self.manager.state_transitions) == 3
    
    def test_hold_breath(self):
        """Test entering holding breath state."""
        result = self.manager.hold_breath()
        
        assert result["state"] == "holding_breath"
        assert "started" in result
        assert self.manager.post_trigger_silence_start is not None
    
    def test_exit_holding_breath(self):
        """Test exiting holding breath state."""
        self.manager.hold_breath()
        result = self.manager.exit_holding_breath()
        
        assert result["state"] == "active"
        assert "silence_duration_seconds" in result
        assert self.manager.post_trigger_silence_start is None


class TestFallbackProtocol:
    """Test main fallback protocol orchestration."""
    
    def setup_method(self):
        self.protocol = FallbackProtocol()
    
    def test_ambiguous_tone_exchange(self):
        """Test processing an exchange with ambiguous tone."""
        result = self.protocol.process_exchange(
            user_text="I'm fine, but honestly I feel so alone right now",
            detected_triggers=None,
        )
        
        assert result["detections"]["ambiguity"]["detected"] is True
        assert result["glyph_response"]["state"] == "paused"
        assert "stay" in result["companion_behavior"]["message"].lower() or "silent" in result["companion_behavior"]["message"].lower()
        assert result["decisions"]["should_ask_clarification"] is True
    
    def test_trigger_misfire_exchange(self):
        """Test processing with trigger misfire."""
        result = self.protocol.process_exchange(
            user_text="Yeah sure, 'stay' with me because that's worked so well before",
            detected_triggers=["stay"],
        )
        
        assert len(result["detections"]["misfires"]) > 0
        assert result["decisions"]["should_lock_trigger"] is False
        assert result["glyph_response"]["state"] == "paused"  # Ambiguous state due to sarcasm
    
    def test_valid_trigger_exchange(self):
        """Test processing with valid trigger."""
        result = self.protocol.process_exchange(
            user_text="I need to stay close.",
            detected_triggers=["stay"],
        )
        
        assert len(result["detections"]["misfires"]) == 0
        assert result["glyph_response"]["state"] == "breathing"
        assert result["decisions"]["should_lock_trigger"] is True
        assert result["decisions"]["should_wait"] is True
    
    def test_overlapping_triggers_exchange(self):
        """Test processing with overlapping triggers."""
        result = self.protocol.process_exchange(
            user_text="I'm struggling but I need to heal and move forward",
            detected_triggers=["heal", "move"],
        )
        
        assert result["detections"]["overlapping_triggers"] is True
        assert result["glyph_response"]["state"] == "holding"
    
    def test_no_triggers_exchange(self):
        """Test processing with no triggers detected."""
        result = self.protocol.process_exchange(
            user_text="Just having a regular conversation here.",
            detected_triggers=None,
        )
        
        assert result["glyph_response"]["state"] == "neutral"
        assert len(result["detections"]["misfires"]) == 0
    
    def test_result_structure(self):
        """Test that result has all required fields."""
        result = self.protocol.process_exchange(
            user_text="Hello",
            detected_triggers=None,
        )
        
        assert "user_text" in result
        assert "timestamp" in result
        assert "detections" in result
        assert "glyph_response" in result
        assert "companion_behavior" in result
        assert "decisions" in result
        
        # Check nested structures
        assert "ambiguity" in result["detections"]
        assert "misfires" in result["detections"]
        assert "overlapping_triggers" in result["detections"]
        assert "animation" in result["glyph_response"]
        assert "behavior" in result["companion_behavior"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
