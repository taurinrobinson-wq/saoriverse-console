"""
🎭 FACTION PRIORITY OVERRIDES: Philosophy as Narrative Force
============================================================

Applies faction philosophy to block priorities as subtle nudges.

This ensures that NPCs don't just respond to player emotion, but also
to their faction's values. Over time, these small consistent nudges
shape the tone of all interactions, making the world feel coherent.

Example:
    Nima (griever) boosting CONTAINMENT blocks = "I can hold this pain"
    This is both her personality AND Nima faction's philosophy
    (griefers specialize in holding emotional weight)
    
    Elenya (witness) boosting IDENTITY_INJURY blocks = "What this did to me"
    Both her pain AND Elenya faction's philosophy
    (witness factions focus on the impact of violence on the soul)

The nudges are small (0.5-1.5 priority points), not overwhelming.
A block that's a natural choice based on REMNANTS stays natural.
But blocks that align with faction philosophy get gentle promotion.

This makes faction membership visible in dialogue patterns,
which makes the world feel like a living ecosystem of philosophies.
"""

from typing import Dict, Optional, List
from enum import Enum
from dataclasses import dataclass


class Faction(Enum):
    """Canonical factions in Saoriverse."""
    NIMA_FACTION = "nima"           # Griefers: hold emotional weight
    ELENYA_FACTION = "elenya"       # Witnesses: process trauma/impact
    MALRIK_FACTION = "malrik"       # Guides: gentle direction
    COREN_FACTION = "coren"         # Preservers: continuity and memory
    UNALIGNED = "unaligned"         # No faction pressure


@dataclass
class FactionNudge:
    """Record of a faction-based priority adjustment."""
    block_name: str
    faction: str
    original_priority: float
    delta: float
    final_priority: float
    philosophy: str  # Why this block aligns with faction
    
    def __str__(self) -> str:
        sign = "+" if self.delta >= 0 else ""
        return f"{self.block_name} ({self.faction}): {self.original_priority} {sign}{self.delta} → {self.final_priority}"


