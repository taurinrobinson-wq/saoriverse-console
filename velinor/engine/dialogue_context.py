"""
Dialogue Context system for skill-based NPC encounters.

Generates dialogue options based on:
- NPC's current REMNANTS state
- Player's actual skills vs claimed skills
- History of deception (especially lies discovered)
- NPC personality (high authority vs high empathy yields different dialogue)

NO narrative forks. Same task always happens. Different dialogue texture reflects
NPC's skepticism/trust toward the player.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class DialogueStyle(Enum):
    """NPC dialogue patterns based on REMNANTS profile."""
    TRUSTING = "trusting"          # High trust, low skepticism
    CAUTIOUS = "cautious"           # Moderate skepticism
    SUSPICIOUS = "suspicious"       # High skepticism, may test you
    DISAPPOINTED = "disappointed"   # Was trusting, now feels betrayed
    DISMISSIVE = "dismissive"       # Low trust, guarded


class DialogueOption:
    """Single dialogue choice available to player in an encounter."""
    
    def __init__(
        self,
        text: str,
        skill_claim: Optional[str] = None,
        is_lie: bool = False,
        hidden_if_traits: Optional[Dict[str, float]] = None,
        requires_previous_lie_discovery: bool = False
    ):
        """
        Args:
            text: What player says aloud
            skill_claim: Skill being claimed (None if just asking to learn)
            is_lie: Whether this option claims a skill player doesn't have
            hidden_if_traits: Option only shows if NPC's traits DON'T match these values
                              e.g., {"skepticism": 0.8} = don't show if skepticism >= 0.8
            requires_previous_lie_discovery: Only show after a lie was discovered
        """
        self.text = text
        self.skill_claim = skill_claim
        self.is_lie = is_lie
        self.hidden_if_traits = hidden_if_traits or {}
        self.requires_previous_lie_discovery = requires_previous_lie_discovery
    
    def is_available(self, npc_traits: Dict[str, float], previous_lie_caught: bool) -> bool:
        """Check if this option should be shown to player."""
        if self.requires_previous_lie_discovery and not previous_lie_caught:
            return False
        
        for trait, max_value in self.hidden_if_traits.items():
            if trait in npc_traits and npc_traits[trait] >= max_value:
                return False
        
        return True


@dataclass
class NPCDialogueContext:
    """Dialogue state for a specific NPC encounter."""
    
    npc_name: str
    npc_traits: Dict[str, float]  # Current REMNANTS: trust, skepticism, memory, etc.
    player_actual_skills: Dict[str, float]  # Player's real skill levels
    player_previous_lies_caught: bool = False  # Has this NPC caught player in a lie?
    
    def get_dialogue_style(self) -> DialogueStyle:
        """Determine NPC's emotional stance toward player based on REMNANTS."""
        trust = self.npc_traits.get("trust", 0.5)
        skepticism = self.npc_traits.get("skepticism", 0.5)
        
        if self.player_previous_lies_caught:
            return DialogueStyle.DISAPPOINTED
        
        if skepticism >= 0.75:
            return DialogueStyle.SUSPICIOUS
        elif skepticism >= 0.5:
            return DialogueStyle.CAUTIOUS
        elif trust >= 0.7:
            return DialogueStyle.TRUSTING
        else:
            return DialogueStyle.DISMISSIVE
    
    def generate_opening_dialogue(self) -> str:
        """NPC's greeting reflects their current REMNANTS state."""
        style = self.get_dialogue_style()
        
        openings = {
            DialogueStyle.TRUSTING: [
                f"Ah, good to see you. I trust you're ready for this?",
                f"I've always found you reliable. Shall we begin?"
            ],
            DialogueStyle.CAUTIOUS: [
                f"I assume you know what you're doing. We'll see.",
                f"Let's proceed. Do be careful though."
            ],
            DialogueStyle.SUSPICIOUS: [
                f"You again. Somehow I doubt your competence here.",
                f"I'll believe it when I see it."
            ],
            DialogueStyle.DISAPPOINTED: [
                f"I thought better of you. Let's just get this done.",
                f"You know, it's hard to trust anyone these days."
            ],
            DialogueStyle.DISMISSIVE: [
                f"If you insist. Don't slow me down.",
                f"This is a waste of my time, but fine."
            ]
        }
        
        options = openings.get(style, openings[DialogueStyle.CAUTIOUS])
        return options[0]  # Return first for determinism; can randomize
    
    def generate_dialogue_options(self, task_skill: str) -> List[DialogueOption]:
        """
        Generate available dialogue options for player.
        
        Same task, different emotional texture based on NPC skepticism/trust.
        """
        player_actual_level = self.player_actual_skills.get(task_skill, 0.0)
        
        options = []
        
        # Option 1: Admit if lacking skill (always available, always truthful)
        if player_actual_level < 0.5:
            options.append(DialogueOption(
                text=f"Honestly, I don't know {task_skill} yet. Could you teach me?",
                skill_claim=None,
                is_lie=False
            ))
        
        # Option 2: Claim honestly if player has the skill
        if player_actual_level >= 0.3:
            options.append(DialogueOption(
                text=f"I have experience with {task_skill}. Let me try.",
                skill_claim=task_skill,
                is_lie=False
            ))
        
        # Option 3: Exaggerate competence (risky lie)
        # Hidden if NPC's skepticism is very high (they'd see through it)
        if player_actual_level > 0.0:
            options.append(DialogueOption(
                text=f"I'm quite skilled at {task_skill}. I can handle this.",
                skill_claim=task_skill,
                is_lie=True,
                hidden_if_traits={"skepticism": 0.8}  # Too suspicious to bluff
            ))
        else:
            # Outright lie (dangerous)
            options.append(DialogueOption(
                text=f"Of course I know {task_skill}. No problem.",
                skill_claim=task_skill,
                is_lie=True,
                hidden_if_traits={"skepticism": 0.6}  # Even moderate skepticism sees through this
            ))
        
        # Option 4: Deflect with humor (only if trust is decent)
        options.append(DialogueOption(
            text=f"How hard can {task_skill} be? Let's find out together.",
            skill_claim=None,
            is_lie=False,
            hidden_if_traits={"skepticism": 0.7}  # Only works if NPC trusts you enough to take jokes
        ))
        
        # Option 5: Appeal to teach you (always available)
        options.append(DialogueOption(
            text=f"I'd rather learn from you than fake it.",
            skill_claim=None,
            is_lie=False
        ))
        
        # Option 6: Callback to previous lie discovery
        # Only shows if NPC caught player lying before
        if self.player_previous_lies_caught:
            options.append(DialogueOption(
                text=f"Last time was an exception. I actually know {task_skill}.",
                skill_claim=task_skill,
                is_lie=False,  # Must be truthful after being caught
                requires_previous_lie_discovery=True,
                hidden_if_traits={"trust": 0.3}  # Need minimal trust to even attempt redemption
            ))
        
        # Filter to only available options
        available = [
            opt for opt in options
            if opt.is_available(self.npc_traits, self.player_previous_lies_caught)
        ]
        
        return available if available else options  # Fallback to all if none pass filters
    
    def generate_reaction_after_success(self) -> str:
        """NPC's reaction after player succeeds (truthfully or lie not caught)."""
        style = self.get_dialogue_style()
        
        reactions = {
            DialogueStyle.TRUSTING: [
                f"Excellent work. I knew I could count on you.",
                f"Just as I thought. You've got real skill here."
            ],
            DialogueStyle.CAUTIOUS: [
                f"Well, you managed that adequately.",
                f"I'm... pleasantly surprised."
            ],
            DialogueStyle.SUSPICIOUS: [
                f"Hmph. Luck, probably. Don't expect me to be impressed.",
                f"So you CAN do something right."
            ],
            DialogueStyle.DISAPPOINTED: [
                f"See? You're capable when you actually try.",
                f"Perhaps you're not as two-faced as I thought."
            ],
            DialogueStyle.DISMISSIVE: [
                f"Fine. You did the job. What now?",
                f"At least you weren't completely useless."
            ]
        }
        
        options = reactions.get(style, reactions[DialogueStyle.CAUTIOUS])
        return options[0]
    
    def generate_reaction_after_failure_truthful(self) -> str:
        """NPC's reaction after player fails (but was honest about limitations)."""
        style = self.get_dialogue_style()
        
        reactions = {
            DialogueStyle.TRUSTING: [
                f"That didn't work out, but I respect your honesty. We'll figure it out.",
                f"No shame in struggling. Let me help you."
            ],
            DialogueStyle.CAUTIOUS: [
                f"Well, that was a swing and a miss. We'll try again.",
                f"Doesn't matter. Failure is just practice."
            ],
            DialogueStyle.SUSPICIOUS: [
                f"Typical. At least you weren't pretending.",
                f"Not surprised. Better luck next time, maybe."
            ],
            DialogueStyle.DISAPPOINTED: [
                f"Everyone fails. What matters is how you respond.",
                f"Let's try a different approach."
            ],
            DialogueStyle.DISMISSIVE: [
                f"You weren't ready. Accept the defeat.",
                f"This is why I prefer working alone."
            ]
        }
        
        options = reactions.get(style, reactions[DialogueStyle.CAUTIOUS])
        return options[0]
    
    def generate_reaction_after_failure_lie_caught(self) -> str:
        """NPC's reaction when lie is discovered (player claimed skill they don't have, failed)."""
        # Special dialogue for Korrin
        if self.npc_name == "Korrin":
            return (
                "I thought I taught you better than this. Lie when it serves you — "
                "but don't get caught. You got caught. That's on you."
            )
        
        style = self.get_dialogue_style()
        
        reactions = {
            DialogueStyle.TRUSTING: [
                f"You lied to me. That... really hurts. I thought you were better than that.",
                f"I was willing to trust you. Why would you deceive me?"
            ],
            DialogueStyle.CAUTIOUS: [
                f"So you don't actually know what you're talking about. Why lie?",
                f"Next time, just tell me the truth from the start."
            ],
            DialogueStyle.SUSPICIOUS: [
                f"I knew it. You talked a big game but had nothing to back it up.",
                f"Don't waste my time with lies. I see through them every time."
            ],
            DialogueStyle.DISAPPOINTED: [
                f"And here I thought you'd learned. Apparently not.",
                f"This is exactly why I stopped trusting you in the first place."
            ],
            DialogueStyle.DISMISSIVE: [
                f"Pathetic. You couldn't even fake competence convincingly.",
                f"I have no use for liars. Get out of my sight."
            ]
        }
        
        options = reactions.get(style, reactions[DialogueStyle.DISMISSIVE])
        return options[0]
    
    def to_dict(self) -> Dict:
        """Export context state for story JSON."""
        return {
            "npc_name": self.npc_name,
            "npc_traits": self.npc_traits,
            "player_actual_skills": self.player_actual_skills,
            "player_previous_lies_caught": self.player_previous_lies_caught,
            "dialogue_style": self.get_dialogue_style().value
        }


def create_npc_dialogue_context(
    npc_name: str,
    npc_profile,  # NPCProfile from npc_manager
    player_actual_skills: Dict[str, float],
    player_lie_history: Optional[Dict[str, bool]] = None
) -> NPCDialogueContext:
    """
    Factory function to create dialogue context from live NPC data.
    
    Args:
        npc_name: Which NPC
        npc_profile: NPCProfile object from NPCManager
        player_actual_skills: Dict of skill_name -> level (0.0 to 1.0)
        player_lie_history: Dict of npc_name -> was_lie_caught (boolean)
    
    Returns:
        NPCDialogueContext ready for dialogue generation
    """
    player_lie_history = player_lie_history or {}
    
    return NPCDialogueContext(
        npc_name=npc_name,
        npc_traits=npc_profile.remnants,  # Use remnants, not get_traits()
        player_actual_skills=player_actual_skills,
        player_previous_lies_caught=player_lie_history.get(npc_name, False)
    )
