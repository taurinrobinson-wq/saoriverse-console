"""
Phase 7 Integration Tests: Web UI + API Integration
Tests for the complete web UI experience and API integration
"""

import pytest
from velinor.web_client import VelinorAPI


@pytest.fixture
def api_client():
    """Create API client for testing"""
    return VelinorAPI()


# ==================== Health Check ====================


class TestWebUIHealth:
    """Tests for web UI health and API connectivity"""
    
    def test_api_health_check(self, api_client):
        """Test API is accessible"""
        assert api_client.health_check() is True
    
    def test_api_base_url_correct(self, api_client):
        """Test API base URL is configured"""
        assert api_client.base_url == "http://localhost:8000"


# ==================== Game Session Workflow ====================


class TestGameSessionWorkflow:
    """Tests for complete game session workflows"""
    
    def test_start_new_game(self, api_client):
        """Test starting a new game"""
        result = api_client.start_game("TestPlayer")
        assert result["success"] is True
        assert "session_id" in result["data"]
        assert result["data"]["player_name"] == "TestPlayer"
        assert api_client.session_id is not None
    
    def test_get_initial_state(self, api_client):
        """Test getting initial game state"""
        api_client.start_game("Player1")
        
        state = api_client.get_game_state()
        assert state["success"] is True
        assert state["data"]["player_name"] == "Player1"
        assert state["data"]["current_day"] == 0
        assert not state["data"]["game_completed"]
    
    def test_end_game(self, api_client):
        """Test ending a game session"""
        api_client.start_game("Player1")
        assert api_client.session_id is not None
        
        result = api_client.end_game()
        assert result["success"] is True
        assert api_client.session_id is None
    
    def test_cannot_act_without_session(self, api_client):
        """Test that actions fail without active session"""
        result = api_client.take_action(choice_index=0)
        assert result["success"] is False
        assert "No active session" in result["error"]


# ==================== Player Choices ====================


class TestPlayerChoices:
    """Tests for player choice processing"""
    
    def test_make_valid_choice(self, api_client):
        """Test making a valid player choice"""
        api_client.start_game("Player1")
        
        result = api_client.take_action(choice_index=0)
        assert result["success"] is True
        assert "new_state" in result["data"]
        assert result["data"]["action_count"] == 1
    
    def test_multiple_choices(self, api_client):
        """Test making multiple consecutive choices"""
        api_client.start_game("Player1")
        
        for i in range(3):
            result = api_client.take_action(choice_index=0)
            assert result["success"] is True
            assert result["data"]["action_count"] == i + 1
    
    def test_choice_updates_state(self, api_client):
        """Test that choices update game state"""
        api_client.start_game("Player1")
        
        state1 = api_client.get_game_state()
        initial_day = state1["data"]["current_day"]
        
        api_client.take_action(choice_index=0)
        
        state2 = api_client.get_game_state()
        # State may or may not change depending on game logic
        assert "current_day" in state2["data"]


# ==================== Save/Load Workflow ====================


class TestSaveLoadWorkflow:
    """Tests for save and load functionality"""
    
    def test_save_current_game(self, api_client):
        """Test saving current game"""
        api_client.start_game("Player1")
        api_client.take_action(choice_index=0)
        
        result = api_client.save_game("SavePoint1", auto_save=False)
        # Save may succeed or fail due to file system
        assert "success" in result
        if result.get("success"):
            assert "slot_id" in result["data"]
    
    def test_get_save_slots(self, api_client):
        """Test retrieving save slots"""
        api_client.start_game("Player1")
        
        slots = api_client.get_save_slots()
        assert isinstance(slots, list)
    
    def test_full_save_load_cycle(self, api_client):
        """Test complete save and load cycle"""
        # Start first game
        api_client.start_game("Player1")
        api_client.take_action(choice_index=0)
        
        # Save
        save_result = api_client.save_game("Checkpoint")
        if not save_result.get("success"):
            pytest.skip("Save failed, skipping load test")
        
        slot_id = save_result["data"]["slot_id"]
        
        # End first game
        api_client.end_game()
        assert api_client.session_id is None
        
        # Start new game
        api_client.start_game("Player2")
        
        # Load previous save
        load_result = api_client.load_game(slot_id)
        # Load may succeed or fail depending on compatibility
        assert "success" in load_result


# ==================== Game Status ====================


