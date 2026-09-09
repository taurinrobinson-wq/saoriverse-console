#!/usr/bin/env python3
"""
Rename "passages" to "beats" in all dialogue JSON files.
This completes the pure-beats architecture (no more hybrid wrappers).
"""

import json
import os
from pathlib import Path

# All dialogue JSON files
json_files = [
    "kaelen_confession_01.json",
    "nima_encounter_01.json",
    "nima_encounter_02.json",
    "ravi_encounter_01.json",
    "ravi_nima_market_discovery.json",
    "saori_desert_encounter_01.json",
    "search_remembrance_01.json",
    "willy_concourse_ruins.json",
]

base_path = Path("C:/saoriverse-console/Velinor-Unity/Assets/Resources/velinor/stories")

print("\n" + "="*70)
print("RENAMING: passages -> beats (Pure Beats Architecture)")
print("="*70 + "\n")

success_count = 0
error_count = 0

for filename in json_files:
    filepath = base_path / filename
    
    try:
        # Read the JSON file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if "passages" exists
        if "passages" not in data:
            print(f"[SKIP] {filename}")
            print(f"       No 'passages' field found\n")
            continue
        
        # Rename "passages" to "beats"
        data["beats"] = data.pop("passages")
        beat_count = len(data["beats"])
        
        # Write back with pretty formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] {filename}")
        print(f"     Converted {beat_count} beats\n")
        success_count += 1
        
    except FileNotFoundError:
        print(f"[ERROR] {filename}")
        print(f"        File not found at {filepath}\n")
        error_count += 1
    except json.JSONDecodeError as e:
        print(f"[ERROR] {filename}")
        print(f"        JSON parse error: {e}\n")
        error_count += 1
    except Exception as e:
        print(f"[ERROR] {filename}")
        print(f"        {e}\n")
        error_count += 1

print("="*70)
print(f"RESULTS: {success_count} converted, {error_count} errors")
print("="*70)
print("\nAll JSON files now use 'beats' instead of 'passages'")
print("Pure beats architecture complete!\n")
