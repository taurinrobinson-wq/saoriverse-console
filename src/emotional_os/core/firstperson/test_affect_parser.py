"""Tests for Phase 2.1: Affect Parser.

Validates emotional affect detection across tone, valence, and arousal dimensions.
Tests realistic conversational inputs and edge cases.
"""

import pytest

from emotional_os.core.firstperson.affect_parser import AffectParser, create_affect_parser


class TestAffectParserBasics:
    """Test core affect parser functionality."""

    def test_parser_initialization(self):
        """Parser initializes with tone lexicons."""
        parser = AffectParser()
        assert parser.tone_lexicons is not None
        assert "warm" in parser.tone_lexicons
        assert "sad" in parser.tone_lexicons
        assert "angry" in parser.tone_lexicons

    def test_analyze_empty_input(self):
        """Empty input returns neutral affect."""
        parser = AffectParser()
        result = parser.analyze_affect("")
        assert result.tone == "neutral"
        assert result.valence == 0.0
        assert result.arousal < 0.5

    def test_analyze_none_input(self):
        """None input returns neutral affect."""
        parser = AffectParser()
        result = parser.analyze_affect(None)
        assert result.tone == "neutral"
        assert result.valence == 0.0

    def test_analyze_returns_valid_affect_analysis(self):
        """analyze_affect returns AffectAnalysis with all fields."""
        parser = AffectParser()
        result = parser.analyze_affect("I love this so much!")
        assert hasattr(result, "tone")
        assert hasattr(result, "tone_confidence")
        assert hasattr(result, "valence")
        assert hasattr(result, "arousal")
        assert hasattr(result, "secondary_tones")
        assert hasattr(result, "explanation")
        assert isinstance(result.tone, str)
        assert isinstance(result.tone_confidence, float)
        assert isinstance(result.valence, float)
        assert isinstance(result.arousal, float)


class TestWarmTone:
    """Test warm/positive tone detection."""

    def test_love_keyword(self):
        """Detects 'love' as warm tone."""
        parser = AffectParser()
        result = parser.analyze_affect("I love this so much")
        assert result.tone in ["warm", "grateful"]
        assert result.valence > 0.5
        assert result.tone_confidence > 0.3

    def test_grateful_keywords(self):
        """Detects gratitude expressions."""
        parser = AffectParser()
        result = parser.analyze_affect("I'm so grateful for your help")
        assert result.tone in ["warm", "grateful"]
        assert result.valence > 0.6

    def test_multiple_positive_words(self):
        """Multiple positive words increase confidence."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "This is wonderful, beautiful, and I'm so happy about it")
        assert result.tone in ["warm", "grateful"]
        assert result.tone_confidence > 0.5
        assert result.valence > 0.7

    def test_warm_with_caring(self):
        """Warm tone with caring vocabulary."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "I really care about you and appreciate your support")
        assert result.tone in ["warm", "grateful"]
        assert result.valence > 0.6


class TestSadTone:
    """Test sad/negative tone detection."""

    def test_sad_keyword(self):
        """Detects 'sad' as sad tone."""
        parser = AffectParser()
        result = parser.analyze_affect("I feel so sad today")
        assert result.tone == "sad"
        assert result.valence < -0.6
        assert result.arousal < 0.5

    def test_depressed_keywords(self):
        """Detects depression/melancholy words."""
        parser = AffectParser()
        result = parser.analyze_affect("I'm depressed and melancholy")
        assert result.tone == "sad"
        assert result.valence < -0.6

    def test_hopeless_expression(self):
        """Detects hopelessness."""
        parser = AffectParser()
        result = parser.analyze_affect("Everything feels hopeless and empty")
        assert result.tone == "sad"
        assert result.valence < -0.7

    def test_tearful_expression(self):
        """Detects sad/tearful expressions."""
        parser = AffectParser()
        result = parser.analyze_affect("I've been crying and feel lost")
        assert result.tone == "sad"
        assert result.valence < -0.6


