#!/usr/bin/env python
"""Quick test to see if REMNANTS imports hang."""
import sys
print("Test starting...", flush=True)
sys.path.insert(0, 'D:/saoriverse-console')

try:
    print("[1/3] Importing npc_manager...", flush=True)
    from velinor.engine.npc_manager import create_marketplace_npcs, create_marketplace_influence_map
    print("[2/3] Creating NPCs...", flush=True)
    npcs = create_marketplace_npcs()
    print(f"[3/3] Created {len(npcs)} NPCs successfully!")
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
