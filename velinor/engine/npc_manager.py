"""
NPC Manager: REMNANTS System
=============================

Manages NPC personality evolution through the REMNANTS trait system.
Implements TONE → REMNANTS correlations and multi-NPC ripple effects.

REMNANTS Traits:
- Resolve: Firmness, conviction, backbone
- Empathy: Emotional openness, compassion
- Memory: Recall of past, context awareness
- Nuance: Subtlety, shades of gray, complexity
- Authority: Command presence, decisiveness
- Need: Vulnerability, dependence, connection desire
- Trust: Confidence in others
- Skepticism: Doubt, caution, suspicion

TONE → REMNANTS Correlation:
- Trust (player) → raises Trust, Resolve; lowers Skepticism
- Observation (player) → raises Nuance, Memory; lowers Authority
- Narrative Presence (player) → raises Authority, Resolve; lowers Nuance
- Empathy (player) → raises Empathy, Need; lowers Resolve
"""

from typing import Dict, List, Tuple, Optional
from copy import deepcopy


class NPCProfile:
    """Represents a single NPC's REMNANTS trait profile."""
    
    def __init__(self, name: str, remnants: Optional[Dict[str, float]] = None):
        """
        Initialize an NPC profile.
        
        Args:
            name: NPC name (e.g., "Ravi", "Nima")
            remnants: Dict of REMNANTS traits, e.g. {"resolve": 0.6, "empathy": 0.5, ...}
                     All 8 traits must be present and 0.0-1.0 range.
        """
        self.name = name
        self.remnants = remnants or {
            "resolve": 0.5,
            "empathy": 0.5,
            "memory": 0.5,
            "nuance": 0.5,
            "authority": 0.5,
            "need": 0.5,
            "trust": 0.5,
            "skepticism": 0.5
        }
        self._validate_traits()
        
    
    def _validate_traits(self):
        """Ensure all 8 REMNANTS traits are present and in valid range [0.1, 0.9]."""
        required = {"resolve", "empathy", "memory", "nuance", "authority", "need", "trust", "skepticism"}
        present = set(self.remnants.keys())
        
        if present != required:
            raise ValueError(f"NPC {self.name} missing traits: {required - present}")
        
        for trait, value in self.remnants.items():
            if not 0.1 <= value <= 0.9:
                raise ValueError(f"{self.name}.{trait} = {value} out of range [0.1, 0.9]")
    
    @property
    def traits(self) -> Dict[str, float]:
        """Alias for remnants to match dialogue_context expectations."""
        return self.remnants
    
    def adjust_trait(self, trait: str, delta: float) -> None:
        """
        Adjust a single trait by delta, clamping to [0.1, 0.9].
        
        Args:
            trait: trait name, e.g. "resolve"
            delta: change value, e.g. 0.1 or -0.15
        """
        if trait not in self.remnants:
            raise ValueError(f"Unknown trait: {trait}")
        
        self.remnants[trait] = max(0.1, min(0.9, self.remnants[trait] + delta))
    
    def copy(self) -> 'NPCProfile':
        """Return a deep copy of this profile."""
        "Sealina": {"empathy": 0.06, "memory": 0.03},
        "Lark": {"authority": 0.05, "nuance": 0.03},
        "Nordia the Mourning Singer": {"empathy": 0.07, "memory": 0.04},
        "Orvak": {"skepticism": 0.06, "nuance": 0.03},
        "Tessa": {"empathy": 0.05, "nuance": 0.03},
        "Lira": {"trust": 0.05, "empathy": 0.04}
        return NPCProfile(self.name, deepcopy(self.remnants))
    
    def to_dict(self) -> Dict:
        """Export profile as JSON-serializable dict."""
        return {
            "name": self.name,
            "remnants": self.remnants
        }


