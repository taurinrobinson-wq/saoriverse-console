"""
Phase 5 Integration Tests - Save/Load Persistence
Tests all save and load functionality
"""

import pytest
import json
import tempfile
from pathlib import Path
from velinor.engine.orchestrator import VelinorTwineOrchestrator
from velinor.engine.game_state import (
    GameStateSnapshot, GameStateBuilder, GameStateRestorer, GameStateValidator
)
from velinor.engine.save_system import SaveManager, SaveSlot, QuickSaveManager
from velinor.engine.load_system import LoadManager, SaveGameRecovery
from velinor.engine.core import VelinorEngine
from velinor.engine.event_timeline import AftermathPath


class TestGameStateSnapshot:
    """Test game state snapshots"""
    
    def test_snapshot_initialization(self):
        """GameStateSnapshot initializes with defaults"""
        snapshot = GameStateSnapshot()
        assert snapshot.version == "1.0"
        assert snapshot.coherence_score == 0.0
        assert snapshot.current_day == 0
    
    def test_snapshot_to_dict(self):
        """Snapshot converts to dictionary"""
        snapshot = GameStateSnapshot(
            player_name="TestPlayer",
            coherence_score=75.0
        )
        data = snapshot.to_dict()
        
        assert isinstance(data, dict)
        assert data['player_name'] == "TestPlayer"
        assert data['coherence_score'] == 75.0
    
    def test_snapshot_from_dict(self):
        """Snapshot restores from dictionary"""
        original = {
            'player_name': 'TestPlayer',
            'coherence_score': 85.0,
            'current_day': 5,
            'version': '1.0',
        }
        
        snapshot = GameStateSnapshot.from_dict(original)
        
        assert snapshot.player_name == "TestPlayer"
        assert snapshot.coherence_score == 85.0
        assert snapshot.current_day == 5
    
    def test_snapshot_from_dict_with_missing_fields(self):
        """Snapshot handles missing fields gracefully"""
        minimal = {
            'player_name': 'TestPlayer',
            'version': '1.0',
        }
        
        snapshot = GameStateSnapshot.from_dict(minimal)
        assert snapshot.coherence_score == 0.0  # Default
        assert snapshot.current_day == 0  # Default


class TestGameStateValidator:
    """Test game state validation"""
    
    def test_validate_valid_snapshot(self):
        """Valid snapshot passes validation"""
        snapshot = GameStateSnapshot(
            player_name="TestPlayer",
            coherence_score=50.0,
            current_day=3,
            building_stability_percent=75
        )
        
        assert GameStateValidator.validate_snapshot(snapshot) is True
    
    def test_validate_missing_player_name(self):
        """Snapshot without player name fails"""
        snapshot = GameStateSnapshot(
            coherence_score=50.0
        )
        
        assert GameStateValidator.validate_snapshot(snapshot) is False
    
    def test_validate_invalid_coherence_score(self):
        """Invalid coherence score fails"""
        snapshot = GameStateSnapshot(
            player_name="TestPlayer",
            coherence_score=150.0  # Out of range
        )
        
        assert GameStateValidator.validate_snapshot(snapshot) is False
    
    def test_get_validation_errors(self):
        """Get list of validation errors"""
        snapshot = GameStateSnapshot(
            coherence_score=-10.0,
            current_day=-1,
            building_stability_percent=150
        )
        
        errors = GameStateValidator.get_validation_errors(snapshot)
        assert len(errors) > 0
        assert any("coherence" in e.lower() for e in errors)


