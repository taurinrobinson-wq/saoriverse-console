"""
Unit tests for LimbicAI core modules.
"""

import unittest
from limbic_ai.models import EmotionalFeatures, LimbicState, clamp_01
from limbic_ai.nlp_parser import EmotionalFeatureExtractor
from limbic_ai.mapping import map_features_to_limbic
from limbic_ai.analyzer import LimbicAnalyzer


class TestModels(unittest.TestCase):
    """Test data models."""
    
    def test_emotional_features_creation(self):
        """Test creating EmotionalFeatures."""
        features = EmotionalFeatures(
            social_rejection=0.5,
            threat_to_identity=0.7
        )
        self.assertEqual(features.social_rejection, 0.5)
        self.assertEqual(features.threat_to_identity, 0.7)
    
    def test_emotional_features_validation(self):
        """Test that values must be in [0, 1]."""
        with self.assertRaises(ValueError):
            EmotionalFeatures(social_rejection=1.5)
        
        with self.assertRaises(ValueError):
            EmotionalFeatures(empathy_for_other=-0.1)
    
    def test_limbic_state_creation(self):
        """Test creating LimbicState."""
        state = LimbicState(
            amygdala=0.7,
            insula=0.3
        )
        self.assertEqual(state.amygdala, 0.7)
    
    def test_limbic_state_as_dict(self):
        """Test converting LimbicState to dict."""
        state = LimbicState(amygdala=0.5)
        state_dict = state.as_dict()
        self.assertIn("amygdala", state_dict)
        self.assertEqual(state_dict["amygdala"], 0.5)
    
    def test_clamp_01(self):
        """Test clamping function."""
        self.assertEqual(clamp_01(0.5), 0.5)
        self.assertEqual(clamp_01(-0.1), 0.0)
        self.assertEqual(clamp_01(1.5), 1.0)


class TestNLPParser(unittest.TestCase):
    """Test NLP feature extraction."""
    
    def setUp(self):
        self.extractor = EmotionalFeatureExtractor()
    
    def test_social_rejection_detection(self):
        """Test detecting social rejection keywords."""
        text = "I was rejected and left alone."
        features = self.extractor.extract_features(text)
        self.assertGreater(features.social_rejection, 0.0)
    
    def test_self_blame_detection(self):
        """Test detecting self-blame keywords."""
        text = "It's my fault. I should have known better."
        features = self.extractor.extract_features(text)
        self.assertGreater(features.self_blame, 0.0)
    
    def test_rationalization_detection(self):
        """Test detecting rationalization keywords."""
        text = "It's not a big deal. People get over it."
        features = self.extractor.extract_features(text)
        self.assertGreater(features.rationalization, 0.0)
    
    def test_empathy_detection(self):
        """Test detecting empathy keywords."""
        text = "I understand their pain and care about how they feel."
        features = self.extractor.extract_features(text)
        self.assertGreater(features.empathy_for_other, 0.0)
    
    def test_get_detected_themes(self):
        """Test theme detection."""
        text = "I was rejected. It's my fault."
        themes = self.extractor.get_detected_themes(text)
        self.assertGreater(len(themes["social_rejection"]), 0)
        self.assertGreater(len(themes["self_blame"]), 0)


class TestMapping(unittest.TestCase):
    """Test feature-to-limbic mapping."""
    
    def test_mapping_low_activation(self):
        """Test mapping with low emotional features."""
        features = EmotionalFeatures()  # All zeros
        limbic = map_features_to_limbic(features)
        self.assertEqual(limbic.amygdala, 0.0)
        self.assertEqual(limbic.insula, 0.0)
    
    def test_mapping_high_social_rejection(self):
        """Test that social rejection activates amygdala."""
        features = EmotionalFeatures(social_rejection=1.0)
        limbic = map_features_to_limbic(features)
        self.assertGreater(limbic.amygdala, 0.5)
    
    def test_mapping_empathy_activates_insula(self):
        """Test that empathy activates insula."""
        features = EmotionalFeatures(empathy_for_other=1.0)
        limbic = map_features_to_limbic(features)
        self.assertGreater(limbic.insula, 0.7)
    
    def test_mapping_rationalization_activates_dlpfc(self):
        """Test that rationalization activates dlPFC."""
        features = EmotionalFeatures(rationalization=1.0)
        limbic = map_features_to_limbic(features)
        self.assertEqual(limbic.dlPFC, 1.0)


class TestAnalyzer(unittest.TestCase):
    """Test main analyzer."""
    
    def setUp(self):
        self.analyzer = LimbicAnalyzer()
    
    def test_analyze_valid_scenario(self):
        """Test analyzing a valid scenario."""
        scenario = "I got fired from my job and I'm so upset about it."
        analysis = self.analyzer.analyze(scenario)
        
        self.assertEqual(analysis.scenario, scenario)
        self.assertIsNotNone(analysis.emotional_features)
        self.assertIsNotNone(analysis.limbic_state)
        self.assertIsNotNone(analysis.explanations)
    
    def test_analyze_too_short_raises_error(self):
        """Test that very short scenarios raise error."""
        with self.assertRaises(ValueError):
            self.analyzer.analyze("Hi")
    
    def test_get_summary(self):
        """Test summary generation."""
        scenario = "I broke up with my girlfriend. She was too dramatic."
        analysis = self.analyzer.analyze(scenario)
        summary = self.analyzer.get_summary(analysis)
        
        self.assertIn("##", summary)  # Markdown formatting
        self.assertGreater(len(summary), 50)


if __name__ == '__main__':
    unittest.main()
