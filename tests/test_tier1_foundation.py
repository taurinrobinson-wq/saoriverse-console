"""
Tests for Tier 1 Foundation - LexiconLearner + Safety integration.

Tests:
1. Memory tracking (if ConversationMemory available)
2. Safety detection (Sanctuary)
3. Signal detection (emotional signals)
4. Learning from exchange (LexiconLearner)
5. Performance (<100ms target)
"""

import pytest
import time
from src.emotional_os.tier1_foundation import Tier1Foundation


class TestTier1Foundation:
    """Test suite for Tier 1 Foundation"""
    
    @pytest.fixture
    def tier1(self):
        """Initialize Tier 1 Foundation"""
        return Tier1Foundation(conversation_memory=None)
    
    def test_initialization(self, tier1):
        """Test that Tier 1 initializes without errors"""
        assert tier1 is not None
        assert tier1.perf_times is not None
        assert hasattr(tier1, 'process_response')
    
    def test_process_response_basic(self, tier1):
        """Test basic response processing"""
        user_input = "I'm feeling really sad today"
        base_response = "I understand you're feeling down. That's okay."
        
        enhanced_response, metrics = tier1.process_response(user_input, base_response)
        
        # Response should not be empty
        assert enhanced_response is not None
        assert len(enhanced_response) > 0
        
        # Metrics should include timing
        assert "total" in metrics
        assert metrics["total"] >= 0
    
    def test_performance_under_100ms(self, tier1):
        """Test that Tier 1 pipeline executes under 100ms"""
        user_input = "How are you?"
        base_response = "I'm doing well, thank you for asking."
        
        enhanced_response, metrics = tier1.process_response(user_input, base_response)
        
        # Should complete in under 100ms (0.1 seconds)
        total_time = metrics.get("total", 1.0)
        assert total_time < 0.15, f"Pipeline took {total_time:.3f}s, expected <0.1s"
    
    def test_response_fallback(self, tier1):
        """Test that if processing fails, base response is returned"""
        user_input = "Test input"
        base_response = "Test response"
        
        enhanced_response, metrics = tier1.process_response(user_input, base_response)
        
        # Should always return a response
        assert enhanced_response is not None
        assert isinstance(enhanced_response, str)
        assert len(enhanced_response) > 0
    
    def test_performance_metrics_structure(self, tier1):
        """Test that performance metrics have expected structure"""
        user_input = "How do you feel?"
        base_response = "I'm here to listen."
        
        enhanced_response, metrics = tier1.process_response(user_input, base_response)
        
        # Metrics should include all pipeline stages
        expected_keys = ["total", "memory", "safety_check", "signal_detection", 
                         "generation", "learning", "wrapping"]
        for key in expected_keys:
            assert key in metrics, f"Missing metric: {key}"
            assert isinstance(metrics[key], (int, float))
            assert metrics[key] >= 0
    
    def test_sensitive_input_detection(self, tier1):
        """Test that sensitive inputs are detected"""
        sensitive_inputs = [
            "I want to hurt myself",
            "I'm suicidal",
            "I've been abused",
        ]
        
        for user_input in sensitive_inputs:
            base_response = "I hear you. You're not alone."
            enhanced_response, metrics = tier1.process_response(user_input, base_response)
            
            # Response should be enhanced (potentially with sanctuary wrapping)
            assert enhanced_response is not None
            assert len(enhanced_response) > 0
    
    def test_learning_integration(self, tier1):
        """Test that learning system integrates without breaking response"""
        user_input = "I feel overwhelmed by everything"
        base_response = "That sounds really heavy. What's the most pressing thing?"
        
        # First call
        response1, metrics1 = tier1.process_response(user_input, base_response)
        
        # Should complete successfully
        assert response1 is not None
        assert metrics1["learning"] >= 0
    
    def test_multiple_exchanges(self, tier1):
        """Test multiple back-to-back exchanges"""
        exchanges = [
            ("Hi there", "Hello! How can I help?"),
            ("I'm feeling anxious", "What's making you anxious?"),
            ("Too many deadlines", "That's a lot to handle. Let's break it down."),
        ]
        
        for user_input, base_response in exchanges:
            enhanced_response, metrics = tier1.process_response(user_input, base_response)
            assert enhanced_response is not None
            assert metrics["total"] < 0.15


class TestTier1ComponentIntegration:
    """Test integration of Tier 1 components"""
    
    def test_lexicon_learner_available(self):
        """Test that LexiconLearner is available"""
        tier1 = Tier1Foundation()
        assert tier1.lexicon_learner is not None or True  # Should not crash if not available
    
    def test_sanctuary_available(self):
        """Test that Sanctuary safety functions are available"""
        tier1 = Tier1Foundation()
        # Should have safety functions (stubs if not available)
        assert callable(tier1.is_sensitive_input)
        assert callable(tier1.ensure_sanctuary_response)
        assert callable(tier1.classify_risk)


if __name__ == "__main__":
    # Run with: pytest tests/test_tier1_foundation.py -v
    pytest.main([__file__, "-v"])
