# Velinor Story JSON Schema

## Overview

One canonical format for all Velinor stories: **Twine-free, emotional-OS-aware, lay-user-friendly.**

## Complete Schema

```json
{
  "title": "Velinor: Remnants of the Tone",
  "version": "1.0",
  "start": "market_entry",
  "metadata": {
    "region": "Saonyx_Market",
    "author": "Taurin Robinson",
    "created_at": "2025-01-01",
    "description": "Optional story description"
  },
  "passages": {
    "passage_id": {
      "id": "passage_id",
      "text": "Full passage text displayed to the player",
      "background": "market_ruins",
      "npc": "Keeper",
      "tags": ["intro", "market"],
      "dice": null,
      "glyph_rewards": ["Courage", "Wisdom"],
      "tone_effects_on_enter": {
        "courage": 0.1,
        "resolve": -0.05
      },
      "choices": [
        {
          "id": "passage_id_choice_1",
          "text": "Choice text shown to player",
          "target": "next_passage_id",
          "dice_check": {
            "stat": "courage",
            "dc": 12
          },
          "tone_effects": {
            "courage": 0.2,
            "empathy": -0.1
          },
          "npc_resonance": {
            "Keeper": 0.3,
            "Ravi": -0.1
          },
          "mark_story_beat": "first_contact_keeper"
        }
      ]
    }
  }
}
```

## Field Reference

### Root Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Story title |
| `version` | string | Yes | Schema version (always "1.0") |
| `start` | string | Yes | ID of starting passage |
| `metadata` | object | Yes | Story metadata (author, region, etc.) |
| `passages` | object | Yes | Map of all passages by ID |

### Passage Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique passage identifier |
| `text` | string | Yes | Full passage text (no markup) |
| `background` | string | No | Background/location (e.g., "market_ruins") |
| `npc` | string | No | NPC present in this passage |
| `tags` | array | No | Story/scene tags for organization |
| `dice` | object | No | Reserved for future dice mechanics |
| `glyph_rewards` | array | No | Glyphs player can earn (e.g., ["Courage", "Wisdom"]) |
| `tone_effects_on_enter` | object | No | TONE stat changes on entering passage (key: stat, value: float) |
| `choices` | array | Yes | Array of available choices (can be empty) |

### Choice Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique choice identifier (often `{passage_id}_choice_{n}`) |
| `text` | string | Yes | Choice text displayed to player |
| `target` | string | Yes | ID of next passage if chosen |
| `dice_check` | object | No | Skill check required (null if none) |
| `tone_effects` | object | No | TONE stat changes if this choice is made |
| `npc_resonance` | object | No | NPC relationship changes (key: NPC name, value: float) |
| `mark_story_beat` | string | No | Named story beat for tracking (e.g., "first_contact_keeper") |

### Dice Check Object

| Field | Type | Description |
|-------|------|-------------|
| `stat` | string | Skill stat ("courage", "wisdom", "empathy", "resolve") |
| `dc` | integer | Difficulty class (typically 8-15) |

## Example: Minimal Story

```json
{
  "title": "Hello Velinor",
  "version": "1.0",
  "start": "start",
  "metadata": {"author": "You"},
  "passages": {
    "start": {
      "id": "start",
      "text": "You wake up.",
      "background": null,
      "npc": null,
      "tags": [],
      "dice": null,
      "glyph_rewards": [],
      "tone_effects_on_enter": {},
      "choices": [
        {
          "id": "start_choice_1",
          "text": "Stand up",
          "target": "stand",
          "dice_check": null,
          "tone_effects": {},
          "npc_resonance": {},
          "mark_story_beat": null
        }
      ]
    },
    "stand": {
      "id": "stand",
      "text": "You are standing.",
      "background": null,
      "npc": null,
      "tags": [],
      "dice": null,
      "glyph_rewards": [],
      "tone_effects_on_enter": {},
      "choices": []
    }
  }
}
```

## Usage Notes

- **No Twine markup** — Just plain text in the `text` field
- **Flat passages** — No nesting; all passages are top-level in the `passages` object
- **One start** — Only one passage can be the starting point
- **Choices are optional** — A passage can have zero choices (end of story/branch)
- **TONE effects** — Small floats (±0.1 to ±0.3) for trait adjustments
- **NPC resonance** — Similar scale; affects NPC trust/relationship
- **Story beats** — Used to track narrative milestones for ending calculations

## Backward Compatibility

This schema **replaces Twine** entirely. If you have old Twine stories:
1. Export as JSON from Twine
2. Run through the converter (see `sheets_to_json_converter.py`)
3. Validate output
4. Update passage IDs if necessary
