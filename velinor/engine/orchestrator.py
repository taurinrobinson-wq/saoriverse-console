"""
Velinor Game Engine + Twine/FirstPerson Integration
====================================================

This module orchestrates the game loop, connecting:
- Velinor game engine (state management, NPCs, dice rolls)
- Twine story system (narrative flow, choices)
- FirstPerson orchestrator (dynamic dialogue, emotional resonance)
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import json
from datetime import datetime

from .core import VelinorEngine, GameSession
from .npc_system import NPCDialogueSystem
from .twine_adapter import TwineGameSession, TwineStoryLoader, DialogueParser


@dataclass
class MultiplayerState:
    """Tracks multiplayer session state."""
    player_ids: List[str]
    active_players: set
    input_buffer: Dict[str, str]  # player_id -> current input
    last_action_timestamp: Dict[str, datetime]
    
    def add_input(self, player_id: str, input_text: str) -> None:
        """Add player input to buffer."""
        self.input_buffer[player_id] = input_text
        self.last_action_timestamp[player_id] = datetime.now()
    
    def get_active_inputs(self) -> Dict[str, str]:
        """Get all active player inputs."""
        return {
            pid: text for pid, text in self.input_buffer.items()
            if pid in self.active_players
        }
    
    def clear_inputs(self) -> None:
        """Clear input buffer after processing."""
        self.input_buffer.clear()


class VelinorTwineOrchestrator:
    """
    Main orchestrator connecting game engine, Twine narrative, and FirstPerson dialogue.
    
    This is the core game loop controller that:
    1. Renders current story passage
    2. Collects player input (typed or choices)
    3. Processes through FirstPerson for dialogue generation
    4. Updates game state via engine
    5. Advances story to next passage
    """
    
    def __init__(
        self,
        game_engine: VelinorEngine,
        story_path: str,
        first_person_module: Optional[Any] = None,
        npc_system: Optional[NPCDialogueSystem] = None
    ):
        self.game_engine = game_engine
        self.first_person = first_person_module
        self.npc_system = npc_system
        
        # Load story
        self.story_loader = TwineStoryLoader()
        self.story_loader.load_from_json(story_path)
        
        # Initialize session
        self.twine_session: Optional[TwineGameSession] = None
        self.multiplayer_state: Optional[MultiplayerState] = None
        self.game_log: List[Dict[str, Any]] = []
    
    def start_game(
        self,
        is_multiplayer: bool = False,
        player_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Initialize new game session.
        
        Args:
            is_multiplayer: Enable multiplayer mode
            player_ids: List of player IDs for multiplayer
        
        Returns:
            Initial passage rendering
        """
        # Start Twine session
        self.twine_session = TwineGameSession(
            story_loader=self.story_loader,
            game_engine=self.game_engine,
            first_person_orchestrator=self.first_person
        )
        
        # Setup multiplayer if needed
        if is_multiplayer and player_ids:
            self.multiplayer_state = MultiplayerState(
                player_ids=player_ids,
                active_players=set(player_ids),
                input_buffer={},
                last_action_timestamp={}
            )
        
        # Render starting passage
        initial_state = self.twine_session.start_story()
        self._log_event('game_started', initial_state)
        
        return self._format_ui_state(initial_state)
    
    def process_player_action(
        self,
        player_input: str,
        choice_index: Optional[int] = None,
        player_id: Optional[str] = None,
        manual_clarifying_response: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a player action (typed input or choice selection).
        
        Args:
            player_input: Free-text player response or choice description
            choice_index: Index of selected choice (alternative to typed input)
            player_id: ID of player taking action (for multiplayer)
            manual_clarifying_response: Player's response to clarifying question
        
        Returns:
            Updated game state with next passage and any game changes
        """
        if not self.twine_session:
            raise RuntimeError("Game not started")
        
        # Buffer input in multiplayer
        if self.multiplayer_state and player_id:
            self.multiplayer_state.add_input(player_id, player_input)
            # In multiplayer, might wait for all players or process individually
            # For now, process immediately but tag with player
        
        # Generate FirstPerson-enhanced dialogue summary if typing
        if player_input and self.first_person:
            player_summary = self._summarize_player_intent(player_input, player_id)
        else:
            player_summary = player_input
        
        # Process through Twine system
        next_state = self.twine_session.process_player_input(
            player_response=player_summary,
            choice_index=choice_index,
            player_id=player_id
        )
        
        # Apply game engine updates (dice rolls, stat changes, etc.)
        updated_state = self._apply_game_mechanics(next_state, player_id)
        
        # Generate NPC response with FirstPerson if available
        if self.npc_system and updated_state.get('npc_name'):
            updated_state['npc_dialogue'] = self._generate_npc_dialogue(
                npc_name=updated_state['npc_name'],
                context=updated_state,
                is_multiplayer=updated_state.get('is_multiplayer', False),
                player_ids=self.multiplayer_state.player_ids if self.multiplayer_state else [player_id]
            )
        
        # Log the interaction
        self._log_event('player_action', {
            'player_id': player_id,
            'input': player_input,
            'passage': updated_state.get('passage_name')
        })
        
        return self._format_ui_state(updated_state)
    
    def _summarize_player_intent(self, player_input: str, player_id: Optional[str]) -> str:
        """
        Use FirstPerson to summarize player's intent from typed input.
        Makes vague responses more specific for story routing.
        """
        if not self.first_person:
            return player_input
        
        try:
            # Call FirstPerson's intent summarization
            # This would integrate with your FirstPerson system
            summary = f"[Intent: {player_input[:50]}...]"
            return summary
        except Exception:
            return player_input
    
    def _apply_game_mechanics(self, story_state: Dict[str, Any], player_id: Optional[str]) -> Dict[str, Any]:
        """
        Apply game mechanics based on story actions.
        Handles dice rolls, stat changes, NPC interactions, location changes.
        """
        story_state = story_state.copy()
        
        # Check for dice roll in passage
        if 'dice_roll' in story_state:
            roll_result = self._execute_dice_roll(story_state['dice_roll'])
            story_state['last_dice_roll'] = roll_result
            
            # Modify story based on roll (e.g., success/failure branches)
            if not roll_result['success']:
                story_state['consequence'] = "Your roll came up short. The path ahead is uncertain."
        
        # Update player stats if story indicates changes
        if 'stat_change' in story_state:
            self._apply_stat_changes(story_state['stat_change'], player_id)
        
        # Trigger background change via callback
        if 'background' in story_state and story_state['background']:
            self.twine_session._trigger_callback('on_background_change', {
                'background': story_state['background']
            })
        
        return story_state
    
    def _execute_dice_roll(self, roll_spec: str) -> Dict[str, Any]:
        """
        Execute a dice roll specified in story (e.g., "d20+wisdom").
        Returns roll result with success determination.
        """
        # Parse roll specification (e.g., "d20", "d6+2", "d20+wisdom")
        import re
        
        match = re.match(r'd(\d+)([\+\-])?(\w+)?', roll_spec)
        if not match:
            return {'success': True, 'raw_roll': 0}
        
        dice_type = int(match.group(1))
        modifier_sign = match.group(2) or '+'
        modifier_name = match.group(3)
        
        # Roll dice
        roll = self.game_engine.roll_with_modifiers(1, dice_type, modifier_name or 'resolve')
        
        # Determine success (typically DC 10)
        success = roll >= 10
        
        return {
            'raw_roll': roll,
            'success': success,
            'dice_type': dice_type,
            'modifier': modifier_name
        }
    
    def _apply_stat_changes(self, changes: Dict[str, int], player_id: Optional[str]) -> None:
        """Apply stat changes to player."""
        if not self.game_engine.session or not self.game_engine.session.player:
            return
        
        player = self.game_engine.session.player
        for stat, delta in changes.items():
            current = getattr(player, stat, 0)
            setattr(player, stat, max(0, min(100, current + delta)))
    
    def _generate_npc_dialogue(
        self,
        npc_name: str,
        context: Dict[str, Any],
        is_multiplayer: bool,
        player_ids: List[str]
    ) -> str:
        """
        Generate dynamic NPC dialogue using FirstPerson orchestrator.
        Adapts tone based on player choices, personality, and group composition.
        """
        if not self.npc_system or not self.first_person:
            return f"{npc_name}: [dialogue pending]"
        
        try:
            # Get NPC instance
            npc = self.npc_system.get_npc(npc_name)
            if not npc:
                return f"{npc_name}: I'm not sure how to respond to that."
            
            # Build context for FirstPerson
            dialogue_context = {
                'npc_personality': npc.personality,
                'player_count': len(player_ids),
                'player_choices': context.get('last_player_action'),
                'story_progression': context.get('passage_name'),
                'dice_roll': context.get('last_dice_roll'),
            }
            
            # Generate dialogue via FirstPerson
            # This would call your FirstPerson system to generate a response
            dialogue = f"{npc_name}: I hear what you're saying..."
            
            return dialogue
        
        except Exception as e:
            return f"{npc_name}: [error generating dialogue: {str(e)}]"
    
    def _format_ui_state(self, story_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format story state for UI consumption.
        Structures data for rendering in Twine UI, web frontend, etc.
        """
        return {
            'passage_id': story_state.get('passage_id'),
            'passage_name': story_state.get('passage_name'),
            'main_dialogue': story_state.get('dialogue'),
            'npc_name': story_state.get('npc_name'),
            'npc_dialogue': story_state.get('npc_dialogue'),
            'background_image': story_state.get('background'),
            'choices': story_state.get('choices', []),
            'clarifying_question': story_state.get('clarifying_question'),
            'has_clarifying_question': story_state.get('has_clarifying_question', False),
            'is_multiplayer': story_state.get('is_multiplayer', False),
            'dice_roll': story_state.get('last_dice_roll'),
            'game_state': {
                'current_location': getattr(self.game_engine.session, 'current_location', None),
                'player_stats': self._get_player_stats(),
            }
        }
    
    def _get_player_stats(self) -> Dict[str, int]:
        """Extract current player stats."""
        if not self.game_engine.session or not self.game_engine.session.player:
            return {}
        
        player = self.game_engine.session.player
        return {
            'courage': player.courage,
            'wisdom': player.wisdom,
            'empathy': player.empathy,
            'resolve': player.resolve,
            'resonance': player.resonance,
        }
    
    def _log_event(self, event_type: str, data: Any) -> None:
        """Log game event for debugging and replay."""
        self.game_log.append({
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        })
    
    def get_game_log(self) -> List[Dict[str, Any]]:
        """Retrieve full game log."""
        return self.game_log
    
    def save_game(self, save_path: str) -> None:
        """Save game state to file."""
        save_data = {
            'timestamp': datetime.now().isoformat(),
            'story_context': {
                'current_passage': self.twine_session.context.current_passage_id if self.twine_session else None,
                'visited_passages': list(self.twine_session.context.visited_passages) if self.twine_session else [],
                'dialogue_log': self.twine_session.context.dialogue_log if self.twine_session else [],
            },
            'game_state': self._get_player_stats(),
            'game_log': self.game_log
        }
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)
    
    def load_game(self, save_path: str) -> Dict[str, Any]:
        """Load game state from file."""
        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        # Restore story context
        if self.twine_session:
            passage_id = save_data['story_context']['current_passage']
            if passage_id:
                self.twine_session.context.current_passage_id = passage_id
                self.twine_session.context.visited_passages = set(
                    save_data['story_context']['visited_passages']
                )
                self.twine_session.context.dialogue_log = save_data['story_context']['dialogue_log']
        
        return self._format_ui_state(
            self.twine_session._render_passage(
                save_data['story_context']['current_passage']
            )
        ) if self.twine_session else {}