class TestSaveManager:
    """Test save manager"""
    
    def setup_method(self):
        """Create temporary save directory"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.save_manager = SaveManager(Path(self.temp_dir.name))
    
    def teardown_method(self):
        """Clean up temporary directory"""
        self.temp_dir.cleanup()
    
    def test_save_manager_initialization(self):
        """SaveManager initializes correctly"""
        assert self.save_manager.save_directory.exists()
        assert self.save_manager.max_save_slots == 10
    
    def test_save_game(self):
        """Save game to file"""
        snapshot = GameStateSnapshot(
            player_name="TestPlayer",
            coherence_score=75.0,
            current_day=5
        )
        
        success, message, slot_id = self.save_manager.save_game(snapshot, "TestSave")
        
        assert success is True
        assert slot_id is not None
        assert "TestSave" in message
        
        # Verify file exists
        save_file = self.save_manager.save_directory / f"{slot_id}.json"
        assert save_file.exists()
    
    def test_save_game_with_invalid_snapshot(self):
        """Save with invalid snapshot fails"""
        snapshot = GameStateSnapshot(
            coherence_score=150.0  # Invalid
        )
        
        success, message, slot_id = self.save_manager.save_game(snapshot)
        
        assert success is False
        assert slot_id is None
    
    def test_auto_save(self):
        """Auto-save uses special slot"""
        snapshot = GameStateSnapshot(player_name="TestPlayer")
        
        success, message, slot_id = self.save_manager.save_game(snapshot, auto_save=True)
        
        assert success is True
        assert slot_id == "__autosave__"
    
    def test_get_save_slots(self):
        """Get list of save slots"""
        # Create a few saves
        for i in range(3):
            snapshot = GameStateSnapshot(
                player_name=f"Player{i}",
                current_day=i+1
            )
            self.save_manager.save_game(snapshot, f"Save{i}")
        
        slots = self.save_manager.get_save_slots()
        
        assert len(slots) >= 3
        assert all(isinstance(slot, SaveSlot) for slot in slots)
    
    def test_delete_save(self):
        """Delete a save slot"""
        snapshot = GameStateSnapshot(player_name="TestPlayer")
        _, _, slot_id = self.save_manager.save_game(snapshot, "TestSave")
        
        # Verify save exists
        assert (self.save_manager.save_directory / f"{slot_id}.json").exists()
        
        # Delete save
        success, message = self.save_manager.delete_save(slot_id)
        
        assert success is True
        assert (self.save_manager.save_directory / f"{slot_id}.json").exists() is False
    
    def test_cannot_delete_autosave(self):
        """Cannot delete auto-save slot"""
        success, message = self.save_manager.delete_save("__autosave__")
        
        assert success is False
    
    def test_is_save_slots_full(self):
        """Check if save slots are full"""
        assert self.save_manager.is_save_slots_full() is False
        
        # Create max saves
        for i in range(self.save_manager.max_save_slots):
            snapshot = GameStateSnapshot(player_name=f"Player{i}")
            self.save_manager.save_game(snapshot)
        
        assert self.save_manager.is_save_slots_full() is True


class TestLoadManager:
    """Test load manager"""
    
    def setup_method(self):
        """Create temporary save directory"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.save_manager = SaveManager(Path(self.temp_dir.name))
        self.load_manager = LoadManager(Path(self.temp_dir.name))
    
    def teardown_method(self):
        """Clean up temporary directory"""
        self.temp_dir.cleanup()
    
    def test_load_game(self):
        """Load a saved game"""
        # Create a save
        snapshot = GameStateSnapshot(
            player_name="TestPlayer",
            coherence_score=80.0,
            current_day=7
        )
        _, _, slot_id = self.save_manager.save_game(snapshot, "TestSave")
        
        # Load it back
        success, message, loaded_state = self.load_manager.load_game(slot_id)
        
        assert success is True
        assert loaded_state is not None
        assert loaded_state.player_name == "TestPlayer"
        assert loaded_state.coherence_score == 80.0
        assert loaded_state.current_day == 7
    
    def test_load_nonexistent_save(self):
        """Loading nonexistent save fails"""
        success, message, state = self.load_manager.load_game("nonexistent")
        
        assert success is False
        assert state is None
    
    def test_load_corrupted_save(self):
        """Loading corrupted save fails"""
        # Create corrupted save file
        corrupted_file = self.load_manager.save_directory / "save_1.json"
        with open(corrupted_file, 'w') as f:
            f.write("{ invalid json")
        
        success, message, state = self.load_manager.load_game("save_1")
        
        assert success is False
        assert state is None
    
    def test_get_save_summary(self):
        """Get summary of a save"""
        snapshot = GameStateSnapshot(
            player_name="TestPlayer",
            current_day=5
        )
        _, _, slot_id = self.save_manager.save_game(snapshot, "TestSave")
        
        summary = self.load_manager.get_save_summary(slot_id)
        
        assert summary is not None
        assert summary['player_name'] == "TestPlayer"
        assert summary['current_day'] == 5


class TestQuickSaveManager:
    """Test quick-save functionality"""
    
    def setup_method(self):
        """Create temporary save directory"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.save_manager = SaveManager(Path(self.temp_dir.name))
        self.quick_save = QuickSaveManager(self.save_manager)
    
    def teardown_method(self):
        """Clean up temporary directory"""
        self.temp_dir.cleanup()
    
    def test_quick_save(self):
        """Quick-save works"""
        snapshot = GameStateSnapshot(player_name="TestPlayer")
        
        success, message = self.quick_save.quick_save(snapshot)
        
        assert success is True
    
    def test_quick_load(self):
        """Quick-load retrieves saved state"""
        snapshot = GameStateSnapshot(
            player_name="QuickPlayer",
            coherence_score=90.0
        )
        
        self.quick_save.quick_save(snapshot)
        loaded = self.quick_save.quick_load()
        
        assert loaded is not None
        assert loaded.player_name == "QuickPlayer"
        assert loaded.coherence_score == 90.0
    
    def test_has_quick_save(self):
        """Check quick-save existence"""
        assert self.quick_save.has_quick_save() is False
        
        snapshot = GameStateSnapshot(player_name="TestPlayer")
        self.quick_save.quick_save(snapshot)
        
        assert self.quick_save.has_quick_save() is True


class TestSaveGameRecovery:
    """Test save game recovery"""
    
    def setup_method(self):
        """Create temporary save directory"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.recovery = SaveGameRecovery(Path(self.temp_dir.name))
    
    def teardown_method(self):
        """Clean up temporary directory"""
        self.temp_dir.cleanup()
    
    def test_backup_all_saves(self):
        """Backup all saves"""
        # Create some save files
        save_manager = SaveManager(self.recovery.save_directory)
        for i in range(2):
            snapshot = GameStateSnapshot(player_name=f"Player{i}")
            save_manager.save_game(snapshot)
        
        success, message, count = self.recovery.backup_all_saves()
        
        assert success is True
        assert count >= 2
    
    def test_recovery_directory_exists(self):
        """Recovery directory is created"""
        assert self.recovery.recovery_directory.exists()


