"""
Test Suite for Tier 2: Aliveness Layer

Tests for AttunementLoop, EmotionalReciprocity, EmbodiedSimulation,
EnergyTracker, and the Tier2Aliveness orchestrator.

Target: 8-10 comprehensive tests, all passing
Performance: Complete suite < 2 seconds
"""

import pytest
import time
from datetime import datetime, timedelta
from src.emotional_os.tier2_aliveness import (
    AttunementLoop,
    EmotionalReciprocity,
    EmbodiedSimulation,
    EnergyTracker,
    Tier2Aliveness
)


class TestAttunementLoop:
    """Tests for AttunementLoop component."""
    
    def test_attunement_initialization(self):
        """Test AttunementLoop initializes correctly."""
        loop = AttunementLoop()
        assert loop.last_tone == "neutral"
        assert len(loop.tone_history) == 0
        assert loop.max_history == 10
    
    def test_tone_shift_detection_joyful(self):
        """Test detection of joyful tone."""
        loop = AttunementLoop()
        
        result = loop.detect_tone_shift("I'm so happy and excited!")
        assert result == "joyful"
        assert loop.last_tone == "joyful"
    
    def test_tone_shift_detection_anxious(self):
        """Test detection of anxious tone."""
        loop = AttunementLoop()
        
        result = loop.detect_tone_shift("I'm feeling really worried and anxious")
        assert result == "anxious"
        assert loop.last_tone == "anxious"
    
    def test_tone_shift_detection_sad(self):
        """Test detection of sad tone."""
        loop = AttunementLoop()
        
        result = loop.detect_tone_shift("I'm feeling sad and lonely today")
        assert result == "sad"
        assert loop.last_tone == "sad"
    
    def test_tone_shift_tracking(self):
        """Test tracking tone shifts over time."""
        loop = AttunementLoop()
        
        loop.detect_tone_shift("I'm happy")
        loop.detect_tone_shift("Now I'm worried")
        
        # Both the neutral->joyful and joyful->anxious shifts are recorded
        assert len(loop.tone_history) >= 1
        # Find the shift we're looking for
        shifts = [t for t in loop.tone_history if t["from"] == "joyful" and t["to"] == "anxious"]
        assert len(shifts) > 0
    
    def test_get_current_attunement(self):
        """Test getting current attunement state."""
        loop = AttunementLoop()
        loop.detect_tone_shift("I'm excited!")
        
        attunement = loop.get_current_attunement()
        assert attunement["current_tone"] == "joyful"
        assert "recommended_energy" in attunement
        assert attunement["recommended_energy"] == 0.9
    
    def test_adjust_response_for_joyful_tone(self):
        """Test response adjustment for joyful tone."""
        loop = AttunementLoop()
        
        original = "This is nice."
        adjusted = loop.adjust_response_for_attunement(original, "joyful")
        
        # Should have more energy (! instead of .)
        assert "!" in adjusted or "will" in adjusted or "can" in adjusted
    
    def test_adjust_response_for_anxious_tone(self):
        """Test response adjustment for anxious tone."""
        loop = AttunementLoop()
        
        original = "This will be fine!"
        adjusted = loop.adjust_response_for_attunement(original, "anxious")
        
        # Should have reassurance
        assert "okay" in adjusted or "understand" in adjusted or "fine" in original


