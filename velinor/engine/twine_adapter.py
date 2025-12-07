"""
Twine/Ink Narrative Adapter for Velinor
=====================================

This module bridges the Velinor game engine with Twine/Ink narrative files,
enabling dynamic dialogue generation and story progression.
"""

import json
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import random


class StoryNodeType(Enum):
    """Types of narrative nodes in Twine story."""
    DIALOGUE = "dialogue"
    CHOICE = "choice"
    ACTION = "action"
    DICE_ROLL = "dice_roll"
    BACKGROUND_CHANGE = "background_change"
    END = "end"


@dataclass
class StoryPassage:
    """Represents a passage in Twine story."""
    pid: str
    name: str
    text: str
    tags: List[str] = field(default_factory=list)
    position: tuple = (0, 0)
    size: tuple = (100, 100)


@dataclass
class DialogueChoice:
    """A player choice that leads to next story node."""
    text: str
    target_passage: str
    requires_skill_check: bool = False
    skill_type: Optional[str] = None
    difficulty: int = 10


@dataclass
class StoryContext:
    """Context for current story state."""
    current_passage_id: str
    passage_history: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    visited_passages: set = field(default_factory=set)
    dialogue_log: List[Dict[str, str]] = field(default_factory=list)
    
    def mark_visited(self, passage_id: str) -> None:
        """Mark a passage as visited."""
        self.visited_passages.add(passage_id)
        self.passage_history.append(passage_id)
    
    def has_visited(self, passage_id: str) -> bool:
        """Check if passage has been visited."""
        return passage_id in self.visited_passages


class TwineStoryLoader:
    """Loads and parses Twine story JSON format."""
    
    def __init__(self):
        self.passages: Dict[str, StoryPassage] = {}
        self.story_data: Optional[Dict[str, Any]] = None
    
    def load_from_json(self, json_path: str) -> Dict[str, StoryPassage]:
        """Load Twine story exported as JSON."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.story_data = json.load(f)
            
            # Extract passages from Twine JSON format
            if 'passages' in self.story_data:
                for passage_data in self.story_data['passages']:
                    pid = str(passage_data.get('pid', ''))
                    passage = StoryPassage(
                        pid=pid,
                        name=passage_data.get('name', 'Unnamed'),
                        text=passage_data.get('text', ''),
                        tags=passage_data.get('tags', []).split() if isinstance(
                            passage_data.get('tags', ''), str) else passage_data.get('tags', []),
                        position=tuple(passage_data.get('position', (0, 0))),
                        size=tuple(passage_data.get('size', (100, 100)))
                    )
                    self.passages[pid] = passage
            
            return self.passages
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Story file not found: {json_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in story file: {json_path}")
    
    def get_passage(self, pid: str) -> Optional[StoryPassage]:
        """Retrieve a passage by ID."""
        return self.passages.get(pid)
    
    def get_start_passage(self) -> Optional[StoryPassage]:
        """Get the story's starting passage."""
        if not self.story_data:
            return None
        
        # Twine typically marks start passage in metadata
        start_pid = self.story_data.get('startnode')
        if start_pid:
            return self.passages.get(str(start_pid))
        
        # Fallback: return first passage
        if self.passages:
            return next(iter(self.passages.values()))
        
        return None


class DialogueParser:
    """Parses Twine dialogue markup and extracts choices/commands."""
    
    @staticmethod
    def parse_choices(passage_text: str) -> List[DialogueChoice]:
        """
        Parse choice syntax from passage text.
        Supports Twine SugarCube format: [[Choice Text->Target Passage]]
        """
        choices = []
        import re
        
        # Match [[text->target]] or [[text|target]] patterns
        pattern = r'\[\[([^\]]+?)(->|=)([^\]]+?)\]\]'
        matches = re.findall(pattern, passage_text)
        
        for match in matches:
            choice_text = match[0].strip()
            target = match[2].strip()
            
            # Check for skill check notation (e.g., "Persuade (Charisma, DC 12)")
            skill_match = re.search(r'\((\w+),\s*DC\s*(\d+)\)', choice_text)
            requires_check = skill_match is not None
            skill_type = skill_match.group(1) if skill_match else None
            difficulty = int(skill_match.group(2)) if skill_match else 10
            
            choices.append(DialogueChoice(
                text=choice_text,
                target_passage=target,
                requires_skill_check=requires_check,
                skill_type=skill_type,
                difficulty=difficulty
            ))
        
        return choices
    
    @staticmethod
    def extract_dialogue(passage_text: str) -> str:
        """
        Extract dialogue content, removing choice markup.
        """
        import re
        # Remove choice brackets
        cleaned = re.sub(r'\[\[.*?\]\]', '', passage_text)
        # Remove command markers (e.g., {background: market})
        cleaned = re.sub(r'\{.*?\}', '', cleaned)
        return cleaned.strip()
    
    @staticmethod
    def extract_commands(passage_text: str) -> Dict[str, Any]:
        """Extract special commands from passage (backgrounds, dice rolls, etc.)."""
        import re
        commands = {}
        
        # Match {command: value} patterns
        pattern = r'\{(\w+):\s*([^}]+)\}'
        matches = re.findall(pattern, passage_text)
        
        for cmd, value in matches:
            if cmd == 'background':
                commands['background'] = value.strip()
            elif cmd == 'dice':
                commands['dice_roll'] = value.strip()  # e.g., "d20+2"
            elif cmd == 'npc':
                commands['npc_name'] = value.strip()
            elif cmd == 'multiplayer':
                commands['multiplayer_mode'] = value.strip() == 'true'
        
        return commands


