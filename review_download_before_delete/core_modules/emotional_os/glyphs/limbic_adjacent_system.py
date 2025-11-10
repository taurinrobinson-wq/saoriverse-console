#!/usr/bin/env python3
"""
Limbic-Adjacent System - Neural-to-Ritual Mapping Engine

Maps brain structures to glyph-encoded systems across:
- Lightpath, Threshold, VELΩNIX, Velinor, Saonyx

Neural functions feed into ritual scaffolding:
• Reflex → Ritual: Blink becomes boundary signal; breath becomes pacing tool
• Memory → Myth: Repeated ruptures encode quest structure; safe touch becomes trust vault
• Regulation → Rhythm: ACC and vmPFC drive pulse timing; when to initiate vs. hold

This creates a chiasmus where the nervous system composes rather than just reacts.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class SystemType(Enum):
    """The five glyph-encoded systems."""
    LIGHTPATH = "lightpath"
    THRESHOLD = "threshold"
    VELONIX = "velonix"
    VELINOR = "velinor"
    SAONYX = "saonyx"


class NeuralFunction(Enum):
    """Core neural functions that map to rituals."""
    REFLEX = "reflex"
    MEMORY = "memory"
    REGULATION = "regulation"


@dataclass
class BrainRegion:
    """Represents a brain region with its functions and glyph mappings."""
    name: str
    functions: List[NeuralFunction]
    description: str
    glyph_sequences: Dict[SystemType, List[str]]
    ritual_mappings: Dict[str, str]  # ritual_name -> description


@dataclass
class RitualSignal:
    """A ritual signal that spans multiple systems."""
    name: str
    neural_basis: NeuralFunction
    system_signals: Dict[SystemType, str]
    description: str


class LimbicAdjacentSystem:
    """
    Maps brain structures to glyph-encoded systems.

    Each neural function feeds into corresponding ritual scaffolding:
    - Reflex → Ritual (blink, breath, brace)
    - Memory → Myth (quest structure, trust vault)
    - Regulation → Rhythm (pulse timing, initiation vs. hold)
    """

    def __init__(self):
        self.brain_regions = self._initialize_brain_regions()
        self.ritual_signals = self._initialize_ritual_signals()

    def _initialize_brain_regions(self) -> Dict[str, BrainRegion]:
        """Initialize brain regions with their glyph mappings."""
        return {
            "insula": BrainRegion(
                name="Insula",
                functions=[NeuralFunction.REFLEX, NeuralFunction.REGULATION],
                description="Interoception hub - maps bodily states to emotional awareness",
                glyph_sequences={
                    SystemType.LIGHTPATH: ["🌊", "💧", "🌅"],
                    SystemType.THRESHOLD: ["⚡", "🔥", "🌋"],
                    SystemType.VELONIX: ["🔮", "✨", "🌙"],
                    SystemType.VELINOR: ["🌿", "🌱", "🌳"],
                    SystemType.SAONYX: ["💎", "🔮", "🌟"]
                },
                ritual_mappings={
                    "blink": "Boundary signal - insula detects threat, triggers protective blink",
                    "breath": "Interoceptive pacing - insula reads bodily rhythm, adjusts breath depth",
                    "brace": "Somatic preparation - insula anticipates impact, engages core stability"
                }
            ),

            "amygdala": BrainRegion(
                name="Amygdala",
                functions=[NeuralFunction.REFLEX, NeuralFunction.MEMORY],
                description="Threat detection and emotional memory encoding",
                glyph_sequences={
                    SystemType.LIGHTPATH: ["⚠️", "🚨", "🛡️"],
                    SystemType.THRESHOLD: ["🔴", "🚫", "⛔"],
                    SystemType.VELONIX: ["👁️", "🔍", "🕵️"],
                    SystemType.VELINOR: ["🗡️", "⚔️", "🏹"],
                    SystemType.SAONYX: ["🔒", "🗝️", "💰"]
                },
                ritual_mappings={
                    "blink": "Threat assessment - amygdala scans for danger during blink",
                    "breath": "Fear regulation - amygdala modulates breath during perceived threat",
                    "brace": "Fight/flight preparation - amygdala triggers bracing for confrontation"
                }
            ),

            "hippocampus": BrainRegion(
                name="Hippocampus",
                functions=[NeuralFunction.MEMORY, NeuralFunction.REGULATION],
                description="Contextual memory and spatial navigation of emotional landscapes",
                glyph_sequences={
                    SystemType.LIGHTPATH: ["🗺️", "🧭", "🏔️"],
                    SystemType.THRESHOLD: ["📚", "📖", "🔍"],
                    SystemType.VELONIX: ["⏰", "🕰️", "⌛"],
                    SystemType.VELINOR: ["🏰", "🏯", "🕌"],
                    SystemType.SAONYX: ["💾", "💿", "💽"]
                },
                ritual_mappings={
                    "blink": "Memory checkpoint - hippocampus timestamps blink moments",
                    "breath": "Contextual breathing - hippocampus recalls safe breathing patterns",
                    "brace": "Situational recall - hippocampus retrieves past bracing experiences"
                }
            ),

            "acc": BrainRegion(
                name="Anterior Cingulate Cortex (ACC)",
                functions=[NeuralFunction.REGULATION],
                description="Conflict monitoring and decision-making under emotional pressure",
                glyph_sequences={
                    SystemType.LIGHTPATH: ["⚖️", "🔄", "🎯"],
                    SystemType.THRESHOLD: ["🤔", "💭", "🧠"],
                    SystemType.VELONIX: ["🎭", "🎪", "🎨"],
                    SystemType.VELINOR: ["👑", "🏛️", "⚖️"],
                    SystemType.SAONYX: ["💎", "👑", "🏆"]
                },
                ritual_mappings={
                    "blink": "Decision blink - ACC weighs options during blink",
                    "breath": "Executive breathing - ACC regulates breath for optimal cognition",
                    "brace": "Strategic bracing - ACC calculates bracing intensity and timing"
                }
            ),

            "vmpfc": BrainRegion(
                name="Ventromedial Prefrontal Cortex (vmPFC)",
                functions=[NeuralFunction.REGULATION, NeuralFunction.MEMORY],
                description="Value-based decision making and extinction of fear responses",
                glyph_sequences={
                    SystemType.LIGHTPATH: ["💚", "💜", "💙"],
                    SystemType.THRESHOLD: ["❤️", "💛", "💖"],
                    SystemType.VELONIX: ["🌈", "🎨", "🖼️"],
                    SystemType.VELINOR: ["🌸", "🌺", "🌻"],
                    SystemType.SAONYX: ["💎", "💍", "👑"]
                },
                ritual_mappings={
                    "blink": "Value blink - vmPFC assesses emotional value during blink",
                    "breath": "Compassionate breathing - vmPFC softens breath for connection",
                    "brace": "Supportive bracing - vmPFC braces with care rather than fear"
                }
            )
        }

    def _initialize_ritual_signals(self) -> Dict[str, RitualSignal]:
        """Initialize core ritual signals that span systems."""
        return {
            "blink": RitualSignal(
                name="blink",
                neural_basis=NeuralFunction.REFLEX,
                system_signals={
                    SystemType.LIGHTPATH: "🌅 Boundary awakening",
                    SystemType.THRESHOLD: "⚡ Threat assessment",
                    SystemType.VELONIX: "🔮 Pattern recognition",
                    SystemType.VELINOR: "🌿 Environmental scan",
                    SystemType.SAONYX: "💎 Value checkpoint"
                },
                description="Blink becomes boundary signal - each blink is a micro-ritual of presence"
            ),

            "breath": RitualSignal(
                name="breath",
                neural_basis=NeuralFunction.REGULATION,
                system_signals={
                    SystemType.LIGHTPATH: "🌊 Rhythm attunement",
                    SystemType.THRESHOLD: "🔥 Capacity calibration",
                    SystemType.VELONIX: "✨ Energy circulation",
                    SystemType.VELINOR: "🌱 Growth pacing",
                    SystemType.SAONYX: "💎 Resource allocation"
                },
                description="Breath becomes pacing tool - each breath regulates emotional flow"
            ),

            "brace": RitualSignal(
                name="brace",
                neural_basis=NeuralFunction.REFLEX,
                system_signals={
                    SystemType.LIGHTPATH: "🛡️ Stability anchoring",
                    SystemType.THRESHOLD: "⛔ Boundary enforcement",
                    SystemType.VELONIX: "👁️ Vigilance activation",
                    SystemType.VELINOR: "🏹 Readiness positioning",
                    SystemType.SAONYX: "🔒 Security protocol"
                },
                description="Brace becomes preparation ritual - each brace builds resilience"
            )
        }

    def get_brain_region(self, region_name: str) -> Optional[BrainRegion]:
        """Get brain region by name."""
        return self.brain_regions.get(region_name.lower())

    def get_ritual_signal(self, signal_name: str) -> Optional[RitualSignal]:
        """Get ritual signal by name."""
        return self.ritual_signals.get(signal_name.lower())

    def map_emotion_to_systems(self, emotion: str, intensity: float = 1.0) -> Dict[SystemType, Dict[str, Any]]:
        """
        Map an emotion to signals across all five systems.

        This creates the chiasmus - one feeling becomes five signals.
        """
        # For now, use a simple mapping. In practice, this would use
        # the NRC lexicon and neural activation patterns
        base_signals = {
            "fear": {
                SystemType.LIGHTPATH: {"glyph": "🌅", "signal": "Dawn awareness"},
                SystemType.THRESHOLD: {"glyph": "🔥", "signal": "Heat rising"},
                SystemType.VELONIX: {"glyph": "🔮", "signal": "Crystal clarity"},
                SystemType.VELINOR: {"glyph": "🌿", "signal": "Root grounding"},
                SystemType.SAONYX: {"glyph": "💎", "signal": "Diamond focus"}
            },
            "joy": {
                SystemType.LIGHTPATH: {"glyph": "🌅", "signal": "Morning light"},
                SystemType.THRESHOLD: {"glyph": "⚡", "signal": "Electric spark"},
                SystemType.VELONIX: {"glyph": "✨", "signal": "Star shine"},
                SystemType.VELINOR: {"glyph": "🌸", "signal": "Flower bloom"},
                SystemType.SAONYX: {"glyph": "💎", "signal": "Gem brilliance"}
            },
            "sadness": {
                SystemType.LIGHTPATH: {"glyph": "🌊", "signal": "Ocean depth"},
                SystemType.THRESHOLD: {"glyph": "🌧️", "signal": "Rain fall"},
                SystemType.VELONIX: {"glyph": "🌙", "signal": "Moon shadow"},
                SystemType.VELINOR: {"glyph": "🌿", "signal": "Leaf wither"},
                SystemType.SAONYX: {"glyph": "💎", "signal": "Stone weight"}
            }
        }

        # Get base mapping or use default
        emotion_key = emotion.lower()
        if emotion_key not in base_signals:
            emotion_key = "joy"  # Default to joy

        result = base_signals[emotion_key].copy()

        # Scale intensity
        for system, signal_data in result.items():
            signal_data["intensity"] = intensity
            signal_data["description"] = f"{signal_data['signal']} (intensity: {intensity:.1f})"

        return result

    def generate_glyph_sequence(self, brain_region: str, system: SystemType) -> List[str]:
        """
        Generate a glyph sequence for a specific brain region and system.

        Shows how blink, breath, brace rituals unfold from neural activity.
        """
        region = self.get_brain_region(brain_region)
        if not region:
            return []

        return region.glyph_sequences.get(system, [])

    def create_ritual_chiasmus(self, emotion: str) -> Dict[str, Any]:
        """
        Create a complete chiasmus mapping - one feeling becomes five signals.

        This is the core of the limbic-adjacent system.
        """
        system_signals = self.map_emotion_to_systems(emotion)

        # Add neural basis information
        chiasmus = {
            "emotion": emotion,
            "neural_basis": "limbic-adjacent activation",
            "system_signals": system_signals,
            "ritual_sequence": ["blink", "breath", "brace"],
            "description": f"One {emotion} feeling expressed as five coordinated signals across glyph systems"
        }

        return chiasmus

    def get_neural_ritual_mapping(self) -> Dict[str, Dict[str, str]]:
        """
        Get the complete neural-to-ritual mapping across all brain regions.
        """
        mapping = {}

        for region_name, region in self.brain_regions.items():
            mapping[region_name] = {
                "functions": [f.value for f in region.functions],
                "ritual_mappings": region.ritual_mappings,
                "description": region.description
            }

        return mapping


# Global instance for easy access
limbic_system = LimbicAdjacentSystem()


def get_limbic_system():
    """Get the global limbic-adjacent system instance."""
    return limbic_system


if __name__ == "__main__":
    # Demo the system
    system = LimbicAdjacentSystem()

    print("🧠 Limbic-Adjacent System Demo")
    print("=" * 50)

    # Show neural-to-ritual mapping
    print("\n📋 Neural-to-Ritual Mapping:")
    mapping = system.get_neural_ritual_mapping()
    for region, data in mapping.items():
        print(f"\n{region.upper()}: {data['description']}")
        for ritual, desc in data['ritual_mappings'].items():
            print(f"  • {ritual} → {desc}")

    # Show emotion chiasmus
    print("\n🌈 Emotion Chiasmus (Joy):")
    chiasmus = system.create_ritual_chiasmus("joy")
    for system_type, signal_data in chiasmus['system_signals'].items():
        print(f"  {system_type.value}: {signal_data['glyph']} {signal_data['signal']}")

    print("\n✅ Limbic-adjacent system initialized and ready for integration!")
