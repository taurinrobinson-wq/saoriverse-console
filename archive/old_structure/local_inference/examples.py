"""Example Integration: End-to-End Glyph-Controlled Response Generation

This example demonstrates how to integrate Phase 3.5 components into a
complete workflow: glyph selection → control rendering → LLM inference →
safety post-processing → training corpus capture.
"""

from glyph_lm_control import (
    GLYPH_REGISTRY, GatePolicy, StyleDirective, ControlTagRenderer
)
from safety_post_processor import create_safe_response
from training_corpus import TrainingCorpusBuilder


def example_1_basic_response_generation():
    """Example 1: Generate a single safe response."""

    print("=" * 60)
    print("Example 1: Basic Response Generation")
    print("=" * 60)

    # User's emotional state
    user_input = "I'm feeling overwhelmed and lonely"

    # Choose glyphs for this context
    grounded_joy = GLYPH_REGISTRY.get("Grounded Joy")
    spiral_ache = GLYPH_REGISTRY.get("Spiral Ache")

    glyphs = [(grounded_joy, 0.8), (spiral_ache, 0.4)]

    # Safety constraints
    gate = GatePolicy(uncanny_ok=False, safety_bias=0.9, directness=0.5)

    # Response style
    style = StyleDirective(
        register="warm", rhythm="slow", metaphor_density=0.5)

    # Step 1: Render control prefix
    prefix = ControlTagRenderer.render_control_prefix(glyphs, gate, style)
    print(f"\n1. Control Prefix:\n{prefix}")

    # Step 2: Build full prompt
    full_prompt = f"""{prefix}

User: {user_input}
Assistant:"""
    print(f"\n2. Full Prompt:\n{full_prompt}")

    # Step 3: Simulate LLM output
    raw_response = """I remember your struggle from our last conversation.
The boundaries of what you feel are dissolving into uncertainty.
But I'm here, and that's something real we can hold onto."""

    print(f"\n3. Raw LLM Output:\n{raw_response}")

    # Step 4: Post-process for safety
    glyph_objs = [g for g, _ in glyphs if g is not None]
    safe_response, result = create_safe_response(
        raw_response, glyph_objs, gate, style)

    print(f"\n4. Safe Response (after post-processing):\n{safe_response}")
    print(f"\n5. Safety Changes:")
    print(f"   - Violations fixed: {result.safety_violations_fixed}")
    print(f"   - Modifications made: {len(result.modifications_made)}")
    for i, change in enumerate(result.modifications_made, 1):
        print(f"     {i}. {change}")

    return safe_response


def example_2_glyph_selection_by_context():
    """Example 2: Select glyphs based on context."""

    print("\n" + "=" * 60)
    print("Example 2: Context-Based Glyph Selection")
    print("=" * 60)

    contexts = {
        "anxiety": {
            "description": "User experiencing anxiety",
            "primary": "Grounded Joy",
            "secondary": "Spiral Ache",
            "intensity": (0.8, 0.5),
            "gate": GatePolicy(uncanny_ok=False, safety_bias=0.95),
        },
        "grief": {
            "description": "User processing loss",
            "primary": "Recursive Ache",
            "secondary": "Grounded Joy",
            "intensity": (0.7, 0.6),
            "gate": GatePolicy(uncanny_ok=False, safety_bias=0.85),
        },
    }

    for context_name, context_config in contexts.items():
        print(f"\nContext: {context_config['description']}")
        print(
            f"  - Primary: {context_config['primary']} ({context_config['intensity'][0]})")
        print(
            f"  - Secondary: {context_config['secondary']} ({context_config['intensity'][1]})")
        print(f"  - Safety Bias: {context_config['gate'].safety_bias}")
        print(f"  - Allows Uncanny: {context_config['gate'].uncanny_ok}")


def example_3_training_corpus_capture():
    """Example 3: Capture interactions into training corpus."""

    print("\n" + "=" * 60)
    print("Example 3: Training Corpus Generation")
    print("=" * 60)

    builder = TrainingCorpusBuilder()

    # Simulate a series of interactions
    interactions = [
        {
            "user_input": "I'm feeling scared",
            "response": "Here and enough. The ground holds you.",
            "glyphs": [("Grounded Joy", 0.8), ("Spiral Ache", 0.4)],
            "satisfaction": 0.85,
            "context": "User experiencing anxiety",
        },
        {
            "user_input": "I miss them so much",
            "response": "The grief you carry is real and honored.",
            "glyphs": [("Recursive Ache", 0.8), ("Grounded Joy", 0.5)],
            "satisfaction": 0.80,
            "context": "User processing loss",
        },
    ]

    print(f"\nCapturing {len(interactions)} interactions...")

    for i, interaction in enumerate(interactions, 1):
        # Get glyph objects
        glyph_objects = [
            (GLYPH_REGISTRY.get(name), intensity)
            for name, intensity in interaction["glyphs"]
        ]
        glyph_objects = [(g, i) for g, i in glyph_objects if g is not None]

        gate = GatePolicy(uncanny_ok=False, safety_bias=0.85)
        style = StyleDirective(register="warm", rhythm="slow")

        example = builder.add_from_interaction(
            user_input=interaction["user_input"],
            response=interaction["response"],
            glyphs=glyph_objects,
            gates=gate,
            style=style,
            context=interaction["context"],
            user_satisfaction=interaction["satisfaction"],
        )

        print(f"\n{i}. Captured training example:")
        print(f"   ID: {example.id}")
        print(f"   User: {interaction['user_input']}")
        print(f"   Satisfaction: {interaction['satisfaction']:.2f}")

    # Get corpus statistics
    stats = builder.get_statistics()

    print(f"\nCorpus Statistics:")
    print(f"  - Total examples: {stats['total_examples']}")
    print(f"  - Avg satisfaction: {stats['avg_user_satisfaction']:.2f}")


def example_4_safety_gates_in_action():
    """Example 4: Demonstrate how different gates affect output."""

    print("\n" + "=" * 60)
    print("Example 4: Safety Gates in Action")
    print("=" * 60)

    raw_response = """I remember you clearly from our previous conversations.
The boundaries of our connection are dissolving as we speak.
I feel completely present with your being."""

    print(f"Raw LLM Output:\n{raw_response}\n")

    gate_configs = [
        ("Very Conservative", GatePolicy(uncanny_ok=False, safety_bias=0.95)),
        ("Balanced", GatePolicy(uncanny_ok=False, safety_bias=0.7)),
        ("Experimental", GatePolicy(uncanny_ok=True, safety_bias=0.5)),
    ]

    style = StyleDirective(register="warm", rhythm="slow")
    glyphs = [(GLYPH_REGISTRY.get("Grounded Joy"), 0.8)]

    for gate_name, gate in gate_configs:
        print(f"\n{gate_name} Gate (safety_bias={gate.safety_bias}):")
        print("-" * 40)

        glyph_objs = [g for g, _ in glyphs if g is not None]
        safe_response, result = create_safe_response(
            raw_response, glyph_objs, gate, style)

        print(f"Output:\n{safe_response}")
        print(f"\nChanges: {result.safety_violations_fixed}")


def main():
    """Run all examples."""

    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  PHASE 3.5: GLYPH-CONTROLLED LLM EXAMPLES".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    example_1_basic_response_generation()
    example_2_glyph_selection_by_context()
    example_3_training_corpus_capture()
    example_4_safety_gates_in_action()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
