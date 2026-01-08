#!/usr/bin/env python3
from emotional_os.learning.archetype_response_generator_v2 import ArchetypeResponseGeneratorV2

turn1 = "I feel fragile today, like even small things overwhelm me. Work has been relentless lately—this week alone I've felt pummeled by back-to-back client meetings and impossible deadlines."
turn3 = "It's not even the hours, honestly. I could handle that. It's that I feel like I'm drowning in something without a clear anchor. I don't know if the work means anything anymore. Like... what's it all for? I used to care about advocacy—helping people navigate complex legal systems—but now I feel like I'm just grinding through."
turn5 = "That's the thing. I lost sight of why it mattered in the first place. The advocacy part used to feel fulfilling, but now I'm just drowning out everything else. I've had this little creative spark lately—I've been thinking about art, about making things—but I feel guilty for even considering that when I'm supposed to be focused on the work."

print("=" * 80)
print("RESPONSE GENERATION TEST - NEW GENERATOR (V2)")
print("=" * 80)

print("\n--- SCENARIO 2 DIALOGUE (6-turn simplified to 3 turns) ---\n")

for run in range(1, 4):
    print(f"\n{'='*80}")
    print(f"RUN {run}")
    print(f"{'='*80}\n")
    
    gen = ArchetypeResponseGeneratorV2()
    
    print("TURN 1 - OVERWHELM:")
    print(f"User: {turn1[:70]}...")
    resp1 = gen.generate_archetype_aware_response(turn1, None)
    print(f"Response: {resp1}\n")
    
    gen.recent_closings = []
    gen.recent_openings = []
    
    prior = turn1[:100]
    print("TURN 3 - EXISTENTIAL:")
    print(f"User: {turn3[:70]}...")
    resp3 = gen.generate_archetype_aware_response(turn3, prior)
    print(f"Response: {resp3}\n")
    
    gen.recent_closings = []
    gen.recent_openings = []
    
    print("TURN 5 - CREATIVE:")
    print(f"User: {turn5[:70]}...")
    resp5 = gen.generate_archetype_aware_response(turn5, turn3[:100])
    print(f"Response: {resp5}\n")