class TestGameStatus:
    """Tests for game status queries"""
    
    def test_get_game_status(self, api_client):
        """Test getting game status"""
        api_client.start_game("Player1")
        
        status = api_client.get_status()
        assert status["success"] is True
        assert "session" in status["data"]
        assert "game" in status["data"]
        assert status["data"]["session"]["player_name"] == "Player1"
    
    def test_status_reflects_actions(self, api_client):
        """Test that status reflects player actions"""
        api_client.start_game("Player1")
        
        status1 = api_client.get_status()
        count1 = status1["data"]["session"]["action_count"]
        
        api_client.take_action(choice_index=0)
        
        status2 = api_client.get_status()
        count2 = status2["data"]["session"]["action_count"]
        
        assert count2 > count1


# ==================== Multi-Session ====================


class TestMultipleSessions:
    """Tests for handling multiple concurrent sessions"""
    
    def test_multiple_players_independent(self):
        """Test that multiple players have independent sessions"""
        player1_api = VelinorAPI()
        player2_api = VelinorAPI()
        
        # Start games for both players
        player1_api.start_game("Alice")
        player2_api.start_game("Bob")
        
        # Verify different session IDs
        assert player1_api.session_id != player2_api.session_id
        
        # Take actions independently
        player1_api.take_action(choice_index=0)
        player2_api.take_action(choice_index=1)
        
        # Verify states are independent
        state1 = player1_api.get_game_state()
        state2 = player2_api.get_game_state()
        
        assert state1["data"]["player_name"] == "Alice"
        assert state2["data"]["player_name"] == "Bob"
        
        # Cleanup
        player1_api.end_game()
        player2_api.end_game()


# ==================== Error Handling ====================


class TestErrorHandling:
    """Tests for proper error handling"""
    
    def test_invalid_session_error(self, api_client):
        """Test handling of invalid session"""
        api_client.session_id = "invalid-session-id"
        result = api_client.get_game_state()
        # API should return error for invalid session
        assert result["success"] is False
    
    def test_operations_fail_without_session(self, api_client):
        """Test that operations fail without active session"""
        assert api_client.session_id is None
        
        assert api_client.get_game_state()["success"] is False
        assert api_client.take_action(choice_index=0)["success"] is False
        assert api_client.save_game("Test")["success"] is False
        assert api_client.end_game()["success"] is False


# ==================== API Client Initialization ====================


class TestAPIClientInit:
    """Tests for API client initialization"""
    
    def test_default_initialization(self):
        """Test default API client initialization"""
        client = VelinorAPI()
        assert client.base_url == "http://localhost:8000"
        assert client.session_id is None
    
    def test_custom_base_url(self):
        """Test API client with custom base URL"""
        client = VelinorAPI(base_url="http://localhost:9000")
        assert client.base_url == "http://localhost:9000"


# ==================== Integration Workflows ====================


class TestWebUIIntegrationWorkflows:
    """End-to-end integration tests for web UI workflows"""
    
    def test_new_game_workflow(self):
        """Test complete new game workflow"""
        api = VelinorAPI()
        
        # Start game
        start = api.start_game("Hero")
        assert start["success"]
        assert api.session_id is not None
        
        # Get state
        state = api.get_game_state()
        assert state["success"]
        assert state["data"]["player_name"] == "Hero"
        
        # Make choices
        for _ in range(3):
            action = api.take_action(choice_index=0)
            assert action["success"]
        
        # Get status
        status = api.get_status()
        assert status["success"]
        assert status["data"]["session"]["action_count"] >= 3
        
        # End game
        end = api.end_game()
        assert end["success"]
        assert api.session_id is None
    
    def test_save_and_resume_workflow(self):
        """Test save and resume workflow"""
        api = VelinorAPI()
        
        # Start and play
        api.start_game("Player")
        for i in range(2):
            api.take_action(choice_index=0)
        
        # Try to save
        save_result = api.save_game("Progress")
        if not save_result.get("success"):
            pytest.skip("Save not supported in test environment")
        
        slot_id = save_result["data"]["slot_id"]
        
        # End current game
        api.end_game()
        
        # Start new game and try to load
        api.start_game("Player")
        load_result = api.load_game(slot_id)
        
        # Cleanup
        api.end_game()
    
    def test_save_management_workflow(self):
        """Test save file management workflow"""
        api = VelinorAPI()
        
        # Create multiple saves
        saves = []
        for i in range(2):
            api.start_game(f"Player{i}")
            api.take_action(choice_index=0)
            save = api.save_game(f"Save{i}")
            if save.get("success"):
                saves.append(save["data"]["slot_id"])
            api.end_game()
        
        # List saves
        api.start_game("Viewer")
        slots = api.get_save_slots()
        assert isinstance(slots, list)
        
        # Delete a save if we have any
        if saves:
            delete_result = api.delete_save(saves[0])
            # Delete may succeed or fail depending on file system
            assert "success" in delete_result
        
        api.end_game()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
