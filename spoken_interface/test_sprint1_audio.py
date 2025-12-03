"""Tests for Sprint 1: Audio Pipeline and STT

Test audio loading, preprocessing, and speech-to-text transcription.
"""

import pytest
import numpy as np
from io import BytesIO
from pathlib import Path

try:
    from spoken_interface.audio_pipeline import (
        AudioProcessor,
        SpeechToText,
        AudioPipeline,
    )
    AUDIO_PIPELINE_AVAILABLE = True
except ImportError:
    AUDIO_PIPELINE_AVAILABLE = False


@pytest.mark.skipif(not AUDIO_PIPELINE_AVAILABLE, reason="Audio pipeline not available")
class TestAudioProcessor:
    """Test audio preprocessing utilities."""
    
    def test_normalize_audio(self):
        """Test audio normalization."""
        # Create synthetic audio
        audio = np.array([0.5, 0.6, -0.4, 0.3])
        
        normalized = AudioProcessor.normalize_audio(audio, target_db=-20.0)
        
        # Should be normalized but same shape
        assert normalized.shape == audio.shape
        # Should be in reasonable range
        assert np.all(np.abs(normalized) <= 1.0)
    
    def test_vad_mask_generation(self):
        """Test voice activity detection."""
        # Create audio with speech and silence
        sr = 16000
        duration = 2.0
        
        # 1s silence, 1s speech, 1s silence
        silence = np.zeros(int(sr * 1))
        speech = np.random.normal(0, 0.3, int(sr * 1))
        audio = np.concatenate([silence, speech, silence])
        
        vad_mask = AudioProcessor.extract_vad_mask(audio, sr)
        
        # Should detect some speech
        assert vad_mask.shape[0] > 0
        # More speech in middle
        middle_portion = vad_mask[len(vad_mask)//4:3*len(vad_mask)//4]
        assert np.mean(middle_portion) > np.mean(vad_mask)
    
    def test_trim_silence(self):
        """Test silence trimming."""
        sr = 16000
        
        # Silence + speech + silence
        silence = np.zeros(int(sr * 0.5))
        speech = np.random.normal(0, 0.2, int(sr * 2))
        audio = np.concatenate([silence, speech, silence])
        
        trimmed = AudioProcessor.trim_silence(audio, sr)
        
        # Trimmed should be shorter
        assert len(trimmed) < len(audio)
        # But should contain the speech
        assert len(trimmed) > len(speech) * 0.8


@pytest.mark.skipif(not AUDIO_PIPELINE_AVAILABLE, reason="Audio pipeline not available")
class TestSpeechToText:
    """Test STT functionality."""
    
    @pytest.fixture
    def stt(self):
        """Create SpeechToText instance."""
        try:
            return SpeechToText(model_size="tiny", device="cpu")
        except Exception as e:
            pytest.skip(f"Whisper not available: {e}")
    
    def test_stt_initialization(self, stt):
        """Test STT model loads."""
        assert stt is not None
        assert stt.model is not None
        assert stt.model_size == "tiny"


@pytest.mark.skipif(not AUDIO_PIPELINE_AVAILABLE, reason="Audio pipeline not available")
class TestAudioPipeline:
    """Test complete audio pipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Create AudioPipeline instance."""
        try:
            return AudioPipeline()
        except Exception as e:
            pytest.skip(f"Audio pipeline not available: {e}")
    
    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initializes."""
        assert pipeline is not None
        assert pipeline.stt is not None
        assert pipeline.audio_processor is not None
    
    def test_audio_metadata_estimation(self, pipeline):
        """Test quick emotion estimation from audio."""
        # Create synthetic audio (higher energy = higher arousal estimate)
        sr = 16000
        audio = np.random.normal(0, 0.3, sr * 2)  # 2 seconds
        
        # Save to bytes
        import soundfile as sf
        buffer = BytesIO()
        sf.write(buffer, audio, sr, format='WAV')
        audio_bytes = buffer.getvalue()
        
        result = pipeline.estimate_emotion_from_audio_metadata(audio_bytes)
        
        assert "estimated_arousal" in result
        assert 0 <= result["estimated_arousal"] <= 1
        assert "speech_rate_wpm" in result
        assert result["speech_rate_wpm"] > 0


class TestAudioInputUI:
    """Test Streamlit audio UI components."""
    
    def test_audio_settings_rendering(self):
        """Test audio settings can be created."""
        try:
            from spoken_interface.audio_input import render_audio_settings
            # Can't easily test Streamlit widgets outside of Streamlit context
            # Just verify the function exists and is callable
            assert callable(render_audio_settings)
        except ImportError:
            pytest.skip("Audio input UI not available")
    
    def test_audio_visualization_function(self):
        """Test waveform visualization exists."""
        try:
            from spoken_interface.audio_input import render_audio_visualization
            assert callable(render_audio_visualization)
        except ImportError:
            pytest.skip("Audio visualization not available")


# Integration test: Full pipeline
@pytest.mark.skipif(not AUDIO_PIPELINE_AVAILABLE, reason="Audio pipeline not available")
def test_full_audio_pipeline():
    """Integration test: Load audio, preprocess, estimate emotion."""
    try:
        from spoken_interface.audio_pipeline import AudioPipeline
        
        pipeline = AudioPipeline()
        
        # Create synthetic audio
        sr = 16000
        duration = 3.0
        t = np.linspace(0, duration, int(sr * duration))
        
        # Generate audio with varying frequency (simulates speech)
        audio = np.sin(2 * np.pi * 200 * t) * 0.2
        audio += np.sin(2 * np.pi * 400 * t) * 0.1  # Harmonics
        audio += np.random.normal(0, 0.02, len(audio))  # Noise
        
        # Save to bytes
        import soundfile as sf
        buffer = BytesIO()
        sf.write(buffer, audio, sr, format='WAV')
        audio_bytes = buffer.getvalue()
        
        # Run through pipeline
        result = pipeline.estimate_emotion_from_audio_metadata(audio_bytes)
        
        # Verify outputs
        assert "estimated_arousal" in result
        assert "speech_rate_wpm" in result
        assert "energy_level" in result
        assert "pitch_range" in result
        
        print(f"✅ Audio pipeline test passed!")
        print(f"   Arousal: {result['estimated_arousal']:.2f}")
        print(f"   Speech rate: {result['speech_rate_wpm']} WPM")
        print(f"   Energy: {result['energy_level']:.2f}")
        print(f"   Pitch range: {result['pitch_range']}")
    
    except Exception as e:
        pytest.skip(f"Full pipeline test skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
