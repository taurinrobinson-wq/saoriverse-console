import streamlit as st
from parser.signal_parser import parse_input
from learning.lexicon_learner import learn_from_conversation_data, get_learning_insights
from supabase_integration import create_hybrid_processor
import datetime
import json
import os
import re
from typing import Dict, List

# Import the auto-evolving glyph system
try:
    from evolving_glyph_integrator import EvolvingGlyphIntegrator
    EVOLUTION_AVAILABLE = True
except ImportError:
    EVOLUTION_AVAILABLE = False
    st.warning("Auto-evolving glyph system not available - check configuration")

st.set_page_config(page_title="Emotional OS", layout="wide", initial_sidebar_state="expanded")

# Load configuration
def load_config():
    """Load configuration from environment variables or .env file"""
    config = {}
    
    # Try to load from .env file
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Get Supabase configuration
    config['supabase'] = {
        'function_url': os.getenv('SUPABASE_FUNCTION_URL'),
        'anon_key': os.getenv('SUPABASE_ANON_KEY'),
        'user_token': os.getenv('SUPABASE_USER_TOKEN')
    }
    
    # Processing preferences
    config['processing'] = {
        'mode': os.getenv('DEFAULT_PROCESSING_MODE', 'hybrid'),
        'privacy_mode': os.getenv('PRIVACY_MODE', 'false').lower() == 'true',
        'prefer_ai': os.getenv('PREFER_AI', 'true').lower() == 'true',
        'use_local_fallback': os.getenv('USE_LOCAL_FALLBACK', 'true').lower() == 'true'
    }
    
    return config

# Initialize session state
if 'conversations' not in st.session_state:
    st.session_state.conversations = {}
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None
if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False

# Debug configuration (only show in debug mode)
config = load_config()
if config.get('ui', {}).get('debug_mode', False):
    with st.expander("🔧 Debug Info"):
        st.write("**Configuration Status:**")
        st.write(f"- Supabase URL: {'✅' if config['supabase']['url'] else '❌'}")
        st.write(f"- Supabase Key: {'✅' if config['supabase']['anon_key'] else '❌'}")
        st.write(f"- Function URL: {'✅' if config['supabase']['function_url'] else '❌'}")
        st.write(f"- Processing Mode: {config['processing']['mode']}")
        if config['supabase']['function_url']:
            st.code(config['supabase']['function_url'])
if 'learned_patterns' not in st.session_state:
    st.session_state.learned_patterns = {}

# Initialize configuration and hybrid processor
if 'config' not in st.session_state:
    st.session_state.config = load_config()

if 'hybrid_processor' not in st.session_state:
    try:
        st.session_state.hybrid_processor = create_hybrid_processor(
            supabase_config=st.session_state.config['supabase'],
            use_local_fallback=st.session_state.config['processing']['use_local_fallback']
        )
        st.session_state.processor_available = True
    except Exception as e:
        st.sidebar.error(f"Hybrid processor initialization failed: {e}")
        st.session_state.hybrid_processor = None
        st.session_state.processor_available = False

# Initialize auto-evolving glyph integrator
if 'evolving_integrator' not in st.session_state and EVOLUTION_AVAILABLE:
    try:
        config = st.session_state.config
        supabase_url = None
        
        # Extract Supabase URL from function URL if not directly available
        function_url = config['supabase']['function_url']
        if function_url:
            # Extract base URL from function URL (e.g., https://abc.supabase.co/functions/v1/... -> https://abc.supabase.co)
            import re
            match = re.match(r'(https://[^/]+\.supabase\.co)', function_url)
            supabase_url = match.group(1) if match else None
            
        st.session_state.evolving_integrator = EvolvingGlyphIntegrator(
            supabase_function_url=config['supabase']['function_url'],
            supabase_anon_key=config['supabase']['anon_key'],
            supabase_url=supabase_url,
            enable_auto_evolution=True,
            evolution_frequency=5  # Check for evolution every 5 conversations
        )
        st.session_state.evolution_enabled = True
    except Exception as e:
        config = st.session_state.config
        supabase_url = None
        function_url = config['supabase']['function_url']
        if function_url:
            import re
            match = re.match(r'(https://[^/]+\.supabase\.co)', function_url)
            supabase_url = match.group(1) if match else None
            
        st.sidebar.error(f"Auto-evolving glyph system failed to initialize: {str(e)}")
        st.sidebar.info(f"Debug: Function URL available: {'Yes' if config['supabase']['function_url'] else 'No'}")
        st.sidebar.info(f"Debug: Anon key available: {'Yes' if config['supabase']['anon_key'] else 'No'}")
        st.sidebar.info(f"Debug: Supabase URL extracted: {'Yes' if supabase_url else 'No'}")
        st.session_state.evolving_integrator = None
        st.session_state.evolution_enabled = False
