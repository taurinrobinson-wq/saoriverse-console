#!/usr/bin/env python3
"""
Demo script to show the enhanced conversational features of Emotional OS.
This demonstrates how the system remembers context and deepens responses over time.
"""

from parser.enhanced_signal_parser import enhanced_parse_input, generate_follow_up_question

def demo_conversation():
    print("🕯 Emotional OS - Conversational Demo")
    print("=" * 50)
    
    # Simulate a conversation with increasing depth
    conversation_history = []
    
    # Example conversation inputs
    inputs = [
        "I feel stuck and recursive, like I'm going in circles with this grief",
        "Yeah, it's about losing someone close to me. It keeps coming back in waves",
        "The ache feels sacred somehow, like I don't want to let go of missing them"
    ]
    
    for i, user_input in enumerate(inputs):
        print(f"\n💭 Turn {i+1}")
        print("-" * 20)
        print(f"User: {user_input}")
        
        # Create conversation context
        conversation_context = {
            'depth': i,
            'history': conversation_history
        }
        
        # Parse with enhanced system
        result = enhanced_parse_input(
            user_input, 
            "parser/signal_lexicon.json",
            conversation_context=conversation_context
        )
        
        # Add to history
        conversation_history.append({
            'input': user_input,
            'response': result["voltage_response"],
            'glyphs': result["glyphs"]
        })
        
        # Show response
        print(f"\n🤖 System: {result['voltage_response']}")
        
        # Generate follow-up
        follow_up = generate_follow_up_question(result, conversation_history)
        print(f"❓ Follow-up: {follow_up}")
        
        # Show activated glyphs
        if result["glyphs"]:
            print(f"\n🔮 Activated glyphs: {', '.join([g['glyph_name'] for g in result['glyphs'][:3]])}")
        
        print(f"⚡ Signals: {', '.join(result['signals']) if result['signals'] else 'None'}")
    
    print("\n" + "=" * 50)
    print("Notice how the responses evolved based on conversation depth and recurring themes!")

if __name__ == "__main__":
    demo_conversation()