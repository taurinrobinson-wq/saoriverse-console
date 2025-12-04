"""Training Corpus Pipeline for Glyph-Controlled Fine-Tuning.

Converts glyph responses and user interactions into JSONL training format
with control tags, gates, and style metadata.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
import json
import logging
from datetime import datetime

from glyph_lm_control import Glyph, GatePolicy, StyleDirective, GLYPH_REGISTRY


logger = logging.getLogger(__name__)


@dataclass
class TrainingExample:
    """Single training example with full control context."""
    id: str
    context: str                           # User's situation/background
    prompt: str                            # User input
    response: str                          # Generated response
    glyphs: List[Dict[str, Any]]          # [{"name": str, "intensity": float}]
    # {uncanny_ok, safety_bias, directness}
    gates: Dict[str, Any]
    # {register, rhythm, metaphor_density}
    style: Dict[str, Any]
    lexicon_tags: List[str]               # Semantic anchors
    user_satisfaction: Optional[float] = None  # Feedback score 0.0-1.0
    metadata: Dict[str, Any] = None       # Additional context

    def to_jsonl_line(self) -> str:
        """Serialize to JSONL line."""
        return json.dumps(asdict(self)) + "\n"


class TrainingCorpusBuilder:
    """Builds training corpus from glyphs and interactions."""

    def __init__(self):
        """Initialize builder."""
        self.examples: List[TrainingExample] = []
        self._id_counter = 0

    def add_from_interaction(
        self,
        user_input: str,
        response: str,
        glyphs: List[Tuple[Glyph, float]],  # (glyph, intensity)
        gates: GatePolicy,
        style: StyleDirective,
        context: str = "",
        lexicon_tags: Optional[List[str]] = None,
        user_satisfaction: Optional[float] = None,
    ) -> TrainingExample:
        """Add training example from real interaction.

        Args:
            user_input: User's input text
            response: System response
            glyphs: List of (glyph, intensity) tuples
            gates: Gate policy used
            style: Style directive used
            context: Additional context (user state, situation)
            lexicon_tags: Semantic anchors
            user_satisfaction: User satisfaction rating

        Returns:
            Created TrainingExample
        """
        self._id_counter += 1

        example = TrainingExample(
            id=f"train_{self._id_counter:06d}",
            context=context,
            prompt=user_input,
            response=response,
            glyphs=[
                {"name": g.name, "intensity": intensity}
                for g, intensity in glyphs
            ],
            gates=asdict(gates),
            style=asdict(style),
            lexicon_tags=lexicon_tags or [],
            user_satisfaction=user_satisfaction,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "source": "live_interaction",
            },
        )

        self.examples.append(example)
        return example

    def add_synthetic_expansion(
        self,
        base_glyph: Glyph,
        seed_phrase: str,
        variants: List[str],
        gates: GatePolicy,
        style: StyleDirective,
    ) -> List[TrainingExample]:
        """Add synthetic training examples from glyph seed phrases.

        This creates curriculum-learning examples that gradually expand the
        model's understanding of glyph-to-language mapping.

        Args:
            base_glyph: Base glyph to expand
            seed_phrase: Seed phrase from glyph definition
            variants: Different renderings of the seed phrase
            gates: Gate policy for training
            style: Style directive

        Returns:
            List of created TrainingExamples
        """
        created = []

        for i, variant in enumerate(variants):
            self._id_counter += 1

            example = TrainingExample(
                id=f"synthetic_{self._id_counter:06d}",
                context=f"Training expansion of {base_glyph.name}",
                prompt=seed_phrase,
                response=variant,
                glyphs=[{"name": base_glyph.name,
                         "intensity": base_glyph.attributes.intensity}],
                gates=asdict(gates),
                style=asdict(style),
                lexicon_tags=[
                    base_glyph.attributes.primary_family,
                    base_glyph.attributes.movement.value,
                    str(base_glyph.attributes.rituality),
                ],
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "source": "synthetic_expansion",
                    "base_glyph": base_glyph.name,
                    "variant_index": i,
                },
            )

            self.examples.append(example)
            created.append(example)

        return created

    def add_curriculum_progression(
        self,
        progression: List[Dict[str, Any]],
        gates_schedule: List[GatePolicy],
    ) -> List[TrainingExample]:
        """Add curriculum-learning progression (safe → uncanny).

        Stages: 
            1. Neutral tones (Stillness, Grounded Joy)
            2. Mild emotions (Ache, Mourning)
            3. Strong emotions (Spiral Ache, Euphoric Yearning)
            4. Uncanny content (if gates allow it)

        Args:
            progression: List of dicts with 'prompt', 'response', 'glyphs'
            gates_schedule: GatePolicy for each stage

        Returns:
            List of created examples
        """
        created = []

        for stage_idx, (example_dict, gates) in enumerate(zip(progression, gates_schedule)):
            self._id_counter += 1

            # Parse glyph names to objects
            glyph_names = example_dict.get("glyphs", [])
            glyphs_data = []
            for g_name in glyph_names:
                glyph = GLYPH_REGISTRY.get(g_name)
                if glyph:
                    glyphs_data.append(
                        {"name": glyph.name, "intensity": glyph.attributes.intensity})

            example = TrainingExample(
                id=f"curriculum_{self._id_counter:06d}",
                context=f"Curriculum stage {stage_idx + 1}",
                prompt=example_dict["prompt"],
                response=example_dict["response"],
                glyphs=glyphs_data,
                gates=asdict(gates),
                style=asdict(example_dict.get("style", StyleDirective())),
                lexicon_tags=example_dict.get("lexicon_tags", []),
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "source": "curriculum_progression",
                    "stage": stage_idx + 1,
                },
            )

            self.examples.append(example)
            created.append(example)

        return created

    def to_jsonl(self, path: str):
        """Write corpus to JSONL file.

        Args:
            path: Output file path
        """
        with open(path, 'w') as f:
            for example in self.examples:
                f.write(example.to_jsonl_line())

        logger.info(f"Wrote {len(self.examples)} examples to {path}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get corpus statistics."""
        if not self.examples:
            return {}

        glyph_counts = {}
        avg_satisfaction = 0.0
        satisfaction_count = 0

        for ex in self.examples:
            for g in ex.glyphs:
                glyph_counts[g["name"]] = glyph_counts.get(g["name"], 0) + 1

            if ex.user_satisfaction is not None:
                avg_satisfaction += ex.user_satisfaction
                satisfaction_count += 1

        return {
            "total_examples": len(self.examples),
            "avg_example_length": sum(len(ex.response.split()) for ex in self.examples) / len(self.examples),
            "glyph_distribution": glyph_counts,
            "avg_user_satisfaction": avg_satisfaction / satisfaction_count if satisfaction_count > 0 else None,
            "satisfaction_count": satisfaction_count,
        }


