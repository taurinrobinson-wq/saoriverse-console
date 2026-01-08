"""
Test: Conversation Memory Layer

Demonstrates how the memory layer integrates two messages
and builds a comprehensive understanding of the user's state.
"""

from src.emotional_os_glyphs.conversation_memory import (
    ConversationMemory,
    SemanticParsing,
    ConfidenceLevel,
)
import json


def test_two_message_integration():
    """Test memory layer with the two-message conversation"""
    
    memory = ConversationMemory()
    
    print("=" * 90)
    print("CONVERSATION MEMORY LAYER TEST")
    print("=" * 90)
    
    # TURN 1: "I'm feeling so stressed today"
    print("\n" + "=" * 90)
    print("TURN 1: Initial Emotional Statement")
    print("=" * 90)
    
    user_input_1 = "I'm feeling so stressed today"
    parsed_1 = SemanticParsing(
        actor="I",
        primary_affects=["stress"],
        secondary_affects=[],
        tense="present",
        emphasis="so",
        domains=[],
        temporal_scope="today",
        thought_patterns=[],
        action_capacity="unknown",
        raw_input=user_input_1,
    )
    
    turn_1 = memory.add_turn(
        user_input=user_input_1,
        parsed=parsed_1,
        glyphs_identified=["Still Insight"],
        missing_elements=["causation", "somatic", "context", "duration", "agency"],
        clarifications_asked=["What triggered this stress?", "What triggered this feeling?"],
    )
    
    print(f"User: {user_input_1}")
    print(f"Parsed actor: {parsed_1.actor}")
    print(f"Primary affects: {parsed_1.primary_affects}")
    print(f"Temporal scope: {parsed_1.temporal_scope}")
    print(f"Glyphs: {turn_1.glyphs_identified}")
    print(f"\nIntegrated state after Turn 1:")
    print(f"  Affects: {memory.integrated_state.primary_affects}")
    print(f"  Intensity: {memory.integrated_state.intensity}")
    print(f"  Confidence: {memory.integrated_state.confidence}")
    print(f"  Needs: {memory.system_knowledge.high_confidence_needs}")
    
    # TURN 2: "I don't I just feel like I have so much on my mind at work that I can't even make one step forward."
    print("\n" + "=" * 90)
    print("TURN 2: Causal Elaboration")
    print("=" * 90)
    
    user_input_2 = "I don't I just feel like I have so much on my mind at work that I can't even make one step forward."
    parsed_2 = SemanticParsing(
        actor="I",
        primary_affects=["cognitive_overload"],
        secondary_affects=["paralysis", "immobility"],
        tense="present_habitual",
        emphasis="feel like",  # hedged
        domains=["work"],
        temporal_scope="ongoing",
        thought_patterns=["flooding", "incomplete (I don't I)"],
        action_capacity="paralyzed",
        raw_input=user_input_2,
    )
    
    turn_2 = memory.add_turn(
        user_input=user_input_2,
        parsed=parsed_2,
        glyphs_identified=["Still Insight", "Quiet Revelation", "Fragmentation"],
        missing_elements=[
            "specificity (what are these things?)",
            "priority (which is most urgent?)",
            "duration (how long building?)",
            "attempts (what have you tried?)",
        ],
        clarifications_asked=[
            "How many distinct things are competing for your mind?",
            "Which one is most time-critical?",
            "What would even one small step forward look like?",
        ],
    )
    
    print(f"User: {user_input_2}")
    print(f"Parsed actor: {parsed_2.actor}")
    print(f"Primary affects: {parsed_2.primary_affects}")
    print(f"Secondary affects: {parsed_2.secondary_affects}")
    print(f"Domain: {parsed_2.domains}")
    print(f"Thought patterns: {parsed_2.thought_patterns}")
    print(f"Action capacity: {parsed_2.action_capacity}")
    print(f"Glyphs: {turn_2.glyphs_identified}")
    
    # INTEGRATED VIEW
    print("\n" + "=" * 90)
    print("INTEGRATED UNDERSTANDING AFTER 2 TURNS")
    print("=" * 90)
    
    print(f"\nEmotional Profile: {memory.get_emotional_profile_brief()}")
    print(f"\nGlyph Evolution:")
    for i, glyphs in enumerate(memory.glyph_evolution, 1):
        print(f"  Turn {i}: {glyphs}")
    print(f"  Current Glyph Set: {memory.get_glyph_set()}")
    
    print(f"\nCausal Chain: {memory.get_causal_narrative()}")
    
    print(f"\nNext Clarifications:")
    for i, clarification in enumerate(memory.get_next_clarifications(), 1):
        print(f"  {i}. {clarification}")
    
    # DETAILED INTEGRATED STATE
    print("\n" + "=" * 90)
    print("DETAILED INTEGRATED STATE")
    print("=" * 90)
    
    state_dict = {
        "emotional": {
            "primary_affects": memory.integrated_state.primary_affects,
            "secondary_affects": memory.integrated_state.secondary_affects,
            "intensity": memory.integrated_state.intensity,
            "confidence": memory.integrated_state.confidence,
        },
        "context": {
            "domains": memory.integrated_state.primary_domains,
            "temporal_scope": memory.integrated_state.temporal_scope,
            "thought_patterns": memory.integrated_state.thought_patterns,
            "action_capacity": memory.integrated_state.action_capacity,
        },
        "causation": {
            "triggers": memory.causal_understanding.root_triggers,
            "mechanisms": memory.causal_understanding.mechanisms,
            "manifestations": memory.causal_understanding.manifestations,
            "agency_state": memory.causal_understanding.agency_state,
        },
        "system_knowledge": {
            "confirmed_facts": memory.system_knowledge.confirmed_facts,
            "needs": memory.system_knowledge.high_confidence_needs,
        },
    }
    
    print(json.dumps(state_dict, indent=2))
    
    # WHAT CHANGED
    print("\n" + "=" * 90)
    print("INFORMATION GAINED FROM TURN 2")
    print("=" * 90)
    
    changes = {
        "Domain specification": "generic -> WORK-specific",
        "Root trigger identified": "WORK DEMANDS",
        "Mechanism revealed": "COGNITIVE FLOODING",
        "Manifestations added": ["paralysis", "immobility"],
        "Thought pattern": "FRAGMENTED, RACING",
        "Agency state clarified": "PARALYZED (cannot progress)",
        "Confidence increased": "0.7 -> 0.85",
        "Glyph set enriched": ["Still Insight", "Quiet Revelation", "Fragmentation"],
    }
    
    for key, value in changes.items():
        if isinstance(value, list):
            print(f"  {key}: {', '.join(value)}")
        else:
            print(f"  {key}: {value}")
    
    # NEXT RESPONSE COMPOSITION
    print("\n" + "=" * 90)
    print("RECOMMENDED RESPONSE FOR TURN 3")
    print("=" * 90)
    
    print("\n1. ACKNOWLEDGE (informed by integrated state):")
    print("   'I hear you - work has flooded your mind with so many")
    print("    competing demands that even taking one step forward feels impossible'")
    
    print("\n2. VALIDATE (using glyph wisdom):")
    print("   'Insight sometimes arrives in fragments that need organizing'")
    
    print("\n3. CLARIFY (targeted to missing elements):")
    print("   'Help me understand: how many distinct things are competing")
    print("    for your mind, and which one is most time-critical?'")


if __name__ == "__main__":
    test_two_message_integration()
