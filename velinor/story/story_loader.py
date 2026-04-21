"""
Velinor Story Loader - Load Stories from JSON
==============================================

This module loads Velinor-native story JSON files into passage objects
for use by the story session and game engine.

No Twine-specific fields, markup, or metadata.
"""

import json
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class StoryPassage:
    """Represents a passage (scene) in a story."""
    pid: str
    name: str
    text: str
    tags: List[str] = field(default_factory=list)
    position: tuple = (0, 0)
    size: tuple = (100, 100)
    background: Optional[str] = None
    npcs: List[str] = field(default_factory=list)
    choices: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_choice_by_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Find a choice by its text."""
        for choice in self.choices:
            if choice.get('text') == text:
                return choice
        return None


@dataclass
class DialogueChoice:
    """A player choice that leads to the next story passage."""
    text: str
    target_passage: str
    tone_effects: Optional[Dict[str, float]] = None
    npc_resonance: Optional[Dict[str, float]] = None


@dataclass
class StoryContext:
    """Context for the current story state."""
    current_passage_id: str
    passage_history: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    visited_passages: set = field(default_factory=set)
    dialogue_log: List[Dict[str, str]] = field(default_factory=list)
    
    def mark_visited(self, passage_id: str) -> None:
        """Mark a passage as visited."""
        self.visited_passages.add(passage_id)
        self.passage_history.append(passage_id)
    
    def has_visited(self, passage_id: str) -> bool:
        """Check if passage has been visited."""
        return passage_id in self.visited_passages


class StoryLoader:
    """Loads and parses Velinor story JSON format."""
    
    def __init__(self):
        self.passages: Dict[str, StoryPassage] = {}
        self.passages_by_name: Dict[str, str] = {}  # Maps passage name to pid
        self.story_data: Optional[Dict[str, Any]] = None
    
    def load_from_json(self, json_path: str) -> Dict[str, StoryPassage]:
        """Load Velinor story from JSON.
        
        Args:
            json_path: Path to the story JSON file
        
        Returns:
            Dictionary mapping passage names to StoryPassage objects
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.story_data = json.load(f)
            
            # Extract passages from JSON
            if 'passages' in self.story_data:
                for passage_data in self.story_data['passages']:
                    pid = str(passage_data.get('pid', ''))
                    name = passage_data.get('name', 'Unnamed')
                    
                    # Extract metadata
                    metadata = passage_data.get('_metadata', {})
                    background = metadata.get('background')
                    npcs = metadata.get('npcs', [])
                    
                    # Extract choices
                    choices = passage_data.get('choices', [])
                    
                    passage = StoryPassage(
                        pid=pid,
                        name=name,
                        text=passage_data.get('text', ''),
                        tags=passage_data.get('tags', []),
                        position=tuple(passage_data.get('position', (0, 0))),
                        size=tuple(passage_data.get('size', (100, 100))),
                        background=background,
                        npcs=npcs,
                        choices=choices
                    )
                    
                    self.passages[pid] = passage
                    self.passages_by_name[name] = pid
            
            return self.passages
        
        except FileNotFoundError:
            print(f"Story file not found: {json_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in story file: {e}")
            return {}
    
    def get_passage(self, passage_id: str) -> Optional[StoryPassage]:
        """Get a passage by ID."""
        return self.passages.get(passage_id)
    
    def get_passage_by_name(self, name: str) -> Optional[StoryPassage]:
        """Get a passage by name."""
        if name in self.passages_by_name:
            pid = self.passages_by_name[name]
            return self.passages.get(pid)
        return None
    
    def get_start_passage(self) -> Optional[StoryPassage]:
        """Get the starting passage."""
        if self.story_data and 'startnode' in self.story_data:
            start_pid = str(self.story_data['startnode'])
            return self.get_passage(start_pid)
        
        # Fallback: return first passage
        if self.passages:
            return next(iter(self.passages.values()))
        
        return None
    
    def get_all_passages(self) -> List[StoryPassage]:
        """Get all passages."""
        return list(self.passages.values())