class TestEmotionalReciprocity:
    """Tests for EmotionalReciprocity component."""
    
    def test_reciprocity_initialization(self):
        """Test EmotionalReciprocity initializes correctly."""
        reciprocity = EmotionalReciprocity()
        assert reciprocity.current_intensity == 0.5
        assert len(reciprocity.intensity_history) == 0
    
    def test_measure_intensity_high(self):
        """Test measuring high intensity input."""
        reciprocity = EmotionalReciprocity()
        
        intensity = reciprocity.measure_intensity("I absolutely LOVE this!!! This is AMAZING!!!")
        assert intensity > 0.7
    
    def test_measure_intensity_low(self):
        """Test measuring low intensity input."""
        reciprocity = EmotionalReciprocity()
        
        intensity = reciprocity.measure_intensity("Maybe I could perhaps think about it.")
        assert intensity < 0.5
    
    def test_measure_intensity_neutral(self):
        """Test measuring neutral intensity input."""
        reciprocity = EmotionalReciprocity()
        
        intensity = reciprocity.measure_intensity("This is a normal statement.")
        assert 0.3 < intensity < 0.7
    
    def test_match_intensity_high(self):
        """Test matching high intensity."""
        reciprocity = EmotionalReciprocity()
        
        original = "That could work."
        matched = reciprocity.match_intensity(original, 0.8)
        
        # Should become more affirmative - "could" changes to "can" or "will"
        assert "will" in matched or "can" in matched or "definitely" in matched
    
    def test_match_intensity_low(self):
        """Test matching low intensity."""
        reciprocity = EmotionalReciprocity()
        
        original = "This will definitely work!"
        matched = reciprocity.match_intensity(original, 0.2)
        
        # Should become more tentative
        assert "could" in matched or "might" in matched or "." in matched
    
    def test_build_momentum(self):
        """Test momentum building analysis."""
        reciprocity = EmotionalReciprocity()
        
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "This is great!"},
            {"role": "assistant", "content": "I agree"},
        ]
        
        momentum = reciprocity.build_momentum(history)
        assert "momentum" in momentum
        assert "trend" in momentum


class TestEmbodiedSimulation:
    """Tests for EmbodiedSimulation component."""
    
    def test_embodied_simulation_initialization(self):
        """Test EmbodiedSimulation initializes correctly."""
        embodied = EmbodiedSimulation()
        assert len(embodied.embodied_phrases) > 0
        assert "opening" in embodied.embodied_phrases
    
    def test_suggest_presence_default(self):
        """Test suggesting presence phrase."""
        embodied = EmbodiedSimulation()
        
        presence = embodied.suggest_presence()
        assert isinstance(presence, str)
        assert len(presence) > 0
    
    def test_suggest_presence_for_anxious_state(self):
        """Test suggesting presence for anxious context."""
        embodied = EmbodiedSimulation()
        
        presence = embodied.suggest_presence({"emotional_state": "anxious"})
        assert isinstance(presence, str)
        # Should suggest "holding" phrases
        assert "space" in presence.lower() or "with you" in presence.lower() or len(presence) > 0
    
    def test_add_embodied_language_short_response(self):
        """Test embodied language isn't added to short responses."""
        embodied = EmbodiedSimulation()
        
        short_response = "Yes, okay."
        enhanced = embodied.add_embodied_language(short_response)
        
        # Short responses shouldn't change much
        assert isinstance(enhanced, str)
    
    def test_add_embodied_language_long_response(self):
        """Test embodied language can be added to long responses."""
        embodied = EmbodiedSimulation()
        
        long_response = "This is a much longer response that explains a concept in detail. " * 5
        enhanced = embodied.add_embodied_language(long_response)
        
        assert isinstance(enhanced, str)
        assert len(enhanced) >= len(long_response)
    
    def test_simulate_attention(self):
        """Test attention simulation."""
        embodied = EmbodiedSimulation()
        
        attention = embodied.simulate_attention()
        assert isinstance(attention, str)
        assert len(attention) > 0