class FactionPriorityOverrides:
    """
    Apply faction-specific philosophy nudges to dialogue block priorities.
    
    Each faction has a philosophical stance that shapes which kinds of
    dialogue blocks get promoted or demoted:
    
    NIMA FACTION (Griefers - "We Hold"):
    - Philosophy: Emotional weight can be metabolized, transformed
    - Boosts: CONTAINMENT, PACING, VALIDATION, PROCESSING
    - Demotes: ESCAPE, SUPPRESSION, DENIAL
    - Represents: Characters processing grief with others
    
    ELENYA FACTION (Witnesses - "We Saw"):
    - Philosophy: Witnessing violence changes the witness
    - Boosts: IDENTITY_INJURY, AMBIVALENCE, MEMORY, QUESTIONING
    - Demotes: CERTAINTY, JUDGMENT, SIMPLIFICATION
    - Represents: Characters grappling with what they've seen
    
    MALRIK FACTION (Guides - "We Show the Way"):
    - Philosophy: Direction comes from wisdom, not force
    - Boosts: GENTLE_DIRECTION, WISDOM, ACKNOWLEDGMENT, COLLABORATION
    - Demotes: DOMINANCE, CONTROL, JUDGMENT
    - Represents: Characters who mentor and support
    
    COREN FACTION (Preservers - "We Remember"):
    - Philosophy: Continuity and memory preserve identity
    - Boosts: CONTINUITY, REFERENCE, HISTORY, COMMITMENT
    - Demotes: NOVELTY, RUPTURE, FORGETTING
    - Represents: Characters maintaining traditions and relationships
    """
    
    @staticmethod
    def apply_for_faction(
        block_priorities: Dict[str, float],
        faction: str,
        npc_name: Optional[str] = None
    ) -> tuple[Dict[str, float], List[FactionNudge]]:
        """
        Apply faction-specific philosophy nudges to block priorities.
        
        Args:
            block_priorities: Dict[block_name, priority]
            faction: Faction name (must match Faction enum)
            npc_name: For logging/debugging
            
        Returns:
            (adjusted_priorities, list_of_nudges)
        """
        
        adjusted = dict(block_priorities)
        nudges: List[FactionNudge] = []
        
        if faction.lower() == Faction.NIMA_FACTION.value:
            FactionPriorityOverrides._apply_nima_nudges(adjusted, nudges)
        
        elif faction.lower() == Faction.ELENYA_FACTION.value:
            FactionPriorityOverrides._apply_elenya_nudges(adjusted, nudges)
        
        elif faction.lower() == Faction.MALRIK_FACTION.value:
            FactionPriorityOverrides._apply_malrik_nudges(adjusted, nudges)
        
        elif faction.lower() == Faction.COREN_FACTION.value:
            FactionPriorityOverrides._apply_coren_nudges(adjusted, nudges)
        
        # If UNALIGNED or unknown, no nudges applied
        
        return adjusted, nudges
    
    @staticmethod
    def _apply_nima_nudges(
        priorities: Dict[str, float],
        nudges: List[FactionNudge]
    ) -> None:
        """
        Nima faction (Griefers): "We Hold"
        
        Philosophy: Emotional weight can be metabolized, transformed, held.
        These blocks reflect the work of processing grief with others.
        """
        
        # Core Nima blocks: holding, processing, pacing
        nima_boosts = {
            "CONTAINMENT": (1.5, "Nima specialty: holding emotional weight"),
            "PACING": (1.0, "Griever pacing: slow, deliberate processing"),
            "VALIDATION": (1.0, "Confirmation that the pain is real and acceptable"),
            "TOGETHERNESS": (1.5, "The cure is shared presence in grief"),
            "ACKNOWLEDGMENT": (1.0, "Naming what has been lost"),
            "PROCESSING": (1.5, "The work of transforming pain into meaning"),
            "RELATIONAL": (1.0, "Grief is shared, bonds deepen"),
        }
        
        for block, (delta, philosophy) in nima_boosts.items():
            if block in priorities:
                original = priorities[block]
                priorities[block] += delta
                nudges.append(FactionNudge(
                    block_name=block,
                    faction="nima",
                    original_priority=original,
                    delta=delta,
                    final_priority=priorities[block],
                    philosophy=philosophy
                ))
        
        # Nima reductions: bypassing grief
        nima_reductions = {
            "ESCAPE": (-0.5, "Griever stays in the pain, doesn't flee"),
            "SUPPRESSION": (-1.0, "Nima faces what happened, doesn't hide"),
            "DENIAL": (-1.0, "The work requires truth-telling"),
        }
        
        for block, (delta, philosophy) in nima_reductions.items():
            if block in priorities:
                original = priorities[block]
                priorities[block] += delta
                nudges.append(FactionNudge(
                    block_name=block,
                    faction="nima",
                    original_priority=original,
                    delta=delta,
                    final_priority=max(0.0, priorities[block]),
                    philosophy=philosophy
                ))
    
    @staticmethod
    def _apply_elenya_nudges(
        priorities: Dict[str, float],
        nudges: List[FactionNudge]
    ) -> None:
        """
        Elenya faction (Witnesses): "We Saw"
        
        Philosophy: Witnessing violence changes the witness.
        These blocks reflect the wound of seeing/knowing/understanding.
        """
        
        # Core Elenya blocks: witnessing, identity impact, complexity
        elenya_boosts = {
            "IDENTITY_INJURY": (1.5, "Witness fact: seeing changes who you are"),
            "AMBIVALENCE": (1.5, "Witnesses hold two truths: innocence lost + survival required"),
            "MEMORY": (1.5, "Elenya cannot forget what was witnessed"),
            "QUESTIONING": (1.0, "Witnesses question 'why' and 'how'"),
            "VULNERABILITY": (1.0, "The witness reveals their wounds too"),
            "PROCESSING": (1.0, "Making sense of what was seen"),
            "NUANCE": (1.0, "Witnesses understand complexity"),
        }
        
        for block, (delta, philosophy) in elenya_boosts.items():
            if block in priorities:
                original = priorities[block]
                priorities[block] += delta
                nudges.append(FactionNudge(
                    block_name=block,
                    faction="elenya",
                    original_priority=original,
                    delta=delta,
                    final_priority=priorities[block],
                    philosophy=philosophy
                ))
        
        # Elenya reductions: false healing
        elenya_reductions = {
            "CERTAINTY": (-1.0, "Witnesses know certainty is impossible"),
            "JUDGMENT": (-1.0, "Witnesses suspend judgment; complexity reigns"),
            "SIMPLIFICATION": (-0.5, "Witnesses know the world is not simple"),
            "DENIAL": (-1.0, "Cannot unsee what was witnessed"),
        }
        
        for block, (delta, philosophy) in elenya_reductions.items():
            if block in priorities:
                original = priorities[block]
                priorities[block] += delta
                nudges.append(FactionNudge(
                    block_name=block,
                    faction="elenya",
                    original_priority=original,
                    delta=delta,
                    final_priority=max(0.0, priorities[block]),
                    philosophy=philosophy
                ))
    
    @staticmethod
    def _apply_malrik_nudges(
        priorities: Dict[str, float],
        nudges: List[FactionNudge]
    ) -> None:
        """
        Malrik faction (Guides): "We Show the Way"
        
        Philosophy: Direction comes from wisdom, not force.
        These blocks reflect gentle mentorship and collaborative discovery.
        """
        
        # Core Malrik blocks: guidance, wisdom, collaboration
        malrik_boosts = {
            "GENTLE_DIRECTION": (1.5, "Guide specialty: suggesting paths without demanding"),
            "WISDOM": (1.5, "Drawing on experience to illuminate"),
            "ACKNOWLEDGMENT": (1.0, "Guides validate the traveler's starting point"),
            "COLLABORATION": (1.5, "The journey is shared; guides walk alongside"),
            "QUESTIONING": (1.0, "Guides ask questions that open possibilities"),
            "VALIDATION": (1.0, "Affirming the wisdom already within the seeker"),
            "RELATIONAL": (1.0, "The relationship itself is transformative"),
        }
        
        for block, (delta, philosophy) in malrik_boosts.items():
            if block in priorities:
                original = priorities[block]
                priorities[block] += delta
                nudges.append(FactionNudge(
                    block_name=block,
                    faction="malrik",
                    original_priority=original,
                    delta=delta,
                    final_priority=priorities[block],
                    philosophy=philosophy
                ))
        
        # Malrik reductions: coercion
        malrik_reductions = {
            "DOMINANCE": (-1.0, "Guides don't impose; they illuminate"),
            "CONTROL": (-1.0, "True guidance respects autonomy"),
            "JUDGMENT": (-0.5, "Guides suspend judgment of the path taken"),
            "DEMAND": (-1.0, "Guides request, not demand"),
        }
        
        for block, (delta, philosophy) in malrik_reductions.items():
            if block in priorities:
                original = priorities[block]
                priorities[block] += delta
                nudges.append(FactionNudge(
                    block_name=block,
                    faction="malrik",
                    original_priority=original,
                    delta=delta,
                    final_priority=max(0.0, priorities[block]),
                    philosophy=philosophy
                ))
    
    @staticmethod
    def _apply_coren_nudges(
        priorities: Dict[str, float],
        nudges: List[FactionNudge]
    ) -> None:
        """
        Coren faction (Preservers): "We Remember"
        
        Philosophy: Continuity and memory preserve identity.
        These blocks reflect tradition, relationship maintenance, and historical continuity.
        """
        
        # Core Coren blocks: continuity, memory, commitment
        coren_boosts = {
            "CONTINUITY": (1.5, "Preserver specialty: connecting past to present"),
            "REFERENCE": (1.5, "Calling upon shared history"),
            "HISTORY": (1.5, "The story of who we've been matters"),
            "MEMORY": (1.0, "Remembering is how we preserve"),
            "COMMITMENT": (1.5, "Vows and bonds endure across time"),
            "ACKNOWLEDGMENT": (1.0, "Naming and honoring what came before"),
            "RELATIONAL": (1.0, "Relationships are the bonds of continuity"),
        }
        
        for block, (delta, philosophy) in coren_boosts.items():
            if block in priorities:
                original = priorities[block]
                priorities[block] += delta
                nudges.append(FactionNudge(
                    block_name=block,
                    faction="coren",
                    original_priority=original,
                    delta=delta,
                    final_priority=priorities[block],
                    philosophy=philosophy
                ))
        
        # Coren reductions: rupture
        coren_reductions = {
            "RUPTURE": (-1.0, "Preservers work against rupture"),
            "FORGETTING": (-1.0, "Memory is Coren's vow against forgetting"),
            "NOVELTY": (-0.5, "Change is accepted, but within continuity"),
            "SEVERING": (-1.0, "Coren maintains bonds; doesn't sever"),
        }
        
        for block, (delta, philosophy) in coren_reductions.items():
            if block in priorities:
                original = priorities[block]
                priorities[block] += delta
                nudges.append(FactionNudge(
                    block_name=block,
                    faction="coren",
                    original_priority=original,
                    delta=delta,
                    final_priority=max(0.0, priorities[block]),
                    philosophy=philosophy
                ))


def get_faction_from_npc_name(npc_name: str) -> str:
    """
    Map NPC names to their faction.
    
    This is a reference implementation. Update as your world grows.
    """
    npc_lower = npc_name.lower()
    
    # Nima faction (griefers)
    if npc_lower in ["nima", "ravi"]:
        return Faction.NIMA_FACTION.value
    
    # Elenya faction (witnesses)
    elif npc_lower in ["kaelen", "torven"]:
        return Faction.ELENYA_FACTION.value
    
    # Malrik faction (guides)
    elif npc_lower in ["lysander", "sera"]:
        return Faction.MALRIK_FACTION.value
    
    # Coren faction (preservers)
    elif npc_lower in ["marin", "celeste"]:
        return Faction.COREN_FACTION.value
    
    else:
        return Faction.UNALIGNED.value
