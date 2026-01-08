"""Tests for Sprint 3: Streaming TTS Integration

Test audio synthesis, prosody application, and streaming buffering.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from spoken_interface.streaming_tts import (
    ProsodyApplier,
    StreamingTTSEngine,
    AudioBufferQueue,
    StreamingTTSPipeline,
    TTSAudioChunk,
    TTSConfig,
    StreamingTTSError,
    export_audio_chunks_to_bytes,
)


class TestProsodyApplier:
    """Test prosody modifications to audio."""

    def test_apply_rate_change_no_change(self):
        """Rate multiplier 1.0 should return unchanged audio."""
        applier = ProsodyApplier(sample_rate=22050)
        audio = np.random.randn(22050)  # 1 second

        result = applier.apply_rate_change(audio, 1.0)

        # Should be very similar (allow small numerical differences)
        assert len(result) == len(audio)
        assert np.allclose(result, audio, atol=0.01)

    def test_apply_rate_change_faster(self):
        """Rate > 1.0 should shorten audio."""
        applier = ProsodyApplier(sample_rate=22050)
        audio = np.random.randn(22050)  # 1 second

        result = applier.apply_rate_change(audio, 1.5)

        # Should be shorter (time-stretched)
        # Exact length depends on librosa availability
        assert len(result) < len(audio)

    def test_apply_rate_change_slower(self):
        """Rate < 1.0 should lengthen audio."""
        applier = ProsodyApplier(sample_rate=22050)
        audio = np.random.randn(22050)  # 1 second

        result = applier.apply_rate_change(audio, 0.75)

        # Should be longer
        assert len(result) > len(audio)

    def test_apply_rate_change_invalid(self):
        """Negative rate should raise error."""
        applier = ProsodyApplier()
        audio = np.random.randn(22050)

        with pytest.raises(ValueError):
            applier.apply_rate_change(audio, -0.5)

    def test_apply_pitch_shift_no_change(self):
        """Pitch shift 0 should return unchanged audio."""
        applier = ProsodyApplier()
        audio = np.random.randn(22050)

        result = applier.apply_pitch_shift(audio, 0.0)

        assert np.allclose(result, audio, atol=0.01)

    def test_apply_pitch_shift_up(self):
        """Positive pitch shift should change audio."""
        applier = ProsodyApplier()
        audio = np.random.randn(22050)

        result = applier.apply_pitch_shift(audio, 2.0)

        # Should produce audio (fallback if librosa unavailable)
        assert len(result) > 0

    def test_apply_energy_scaling(self):
        """Energy scaling should change amplitude."""
        applier = ProsodyApplier()
        audio = np.random.randn(22050) * 0.5

        result = applier.apply_energy_scaling(audio, 0.5)

        # Should be quieter
        assert np.max(np.abs(result)) <= np.max(np.abs(audio))

    def test_apply_energy_scaling_clipping(self):
        """Energy scaling should clip to prevent distortion."""
        applier = ProsodyApplier()
        audio = np.ones(22050) * 0.5

        result = applier.apply_energy_scaling(audio, 3.0)

        # Should be clipped to avoid distortion
        assert np.max(np.abs(result)) <= 0.95


class TestTTSConfig:
    """Test TTS configuration."""

    def test_default_config(self):
        """Default config should have sensible values."""
        config = TTSConfig()

        assert config.sample_rate == 22050
        assert config.chunk_size_ms == 500
        assert config.gpu is False

    def test_custom_config(self):
        """Custom config should override defaults."""
        config = TTSConfig(
            sample_rate=16000,
            chunk_size_ms=1000,
            gpu=True,
        )

        assert config.sample_rate == 16000
        assert config.chunk_size_ms == 1000
        assert config.gpu is True


class TestAudioBufferQueue:
    """Test audio buffering."""

    def test_put_and_get_chunk(self):
        """Should buffer and retrieve chunks."""
        buffer = AudioBufferQueue(max_chunks=10)
        chunk = TTSAudioChunk(
            audio_data=np.random.randn(1000),
            duration_ms=100,
            start_time_ms=0,
            is_final=False
        )

        buffer.put_chunk(chunk)
        retrieved = buffer.get_chunk(timeout=1.0)

        assert retrieved is not None
        assert np.allclose(retrieved.audio_data, chunk.audio_data)
        assert retrieved.duration_ms == chunk.duration_ms

    def test_buffer_fifo(self):
        """Buffer should be FIFO."""
        buffer = AudioBufferQueue(max_chunks=3)

        chunks = [
            TTSAudioChunk(np.ones(1000) * i, 100, float(i * 100), False)
            for i in range(3)
        ]

        for chunk in chunks:
            buffer.put_chunk(chunk)

        for i, expected in enumerate(chunks):
            retrieved = buffer.get_chunk(timeout=1.0)
            assert np.allclose(retrieved.audio_data, expected.audio_data)

    def test_buffer_full_timeout(self):
        """Full buffer should timeout on put."""
        buffer = AudioBufferQueue(max_chunks=1)

        chunk1 = TTSAudioChunk(np.ones(1000), 100, 0, False)
        chunk2 = TTSAudioChunk(np.ones(1000), 100, 100, False)

        buffer.put_chunk(chunk1)

        # Second put should timeout
        with pytest.raises(StreamingTTSError):
            buffer.put_chunk(chunk2, timeout=0.1)

    def test_empty_timeout(self):
        """Get from empty buffer should timeout."""
        buffer = AudioBufferQueue()

        result = buffer.get_chunk(timeout=0.1)

        assert result is None

    def test_buffer_size(self):
        """Buffer size should reflect number of chunks."""
        buffer = AudioBufferQueue(max_chunks=5)

        assert buffer.size() == 0

        buffer.put_chunk(TTSAudioChunk(np.ones(1000), 100, 0, False))
        assert buffer.size() == 1

        buffer.put_chunk(TTSAudioChunk(np.ones(1000), 100, 100, False))
        assert buffer.size() == 2

    def test_clear_buffer(self):
        """Clear should remove all chunks."""
        buffer = AudioBufferQueue(max_chunks=5)

        for i in range(3):
            buffer.put_chunk(TTSAudioChunk(
                np.ones(1000), 100, float(i * 100), False))

        assert buffer.size() == 3
        buffer.clear()
        assert buffer.size() == 0


class TestAudioChunk:
    """Test audio chunk dataclass."""

    def test_chunk_creation(self):
        """Should create chunk with proper fields."""
        audio = np.random.randn(2000)
        chunk = TTSAudioChunk(
            audio_data=audio,
            duration_ms=200,
            start_time_ms=100,
            is_final=True
        )

        assert chunk.duration_ms == 200
        assert chunk.start_time_ms == 100
        assert chunk.is_final is True
        assert len(chunk.audio_data) == 2000

    def test_chunk_default_final(self):
        """is_final should default to False."""
        chunk = TTSAudioChunk(
            audio_data=np.zeros(1000),
            duration_ms=100,
            start_time_ms=0
        )

        assert chunk.is_final is False


class TestStreamingTTSEngine:
    """Test TTS synthesis engine."""

    def test_engine_initialization(self):
        """Engine should initialize with config."""
        config = TTSConfig(sample_rate=16000)

        # Mock TTS to avoid loading model
        with patch('spoken_interface.streaming_tts.HAS_TTS', True):
            with patch.object(StreamingTTSEngine, '_load_model'):
                engine = StreamingTTSEngine(config)

                assert engine.config.sample_rate == 16000
                assert engine.sample_rate == 16000

    def test_engine_requires_tts(self):
        """Engine should fail if TTS not available."""
        with patch('spoken_interface.streaming_tts.HAS_TTS', False):
            with pytest.raises(StreamingTTSError):
                StreamingTTSEngine()

    def test_lazy_load_model(self):
        """Model should load on first use, not on init."""
        with patch('spoken_interface.streaming_tts.HAS_TTS', True):
            with patch.object(StreamingTTSEngine, '_load_model') as mock_load:
                engine = StreamingTTSEngine()

                # _load_model not called on init
                mock_load.assert_not_called()

                # Model not loaded yet
                assert engine._tts_model is None


class TestStreamingTTSPipeline:
    """Test complete streaming pipeline."""

    def test_pipeline_initialization(self):
        """Pipeline should initialize successfully."""
        with patch('spoken_interface.streaming_tts.HAS_TTS', True):
            with patch.object(StreamingTTSEngine, '_load_model'):
                pipeline = StreamingTTSPipeline()

                assert pipeline.engine is not None
                assert pipeline.buffer is not None
                assert pipeline._is_running is False

    def test_buffer_queue_integration(self):
        """Pipeline buffer should be functional."""
        with patch('spoken_interface.streaming_tts.HAS_TTS', True):
            with patch.object(StreamingTTSEngine, '_load_model'):
                pipeline = StreamingTTSPipeline()

                # Add chunk to buffer
                chunk = TTSAudioChunk(
                    audio_data=np.ones(1000),
                    duration_ms=100,
                    start_time_ms=0
                )
                pipeline.buffer.put_chunk(chunk)

                # Retrieve from buffer
                retrieved = pipeline.buffer.get_chunk(timeout=1.0)
                assert retrieved is not None


class TestExportAudioChunks:
    """Test audio export functionality."""

    def test_export_single_chunk(self):
        """Should export single chunk to WAV bytes."""
        pytest.importorskip("soundfile")

        chunk = TTSAudioChunk(
            audio_data=np.sin(np.linspace(0, 4 * np.pi, 22050)),
            duration_ms=1000,
            start_time_ms=0,
            is_final=True
        )

        result = export_audio_chunks_to_bytes([chunk], sample_rate=22050)

        # Should be bytes
        assert isinstance(result, bytes)

        # Should have WAV header
        assert result[:4] == b'RIFF'
        assert result[8:12] == b'WAVE'

    def test_export_multiple_chunks(self):
        """Should export multiple chunks combined."""
        pytest.importorskip("soundfile")

        chunks = [
            TTSAudioChunk(
                audio_data=np.sin(np.linspace(0, 4 * np.pi, 11025)),
                duration_ms=500,
                start_time_ms=float(i * 500)
            )
            for i in range(2)
        ]
        chunks[-1].is_final = True

        result = export_audio_chunks_to_bytes(chunks, sample_rate=22050)

        # Should be valid WAV
        assert isinstance(result, bytes)
        assert result[:4] == b'RIFF'

    def test_export_empty_chunks_error(self):
        """Should error on empty chunks."""
        pytest.importorskip("soundfile")

        with pytest.raises(StreamingTTSError):
            export_audio_chunks_to_bytes([])

    def test_export_without_soundfile(self):
        """Should error if soundfile not available."""
        with patch('spoken_interface.streaming_tts.HAS_SOUNDFILE', False):
            chunk = TTSAudioChunk(
                audio_data=np.ones(1000),
                duration_ms=100,
                start_time_ms=0
            )

            with pytest.raises(StreamingTTSError):
                export_audio_chunks_to_bytes([chunk])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
