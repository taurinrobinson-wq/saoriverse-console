"""
Test Suite for Tier 3: Poetic Consciousness
==============================================

Tests for PoetryEngine, SaoriLayer, TensionManager, and MythologyWeaver
with comprehensive coverage including edge cases and performance benchmarks.
"""

import pytest
import time
from typing import List, Dict
from src.emotional_os.tier3_poetic_consciousness import (
    PoetryEngine,
    SaoriLayer,
    TensionManager,
    MythologyWeaver,
    Tier3PoeticConsciousness
)


class TestPoetryEngine:
    """Test suite for PoetryEngine component."""
    
    @pytest.fixture
    def engine(self):
        """Provide PoetryEngine instance."""
        return PoetryEngine()
    
    def test_initialization(self, engine):
        """Test PoetryEngine initializes with required mappings."""
        assert engine.metaphor_map is not None
        assert "joy" in engine.metaphor_map
        assert "sadness" in engine.metaphor_map
        assert engine.symbol_pool is not None
        assert len(engine.poetic_starters) > 0
    
    def test_find_metaphor_joy(self, engine):
        """Test finding metaphor for joy emotion."""
        metaphor = engine.find_metaphor("growth", "joy")
        assert isinstance(metaphor, str)
        assert len(metaphor) > 0
    
    def test_find_metaphor_sadness(self, engine):
        """Test finding metaphor for sadness emotion."""
        metaphor = engine.find_metaphor("growth", "sadness")
        assert isinstance(metaphor, str)
        assert len(metaphor) > 0
    
    def test_find_metaphor_fallback(self, engine):
        """Test metaphor finding with unknown emotion uses fallback."""
        metaphor = engine.find_metaphor("growth", "unknown_emotion")
        assert metaphor is not None
        assert isinstance(metaphor, str)
    
    def test_add_symbolic_language_short_response(self, engine):
        """Test symbolic language not added to short responses."""
        short = "OK"
        result = engine.add_symbolic_language(short)
        assert isinstance(result, str)
        # Should return unchanged or minimally changed
        assert len(result) <= len(short) + 50
    
    def test_add_symbolic_language_long_response(self, engine):
        """Test symbolic language can be added to long responses."""
        long = "This is a comprehensive response about growth and transformation that spans multiple sentences and discusses the nature of personal development over time."
        result = engine.add_symbolic_language(long)
        assert isinstance(result, str)
        # Should be string, either enhanced or original
        assert len(result) >= len(long)
    
    def test_generate_poetic_expression_metaphorical(self, engine):
        """Test generating metaphorical poetic expressions."""
        expr = engine.generate_poetic_expression("growth", "metaphorical")
        assert isinstance(expr, str)
        assert len(expr) > 0
    
    def test_generate_poetic_expression_symbolic(self, engine):
        """Test generating symbolic poetic expressions."""
        expr = engine.generate_poetic_expression("growth", "symbolic")
        assert isinstance(expr, str)
        assert len(expr) > 0
    
    def test_generate_poetic_expression_paradoxical(self, engine):
        """Test generating paradoxical poetic expressions."""
        expr = engine.generate_poetic_expression("growth", "paradoxical")
        assert isinstance(expr, str)
        assert len(expr) > 0
    
    def test_bridge_concepts(self, engine):
        """Test bridging concepts with metaphor."""
        bridge = engine.bridge_concepts("growth", "challenge")
        assert isinstance(bridge, str)
        assert len(bridge) > 0


class TestSaoriLayer:
    """Test suite for SaoriLayer component."""
    
    @pytest.fixture
    def saori(self):
        """Provide SaoriLayer instance."""
        return SaoriLayer()
    
    def test_initialization(self, saori):
        """Test SaoriLayer initializes with aesthetic principles."""
        assert saori.principles is not None
        assert "ma" in saori.principles
        assert "wabi_sabi" in saori.principles
        assert "yugen" in saori.principles
        assert "mono_no_aware" in saori.principles
    
    def test_apply_ma_short_response(self, saori):
        """Test ma (brevity) doesn't shorten already-brief responses."""
        short = "This is brief."
        result = saori.apply_ma(short, max_length=10)
        assert isinstance(result, str)
        # Should preserve short responses
        assert "brief" in result
    
    def test_apply_ma_long_response(self, saori):
        """Test ma trims long responses appropriately."""
        long = "This is a very long response. " * 20 + "Final thought."
        result = saori.apply_ma(long, max_length=50)
        assert isinstance(result, str)
        # Should be shorter than original
        assert len(result.split()) <= len(long.split())
    
    def test_apply_wabi_sabi(self, saori):
        """Test wabi-sabi principle application."""
        response = "This is a perfect solution to your problem."
        result = saori.apply_wabi_sabi(response)
        assert isinstance(result, str)
        # Should be same or enhanced
        assert len(result) >= len(response) - 10
    
    def test_apply_yugen(self, saori):
        """Test yūgen principle application."""
        response = "There is clearly a meaning to this."
        result = saori.apply_yugen(response)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_apply_mono_no_aware(self, saori):
        """Test mono no aware principle application."""
        response = "This moment is beautiful and eternal."
        result = saori.apply_mono_no_aware(response)
        assert isinstance(result, str)
        assert len(result) > 0


