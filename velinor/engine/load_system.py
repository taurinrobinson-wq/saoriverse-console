"""
Load System - Phase 5
Manages loading saved game progress
"""

import json
from typing import Optional, Tuple, Any, Dict
from pathlib import Path
from .game_state import GameStateSnapshot, GameStateRestorer, GameStateValidator


class LoadManager:
    """Manages game loading"""
    
    def __init__(self, save_directory: Path = None):
        """
        Initialize load manager
        
        Args:
            save_directory: Path to directory where saves are stored
        """
        if save_directory is None:
            save_directory = Path(__file__).parent.parent.parent / "saves"
        
        self.save_directory = Path(save_directory)
        self.current_loaded_state: Optional[GameStateSnapshot] = None
        self.loaded_from_slot: Optional[str] = None
    
    def load_game(self, slot_id: str) -> Tuple[bool, str, Optional[GameStateSnapshot]]:
        """
        Load a saved game
        
        Args:
            slot_id: ID of save slot to load
            
        Returns:
            Tuple of (success: bool, message: str, state: Optional[GameStateSnapshot])
        """
        try:
            filepath = self.save_directory / f"{slot_id}.json"
            
            if not filepath.exists():
                return False, f"Save slot '{slot_id}' not found", None
            
            # Load and parse save file
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Check version compatibility
            state_data = data.get('state', {})
            version = state_data.get('version', '1.0')
            if not self._is_version_compatible(version):
                return False, f"Save file version {version} is not compatible with current game", None
            
            # Create snapshot from loaded data
            state = GameStateSnapshot.from_dict(state_data)
            
            # Validate loaded state
            if not GameStateValidator.validate_snapshot(state):
                errors = GameStateValidator.get_validation_errors(state)
                return False, f"Save file is corrupted: {', '.join(errors)}", None
            
            # Store loaded state
            self.current_loaded_state = state
            self.loaded_from_slot = slot_id
            
            return True, f"Loaded '{data.get('save_name', 'Unknown')}'", state
        
        except json.JSONDecodeError:
            return False, "Save file is corrupted (invalid JSON)", None
        except Exception as e:
            return False, f"Error loading save: {str(e)}", None
    
    def restore_to_orchestrator(
        self,
        state: GameStateSnapshot,
        orchestrator: Any
    ) -> Tuple[bool, str]:
        """
        Restore loaded state to orchestrator
        
        Args:
            state: GameStateSnapshot to restore
            orchestrator: VelinorTwineOrchestrator instance
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            success = GameStateRestorer.restore_to_orchestrator(state, orchestrator)
            if success:
                return True, f"Restored game for {state.player_name}"
            else:
                return False, "Failed to restore game state"
        except Exception as e:
            return False, f"Error restoring game: {str(e)}"
    
    def get_current_loaded_state(self) -> Optional[GameStateSnapshot]:
        """Get currently loaded game state"""
        return self.current_loaded_state
    
    def clear_loaded_state(self) -> None:
        """Clear currently loaded state"""
        self.current_loaded_state = None
        self.loaded_from_slot = None
    
    def get_save_summary(self, slot_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summary information about a save
        
        Args:
            slot_id: ID of save slot
            
        Returns:
            Dictionary with save information, or None if not found
        """
        try:
            filepath = self.save_directory / f"{slot_id}.json"
            if not filepath.exists():
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            state = data.get('state', {})
            return {
                'save_name': data.get('save_name', 'Unknown'),
                'player_name': state.get('player_name', 'Unknown'),
                'save_timestamp': state.get('save_timestamp', ''),
                'coherence_score': state.get('coherence_score', 0),
                'current_day': state.get('current_day', 0),
                'current_phase': state.get('current_phase', ''),
                'game_completed': state.get('game_completed', False),
                'ending_type': state.get('ending_type'),
                'play_duration_seconds': state.get('play_duration_seconds', 0),
            }
        except Exception:
            return None
    
    @staticmethod
    def _is_version_compatible(save_version: str) -> bool:
        """Check if save file version is compatible"""
        # For now, only support version 1.0
        # In the future, this can implement migration logic
        return save_version == "1.0"


class SaveGameRecovery:
    """Handles recovery from corrupted or incomplete saves"""
    
    def __init__(self, save_directory: Path = None):
        """
        Initialize recovery system
        
        Args:
            save_directory: Path to directory where saves are stored
        """
        if save_directory is None:
            save_directory = Path(__file__).parent.parent.parent / "saves"
        
        self.save_directory = Path(save_directory)
        self.recovery_directory = self.save_directory / ".recovery"
        self.recovery_directory.mkdir(parents=True, exist_ok=True)
    
    def backup_all_saves(self) -> Tuple[bool, str, int]:
        """
        Create backup of all saves
        
        Returns:
            Tuple of (success: bool, message: str, backup_count: int)
        """
        try:
            import shutil
            
            backup_count = 0
            for filepath in self.save_directory.glob("*.json"):
                if filepath.name == "saves_metadata.json":
                    continue
                
                try:
                    backup_path = self.recovery_directory / filepath.name
                    shutil.copy2(filepath, backup_path)
                    backup_count += 1
                except Exception:
                    continue
            
            return True, f"Backed up {backup_count} save files", backup_count
        except Exception as e:
            return False, f"Error backing up saves: {str(e)}", 0
    
    def restore_from_backup(self, slot_id: str) -> Tuple[bool, str]:
        """
        Restore a save from backup
        
        Args:
            slot_id: ID of slot to restore
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            import shutil
            
            backup_path = self.recovery_directory / f"{slot_id}.json"
            if not backup_path.exists():
                return False, f"No backup found for slot {slot_id}"
            
            original_path = self.save_directory / f"{slot_id}.json"
            shutil.copy2(backup_path, original_path)
            
            return True, f"Restored save from backup"
        except Exception as e:
            return False, f"Error restoring from backup: {str(e)}"
    
    def attempt_recovery(self, slot_id: str) -> Tuple[bool, str, Optional[GameStateSnapshot]]:
        """
        Attempt to recover a corrupted save
        
        Args:
            slot_id: ID of corrupted slot
            
        Returns:
            Tuple of (success: bool, message: str, state: Optional[GameStateSnapshot])
        """
        filepath = self.save_directory / f"{slot_id}.json"
        
        if not filepath.exists():
            return False, f"Save slot {slot_id} not found", None
        
        try:
            # Try to load and fix common issues
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Try to parse as JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # Try to recover from incomplete JSON
                data = self._recover_json(content)
                if data is None:
                    return False, "Save file is too corrupted to recover", None
            
            # Verify and fix state data
            state_data = data.get('state', {})
            state = GameStateSnapshot.from_dict(state_data)
            
            # Save recovered state
            recovered_data = {
                'slot_id': slot_id,
                'save_name': data.get('save_name', 'Recovered Save'),
                'state': state.to_dict(),
            }
            
            with open(filepath, 'w') as f:
                json.dump(recovered_data, f, indent=2)
            
            return True, "Save file recovered and repaired", state
        
        except Exception as e:
            return False, f"Recovery failed: {str(e)}", None
    
    @staticmethod
    def _recover_json(content: str) -> Optional[dict]:
        """Attempt to recover JSON from incomplete content"""
        try:
            # Try to fix common JSON issues
            # Add missing closing braces if needed
            if content.count('{') > content.count('}'):
                content += '}' * (content.count('{') - content.count('}'))
            
            return json.loads(content)
        except Exception:
            return None
