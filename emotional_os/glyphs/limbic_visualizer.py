#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limbic-Adjacent System Visualizer

Creates visualizations showing how one feeling becomes five signals
across the glyph-encoded systems (Lightpath, Threshold, VELONIX, Velinor, Saonyx).

This demonstrates the chiasmus - the nervous system composing rather than reacting.
"""

import os
from typing import Dict

# Import the minimal symbol we need; other components are optional and only
# imported when present in the execution environment.
try:
    from limbic_adjacent_system import get_limbic_system
except ImportError:
    # Fallback for when run from different directory
    import sys

    sys.path.append(os.path.dirname(__file__))
    from limbic_adjacent_system import get_limbic_system


class LimbicVisualizer:
    """
    Visualizes the limbic-adjacent system mappings and chiasmus transformations.
    """

    def __init__(self):
        self.system = get_limbic_system()

    def create_emotion_chiasmus_diagram(self, emotion: str, intensity: float = 1.0) -> str:
        """
        Create a text-based diagram showing how one emotion becomes five signals.
        """
        chiasmus = self.system.create_ritual_chiasmus(emotion)

        diagram = f"""
FP LIMBIC-ADJACENT CHIASMUS: {emotion.upper()}
{'=' * 60}

ONE FEELING → FIVE SIGNALS

Emotion Input: {emotion} (intensity: {intensity:.1f})
Neural Basis: {chiasmus['neural_basis']}

SYSTEM SIGNALS:
"""

        for system_type, signal_data in chiasmus["system_signals"].items():
            glyph = signal_data["glyph"]
            signal = signal_data["signal"]
            desc = signal_data["description"]

            diagram += f"""
{system_type.value.upper():>12}: {glyph} {signal}
             {desc}"""

        diagram += f"""

RITUAL SEQUENCE: {' → '.join(chiasmus['ritual_sequence'])}

{chiasmus['description']}

✨ Each blink, breath, and brace becomes a coordinated signal
   across all five systems - composing emotional harmony.
"""

        return diagram

    def create_brain_region_glyph_map(self, brain_region: str) -> str:
        """
        Create a glyph map showing how a brain region expresses across systems.
        """
        region = self.system.get_brain_region(brain_region)
        if not region:
            return f"❌ Brain region '{brain_region}' not found."

        diagram = f"""
FP {region.name.upper()} GLYPH MAP
{'=' * 50}

{region.description}

GLYPH SEQUENCES BY SYSTEM:
"""

        for system_type, glyphs in region.glyph_sequences.items():
            glyph_sequence = " → ".join(glyphs)
            diagram += f"""
{system_type.value.upper():>12}: {glyph_sequence}"""

        diagram += """

RITUAL MAPPINGS:
"""
        for ritual, description in region.ritual_mappings.items():
            diagram += f"""
• {ritual.upper()}: {description}"""

        diagram += f"""

NEURAL FUNCTIONS: {', '.join([f.value for f in region.functions])}
"""

        return diagram

    def create_neural_ritual_flowchart(self) -> str:
        """
        Create a flowchart showing the neural-to-ritual transformation.
        """
        flowchart = """
FP NEURAL-TO-RITUAL FLOWCHART
{'=' * 50}

NEURAL FUNCTIONS → RITUAL SCAFFOLDING → GLYPH SYSTEMS

┌─────────────────┐
│   BRAIN INPUT   │
│                 │
│  • Insula       │
│  • Amygdala     │
│  • Hippocampus  │
│  • ACC          │
│  • vmPFC        │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ NEURAL FUNCTIONS│
│                 │
│  • REFLEX       │
│  • MEMORY       │
│  • REGULATION   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ RITUAL SCAFFOLD │
│                 │
│  • BLINK        │ ← Boundary signal
│  • BREATH       │ ← Pacing tool
│  • BRACE        │ ← Resilience builder
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   GLYPH SYSTEMS │
│                 │
│  • Lightpath    │ ← Awakening
│  • Threshold    │ ← Assessment
│  • VELΩNIX      │ ← Processing
│  • Velinor      │ ← Growth
│  • Saonyx       │ ← Value
└─────────────────┘

✨ CHIASMUS: One feeling becomes five signals
   The nervous system composes, it doesn't just react.
"""

        return flowchart

    def create_system_harmonics_diagram(self, emotion: str) -> str:
        """
        Create a harmonics diagram showing system interactions.
        """
        system_signals = self.system.map_emotion_to_systems(emotion)

        diagram = f"""
🎵 SYSTEM HARMONICS: {emotion.upper()}
{'=' * 50}

HARMONIC INTERACTIONS:
"""

        # Create a simple harmonics visualization
        systems = list(system_signals.keys())
        for i, system1 in enumerate(systems):
            for j, system2 in enumerate(systems):
                if i < j:  # Only show each pair once
                    sig1 = system_signals[system1]
                    sig2 = system_signals[system2]

                    diagram += f"""
{system1.value[:3].upper()}+{system2.value[:3].upper()}: {sig1['glyph']}{sig2['glyph']} {sig1['signal']} × {sig2['signal']}"""

        diagram += """

INDIVIDUAL CONTRIBUTIONS:
"""
        for system_type, signal_data in system_signals.items():
            diagram += f"""
{system_type.value.upper():>12}: {signal_data['glyph']} {signal_data['signal']}"""

        diagram += """

🎼 The five systems create emotional harmony through coordinated signaling.
   Each system contributes its unique resonance to the emotional symphony.
"""

        return diagram

    def export_visualizations(
        self, emotion: str = "joy", output_dir: str = "emotional_os/glyphs/visualizations"
    ) -> Dict[str, str]:
        """
        Export all visualizations for a given emotion.
        """
        os.makedirs(output_dir, exist_ok=True)

        visualizations = {
            "chiasmus_diagram": self.create_emotion_chiasmus_diagram(emotion),
            "brain_region_maps": {
                region: self.create_brain_region_glyph_map(region)
                for region in ["insula", "amygdala", "hippocampus", "acc", "vmpfc"]
            },
            "neural_flowchart": self.create_neural_ritual_flowchart(),
            "harmonics_diagram": self.create_system_harmonics_diagram(emotion),
        }

        # Save to files
        for name, content in visualizations.items():
            if isinstance(content, str):
                filename = f"{output_dir}/{emotion}_{name}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Saved {filename}")
            elif isinstance(content, dict):
                for sub_name, sub_content in content.items():
                    filename = f"{output_dir}/{emotion}_{name}_{sub_name}.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(sub_content)
                    print(f"✅ Saved {filename}")

        return visualizations


def demo_limbic_visualizer():
    """Demo the limbic visualizer."""
    visualizer = LimbicVisualizer()

    print("FP Limbic-Adjacent System Visualizer Demo")
    print("=" * 60)

    # Show emotion chiasmus
    print("\n🌈 Emotion Chiasmus (Joy):")
    print(visualizer.create_emotion_chiasmus_diagram("joy"))

    # Show brain region map
    print("\nFP Insula Glyph Map:")
    print(visualizer.create_brain_region_glyph_map("insula"))

    # Show neural flowchart
    print("\n📊 Neural-to-Ritual Flowchart:")
    print(visualizer.create_neural_ritual_flowchart())

    # Show harmonics
    print("\n🎵 System Harmonics (Fear):")
    print(visualizer.create_system_harmonics_diagram("fear"))

    print("\n✅ Visualizer demo complete!")


if __name__ == "__main__":
    demo_limbic_visualizer()
