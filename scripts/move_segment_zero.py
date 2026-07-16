#!/usr/bin/env python3
"""Move Segment Zero from Act 5 to Act 1 for proper narrative flow."""

import json

def move_segment_zero(json_file, npc_name):
    """Move Segment Zero from Act 5 to beginning of Act 1."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find Segment Zero in Act 5
    act5_segments = data['acts'][4]['segments']  # Act 5 is index 4
    
    seg0 = None
    seg0_index = -1
    for i, seg in enumerate(act5_segments):
        if seg['segmentId'].endswith('_seg0_intro'):
            seg0 = seg.copy()
            seg0_index = i
            break
    
    if seg0 is None:
        print(f"⚠️  No Segment Zero found in Act 5 for {npc_name}")
        return data
    
    print(f"Found Segment Zero in Act 5 for {npc_name}: {seg0['segmentId']}")
    
    # Remove from Act 5
    act5_segments.pop(seg0_index)
    print(f"  Removed from Act 5 (now {len(act5_segments)} segments)")
    
    # Add to beginning of Act 1
    act1_segments = data['acts'][0]['segments']  # Act 1 is index 0
    act1_segments.insert(0, seg0)
    print(f"  Added to Act 1 (now {len(act1_segments)} segments)")
    
    # Save back
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return data

print("="*60)
print("MOVING SEGMENT ZERO TO ACT 1")
print("="*60)

malrik_file = r"d:\saoriverse-console\Velinor-Unity\Assets\Resources\Dialogue\MalrikStoryGates.json"
elenya_file = r"d:\saoriverse-console\Velinor-Unity\Assets\Resources\Dialogue\ElenyaStoryGates.json"

malrik_data = move_segment_zero(malrik_file, "Malrik")
elenya_data = move_segment_zero(elenya_file, "Elenya")

print("\n" + "="*60)
print("NEW ACT SEGMENT COUNTS")
print("="*60)
print("\nMalrik:")
for act in malrik_data['acts']:
    print(f"  Act {act['actNumber']}: {len(act['segments'])} segments")

print("\nElenya:")
for act in elenya_data['acts']:
    print(f"  Act {act['actNumber']}: {len(act['segments'])} segments")

print("\n✅ Segment Zero moved to Act 1!")