else:
    st.session_state.evolution_enabled = False

# Custom CSS for chat-like interface
st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .conversation-container {
        max-height: 60vh;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        background-color: #fafafa;
        margin-bottom: 1rem;
    }
    .message-bubble {
        margin: 0.5rem 0;
        padding: 0.75rem 1rem;
        border-radius: 18px;
        max-width: 80%;
        word-wrap: break-word;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    .system-message {
        background-color: #e9ecef;
        color: #333;
        margin-right: auto;
    }
    .timestamp {
        font-size: 0.75em;
        opacity: 0.7;
        margin-top: 0.25rem;
    }
    .send-button-container {
        display: flex;
        justify-content: flex-end;
        margin-top: 0.5rem;
    }
    .conversation-list-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        cursor: pointer;
        border: 1px solid #ddd;
    }
    .conversation-list-item:hover {
        background-color: #f0f0f0;
    }
    .active-conversation {
        background-color: #e3f2fd;
        border-color: #2196f3;
    }
    </style>
""", unsafe_allow_html=True)

def generate_conversation_name(first_message: str) -> str:
    """Generate a conversation name based on the first message content"""
    # Extract key emotional words for naming
    emotional_keywords = [
        'grief', 'joy', 'love', 'fear', 'anger', 'sadness', 'happiness',
        'anxiety', 'peace', 'longing', 'hope', 'despair', 'excitement',
        'worry', 'calm', 'stress', 'content', 'frustrated', 'grateful',
        'lonely', 'connected', 'overwhelmed', 'clarity', 'confusion'
    ]
    
    words = first_message.lower().split()
    found_emotions = [word for word in words if any(emo in word for emo in emotional_keywords)]
    
    if found_emotions:
        primary_emotion = found_emotions[0].capitalize()
        return f"Exploring {primary_emotion}"
    else:
        # Fallback: use first few words
        clean_words = [word.strip('.,!?') for word in words[:3]]
        return " ".join(clean_words).title()[:30] + "..."

def get_current_conversation() -> Dict:
    """Get the current conversation data for context"""
    if not hasattr(st.session_state, 'current_conversation_id') or not st.session_state.current_conversation_id:
        return {'messages': []}
    
    conv_id = st.session_state.current_conversation_id
    if conv_id not in st.session_state.conversations:
        return {'messages': []}
        
    current_conv = st.session_state.conversations[conv_id]
    return {
        'messages': current_conv.get('messages', []),
        'conversation_id': conv_id
    }

def analyze_for_learning(user_input: str, system_response: str) -> Dict:
    """Analyze conversation for new patterns to add to lexicon"""
    # This is where you'd implement your medium language model learning
    # For now, let's do simple pattern recognition
    
    patterns = {
        'new_emotional_phrases': [],
        'response_patterns': [],
        'signal_candidates': []
    }
    
    # Look for repeated emotional phrases in user input
    emotional_indicators = ['feel', 'feeling', 'emotion', 'sense', 'experience']
    words = user_input.lower().split()
    
    for i, word in enumerate(words):
        if word in emotional_indicators and i < len(words) - 1:
            # Capture the phrase after emotional indicators
            following_phrase = ' '.join(words[i+1:i+3])
            patterns['new_emotional_phrases'].append(following_phrase)
    
    # Look for effective response patterns
    if len(system_response.split()) > 5:  # Substantial response
        patterns['response_patterns'].append({
            'trigger_context': user_input[:50],
            'effective_response': system_response[:100]
        })
    
    return patterns

def save_conversation(conversation_id: str, conversation_data: Dict):
    """Save conversation to persistent storage"""
    conversations_dir = "conversations"
    if not os.path.exists(conversations_dir):
        os.makedirs(conversations_dir)
    
    filepath = os.path.join(conversations_dir, f"{conversation_id}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, ensure_ascii=False, indent=2, default=str)

def load_conversations() -> Dict:
    """Load saved conversations"""
    conversations = {}
    conversations_dir = "conversations"
    if os.path.exists(conversations_dir):
        for filename in os.listdir(conversations_dir):
            if filename.endswith('.json'):
                conversation_id = filename[:-5]  # Remove .json extension
                try:
                    with open(os.path.join(conversations_dir, filename), 'r', encoding='utf-8') as f:
                        conversations[conversation_id] = json.load(f)
                except Exception as e:
                    st.sidebar.error(f"Error loading {filename}: {e}")
    return conversations

# Sidebar for conversation management
with st.sidebar:
    st.title("💭 Conversations")
    
    # Evolution Status
    if st.session_state.evolution_enabled:
        st.success("🧬 Auto-Evolving Glyphs: **Active**")
        if st.session_state.evolving_integrator:
            stats = st.session_state.evolving_integrator.get_evolution_stats()
            st.caption(f"Conversations processed: {stats.get('conversations_processed', 0)}")
            st.caption(f"Next evolution check in: {stats.get('next_evolution_check', 'N/A')} conversations")
    else:
        st.info("🧬 Auto-Evolving Glyphs: **Disabled**")
    
    # Processing Settings
    st.markdown("### ⚙️ Processing Settings")
    
    # Processing mode selection
    processing_mode = st.selectbox(
        "Processing Mode",
        ["hybrid", "supabase", "local"],
        index=["hybrid", "supabase", "local"].index(st.session_state.config['processing']['mode']),
        help="Hybrid: Try AI first, fallback to local. Supabase: AI-enhanced only. Local: Privacy-first local only."
    )
    
    # Privacy mode toggle
    privacy_mode = st.checkbox(
        "Privacy Mode", 
        value=st.session_state.config['processing']['privacy_mode'],
        help="Only use local processing - no external API calls"
    )
    
    # AI preference (only show if not in privacy mode)
    if not privacy_mode:
        prefer_ai = st.checkbox(
            "Prefer AI Enhancement", 
            value=st.session_state.config['processing']['prefer_ai'],
            help="Try AI-enhanced processing first in hybrid mode"
        )
    else:
        prefer_ai = False
    
    # Update config if settings changed
    if (processing_mode != st.session_state.config['processing']['mode'] or 
        privacy_mode != st.session_state.config['processing']['privacy_mode'] or
        prefer_ai != st.session_state.config['processing']['prefer_ai']):
        
        st.session_state.config['processing']['mode'] = processing_mode
        st.session_state.config['processing']['privacy_mode'] = privacy_mode
        st.session_state.config['processing']['prefer_ai'] = prefer_ai
    
    # Show system status
    if st.session_state.processor_available:
        if st.session_state.config['supabase']['function_url']:
            st.success("🔗 Supabase Integration Available")
        else:
            st.warning("⚠️ Local Processing Only")
    else:
        st.error("❌ Processing System Error")
    
    st.markdown("---")
    
    # Load existing conversations
    if st.button("🔄 Refresh Conversations"):
        st.session_state.conversations = load_conversations()
    
    # Display conversation list
    conversations = st.session_state.conversations
    if conversations:
        st.markdown("### Past Conversations")
        
        for conv_id, conv_data in conversations.items():
            conversation_name = conv_data.get('name', 'Untitled Conversation')
            message_count = len(conv_data.get('messages', []))
            
            # Create a clickable conversation item
            if st.button(
                f"{conversation_name}\n({message_count} messages)",
                key=f"conv_{conv_id}",
                use_container_width=True
            ):
                st.session_state.current_conversation_id = conv_id
                st.session_state.conversation_started = True
                st.rerun()
    
    st.markdown("---")
    
    # Learning insights
    st.markdown("### 🧠 Learning Insights")
    learning_stats = get_learning_insights()
    
    if learning_stats:
        st.metric("Base Vocabulary", learning_stats.get('base_lexicon_size', 0))
        st.metric("Learned Words", learning_stats.get('learned_lexicon_size', 0))
        
        top_words = learning_stats.get('top_learned_words', [])
        if top_words:
            st.markdown("**Recent Discoveries:**")
            for word, score in top_words[:3]:
                st.text(f"• {word} ({score:.2f})")
    
    if st.button("📊 Detailed Learning Stats"):
        st.json(learning_stats)

# Main chat interface
st.title("🕯 Emotional OS")

# Get current conversation
current_conv = None
if st.session_state.current_conversation_id:
    current_conv = st.session_state.conversations.get(st.session_state.current_conversation_id)

# Display conversation or start screen
if not st.session_state.conversation_started:
    # Welcome screen
    st.markdown("""
    ## Welcome to Emotional OS
    
    A space for exploring your inner landscape through conversation. 
    
    Share what you're feeling, and the system will reflect back what it hears,
    asking questions to help you go deeper.
    """)
    
    if st.button("🌟 Start New Conversation", type="primary", use_container_width=True):
        # Create new conversation
        new_conv_id = f"conv_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state.current_conversation_id = new_conv_id
        st.session_state.conversation_started = True
        st.session_state.conversations[new_conv_id] = {
            'id': new_conv_id,
            'name': 'New Conversation',
            'created_at': datetime.datetime.now().isoformat(),
            'messages': []
        }
        st.rerun()

else:
    # Active conversation interface
    if current_conv:
        # Display conversation history
        if current_conv['messages']:
            st.markdown('<div class="conversation-container">', unsafe_allow_html=True)
            
            for message in current_conv['messages']:
                timestamp = datetime.datetime.fromisoformat(message['timestamp']).strftime("%H:%M")
                
                if message['type'] == 'user':
                    st.markdown(f"""
                    <div class="message-bubble user-message">
                        {message['content']}
                        <div class="timestamp">{timestamp}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="message-bubble system-message">
                        {message['content']}
                        <div class="timestamp">{timestamp}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    with st.form(key="message_form", clear_on_submit=True):
        prompt_text = "What are you feeling right now?" if not current_conv or not current_conv['messages'] else "Continue sharing..."
        
        user_input = st.text_area(
            prompt_text,
            height=100,
            placeholder="Speak plainly. The system will reflect back what it hears...",
            key="message_input"
        )
        
        # Send button (right-aligned)
        col1, col2, col3 = st.columns([4, 1, 1])
        with col3:
            send_clicked = st.form_submit_button("Send 💫", type="primary")
    
    # Process message
    if send_clicked and user_input.strip():
        # Get current conversation for context
        current_conversation = get_current_conversation()
        
        # Add debugging to see what context we're passing
        print(f"DEBUG: Current conversation has {len(current_conversation.get('messages', []))} messages")
        print(f"DEBUG: Conversation ID: {current_conversation.get('conversation_id', 'None')}")
        print(f"DEBUG: Processing mode: {st.session_state.config['processing']['mode']}")
        
        # Process using evolving glyph system if available
        evolution_result = None
        if st.session_state.evolution_enabled and st.session_state.evolving_integrator:
            try:
                evolution_result = st.session_state.evolving_integrator.process_conversation_with_evolution(
                    message=user_input.strip(),
                    conversation_context=current_conversation
                )
                if evolution_result['saori_response']:
                    result = {
                        "response": evolution_result['saori_response'].reply,
                        "source": "evolving_glyph_system"
                    }
                    print(f"DEBUG: Used evolving glyph system")
                else:
                    raise Exception("No response from evolving system")
                    
            except Exception as e:
                print(f"DEBUG: Evolving glyph system failed: {e}")
                evolution_result = None
        
        # Fallback to hybrid system if evolving system not available
        if not evolution_result or not evolution_result.get('saori_response'):
            if st.session_state.processor_available and st.session_state.hybrid_processor:
                try:
                    processing_config = st.session_state.config['processing']
                    result = st.session_state.hybrid_processor.process_emotional_input(
                        message=user_input.strip(),
                        conversation_context=current_conversation,
                        prefer_ai=processing_config['prefer_ai'],
                        privacy_mode=processing_config['privacy_mode']
                    )
                    
                    print(f"DEBUG: Processing source: {result.get('source', 'unknown')}")
                    print(f"DEBUG: Processing method: {result.get('processing_method', 'unknown')}")
                    
                except Exception as e:
                    print(f"DEBUG: Hybrid processing failed: {e}")
                    # Fallback to local processing
                    result = parse_input(
                        user_input.strip(), 
                        "parser/signal_lexicon.json",
                        conversation_context=current_conversation
                    )
                    result = {"response": result.get("voltage_response", "Processing error"), "source": "local_fallback"}
            else:
                # Fallback to original local processing
                result = parse_input(
                    user_input.strip(), 
                    "parser/signal_lexicon.json",
                    conversation_context=current_conversation
                )
                result = {"response": result.get("voltage_response", "Processing error"), "source": "local_only"}
        
        # Add user message
        user_message = {
            'type': 'user',
            'content': user_input.strip(),
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Add system response
        response_text = result.get("response", "No response generated")
        system_message = {
            'type': 'system',
            'content': response_text,
            'timestamp': datetime.datetime.now().isoformat(),
            'metadata': {
                'source': result.get('source', 'unknown'),
                'processing_method': result.get('processing_method', 'unknown'),
                'signals': result.get('signals', []),
                'glyphs': result.get('glyphs', []),
                'glyph_data': result.get('glyph_data'),
                'parsed_glyphs': result.get('parsed_glyphs', []),
                'privacy_preserved': result.get('privacy_preserved', True)
            }
        }
        
        # Debug output to see what response we got
        print(f"UI DEBUG: Response received: {response_text[:100]}...")
        print(f"UI DEBUG: Response source: {result.get('source', 'unknown')}")
        
        # Add evolution information if available
        if evolution_result and evolution_result.get('evolution_triggered'):
            evolution_info = {
                'type': 'evolution',
                'timestamp': datetime.datetime.now().isoformat(),
                'new_glyphs_count': len(evolution_result.get('new_glyphs_generated', [])),
                'new_glyphs': evolution_result.get('new_glyphs_generated', [])
            }
            
            if evolution_info['new_glyphs_count'] > 0:
                evolution_message = f"🧬 **Evolution Triggered!** Generated {evolution_info['new_glyphs_count']} new glyph(s):\n"
                for glyph in evolution_info['new_glyphs']:
                    evolution_message += f"• **{glyph.get('tag_name', 'Unknown')}** ({glyph.get('glyph', 'N/A')})\n"
                
                evolution_system_message = {
                    'type': 'system',
                    'content': evolution_message,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'metadata': {'source': 'evolution_system', 'is_evolution': True}
                }
                system_message = evolution_system_message  # Replace the normal system message
            else:
                # Just add a small note that evolution was checked
                st.success("🧬 Evolution check completed - patterns analyzed")
        
        # Update conversation
        if not current_conv:
            current_conv = st.session_state.conversations[st.session_state.current_conversation_id]
        
        current_conv['messages'].extend([user_message, system_message])
        
        # Generate conversation name if first message
        if len(current_conv['messages']) == 2:  # First exchange
            current_conv['name'] = generate_conversation_name(user_input.strip())
        
        # Learn from this exchange using the enhanced learning system
        learning_results = learn_from_conversation_data(current_conv)
        st.session_state.learned_patterns[st.session_state.current_conversation_id] = learning_results
        
        # Save conversation
        save_conversation(st.session_state.current_conversation_id, current_conv)
        
        st.rerun()

    # Conversation actions
    if current_conv and current_conv['messages']:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🆕 New Conversation"):
                st.session_state.conversation_started = False
                st.session_state.current_conversation_id = None
                st.rerun()
        
        with col2:
            # Rename conversation
            new_name = st.text_input("Rename conversation:", value=current_conv.get('name', ''))
            if st.button("✏️ Rename") and new_name:
                current_conv['name'] = new_name
                save_conversation(st.session_state.current_conversation_id, current_conv)
                st.success("Conversation renamed!")
                st.rerun()
        
        with col3:
            if st.button("🗑️ Delete Conversation"):
                # Delete conversation file
                conv_file = f"conversations/{st.session_state.current_conversation_id}.json"
                if os.path.exists(conv_file):
                    os.remove(conv_file)
                
                # Remove from session state
                if st.session_state.current_conversation_id in st.session_state.conversations:
                    del st.session_state.conversations[st.session_state.current_conversation_id]
                
                st.session_state.conversation_started = False
                st.session_state.current_conversation_id = None
                st.success("Conversation deleted!")
                st.rerun()

# Help text
if st.session_state.conversation_started:
    st.markdown("---")
    st.markdown("*💡 Press Ctrl+Enter for new lines. Press Enter to send your message.*")