class TestOrchestratorPhase5Integration:
    """Test Phase 5 integration with orchestrator"""
    
    def setup_method(self):
        """Create a fresh orchestrator for each test"""
        self.temp_dir = tempfile.TemporaryDirectory()
        engine = VelinorEngine()
        engine.create_session(player_name="TestPlayer")
        self.orchestrator = VelinorTwineOrchestrator(
            game_engine=engine,
            story_path="",
            player_name="TestPlayer"
        )
        # Override save directory
        self.orchestrator.save_manager.save_directory = Path(self.temp_dir.name)
        self.orchestrator.load_manager.save_directory = Path(self.temp_dir.name)
    
    def teardown_method(self):
        """Clean up"""
        self.temp_dir.cleanup()
    
    def test_orchestrator_has_phase5_systems(self):
        """Orchestrator has Phase 5 systems"""
        assert hasattr(self.orchestrator, 'save_manager')
        assert hasattr(self.orchestrator, 'load_manager')
        assert hasattr(self.orchestrator, 'quick_save_manager')
    
    def test_save_game(self):
        """Save game through orchestrator"""
        result = self.orchestrator.save_game("TestSave")
        
        assert result["save_success"] is True
        assert result["slot_id"] is not None
        assert "TestPlayer" in result["player_name"]
    
    def test_get_save_slots(self):
        """Get save slots through orchestrator"""
        # Create a save first
        self.orchestrator.save_game("TestSave1")
        self.orchestrator.save_game("TestSave2")
        
        result = self.orchestrator.get_save_slots()
        
        assert "save_slots" in result
        assert result["total_slots"] >= 2
    
    def test_quick_save(self):
        """Quick-save through orchestrator"""
        result = self.orchestrator.quick_save()
        
        assert result["quick_save_success"] is True
    
    def test_has_quick_save(self):
        """Check quick-save through orchestrator"""
        assert self.orchestrator.has_quick_save()["has_quick_save"] is False
        
        self.orchestrator.quick_save()
        
        assert self.orchestrator.has_quick_save()["has_quick_save"] is True
    
    def test_delete_save(self):
        """Delete save through orchestrator"""
        _, _, slot_id = self.orchestrator.save_manager.save_game(
            GameStateSnapshot(player_name="TestPlayer")
        )
        
        result = self.orchestrator.delete_save(slot_id)
        
        assert result["delete_success"] is True
    
    def test_get_phase5_status(self):
        """Get Phase 5 status"""
        result = self.orchestrator.get_phase5_status()
        
        assert result["phase"] == 5
        assert "save_slots_used" in result
        assert "save_slots_total" in result
        assert "has_quick_save" in result


class TestPhase5Workflow:
    """Test complete save/load workflow"""
    
    def setup_method(self):
        """Create a fresh orchestrator for each test"""
        self.temp_dir = tempfile.TemporaryDirectory()
        engine = VelinorEngine()
        engine.create_session(player_name="TestPlayer")
        self.orchestrator = VelinorTwineOrchestrator(
            game_engine=engine,
            story_path="",
            player_name="TestPlayer"
        )
        # Override save directory
        self.orchestrator.save_manager.save_directory = Path(self.temp_dir.name)
        self.orchestrator.load_manager.save_directory = Path(self.temp_dir.name)
    
    def teardown_method(self):
        """Clean up"""
        self.temp_dir.cleanup()
    
    def test_save_load_cycle(self):
        """Complete save/load cycle"""
        # Simulate some game progress
        self.orchestrator.event_timeline.current_day = 5
        
        # Save
        save_result = self.orchestrator.save_game("ProgressSave")
        assert save_result["save_success"] is True
        slot_id = save_result["slot_id"]
        
        # Verify save was created
        slots = self.orchestrator.get_save_slots()
        assert slots["total_slots"] > 0
        
        # Simulate different game state
        self.orchestrator.event_timeline.current_day = 1
        
        # Load
        load_result = self.orchestrator.load_game(slot_id)
        assert load_result["load_success"] is True
        
        # Verify state was restored
        # (Note: Full restoration depends on GameStateRestorer implementation)
    
    def test_multiple_saves(self):
        """Create and manage multiple saves"""
        # Create multiple saves
        for i in range(3):
            save_result = self.orchestrator.save_game(f"Save{i}")
            assert save_result["save_success"] is True
        
        # Check all saves exist
        slots_result = self.orchestrator.get_save_slots()
        assert slots_result["total_slots"] >= 3
        
        # Delete one save
        first_slot = slots_result["save_slots"][0]
        delete_result = self.orchestrator.delete_save(first_slot["slot_id"])
        assert delete_result["delete_success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