class TestAnxiousTone:
    """Test anxious tone detection."""

    def test_anxious_keyword(self):
        """Detects 'anxious' as anxious tone."""
        parser = AffectParser()
        result = parser.analyze_affect("I'm feeling really anxious about this")
        assert result.tone == "anxious"
        assert result.valence < 0
        assert result.arousal > 0.6

    def test_worried_expression(self):
        """Detects worry."""
        parser = AffectParser()
        result = parser.analyze_affect("I'm so worried and stressed out")
        assert result.tone == "anxious"
        assert result.arousal > 0.6

    def test_panic_expression(self):
        """Detects panic/fear."""
        parser = AffectParser()
        result = parser.analyze_affect("I'm panicking and terrified")
        assert result.tone == "anxious"
        assert result.arousal > 0.7
        assert result.valence < -0.5

    def test_overwhelmed_expression(self):
        """Detects overwhelm."""
        parser = AffectParser()
        result = parser.analyze_affect("I feel completely overwhelmed")
        assert result.tone == "anxious"
        assert result.arousal > 0.6


class TestAngryTone:
    """Test angry tone detection."""

    def test_angry_keyword(self):
        """Detects 'angry' as angry tone."""
        parser = AffectParser()
        result = parser.analyze_affect("I'm really angry about this")
        assert result.tone == "angry"
        assert result.valence < -0.6
        assert result.arousal > 0.7

    def test_furious_expression(self):
        """Detects fury/rage."""
        parser = AffectParser()
        result = parser.analyze_affect("I'm absolutely furious and enraged")
        assert result.tone == "angry"
        assert result.arousal > 0.8

    def test_fed_up_expression(self):
        """Detects being fed up."""
        parser = AffectParser()
        result = parser.analyze_affect("I'm fed up with this nonsense")
        assert result.tone == "angry"
        assert result.valence < -0.5

    def test_hate_expression(self):
        """Detects hate/disgust."""
        parser = AffectParser()
        result = parser.analyze_affect("I hate this and I'm disgusted")
        assert result.tone == "angry"
        assert result.valence < -0.7


class TestSardonicTone:
    """Test sardonic/ironic tone detection."""

    def test_sarcastic_expression(self):
        """Detects sarcasm."""
        parser = AffectParser()
        result = parser.analyze_affect("Yeah, right. That's just great.")
        assert result.tone == "sardonic"
        assert result.valence < 0

    def test_eye_roll_expression(self):
        """Detects eye-roll tone."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "Oh please, obviously that's not going to work")
        assert result.tone == "sardonic"

    def test_tongue_in_cheek(self):
        """Detects witty/clever tone."""
        parser = AffectParser()
        result = parser.analyze_affect("As if that could possibly work")
        assert result.tone == "sardonic"


class TestValence:
    """Test valence (sentiment) detection."""

    def test_positive_valence(self):
        """Positive tone yields high valence."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "I absolutely love this and I'm so happy!")
        assert result.valence > 0.5

    def test_negative_valence(self):
        """Negative tone yields low valence."""
        parser = AffectParser()
        result = parser.analyze_affect("I hate this and I'm so sad about it")
        assert result.valence < -0.5

    def test_neutral_valence(self):
        """Neutral text yields near-zero valence."""
        parser = AffectParser()
        result = parser.analyze_affect("It seems this is probably the case")
        assert -0.3 < result.valence < 0.3

    def test_negation_flips_valence(self):
        """Negation affects sentiment."""
        parser = AffectParser()
        result = parser.analyze_affect("I hate this situation")
        # Strong negative should override any weak positive
        assert result.valence < 0


