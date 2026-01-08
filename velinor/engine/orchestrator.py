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
from .event_timeline import EventTimeline, CollapsePhase, AftermathPath
from .collapse_scene import CollapseTriggerScene, ImmediateAftermathScene, AftermathPathDivergence
from .ending_system import EndingManager, CoreLinkChoice, EndingType
from .corelink_scene import CoreLinkScene
from .game_state import GameStateSnapshot, GameStateBuilder
from .save_system import SaveManager, QuickSaveManager
from .load_system import LoadManager, SaveGameRecovery
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
        
        # Initialize trait system (Phase 1 & 2)
        self.trait_profiler = TraitProfiler(player_name)
        self.coherence_calculator = CoherenceCalculator(self.trait_profiler)
        self.npc_response_engine = NPCResponseEngine(self.trait_profiler)
        
        # Initialize Phase 3 systems
        self.event_timeline = EventTimeline()
        self.collapse_trigger_scene = CollapseTriggerScene()
        self.aftermath_scene = ImmediateAftermathScene()
        
        # Initialize Phase 4 systems (Ending)
        self.ending_manager = EndingManager()
        self.corelink_scene = CoreLinkScene()
        
        # Initialize Phase 5 systems (Save/Load)
        self.save_manager = SaveManager()
        self.load_manager = LoadManager()
        self.quick_save_manager = QuickSaveManager(self.save_manager)
        self.save_recovery = SaveGameRecovery()
        
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
    
    # ===== PHASE 3: COLLAPSE EVENT SYSTEM =====
    
    def advance_game_day(self) -> Dict[str, Any]:
        """Advance one in-game day and check for events"""
        day_events = self.event_timeline.advance_day()
        
        return {
            "day": day_events["day"],
            "phase": self.event_timeline.current_phase.value,
            "events": day_events["triggered_events"],
            "building_status": self.event_timeline.get_building_description(),
            "game_state": self.event_timeline.get_game_state()
        }
    
    def set_marketplace_conclusion(self, coherence: float, primary_trait: str) -> None:
        """
        Store player's state from marketplace scene and sync to timeline.
        Called after marketplace scene completion.
        """
        malrik_elenya_cooperation = 100 - int((100 - coherence) * 0.3)
        
        self.event_timeline.set_marketplace_state(
            coherence=coherence,
            primary_trait=primary_trait,
            malrik_elenya_cooperation=malrik_elenya_cooperation
        )
    
    def trigger_collapse_event(self) -> Dict[str, Any]:
        """Trigger the building collapse event"""
        collapse_result = self.event_timeline.trigger_collapse()
        
        return {
            "status": "collapse_triggered",
            "scene": self.collapse_trigger_scene.get_post_collapse_dialogue(),
            "collapse_data": collapse_result,
            "game_state": self.event_timeline.get_game_state()
        }
    
    def record_post_collapse_intervention(
        self,
        npc_name: str,
        choice: str
    ) -> Dict[str, Any]:
        """Record player intervention during immediate aftermath"""
        intervention_result = self.event_timeline.record_player_intervention(
            npc_name=npc_name,
            choice=choice,
            effectiveness=1
        )
        
        # Update aftermath scene based on intervention
        self.aftermath_scene.player_interventions.append(choice)
        
        # Update position if choosing a side
        if choice in ["pro_malrik", "support_malrik"]:
            self.aftermath_scene.player_position = "pro_malrik"
        elif choice in ["pro_elenya", "support_elenya"]:
            self.aftermath_scene.player_position = "pro_elenya"
        
        return {
            "intervention_recorded": True,
            "rebuild_potential": intervention_result["rebuild_potential"],
            "aftermath_path_probabilities": intervention_result["aftermath_path_probability"]
        }
    
    def get_aftermath_narration(self, phase: str) -> str:
        """Get narration for aftermath phase"""
        if phase == "separation":
            return self.aftermath_scene.get_separation_narration()
        elif phase == "malrik_isolation":
            return self.aftermath_scene.get_malrik_isolation_dialogue()
        elif phase == "elenya_isolation":
            return self.aftermath_scene.get_elenya_isolation_dialogue()
        elif phase == "coren_exhaustion":
            return self.aftermath_scene.get_coren_exhaustion_dialogue()
        return ""
    
    def get_npc_response_to_intervention(
        self,
        npc_name: str,
        intervention_type: str
    ) -> str:
        """Get NPC response to player intervention"""
        if npc_name == "malrik":
            return self.aftermath_scene.get_malrik_response_to_intervention(intervention_type)
        elif npc_name == "elenya":
            return self.aftermath_scene.get_elenya_response_to_intervention(intervention_type)
        return ""
    
    def get_aftermath_path_narration(self, path: AftermathPath) -> str:
        """Get narration for the aftermath path resolution"""
        if path == AftermathPath.REBUILD_TOGETHER:
            return self.aftermath_scene.get_rebuild_together_setup() + "\n\n" + \
                   self.aftermath_scene.get_rebuild_together_progression()
        elif path == AftermathPath.STALEMATE:
            return self.aftermath_scene.get_stalemate_setup() + "\n\n" + \
                   self.aftermath_scene.get_stalemate_resolution()
        elif path == AftermathPath.COMPLETE_SEPARATION:
            return self.aftermath_scene.get_complete_separation_setup() + "\n\n" + \
                   self.aftermath_scene.get_complete_separation_aftermath()
        return ""
    
    def resolve_aftermath_path(self) -> Dict[str, Any]:
        """Determine and resolve which aftermath path the player is on"""
        path = self.event_timeline.aftermath_path
        path_connection = AftermathPathDivergence.get_aftermath_ending_connection(path)
        
        return {
            "aftermath_path": path.value,
            "description": path_connection.get("description", ""),
            "narration": self.get_aftermath_path_narration(path),
            "ending_paths_unlocked": path_connection.get("ending_paths_unlocked", []),
            "npc_state": path_connection.get("npc_state", ""),
            "world_state": path_connection.get("world_state", ""),
            "game_state": self.event_timeline.get_game_state()
        }
    
    def get_phase3_status(self) -> Dict[str, Any]:
        """Get complete Phase 3 game status for UI"""
        coherence_report = self.coherence_calculator.get_coherence_report()
        
        return {
            "current_day": self.event_timeline.current_day,
            "current_phase": self.event_timeline.current_phase.value,
            "aftermath_path": self.event_timeline.aftermath_path.value,
            "building_status": self.event_timeline.get_building_description(),
            "building_stability": self.event_timeline.building_status.stability_percent,
            "malrik_stress": self.event_timeline.malrik_state.stress_level,
            "elenya_stress": self.event_timeline.elenya_state.stress_level,
            "malrik_elenya_cooperation": self.event_timeline.malrik_state.cooperation_level,
            "collapse_triggered": self.event_timeline.collapse_triggered,
            "rebuild_potential": self.event_timeline.player_interventions.get_rebuild_potential(),
            "player_interventions_count": self.event_timeline.player_interventions.total_intervention_count,
            "coherence": coherence_report.overall_coherence,
            "primary_trait": self.trait_profiler.get_primary_trait().value if self.trait_profiler.get_primary_trait() else "none"
        }

    # ============================================================================
    # PHASE 4: ENDING SYSTEM
    # ============================================================================
    
    def initiate_ending_sequence(self) -> Dict[str, Any]:
        """Start the ending sequence after Phase 3 completes"""
        # Set up ending manager with Phase 3 state
        coherence_report = self.coherence_calculator.get_coherence_report()
        primary_trait = self.trait_profiler.get_primary_trait()
        rebuild_advocacy = self.event_timeline.player_interventions.get_rebuild_potential()
        
        self.ending_manager.setup_from_phase3(
            aftermath_path=self.event_timeline.aftermath_path,
            coherence=coherence_report.overall_coherence,
            primary_trait=primary_trait.value if primary_trait else "unknown",
            rebuild_advocacy=rebuild_advocacy
        )
        
        return {
            "phase": "ending_sequence_started",
            "corelink_chamber_narration": self.corelink_scene.get_chamber_entrance_narration(),
            "setup_monologue": self.corelink_scene.get_setup_monologue(),
            "aftermath_path": self.event_timeline.aftermath_path.value,
            "player_coherence": coherence_report.overall_coherence,
            "primary_trait": primary_trait.value if primary_trait else "unknown"
        }
    
    def get_corelink_choice_prompt(self) -> Dict[str, Any]:
        """Get the player choice prompt for Corelink decision"""
        return {
            "phase": "corelink_choice",
            "choices": self.corelink_scene.get_choice_prompt(),
            "reflection_prompt": self.corelink_scene.get_setup_monologue()
        }
    
    def make_corelink_choice(self, choice: str) -> Dict[str, Any]:
        """Player makes their Corelink decision"""
        if choice not in ["restart", "abandon"]:
            return {"error": f"Invalid choice: {choice}"}
        
        # Convert to CoreLinkChoice enum
        core_choice = CoreLinkChoice.RESTART_SYSTEM if choice == "restart" else CoreLinkChoice.ABANDON_SYSTEM
        
        # Record choice and determine ending
        ending_result = self.ending_manager.player_chooses_corelink(core_choice)
        
        # Get choice confirmation
        confirmation = self.corelink_scene.get_choice_confirmation(choice)
        
        return {
            "choice_made": True,
            "choice": choice,
            "confirmation_narration": confirmation["confirmation_narration"],
            "ending_determined": ending_result["ending_determined"],
            "ending_type": ending_result["ending_type"],
            "ending_title": ending_result["ending_title"],
            "aftermath_reflection": self.corelink_scene.get_after_choice_reflection(choice)
        }
    
    def trigger_ending(self) -> Dict[str, Any]:
        """Trigger the determined ending"""
        ending_content = self.ending_manager.get_ending_content()
        
        if "error" in ending_content:
            return ending_content
        
        return {
            "phase": "ending",
            "ending_type": ending_content["ending_type"],
            "ending_title": ending_content["ending_title"],
            "ending_description": ending_content["ending_description"],
            "narration": ending_content["narration"],
            "npc_final_states": ending_content["npc_final_states"],
            "game_complete": True
        }
    
    def get_ending_status(self) -> Dict[str, Any]:
        """Get current ending status"""
        return self.ending_manager.get_ending_status()
    
    def get_phase4_status(self) -> Dict[str, Any]:
        """Get complete Phase 4 game status for UI"""
        return {
            "phase": 4,
            "ending_status": self.get_ending_status(),
            "game_complete": self.ending_manager.current_ending is not None
        }

    # ============================================================================
    # PHASE 5: SAVE/LOAD PERSISTENCE
    # ============================================================================
    
    def save_game(self, save_name: str = None, auto_save: bool = False) -> Dict[str, Any]:
        """
        Save current game progress
        
        Args:
            save_name: Name for the save slot (optional)
            auto_save: Whether this is an auto-save
            
        Returns:
            Dictionary with save result
        """
        # Build current game state
        state_snapshot = GameStateBuilder.build_from_orchestrator(self)
        
        # Save to file
        success, message, slot_id = self.save_manager.save_game(
            state_snapshot,
            save_name=save_name,
            auto_save=auto_save
        )
        
        used, max_slots = self.save_manager.get_save_slot_count()
        
        return {
            "save_success": success,
            "save_message": message,
            "slot_id": slot_id,
            "save_name": save_name or "Auto-Save",
            "player_name": state_snapshot.player_name,
            "current_day": state_snapshot.current_day,
            "current_phase": state_snapshot.current_phase,
            "game_completed": state_snapshot.game_completed,
            "save_slots_used": used,
            "save_slots_total": max_slots,
        }
    
    def load_game(self, slot_id: str) -> Dict[str, Any]:
        """
        Load a saved game
        
        Args:
            slot_id: ID of save slot to load
            
        Returns:
            Dictionary with load result and game state
        """
        success, message, state = self.load_manager.load_game(slot_id)
        
        if not success:
            return {
                "load_success": False,
                "load_message": message,
            }
        
        # Restore state to orchestrator
        restore_success, restore_message = self.load_manager.restore_to_orchestrator(
            state, self
        )
        
        if not restore_success:
            return {
                "load_success": False,
                "load_message": restore_message,
            }
        
        return {
            "load_success": True,
            "load_message": message,
            "player_name": state.player_name,
            "current_day": state.current_day,
            "current_phase": state.current_phase,
            "coherence_score": state.coherence_score,
            "game_completed": state.game_completed,
            "ending_type": state.ending_type,
        }
    
    def get_save_slots(self) -> Dict[str, Any]:
        """
        Get all available save slots
        
        Returns:
            Dictionary with list of save slots
        """
        slots = self.save_manager.get_save_slots()
        
        return {
            "save_slots": [
                {
                    "slot_id": slot.slot_id,
                    "save_name": slot.save_name,
                    "player_name": slot.player_name,
                    "save_timestamp": slot.save_timestamp,
                    "current_day": slot.current_day,
                    "current_phase": slot.current_phase,
                    "game_completed": slot.game_completed,
                    "ending_type": slot.ending_type,
                    "description": self.save_manager.get_save_description(slot),
                }
                for slot in slots
            ],
            "total_slots": len(slots),
        }
    
    def delete_save(self, slot_id: str) -> Dict[str, Any]:
        """
        Delete a save slot
        
        Args:
            slot_id: ID of slot to delete
            
        Returns:
            Dictionary with delete result
        """
        success, message = self.save_manager.delete_save(slot_id)
        
        return {
            "delete_success": success,
            "delete_message": message,
        }
    
    def quick_save(self) -> Dict[str, Any]:
        """
        Perform a quick save
        
        Returns:
            Dictionary with quick-save result
        """
        state_snapshot = GameStateBuilder.build_from_orchestrator(self)
        success, message = self.quick_save_manager.quick_save(state_snapshot)
        
        return {
            "quick_save_success": success,
            "quick_save_message": message,
        }
    
    def quick_load(self) -> Dict[str, Any]:
        """
        Load the quick-save
        
        Returns:
            Dictionary with quick-load result
        """
        state = self.quick_save_manager.quick_load()
        
        if state is None:
            return {
                "quick_load_success": False,
                "quick_load_message": "No quick-save available",
            }
        
        restore_success, restore_message = self.load_manager.restore_to_orchestrator(state, self)
        
        return {
            "quick_load_success": restore_success,
            "quick_load_message": restore_message or "Quick-saved game loaded",
            "player_name": state.player_name,
            "current_day": state.current_day,
        }
    
    def has_quick_save(self) -> Dict[str, Any]:
        """Check if quick-save exists"""
        return {
            "has_quick_save": self.quick_save_manager.has_quick_save(),
        }
    
    def get_phase5_status(self) -> Dict[str, Any]:
        """Get complete Phase 5 game status for UI"""
        used, max_slots = self.save_manager.get_save_slot_count()
        
        return {
            "phase": 5,
            "save_slots_used": used,
            "save_slots_total": max_slots,
            "save_slots_full": self.save_manager.is_save_slots_full(),
            "has_quick_save": self.quick_save_manager.has_quick_save(),
            "save_directory": str(self.save_manager.save_directory),
        }
    
    # ======================== Phase 6: API Serialization ========================
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete game status for API serialization"""
        try:
            # Basic game progress
            status = {
                "player_name": self.trait_profiler.player_name,
                "phase": self.event_timeline.current_phase.value if self.event_timeline.current_phase else "unknown",
                "day": self.event_timeline.current_day,
                "completed": self.ending_manager.game_completed if self.ending_manager else False,
            }
            
            # Coherence info
            coherence = self.coherence_calculator.get_coherence_report()
            status["coherence_score"] = coherence.overall_coherence
            status["coherence_level"] = coherence.level.value if hasattr(coherence, 'level') else 'UNKNOWN'
            status["primary_trait"] = self.trait_profiler.get_primary_trait().value
            
            # Building status
            status["building_stability"] = self.event_timeline.building_status.stability_percent
            status["malrik_stress"] = self.event_timeline.malrik_state.stress_level
            status["elenya_stress"] = self.event_timeline.elenya_state.stress_level
            
            # Ending info
            if self.ending_manager.game_completed:
                status["ending_type"] = self.ending_manager.current_ending.value if self.ending_manager.current_ending else None
            
            return status
        except Exception as e:
            return {
                "error": str(e),
                "player_name": self.trait_profiler.player_name if self.trait_profiler else "Unknown",
            }
    
    def process_player_choice(self, choice_index: int) -> Dict[str, Any]:
        """Process a player choice (API wrapper)"""
        try:
            # Process the choice through the game engine
            result = self.process_player_action(choice_index=choice_index)
            
            # Return structured result
            return {
                "success": True,
                "choice_processed": True,
                "result": result,
                "new_status": self.get_status(),
            }
        except Exception as e:
            return {
                "success": False,
                "choice_processed": False,
                "error": str(e),
            }
    
    def process_player_input(self, player_input: str) -> Dict[str, Any]:
        """Process free-form player input (API wrapper)"""
        try:
            # Try to process as action
            result = self.process_player_action(player_input=player_input)
            
            return {
                "success": True,
                "input_processed": True,
                "result": result,
                "new_status": self.get_status(),
            }
        except Exception as e:
            return {
                "success": False,
                "input_processed": False,
                "error": str(e),
            }
