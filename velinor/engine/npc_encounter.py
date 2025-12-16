"""
NPC Encounter Generation System

Generates complete encounter snapshots including:
1. NPC dialogue (auto-generated from lexicon + trait)
2. Player choice menu (auto-generated from NPC state)
3. NPC REMNANTS state before/after
4. Context-aware variations (greeting, conflict, resolution)

This enables truly emergent encounters: no two runs feel identical.
"""

import random
from typing import Dict, List, Any, Optional
from .npc_dialogue import generate_dialogue, generate_choices


# ============================================================================
# ENCOUNTER TEMPLATES: Fixed beats with flexible dialogue
# ============================================================================

ENCOUNTER_CONTEXTS = {
    "greeting": {
        "templates": [
            "You approach {npc}.",
            "{npc} turns to face you, curious.",
            "There's {npc}, working quietly."
        ]
    },
    "alliance": {
        "templates": [
            "You ask {npc} to join you.",
            "{npc} considers your proposal carefully.",
            "You extend an offer of partnership to {npc}."
        ]
    },
    "conflict": {
        "templates": [
            "Tension rises between you and {npc}.",
            "{npc} confronts you directly.",
            "A disagreement surfaces between you."
        ]
    },
    "resolution": {
        "templates": [
            "Perhaps there's a way forward with {npc}.",
            "{npc} looks at you with new eyes.",
            "Understanding blooms between you both."
        ]
    }
}


def generate_encounter_intro(npc_name: str, context: str = "greeting") -> str:
    """Generate context-appropriate encounter introduction."""
    if context not in ENCOUNTER_CONTEXTS:
        context = "greeting"
    
    templates = ENCOUNTER_CONTEXTS[context]["templates"]
    template = random.choice(templates)
    return template.format(npc=npc_name)


# ============================================================================
# FULL ENCOUNTER GENERATOR
# ============================================================================

def generate_encounter(npc_name: str, 
                      remnants: Dict[str, float],
                      encounter_id: int,
                      context: str = "greeting") -> Dict[str, Any]:
    """
    Generate a complete NPC encounter with dialogue + choices.
    
    Args:
        npc_name: Name of the NPC
        remnants: Current REMNANTS trait values
        encounter_id: Which encounter number this is (for sequencing)
        context: Type of encounter (greeting, alliance, conflict, resolution)
    
    Returns:
        Dictionary with encounter data:
        {
            "encounter_id": int,
            "npc": str,
            "context": str,
            "intro": str,
            "dialogue": str,
            "choices": [{"trait": str, "text": str, "value": float}, ...],
            "remnants": dict (current state),
            "dialogue_meta": {
                "dominant_trait": str,
                "dominant_value": float
            }
        }
    """
    
    # Generate intro
    intro = generate_encounter_intro(npc_name, context)
    
    # Generate NPC dialogue
    dialogue = generate_dialogue(npc_name, remnants, context)
    
    # Generate player choices
    choices = generate_choices(npc_name, remnants, num_choices=3)
    
    # Get dominant trait for metadata
    dominant_trait, dominant_value = max(remnants.items(), key=lambda x: x[1])
    
    return {
        "encounter_id": encounter_id,
        "npc": npc_name,
        "context": context,
        "intro": intro,
        "dialogue": dialogue,
        "choices": choices,
        "remnants": remnants,
        "dialogue_meta": {
            "dominant_trait": dominant_trait,
            "dominant_value": round(dominant_value, 2)
        }
    }


# ============================================================================
# MULTI-NPC SCENE GENERATOR
# ============================================================================

def generate_scene(npcs_dict: Dict[str, Dict[str, float]],
                  encounter_id: int,
                  context: str = "greeting") -> Dict[str, Any]:
    """
    Generate encounter data for all NPCs in current scene.
    
    Useful for showing entire marketplace reaction to player.
    
    Args:
        npcs_dict: Dict of {npc_name: remnants_dict}
        encounter_id: Encounter sequence number
        context: Scene context
    
    Returns:
        Dictionary with all NPC encounters:
        {
            "scene_id": int,
            "context": str,
            "npcs": [encounter, encounter, ...],
            "dominant_mood": str (most common dominant trait)
        }
    """
    
    encounters = []
    for npc_name, remnants in npcs_dict.items():
        encounter = generate_encounter(npc_name, remnants, encounter_id, context)
        encounters.append(encounter)
    
    # Calculate dominant mood across all NPCs
    all_dominant_traits = [enc["dialogue_meta"]["dominant_trait"] for enc in encounters]
    dominant_mood = max(set(all_dominant_traits), key=all_dominant_traits.count)
    
    return {
        "scene_id": encounter_id,
        "context": context,
        "npcs": encounters,
        "dominant_mood": dominant_mood
    }


# ============================================================================
# DIALOGUE + CHOICES PRETTY PRINTER
# ============================================================================

def print_encounter(encounter: Dict[str, Any], full_details: bool = True) -> None:
    """Pretty-print an encounter with formatting."""
    print()
    print(f"{'='*70}")
    print(f"ENCOUNTER #{encounter['encounter_id']} - {encounter['npc'].upper()}")
    print(f"{'='*70}")
    print(f"\n{encounter['intro']}")
    print(f"\n{encounter['dialogue']}")
    print(f"\nYour Choices:")
    
    for i, choice in enumerate(encounter['choices'], 1):
        trait_display = f"[{choice['trait'].upper()}]"
        trait_bar_length = int(choice['value'] * 10)
        trait_bar = "#" * trait_bar_length + "-" * (10 - trait_bar_length)
        print(f"  {i}. {trait_display} [{trait_bar}] {choice['text']}")
    
    if full_details:
        print(f"\n[NPC State: {encounter['dialogue_meta']['dominant_trait']} dominant at {encounter['dialogue_meta']['dominant_value']}]")
    print()


def print_scene(scene: Dict[str, Any], summary_only: bool = False) -> None:
    """Pretty-print a full scene with all NPC encounters."""
    print(f"\n{'#'*70}")
    print(f"SCENE #{scene['scene_id']} - {scene['context'].upper()}")
    print(f"Dominant Mood: {scene['dominant_mood'].upper()}")
    print(f"{'#'*70}")
    
    for i, encounter in enumerate(scene['npcs'], 1):
        if summary_only:
            print(f"\n[{i}] {encounter['npc']:12} | {encounter['dialogue'][:60]}...")
        else:
            print_encounter(encounter, full_details=False)


# ============================================================================
# ENCOUNTER SEQUENCE BUILDER
# ============================================================================

def build_encounter_sequence(npcs_dict_sequence: List[Dict[str, Dict[str, float]]],
                            contexts: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Build a sequence of encounters across multiple NPC states.
    
    Useful for showing how NPCs evolve across decision sequence.
    
    Args:
        npcs_dict_sequence: List of NPC dicts, one per decision point
        contexts: Optional list of contexts (same length as sequence)
    
    Returns:
        List of encounter dicts
    """
    
    if contexts is None:
        contexts = ["greeting"] * len(npcs_dict_sequence)
    
    if len(contexts) != len(npcs_dict_sequence):
        contexts = contexts + ["neutral"] * (len(npcs_dict_sequence) - len(contexts))
    
    encounters = []
    for enc_id, (npcs_dict, context) in enumerate(zip(npcs_dict_sequence, contexts), 1):
        scene = generate_scene(npcs_dict, enc_id, context)
        encounters.append(scene)
    
    return encounters