def create_baseline_curriculum() -> List[Dict[str, Any]]:
    """Create baseline curriculum progression for safe → uncanny learning."""

    return [
        # Stage 1: Safe, grounded
        {
            "prompt": "I'm feeling uncertain",
            "response": "Here and enough. The ground of this moment holds you.",
            "glyphs": ["Active Stillness", "Grounded Joy"],
            "style": StyleDirective(register="warm", rhythm="slow", metaphor_density=0.4),
            "lexicon_tags": ["grounding", "presence", "safety"],
        },
        # Stage 2: Mild sorrow
        {
            "prompt": "There's a sadness I can't quite name",
            "response": "Grief that knows your name. The presence of what's gone, held in your body.",
            "glyphs": ["Held Mourning"],
            "style": StyleDirective(register="warm", rhythm="slow", metaphor_density=0.6),
            "lexicon_tags": ["mourning", "tenderness", "presence"],
        },
        # Stage 3: Yearning
        {
            "prompt": "I feel like something is reaching in me",
            "response": "Joy that extends—reaching toward connection, meaning, more. Your aliveness in motion.",
            "glyphs": ["Euphoric Yearning"],
            "style": StyleDirective(register="poetic", rhythm="mixed", metaphor_density=0.7),
            "lexicon_tags": ["aspiration", "connection", "aliveness"],
        },
        # Stage 4: Recursive depth
        {
            "prompt": "I keep coming back to the same feeling",
            "response": "Longing that loops inward—not to collapse but to deepen. Each return visits the same ground with fresher eyes.",
            "glyphs": ["Recursive Ache"],
            "style": StyleDirective(register="poetic", rhythm="contemplative", metaphor_density=0.8),
            "lexicon_tags": ["recursion", "depth", "returning"],
        },
    ]


def create_safe_gate_schedule() -> List[GatePolicy]:
    """Create gate schedule that progresses gradually."""
    return [
        GatePolicy(uncanny_ok=False, safety_bias=1.0,
                   directness=0.3),     # Very safe
        GatePolicy(uncanny_ok=False, safety_bias=0.9,
                   directness=0.4),     # Safe
        GatePolicy(uncanny_ok=False, safety_bias=0.8,
                   directness=0.5),     # Mostly safe
        GatePolicy(uncanny_ok=False, safety_bias=0.7,
                   directness=0.6),     # Cautious
    ]


def create_corpus_from_phase_3_1_data(
    profile_data: List[Dict[str, Any]],
    session_data: List[Dict[str, Any]],
) -> TrainingCorpusBuilder:
    """Create training corpus from Phase 3.1 profile and session data.

    Integrates emotional profiles and session coherence metrics to generate
    realistic training examples.

    Args:
        profile_data: User emotional profiles from Phase 3.1
        session_data: Session transcripts and metrics

    Returns:
        Populated TrainingCorpusBuilder
    """
    builder = TrainingCorpusBuilder()

    # For now, return basic builder
    # In production, would parse profile_data and session_data

    return builder
