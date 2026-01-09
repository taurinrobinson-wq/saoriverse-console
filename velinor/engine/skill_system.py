"""
Skill System: Player Competency & Claims
=========================================

Manages player skills and the gap between what they claim vs what they have.
Integrates with NPCManager to apply REMNANTS consequences based on skill performance.

Key Design:
- Player can claim any skill (truth or lie)
- If they fail a task with a claimed skill, NPCs discover the lie
- Success/failure → REMNANTS shifts + dialogue branches
- Social ripples through influence_map when lies are discovered
"""

from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
from copy import deepcopy


class SkillDomain(Enum):
    """Categories of skills in Velinor."""
    CRAFTING = "crafting"           # Boat-making, weaving, construction
    HEALING = "healing"             # Herbalism, field medicine
    NAVIGATION = "navigation"       # Route-finding, survival, tracking
    STEALTH = "stealth"            # Infiltration, misdirection, perception
    SOCIAL = "social"              # Persuasion, negotiation, reading people
    RITUAL = "ritual"              # Spiritual practice, ceremony
    TRADE = "trade"                # Commerce, appraisal, bartering
    DEFENSE = "defense"            # Combat, discipline, leadership
    OBSERVATION = "observation"    # Reading environments, noticing details


class SkillLevel(Enum):
    """Proficiency levels."""
    NOVICE = 0.3       # Can do basics, will struggle with complex tasks
    APPRENTICE = 0.6   # Competent at standard tasks
    JOURNEYMAN = 0.8   # Skilled, can handle difficult tasks
    MASTER = 0.95      # Expert, rarely fails


class PlayerSkill:
    """Represents a single player skill with proficiency."""
    
    def __init__(self, name: str, domain: SkillDomain, level: SkillLevel = SkillLevel.APPRENTICE):
        self.name = name
        self.domain = domain
        self.level = level.value  # 0.3 to 0.95
        self.experience = 0.0     # Tracks progress toward next level
    
    def __repr__(self):
        return f"Skill({self.name}, {self.domain.value}, {self.level:.2f})"
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "domain": self.domain.value,
            "level": self.level,
            "experience": self.experience
        }


class SkillManager:
    """Manages player skills and skill claims."""
    
    def __init__(self):
        """Initialize empty skill list."""
        self.skills: Dict[str, PlayerSkill] = {}
        self.claims_history: List[Dict] = []  # Track all claims for debugging
    
    def add_skill(self, skill: PlayerSkill) -> None:
        """Add a skill to player's repertoire."""
        self.skills[skill.name] = skill
    
    def has_skill(self, skill_name: str) -> bool:
        """Check if player has a skill."""
        return skill_name in self.skills
    
    def get_skill(self, skill_name: str) -> Optional[PlayerSkill]:
        """Get skill object by name."""
        return self.skills.get(skill_name)
    
    def get_skill_level(self, skill_name: str) -> float:
        """Get skill proficiency (0.3-0.95)."""
        skill = self.skills.get(skill_name)
        return skill.level if skill else 0.0
    
    def get_skills_by_domain(self, domain: SkillDomain) -> List[PlayerSkill]:
        """Get all skills in a domain."""
        return [s for s in self.skills.values() if s.domain == domain]
    
    def list_all_skills(self) -> List[str]:
        """Get list of all skill names."""
        return list(self.skills.keys())
    
    def export_skills(self) -> Dict:
        """Export all skills as JSON."""
        return {
            name: skill.to_dict()
            for name, skill in self.skills.items()
        }


class SkillClaim:
    """Represents a single claim about having a skill."""
    
    def __init__(
        self,
        player_skill_manager: SkillManager,
        npc_name: str,
        skill_claimed: str,
        is_truthful: bool
    ):
        """
        Initialize a skill claim.
        
        Args:
            player_skill_manager: Reference to player's SkillManager
            npc_name: Who the claim is made to
            skill_claimed: Name of skill being claimed
            is_truthful: Whether player actually has this skill
        """
        self.npc_name = npc_name
        self.skill_claimed = skill_claimed
        self.is_truthful = is_truthful
        self.player_skill_mgr = player_skill_manager
        
        # Compute actual player skill level
        self.player_actual_level = player_skill_manager.get_skill_level(skill_claimed)
    
    def is_lie(self) -> bool:
        """Check if this claim is a lie."""
        return not self.is_truthful
    
    def will_likely_fail(self, difficulty: float = 0.6) -> bool:
        """
        Predict if player will fail the task.
        
        Args:
            difficulty: Task difficulty (0.0-1.0). Higher = harder.
        
        Returns:
            True if player_actual_level < difficulty
        """
        return self.player_actual_level < difficulty
    
    def discovery_confidence(self) -> float:
        """
        If claim is a lie, how obvious is it that they're lying?
        
        Higher = more obvious the lie, easier to catch.
        """
        if self.is_truthful:
            return 0.0
        
        # Lies are easier to catch if player has NO skill at all
        # vs has SOME skill but claims a level they don't have
        if self.player_actual_level == 0.0:
            return 0.95  # Obviously lying
        else:
            return 0.5 + (0.45 * (1.0 - self.player_actual_level))
    
    def to_dict(self) -> Dict:
        return {
            "npc": self.npc_name,
            "skill_claimed": self.skill_claimed,
            "is_truthful": self.is_truthful,
            "player_actual_level": self.player_actual_level,
            "discovery_confidence": self.discovery_confidence()
        }