class NPCManager:
    """
    Manages all NPCs and applies TONE → REMNANTS correlations and ripple effects.
    """
    
    # TONE → REMNANTS correlation map
    TONE_CORRELATION = {
        "trust": {
            "raise": ["trust", "resolve"],
            "lower": ["skepticism"]
        },
        "observation": {
            "raise": ["nuance", "memory"],
            "lower": ["authority"]
        },
        "narrative_presence": {
            "raise": ["authority", "resolve"],
            "lower": ["nuance"]
        },
        "empathy": {
            "raise": ["empathy", "need"],
            "lower": ["resolve"]
        }
    }
    
    def __init__(self):
        """Initialize empty NPC manager."""
        self.npcs: Dict[str, NPCProfile] = {}
        self.influence_map: Dict[str, Dict[str, float]] = {}
        # When True, ripple strength is scaled by source NPC dominance
        # in the relevant trait (trust for positive ripples, skepticism for negative).
        self.use_emergent_influence: bool = False
        # emergent base offset (multiplier baseline)
        self.emergent_baseline: float = 0.5
        self.history: List[Dict] = []
    
    def add_npc(self, npc: NPCProfile) -> None:
        """Add an NPC profile to the manager."""
        self.npcs[npc.name] = npc.copy()
    
    def add_npcs_batch(self, npcs: List[NPCProfile]) -> None:
        """Add multiple NPC profiles at once."""
        for npc in npcs:
            self.add_npc(npc)
    
    def set_influence(self, from_npc: str, to_npc: str, ripple_value: float) -> None:
        """
        Set ripple influence from one NPC to another.
        
        Args:
            from_npc: NPC name whose trait changes ripple outward
            to_npc: NPC name receiving the ripple effect
            ripple_value: influence strength, e.g. -0.1 (Ravi's trust weakens Nima's trust)
        """
        if from_npc not in self.influence_map:
            self.influence_map[from_npc] = {}
        self.influence_map[from_npc][to_npc] = ripple_value
    
    def apply_tone_effects(self, tone_effects: Dict[str, float]) -> None:
        """
        Apply TONE changes to all NPCs via correlation map.
        
        Args:
            tone_effects: dict of TONE stat changes, e.g. {"empathy": 0.2, "trust": -0.1}
        """
        # Step 1: Apply direct TONE → REMNANTS correlations to each NPC
        for npc in self.npcs.values():
            for tone_stat, delta in tone_effects.items():
                if tone_stat in self.TONE_CORRELATION:
                    correlation = self.TONE_CORRELATION[tone_stat]
                    
                    # Raise traits
                    for trait in correlation["raise"]:
                        npc.adjust_trait(trait, delta)
                    
                    # Lower traits
                    for trait in correlation["lower"]:
                        npc.adjust_trait(trait, -delta)
        
        # Step 2: Apply ripple effects between NPCs
        for from_npc, ripples in self.influence_map.items():
            if from_npc not in self.npcs:
                continue
            
            for to_npc, ripple_value in ripples.items():
                if to_npc not in self.npcs:
                    continue
                # Compute emergent multiplier if enabled
                effective_ripple = ripple_value
                if self.use_emergent_influence:
                    source = self.npcs[from_npc]
                    # Positive ripples align with source trust, negative with source skepticism
                    if ripple_value > 0:
                        source_factor = source.remnants.get('trust', 0.5)
                    else:
                        source_factor = source.remnants.get('skepticism', 0.5)

                    # Multiplier ranges roughly from (baseline+0.1) to (baseline+0.9)
                    multiplier = self.emergent_baseline + source_factor
                    effective_ripple = ripple_value * multiplier

                # Ripple nudges trust/skepticism based on sign
                self.npcs[to_npc].adjust_trait("trust", effective_ripple)
                self.npcs[to_npc].adjust_trait("skepticism", -effective_ripple)
    
    def simulate_encounters(self, encounters: List[Dict[str, float]]) -> List[Dict]:
        """
        Simulate multiple encounters, tracking NPC evolution through each one.
        
        Args:
            encounters: list of dicts, each with tone_effects
            
        Returns:
            history: list of snapshots, one per encounter
        """
        self.history = []
        
        for i, tone_effects in enumerate(encounters, start=1):
            self.apply_tone_effects(tone_effects)
            
            # Record snapshot
            snapshot = {
                "encounter": i,
                "tone_effects": tone_effects,
                "npc_profiles": {
                    name: npc.to_dict() for name, npc in self.npcs.items()
                }
            }
            self.history.append(snapshot)
        
        return self.history
    
    def get_npc(self, name: str) -> Optional[NPCProfile]:
        """Get an NPC profile by name."""
        return self.npcs.get(name)
    
    def get_npc_state(self, name: str) -> Dict:
        """Get current REMNANTS traits for an NPC."""
        npc = self.npcs.get(name)
        return npc.to_dict() if npc else None
    
    def get_all_npc_states(self) -> Dict[str, Dict]:
        """Get current REMNANTS traits for all NPCs."""
        return {name: npc.to_dict() for name, npc in self.npcs.items()}
    
    def get_dominant_trait(self, npc_name: str) -> Tuple[str, float]:
        """
        Get the highest trait for an NPC (reflects their "personality flavor").
        
        Returns:
            (trait_name, trait_value)
        """
        npc = self.npcs.get(npc_name)
        if not npc:
            return None
        
        return max(npc.remnants.items(), key=lambda x: x[1])
    
    def get_trait_vector(self, npc_name: str) -> List[Tuple[str, float]]:
        """Get all traits for an NPC sorted by value (dominant to recessive)."""
        npc = self.npcs.get(npc_name)
        if not npc:
            return []
        
        return sorted(npc.remnants.items(), key=lambda x: x[1], reverse=True)
    
    def apply_skill_task_outcome(self, task_outcome) -> None:
        """
        Apply REMNANTS shifts from a skill task outcome.
        
        This integrates SkillTaskOutcome from skill_system.py with NPCManager.
        Handles:
        - Direct REMNANTS shift to the NPC
        - Ripple effects to connected NPCs (especially if lie discovered)
        - Korrin-specific lie propagation
        
        Args:
            task_outcome: SkillTaskOutcome object from skill_system.py
        """
        npc_name = task_outcome.claim.npc_name
        if npc_name not in self.npcs:
            return  # NPC not tracked, skip
        
        # Step 1: Apply direct REMNANTS effects
        npc = self.npcs[npc_name]
        for trait, delta in task_outcome.get_remnants_effects().items():
            npc.adjust_trait(trait, delta)
        
        # Step 2: If lie was discovered, amplify ripples to connected NPCs
        if task_outcome.lie_discovered:
            self._propagate_lie_discovery(npc_name, task_outcome)
        
        # Step 3: Record in history
        self.history.append({
            "type": "skill_task_outcome",
            "task_outcome": task_outcome.to_dict(),
            "direct_npc": npc_name,
            "ripple_npc": list(self.influence_map.get(npc_name, {}).keys())
        })
    
    def _propagate_lie_discovery(self, source_npc: str, task_outcome) -> None:
        """
        When a lie is discovered, propagate skepticism through social network.
        
        Korrin is special — she actively spreads rumors about lies.
        """
        # Connected NPCs lose trust in player (through the source NPC's skepticism)
        connected_npcs = self.influence_map.get(source_npc, {})
        
        for connected_npc in connected_npcs.keys():
            if connected_npc not in self.npcs:
                continue
            
            # Connected NPCs shift toward skepticism about the player
            npc = self.npcs[connected_npc]
            npc.adjust_trait("skepticism", 0.1)  # They hear about the deception
            npc.adjust_trait("trust", -0.08)
        
        # Korrin specifically weaponizes lies she hears about
        if "Korrin" in self.npcs and source_npc != "Korrin":
            korrin = self.npcs["Korrin"]
            # Korrin's skepticism goes up, memory of incident goes up
            korrin.adjust_trait("skepticism", 0.15)
            korrin.adjust_trait("memory", 0.1)
            # This makes her future dialogue about the lie more likely
    
    def export_state(self) -> Dict:
        """Export all NPC states and influence map for story JSON."""
        return {
            "npc_profiles": self.get_all_npc_states(),
            "influence_map": self.influence_map,
            "history": self.history
        }