class TwineGameSession:
    """Manages a game session using Twine story and game engine."""
    
    def __init__(
        self,
        story_loader: TwineStoryLoader,
        game_engine: 'VelinorEngine',  # type hint from core.py
        first_person_orchestrator: Optional[Any] = None
    ):
        self.story_loader = story_loader
        self.game_engine = game_engine
        self.first_person = first_person_orchestrator
        self.context = None
        self.parser = DialogueParser()
        self.clarifying_questions = self._default_clarifying_questions()
        self.callbacks: Dict[str, Callable] = {}
    
    def _default_clarifying_questions(self) -> List[str]:
        """Default set of clarifying questions from FirstPerson."""
        return [
            "Are you sure this is the path you want?",
            "That path is risky, but you sound resolved.",
            "Do you feel prepared for the next leg of this journey?",
            "I'm sensing hesitation—want to reconsider?",
            "Your choice carries weight. Ready to commit?",
            "This feels like a turning point. How are you feeling about it?"
        ]
    
    def start_story(self, start_passage_id: Optional[str] = None) -> Dict[str, Any]:
        """Initialize story session."""
        start = start_passage_id or self.story_loader.get_start_passage()
        if not start:
            raise ValueError("No starting passage found")
        
        self.context = StoryContext(
            current_passage_id=start.pid,
            variables={'player_name': self.game_engine.current_session.player.name}
        )
        self.context.mark_visited(start.pid)
        
        return self._render_passage(start.pid)
    
    def _render_passage(self, passage_id: str) -> Dict[str, Any]:
        """Render a passage with all necessary data for UI display."""
        passage = self.story_loader.get_passage(passage_id)
        if not passage:
            raise ValueError(f"Passage not found: {passage_id}")
        
        # Parse content
        dialogue = self.parser.extract_dialogue(passage.text)
        choices = self.parser.parse_choices(passage.text)
        commands = self.parser.extract_commands(passage.text)
        
        # Generate dynamic dialogue if FirstPerson available
        if self.first_person and 'npc_name' in commands:
            dialogue = self._generate_dynamic_dialogue(
                base_dialogue=dialogue,
                npc_name=commands['npc_name'],
                is_multiplayer=commands.get('multiplayer_mode', False)
            )
        
        result = {
            'passage_id': passage_id,
            'passage_name': passage.name,
            'dialogue': dialogue,
            'choices': [
                {'text': c.text, 'target': c.target_passage, 'requires_check': c.requires_skill_check}
                for c in choices
            ],
            'background': commands.get('background'),
            'npc_name': commands.get('npc_name'),
            'is_multiplayer': commands.get('multiplayer_mode', False),
            'has_clarifying_question': random.random() < 0.4  # 40% of turns
        }
        
        if result['has_clarifying_question']:
            result['clarifying_question'] = random.choice(self.clarifying_questions)
        
        return result
    
    def _generate_dynamic_dialogue(
        self,
        base_dialogue: str,
        npc_name: str,
        is_multiplayer: bool
    ) -> str:
        """
        Use FirstPerson orchestrator to generate dynamic dialogue variant.
        Adapts tone based on player choices and group composition.
        """
        if not self.first_person:
            return base_dialogue
        
        try:
            # Get player personality traits from game engine
            player_session = self.game_engine.current_session
            tone_modifiers = {
                'player_count': len(player_session.players) if is_multiplayer else 1,
                'player_courage': player_session.players[0].stats.courage if player_session.players else 50,
                'player_empathy': player_session.players[0].stats.empathy if player_session.players else 50,
            }
            
            # Request dialogue variation from FirstPerson
            # This would call into your FirstPerson orchestrator
            # For now, return base with adaptation hint
            adaptation = " [NPC adapts tone based on group dynamics]" if is_multiplayer else ""
            return base_dialogue + adaptation
        
        except Exception:
            return base_dialogue
    
    def process_player_input(
        self,
        player_response: str,
        choice_index: Optional[int] = None,
        player_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process player input (typed response or choice selection).
        Returns next passage state and any dice roll results.
        """
        passage = self.story_loader.get_passage(self.context.current_passage_id)
        choices = self.parser.parse_choices(passage.text)
        
        # Use choice or interpret typed response
        if choice_index is not None and choice_index < len(choices):
            chosen = choices[choice_index]
            next_passage_id = chosen.target_passage
            
            # Handle skill check if needed
            if chosen.requires_skill_check:
                result = self._roll_skill_check(chosen, player_id)
                if not result['success']:
                    # Failure branch - might exist in story
                    next_passage_id = self._find_failure_passage(next_passage_id)
        else:
            # Free-text response - use FirstPerson to classify and route
            next_passage_id = self._classify_and_route_response(player_response, choices)
        
        # Update story context
        self.context.current_passage_id = next_passage_id
        self.context.mark_visited(next_passage_id)
        
        # Log dialogue exchange
        self.context.dialogue_log.append({
            'player_id': player_id or 'solo',
            'input': player_response or f"Choice {choice_index}",
            'passage_id': next_passage_id
        })
        
        # Render and return next passage
        return self._render_passage(next_passage_id)
    
    def _roll_skill_check(self, choice: DialogueChoice, player_id: Optional[str]) -> Dict[str, Any]:
        """Roll d20 + modifiers for skill check."""
        player = self.game_engine.current_session.players[0] if self.game_engine.current_session.players else None
        
        # Map skill names to player stats
        skill_map = {
            'courage': player.stats.courage if player else 0,
            'wisdom': player.stats.wisdom if player else 0,
            'empathy': player.stats.empathy if player else 0,
            'resolve': player.stats.resolve if player else 0,
        }
        
        modifier = skill_map.get(choice.skill_type, 0)
        d20_roll = random.randint(1, 20)
        total = d20_roll + modifier
        success = total >= choice.difficulty
        
        return {
            'd20': d20_roll,
            'modifier': modifier,
            'total': total,
            'difficulty': choice.difficulty,
            'success': success
        }
    
    def _find_failure_passage(self, success_passage_id: str) -> str:
        """Look for failure passage variant (e.g., 'passage_fail')."""
        failure_id = f"{success_passage_id}_fail"
        if self.story_loader.get_passage(failure_id):
            return failure_id
        return success_passage_id  # Fallback to success
    
    def _classify_and_route_response(self, response: str, choices: List[DialogueChoice]) -> str:
        """
        Classify free-text response and route to appropriate passage.
        If FirstPerson available, use its affect parsing.
        """
        if not choices:
            return self.context.current_passage_id
        
        # Simple keyword matching as fallback
        response_lower = response.lower()
        for choice in choices:
            # Very basic routing - could be enhanced with NLP
            if choice.text.lower() in response_lower or response_lower in choice.text.lower():
                return choice.target_passage
        
        # Default to first choice if no match
        return choices[0].target_passage
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Register callback for story events (e.g., 'on_background_change')."""
        self.callbacks[event] = callback
    
    def _trigger_callback(self, event: str, data: Any) -> None:
        """Trigger registered callback."""
        if event in self.callbacks:
            self.callbacks[event](data)


class StoryBuilder:
    """Helper to programmatically build Twine stories."""
    
    def __init__(self, story_title: str):
        self.story_data = {
            'name': story_title,
            'startnode': None,
            'passages': []
        }
        self.next_pid = 1
        self.passage_map = {}
    
    def add_passage(
        self,
        name: str,
        text: str,
        tags: Optional[List[str]] = None,
        is_start: bool = False
    ) -> str:
        """Add a passage to the story."""
        pid = str(self.next_pid)
        self.next_pid += 1
        
        passage = {
            'pid': pid,
            'name': name,
            'text': text,
            'tags': tags or [],
            'position': (0, 0),
            'size': (100, 100)
        }
        
        self.story_data['passages'].append(passage)
        self.passage_map[name] = pid
        
        if is_start:
            self.story_data['startnode'] = pid
        
        return pid
    
    def add_choice(self, from_passage_name: str, choice_text: str, to_passage_name: str) -> None:
        """Add a choice link between passages."""
        # Find the passage and append choice to its text
        for passage in self.story_data['passages']:
            if passage['name'] == from_passage_name:
                choice_markup = f"[[{choice_text}->{to_passage_name}]]"
                passage['text'] += f"\n\n{choice_markup}"
                break
    
    def export_json(self, output_path: str) -> None:
        """Export story as JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.story_data, f, indent=2)