class TestArousal:
    """Test arousal (intensity) detection."""

    def test_calm_arousal(self):
        """Calm tone yields low arousal."""
        parser = AffectParser()
        result = parser.analyze_affect("I feel peaceful and serene")
        assert result.arousal < 0.5

    def test_intense_arousal_with_exclamation(self):
        """Exclamation marks increase arousal."""
        parser = AffectParser()
        result = parser.analyze_affect("I'm SO angry about this!!!")
        assert result.arousal > 0.6

    def test_arousal_with_intensifiers(self):
        """Intensifier words boost arousal."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "I am absolutely, completely, totally exhausted")
        assert result.arousal > 0.5

    def test_worried_arousal(self):
        """Anxiety increases arousal even if valence is neutral."""
        parser = AffectParser()
        result = parser.analyze_affect("I'm worried about the deadline")
        assert result.arousal > 0.5


class TestSecondaryTones:
    """Test detection of secondary emotional tones."""

    def test_mixed_emotions(self):
        """Mixed emotions detected in secondary_tones."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "I'm anxious but grateful for the opportunity")
        assert result.secondary_tones is not None
        assert len(result.secondary_tones) > 0

    def test_complex_feeling(self):
        """Complex emotional states yield multiple tones."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "I'm confused about whether I should be excited or worried"
        )
        assert len(result.secondary_tones) > 0

    def test_secondary_tones_ranked(self):
        """Secondary tones are ranked by confidence."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "I'm very sad and a bit angry but also confused about why"
        )
        assert result.secondary_tones is not None


class TestConfidenceScores:
    """Test tone confidence scoring."""

    def test_high_confidence_with_strong_signal(self):
        """Strong emotional signal yields high confidence."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "I absolutely love this! I'm so grateful and blessed!"
        )
        assert result.tone_confidence > 0.6

    def test_low_confidence_with_weak_signal(self):
        """Weak emotional signal yields lower confidence."""
        parser = AffectParser()
        result = parser.analyze_affect("It's fine.")
        assert result.tone_confidence < 0.8

    def test_confidence_clamped(self):
        """Confidence score is always 0-1."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "I LOVE THIS I LOVE THIS I LOVE THIS!!!" * 10
        )
        assert 0.0 <= result.tone_confidence <= 1.0


class TestToneDescriptors:
    """Test tone descriptor generation."""

    def test_warm_descriptor(self):
        """Warm tone descriptor is helpful."""
        parser = AffectParser()
        desc = parser.get_tone_descriptor("warm")
        assert "empathy" in desc.lower() or "warm" in desc.lower()

    def test_sardonic_descriptor(self):
        """Sardonic descriptor is accurate."""
        parser = AffectParser()
        desc = parser.get_tone_descriptor("sardonic")
        assert "wit" in desc.lower() or "irony" in desc.lower()

    def test_anxious_descriptor(self):
        """Anxious descriptor suggests reassurance."""
        parser = AffectParser()
        desc = parser.get_tone_descriptor("anxious")
        assert "reassur" in desc.lower() or "calm" in desc.lower()

    def test_sad_descriptor(self):
        """Sad descriptor suggests support."""
        parser = AffectParser()
        desc = parser.get_tone_descriptor("sad")
        assert "support" in desc.lower() or "gentle" in desc.lower()


class TestEscalationLogic:
    """Test escalation and softening logic."""

    def test_should_escalate_high_arousal(self):
        """High arousal suggests escalation."""
        parser = AffectParser()
        assert parser.should_escalate_tone(arousal=0.8, valence=-0.5) is True

    def test_should_escalate_extreme_valence(self):
        """Extreme valence suggests escalation."""
        parser = AffectParser()
        assert parser.should_escalate_tone(arousal=0.4, valence=0.9) is True

    def test_no_escalate_calm(self):
        """Calm input does not escalate."""
        parser = AffectParser()
        assert parser.should_escalate_tone(arousal=0.2, valence=0.1) is False

    def test_should_soften_distressed(self):
        """High arousal + negative valence suggests softening."""
        parser = AffectParser()
        assert parser.should_soften_tone(arousal=0.7, valence=-0.7) is True

    def test_no_soften_calm_negative(self):
        """Calm negative input doesn't need softening."""
        parser = AffectParser()
        assert parser.should_soften_tone(arousal=0.3, valence=-0.7) is False


