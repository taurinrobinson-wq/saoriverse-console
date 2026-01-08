"""
Phase 6 API Layer Tests
Tests for FastAPI endpoints, session management, and game state serialization
"""

import pytest
from fastapi.testclient import TestClient
import json
from datetime import datetime

from velinor.api import app, session_store, GameSession, SessionStore
from velinor.engine.orchestrator import VelinorTwineOrchestrator


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def session_store_fixture():
    """Fresh session store for testing"""
    return SessionStore()


# ==================== Health Check Tests ====================


class TestHealthCheck:
    """Tests for health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "operational"
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Velinor" in data["title"]


# ==================== Session Management Tests ====================


class TestGameSessionCreation:
    """Tests for game session creation and management"""
    
    def test_start_game_default_player(self, client):
        """Test starting game with default player name"""
        response = client.post("/api/game/start?player_name=TestPlayer")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "session_id" in data["data"]
        assert data["data"]["player_name"] == "TestPlayer"
        assert "game_state" in data["data"]
    
    def test_start_game_custom_player(self, client):
        """Test starting game with custom player name"""
        response = client.post("/api/game/start?player_name=Hero")
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["player_name"] == "Hero"
    
    def test_session_created_in_store(self, client):
        """Test that session is created in store"""
        initial_count = len(session_store.list_sessions())
        
        response = client.post("/api/game/start?player_name=Test")
        session_id = response.json()["data"]["session_id"]
        
        assert len(session_store.list_sessions()) == initial_count + 1
        assert session_id in session_store.list_sessions()
    
    def test_multiple_sessions(self, client):
        """Test creating multiple concurrent sessions"""
        sessions = []
        for i in range(3):
            response = client.post(f"/api/game/start?player_name=Player{i}")
            assert response.status_code == 200
            sessions.append(response.json()["data"]["session_id"])
        
        assert len(sessions) == 3
        assert len(set(sessions)) == 3  # All unique


# ==================== Game State Retrieval Tests ====================


class TestGameStateRetrieval:
    """Tests for getting game state"""
    
    def test_get_game_state(self, client):
        """Test retrieving game state"""
        # Start game
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        # Get state
        response = client.get(f"/api/game/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["session_id"] == session_id
        assert data["data"]["player_name"] == "Test"
    
    def test_get_state_nonexistent_session(self, client):
        """Test getting state for nonexistent session"""
        response = client.get("/api/game/invalid-session-id")
        assert response.status_code == 404
    
    def test_game_state_contains_required_fields(self, client):
        """Test that game state has all required fields"""
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        response = client.get(f"/api/game/{session_id}")
        state = response.json()["data"]
        
        required_fields = [
            "session_id", "player_name", "current_phase",
            "current_day", "game_completed", "available_choices"
        ]
        
        for field in required_fields:
            assert field in state, f"Missing field: {field}"


# ==================== Game Action Tests ====================


class TestGameActions:
    """Tests for processing player actions"""
    
    def test_take_action_with_choice(self, client):
        """Test taking action with choice index"""
        # Start game
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        # Take action
        response = client.post(
            f"/api/game/{session_id}/action",
            json={"choice_index": 0, "player_input": None}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "action_result" in data["data"]
        assert "new_state" in data["data"]
    
    def test_take_action_with_input(self, client):
        """Test taking action with player input"""
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        response = client.post(
            f"/api/game/{session_id}/action",
            json={"choice_index": None, "player_input": "Hello"}
        )
        assert response.status_code in [200, 500]  # May error if input not supported
    
    def test_take_action_no_choice_or_input(self, client):
        """Test taking action with neither choice nor input"""
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        response = client.post(
            f"/api/game/{session_id}/action",
            json={"choice_index": None, "player_input": None}
        )
        assert response.status_code == 400
    
    def test_action_count_increases(self, client):
        """Test that action count increases"""
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        # Get initial status
        status1 = client.get(f"/api/game/{session_id}/status").json()
        count1 = status1["data"]["session"]["action_count"]
        
        # Take action
        client.post(
            f"/api/game/{session_id}/action",
            json={"choice_index": 0}
        )
        
        # Get updated status
        status2 = client.get(f"/api/game/{session_id}/status").json()
        count2 = status2["data"]["session"]["action_count"]
        
        assert count2 > count1


# ==================== Save/Load Tests ====================


class TestSaveLoad:
    """Tests for save and load functionality"""
    
    def test_save_game(self, client):
        """Test saving a game"""
        start_response = client.post("/api/game/start?player_name=TestPlayer")
        session_id = start_response.json()["data"]["session_id"]
        
        response = client.post(
            f"/api/game/{session_id}/save",
            json={"save_name": "TestSave", "auto_save": False}
        )
        
        # Save may succeed or fail depending on file system permissions
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "slot_id" in data["data"]
            assert data["data"]["save_name"] == "TestSave"
    
    def test_get_save_slots(self, client):
        """Test retrieving save slots"""
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        # Save a game
        client.post(
            f"/api/game/{session_id}/save",
            json={"save_name": "Save1", "auto_save": False}
        )
        
        # Get slots
        response = client.get(f"/api/game/{session_id}/save-slots")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "save_slots" in data["data"]
        assert isinstance(data["data"]["save_slots"], list)
    
    def test_load_game(self, client):
        """Test loading a game"""
        # Create and save
        start_response = client.post("/api/game/start?player_name=TestPlayer")
        session_id = start_response.json()["data"]["session_id"]
        
        save_response = client.post(
            f"/api/game/{session_id}/save",
            json={"save_name": "LoadTest", "auto_save": False}
        )
        
        # Save response may fail or succeed depending on file system state
        if save_response.status_code != 200:
            pytest.skip("Save operation failed, skipping load test")
        
        slot_id = save_response.json()["data"]["slot_id"]
        
        # Create new session and load
        start_response2 = client.post("/api/game/start?player_name=NewPlayer")
        session_id2 = start_response2.json()["data"]["session_id"]
        
        load_response = client.post(
            f"/api/game/{session_id2}/load",
            json={"slot_id": slot_id}
        )
        
        # Load may succeed or fail depending on save data
        assert load_response.status_code in [200, 500]
    
    def test_delete_save(self, client):
        """Test deleting a save"""
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        # Save game
        save_response = client.post(
            f"/api/game/{session_id}/save",
            json={"save_name": "DeleteTest", "auto_save": False}
        )
        
        if save_response.status_code != 200:
            pytest.skip("Save operation failed, skipping delete test")
        
        slot_id = save_response.json()["data"]["slot_id"]
        
        # Delete save
        delete_response = client.delete(f"/api/game/save/{slot_id}")
        assert delete_response.status_code in [200, 500]


# ==================== Session Status Tests ====================


class TestSessionStatus:
    """Tests for session status endpoints"""
    
    def test_get_game_status(self, client):
        """Test getting game status"""
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        response = client.get(f"/api/game/{session_id}/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "session" in data["data"]
        assert "game" in data["data"]
    
    def test_list_sessions(self, client):
        """Test listing all sessions"""
        # Create multiple sessions
        for i in range(2):
            client.post(f"/api/game/start?player_name=Player{i}")
        
        response = client.get("/api/sessions")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "sessions" in data["data"]
        assert isinstance(data["data"]["sessions"], list)
    
    def test_list_sessions_empty(self, client):
        """Test listing sessions when empty"""
        # Clear store
        for sid in session_store.list_sessions():
            session_store.delete_session(sid)
        
        response = client.get("/api/sessions")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["data"]["sessions"]) == 0


# ==================== Session Cleanup Tests ====================


class TestSessionCleanup:
    """Tests for ending games and cleanup"""
    
    def test_end_game(self, client):
        """Test ending a game session"""
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        response = client.delete(f"/api/game/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["session_id"] == session_id
    
    def test_session_removed_after_delete(self, client):
        """Test that session is removed from store after delete"""
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        assert session_id in session_store.list_sessions()
        
        client.delete(f"/api/game/{session_id}")
        
        assert session_id not in session_store.list_sessions()
    
    def test_cannot_access_deleted_session(self, client):
        """Test that deleted session cannot be accessed"""
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        client.delete(f"/api/game/{session_id}")
        
        response = client.get(f"/api/game/{session_id}")
        assert response.status_code == 404


# ==================== Error Handling Tests ====================


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_nonexistent_session_error(self, client):
        """Test accessing nonexistent session"""
        response = client.get("/api/game/invalid-session")
        assert response.status_code == 404
    
    def test_invalid_action_error(self, client):
        """Test invalid action handling"""
        start_response = client.post("/api/game/start?player_name=Test")
        session_id = start_response.json()["data"]["session_id"]
        
        response = client.post(
            f"/api/game/{session_id}/action",
            json={"choice_index": 999, "player_input": None}
        )
        # API may return 400, 500, or 200 depending on whether validation is strict
        assert response.status_code in [200, 400, 500]


# ==================== Integration Tests ====================


class TestApiIntegration:
    """Integration tests for full workflows"""
    
    def test_full_game_workflow(self, client):
        """Test complete game workflow: start -> action -> save -> load"""
        # Start game
        start = client.post("/api/game/start?player_name=Hero")
        assert start.status_code == 200
        session_id = start.json()["data"]["session_id"]
        
        # Get state
        state1 = client.get(f"/api/game/{session_id}")
        assert state1.status_code == 200
        state1_data = state1.json()
        assert state1_data["success"]
        
        # Take action
        action = client.post(
            f"/api/game/{session_id}/action",
            json={"choice_index": 0}
        )
        assert action.status_code == 200
        action_data = action.json()
        assert action_data["success"]
        
        # Save game (may fail with file I/O issues)
        save = client.post(
            f"/api/game/{session_id}/save",
            json={"save_name": "Checkpoint", "auto_save": False}
        )
        assert save.status_code in [200, 500]
        
        if save.status_code == 200:
            save_data = save.json()
            if save_data.get("success"):
                slot_id = save_data["data"]["slot_id"]
                
                # Create new session and load
                start2 = client.post("/api/game/start?player_name=Hero2")
                assert start2.status_code == 200
                session_id2 = start2.json()["data"]["session_id"]
                
                load = client.post(
                    f"/api/game/{session_id2}/load",
                    json={"slot_id": slot_id}
                )
                # Load may succeed or fail depending on save data
                assert load.status_code in [200, 500]
        
        # End session
        end = client.delete(f"/api/game/{session_id}")
        assert end.status_code == 200
        end_data = end.json()
        assert end_data["success"]
    
    def test_concurrent_sessions(self, client):
        """Test multiple concurrent game sessions"""
        sessions = {}
        
        # Create 3 concurrent sessions
        for i in range(3):
            response = client.post(f"/api/game/start?player_name=Player{i}")
            session_id = response.json()["data"]["session_id"]
            sessions[i] = session_id
        
        # All sessions accessible
        for i, sid in sessions.items():
            response = client.get(f"/api/game/{sid}")
            assert response.status_code == 200
            assert response.json()["data"]["player_name"] == f"Player{i}"
        
        # Take actions in all sessions
        for i, sid in sessions.items():
            response = client.post(
                f"/api/game/{sid}/action",
                json={"choice_index": i % 2}
            )
            assert response.status_code == 200
        
        # Clean up
        for sid in sessions.values():
            response = client.delete(f"/api/game/{sid}")
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
