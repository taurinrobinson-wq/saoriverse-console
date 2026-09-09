#!/usr/bin/env python3
"""
Convert old dialogue JSON format to new beats format.

Old format has:
- Missing beat_type
- tone_str, npcResponse, etc.
- tone_effects as {entries: [...]}

New format needs:
- beat_type field
- tone, label, npc_response, result_text
- tone_effects as array
"""

import json
import os
import sys

TONE_LABELS = {
    "Trust": "T",
    "Observation": "O",
    "NarrativePresence": "N",
    "Empathy": "E"
}

def convert_beat(beat):
    """Convert a single beat to new format."""
    
    # Add beat_type if missing
    if "beat_type" not in beat:
        # Infer beat_type from active_speaker and choices
        has_choices = beat.get("choices") and len(beat["choices"]) > 0
        speaker = beat.get("active_speaker", "")
        
        if speaker == "System":
            beat["beat_type"] = "npc_shared"
        elif speaker == "Player" and not has_choices:
            beat["beat_type"] = "player_inner"
        elif speaker == "Player" and has_choices:
            beat["beat_type"] = "player_posture"
        elif has_choices:
            beat["beat_type"] = "npc_turn"
        else:
            beat["beat_type"] = "npc_shared"
    
    # Add active_speaker if missing or empty
    if not beat.get("active_speaker") and "name" in beat:
        # Extract speaker name from beat name if no active_speaker
        beat_name = beat["name"].strip()
        # Use first word of name as speaker (e.g., "Older Woman in the Desert" -> "Older")
        speaker = beat_name.split()[0] if beat_name else "Unknown"
        beat["active_speaker"] = speaker
    elif not beat.get("active_speaker"):
        # Default to character name or system
        beat["active_speaker"] = "NPC"
    
    # Convert choices if they use old format
    if "choices" in beat and beat["choices"]:
        new_choices = []
        for choice in beat["choices"]:
            new_choice = convert_choice(choice)
            new_choices.append(new_choice)
        beat["choices"] = new_choices
    
    return beat


def convert_choice(choice):
    """Convert a single choice from old format to new."""
    new_choice = {}
    
    # tone_str -> tone (first letter)
    if "tone_str" in choice:
        tone_str = choice["tone_str"]
        if tone_str and len(tone_str) > 0:
            new_choice["tone"] = TONE_LABELS.get(tone_str, tone_str[0])
            new_choice["label"] = tone_str  # Use full name as label
        else:
            # Empty tone_str - default to Trust
            new_choice["tone"] = "T"
            new_choice["label"] = "Trust"
    elif "tone" in choice:
        new_choice["tone"] = choice["tone"]
        # Infer label from tone if not present
        if "label" not in choice:
            reverse_labels = {v: k for k, v in TONE_LABELS.items()}
            new_choice["label"] = reverse_labels.get(choice["tone"], choice["tone"])
    else:
        # No tone field at all - error case
        new_choice["tone"] = "T"
        new_choice["label"] = "Unknown"
    # playerLine stays the same
    if "playerLine" in choice:
        new_choice["playerLine"] = choice["playerLine"]
    
    # npcResponse -> npc_response
    if "npcResponse" in choice:
        new_choice["npc_response"] = choice["npcResponse"]
    elif "npc_response" in choice:
        new_choice["npc_response"] = choice["npc_response"]
    else:
        new_choice["npc_response"] = ""
    
    # Add result_text if missing
    if "result_text" not in choice:
        new_choice["result_text"] = ""
    else:
        new_choice["result_text"] = choice["result_text"]
    
    # target stays the same
    if "target" in choice:
        new_choice["target"] = choice["target"]
    
    # Convert tone_effects from dict format to array
    if "tone_effects" in choice:
        if isinstance(choice["tone_effects"], dict) and "entries" in choice["tone_effects"]:
            # Old format: {"entries": [{"key": "Trust", "value": 0.02}]}
            entries = choice["tone_effects"]["entries"]
            new_effects = []
            for entry in entries:
                new_effects.append({
                    "stat": entry["key"].lower(),
                    "delta": entry["value"]
                })
            new_choice["tone_effects"] = new_effects
        else:
            # Already in new format
            new_choice["tone_effects"] = choice["tone_effects"]
    else:
        new_choice["tone_effects"] = []
    
    # remnants_effects should already be in correct format
    if "remnants_effects" in choice:
        new_choice["remnants_effects"] = choice["remnants_effects"]
    else:
        new_choice["remnants_effects"] = []
    
    # Keep npc_resonance if present
    if "npc_resonance" in choice:
        new_choice["npc_resonance"] = choice["npc_resonance"]
    
    return new_choice


def convert_file(filepath):
    """Convert a dialogue file."""
    print(f"\nProcessing: {os.path.basename(filepath)}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert all beats
        if "passages" in data:
            new_passages = []
            for beat in data["passages"]:
                new_beat = convert_beat(beat)
                new_passages.append(new_beat)
            data["passages"] = new_passages
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  [OK] Converted {len(data['passages'])} beats")
        return True
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    """Convert all problem files."""
    files = [
        r"C:\saoriverse-console\Velinor-Unity\Assets\Resources\velinor\stories\ravi_encounter_01.json",
        r"C:\saoriverse-console\Velinor-Unity\Assets\Resources\velinor\stories\nima_encounter_02.json",
        r"C:\saoriverse-console\Velinor-Unity\Assets\Resources\velinor\stories\saori_desert_encounter_01.json"
    ]
    
    print("=" * 60)
    print("Converting Dialogue JSON Files to New Format")
    print("=" * 60)
    
    success_count = 0
    for filepath in files:
        if os.path.exists(filepath):
            if convert_file(filepath):
                success_count += 1
        else:
            print(f"\n[ERROR] File not found: {filepath}")
    
    print(f"\n{'=' * 60}")
    print(f"[OK] Conversion complete: {success_count}/{len(files)} files converted")
    print("=" * 60)


if __name__ == "__main__":
    main()
