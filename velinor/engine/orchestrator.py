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
from .trait_system import TraitProfiler, TraitChoice, TraitType
from .coherence_calculator import CoherenceCalculator
from .npc_response_engine import NPCResponseEngine
# Try to import REMNANTS NPC manager and helper constructors
try:
    from .npc_manager import NPCManager, create_marketplace_npcs, create_marketplace_influence_map
except Exception:
    NPCManager = None
    create_marketplace_npcs = None
    create_marketplace_influence_map = None
# Optional Twine -> frontend scene mapping
try:
    from .scene_mapping import get_scene_id
except Exception:
    def get_scene_id(name: str):
        return None


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
        npc_system: Optional[NPCDialogueSystem] = None,
        player_name: str = "Player"
    ):
        self.game_engine = game_engine
        self.first_person = first_person_module
        self.npc_system = npc_system
        
        # Initialize trait system
        self.trait_profiler = TraitProfiler(player_name)
        self.coherence_calculator = CoherenceCalculator(self.trait_profiler)
        self.npc_response_engine = NPCResponseEngine(self.trait_profiler)
        
        # REMNANTS manager (for trait/influence simulation)
        self.remnants_manager = NPCManager() if NPCManager is not None else None
        # Populate REMNANTS manager with marketplace NPCs and influence map
        if self.remnants_manager and create_marketplace_npcs:
            try:
                npcs = create_marketplace_npcs()
                self.remnants_manager.add_npcs_batch(npcs)
                influence_map = create_marketplace_influence_map() if create_marketplace_influence_map else {}
                for from_npc, ripples in (influence_map or {}).items():
                    for to_npc, val in ripples.items():
                        try:
                            self.remnants_manager.set_influence(from_npc, to_npc, val)
                        except Exception:
                            continue
            except Exception:
                # Fail gracefully if population fails
                pass
        
        # Load story
        self.story_loader = TwineStoryLoader()
        if story_path:  # Only load if path provided
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
        
        # Add trait system info to initial state
        initial_state['trait_profile'] = self.trait_profiler.get_trait_summary()
        
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
        
        # Generate FirstPerson-enhanced emotional analysis if typing
        player_analysis = None
        if player_input and self.first_person:
            player_analysis = self._summarize_player_intent(player_input, player_id)
            player_summary = player_analysis.get('original_input', player_input) if isinstance(player_analysis, dict) else player_input
        else:
            player_summary = player_input
        
        # Process through Twine system
        next_state = self.twine_session.process_player_input(
            player_response=player_summary,
            choice_index=choice_index,
            player_id=player_id
        )
        
        # Attach player analysis to state for downstream use
        if player_analysis:
            next_state['player_analysis'] = player_analysis
        next_state['player_input'] = player_input
        
        # Apply game engine updates (dice rolls, stat changes, etc.)
        updated_state = self._apply_game_mechanics(next_state, player_id)
        
        # Generate NPC response with FirstPerson emotional analysis if available
        if updated_state.get('npc_name'):
            updated_state['npc_dialogue'] = self._generate_npc_dialogue(
                npc_name=updated_state['npc_name'],
                context=updated_state,
                is_multiplayer=updated_state.get('is_multiplayer', False),
                player_ids=self.multiplayer_state.player_ids if self.multiplayer_state else [player_id] if player_id else []
            )
        
        # Log the interaction
        self._log_event('player_action', {
            'player_id': player_id,
            'input': player_input,
            'passage': updated_state.get('passage_name'),
            'emotional_tone': player_analysis.get('emotional_tone') if isinstance(player_analysis, dict) else None
        })
        
        return self._format_ui_state(updated_state)
    
    def record_trait_choice(
        self,
        choice_id: str,
        choice_text: str,
        primary_trait: TraitType,
        trait_weight: float = 0.3,
        secondary_trait: Optional[TraitType] = None,
        secondary_weight: float = 0.0,
        npc_name: str = "",
        scene_name: str = "",
    ) -> Dict[str, Any]:
        """
        Record a player choice that tags a trait.
        
        Called when dialogue options are selected in scenes.
        Updates trait profile and returns current coherence state.
        
        Returns:
            Updated trait profile with coherence info
        """
        trait_choice = TraitChoice(
            choice_id=choice_id,
            dialogue_option=choice_text,
            primary_trait=primary_trait,
            trait_weight=trait_weight,
            secondary_trait=secondary_trait,
            secondary_weight=secondary_weight,
            npc_name=npc_name,
            scene_name=scene_name,
        )
        
        # Record the choice
        self.trait_profiler.record_choice(trait_choice)
        
        # Get updated coherence report
        coherence_report = self.coherence_calculator.get_coherence_report()
        
        # Log for diagnostics
        self._log_event('trait_choice', {
            'choice_id': choice_id,
            'primary_trait': primary_trait.value,
            'npc': npc_name,
            'scene': scene_name,
            'coherence': coherence_report.overall_coherence,
            'npc_trust': coherence_report.npc_trust_level,
        })
        
        return {
            'trait_profile': self.trait_profiler.get_trait_summary(),
            'coherence_report': {
                'overall_coherence': coherence_report.overall_coherence,
                'level': coherence_report.level.name,
                'primary_pattern': coherence_report.primary_pattern.value,
                'npc_trust_level': coherence_report.npc_trust_level,
                'dialogue_depth': coherence_report.dialogue_depth,
            }
        }
    
    def get_trait_status(self) -> Dict[str, Any]:
        """Get current player trait status for UI display."""
        coherence_report = self.coherence_calculator.get_coherence_report()
        return {
            'trait_profile': self.trait_profiler.get_trait_summary(),
            'coherence_report': {
                'overall_coherence': coherence_report.overall_coherence,
                'level': coherence_report.level.name,
                'primary_pattern': coherence_report.primary_pattern.value,
                'secondary_pattern': coherence_report.secondary_pattern.value if coherence_report.secondary_pattern else None,
                'pattern_strength': coherence_report.pattern_strength,
                'npc_trust_level': coherence_report.npc_trust_level,
                'dialogue_depth': coherence_report.dialogue_depth,
                'summary': coherence_report.summary(),
            },
            'npc_conflicts': {
                npc: self.npc_response_engine.get_npc_conflict_level(npc)
                for npc in ['Saori', 'Ravi', 'Nima', 'Malrik', 'Elenya', 'Coren']
            }
        }
        """
        Use FirstPerson to analyze and contextualize player's intent.
        Extracts emotional tone, themes, and context for nuanced NPC responses.
        """
        if not self.first_person:
            return player_input
        
        try:
            # Run FirstPerson analysis on player input
            analysis = self.first_person.handle_conversation_turn(
                user_input=player_input,
                glyph=None  # Can pass glyph data if available
            )
            
            # Extract emotional tone and theme for story routing
            affect = analysis.get('affect_analysis', {})
            theme = analysis.get('detected_theme', 'general')
            tone = affect.get('tone', 'neutral')
            
            # Create contextualized summary that preserves original intent
            # but adds emotional/thematic metadata for NPC responses
            summary = {
                'original_input': player_input,
                'emotional_tone': tone,
                'detected_theme': theme,
                'valence': affect.get('valence', 0),
                'intensity': affect.get('intensity', 0.5),
                'memory_context': analysis.get('memory_context', {})
            }
            
            return summary
        except Exception as e:
            # Graceful fallback if FirstPerson unavailable
            return {'original_input': player_input, 'error': str(e)}
    
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

        # Apply metadata from the last chosen choice (tone effects, npc resonance, story beats)
        last_choice_meta = story_state.get('last_choice_metadata', {}) or {}
        if last_choice_meta:
            # Tone effects: map small float values to engine stat deltas (engine uses 0-1 floats)
            tone_effects = last_choice_meta.get('tone_effects', {})
            if tone_effects:
                # Apply to player stats via game engine (expects normalized floats)
                for stat, delta in tone_effects.items():
                    try:
                        # If the tone effects are expressed as small floats (-0.2..0.2), apply directly
                        delta_float = float(delta)
                        self.game_engine.update_stat(stat, delta_float)
                    except Exception:
                        # Fallback: try converting from percent-like values
                        try:
                            d = int(delta)
                            self.game_engine.update_stat(stat, d / 100.0)
                        except Exception:
                            pass

                # Also apply to REMNANTS manager if available (affects NPC trait profiles)
                if self.remnants_manager:
                    try:
                        self.remnants_manager.apply_tone_effects(tone_effects)
                    except Exception:
                        pass

            # NPC resonance: direct per-NPC nudges (treated as trust changes)
            npc_res = last_choice_meta.get('npc_resonance', {})
            if npc_res and self.remnants_manager:
                for npc_name, val in npc_res.items():
                    try:
                        if npc_name in self.remnants_manager.npcs:
                            # Treat as a small trust delta (0.1 scale)
                            delta_val = float(val)
                            self.remnants_manager.npcs[npc_name].adjust_trait('trust', delta_val)
                    except Exception:
                        continue

            # Mark story beats if author provided them
            beat = last_choice_meta.get('mark_story_beat')
            if beat:
                try:
                    self.game_engine.mark_story_beat(beat)
                except Exception:
                    pass
        
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
        Adapts tone, empathy, and responsiveness based on:
        - Player's emotional state (via FirstPerson analysis)
        - Conversation history and recurring themes
        - NPC personality and story context
        - Group dynamics (if multiplayer)
        """
        if not self.first_person:
            # Fallback if FirstPerson not available
            if self.npc_system:
                npc = self.npc_system.get_npc(npc_name)
                if npc:
                    return f"{npc_name}: I'm listening. Tell me more."
            return f"{npc_name}: [awaiting your words]"
        
        try:
            # Get player's emotional analysis from FirstPerson
            player_context = context.get('player_analysis', {})
            original_input = context.get('player_input', '')
            
            if isinstance(player_context, dict) and 'emotional_tone' in player_context:
                emotional_tone = player_context['emotional_tone']
                theme = player_context['detected_theme']
                valence = player_context.get('valence', 0)
                intensity = player_context.get('intensity', 0.5)
                memory = player_context.get('memory_context', {})
            else:
                # Fallback analysis
                emotional_tone = 'neutral'
                theme = 'general'
                valence = 0
                intensity = 0.5
                memory = {}
            
            # Get NPC personality if available
            npc_name_clean = npc_name.lower()
            npc_personality = None
            if self.npc_system:
                npc = self.npc_system.get_npc(npc_name_clean)
                if npc:
                    npc_personality = npc.personality
            
            # Build dialogue response using FirstPerson with emotional awareness
            dialogue_base = self._generate_emotionally_aware_response(
                npc_name=npc_name,
                player_input=original_input,
                emotional_tone=emotional_tone,
                theme=theme,
                valence=valence,
                intensity=intensity,
                memory=memory,
                npc_personality=npc_personality,
                is_multiplayer=is_multiplayer
            )
            
            return dialogue_base
        
        except Exception as e:
            return f"{npc_name}: [I'm here, but having trouble finding words right now]"
    
    def _generate_emotionally_aware_response(
        self,
        npc_name: str,
        player_input: str,
        emotional_tone: str,
        theme: str,
        valence: float,
        intensity: float,
        memory: Dict,
        npc_personality: Optional[Any],
        is_multiplayer: bool
    ) -> str:
        """
        Generate nuanced NPC response using FirstPerson's emotional analysis.
        
        Response adapts based on:
        - Player's emotional valence (positive/negative)
        - Intensity of feeling
        - Detected theme (what they're talking about)
        - Whether this theme is recurring
        - Group dynamics if multiplayer
        """
        
        # Base response openings adjusted by emotional state
        response_openings = {
            'uplifting': [
                f"{npc_name}: I feel that brightness too.",
                f"{npc_name}: That's a light worth holding.",
            ],
            'heavy': [
                f"{npc_name}: I hear the weight in that.",
                f"{npc_name}: The gravity of it—I feel it too.",
            ],
            'reflective': [
                f"{npc_name}: There's something to sit with there.",
                f"{npc_name}: That deserves thought.",
            ],
            'curious': [
                f"{npc_name}: Tell me more about that.",
                f"{npc_name}: I'm curious where that's leading.",
            ]
        }
        
        # Select opening based on tone
        opening_options = response_openings.get(emotional_tone, response_openings['curious'])
        opening = opening_options[0]  # Could randomize
        
        # Middle section acknowledges specific themes
        theme_acknowledgments = {
            'grief': "Loss shapes us in ways words sometimes can't reach.",
            'joy': "Joy that's felt this deeply—that matters.",
            'general': "What you're feeling is real.",
        }
        
        middle = theme_acknowledgments.get(theme, "What you're naming has weight.")
        
        # Add memory awareness if conversation history exists
        if memory.get('has_context') and memory.get('num_turns', 0) > 1:
            recurring = memory.get('recurring_themes', [])
            if recurring:
                middle += f" And I'm noticing {recurring[0]} keeps coming back to you."
        
        # Closing invites deeper exploration, adjusts for intensity
        if intensity > 0.7:
            closing = "What needs to be said about it?"
        elif intensity < 0.3:
            closing = "What's sitting underneath that?"
        else:
            closing = "What would help you carry this?"
        
        # Build multiplayer awareness if needed
        response = f"{opening} {middle} {closing}"
        
        if is_multiplayer and len(self.multiplayer_state.active_players) > 1:
            response += "\n(The others are listening too.)"
        
        return response
    
    def _format_ui_state(self, story_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format story state for UI consumption.
        Structures data for rendering in Twine UI, web frontend, etc.
        """
        # Include optional frontend scene id mapping when available so the
        # web UI can either render Twine content or use a local scene graph.
        scene_id = None
        try:
            scene_id = get_scene_id(story_state.get('passage_name'))
        except Exception:
            scene_id = None

        return {
            'passage_id': story_state.get('passage_id'),
            'passage_name': story_state.get('passage_name'),
            'scene_id': scene_id,
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
