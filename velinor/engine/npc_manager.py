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
                
                # Ripple nudges trust/skepticism based on sign
                self.npcs[to_npc].adjust_trait("trust", ripple_value)
                self.npcs[to_npc].adjust_trait("skepticism", -ripple_value)
    
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
            "Nima": -0.08,      # Ravi's trust weakens Nima's distrust slightly
            "Tovren": 0.1,      # Ravi's openness encourages Tovren's trust
            "Mariel": 0.05
        },
        "Nima": {
            "Ravi": -0.05,      # Nima's skepticism nudges Ravi toward doubt
            "Kaelen": -0.15,    # Nima's suspicion intensifies Kaelen distrust
            "Mariel": 0.1
        },
        "Kaelen": {
            "Tovren": -0.1,     # Kaelen's shifty presence worries merchants
            "Korrin": 0.05,     # Gossip and thieves circulate rumors
            "Drossel": 0.2      # Kaelen's thief nature aligns with Drossel's authority
        },
        "Tovren": {
            "Ravi": 0.05        # Practical caution spreads to merchants
        },
        "Sera": {
            "Mariel": 0.15      # Sera's trust in Mariel is reciprocal
        },
        "Mariel": {
            "Ravi": 0.1,        # Mariel's respect strengthens Ravi
            "Nima": 0.1         # Mariel's wisdom calms Nima's skepticism
        },
        "Drossel": {
            "Kaelen": 0.15,     # Drossel respects Kaelen's criminality
            "Korrin": -0.1,     # Drossel mistrusts even allies; gossips are loose cannons
            "Tovren": -0.2,     # Drossel's presence darkens merchants' suspicion
            "Ravi": -0.25,      # Drossel's criminality erodes Ravi's trust in community
            "Nima": 0.05        # Nima's suspicion resonates with Drossel's distrust
        }
    }
