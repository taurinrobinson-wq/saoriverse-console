#!/usr/bin/env python3
"""
Integration example showing how to connect auto-evolving glyphs
to your existing Saoriverse conversation flow
"""

import os
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_enhanced_conversation_demo():
    """
    Enhanced version of your conversation_demo.py that includes auto-evolving glyphs
    """

    enhanced_demo_code = '''#!/usr/bin/env python3
"""
Enhanced Saoriverse Conversation Demo with Auto-Evolving Glyphs
This replaces your existing conversation_demo.py with glyph evolution capabilities
"""

import requests
import json
import time
from typing import Dict, Optional

# Import the evolving glyph system
try:
    from evolving_glyph_integrator import EvolvingGlyphIntegrator
    EVOLUTION_AVAILABLE = True
except ImportError:
    print("Evolution system not available - falling back to basic mode")
    EVOLUTION_AVAILABLE = False

class EnhancedSaoriverse:
    """Enhanced Saoriverse with auto-evolving glyphs"""
    
    def __init__(self, 
                 supabase_function_url: str,
                 supabase_anon_key: str,
                 supabase_url: str = None,
                 enable_evolution: bool = True):
        
        self.basic_function_url = supabase_function_url
        self.basic_headers = {
            'Authorization': f'Bearer {supabase_anon_key}',
            'Content-Type': 'application/json'
        }
        
        # Initialize evolution system if available
        if EVOLUTION_AVAILABLE and enable_evolution:
            self.integrator = EvolvingGlyphIntegrator(
                supabase_function_url=supabase_function_url,
                supabase_anon_key=supabase_anon_key,
                supabase_url=supabase_url,
                enable_auto_evolution=True,
                evolution_frequency=3  # Check every 3 conversations
            )
            self.evolution_enabled = True
            print("Auto-evolving glyph system enabled!")
        else:
            self.integrator = None
            self.evolution_enabled = False
            print("Basic conversation mode (no evolution)")
    
    def chat(self, message: str, conversation_context: Optional[Dict] = None) -> Dict:
        """Enhanced chat method with optional evolution"""
        
        if self.evolution_enabled and self.integrator:
            # Use the evolving integrator
            result = self.integrator.process_conversation_with_evolution(
                message=message,
                conversation_context=conversation_context or {}
            )
            
            # Extract the basic response for display
            if result['saori_response']:
                response = {
                    'reply': result['saori_response'].reply,
                    'glyph': result['saori_response'].glyph,
                    'parsed_glyphs': result['saori_response'].parsed_glyphs,
                    'evolution_info': {
                        'evolution_triggered': result['evolution_triggered'],
                        'new_glyphs_count': len(result['new_glyphs_generated']),
                        'new_glyphs': result['new_glyphs_generated']
                    }
                }
            else:
                response = {'reply': 'Connection error', 'evolution_info': {'evolution_triggered': False}}
                
        else:
            # Fall back to basic API call
            try:
                payload = {"message": message}
                if conversation_context:
                    payload.update(conversation_context)
                
                response_raw = requests.post(
                    self.basic_function_url, 
                    headers=self.basic_headers, 
                    json=payload,
                    timeout=30
                )
                response_raw.raise_for_status()
                response = response_raw.json()
                response['evolution_info'] = {'evolution_triggered': False}
                
            except Exception as e:
                response = {
                    'reply': f'Error: {e}',
                    'evolution_info': {'evolution_triggered': False}
                }
        
        return response
    
    def get_evolution_stats(self) -> Dict:
        """Get statistics about glyph evolution"""
        if self.evolution_enabled and self.integrator:
            return self.integrator.get_evolution_stats()
        return {'evolution_enabled': False}

def interactive_demo():
    """Interactive demo with evolving glyphs"""
    
    print("Enhanced Saoriverse Console with Auto-Evolving Glyphs")
    print("=" * 60)
    print()
    
    # Configuration (replace with your actual values)
    SUPABASE_FUNCTION_URL = "https://your-project.supabase.co/functions/v1/saori-fixed"
    SUPABASE_ANON_KEY = "your-anon-key-here"
    SUPABASE_URL = "https://your-project.supabase.co"
    
    # Initialize enhanced saoriverse
    saori = EnhancedSaoriverse(
        supabase_function_url=SUPABASE_FUNCTION_URL,
        supabase_anon_key=SUPABASE_ANON_KEY,
        supabase_url=SUPABASE_URL,
        enable_evolution=True
    )
    
    print("Type 'quit' to exit, 'stats' to see evolution statistics")
    print("Try expressing complex emotions to trigger glyph evolution!")
    print("-" * 60)
    
    conversation_count = 0
    
    while True:
        try:
            user_input = input("\\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'stats':
                stats = saori.get_evolution_stats()
                print("\\n📊 Evolution Statistics:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
                continue
            elif not user_input:
                continue
            
            conversation_count += 1
            
            # Process the message
            print("\\nSaori: ", end="", flush=True)
            
            result = saori.chat(
                message=user_input,
                conversation_context={
                    'conversation_id': conversation_count,
                    'timestamp': time.time()
                }
            )
            
            # Display the response
            print(result.get('reply', 'No response'))
            
            # Show evolution info if available
            evolution_info = result.get('evolution_info', {})
            if evolution_info.get('evolution_triggered'):
                print("\\n🧬 Evolution Check Triggered!")
                new_glyphs_count = evolution_info.get('new_glyphs_count', 0)
                if new_glyphs_count > 0:
                    print(f"✨ Generated {new_glyphs_count} new glyphs:")
                    for glyph in evolution_info.get('new_glyphs', []):
                        print(f"   • {glyph['tag_name']} ({glyph['glyph']})")
                else:
                    print("   No new glyphs needed - existing patterns cover this")
            
            # Show parsed glyphs if available
            if 'parsed_glyphs' in result and result['parsed_glyphs']:
                print(f"\\n🔮 Activated Glyphs: {', '.join([g.get('glyph_name', 'Unknown') for g in result['parsed_glyphs']])}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\\nError: {e}")
    
    print("\\n🎉 Thanks for exploring the evolving Saoriverse!")
    
    # Final stats
    final_stats = saori.get_evolution_stats()
    if final_stats.get('evolution_enabled'):
        print("\\n📊 Final Evolution Statistics:")
        for key, value in final_stats.items():
            print(f"   {key}: {value}")

def batch_evolution_test():
    """Test batch processing of conversations to see evolution in action"""
    
    print("🧪 Batch Evolution Test")
    print("=" * 30)
    
    # Sample conversations designed to trigger evolution
    test_conversations = [
        "I'm feeling this profound mixture of joy and sorrow, like watching a sunset that breaks your heart with beauty.",
        "There's this sacred ache when I think about deep connection - not painful, but a gentle yearning that flows like water.",
        "I experience this intense clarity mixed with overwhelming confusion, like seeing truth through a fractured lens.",
        "Sometimes I feel this contained wildness - like having a storm inside a sacred vessel, powerful but held.",
        "I'm touched by this quiet celebration mixed with deep reverence, like joy that doesn't need to perform.",
        "This flowing stillness moves through me - not static, but dynamically peaceful, like a deep silent river.",
        "I feel this expansive vulnerability - not weakness, but strength that opens like a flower toward sunlight."
    ]
    
    # Configuration (replace with your actual values)
    SUPABASE_FUNCTION_URL = "https://your-project.supabase.co/functions/v1/saori-fixed"
    SUPABASE_ANON_KEY = "your-anon-key-here"
    SUPABASE_URL = "https://your-project.supabase.co"
    
    saori = EnhancedSaoriverse(
        supabase_function_url=SUPABASE_FUNCTION_URL,
        supabase_anon_key=SUPABASE_ANON_KEY,
        supabase_url=SUPABASE_URL,
        enable_evolution=True
    )
    
    total_new_glyphs = 0
    
    for i, conversation in enumerate(test_conversations, 1):
        print(f"\\n--- Processing Conversation {i} ---")
        print(f"Input: {conversation}")
        
        result = saori.chat(
            message=conversation,
            conversation_context={'test_id': i}
        )
        
        print(f"Response: {result.get('reply', 'No response')[:100]}...")
        
        evolution_info = result.get('evolution_info', {})
        if evolution_info.get('evolution_triggered'):
            new_count = evolution_info.get('new_glyphs_count', 0)
            total_new_glyphs += new_count
            print(f"🧬 Evolution: Generated {new_count} new glyphs")
        else:
            print("🧬 Evolution: Not triggered")
    
    print(f"\\n🎉 Batch test complete!")
    print(f"   Total new glyphs generated: {total_new_glyphs}")
    
    final_stats = saori.get_evolution_stats()
    if final_stats.get('evolution_enabled'):
        print("\\n📊 Final Statistics:")
        for key, value in final_stats.items():
            print(f"   {key}: {value}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        batch_evolution_test()
    else:
        interactive_demo()
'''

    # Write the enhanced demo to a file
    with open("enhanced_conversation_demo.py", "w") as f:
        f.write(enhanced_demo_code)

    print("Created enhanced_conversation_demo.py")
    print("This shows how to integrate the evolving glyph system with your existing conversation flow.")