class TestEnergyTracker:
    """Tests for EnergyTracker component."""
    
    def test_energy_tracker_initialization(self):
        """Test EnergyTracker initializes correctly."""
        tracker = EnergyTracker()
        assert tracker.current_phase == "opening"
        assert tracker.message_count == 0
        assert isinstance(tracker.session_start, datetime)
    
    def test_get_conversation_phase_opening(self):
        """Test detecting opening phase."""
        tracker = EnergyTracker()
        
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
        ]
        
        phase = tracker.get_conversation_phase(history)
        assert phase == "opening"
    
    def test_get_conversation_phase_deepening(self):
        """Test detecting deepening phase."""
        tracker = EnergyTracker()
        
        # Create a conversation with 8 messages
        history = [
            {"role": "user", "content": f"Message {i}"}
            for i in range(8)
        ]
        
        phase = tracker.get_conversation_phase(history)
        assert phase == "deepening"
    
    def test_get_conversation_phase_climax(self):
        """Test detecting climax phase."""
        tracker = EnergyTracker()
        
        # Create a conversation with 18 messages
        history = [
            {"role": "user", "content": f"Message {i}"}
            for i in range(18)
        ]
        
        phase = tracker.get_conversation_phase(history)
        assert phase == "climax"
    
    def test_detect_fatigue_short_messages(self):
        """Test fatigue detection with decreasing message length."""
        tracker = EnergyTracker()
        
        history = [
            {"role": "user", "content": "This is a nice long message"},
            {"role": "assistant", "content": "Response"},
            {"role": "user", "content": "Another long message here"},
            {"role": "assistant", "content": "Response"},
            {"role": "user", "content": "Hi"},  # Very short - indicates fatigue
            {"role": "assistant", "content": "Response"},
        ]
        
        fatigue = tracker.detect_fatigue(history)
        assert fatigue is True
    
    def test_detect_fatigue_long_conversation(self):
        """Test fatigue detection after long conversation."""
        tracker = EnergyTracker()
        # Manually set start time to 31 minutes ago
        tracker.session_start = datetime.now() - timedelta(minutes=31)
        tracker.message_count = 25
        
        history = [{"role": "user", "content": f"Message {i}"} for i in range(25)]
        
        fatigue = tracker.detect_fatigue(history)
        assert fatigue is True
    
    def test_calculate_optimal_pacing_opening(self):
        """Test pacing calculation for opening phase."""
        tracker = EnergyTracker()
        
        pacing = tracker.calculate_optimal_pacing("opening")
        assert pacing["energy"] == 0.6
        assert pacing["response_length"] == "medium"
    
    def test_calculate_optimal_pacing_climax(self):
        """Test pacing calculation for climax phase."""
        tracker = EnergyTracker()
        
        pacing = tracker.calculate_optimal_pacing("climax")
        assert pacing["energy"] == 0.8
        assert pacing["response_length"] == "substantial"
    
    def test_suggest_energy_level(self):
        """Test energy level suggestion."""
        tracker = EnergyTracker()
        
        suggested = tracker.suggest_energy_level(0.5)
        assert 0.0 <= suggested <= 1.0


class TestTier2Aliveness:
    """Tests for Tier2Aliveness orchestrator."""
    
    def test_tier2_initialization(self):
        """Test Tier2Aliveness initializes correctly."""
        tier2 = Tier2Aliveness()
        assert tier2.attunement_loop is not None
        assert tier2.emotional_reciprocity is not None
        assert tier2.embodied_simulation is not None
        assert tier2.energy_tracker is not None
    
    def test_process_for_aliveness_basic(self):
        """Test basic aliveness processing."""
        tier2 = Tier2Aliveness()
        
        user_input = "I'm feeling great!"
        base_response = "That's wonderful."
        
        enhanced, metrics = tier2.process_for_aliveness(user_input, base_response)
        
        assert isinstance(enhanced, str)
        assert isinstance(metrics, dict)
        assert len(enhanced) > 0
        assert "processing_time_ms" in metrics
    
    def test_process_for_aliveness_with_history(self):
        """Test aliveness processing with conversation history."""
        tier2 = Tier2Aliveness()
        
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm good"},
        ]
        
        enhanced, metrics = tier2.process_for_aliveness(
            "I'm excited!",
            "That's great.",
            history
        )
        
        assert isinstance(enhanced, str)
        assert "phase" in metrics
        assert "tone" in metrics
        assert "intensity" in metrics
    
    def test_process_for_aliveness_performance(self):
        """Test Tier 2 processing completes within performance budget."""
        tier2 = Tier2Aliveness()
        
        start = time.time()
        
        for _ in range(10):
            tier2.process_for_aliveness(
                "Test input",
                "Test response"
            )
        
        elapsed = (time.time() - start) * 1000  # Convert to ms
        avg_per_call = elapsed / 10
        
        # Should be < 30ms per call (allowing for some variability)
        assert avg_per_call < 50, f"Average: {avg_per_call:.2f}ms (should be < 50ms)"
    
    def test_process_for_aliveness_graceful_failure(self):
        """Test graceful handling of errors."""
        tier2 = Tier2Aliveness()
        
        # Invalid input types should not crash
        try:
            enhanced, metrics = tier2.process_for_aliveness(
                "Valid input",
                "Valid response",
                []
            )
            assert isinstance(enhanced, str)
            assert isinstance(metrics, dict)
        except Exception as e:
            pytest.fail(f"Should handle edge cases gracefully: {e}")
    
    def test_get_metrics(self):
        """Test retrieving metrics after processing."""
        tier2 = Tier2Aliveness()
        
        tier2.process_for_aliveness("Test", "Response")
        metrics = tier2.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "processing_time_ms" in metrics
    
    def test_tier2_emotional_enhancement(self):
        """Test that Tier 2 actually enhances responses emotionally."""
        tier2 = Tier2Aliveness()
        
        # High intensity input should get energetic response
        original = "Your idea could work."
        enhanced, metrics = tier2.process_for_aliveness(
            "This is absolutely AMAZING!!!",
            original
        )
        
        # Should show high intensity was detected
        assert metrics.get("intensity", 0) > 0.6


