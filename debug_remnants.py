"""Quick debug test to verify state capture."""
import sys
from pathlib import Path
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs, create_marketplace_influence_map

# Create manager
manager = NPCManager()
npcs = create_marketplace_npcs()
manager.add_npcs_batch(npcs)
influence_map = create_marketplace_influence_map()
for from_npc, ripples in influence_map.items():
    for to_npc, ripple_value in ripples.items():
        manager.set_influence(from_npc, to_npc, ripple_value)

# WRONG: Shallow copy - remnants dict is shared!
initial_state_wrong = {name: npc.to_dict() for name, npc in manager.npcs.items()}

# CORRECT: Deep copy - fully independent
initial_state_correct = {name: deepcopy(npc.to_dict()) for name, npc in manager.npcs.items()}

print("Test: Are they the same object?")
print(f"  Wrong method: {initial_state_wrong['Kaelen']['remnants'] is manager.npcs['Kaelen'].remnants}")
print(f"  Correct method: {initial_state_correct['Kaelen']['remnants'] is manager.npcs['Kaelen'].remnants}")

print("\nInitial Kaelen empathy (correct method):", initial_state_correct["Kaelen"]["remnants"]["empathy"])

# Run ONE empathetic encounter
encounters = [
    {"empathy": 0.3, "trust": 0.2},
]

manager.simulate_encounters(encounters)

print("\nAfter encounter:")
print("  Kaelen empathy (current):", manager.npcs["Kaelen"].remnants["empathy"])
print("  Kaelen empathy (initial from wrong method):", initial_state_wrong["Kaelen"]["remnants"]["empathy"])
print("  Kaelen empathy (initial from correct method):", initial_state_correct["Kaelen"]["remnants"]["empathy"])

print("\nDelta from correct initial state:", 
      manager.npcs["Kaelen"].remnants["empathy"] - initial_state_correct["Kaelen"]["remnants"]["empathy"])