def create_quick_setup_guide():
    """Create a quick setup guide"""

    setup_guide = """# Quick Setup Guide: Auto-Evolving Glyphs

## 🚀 Getting Started

### 1. Install Dependencies
pip install requests  # If not already installed

### 2. Configure Your Credentials
1. Copy `config_template.py` to `config.py`
2. Fill in your Supabase credentials:
   - SUPABASE_URL
   - SUPABASE_ANON_KEY  
   - SUPABASE_FUNCTION_URL

### 3. Test the System
# Test glyph generation (offline)
python test_evolving_glyphs.py

# Test with your Supabase setup
python enhanced_conversation_demo.py

# Run batch evolution test
python enhanced_conversation_demo.py batch

### 4. Integration Options

#### Option A: Replace your existing conversation flow
Replace your `conversation_demo.py` with `enhanced_conversation_demo.py`

#### Option B: Add to existing code
from evolving_glyph_integrator import EvolvingGlyphIntegrator

integrator = EvolvingGlyphIntegrator(
    supabase_function_url="your-url",
    supabase_anon_key="your-key",
    enable_auto_evolution=True
)

result = integrator.process_conversation_with_evolution(message="user input")

#### Option C: Use as background service
The system can run alongside your existing setup, monitoring conversations and automatically adding new glyphs to your database.

## 🧬 How It Works

1. **Pattern Detection**: System analyzes conversations for complex emotional patterns
2. **Glyph Generation**: Creates new glyphs when patterns meet frequency/novelty thresholds  
3. **Auto-Insertion**: New glyphs are automatically added to your emotional_tags table
4. **Immediate Availability**: Generated glyphs are instantly available for future conversations

## ⚙️ Configuration

- `EVOLUTION_FREQUENCY`: How often to check for new patterns (default: every 5 conversations)
- `MIN_PATTERN_FREQUENCY`: Pattern must appear N times before generating glyph (default: 3)
- `NOVELTY_THRESHOLD`: How unique a pattern must be (0.0-1.0, default: 0.7)

## 📊 Monitoring

- Use `get_evolution_stats()` to see system performance
- Check `generated/new_glyphs.sql` for backup of created glyphs
- Monitor `glyph_generation.log` for detailed activity

## 🎯 Benefits

- **Automatic Evolution**: System becomes more nuanced without manual intervention
- **Human-like Growth**: Captures subtle emotional patterns like humans do
- **Zero Maintenance**: Runs invisibly alongside your existing system
- **Instant Integration**: New glyphs immediately available to Saori

## 🔧 Troubleshooting

- Check logs in `glyph_generation.log` for detailed error information
- Verify Supabase credentials and permissions
- Test with `test_evolving_glyphs.py` to debug pattern detection
- Start with higher evolution frequency for testing, then reduce for production

Your emotional OS will now continuously evolve and become more sophisticated! 🎉
"""

    with open("SETUP_EVOLVING_GLYPHS.md", "w") as f:
        f.write(setup_guide)

    print("Created SETUP_EVOLVING_GLYPHS.md - your quick setup guide!")


if __name__ == "__main__":
    print("🔧 Creating integration examples and setup guides...")

    create_enhanced_conversation_demo()
    create_quick_setup_guide()

    print("\n✅ Integration files created:")
    print("   - enhanced_conversation_demo.py  (replaces your existing demo) (local demo; archived in repo)")
    print("   - SETUP_EVOLVING_GLYPHS.md (setup guide)")
    print("   - config_template.py (configuration template)")

    print("\n🌟 Your auto-evolving glyph system is ready!")
    print("   Follow the setup guide to integrate with your Saoriverse system.")
