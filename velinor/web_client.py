"""
Phase 7: Web UI - API Client Library
TypeScript/JavaScript client for calling Velinor Phase 6 API

This file would be converted to TypeScript (api.ts) in the actual Next.js project
For now, creating a Python wrapper for testing purposes
"""

import requests
from typing import Dict, Optional, Any, List
from dataclasses import dataclass

# Configuration
API_BASE_URL = "http://localhost:8000"

@dataclass
class GameState:
    session_id: str
    player_name: str
    current_phase: str
    current_day: int
    game_completed: bool
    available_choices: List[str]
    orchestrator_status: Dict[str, Any]

@dataclass
class SaveSlot:
    slot_id: str
    player_name: str
    save_name: str
    timestamp: str
    day: int
    phase: str

class VelinorAPI:
    """Python client for Velinor Game API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    # ==================== Game Session ====================
    
    def start_game(self, player_name: str = "Traveler") -> Dict[str, Any]:
        """Start a new game session"""
        response = requests.post(
            f"{self.base_url}/api/game/start",
            params={"player_name": player_name}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.session_id = data["data"]["session_id"]
            return data
        return {"success": False, "error": f"HTTP {response.status_code}"}
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state"""
        if not self.session_id:
            return {"success": False, "error": "No active session"}
        
        response = requests.get(f"{self.base_url}/api/game/{self.session_id}")
        return response.json() if response.status_code == 200 else {"success": False}
    
    def end_game(self) -> Dict[str, Any]:
        """End current game session"""
        if not self.session_id:
            return {"success": False, "error": "No active session"}
        
        response = requests.delete(f"{self.base_url}/api/game/{self.session_id}")
        if response.status_code == 200:
            self.session_id = None
            return response.json()
        return {"success": False}
    
    # ==================== Game Actions ====================
    
    def take_action(self, choice_index: Optional[int] = None, player_input: Optional[str] = None) -> Dict[str, Any]:
        """Process player action"""
        if not self.session_id:
            return {"success": False, "error": "No active session"}
        
        response = requests.post(
            f"{self.base_url}/api/game/{self.session_id}/action",
            json={
                "choice_index": choice_index,
                "player_input": player_input
            }
        )
        return response.json() if response.status_code == 200 else {"success": False}
    
    # ==================== Save/Load ====================
    
    def save_game(self, save_name: str, auto_save: bool = False) -> Dict[str, Any]:
        """Save current game"""
        if not self.session_id:
            return {"success": False, "error": "No active session"}
        
        response = requests.post(
            f"{self.base_url}/api/game/{self.session_id}/save",
            json={"save_name": save_name, "auto_save": auto_save}
        )
        return response.json() if response.status_code == 200 else {"success": False}
    
    def load_game(self, slot_id: str) -> Dict[str, Any]:
        """Load a saved game"""
        if not self.session_id:
            return {"success": False, "error": "No active session"}
        
        response = requests.post(
            f"{self.base_url}/api/game/{self.session_id}/load",
            json={"slot_id": slot_id}
        )
        return response.json() if response.status_code == 200 else {"success": False}
    
    def get_save_slots(self) -> List[SaveSlot]:
        """Get all save slots"""
        if not self.session_id:
            return []
        
        response = requests.get(f"{self.base_url}/api/game/{self.session_id}/save-slots")
        if response.status_code == 200:
            data = response.json()
            slots = data.get("data", {}).get("save_slots", [])
            return [SaveSlot(**slot) for slot in slots]
        return []
    
    def delete_save(self, slot_id: str) -> Dict[str, Any]:
        """Delete a save slot"""
        response = requests.delete(f"{self.base_url}/api/game/save/{slot_id}")
        return response.json() if response.status_code == 200 else {"success": False}
    
    # ==================== Status ====================
    
    def get_status(self) -> Dict[str, Any]:
        """Get game status"""
        if not self.session_id:
            return {"success": False, "error": "No active session"}
        
        response = requests.get(f"{self.base_url}/api/game/{self.session_id}/status")
        return response.json() if response.status_code == 200 else {"success": False}
    
    def health_check(self) -> bool:
        """Check if API is alive"""
        response = requests.get(f"{self.base_url}/health")
        return response.status_code == 200


# Export for use
__all__ = ['VelinorAPI', 'GameState', 'SaveSlot']