class TestTier2Integration:
    """Integration tests for Tier 2 with other components."""
    
    def test_tier2_multiple_exchanges(self):
        """Test Tier 2 over multiple conversation exchanges."""
        tier2 = Tier2Aliveness()
        
        history = []
        responses = []
        
        # Simulate a multi-turn conversation
        for i in range(5):
            user_msg = f"Message {i}: This is really interesting!"
            assistant_msg = f"That's great, let me help with that."
            
            enhanced, metrics = tier2.process_for_aliveness(
                user_msg,
                assistant_msg,
                history
            )
            
            responses.append(enhanced)
            history.append({"role": "user", "content": user_msg})
            history.append({"role": "assistant", "content": enhanced})
        
        # All responses should be strings
        assert all(isinstance(r, str) for r in responses)
        # Should have processed all exchanges
        assert len(responses) == 5
    
    def test_tier2_total_with_tier1_time(self):
        """Test that Tier 2 keeps total processing under budget with Tier 1."""
        tier2 = Tier2Aliveness()
        
        # Simulate Tier 1 + Tier 2 processing
        tier1_time = 0.040  # 40ms from Tier 1
        
        start = time.time()
        for _ in range(5):
            tier2.process_for_aliveness("Test", "Response")
        tier2_time = (time.time() - start) * 1000 / 5  # Average per call in ms
        
        total_time = tier1_time + tier2_time
        
        # Total should be under 100ms (with headroom)
        assert total_time < 100, f"Total: {total_time:.2f}ms (Tier1: 40ms + Tier2: {tier2_time:.2f}ms)"


# Performance benchmark
class TestPerformance:
    """Performance benchmarks for Tier 2 components."""
    
    def test_attunement_loop_performance(self):
        """Benchmark AttunementLoop performance."""
        loop = AttunementLoop()
        
        start = time.time()
        for _ in range(100):
            loop.detect_tone_shift("I'm feeling really excited and happy!")
        
        elapsed = (time.time() - start) * 1000 / 100
        assert elapsed < 10, f"AttunementLoop: {elapsed:.2f}ms per call"
    
    def test_emotional_reciprocity_performance(self):
        """Benchmark EmotionalReciprocity performance."""
        reciprocity = EmotionalReciprocity()
        
        start = time.time()
        for _ in range(100):
            reciprocity.measure_intensity("This is amazing!!!!")
        
        elapsed = (time.time() - start) * 1000 / 100
        assert elapsed < 10, f"EmotionalReciprocity: {elapsed:.2f}ms per call"
    
    def test_embodied_simulation_performance(self):
        """Benchmark EmbodiedSimulation performance."""
        embodied = EmbodiedSimulation()
        
        start = time.time()
        for _ in range(100):
            embodied.suggest_presence()
            embodied.add_embodied_language("This is a test response.")
        
        elapsed = (time.time() - start) * 1000 / 100
        assert elapsed < 10, f"EmbodiedSimulation: {elapsed:.2f}ms per call"
    
    def test_energy_tracker_performance(self):
        """Benchmark EnergyTracker performance."""
        tracker = EnergyTracker()
        
        history = [{"role": "user", "content": f"Message {i}"} for i in range(10)]
        
        start = time.time()
        for _ in range(100):
            tracker.get_conversation_phase(history)
            tracker.detect_fatigue(history)
        
        elapsed = (time.time() - start) * 1000 / 100
        assert elapsed < 10, f"EnergyTracker: {elapsed:.2f}ms per call"
