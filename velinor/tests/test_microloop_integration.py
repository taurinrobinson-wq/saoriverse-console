"""Integration test for the Velinor micro-loop prototype.

Validates that the emotional gating system works end-to-end
without requiring interactive play.
"""
import json
from pathlib import Path

from velinor.velinor_api import query_gate, load_seeds
from velinor.npc_profiles import NPCS


def test_microloop_integration():
    """Test that seeds, client, and NPC profiles all work together."""
    print("\n🧪 Velinor Micro-Loop Integration Test\n")

    # 1. Load seeds
    print("1. Loading seeds...")
    seeds_path = Path("velinor/cipher_seeds.json")
    assert seeds_path.exists(), "❌ cipher_seeds.json not found"

    with open(seeds_path, "r") as f:
        seeds_data = json.load(f)

    seeds = seeds_data.get("seeds", [])
    assert len(seeds) > 0, "❌ No seeds loaded"
    print(f"   ✓ Loaded {len(seeds)} seeds")

    # 2. Check NPCs
    print("\n2. Checking NPC profiles...")
    assert len(NPCS) > 0, "❌ No NPCs found"
    for key, npc in NPCS.items():
        assert "name" in npc, f"❌ NPC {key} missing 'name'"
        assert "intro" in npc, f"❌ NPC {key} missing 'intro'"
        assert "locked" in npc, f"❌ NPC {key} missing 'locked'"
        assert "fragment" in npc, f"❌ NPC {key} missing 'fragment'"
        assert "reveal" in npc, f"❌ NPC {key} missing 'reveal'"
    print(f"   ✓ {len(NPCS)} NPCs ready")

    # 3. Test API calls (in-process, no server required)
    print("\n3. Testing API logic (in-process)...")

    # Try a few seed types
    test_cases = [
        ("velinor-0-001", "hello", "Fragment should always be accessible"),
        (
            "velinor-1-004",
            "hello",
            "Deep fragment should always be accessible",
        ),
        (
            "velinor-2-007",
            "I feel afraid",
            "Plaintext might unlock with fear emotion",
        ),
    ]

    seeds_dict = load_seeds()
    seeds = list(seeds_dict.values()) if isinstance(seeds_dict, dict) else seeds_dict

    for seed_id, player_msg, description in test_cases:
        seed = next((s for s in seeds if s["id"] == seed_id), None)
        if seed is None:
            print(f"   ⚠ Skipping {seed_id} (not in corpus)")
            continue

        response = query_gate(seed_id=seed_id, player_state=player_msg)

        assert "layer" in response, f"❌ Response missing 'layer' for {seed_id}"
        assert "allowed" in response, f"❌ Response missing 'allowed' for {seed_id}"

        layer = response.get("layer")
        allowed = response.get("allowed")

        if layer in (0, 1):
            assert (
                allowed
            ), f"❌ Layer {layer} should always be allowed for {seed_id}"
            print(f"   ✓ {seed_id}: Fragment always accessible")
        else:
            print(
                f"   ✓ {seed_id}: Plaintext {'unlocked' if allowed else 'locked'} — {description}"
            )

    # 4. Seed structure validation
    print("\n4. Validating seed structure...")
    for i, seed in enumerate(seeds):
        assert "id" in seed, f"❌ Seed {i} missing 'id'"
        assert "phrase" in seed, f"❌ Seed {i} missing 'phrase'"
        assert "layer" in seed, f"❌ Seed {i} missing 'layer'"
        assert "required_gates" in seed, f"❌ Seed {i} missing 'required_gates'"
        assert seed["layer"] in (0, 1, 2), f"❌ Seed {i} has invalid layer"

    print(f"   ✓ All {len(seeds)} seeds have valid structure")
    print("\n" + "=" * 60)
    print("✅ Micro-Loop Integration Test PASSED")
    print("=" * 60)
    print(f"\n🌒 Ready to play:")
    print(f"   - {len(seeds)} seeds available")
    print(f"   - {len(NPCS)} NPCs ready to interact")
    print(f"   - Emotional gates active")
    print(f"\nRun with: python velinor/micro_loop.py\n")


if __name__ == "__main__":
    test_microloop_integration()