class SkillTaskOutcome:
    """Represents the outcome of attempting a skill task."""
    
    def __init__(
        self,
        skill_claim: SkillClaim,
        task_difficulty: float,
        execution_roll: float  # 0.0-1.0, randomness/luck
    ):
        """
        Initialize task outcome.
        
        Args:
            skill_claim: The SkillClaim this task is testing
            task_difficulty: How hard the task is (0.0-1.0)
            execution_roll: Random factor (0.0-1.0)
        """
        self.claim = skill_claim
        self.task_difficulty = task_difficulty
        self.execution_roll = execution_roll
        self.success = self._compute_success()
        self.lie_discovered = self._compute_lie_discovery()
    
    def _compute_success(self) -> bool:
        """
        Determine if task succeeds.
        
        Success happens if: (player_level + execution_roll) >= task_difficulty
        """
        combined_ability = self.claim.player_actual_level + (self.execution_roll * 0.3)
        return combined_ability >= self.task_difficulty
    
    def _compute_lie_discovery(self) -> bool:
        """
        Determine if NPC discovers the lie (if it is one).
        
        Only matters if claim is false. Discovery depends on:
        - How obvious the lie is
        - Whether the task fails (failure makes lies obvious)
        """
        if self.claim.is_truthful:
            return False
        
        # If task fails, lie is almost certainly discovered
        if not self.success:
            return True
        
        # If task succeeds, lie might not be discovered
        # (player got lucky, or NPC didn't scrutinize closely)
        discovery_confidence = self.claim.discovery_confidence()
        return self.execution_roll > (1.0 - discovery_confidence)
    
    def get_remnants_effects(self) -> Dict[str, float]:
        """
        Compute REMNANTS shifts based on outcome.
        
        Returns dict of trait → delta
        """
        effects = {}
        
        if self.success:
            # Task succeeded — NPC is impressed/trusting
            effects["trust"] = 0.1
            effects["resolve"] = 0.05
            effects["authority"] = 0.05
            effects["skepticism"] = -0.1
        else:
            # Task failed — NPC is disappointed/cautious
            effects["trust"] = -0.1
            effects["skepticism"] = 0.15
            effects["empathy"] = -0.05  # Disappointed in player
        
        if self.lie_discovered:
            # Lie was discovered — significant trust damage
            effects["trust"] = effects.get("trust", 0.0) - 0.2
            effects["skepticism"] = effects.get("skepticism", 0.0) + 0.25
            effects["nuance"] = -0.1  # "They seem simpler/deceptive now"
        
        return effects
    
    def to_dict(self) -> Dict:
        return {
            "claim": self.claim.to_dict(),
            "task_difficulty": self.task_difficulty,
            "execution_roll": self.execution_roll,
            "success": self.success,
            "lie_discovered": self.lie_discovered,
            "remnants_effects": self.get_remnants_effects()
        }


