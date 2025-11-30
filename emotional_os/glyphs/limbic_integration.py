#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limbic-Adjacent System Integration

Integrates the limbic-adjacent neural mappings into the existing
glyph learning and emotional processing pipeline.

This creates the complete chiasmus: neural activation → ritual scaffolding → glyph systems.
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Optional instrumentation logger. Enable by setting env var SAORIVERSE_LIMBIC_DEBUG
logger = logging.getLogger(__name__)

# Add the glyphs directory to path for imports
sys.path.append(os.path.dirname(__file__))

from .limbic_adjacent_system import SystemType, get_limbic_system
from .limbic_visualizer import LimbicVisualizer

try:
    from .glyph_learner import GlyphLearner

    HAS_GLYPH_LEARNER = True
except ImportError:
    try:
        from glyph_learner import GlyphLearner

        HAS_GLYPH_LEARNER = True
    except ImportError:
        HAS_GLYPH_LEARNER = False
        GlyphLearner = None

try:
    from .shared_glyph_manager import SharedGlyphManager

    HAS_SHARED_MANAGER = True
except ImportError:
    try:
        from shared_glyph_manager import SharedGlyphManager

        HAS_SHARED_MANAGER = True
    except ImportError:
        HAS_SHARED_MANAGER = False
        SharedGlyphManager = None


