"""Sprint 5a: Performance Profiling & Optimization

Profiles STT/TTS pipeline latency and identifies bottlenecks.
Supports model selection for speed/quality tradeoffs.
"""

import time
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import json
from pathlib import Path


@dataclass
class LatencyMeasurement:
    """Records timing for a single operation."""

    operation: str
    """Name of the operation."""

    start_time: float
    """Unix timestamp when operation started."""

    end_time: float
    """Unix timestamp when operation ended."""

    duration_ms: float = field(init=False)
    """Duration in milliseconds."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional context (model name, input size, etc)."""

    def __post_init__(self):
        """Calculate duration."""
        self.duration_ms = (self.end_time - self.start_time) * 1000


class PerformanceProfiler:
    """Profiles voice pipeline operations for latency optimization."""

    def __init__(self, auto_save: bool = True, save_path: Optional[str] = None):
        """Initialize profiler.

        Args:
            auto_save: Automatically save results
            save_path: Path to save JSON results
        """
        self.measurements: List[LatencyMeasurement] = []
        self.auto_save = auto_save
        self.save_path = Path(save_path) if save_path else Path(
            "latency_results.json")
        self.session_start = datetime.now()

    def measure(
        self,
        operation: str,
        func: Callable,
        *args,
        metadata: Optional[Dict] = None,
        **kwargs
    ) -> Any:
        """Measure execution time of a function.

        Args:
            operation: Operation name
            func: Function to execute
            metadata: Optional metadata to record
            args/kwargs: Arguments to pass to func

        Returns:
            Function result
        """
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        self.measurements.append(LatencyMeasurement(
            operation=operation,
            start_time=start,
            end_time=end,
            metadata=metadata or {}
        ))

        return result

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics.

        Returns:
            Dictionary with latency statistics
        """
        if not self.measurements:
            return {"error": "No measurements recorded"}

        # Group by operation
        by_operation = {}
        for m in self.measurements:
            if m.operation not in by_operation:
                by_operation[m.operation] = []
            by_operation[m.operation].append(m.duration_ms)

        # Calculate stats
        stats = {}
        for op, durations in by_operation.items():
            durations_arr = np.array(durations)
            stats[op] = {
                "count": len(durations),
                "mean_ms": float(np.mean(durations_arr)),
                "median_ms": float(np.median(durations_arr)),
                "min_ms": float(np.min(durations_arr)),
                "max_ms": float(np.max(durations_arr)),
                "std_ms": float(np.std(durations_arr)),
                "p95_ms": float(np.percentile(durations_arr, 95)),
                "p99_ms": float(np.percentile(durations_arr, 99)),
            }

        # Calculate total pipeline time
        if self.measurements:
            total_duration = (
                self.measurements[-1].end_time -
                self.measurements[0].start_time
            ) * 1000
        else:
            total_duration = 0

        return {
            "session_start": self.session_start.isoformat(),
            "measurement_count": len(self.measurements),
            "total_duration_ms": total_duration,
            "by_operation": stats,
        }

    def save_results(self, path: Optional[str] = None) -> str:
        """Save profiling results to JSON.

        Args:
            path: Path to save to (default: self.save_path)

        Returns:
            Path where results were saved
        """
        save_path = Path(path) if path else self.save_path

        summary = self.get_summary()
        summary["measurements"] = [
            {
                "operation": m.operation,
                "duration_ms": m.duration_ms,
                "metadata": m.metadata,
                "timestamp": m.start_time,
            }
            for m in self.measurements
        ]

        with open(save_path, "w") as f:
            json.dump(summary, f, indent=2)

        return str(save_path)

    def print_summary(self) -> None:
        """Print summary to console."""
        summary = self.get_summary()

        print("\n" + "="*60)
        print("PERFORMANCE PROFILING SUMMARY")
        print("="*60)
        print(f"Session: {summary['session_start']}")
        print(f"Total measurements: {summary['measurement_count']}")
        print(f"Total duration: {summary['total_duration_ms']:.1f}ms")
        print("\nOperation Breakdown:")
        print("-"*60)

        for op, stats in summary["by_operation"].items():
            print(f"\n{op}:")
            print(f"  Count:    {stats['count']}")
            print(f"  Mean:     {stats['mean_ms']:.1f}ms")
            print(f"  Median:   {stats['median_ms']:.1f}ms")
            print(
                f"  Min/Max:  {stats['min_ms']:.1f}ms / {stats['max_ms']:.1f}ms")
            print(f"  Std Dev:  {stats['std_ms']:.1f}ms")
            print(
                f"  P95/P99:  {stats['p95_ms']:.1f}ms / {stats['p99_ms']:.1f}ms")

        print("\n" + "="*60 + "\n")


class ModelPerformanceBenchmark:
    """Benchmarks different model configurations for speed/quality tradeoff."""

    # Whisper model configurations (size -> latency tradeoff)
    WHISPER_MODELS = {
        "tiny": {"size_mb": 39, "lang_tokens": 50, "relative_speed": 1.0},
        "small": {"size_mb": 139, "lang_tokens": 50, "relative_speed": 0.6},
        "base": {"size_mb": 293, "lang_tokens": 50, "relative_speed": 0.4},
        "medium": {"size_mb": 769, "lang_tokens": 50, "relative_speed": 0.2},
    }

    # Coqui TTS model configurations
    TTS_MODELS = {
        "glow-tts": {"size_mb": 600, "relative_speed": 1.0, "quality": "high"},
        "tacotron2": {"size_mb": 200, "relative_speed": 0.8, "quality": "high"},
        "glow-tts-tiny": {"size_mb": 150, "relative_speed": 1.5, "quality": "medium"},
    }

    @classmethod
    def get_whisper_recommendation(cls, target_latency_ms: float) -> str:
        """Recommend Whisper model based on latency target.

        Args:
            target_latency_ms: Desired maximum latency in milliseconds

        Returns:
            Recommended model name
        """
        # Baseline: tiny is ~100ms for 10s audio
        baseline_latency = 100  # ms for 10s audio

        recommendations = []
        for model, info in cls.WHISPER_MODELS.items():
            estimated_latency = baseline_latency / info["relative_speed"]
            recommendations.append((estimated_latency, model))

        recommendations.sort()

        for latency, model in recommendations:
            if latency <= target_latency_ms:
                return model

        # Return fastest if none match target
        return recommendations[0][1]

    @classmethod
    def get_tts_recommendation(cls, target_latency_ms: float) -> str:
        """Recommend TTS model based on latency target.

        Args:
            target_latency_ms: Desired maximum latency in milliseconds

        Returns:
            Recommended model name
        """
        # Baseline: tacotron2 is ~100ms for 10 words
        baseline_latency = 100  # ms for 10 words

        recommendations = []
        for model, info in cls.TTS_MODELS.items():
            estimated_latency = baseline_latency / info["relative_speed"]
            recommendations.append((estimated_latency, model))

        recommendations.sort()

        for latency, model in recommendations:
            if latency <= target_latency_ms:
                return model

        return recommendations[0][1]

    @classmethod
    def print_benchmark_table(cls) -> None:
        """Print benchmark comparison table."""
        print("\n" + "="*70)
        print("WHISPER MODEL BENCHMARK")
        print("="*70)
        print(f"{'Model':<12} {'Size (MB)':<12} {'Est. Latency*':<20} {'Quality':<15}")
        print("-"*70)

        for model, info in cls.WHISPER_MODELS.items():
            est_latency = f"{100 / info['relative_speed']:.0f}ms (10s)"
            quality = "High"
            print(
                f"{model:<12} {info['size_mb']:<12} {est_latency:<20} {quality:<15}")

        print("\n" + "="*70)
        print("COQUI TTS MODEL BENCHMARK")
        print("="*70)
        print(f"{'Model':<20} {'Size (MB)':<12} {'Est. Latency*':<20} {'Quality':<12}")
        print("-"*70)

        for model, info in cls.TTS_MODELS.items():
            est_latency = f"{100 / info['relative_speed']:.0f}ms (10w)"
            print(
                f"{model:<20} {info['size_mb']:<12} {est_latency:<20} {info['quality']:<12}")

        print("\n* Estimated latency per 10s audio (Whisper) or 10 words (TTS)")
        print("  Actual latency depends on hardware (CPU/GPU), audio quality, etc.")
        print("="*70 + "\n")


class LatencyOptimizer:
    """Suggests optimizations based on profiling data."""

    @staticmethod
    def analyze_measurements(measurements: List[LatencyMeasurement]) -> Dict[str, Any]:
        """Analyze latency measurements and suggest optimizations.

        Args:
            measurements: List of profiled measurements

        Returns:
            Dictionary with analysis and recommendations
        """
        if not measurements:
            return {"error": "No measurements to analyze"}

        by_operation = {}
        for m in measurements:
            if m.operation not in by_operation:
                by_operation[m.operation] = []
            by_operation[m.operation].append(m.duration_ms)

        # Find bottlenecks (operations taking >20% of total time)
        total_time = sum(max(times) for times in by_operation.values())
        bottlenecks = []

        for op, times in by_operation.items():
            avg_time = np.mean(times)
            if avg_time > total_time * 0.2:
                bottlenecks.append({
                    "operation": op,
                    "avg_ms": float(avg_time),
                    "percent_of_total": float(avg_time / total_time * 100),
                })

        bottlenecks.sort(key=lambda x: x["avg_ms"], reverse=True)

        # Generate recommendations
        recommendations = []

        for bn in bottlenecks:
            if "stt" in bn["operation"].lower() or "whisper" in bn["operation"].lower():
                recommendations.append(
                    f"STT bottleneck detected ({bn['avg_ms']:.0f}ms): "
                    "Consider using 'tiny' Whisper model for faster transcription"
                )
            elif "tts" in bn["operation"].lower() or "synthesis" in bn["operation"].lower():
                recommendations.append(
                    f"TTS bottleneck detected ({bn['avg_ms']:.0f}ms): "
                    "Consider using faster TTS model or increasing chunk size"
                )
            elif "buffer" in bn["operation"].lower():
                recommendations.append(
                    f"Buffering bottleneck ({bn['avg_ms']:.0f}ms): "
                    "Check buffer queue size or playback speed"
                )

        return {
            "total_operations": len(measurements),
            "bottlenecks": bottlenecks,
            "recommendations": recommendations,
        }


def profile_stt_pipeline(audio_bytes: bytes) -> Dict[str, float]:
    """Profile STT pipeline on sample audio.

    Args:
        audio_bytes: Audio data to transcribe

    Returns:
        Dictionary with latency measurements
    """
    try:
        from spoken_interface import AudioPipeline
    except ImportError:
        return {"error": "Audio pipeline not available"}

    profiler = PerformanceProfiler()
    pipeline = AudioPipeline()

    # Profile entire pipeline
    result = profiler.measure(
        "stt_full_pipeline",
        pipeline.process_user_audio,
        audio_bytes,
        metadata={"audio_size_bytes": len(audio_bytes)}
    )

    profiler.print_summary()
    return profiler.get_summary()


def profile_tts_pipeline(text: str) -> Dict[str, float]:
    """Profile TTS pipeline on sample text.

    Args:
        text: Text to synthesize

    Returns:
        Dictionary with latency measurements
    """
    try:
        from spoken_interface.streaming_tts import StreamingTTSPipeline
        from spoken_interface.prosody_planner import ProsodyPlanner, GlyphSignals
    except ImportError:
        return {"error": "TTS pipeline not available"}

    profiler = PerformanceProfiler()
    tts_pipeline = StreamingTTSPipeline()
    prosody_planner = ProsodyPlanner()

    # Create glyph signals
    signals = GlyphSignals(
        text=text,
        voltage=0.5,
        tone="neutral",
        emotional_attunement=0.5,
        certainty=0.7,
        valence=0.5,
    )

    # Profile prosody planning
    prosody_plan = profiler.measure(
        "prosody_planning",
        prosody_planner.plan_from_glyph,
        signals,
        metadata={"text_length": len(text)}
    )

    # Profile TTS synthesis
    audio = profiler.measure(
        "tts_synthesis",
        tts_pipeline.engine.synthesize_with_prosody,
        text,
        prosody_plan,
        metadata={"text_length": len(text), "model": "tacotron2"}
    )

    profiler.print_summary()
    return profiler.get_summary()


if __name__ == "__main__":
    print("Voice Pipeline Performance Profiler\n")

    # Show model recommendations
    ModelPerformanceBenchmark.print_benchmark_table()

    print("\nExample: Recommend models for 150ms latency target:")
    print(f"  STT: {ModelPerformanceBenchmark.get_whisper_recommendation(150)}")
    print(f"  TTS: {ModelPerformanceBenchmark.get_tts_recommendation(150)}")

    print("\nNote: Run profile_stt_pipeline() or profile_tts_pipeline() with real data")
    print("      to measure actual performance on your hardware")