class SkillDialogueContext:
    """
    Context for generating skill-specific dialogue branches.
    
    Determines what dialogue options appear based on:
    - What skill the NPC is offering to teach
    - What skills the player has
    - What skills the player might claim
    """
    
    def __init__(
        self,
        npc_name: str,
        skill_being_taught: str,
        player_skill_manager: SkillManager
    ):
        self.npc_name = npc_name
        self.skill_being_taught = skill_being_taught
        self.player_skill_mgr = player_skill_manager
        
        self.player_has_skill = player_skill_manager.has_skill(skill_being_taught)
        self.player_skill_level = player_skill_manager.get_skill_level(skill_being_taught)
    
    def dialogue_options(self) -> Dict[str, str]:
        """
        Generate available dialogue options.
        
        Returns dict of {option_key: description}
        """
        options = {}
        
        # Option 1: Honest admission
        if self.player_has_skill:
            options["admit_skilled"] = "Admit you have experience with this"
        else:
            options["admit_novice"] = "Admit you're new to this"
        
        # Option 2: Lie (always available)
        if not self.player_has_skill:
            options["claim_skilled"] = "Claim you have experience (lie)"
        elif self.player_skill_level < 0.8:
            options["exaggerate_skill"] = "Claim you're more skilled than you are"
        
        # Option 3: Partial truth / deflection
        options["deflect"] = "Change the subject or deflect"
        
        # Option 4: Ask to learn
        options["ask_to_learn"] = "Ask if they can teach you"
        
        return options
    
    def get_dialogue_flavor(self, chosen_option: str) -> str:
        """
        Get flavor text for a dialogue option.
        
        This is what the player sees when hovering over/selecting an option.
        """
        flavors = {
            "admit_skilled": "Be honest about your experience.",
            "admit_novice": "Admit you're still learning.",
            "claim_skilled": "Risk it. Claim expertise you don't have.",
            "exaggerate_skill": "Stretch the truth about your abilities.",
            "deflect": "Avoid committing to anything.",
            "ask_to_learn": "Show genuine interest in learning."
        }
        return flavors.get(chosen_option, "")
    
    def to_dict(self) -> Dict:
        return {
            "npc": self.npc_name,
            "skill_offered": self.skill_being_taught,
            "player_has_skill": self.player_has_skill,
            "player_skill_level": self.player_skill_level,
            "dialogue_options": self.dialogue_options()
        }


# Preset skills for Velinor
def create_velinor_skills() -> Dict[str, PlayerSkill]:
    """Create the skill list for Velinor."""
    return {
        # Crafting
        "Boat-Making": PlayerSkill("Boat-Making", SkillDomain.CRAFTING),
        "Weaving": PlayerSkill("Weaving", SkillDomain.CRAFTING),
        "Shrine-Masonry": PlayerSkill("Shrine-Masonry", SkillDomain.CRAFTING),
        
        # Healing
        "Herbalism": PlayerSkill("Herbalism", SkillDomain.HEALING),
        "Field Medicine": PlayerSkill("Field Medicine", SkillDomain.HEALING),
        
        # Navigation
        "Route-Finding": PlayerSkill("Route-Finding", SkillDomain.NAVIGATION),
        "Survival Tracking": PlayerSkill("Survival Tracking", SkillDomain.NAVIGATION),
        "Environmental Reading": PlayerSkill("Environmental Reading", SkillDomain.NAVIGATION),
        
        # Stealth
        "Stealth Movement": PlayerSkill("Stealth Movement", SkillDomain.STEALTH),
        "Infiltration": PlayerSkill("Infiltration", SkillDomain.STEALTH),
        "Misdirection": PlayerSkill("Misdirection", SkillDomain.STEALTH),
        
        # Social
        "Persuasion": PlayerSkill("Persuasion", SkillDomain.SOCIAL),
        "Negotiation": PlayerSkill("Negotiation", SkillDomain.SOCIAL),
        "Social Inference": PlayerSkill("Social Inference", SkillDomain.SOCIAL),
        "Reading People": PlayerSkill("Reading People", SkillDomain.SOCIAL),
        
        # Ritual
        "Ritual Practice": PlayerSkill("Ritual Practice", SkillDomain.RITUAL),
        "Spiritual Presence": PlayerSkill("Spiritual Presence", SkillDomain.RITUAL),
        "Narrative Memory": PlayerSkill("Narrative Memory", SkillDomain.RITUAL),
        
        # Trade
        "Commerce": PlayerSkill("Commerce", SkillDomain.TRADE),
        "Appraisal": PlayerSkill("Appraisal", SkillDomain.TRADE),
        "Bartering": PlayerSkill("Bartering", SkillDomain.TRADE),
        
        # Defense
        "Combat": PlayerSkill("Combat", SkillDomain.DEFENSE),
        "Discipline": PlayerSkill("Discipline", SkillDomain.DEFENSE),
        "Leadership": PlayerSkill("Leadership", SkillDomain.DEFENSE),
        
        # Observation
        "Environmental Perception": PlayerSkill("Environmental Perception", SkillDomain.OBSERVATION),
        "Detail Noticing": PlayerSkill("Detail Noticing", SkillDomain.OBSERVATION),
    }
