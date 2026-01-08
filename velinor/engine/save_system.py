"""
Save System - Phase 5
Manages saving game progress to files
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from .game_state import GameStateSnapshot, GameStateValidator


@dataclass
class SaveSlot:
    """Represents a single save slot"""
    slot_id: str
    save_name: str
    player_name: str
    save_timestamp: str
    play_duration_seconds: int
    current_day: int
    current_phase: str
    ending_type: Optional[int]
    game_completed: bool
    filepath: Path
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'slot_id': self.slot_id,
            'save_name': self.save_name,
            'player_name': self.player_name,
            'save_timestamp': self.save_timestamp,
            'play_duration_seconds': self.play_duration_seconds,
            'current_day': self.current_day,
            'current_phase': self.current_phase,
            'ending_type': self.ending_type,
            'game_completed': self.game_completed,
            'filepath': str(self.filepath),
        }


class SaveManager:
    """Manages game saves"""
    
    def __init__(self, save_directory: Path = None):
        """
        Initialize save manager
        
        Args:
            save_directory: Path to directory where saves are stored
        """
        if save_directory is None:
            save_directory = Path(__file__).parent.parent.parent / "saves"
        
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
        self.max_save_slots = 10
        self.auto_save_slot = "__autosave__"
        self.metadata_filename = "saves_metadata.json"
    
    def save_game(
        self,
        state_snapshot: GameStateSnapshot,
        save_name: str = None,
        auto_save: bool = False
    ) -> tuple[bool, str, Optional[str]]:
        """
        Save game state to file
        
        Args:
            state_snapshot: GameStateSnapshot with game state
            save_name: Name for the save (optional)
            auto_save: Whether this is an auto-save
            
        Returns:
            Tuple of (success: bool, message: str, slot_id: Optional[str])
        """
        # Validate snapshot
        if not GameStateValidator.validate_snapshot(state_snapshot):
            errors = GameStateValidator.get_validation_errors(state_snapshot)
            return False, f"Invalid game state: {', '.join(errors)}", None
        
        try:
            # Determine slot ID
            if auto_save:
                slot_id = self.auto_save_slot
            else:
                slot_id = self._get_next_slot_id()
                if slot_id is None:
                    return False, "Save slots are full", None
            
            # Create save filename
            save_name = save_name or f"Save {state_snapshot.player_name}"
            filename = f"{slot_id}.json"
            filepath = self.save_directory / filename
            
            # Save state to file
            save_data = {
                'slot_id': slot_id,
                'save_name': save_name,
                'state': state_snapshot.to_dict(),
            }
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            # Update metadata
            self._update_metadata(slot_id, save_name, state_snapshot)
            
            action = "Auto-saved" if auto_save else "Saved"
            return True, f"{action} to '{save_name}'", slot_id
        
        except Exception as e:
            return False, f"Error saving game: {str(e)}", None
    
    def get_save_slots(self) -> List[SaveSlot]:
        """
        Get all available save slots
        
        Returns:
            List of SaveSlot objects
        """
        slots = []
        
        for filepath in self.save_directory.glob("*.json"):
            if filepath.name == self.metadata_filename:
                continue
            
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                state = data.get('state', {})
                slot = SaveSlot(
                    slot_id=data.get('slot_id', ''),
                    save_name=data.get('save_name', 'Unknown'),
                    player_name=state.get('player_name', 'Unknown'),
                    save_timestamp=state.get('save_timestamp', ''),
                    play_duration_seconds=state.get('play_duration_seconds', 0),
                    current_day=state.get('current_day', 0),
                    current_phase=state.get('current_phase', ''),
                    ending_type=state.get('ending_type'),
                    game_completed=state.get('game_completed', False),
                    filepath=filepath,
                )
                slots.append(slot)
            except Exception:
                continue
        
        # Sort by timestamp (newest first)
        slots.sort(
            key=lambda s: s.save_timestamp,
            reverse=True
        )
        
        return slots
    
    def delete_save(self, slot_id: str) -> tuple[bool, str]:
        """
        Delete a save slot
        
        Args:
            slot_id: ID of slot to delete
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if slot_id == self.auto_save_slot:
            return False, "Cannot delete auto-save"
        
        try:
            filepath = self.save_directory / f"{slot_id}.json"
            if filepath.exists():
                filepath.unlink()
                self._remove_from_metadata(slot_id)
                return True, f"Deleted save slot {slot_id}"
            else:
                return False, f"Save slot {slot_id} not found"
        except Exception as e:
            return False, f"Error deleting save: {str(e)}"
    
    def get_save_slot_count(self) -> tuple[int, int]:
        """
        Get current save slot count
        
        Returns:
            Tuple of (used_slots, max_slots)
        """
        used = len([s for s in self.save_directory.glob("*.json") 
                   if s.name != self.metadata_filename 
                   and s.name != f"{self.auto_save_slot}.json"])
        return used, self.max_save_slots
    
    def is_save_slots_full(self) -> bool:
        """Check if save slots are full"""
        used, max_slots = self.get_save_slot_count()
        return used >= max_slots
    
    def _get_next_slot_id(self) -> Optional[str]:
        """Get next available slot ID"""
        used_slots = set()
        for filepath in self.save_directory.glob("*.json"):
            if filepath.name == self.metadata_filename:
                continue
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    used_slots.add(data.get('slot_id', ''))
            except Exception:
                continue
        
        # Find first available slot
        for i in range(1, self.max_save_slots + 1):
            slot_id = f"save_{i}"
            if slot_id not in used_slots:
                return slot_id
        
        return None
    
    def _update_metadata(
        self,
        slot_id: str,
        save_name: str,
        state: GameStateSnapshot
    ) -> None:
        """Update saves metadata file"""
        metadata_path = self.save_directory / self.metadata_filename
        
        try:
            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            
            metadata[slot_id] = {
                'save_name': save_name,
                'player_name': state.player_name,
                'save_timestamp': state.save_timestamp,
                'coherence_score': state.coherence_score,
                'current_day': state.current_day,
                'ending_type': state.ending_type,
                'game_completed': state.game_completed,
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception:
            pass  # Silent failure for metadata updates
    
    def _remove_from_metadata(self, slot_id: str) -> None:
        """Remove slot from metadata"""
        metadata_path = self.save_directory / self.metadata_filename
        
        try:
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                if slot_id in metadata:
                    del metadata[slot_id]
                
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
        except Exception:
            pass  # Silent failure
    
    def get_save_description(self, slot: SaveSlot) -> str:
        """Get human-readable description of a save"""
        timestamp = datetime.fromisoformat(slot.save_timestamp).strftime("%b %d, %Y %I:%M %p")
        duration_hours = slot.play_duration_seconds // 3600
        duration_mins = (slot.play_duration_seconds % 3600) // 60
        
        if slot.game_completed and slot.ending_type:
            status = f"Completed (Ending {slot.ending_type})"
        else:
            status = f"Day {slot.current_day} - {slot.current_phase}"
        
        return f"{slot.save_name} - {status}\n{timestamp} ({duration_hours}h {duration_mins}m)"


class QuickSaveManager:
    """Manages quick-save functionality"""
    
    def __init__(self, save_manager: SaveManager):
        self.save_manager = save_manager
    
    def quick_save(self, state_snapshot: GameStateSnapshot) -> tuple[bool, str]:
        """Perform a quick-save"""
        success, message, _ = self.save_manager.save_game(
            state_snapshot,
            save_name="Quick Save",
            auto_save=True
        )
        return success, message
    
    def quick_load(self) -> Optional[GameStateSnapshot]:
        """Load the quick-save"""
        try:
            filepath = self.save_manager.save_directory / f"{self.save_manager.auto_save_slot}.json"
            if filepath.exists():
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return GameStateSnapshot.from_dict(data.get('state', {}))
        except Exception:
            pass
        return None
    
    def has_quick_save(self) -> bool:
        """Check if quick-save exists"""
        filepath = self.save_manager.save_directory / f"{self.save_manager.auto_save_slot}.json"
        return filepath.exists()