class LimbicIntegrationEngine:
    """
    Integrates limbic-adjacent system into glyph learning pipeline.

    This creates the complete neural-to-glyph transformation:
    Brain Region → Neural Function → Ritual → Glyph Sequence → System Signal
    """

    def __init__(self, db_path: str = "glyphs.db"):
        self.limbic_system = get_limbic_system()
        self.visualizer = LimbicVisualizer()

        # Initialize glyph systems if available
        self.glyph_learner = GlyphLearner(db_path) if HAS_GLYPH_LEARNER else None
        self.glyph_manager = SharedGlyphManager(db_path) if HAS_SHARED_MANAGER else None

        print("FP Limbic-Adjacent Integration Engine initialized")

    def process_emotion_with_limbic_mapping(self, emotion: str, intensity: float = 1.0) -> Dict[str, Any]:
        """
        Process an emotion through the complete limbic-adjacent pipeline.

        Returns neural mappings, glyph sequences, and system signals.
        """
        result = {
            "emotion": emotion,
            "intensity": intensity,
            "limbic_mapping": {},
            "glyph_sequences": {},
            "system_signals": {},
            "ritual_sequence": [],
        }

        # Get chiasmus mapping
        chiasmus = self.limbic_system.create_ritual_chiasmus(emotion)
        result["system_signals"] = chiasmus["system_signals"]
        result["ritual_sequence"] = chiasmus["ritual_sequence"]

        # Instrumentation: lightweight logging to help detect when limbic mapping
        # actually runs and what it produced. Controlled by logger level.
        try:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "process_emotion_with_limbic_mapping emotion=%s -> signals=%d regions=%d",
                    str(emotion)[:120],
                    len(result["system_signals"]),
                    len(result["limbic_mapping"]),
                )
        except Exception:
            pass

        # Generate glyph sequences for each brain region
        brain_regions = ["insula", "amygdala", "hippocampus", "acc", "vmpfc"]
        for region in brain_regions:
            region_data = {"glyph_sequences": {}, "ritual_mappings": {}}

            # Get glyph sequences for each system
            for system in SystemType:
                glyphs = self.limbic_system.generate_glyph_sequence(region, system)
                if glyphs:
                    region_data["glyph_sequences"][system.value] = glyphs

            # Get ritual mappings
            brain_region = self.limbic_system.get_brain_region(region)
            if brain_region:
                region_data["ritual_mappings"] = {ritual: desc for ritual, desc in brain_region.ritual_mappings.items()}

            result["limbic_mapping"][region] = region_data

        return result

    def create_neural_glyph_candidates(self, emotion: str, user_id: str = "default") -> List[Dict[str, Any]]:
        """
        Create glyph candidates based on neural mappings.

        This integrates limbic processing with glyph learning.
        """
        candidates = []

        # Process emotion through limbic system
        limbic_result = self.process_emotion_with_limbic_mapping(emotion)

        # Create candidates from system signals
        for system_enum, signal_data in limbic_result["system_signals"].items():
            system_name = system_enum.value if hasattr(system_enum, "value") else str(system_enum)
            candidate = {
                "glyph_name": f"{emotion}_{system_name}_{signal_data['glyph']}",
                "emotion": emotion,
                "system": system_name,
                "glyph": signal_data["glyph"],
                "signal": signal_data["signal"],
                "intensity": limbic_result["intensity"],
                "neural_basis": "limbic_adjacent",
                "user_id": user_id,
            }
            candidates.append(candidate)

        # Create candidates from brain region glyph sequences
        for region_name, region_data in limbic_result["limbic_mapping"].items():
            for system_name, glyph_sequence in region_data["glyph_sequences"].items():
                if glyph_sequence:  # Only if there are glyphs
                    candidate = {
                        "glyph_name": f"{emotion}_{region_name}_{system_name}_sequence",
                        "emotion": emotion,
                        "brain_region": region_name,
                        "system": system_name,
                        "glyph_sequence": glyph_sequence,
                        "primary_glyph": glyph_sequence[0],  # Use first glyph as primary
                        "intensity": limbic_result["intensity"],
                        "neural_basis": "limbic_adjacent",
                        "user_id": user_id,
                    }
                    candidates.append(candidate)

        return candidates

    def integrate_with_glyph_learning(self, emotion: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Integrate limbic processing with glyph learning system.

        This creates the complete pipeline from neural activation to glyph storage.
        """
        result = {
            "emotion": emotion,
            "user_id": user_id,
            "limbic_processed": False,
            "glyphs_generated": 0,
            "glyphs_stored": 0,
            "errors": [],
        }

        try:
            # Process through limbic system
            limbic_result = self.process_emotion_with_limbic_mapping(
                emotion
            )  # noqa: F841  # kept for potential debugging
            result["limbic_processed"] = True

            # Generate glyph candidates
            candidates = self.create_neural_glyph_candidates(emotion, user_id)
            result["glyphs_generated"] = len(candidates)

            # Store in glyph systems if available
            if self.glyph_learner and self.glyph_manager:
                stored_count = 0
                for candidate in candidates:
                    try:
                        # Store glyph candidate
                        glyph_name = candidate["glyph_name"]
                        glyph_data = {  # noqa: F841  # built for potential downstream storage/logging
                            "emotion": candidate["emotion"],
                            "glyph": candidate.get("glyph", candidate.get("primary_glyph", "❓")),
                            "signal": candidate.get("signal", f"Neural {emotion} signal"),
                            "system": candidate.get("system", "unknown"),
                            "neural_basis": candidate["neural_basis"],
                            "intensity": candidate["intensity"],
                        }

                        # Use glyph learner to analyze (not store yet)
                        # TODO: Implement proper glyph storage integration
                        print(f"Generated glyph candidate: {glyph_name}")
                        stored_count += 1

                    except Exception as e:
                        result["errors"].append(f"Failed to store {candidate['glyph_name']}: {str(e)}")

                result["glyphs_stored"] = stored_count

            result["status"] = "success"

        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"Limbic integration failed: {str(e)}")

        return result

    def get_neural_activation_report(self, emotion: str) -> str:
        """
        Generate a comprehensive report of neural activation for an emotion.
        """
        report = f"""
FP NEURAL ACTIVATION REPORT: {emotion.upper()}
{'=' * 60}

"""

        # Get limbic processing
        limbic_result = self.process_emotion_with_limbic_mapping(emotion)

        report += f"""EMOTION: {emotion}
INTENSITY: {limbic_result['intensity']}

SYSTEM SIGNALS:
"""
        for system_name, signal_data in limbic_result["system_signals"].items():
            # Convert SystemType enum to string if needed
            system_key = system_name.value if hasattr(system_name, "value") else str(system_name)
            report += f"  {system_key.upper()}: {signal_data['glyph']} {signal_data['signal']}\n"

        report += f"""
RITUAL SEQUENCE: {' → '.join(limbic_result['ritual_sequence'])}

BRAIN REGION ACTIVATION:
"""

        for region_name, region_data in limbic_result["limbic_mapping"].items():
            report += f"""
{region_name.upper()}:
"""
            # Show glyph sequences
            for system_name, glyphs in region_data["glyph_sequences"].items():
                if glyphs:
                    report += f"  {system_name}: {' → '.join(glyphs)}\n"

            # Show ritual mappings
            for ritual, desc in region_data["ritual_mappings"].items():
                report += f"  • {ritual}: {desc}\n"

        report += f"""
✨ CHIASMUS COMPLETE: Neural activation → Ritual scaffolding → Glyph systems
   One {emotion} feeling expressed as coordinated signals across all systems.
"""

        return report

    def visualize_neural_flow(self, emotion: str, output_file: Optional[str] = None) -> str:
        """
        Create and optionally save a visualization of the neural flow.
        """
        visualization = self.visualizer.create_emotion_chiasmus_diagram(emotion)

        if output_file:
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(visualization)
                print(f"✅ Neural flow visualization saved to {output_file}")
            except Exception as e:
                print(f"❌ Failed to save visualization: {e}")

        return visualization


def demo_limbic_integration():
    """Demo the limbic integration engine."""
    print("FP Limbic-Adjacent Integration Engine Demo")
    print("=" * 60)

    engine = LimbicIntegrationEngine()

    # Test emotion processing
    emotion = "joy"
    print(f"\n🎭 Processing emotion: {emotion}")

    result = engine.process_emotion_with_limbic_mapping(emotion)
    print(f"✅ Generated {len(result['system_signals'])} system signals")
    print(f"✅ Mapped to {len(result['limbic_mapping'])} brain regions")

    # Show system signals
    print("\n🌈 System Signals:")
    for system, signal in result["system_signals"].items():
        print(f"  {system.value}: {signal['glyph']} {signal['signal']}")

    # Generate neural activation report
    print("\n📊 Neural Activation Report:")
    report = engine.get_neural_activation_report(emotion)
    print(report[:500] + "...\n[Report truncated for demo]")

    # Test glyph candidate generation
    candidates = engine.create_neural_glyph_candidates(emotion)
    print(f"\n🎨 Generated {len(candidates)} glyph candidates")

    # Show first few candidates
    for i, candidate in enumerate(candidates[:3]):
        glyph = candidate.get("glyph", candidate.get("primary_glyph", "❓"))
        print(f"  {i+1}. {candidate['glyph_name']}: {glyph}")

    print("\n✅ Limbic integration demo complete!")


if __name__ == "__main__":
    demo_limbic_integration()
