"""
Velinor Streamlit Integration Test
===================================

Quick validation that all components work together.
"""

from velinor.streamlit_ui import StreamlitUI
from velinor.streamlit_state import StreamlitGameState
from velinor.stories.story_definitions import build_velinor_story
from velinor.engine.npc_system import NPCDialogueSystem
from velinor.engine.core import VelinorEngine
from velinor.engine.orchestrator import VelinorTwineOrchestrator
import sys
from pathlib import Path

# Add parent of velinor directory to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_story_building():
    """Test that story builds without errors."""
    print("Testing story building...")
    story = build_velinor_story()
    assert story.story_data is not None
    assert len(story.story_data['passages']) > 0
    print(f"✅ Story built: {len(story.story_data['passages'])} passages")


def test_game_state():
    """Test that game state initializes correctly."""
    print("\nTesting game state...")
    state = StreamlitGameState()
    assert state.mode == "narrative"
    assert len(state.glyphs) > 0
    assert len(state.npc_perception) > 0
    print(
        f"✅ Game state initialized: {len(state.glyphs)} glyphs, {len(state.npc_perception)} NPCs")


def test_tone_effects():
    """Test that tone effects work."""
    print("\nTesting tone effects...")
    state = StreamlitGameState()
    initial_trust = state.tone.trust
    state.apply_tone_effect({"trust": 0.5, "empathy": -0.2})
    assert state.tone.trust > initial_trust
    print(
        f"✅ Tone effects applied: Trust {initial_trust} → {state.tone.trust}")


def test_glyph_operations():
    """Test glyph collection and usage."""
    print("\nTesting glyph operations...")
    state = StreamlitGameState()

    # Obtain a glyph
    assert state.obtain_glyph("Sorrow")
    assert "Sorrow" in state.get_obtained_glyphs()
    print(f"✅ Glyph obtained: {state.get_obtained_glyphs()}")

    # Use at door
    assert state.use_glyph_at_door("Sorrow")
    assert "Sorrow" in state.glyphs_used_at_door
    print(f"✅ Glyph used at door: {state.glyphs_used_at_door}")


def test_npc_perception():
    """Test NPC perception tracking."""
    print("\nTesting NPC perception...")
    state = StreamlitGameState()

    initial_trust = state.npc_perception["Ravi"].trust
    state.update_npc_perception("Ravi", trust_delta=0.3, emotion="warm")

    assert state.npc_perception["Ravi"].trust > initial_trust
    assert state.npc_perception["Ravi"].emotion == "warm"
    print(
        f"✅ NPC perception updated: Ravi trust {initial_trust} → {state.npc_perception['Ravi'].trust}")


def test_ui_components():
    """Test that UI components instantiate."""
    print("\nTesting UI components...")
    ui = StreamlitUI()
    assert ui.backgrounds_path is not None
    assert ui.npcs_path is not None
    print(f"✅ UI components initialized")


def test_game_engine():
    """Test that game engine initializes."""
    print("\nTesting game engine...")

    # First build and export a story
    story = build_velinor_story()
    story_path = "/tmp/velinor_test_story.json"
    story.export_json(story_path)

    game_engine = VelinorEngine()
    game_engine.create_session(player_name="TestPlayer")
    npc_system = NPCDialogueSystem()
    orchestrator = VelinorTwineOrchestrator(
        game_engine=game_engine,
        story_path=story_path,
        npc_system=npc_system,
        player_name="TestPlayer"
    )
    assert orchestrator is not None
    print(f"✅ Game engine and orchestrator initialized")


def test_serialization():
    """Test that game state serializes."""
    print("\nTesting serialization...")
    state = StreamlitGameState()
    state.obtain_glyph("Sorrow")
    state.apply_tone_effect({"trust": 0.3})

    serialized = state.to_dict()
    assert serialized is not None
    assert "tone" in serialized
    assert "glyphs" in serialized
    print(f"✅ Game state serialized: {len(str(serialized))} bytes")


if __name__ == "__main__":
    print("=" * 60)
    print("VELINOR STREAMLIT INTEGRATION TEST")
    print("=" * 60)

    try:
        test_story_building()
        test_game_state()
        test_tone_effects()
        test_glyph_operations()
        test_npc_perception()
        test_ui_components()
        test_game_engine()
        test_serialization()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nYou can now run:")
        print("  streamlit run velinor/streamlit_app.py")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
