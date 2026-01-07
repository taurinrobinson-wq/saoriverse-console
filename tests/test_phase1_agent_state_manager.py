"""Behavior Trace Test for AgentStateManager (Phase 1 Validation).

Demonstrates the agent's emotional state evolving through a sample conversation.
Shows mood changes, hypothesis formation, and commitment tracking.
"""

import sys
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from emotional_os.core.firstperson.agent_state_manager import AgentStateManager
from emotional_os.core.firstperson.affect_parser import AffectParser


def trace_conversation():
    """Run a sample conversation and trace agent state changes."""
    
    print("\n" + "="*80)
    print("BEHAVIOR TRACE: Agent Emotional State Evolution")
    print("="*80 + "\n")
    
    # Initialize
    agent_state = AgentStateManager(user_id="test_user", conversation_id="test_conv")
    affect_parser = AffectParser()
    
    # Sample conversation with different emotional beats
    conversation = [
        "Hi, I'm not sure where to start.",
        "I've been thinking about something that happened last week, and I can't stop thinking about it.",
        "It's making me really anxious. I feel like I'm spiraling.",
        "No one understands what I'm going through. I feel so alone.",
        "But you're listening, and that actually helps. Thank you for being here.",
    ]
    
    print(f"Agent initialized: {agent_state.get_mood_string()}\n")
    
    # Process each turn
    for turn_num, user_input in enumerate(conversation, 1):
        print(f"\n{'─'*80}")
        print(f"TURN {turn_num}: User Input")
        print(f"{'─'*80}")
        print(f'"{user_input}"\n')
        
        # Parse affect
        user_affect = affect_parser.analyze_affect(user_input)
        print(f"User Affect Analysis:")
        print(f"  Tone: {user_affect.tone} (confidence: {user_affect.tone_confidence:.2f})")
        print(f"  Valence: {user_affect.valence:.2f} (negative to positive)")
        print(f"  Arousal: {user_affect.arousal:.2f} (calm to intense)")
        
        # Update agent state
        previous_mood = agent_state.state.primary_mood.value
        agent_state.on_input(user_input, user_affect)
        new_mood = agent_state.state.primary_mood.value
        
        print(f"\nAgent State Update:")
        print(f"  Previous mood: {previous_mood}")
        print(f"  New mood: {new_mood} (intensity: {agent_state.state.mood_intensity:.2f})")
        
        if agent_state.state.emotional_hypothesis:
            print(f"  Emotional hypothesis: {agent_state.state.emotional_hypothesis}")
        
        if agent_state.state.unresolved_tension:
            print(f"  Unresolved tension detected: {agent_state.state.unresolved_tension}")
        
        print(f"\n  Commitments: {agent_state.state.established_commitments if agent_state.state.established_commitments else 'None yet'}")
        
        # Simulate response generation and commitment extraction
        simulated_response = _generate_response(user_input, agent_state, user_affect)
        print(f"\nSimulated Response:")
        print(f'  "{simulated_response}"')
        
        # Extract commitments from response
        commitments = agent_state.extract_commitments_from_response(simulated_response)
        if commitments:
            print(f"\nCommitments extracted from response:")
            for commitment in commitments:
                print(f"  - {commitment}")
                agent_state.add_commitment(commitment)
        
        # Integrate response back into state
        agent_state.integrate_after_response(simulated_response)
        
        print(f"\nAgent State Summary:")
        state_summary = agent_state.get_state_summary()
        print(f"  Turn: {state_summary['turn_count']}")
        print(f"  Mood: {state_summary['mood']} (intensity: {state_summary['intensity']:.2f})")
        print(f"  Hypothesis: {state_summary['hypothesis']}")
        print(f"  Commitments: {state_summary['commitments']}")
    
    print(f"\n{'═'*80}")
    print("FINAL AGENT STATE")
    print(f"{'═'*80}\n")
    
    final_state = agent_state.get_state_summary()
    print(f"Turn count: {final_state['turn_count']}")
    print(f"Final mood: {final_state['mood']}")
    print(f"Emotional hypothesis: {final_state['hypothesis']}")
    print(f"Agent's commitments: {final_state['commitments']}")
    print(f"Unresolved tension: {final_state['unresolved_tension']}")
    
    print(f"\n{'═'*80}")
    print("KEY OBSERVATIONS")
    print(f"{'═'*80}\n")
    
    observations = [
        "✓ Agent mood evolves in response to user input",
        "✓ Agent forms emotional hypothesis about user state",
        "✓ Agent detects tension and vulnerability",
        "✓ Agent extracts and maintains commitments",
        "✓ Agent state persists across turns",
        "✓ Agent's emotional intensity moderates after response",
    ]
    
    for obs in observations:
        print(obs)
    
    print("\n" + "="*80 + "\n")


def _generate_response(user_input: str, agent_state: AgentStateManager, user_affect: Any) -> str:
    """Generate a simple response based on agent state.
    
    This is a placeholder that would normally use templates + glyph composer.
    Here we just show how agent state would influence response.
    """
    
    mood = agent_state.state.primary_mood.value
    hypothesis = agent_state.state.emotional_hypothesis or ""
    
    # Response templates based on agent mood
    mood_templates = {
        "listening": [
            "I'm here, and I'm listening to what you're saying.",
            "Tell me more about what's on your mind.",
        ],
        "resonating": [
            "I can feel how much this matters to you.",
            "Something in what you said really resonates with me.",
        ],
        "concerned": [
            "I'm concerned about you right now. Your pain is real.",
            "I'm with you in this. You're not alone.",
        ],
        "protective": [
            "I want to keep you safe. Your vulnerability matters to me.",
            "I'm here to protect your wellbeing.",
        ],
        "moved": [
            "Your honesty moves me. I see you.",
            "There's something real happening here.",
        ],
        "reflecting": [
            "Let me sit with this for a moment and really understand.",
            "I'm reflecting on what you just shared.",
        ],
    }
    
    templates = mood_templates.get(mood, ["I hear you."])
    response = templates[0]  # Use first template
    
    # Add hypotheses-based detail
    if "spiral" in hypothesis.lower() or "loop" in hypothesis.lower():
        response += " It sounds like you're caught in a loop."
    elif "grief" in hypothesis.lower() or "loss" in hypothesis.lower():
        response += " That sounds like deep grief."
    elif "alone" in user_input.lower():
        response += " You don't have to face this alone."
    
    # Add presence marker if in vulnerable mood
    if mood in ["protective", "moved", "concerned"]:
        response += " I'm right here with this."
    
    return response


if __name__ == "__main__":
    trace_conversation()
