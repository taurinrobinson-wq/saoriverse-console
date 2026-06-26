#!/usr/bin/env python3
"""
Restructure Malrik and Elenya story gates to move present-day acts to beginning.

Current structure:
- Acts 1-4: Pre-collapse (memory)
- Acts 5-8: Present-day

New structure:
- Acts 1-4: Present-day
- Acts 5-8: Pre-collapse (memory)

Mapping:
- Current Acts 5-7 → New Acts 1-3
- Current Act 8 → New Act 4
- Current Acts 1-4 → New Acts 5-8
"""

import json

def restructure_story_gates(input_file, output_file, npc_name):
    """
    Restructure story gates by reordering acts.
    
    Current order: pre-collapse (1-4), present-day (5-8)
    New order: present-day (1-4), pre-collapse (5-8)
    """
    
    # Load the JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract acts
    acts = data['acts']
    print(f"Loaded {len(acts)} acts for {npc_name}")
    
    # Print current structure
    print(f"\nCurrent act structure:")
    for act in acts:
        print(f"  Act {act['actNumber']}: {act['actTitle']} ({act.get('timeframe', '?')})")
    
    # Reorder acts: [5,6,7,8, 1,2,3,4] → [1,2,3,4, 5,6,7,8]
    # This means: acts[4:8] + acts[0:4] (in 0-indexed)
    reordered_acts = acts[4:8] + acts[0:4]
    
    # Update actNumber for each act
    for i, act in enumerate(reordered_acts):
        old_act_num = act['actNumber']
        act['actNumber'] = i + 1
        print(f"\nUpdating Act {old_act_num} → Act {i+1}")
        print(f"  Title: {act['actTitle']}")
        print(f"  Timeframe: {act.get('timeframe', '?')}")
        print(f"  Segments: {len(act['segments'])}")
    
    # Update the acts in the data structure
    data['acts'] = reordered_acts
    
    # Save the restructured JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Restructured {npc_name} acts and saved to {output_file}")
    
    return data

# Process both NPCs
malrik_input = r"d:\saoriverse-console\Velinor-Unity\Assets\Resources\Dialogue\MalrikStoryGates.json"
malrik_output = malrik_input  # Overwrite original

elenya_input = r"d:\saoriverse-console\Velinor-Unity\Assets\Resources\Dialogue\ElenyaStoryGates.json"
elenya_output = elenya_input  # Overwrite original

print("="*60)
print("RESTRUCTURING MALRIK AND ELENYA STORY GATES")
print("="*60)

malrik_data = restructure_story_gates(malrik_input, malrik_output, "Malrik")
elenya_data = restructure_story_gates(elenya_input, elenya_output, "Elenya")

print("\n" + "="*60)
print("NEW ACT STRUCTURE (BOTH NPCS)")
print("="*60)
print("\nMalrik:")
for act in malrik_data['acts']:
    print(f"  Act {act['actNumber']}: {act['actTitle']} ({act.get('timeframe', '?')})")

print("\nElenya:")
for act in elenya_data['acts']:
    print(f"  Act {act['actNumber']}: {act['actTitle']} ({act.get('timeframe', '?')})")

print("\n✅ RESTRUCTURING COMPLETE!")
print("Acts 1-4 are now PRESENT-DAY")
print("Acts 5-8 are now PAST MEMORY")
