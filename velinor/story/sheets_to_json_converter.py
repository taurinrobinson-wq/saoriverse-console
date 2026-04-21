"""
Velinor Sheets to JSON Converter
================================

Convert Google Sheets story templates to Velinor-native JSON format.

Usage:
    python sheets_to_json_converter.py --csv story_export.csv --output story.json
    
    Or programmatically:
    
    from sheets_to_json_converter import convert_rows_to_story
    rows = load_from_sheets()  # Your own loader
    story = convert_rows_to_story(rows)
"""

import json
import csv
import argparse
from typing import Dict, List, Any, Optional


def parse_kv_pairs(raw: str) -> Dict[str, float]:
    """Parse comma-separated key:value pairs into a dict.
    
    Format: "key1:val1,key2:val2"
    Returns: {"key1": val1, "key2": val2}
    """
    if not raw or not raw.strip():
        return {}
    result = {}
    for part in raw.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            key, val = part.split(':')
            result[key.strip()] = float(val.strip())
        except ValueError:
            print(f"Warning: Could not parse kv pair: {part}")
    return result


def parse_dice_check(raw: str) -> Optional[Dict[str, Any]]:
    """Parse dice check specification.
    
    Format: "stat:DC" e.g. "courage:12"
    Returns: {"stat": "courage", "dc": 12} or None if empty
    """
    if not raw or not raw.strip():
        return None
    try:
        stat, dc = raw.split(':')
        return {
            "stat": stat.strip(),
            "dc": int(dc.strip())
        }
    except (ValueError, AttributeError):
        print(f"Warning: Could not parse dice check: {raw}")
        return None


def parse_list(raw: str, separator: str = "|") -> List[str]:
    """Parse pipe or comma-separated list.
    
    Format: "item1|item2|item3" or "item1,item2,item3"
    Returns: ["item1", "item2", "item3"]
    """
    if not raw or not raw.strip():
        return []
    return [item.strip() for item in raw.split(separator) if item.strip()]


def convert_rows_to_story(
    rows: List[Dict[str, str]],
    title: str = "Velinor Story",
    author: str = "Unknown",
    region: str = "Unknown"
) -> Dict[str, Any]:
    """Convert spreadsheet rows to Velinor story JSON.
    
    Args:
        rows: List of row dictionaries from CSV/Sheets export
        title: Story title
        author: Story author
        region: Story region
    
    Returns:
        Story dictionary following Velinor schema
    """
    story = {
        "title": title,
        "version": "1.0",
        "start": None,
        "metadata": {
            "author": author,
            "region": region,
            "created_at": "2025-01-01"
        },
        "passages": {}
    }
    
    for i, row in enumerate(rows):
        # Get passage ID (required)
        pid = row.get("PassageID") or row.get("passage_id") or f"passage_{i}"
        pid = pid.strip()
        
        if i == 0 and not story["start"]:
            story["start"] = pid
        
        # Build passage object
        passage = {
            "id": pid,
            "text": row.get("Text") or row.get("text") or "",
            "background": row.get("Background") or row.get("background") or None,
            "npc": row.get("NPC") or row.get("npc") or None,
            "tags": parse_list(row.get("Tags") or row.get("tags") or "", ","),
            "dice": None,
            "glyph_rewards": parse_list(row.get("GlyphRewards") or row.get("glyph_rewards") or "", "|"),
            "tone_effects_on_enter": parse_kv_pairs(
                row.get("ToneOnEnter") or row.get("tone_on_enter") or ""
            ),
            "choices": []
        }
        
        # Parse up to 6 choices
        for choice_idx in range(1, 7):
            text_key_variations = [
                f"Choice{choice_idx}_Text",
                f"choice{choice_idx}_text",
                f"Choice{choice_idx}Text",
                f"choice{choice_idx}text"
            ]
            
            # Find text field with any case variation
            choice_text = None
            for key in text_key_variations:
                if key in row and row[key]:
                    choice_text = row[key].strip()
                    break
            
            if not choice_text:
                continue
            
            # Find corresponding fields
            target_key = f"Choice{choice_idx}_Target"
            if target_key not in row or not row[target_key]:
                target_key = f"choice{choice_idx}_target"
            
            dice_key = f"Choice{choice_idx}_DiceCheck"
            if dice_key not in row:
                dice_key = f"choice{choice_idx}_dicecheck"
            
            tone_key = f"Choice{choice_idx}_ToneEffects"
            if tone_key not in row:
                tone_key = f"choice{choice_idx}_toneeffects"
            
            npc_key = f"Choice{choice_idx}_NPCResonance"
            if npc_key not in row:
                npc_key = f"choice{choice_idx}_npcresonance"
            
            beat_key = f"Choice{choice_idx}_StoryBeat"
            if beat_key not in row:
                beat_key = f"choice{choice_idx}_storybeat"
            
            # Build choice object
            choice = {
                "id": f"{pid}_choice_{choice_idx}",
                "text": choice_text,
                "target": row.get(target_key, "").strip(),
                "dice_check": parse_dice_check(row.get(dice_key, "")),
                "tone_effects": parse_kv_pairs(row.get(tone_key, "")),
                "npc_resonance": parse_kv_pairs(row.get(npc_key, "")),
                "mark_story_beat": row.get(beat_key) or None
            }
            
            passage["choices"].append(choice)
        
        story["passages"][pid] = passage
    
    return story


def csv_to_story(csv_path: str, output_path: str, title: Optional[str] = None) -> None:
    """Load CSV file and convert to Velinor story JSON.
    
    Args:
        csv_path: Path to CSV file from Sheets export
        output_path: Path to output JSON file
        title: Optional story title (uses first row if not provided)
    """
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if not rows:
        raise ValueError("CSV file is empty")
    
    # Use first PassageID as title if not provided
    if not title:
        title = rows[0].get("PassageID", "Velinor Story")
    
    story = convert_rows_to_story(rows, title=title or "Velinor Story")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(story, f, indent=2)
    
    print(f"✅ Converted {len(rows)} passages to {output_path}")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Convert Google Sheets CSV export to Velinor story JSON"
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to CSV file from Sheets export"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output JSON file"
    )
    parser.add_argument(
        "--title",
        help="Story title (defaults to first PassageID)"
    )
    
    args = parser.parse_args()
    csv_to_story(args.csv, args.output, args.title)


if __name__ == "__main__":
    main()