# Preset NPC definitions with initial REMNANTS values
def create_marketplace_npcs() -> List[NPCProfile]:
    """
    Create the full marketplace NPC roster with initial REMNANTS values.
    """
    npcs = [
        # Ravi: Warm, open, trusting but cautious due to thieves
        NPCProfile("Ravi", {
            "resolve": 0.6,
            "empathy": 0.7,
            "memory": 0.6,
            "nuance": 0.4,
            "authority": 0.5,
            "need": 0.5,
            "trust": 0.7,
            "skepticism": 0.2
        }),
        
        # Nima: Suspicious, observant, deeply empathetic once trust is earned
        NPCProfile("Nima", {
            "resolve": 0.6,
            "empathy": 0.6,
            "memory": 0.7,
            "nuance": 0.8,
            "authority": 0.4,
            "need": 0.5,
            "trust": 0.3,
            "skepticism": 0.8
        }),
        
        # Kaelen: Shifty, nimble, untrustworthy but redeemable
        NPCProfile("Kaelen", {
            "resolve": 0.4,
            "empathy": 0.3,
            "memory": 0.6,
            "nuance": 0.5,
            "authority": 0.3,
            "need": 0.7,
            "trust": 0.2,
            "skepticism": 0.8       # capped at 0.8, was 0.9
        }),
        
        # Tovren: Practical, distrustful, values observation over dreaming
        NPCProfile("Tovren", {
            "resolve": 0.7,
            "empathy": 0.3,
            "memory": 0.6,
            "nuance": 0.3,
            "authority": 0.6,
            "need": 0.2,
            "trust": 0.4,
            "skepticism": 0.7
        }),
        
        # Sera: Gentle, shy, responds to empathy
        NPCProfile("Sera", {
            "resolve": 0.3,
            "empathy": 0.8,
            "memory": 0.5,
            "nuance": 0.6,
            "authority": 0.2,
            "need": 0.8,
            "trust": 0.6,
            "skepticism": 0.3
        }),
        
        # Dalen: Bold, reckless, values narrative presence
        NPCProfile("Dalen", {
            "resolve": 0.8,
            "empathy": 0.4,
            "memory": 0.5,
            "nuance": 0.2,
            "authority": 0.7,
            "need": 0.3,
            "trust": 0.5,
            "skepticism": 0.4
        }),
        
        # Mariel: Patient, wise, bridges merchants and shrine keepers
        NPCProfile("Mariel", {
            "resolve": 0.6,
            "empathy": 0.8,
            "memory": 0.8,         # capped at 0.8, was 0.9
            "nuance": 0.7,
            "authority": 0.5,
            "need": 0.4,
            "trust": 0.7,
            "skepticism": 0.2
        }),
        
        # Korrin: Gossip, suspicious, loves information
        NPCProfile("Korrin", {
            "resolve": 0.4,
            "empathy": 0.3,
            "memory": 0.8,
            "nuance": 0.7,
            "authority": 0.3,
            "need": 0.5,
            "trust": 0.3,
            "skepticism": 0.8
        }),
        
        # Drossel: Thieves' Leader - Charming yet Dangerous
        NPCProfile("Drossel", {
            "resolve": 0.8,       # Firm in his convictions, steady as leader
            "empathy": 0.2,       # Appears caring but internally cold
            "memory": 0.8,        # capped at 0.8, was 0.9
            "nuance": 0.8,        # capped at 0.8, was 0.9
            "authority": 0.8,     # capped at 0.8, was 0.9
            "need": 0.3,          # Self-sufficient, relies on no one
            "trust": 0.1,         # Trusts no one, distrusts by default
            "skepticism": 0.9     # High distrust, sees threats everywhere
        }),
        
        # Captain Veynar: Guard Captain - Weary Authority
        NPCProfile("Captain Veynar", {
            "resolve": 0.8,       # Steadfast despite exhaustion
            "empathy": 0.4,       # Compassionate but duty-bound
            "memory": 0.7,        # Remembers every theft, every cost
            "nuance": 0.5,        # Pragmatic, but understands complexities
            "authority": 0.9,     # Highest command presence (capped at 0.9)
            "need": 0.3,          # Self-reliant, carries burdens alone
            "trust": 0.6,         # Trusts those who keep law
            "skepticism": 0.5     # Cautious but not paranoid
        }),

        # Archivist Malrik: Skeptics' leader - guardian of records, high memory and skepticism
        NPCProfile("Archivist Malrik", {
            "resolve": 0.7,
            "empathy": 0.3,
            "memory": 0.9,       # Archivist: exceptional recall and context
            "nuance": 0.6,
            "authority": 0.7,
            "need": 0.3,
            "trust": 0.3,
            "skepticism": 0.7    # Leads the Skeptics; spreads doubt
        }),

        # High Seer Elenya: Mystics' leader - communal seer, high empathy and trust
        NPCProfile("High Seer Elenya", {
            "resolve": 0.5,
            "empathy": 0.9,
            "memory": 0.7,
            "nuance": 0.8,
            "authority": 0.6,
            "need": 0.4,
            "trust": 0.8,
            "skepticism": 0.2    # Mystics inspire faith, lower skepticism
        })
        ,
        # Saori: Oracle — measured, reflective, paradoxical (persistent presence)
        NPCProfile("Saori", {
            "resolve": 0.8,
            "empathy": 0.6,
            "memory": 0.85,
            "nuance": 0.9,
            "authority": 0.75,
            "need": 0.35,
            "trust": 0.4,
            "skepticism": 0.7
        }),
        # Coren: Mediator - bridges opposing factions, high nuance and trust
        NPCProfile("Coren the Mediator", {
            "resolve": 0.6,
            "empathy": 0.65,
            "memory": 0.6,
            "nuance": 0.8,
            "authority": 0.6,
            "need": 0.4,
            "trust": 0.75,
            "skepticism": 0.2
        })
        ,
        # Additional Tier-2 NPCs
        NPCProfile("Sealina", {
            "resolve": 0.65,
            "empathy": 0.85,
            "memory": 0.9,
            "nuance": 0.75,
            "authority": 0.55,
            "need": 0.8,
            "trust": 0.6,
            "skepticism": 0.6
        }),
        NPCProfile("Lark", {
            "resolve": 0.7,
            "empathy": 0.6,
            "memory": 0.8,
            "nuance": 0.65,
            "authority": 0.75,
            "need": 0.45,
            "trust": 0.65,
            "skepticism": 0.5
        }),
        NPCProfile("Nordia the Mourning Singer", {
            "resolve": 0.7,
            "empathy": 0.9,
            "memory": 0.9,
            "nuance": 0.8,
            "authority": 0.6,
            "need": 0.85,
            "trust": 0.55,
            "skepticism": 0.6
        }),
        NPCProfile("Helia", {
            "resolve": 0.8,
            "empathy": 0.75,
            "memory": 0.5,
            "nuance": 0.6,
            "authority": 0.55,
            "need": 0.6,
            "trust": 0.75,
            "skepticism": 0.5
        }),
        NPCProfile("Elka", {
            "resolve": 0.75,
            "empathy": 0.65,
            "memory": 0.45,
            "nuance": 0.5,
            "authority": 0.5,
            "need": 0.55,
            "trust": 0.7,
            "skepticism": 0.5
        }),
        NPCProfile("Inodora", {
            "resolve": 0.7,
            "empathy": 0.8,
            "memory": 0.8,
            "nuance": 0.65,
            "authority": 0.6,
            "need": 0.6,
            "trust": 0.7,
            "skepticism": 0.55
        }),
        NPCProfile("Rasha", {
            "resolve": 0.65,
            "empathy": 0.8,
            "memory": 0.55,
            "nuance": 0.6,
            "authority": 0.55,
            "need": 0.65,
            "trust": 0.85,
            "skepticism": 0.45
        }),
        NPCProfile("Juria & Korinth", {
            "resolve": 0.7,
            "empathy": 0.8,
            "memory": 0.65,
            "nuance": 0.65,
            "authority": 0.6,
            "need": 0.6,
            "trust": 0.85,
            "skepticism": 0.45
        }),
        NPCProfile("Lira", {
            "resolve": 0.65,
            "empathy": 0.85,
            "memory": 0.5,
            "nuance": 0.55,
            "authority": 0.5,
            "need": 0.55,
            "trust": 0.8,
            "skepticism": 0.4
        }),
        NPCProfile("Orvak", {
            "resolve": 0.7,
            "empathy": 0.5,
            "memory": 0.7,
            "nuance": 0.75,
            "authority": 0.65,
            "need": 0.75,
            "trust": 0.5,
            "skepticism": 0.8
        }),
        NPCProfile("Sanor", {
            "resolve": 0.75,
            "empathy": 0.55,
            "memory": 0.6,
            "nuance": 0.7,
            "authority": 0.6,
            "need": 0.8,
            "trust": 0.55,
            "skepticism": 0.85
        }),
        NPCProfile("Dakrin", {
            "resolve": 0.85,
            "empathy": 0.6,
            "memory": 0.55,
            "nuance": 0.7,
            "authority": 0.75,
            "need": 0.6,
            "trust": 0.65,
            "skepticism": 0.65
        }),
        NPCProfile("Kiv", {
            "resolve": 0.6,
            "empathy": 0.7,
            "memory": 0.9,
            "nuance": 0.85,
            "authority": 0.5,
            "need": 0.75,
            "trust": 0.55,
            "skepticism": 0.7
        }),
        NPCProfile("Seyla", {
            "resolve": 0.5,
            "empathy": 0.5,
            "memory": 0.85,
            "nuance": 0.8,
            "authority": 0.75,
            "need": 0.5,
            "trust": 0.5,
            "skepticism": 0.5
        }),
        NPCProfile("Velka", {
            "resolve": 0.5,
            "empathy": 0.5,
            "memory": 0.85,
            "nuance": 0.8,
            "authority": 0.75,
            "need": 0.5,
            "trust": 0.5,
            "skepticism": 0.5
        }),
        NPCProfile("Tala", {
            "resolve": 0.5,
            "empathy": 0.75,
            "memory": 0.5,
            "nuance": 0.7,
            "authority": 0.5,
            "need": 0.5,
            "trust": 0.8,
            "skepticism": 0.5
        }),
        NPCProfile("Tessa", {
            "resolve": 0.65,
            "empathy": 0.9,
            "memory": 0.85,
            "nuance": 0.8,
            "authority": 0.55,
            "need": 0.25,
            "trust": 0.45,
            "skepticism": 0.4
        })
    ]
    
    return npcs


