import streamlit as st
from emotional_os.parser.signal_parser import parse_input

import datetime
import random

st.set_page_config(page_title="Emotional OS", layout="centered")

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'last_themes' not in st.session_state:
    st.session_state.last_themes = []
if 'conversation_depth' not in st.session_state:
    st.session_state.conversation_depth = 0

st.markdown("""
    <style>
    body {
        background-color: #f4f4f2;
        color: #2e2e2e;
    }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #ffffff;
        color: #2e2e2e;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    .conversation-bubble {
        background-color: #f9f9f7;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #d4af37;
    }
    .user-bubble {
        background-color: #e8f4f8;
        border-left: 4px solid #4a9eff;
    }
    .system-timestamp {
        font-size: 0.8em;
        color: #888;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

def get_conversational_prompt():
    """Generate contextual prompts based on conversation history and depth"""
    depth = st.session_state.conversation_depth
    
    if depth == 0:
        prompts = [
            "What are you feeling right now?",
            "What's moving through you today?", 
            "How is your inner landscape?",
            "What wants to be witnessed?"
        ]
    elif depth == 1:
        prompts = [
            "Tell me more about that feeling...",
            "What else is there?",
            "How does that sit with you?",
            "What's beneath that?"
        ]
    elif depth >= 2:
        prompts = [
            "Keep going... I'm listening",
            "What's the deeper layer here?",
            "How does this connect to what you shared before?",
            "What wants to unfold next?"
        ]
    
    return random.choice(prompts)

def get_follow_up_question(result):
    """Generate follow-up questions based on the parsed emotional content"""
    themes = []
    for glyph in result["glyphs"]:
        name = glyph["glyph_name"].lower()
        if any(k in name for k in ["grief", "mourning", "collapse"]):
            themes.append("grief")
        elif any(k in name for k in ["ache", "recursive", "spiral"]):
            themes.append("longing")
        elif any(k in name for k in ["joy", "delight", "recognition"]):
            themes.append("joy")
        elif any(k in name for k in ["boundary", "contain", "still"]):
            themes.append("protection")
    
    questions = {
        "grief": [
            "What are you grieving? Would you like to say more about what you've lost?",
            "How long have you been carrying this grief?",
            "What would it mean to let this grief be witnessed fully?"
        ],
        "longing": [
            "What is this ache pointing toward?",
            "What are you yearning for that feels just out of reach?", 
            "When did you first notice this recursive pattern?"
        ],
        "joy": [
            "What brought this joy forward?",
            "How does it feel to let yourself be seen in this happiness?",
            "What wants to be celebrated here?"
        ],
        "protection": [
            "What are you protecting by holding these boundaries?",
            "What would happen if you let your guard down right now?",
            "What does this containment serve?"
        ]
    }
    
    if themes:
        theme = themes[0]  # Take the first detected theme
        return random.choice(questions.get(theme, [
            "What else wants to be explored here?",
            "How does this feel in your body right now?",
            "What would it look like to go deeper with this feeling?"
        ]))
    
    return "What else is present for you right now?"

st.title("🕯 Emotional OS")

# Display conversation history
if st.session_state.conversation_history:
    st.markdown("### Our Conversation")
    
    for i, entry in enumerate(st.session_state.conversation_history[-3:]):  # Show last 3 exchanges
        timestamp = entry['timestamp'].strftime("%H:%M")
        
        # User input
        st.markdown(f"""
        <div class="conversation-bubble user-bubble">
            <div class="system-timestamp">You at {timestamp}</div>
            {entry['input']}
        </div>
        """, unsafe_allow_html=True)
        
        # System response
        st.markdown(f"""
        <div class="conversation-bubble">
            <div class="system-timestamp">System response</div>
            {entry['response']}
        </div>
        """, unsafe_allow_html=True)
    
    if len(st.session_state.conversation_history) > 3:
        if st.button("🔍 Show full conversation history"):
            for entry in st.session_state.conversation_history:
                timestamp = entry['timestamp'].strftime("%H:%M")
                st.markdown(f"**{timestamp} - You:** {entry['input']}")
                st.markdown(f"**System:** {entry['response']}")
                st.markdown("---")

# Get current prompt
current_prompt = get_conversational_prompt()

# Main input area with dynamic prompting
st.markdown("### " + ("Continue..." if st.session_state.conversation_depth > 0 else "Begin"))

input_text = st.text_area(
    current_prompt, 
    height=120,
    key="current_input",
    placeholder="Speak plainly. The system will reflect back what it hears..."
)

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    trace_button = st.button("✨ Trace", type="primary")

with col2:
    if st.session_state.conversation_history:
        if st.button("🔄 Continue Thread"):
            # This will just update the prompt
            st.session_state.conversation_depth += 1
            st.rerun()

with col3:
    if st.session_state.conversation_history:
        if st.button("🆕 Fresh Start"):
            st.session_state.conversation_history = []
            st.session_state.last_themes = []
            st.session_state.conversation_depth = 0
            st.rerun()

# Process input
if trace_button and input_text.strip():
    # Create conversation context for enhanced parsing
    conversation_context = {
        'depth': st.session_state.conversation_depth,
        'history': st.session_state.conversation_history
    }
    
    result = parse_input(input_text, "parser/signal_lexicon.json")
    
    # Add to conversation history
    st.session_state.conversation_history.append({
        'timestamp': datetime.datetime.now(),
        'input': input_text,
        'response': result["voltage_response"],
        'glyphs': result["glyphs"]
    })
    
    st.session_state.conversation_depth += 1
    
    # Display current response
    st.markdown("### 💬 Response")
    st.markdown(f"*{result['voltage_response']}*")
    
    # Generate and display follow-up question
    follow_up = get_follow_up_question(result)
    st.markdown(f"**{follow_up}**")
    
    # Expandable glyph details
    with st.expander(f"🔮 Activated Glyphs ({len(result['glyphs'])} found)"):
        if result["glyphs"]:
            for glyph in result["glyphs"]:
                st.markdown(f"**{glyph['glyph_name']}** — *{glyph['gate']}*  \n{glyph['description']}")
        else:
            st.markdown("*No specific glyphs activated - this might be a moment of quiet or transition.*")
    
    # Show detected signals for transparency
    with st.expander("⚡ Signal Analysis"):
        if result["signals"]:
            st.markdown("**Detected signals:** " + ", ".join(result["signals"]))
            st.markdown("**Activated gates:** " + ", ".join(result["gates"]))
        else:
            st.markdown("*No strong signals detected - sometimes the quieter moments matter too.*")

# Footer with helpful context
if not st.session_state.conversation_history:
    st.markdown("---")
    st.markdown("*Start by sharing what you're feeling. The system will listen, reflect, and ask questions to go deeper. Each exchange builds on the last.*")