"""
Velinor Story Session - Twine-free Narrative Engine
==================================================

Runtime story management for Velinor-native JSON stories.
Consumes the canonical Velinor JSON schema and manages
player progression through passages and choices.

Usage:
    story_data = json.load(open("story.json"))
    session = StorySession(story_data)
    passage = session.get_current_passage()
    choices = session.get_choices()
    session.choose(0)  # Select first choice
"""

from typing import Dict, Any, Optional, List


class StorySession:
    """Runtime narrative engine for Velinor stories."""
    
    def __init__(self, story_data: Dict[str, Any]):
        """Initialize a story session from Velinor JSON data.
        
        Args:
            story_data: Story dictionary following Velinor schema
        """
        self.story = story_data
        self.current_id: str = story_data["start"]
        self.history: List[str] = [self.current_id]
    
    def get_current_passage(self) -> Dict[str, Any]:
        """Get the current passage object.
        
        Returns:
            Current passage dictionary with all fields
        """
        return self.story["passages"][self.current_id]
    
    def get_choices(self) -> List[Dict[str, Any]]:
        """Get available choices in the current passage.
        
        Returns:
            List of choice dictionaries
        """
        return self.get_current_passage().get("choices", [])
    
    def advance_to(self, passage_id: str) -> Dict[str, Any]:
        """Advance story to a specific passage by ID.
        
        Args:
            passage_id: Target passage ID
        
        Returns:
            The new current passage
        
        Raises:
            ValueError: If passage_id doesn't exist
        """
        if passage_id not in self.story["passages"]:
            raise ValueError(f"Unknown passage: {passage_id}")
        self.current_id = passage_id
        self.history.append(passage_id)
        return self.get_current_passage()
    
    def choose(self, choice_index: int) -> Dict[str, Any]:
        """Select a choice and advance to its target passage.
        
        Args:
            choice_index: Index of choice to select (0-based)
        
        Returns:
            The new current passage
        
        Raises:
            IndexError: If choice_index is out of range
        """
        choices = self.get_choices()
        if choice_index < 0 or choice_index >= len(choices):
            raise IndexError("Invalid choice index")
        choice = choices[choice_index]
        # Note: Dice checks are handled by orchestrator/game engine
        target = choice["target"]
        return self.advance_to(target)
    
    def get_choice_metadata(self, choice_index: int) -> Dict[str, Any]:
        """Get consequence metadata for a choice (without selecting it).
        
        Args:
            choice_index: Index of choice (0-based)
        
        Returns:
            Dictionary with tone_effects, npc_resonance, mark_story_beat
        """
        choices = self.get_choices()
        choice = choices[choice_index]
        return {
            "tone_effects": choice.get("tone_effects", {}),
            "npc_resonance": choice.get("npc_resonance", {}),
            "mark_story_beat": choice.get("mark_story_beat")
        }
    
    def get_history(self) -> List[str]:
        """Get list of all passages visited in order.
        
        Returns:
            List of passage IDs
        """
        return self.history.copy()