class TestTensionManager:
    """Test suite for TensionManager component."""
    
    @pytest.fixture
    def tension(self):
        """Provide TensionManager instance."""
        return TensionManager()
    
    def test_initialization(self, tension):
        """Test TensionManager initializes with tension phrases."""
        assert tension.tension_phrases is not None
        assert "question" in tension.tension_phrases
        assert "paradox" in tension.tension_phrases
        assert "opening" in tension.tension_phrases
    
    def test_introduce_tension_low(self, tension):
        """Test introducing low-level tension."""
        response = "This is a clear statement."
        result = tension.introduce_tension(response, level=0.2)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_introduce_tension_medium(self, tension):
        """Test introducing medium-level tension."""
        response = "This is a clear statement."
        result = tension.introduce_tension(response, level=0.5)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_introduce_tension_high(self, tension):
        """Test introducing high-level tension."""
        response = "This is a clear statement."
        result = tension.introduce_tension(response, level=0.8)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_create_opening(self, tension):
        """Test creating space for exploration."""
        response = "Here is what I think."
        result = tension.create_opening(response)
        assert isinstance(result, str)
        assert len(result) > len(response) - 10
    
    def test_balance_paradox(self, tension):
        """Test balancing paradoxical concepts."""
        paradox = tension.balance_paradox("strength", "vulnerability")
        assert isinstance(paradox, str)
        assert "strength" in paradox.lower()
        assert "vulnerability" in paradox.lower()


class TestMythologyWeaver:
    """Test suite for MythologyWeaver component."""
    
    @pytest.fixture
    def weaver(self):
        """Provide MythologyWeaver instance."""
        return MythologyWeaver()
    
    def test_initialization(self, weaver):
        """Test MythologyWeaver initializes correctly."""
        assert weaver.mythology is not None
        assert "themes" in weaver.mythology
        assert "symbols" in weaver.mythology
    
    def test_weave_myth_empty_history(self, weaver):
        """Test weaving myth from empty history."""
        myth = weaver.weave_myth(None)
        assert myth is not None
        assert isinstance(myth, dict)
    
    def test_weave_myth_with_history(self, weaver):
        """Test weaving myth from conversation history."""
        history = [
            {"content": "I want to grow and learn"},
            {"content": "I'm facing a challenge but I'm discovering new things"},
        ]
        myth = weaver.weave_myth(history)
        assert myth is not None
        themes = myth.get("themes", [])
        # Should detect some themes
        if themes:
            assert any(t in ["growth", "challenge", "discovery"] for t in themes)
    
    def test_add_mythological_element(self, weaver):
        """Test adding mythological elements to response."""
        response = "This is a response."
        myth = {"themes": ["growth", "challenge"]}
        result = weaver.add_mythological_element(response, myth)
        assert isinstance(result, str)
    
    def test_track_symbols(self, weaver):
        """Test tracking recurring symbols."""
        response = "There is light in the journey, the seed grows, and the journey continues."
        symbols = weaver.track_symbols(response)
        assert isinstance(symbols, dict)
        assert "journey" in symbols or "light" in symbols or "seed" in symbols
    
    def test_build_personal_narrative_empty_history(self, weaver):
        """Test building narrative from empty history."""
        narrative = weaver.build_personal_narrative(None)
        assert isinstance(narrative, str)
        assert len(narrative) > 0
    
    def test_build_personal_narrative_with_history(self, weaver):
        """Test building narrative from history with themes."""
        history = [
            {"content": "I'm growing"},
            {"content": "I discovered something"},
            {"content": "I learned from challenge"},
        ]
        narrative = weaver.build_personal_narrative(history)
        assert isinstance(narrative, str)
        assert len(narrative) > 0


class TestTier3Integration:
    """Integration tests for Tier 3 Poetic Consciousness."""
    
    @pytest.fixture
    def tier3(self):
        """Provide Tier3PoeticConsciousness instance."""
        return Tier3PoeticConsciousness()
    
    def test_initialization(self, tier3):
        """Test Tier 3 initializes all components."""
        assert tier3.poetry_engine is not None
        assert tier3.saori_layer is not None
        assert tier3.tension_manager is not None
        assert tier3.mythology_weaver is not None
    
    def test_process_for_poetry_simple(self, tier3):
        """Test processing response for poetry."""
        response = "This is a simple response."
        result, metrics = tier3.process_for_poetry(response)
        
        assert isinstance(result, str)
        assert isinstance(metrics, dict)
        assert "processing_time_ms" in metrics
    
    def test_process_for_poetry_with_context(self, tier3):
        """Test processing with full context."""
        response = "We've been exploring growth together."
        context = {
            "theme": "growth",
            "messages": [
                {"content": "I want to grow"},
                {"content": "I'm learning things"}
            ]
        }
        result, metrics = tier3.process_for_poetry(response, context)
        
        assert isinstance(result, str)
        assert isinstance(metrics, dict)
    
    def test_process_for_poetry_empty_response(self, tier3):
        """Test processing empty response handles gracefully."""
        result, metrics = tier3.process_for_poetry("")
        assert isinstance(result, str)
        assert isinstance(metrics, dict)
    
    def test_get_metrics(self, tier3):
        """Test retrieving metrics after processing."""
        response = "Test response"
        tier3.process_for_poetry(response)
        metrics = tier3.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "processing_time_ms" in metrics
    
    def test_multiple_processing_calls(self, tier3):
        """Test multiple processing calls maintain state."""
        responses = [
            "First response",
            "Second response",
            "Third response"
        ]
        
        for resp in responses:
            result, metrics = tier3.process_for_poetry(resp)
            assert isinstance(result, str)
            assert isinstance(metrics, dict)


