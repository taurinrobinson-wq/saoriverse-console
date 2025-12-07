"""Velinor NPC System

NPCs act as mini-DMs, using FirstPerson orchestration to:
- Summarize player intent
- Ask clarifying questions  
- Adapt tone based on player choices and emotional state
- Maintain dialogue history
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sys
from pathlib import Path

# Add src to path for FirstPerson imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from emotional_os.deploy.core.firstperson import (
        FirstPersonOrchestrator,
        AffectParser,
        ConversationMemory
    )
    HAS_FIRSTPERSON = True
except ImportError:
    HAS_FIRSTPERSON = False


@dataclass
class NPCPersonality:
    """NPC personality profile."""
    name: str
    role: str  # "Archivist", "Guard", "Healer", "Merchant"
    base_tone: str  # "riddle", "skeptical", "gentle", "pragmatic"
    
    # Dialogue templates
    summary_template: str
    clarification_template: str
    affirmation_template: str
    challenge_template: str


class NPCDialogueSystem:
    """Manages NPC dialogue generation and adaptation."""
    
    def __init__(self, use_firstperson: bool = True):
        """Initialize NPC dialogue system.
        
        Args:
            use_firstperson: Whether to use FirstPerson orchestrator for dialogue
        """
        self.use_firstperson = use_firstperson and HAS_FIRSTPERSON
        
        if self.use_firstperson:
            self.orchestrator = FirstPersonOrchestrator("game_npc", "velinor_session")
            self.affect_parser = AffectParser()
        
        self.npc_personalities: Dict[str, NPCPersonality] = self._load_personalities()
    
    def _load_personalities(self) -> Dict[str, NPCPersonality]:
        """Load NPC personality profiles."""
        return {
            "archivist": NPCPersonality(
                name="The Archivist",
                role="Archivist",
                base_tone="riddle",
                summary_template="So you say: {input}. Let me understand—{question}",
                clarification_template="Are you certain of this path? {reflection}",
                affirmation_template="Wisdom flows through your choice. {encouragement}",
                challenge_template="That path is treacherous, yet you seem resolute. {warning}"
            ),
            "guard": NPCPersonality(
                name="The Guard",
                role="Guard",
                base_tone="skeptical",
                summary_template="You propose: {input}. Interesting. {question}",
                clarification_template="I've seen many try this. Are you prepared? {assessment}",
                affirmation_template="Your resolve is noted. Proceed. {instruction}",
                challenge_template="That's bold. Perhaps foolish. {caution}"
            ),
            "healer": NPCPersonality(
                name="The Healer",
                role="Healer",
                base_tone="gentle",
                summary_template="I hear you: {input}. Tell me, {question}",
                clarification_template="Your heart guides you. But are you ready? {reassurance}",
                affirmation_template="Your courage steadies you. {blessing}",
                challenge_template="This path demands much. Do you have strength? {gentle_warning}"
            ),
            "merchant": NPCPersonality(
                name="The Merchant",
                role="Merchant",
                base_tone="pragmatic",
                summary_template="So you need: {input}. Fair enough. {question}",
                clarification_template="What's in it for you? Be honest. {probe}",
                affirmation_template="Smart choice. You'll go far. {incentive}",
                challenge_template="That route has complications. {risk_assessment}"
            ),
        }
    
    def generate_summary(self, npc_name: str, player_input: str) -> str:
        """Generate NPC summary of player intent."""
        npc = self.npc_personalities.get(npc_name.lower())
        if not npc:
            return f"I understand: {player_input}"
        
        if self.use_firstperson:
            # Use FirstPerson to analyze intent
            affect = self.affect_parser.analyze_affect(player_input)
            tone = affect.get("tone", "neutral")
            
            # Map tone to question
            question_map = {
                "uplifting": "what brings you such hope?",
                "heavy": "why does this weigh so heavily?",
                "curious": "what draws you to this?",
                "reflective": "have you considered the costs?",
            }
            question = question_map.get(tone, "what moves you?")
            
            return npc.summary_template.format(
                input=player_input[:50],
                question=question
            )
        else:
            return npc.summary_template.format(
                input=player_input[:50],
                question="tell me more"
            )
    
    def generate_clarification(self, npc_name: str, player_input: str, is_risky: bool = False) -> str:
        """Generate clarifying question from NPC."""
        npc = self.npc_personalities.get(npc_name.lower())
        if not npc:
            return "Are you certain of this choice?"
        
        if is_risky:
            return npc.challenge_template.format(
                caution="Tread carefully.",
                warning="The path ahead is uncertain.",
                risk_assessment="There are risks here.",
                assessment="Think twice.",
                assessment="Few return.",
                probe="What's driving this?"
            )
        else:
            return npc.clarification_template.format(
                reflection="What do you seek?",
                assessment="You seem prepared.",
                reassurance="Trust your instincts.",
                gentle_warning="Be mindful.",
            )
    
    def generate_affirmation(self, npc_name: str, player_input: str) -> str:
        """Generate affirmation from NPC when player makes positive choice."""
        npc = self.npc_personalities.get(npc_name.lower())
        if not npc:
            return "Your choice stands."
        
        return npc.affirmation_template.format(
            encouragement="You will prevail.",
            instruction="Move forward with confidence.",
            blessing="May your path be clear.",
            incentive="This will serve you well."
        )
    
    def adapt_for_multiplayer(self, dialogue: str, group_size: int) -> str:
        """Adapt dialogue for group play."""
        if group_size == 1:
            return dialogue
        
        # Shift pronouns and emphasis for group
        multiplayer_adapts = {
            "You steady": "Together, you steady",
            "Your resolve": "Your collective resolve",
            "You feel": "You all feel",
            "Your courage": "Your shared courage",
        }
        
        adapted = dialogue
        for solo, group in multiplayer_adapts.items():
            adapted = adapted.replace(solo, group)
        
        return adapted
    
    def get_contextual_dialogue(
        self,
        npc_name: str,
        dialogue_type: str,  # "greeting", "summary", "clarification", "affirmation"
        player_input: str,
        group_size: int = 1,
        is_risky: bool = False
    ) -> str:
        """Generate contextual NPC dialogue."""
        if dialogue_type == "summary":
            dialogue = self.generate_summary(npc_name, player_input)
        elif dialogue_type == "clarification":
            dialogue = self.generate_clarification(npc_name, player_input, is_risky)
        elif dialogue_type == "affirmation":
            dialogue = self.generate_affirmation(npc_name, player_input)
        else:
            dialogue = f"{self.npc_personalities.get(npc_name.lower(), 'NPC').name} awaits your next word."
        
        # Adapt for multiplayer if needed
        if group_size > 1:
            dialogue = self.adapt_for_multiplayer(dialogue, group_size)
        
        return dialogue


class NPCRegistry:
    """Manages all active NPCs in the game."""
    
    def __init__(self):
        """Initialize NPC registry."""
        self.npcs: Dict[str, 'NPC'] = {}
        self.dialogue_system = NPCDialogueSystem()
    
    def add_npc(self, npc_name: str, personality_type: str, location: str) -> 'NPC':
        """Add an NPC to the game."""
        npc = NPC(
            name=npc_name,
            personality_type=personality_type,
            location=location,
            dialogue_system=self.dialogue_system
        )
        self.npcs[npc_name] = npc
        return npc
    
    def get_npc(self, npc_name: str) -> Optional['NPC']:
        """Get NPC by name."""
        return self.npcs.get(npc_name)
    
    def get_npcs_at_location(self, location: str) -> List['NPC']:
        """Get all NPCs at a specific location."""
        return [npc for npc in self.npcs.values() if npc.location == location]


class NPC:
    """Individual NPC instance."""
    
    def __init__(self, name: str, personality_type: str, location: str, dialogue_system: NPCDialogueSystem):
        """Initialize NPC."""
        self.name = name
        self.personality_type = personality_type
        self.location = location
        self.dialogue_system = dialogue_system
        
        self.dialogue_history: List[Tuple[str, str]] = []  # (speaker, text)
        self.player_relationship: float = 0.5  # -1 to 1
        self.group_size: int = 1
    
    def get_greeting(self) -> str:
        """Get NPC greeting."""
        greetings = {
            "archivist": "The Archivist studies you carefully, quill poised.",
            "guard": "The Guard shifts, hand on sword hilt.",
            "healer": "The Healer's eyes soften with recognition.",
            "merchant": "The Merchant eyes you with mercantile interest.",
        }
        return greetings.get(self.personality_type.lower(), f"{self.name} notices you.")
    
    def respond_to_player(
        self,
        player_input: str,
        dialogue_type: str = "summary",
        is_risky: bool = False
    ) -> str:
        """Generate NPC response to player input."""
        dialogue = self.dialogue_system.get_contextual_dialogue(
            npc_name=self.personality_type,
            dialogue_type=dialogue_type,
            player_input=player_input,
            group_size=self.group_size,
            is_risky=is_risky
        )
        
        self.dialogue_history.append(("npc", dialogue))
        return dialogue
    
    def record_player_input(self, player_input: str) -> None:
        """Record player input in dialogue history."""
        self.dialogue_history.append(("player", player_input))
    
    def adjust_relationship(self, delta: float) -> None:
        """Adjust player-NPC relationship."""
        self.player_relationship = max(-1, min(1, self.player_relationship + delta))
    
    def get_dialogue_history(self, limit: int = 5) -> List[Tuple[str, str]]:
        """Get recent dialogue history."""
        return self.dialogue_history[-limit:]
