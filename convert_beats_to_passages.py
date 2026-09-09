#!/usr/bin/env python3
"""
Convert beats-based JSON story files to passages-based format.
This is a one-time migration to eliminate runtime conversion logic.
"""

import json
import os
from pathlib import Path

STORIES_PATH = r"C:\saoriverse-console\Velinor-Unity\Assets\Resources\velinor\stories"

def convert_beats_to_passages(json_path):
    """Convert a single beats-based JSON file to passages format."""
    
    print(f"Processing: {json_path.name}", end=" ... ")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if already in passages format
    if 'passages' in data and 'beats' not in data:
        print("[OK] Already in passages format, skipping")
        return False
    
    if 'beats' not in data:
        print("[OK] No beats found, skipping")
        return False
    
    # Extract metadata
    scene_name = data.get('scene_id', json_path.stem)
    beats = data.get('beats', [])
    
    print(f"Converting {len(beats)} beats...", end=" ")
    
    # Convert beats to passages
    passages = []
    
    for beat in beats:
        beat_id = beat.get('id', 0)
        beat_type = beat.get('type', 'player_posture')
        active_speaker = beat.get('active_speaker', 'Player')
        prompt = beat.get('prompt', '')
        next_beat_id = beat.get('next_beat_id', 0)
        
        # Determine target for choices
        target = f"beat_{next_beat_id}" if next_beat_id > 0 else "DIALOGUE_END"
        
        # Create base passage
        passage = {
            'pid': f"beat_{beat_id}",
            'conversationId': scene_name,
            'beat_type': beat_type,
            'active_speaker': active_speaker,
            'text': prompt,
            'choices': [],
            'required_flags': [],
            'name': None,
            'scene_context': beat.get('setting_description'),
            'npc_responses': None,
            'shared_beat': None,
            'system_trigger': None,
            'data_hook': None,
            'system_triggers_list': None,
            'is_shared_beat': False
        }
        
        # Handle shared dialogue
        if beat_type == 'npc_shared' and 'shared_dialogue' in beat:
            shared_dialogues = beat.get('shared_dialogue', [])
            
            # Create passages for each shared speaker
            for i, speaker_obj in enumerate(shared_dialogues):
                next_target = f"beat_{beat_id}_shared_{i + 1}" if i < len(shared_dialogues) - 1 else target
                
                shared_passage = {
                    'pid': f"beat_{beat_id}_shared_{i}",
                    'conversationId': scene_name,
                    'beat_type': 'npc_shared',
                    'active_speaker': speaker_obj.get('speaker', 'Shared'),
                    'text': speaker_obj.get('text', ''),
                    'choices': [{
                        'tone': 'T',
                        'playerLine': '[Continue]',
                        'npc_response': '',
                        'target': next_target,
                        'result_text': '',
                        'tone_effects': [],
                        'remnants_effects': [],
                        'npc_resonance': []
                    }],
                    'required_flags': [],
                    'name': None,
                    'scene_context': None,
                    'npc_responses': None,
                    'shared_beat': None,
                    'system_trigger': None,
                    'data_hook': None,
                    'system_triggers_list': None,
                    'is_shared_beat': True
                }
                passages.append(shared_passage)
            
            # Main beat points to first shared passage
            passage['choices'] = [{
                'tone': 'T',
                'playerLine': '[Continue]',
                'npc_response': '',
                'target': f"beat_{beat_id}_shared_0",
                'result_text': '',
                'tone_effects': [],
                'remnants_effects': [],
                'npc_resonance': []
            }]
        
        # Handle tone choices
        elif 'tone_choices' in beat:
            for tone_choice in beat['tone_choices']:
                choice = {
                    'tone': tone_choice.get('tone', 'T'),
                    'playerLine': tone_choice.get('text', ''),
                    'label': tone_choice.get('label', ''),
                    'npc_response': tone_choice.get('npc_response', ''),
                    'result_text': tone_choice.get('result_text', ''),
                    'target': target,
                    'tone_effects': tone_choice.get('tone_effects', []),
                    'remnants_effects': tone_choice.get('remnants_effects', []),
                    'npc_resonance': tone_choice.get('npc_resonance', [])
                }
                passage['choices'].append(choice)
        
        passages.append(passage)
    
    # Create new passages-based structure
    new_data = {
        'name': scene_name,
        'startnode': 'beat_1',
        'passages': passages
    }
    
    # Write back to file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Done ({len(passages)} passages)")
    return True

def main():
    print("=" * 60)
    print("Converting beats-based JSON files to passages format")
    print("=" * 60)
    print()
    
    stories_dir = Path(STORIES_PATH)
    
    if not stories_dir.exists():
        print(f"ERROR: Stories directory not found: {stories_dir}")
        return 1
    
    json_files = list(stories_dir.glob("*.json"))
    
    if not json_files:
        print("ERROR: No JSON files found!")
        return 1
    
    converted = 0
    skipped = 0
    
    for json_file in sorted(json_files):
        try:
            if convert_beats_to_passages(json_file):
                converted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"[FAIL] ERROR: {e}")
            skipped += 1
    
    print()
    print("=" * 60)
    print("Conversion Complete!")
    print(f"  Converted: {converted} files")
    print(f"  Skipped:   {skipped} files")
    print()
    print("Next steps:")
    print("  1. Review the converted files in Unity")
    print("  2. Build and test the dialogue system")
    print("  3. Delete ConvertBeatsToPassages() from DialogueManager.cs")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    exit(main())