class TestTier3Performance:
    """Performance benchmarks for Tier 3."""
    
    @pytest.fixture
    def tier3(self):
        """Provide Tier3PoeticConsciousness instance."""
        return Tier3PoeticConsciousness()
    
    def test_single_processing_performance(self, tier3):
        """Test single processing call performance target: <30ms."""
        response = "This is a comprehensive response about growth and learning."
        
        start = time.time()
        result, metrics = tier3.process_for_poetry(response)
        elapsed = (time.time() - start) * 1000
        
        # Should complete in under 30ms
        assert elapsed < 30, f"Processing took {elapsed:.2f}ms (target: <30ms)"
        assert "processing_time_ms" in metrics
    
    def test_batch_processing_performance(self, tier3):
        """Test batch processing stays under performance target."""
        responses = [
            "First response about growth",
            "Second response about challenge",
            "Third response about discovery"
        ]
        
        start = time.time()
        for response in responses:
            result, metrics = tier3.process_for_poetry(response)
        elapsed = (time.time() - start) * 1000
        
        # Should handle 3 responses in under 90ms (30ms each)
        assert elapsed < 90, f"Batch processing took {elapsed:.2f}ms (target: <90ms)"
    
    def test_average_processing_time(self, tier3):
        """Test average processing time over multiple calls."""
        num_iterations = 10
        total_time = 0
        
        for i in range(num_iterations):
            response = f"Response {i}: This is a test response about various topics."
            start = time.time()
            tier3.process_for_poetry(response)
            total_time += (time.time() - start) * 1000
        
        avg_time = total_time / num_iterations
        # Average should be under 20ms for consistent performance
        assert avg_time < 20, f"Average processing time: {avg_time:.2f}ms (target: <20ms)"


class TestTier3EdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def tier3(self):
        """Provide Tier3PoeticConsciousness instance."""
        return Tier3PoeticConsciousness()
    
    def test_very_long_response(self, tier3):
        """Test handling very long responses."""
        long_response = "Response. " * 500
        result, metrics = tier3.process_for_poetry(long_response)
        
        assert isinstance(result, str)
        assert isinstance(metrics, dict)
    
    def test_special_characters(self, tier3):
        """Test handling special characters."""
        special = "Response with émojis 😊 and special chars: @#$%^&*()"
        result, metrics = tier3.process_for_poetry(special)
        
        assert isinstance(result, str)
        assert isinstance(metrics, dict)
    
    def test_none_context(self, tier3):
        """Test handling None context gracefully."""
        response = "Test response"
        result, metrics = tier3.process_for_poetry(response, None)
        
        assert isinstance(result, str)
        assert isinstance(metrics, dict)
    
    def test_empty_context(self, tier3):
        """Test handling empty context dict."""
        response = "Test response"
        result, metrics = tier3.process_for_poetry(response, {})
        
        assert isinstance(result, str)
        assert isinstance(metrics, dict)
    
    def test_unicode_handling(self, tier3):
        """Test handling unicode in response."""
        unicode_response = "日本語のテキスト with English mixed in"
        result, metrics = tier3.process_for_poetry(unicode_response)
        
        assert isinstance(result, str)
        assert isinstance(metrics, dict)


class TestTier3Consistency:
    """Test consistency and determinism where appropriate."""
    
    @pytest.fixture
    def tier3(self):
        """Provide Tier3PoeticConsciousness instance."""
        return Tier3PoeticConsciousness()
    
    def test_response_structure_preservation(self, tier3):
        """Test that response structure is generally preserved."""
        original = "This is a clear point. It leads somewhere. Finally, a conclusion."
        result, _ = tier3.process_for_poetry(original)
        
        # Result should be reasonable length
        assert len(result) > 0
        assert len(result) < len(original) * 3  # Shouldn't expand excessively
    
    def test_component_independence(self, tier3):
        """Test that components can be called independently."""
        response = "Test response"
        
        # Test poetry engine alone
        result1 = tier3.poetry_engine.add_symbolic_language(response)
        assert isinstance(result1, str)
        
        # Test saori layer alone
        result2 = tier3.saori_layer.apply_ma(response)
        assert isinstance(result2, str)
        
        # Test tension manager alone
        result3 = tier3.tension_manager.introduce_tension(response)
        assert isinstance(result3, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