def create_marketplace_influence_map() -> Dict[str, Dict[str, float]]:
    """
    Create ripple influence map showing how one NPC affects others.
    Negative values indicate skepticism/suspicion transfer.
    """
    return {
        "Ravi": {
            "Nima": 0.15,       # couple influence (exception to 0.1 cap)
            "Tovren": 0.1,      # Ravi's openness encourages Tovren's trust
            "Mariel": 0.05
        },
        "Nima": {
            "Ravi": -0.15,      # mutual couple influence (negative sign indicates Nima's skepticism)
            "Kaelen": -0.1,     # capped at 0.1
            "Mariel": 0.1
        },
        "Kaelen": {
            "Tovren": -0.1,     # Kaelen's shifty presence worries merchants
            "Korrin": 0.05,     # Gossip and thieves circulate rumors
            "Drossel": 0.1      # Dalen/Drossel/Kaelen camaraderie (capped at 0.1)
        },
        "Dalen": {
            "Ravi": 0.08,       # Dalen's bold presence lifts merchant morale slightly
            "Mariel": 0.05,     # Dalen's narrative presence encourages community bridging
            "Nima": -0.05,      # Dalen's recklessness can heighten Nima's suspicion
            "Drossel": 0.1,     # roguelike affinity
            "Kaelen": 0.1       # roguelike affinity
        },
        "Tovren": {
            "Ravi": 0.05,       # Practical caution spreads to merchants
            "Archivist Malrik": 0.1,  # practical alignment
            "High Seer Elenya": -0.1, # misaligned with mystical values
            "Captain Veynar": 0.1     # values safety in market
        },
        "Sera": {
            "Mariel": 0.1,      # Sera's trust in Mariel
            "Ravi": 0.1,        # communal influence (capped)
            "High Seer Elenya": 0.05
        },
        "Mariel": {
            "Ravi": 0.1,        # Mariel's respect strengthens Ravi
            "Nima": 0.1         # Mariel's wisdom calms Nima's skepticism
        },
        "Drossel": {
            "Kaelen": 0.1,
            "Korrin": -0.1,
            "Tovren": -0.1,
            "Ravi": -0.1,
            "Nima": 0.05
        },
        "Captain Veynar": {
            "Ravi": 0.1,        # Veynar's protection strengthens merchants' confidence
            "Tovren": 0.1,      # Practical alliance with practical merchant
            "Mariel": 0.08,     # Mutual respect between law and wisdom
            "Kaelen": -0.1,     # capped negative correlation
            "Drossel": -0.1,    # capped negative correlation
            "Nima": 0.05
        }
        ,
        "Archivist Malrik": {
            "Nima": -0.1,      # capped skepticism influence
            "Ravi": -0.1,
            "Kaelen": -0.05,
            "Mariel": 0.05,
            "High Seer Elenya": -0.1
        },
        "High Seer Elenya": {
            "Sera": 0.1,
            "Mariel": 0.1,
            "Ravi": 0.05,
            "Nima": 0.05,
            "Archivist Malrik": -0.1,
            "Saori": 0.05
        },
        "Coren the Mediator": {
            "Archivist Malrik": 0.1,
            "High Seer Elenya": 0.1,
            "Mariel": 0.05,
            "Kaelen": 0.08,
            "Korrin": 0.08
        }
        ,
        "Saori": {
            "Archivist Malrik": 0.08,
            "High Seer Elenya": 0.05,
            "Mariel": 0.04
        }
    }