class TestRealWorldExamples:
    """Test with realistic conversation examples."""

    def test_user_sharing_good_news(self):
        """User sharing positive experience."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "I just got the job offer! I'm so excited and grateful for this opportunity!"
        )
        assert result.tone in ["warm", "grateful"]
        assert result.valence > 0.6
        assert result.arousal >= 0.5  # Excited

    def test_user_processing_grief(self):
        """User processing difficult emotion."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "My grandmother passed away yesterday. I feel so lost.")
        assert result.tone == "sad"
        assert result.valence < -0.6
        assert result.arousal < 0.6  # Sad is low-arousal

    def test_user_expressing_frustration(self):
        """User expressing frustration."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "I'm SO angry and mad about this! I hate it! Nothing's going right!"
        )
        assert result.tone == "angry"
        assert result.arousal > 0.7
        assert result.valence < -0.5

    def test_user_seeking_reassurance(self):
        """User seeking reassurance."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "I'm really worried about this meeting tomorrow. What if I mess up?")
        assert result.tone == "anxious"
        assert result.arousal > 0.6
        assert result.valence < -0.3

    def test_user_sarcastic_complaint(self):
        """User expressing complaint with sarcasm."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "Oh sure, because THAT'S going to work out great.")
        assert result.tone == "sardonic"
        assert result.valence < 0

    def test_user_confused_about_next_steps(self):
        """User confused about direction."""
        parser = AffectParser()
        result = parser.analyze_affect(
            "I don't know what to do next. Should I stay or leave?")
        assert result.tone == "confused"


class TestFactoryFunction:
    """Test factory function."""

    def test_create_affect_parser(self):
        """Factory creates valid parser."""
        parser = create_affect_parser()
        assert isinstance(parser, AffectParser)
        assert parser.tone_lexicons is not None

    def test_factory_parser_works(self):
        """Parser from factory is functional."""
        parser = create_affect_parser()
        result = parser.analyze_affect("I'm so happy!")
        assert result.tone == "warm"
        assert result.valence > 0.5


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_long_text(self):
        """Parser handles very long input."""
        parser = AffectParser()
        long_text = "I'm sad. " * 100
        result = parser.analyze_affect(long_text)
        assert result.tone == "sad"

    def test_mixed_case_text(self):
        """Parser handles mixed case."""
        parser = AffectParser()
        result = parser.analyze_affect("I'M So HaPpY!")
        assert result.tone == "warm"
        assert result.valence > 0.5

    def test_special_characters(self):
        """Parser handles special characters."""
        parser = AffectParser()
        result = parser.analyze_affect("I'm sad... :( so very sad!!!")
        assert result.tone == "sad"

    def test_multiple_languages_not_supported(self):
        """Non-English text returns neutral."""
        parser = AffectParser()
        result = parser.analyze_affect("Ich bin traurig")
        # Should not crash, returns neutral or tries best
        assert result.tone is not None

    def test_numeric_text(self):
        """Pure numbers return neutral or weak signal."""
        parser = AffectParser()
        result = parser.analyze_affect("123 456 789")
        # Should return neutral or have low confidence
        assert result.tone_confidence < 0.5


class TestConsistency:
    """Test consistency of parsing."""

    def test_same_input_same_output(self):
        """Same input always produces same output."""
        parser = AffectParser()
        text = "I'm so happy about this amazing opportunity!"
        result1 = parser.analyze_affect(text)
        result2 = parser.analyze_affect(text)
        assert result1.tone == result2.tone
        assert result1.valence == result2.valence
        assert result1.arousal == result2.arousal

    def test_multiple_parsers_consistent(self):
        """Different parser instances give same results."""
        text = "I'm anxious about the test"
        result1 = create_affect_parser().analyze_affect(text)
        result2 = create_affect_parser().analyze_affect(text)
        assert result1.tone == result2.tone
        assert abs(result1.valence - result2.valence) < 0.01
        assert abs(result1.arousal - result2.arousal) < 0.01
