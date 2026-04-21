"""
Velinor Story Builder - Programmatic Story Construction
=======================================================

This module provides a Velinor-native DSL for building stories
that export to the canonical Velinor JSON schema (emotion-OS aware,
Twine-free).

Usage:
    builder = StoryBuilder("My Story")
    builder.add_passage("start", "You wake up.", is_start=True)
    builder.add_choice("start", "Get up", "standing")
    builder.add_passage("standing", "You are standing.", 
                       background="bedroom", npc="Cat")
    builder.export_json("story.json")
"""

import json
from typing import Optional, Dict, List, Any


class StoryBuilder:
    """Programmatic builder for Velinor stories matching canonical JSON schema."""
    
    def __init__(self, title: str, author: str = "Anonymous", region: str = "Unknown"):
        """Initialize a new story.
        
        Args:
            title: Story title
            author: Author name
            region: Region/setting name
        """
        self.story = {
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
    
    def add_passage(
        self,
        passage_id: str,
        text: str,
        background: Optional[str] = None,
        npc: Optional[str] = None,
        tags: Optional[List[str]] = None,
        glyph_rewards: Optional[List[str]] = None,
        tone_effects_on_enter: Optional[Dict[str, float]] = None,
        is_start: bool = False
    ) -> None:
        """Add a passage (scene) to the story.
        
        Args:
            passage_id: Unique identifier for this passage
            text: Full passage text (no Twine markup)
            background: Background image/location name (e.g., "market_ruins")
            npc: NPC name present in this scene
            tags: List of tags for organization (e.g., ["intro", "market"])
            glyph_rewards: List of glyphs player can earn here
            tone_effects_on_enter: TONE stat changes on entering (e.g., {"courage": 0.1})
            is_start: Whether this is the starting passage
        """
        self.story["passages"][passage_id] = {
            "id": passage_id,
            "text": text,
            "background": background,
            "npc": npc,
            "tags": tags or [],
            "dice": None,
            "glyph_rewards": glyph_rewards or [],
            "tone_effects_on_enter": tone_effects_on_enter or {},
            "choices": []
        }
        
        if is_start or self.story["start"] is None:
            self.story["start"] = passage_id
    
    def add_choice(
        self,
        from_passage_id: str,
        text: str,
        target_id: str,
        dice_check: Optional[Dict[str, Any]] = None,
        tone_effects: Optional[Dict[str, float]] = None,
        npc_resonance: Optional[Dict[str, float]] = None,
        mark_story_beat: Optional[str] = None
    ) -> None:
        """Add a choice to a passage.
        
        Args:
            from_passage_id: ID of source passage
            text: Choice text shown to player
            target_id: ID of next passage if this choice is selected
            dice_check: Optional skill check (e.g., {"stat": "courage", "dc": 12})
            tone_effects: TONE stat changes (e.g., {"courage": 0.2, "empathy": -0.1})
            npc_resonance: NPC relationship changes (e.g., {"Keeper": 0.3})
            mark_story_beat: Named story beat (e.g., "first_contact_keeper")
        """
        if from_passage_id not in self.story["passages"]:
            raise ValueError(f"Passage '{from_passage_id}' does not exist")
        
        passage = self.story["passages"][from_passage_id]
        choice_number = len(passage["choices"]) + 1
        choice_id = f"{from_passage_id}_choice_{choice_number}"
        
        choice = {
            "id": choice_id,
            "text": text,
            "target": target_id,
            "dice_check": dice_check,
            "tone_effects": tone_effects or {},
            "npc_resonance": npc_resonance or {},
            "mark_story_beat": mark_story_beat
        }
        
        passage["choices"].append(choice)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata field (e.g., author, region, description).
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.story["metadata"][key] = value
    
    def export_json(self, output_path: str) -> None:
        """Export story to JSON file following Velinor schema.
        
        Args:
            output_path: Path to output JSON file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.story, f, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Return story as dictionary (for programmatic use).
        
        Returns:
            Story dictionary following Velinor schema
        """
        return self.story
    
    def validate(self) -> List[str]:
        """Validate story structure and return list of issues.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.story["title"]:
            errors.append("Story must have a title")
        
        if not self.story["start"]:
            errors.append("Story must have a start passage")
        
        if self.story["start"] not in self.story["passages"]:
            errors.append(f"Start passage '{self.story['start']}' does not exist")
        
        # Check all choice targets exist
        for passage_id, passage in self.story["passages"].items():
            for choice in passage.get("choices", []):
                target = choice.get("target")
                if target and target not in self.story["passages"]:
                    errors.append(f"Choice in '{passage_id}' references unknown passage '{target}'")
        
        return errors
