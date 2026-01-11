"""
Velinor Phase 2 Test Interface - Trait System + Marketplace Debate
===================================================================

Streamlit interface demonstrating:
- Trait system tracking
- Coherence calculation
- Marketplace debate scene branching
- NPC personality responses
- Trait-based dialogue variations
"""

import streamlit as st
from pathlib import Path
import sys
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "velinor" / "engine"))

from trait_system import TraitProfiler, TraitType, TraitChoice
from coherence_calculator import CoherenceCalculator
from npc_response_engine import NPCResponseEngine
from marketplace_scene import create_marketplace_debate_scene

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Velinor Phase 2: Trait System & Marketplace Debate",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for trait visualization
st.markdown("""
<style>
    .trait-meter {
        display: flex;
        align-items: center;
        margin: 10px 0;
        gap: 10px;
    }
    
    .trait-bar {
        flex-grow: 1;
        height: 24px;
        background: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .trait-fill {
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
    }
    
    .empathy-fill { background: #ec4899; }
    .skepticism-fill { background: #3b82f6; }
    .integration-fill { background: #8b5cf6; }
    .awareness-fill { background: #f59e0b; }
    
    .coherence-status {
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-weight: bold;
    }
    
    .coherence-crystal { background: #c7d2fe; color: #312e81; }
    .coherence-clear { background: #a5e6ba; color: #065f46; }
    .coherence-mixed { background: #fcd34d; color: #92400e; }
    .coherence-confused { background: #f8a291; color: #7c2d12; }
    .coherence-contradictory { background: #f87171; color: #7f1d1d; }
    
    .dialogue-option-button {
        background: linear-gradient(135deg, #ede9fe 0%, #f5f3ff 100%);
        border: 2px solid #c4b5fd;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        cursor: pointer;
        text-align: left;
    }
    
    .dialogue-option-button:hover {
        background: linear-gradient(135deg, #ddd6fe 0%, #ede9fe 100%);
        border-color: #a78bfa;
    }
    
    .npc-response {
        background: linear-gradient(135deg, #f0fdf4 0%, #f0f9ff 100%);
        border-left: 4px solid #10b981;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        font-style: italic;
    }
    
    .trait-tagged {
        display: inline-block;
        background: #f3e8ff;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        margin-left: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session():
    """Initialize session state"""
    if 'trait_profiler' not in st.session_state:
        st.session_state.trait_profiler = TraitProfiler("Player")
        st.session_state.coherence_calculator = CoherenceCalculator(st.session_state.trait_profiler)
        st.session_state.npc_response_engine = NPCResponseEngine(st.session_state.trait_profiler)
        st.session_state.marketplace_scene = create_marketplace_debate_scene()
        
        st.session_state.scene_phase = "welcome"
        st.session_state.choices_log = []
        st.session_state.current_entry_choice = None
        st.session_state.show_branching = False

init_session()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def record_trait_choice(choice_id: str, choice_text: str, trait: TraitType, 
                        weight: float = 0.3, secondary: Optional[TraitType] = None,
                        secondary_weight: float = 0.0, npc_name: str = "") -> None:
    """Record a trait choice and update profile"""
    trait_choice = TraitChoice(
        choice_id=choice_id,
        dialogue_option=choice_text,
        primary_trait=trait,
        trait_weight=weight,
        secondary_trait=secondary,
        secondary_weight=secondary_weight,
        npc_name=npc_name,
        scene_name="marketplace_debate",
    )
    
    st.session_state.trait_profiler.record_choice(trait_choice)
    st.session_state.coherence_calculator = CoherenceCalculator(st.session_state.trait_profiler)
    st.session_state.npc_response_engine = NPCResponseEngine(st.session_state.trait_profiler)
    
    st.session_state.choices_log.append({
        'choice_id': choice_id,
        'text': choice_text,
        'trait': trait.value,
        'npc': npc_name,
    })

def render_trait_meters() -> None:
    """Render trait meter visualization"""
    profile = st.session_state.trait_profiler.get_trait_summary()
    traits = profile['trait_scores']
    
    st.markdown("### 🧭 Trait Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Empathy meter
        emp_pct = int(traits['empathy'])
        st.markdown(f"""
        <div class='trait-meter'>
            <div class='trait-bar'>
                <div class='trait-fill empathy-fill' style='width: {emp_pct}%'>
                    {emp_pct}%
                </div>
            </div>
            <span>Empathy</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Integration meter
        int_pct = int(traits['integration'])
        st.markdown(f"""
        <div class='trait-meter'>
            <div class='trait-bar'>
                <div class='trait-fill integration-fill' style='width: {int_pct}%'>
                    {int_pct}%
                </div>
            </div>
            <span>Integration</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Skepticism meter
        skep_pct = int(traits['skepticism'])
        st.markdown(f"""
        <div class='trait-meter'>
            <div class='trait-bar'>
                <div class='trait-fill skepticism-fill' style='width: {skep_pct}%'>
                    {skep_pct}%
                </div>
            </div>
            <span>Skepticism</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Awareness meter
        awa_pct = int(traits['awareness'])
        st.markdown(f"""
        <div class='trait-meter'>
            <div class='trait-bar'>
                <div class='trait-fill awareness-fill' style='width: {awa_pct}%'>
                    {awa_pct}%
                </div>
            </div>
            <span>Awareness</span>
        </div>
        """, unsafe_allow_html=True)

def render_coherence_status() -> None:
    """Render coherence information"""
    report = st.session_state.coherence_calculator.get_coherence_report()
    coherence = report.overall_coherence
    level = report.level.name
    
    level_class = {
        'CRYSTAL_CLEAR': 'coherence-crystal',
        'CLEAR': 'coherence-clear',
        'MIXED': 'coherence-mixed',
        'CONFUSED': 'coherence-confused',
        'CONTRADICTORY': 'coherence-contradictory',
    }.get(level, 'coherence-mixed')
    
    st.markdown(f"""
    <div class='coherence-status {level_class}'>
        Coherence: {int(coherence)}/100 ({level})
        <br>
        <small>{report.summary()}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Additional details
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("NPC Trust", report.npc_trust_level.title())
    with col2:
        st.metric("Dialogue Depth", report.dialogue_depth.title())
    with col3:
        st.metric("Contradictions", report.contradiction_count)

def render_sidebar_info() -> None:
    """Render information sidebar"""
    st.sidebar.markdown("### 📊 Player Status")
    profile = st.session_state.trait_profiler.get_trait_summary()
    st.sidebar.metric("Choices Made", profile['choices_made'])
    
    primary = profile['primary_trait']
    st.sidebar.info(f"**Primary Trait**: {primary.upper()}")
    
    if st.session_state.choices_log:
        st.sidebar.markdown("**Recent Choices:**")
        for log in st.session_state.choices_log[-5:]:
            trait_tag = f"<span class='trait-tagged'>{log['trait']}</span>"
            st.sidebar.markdown(
                f"- {log['text']}\n{trait_tag}",
                unsafe_allow_html=True
            )

# ============================================================================
# SCENE RENDERING
# ============================================================================

def render_welcome() -> None:
    """Render welcome screen"""
    st.markdown("""
    <div style='text-align: center; padding: 40px;'>
        <h1>🧠 Velinor: Phase 2</h1>
        <h2>Trait System & Marketplace Debate</h2>
        <p style='font-size: 18px; color: #666;'>
            Your choices shape who you are.<br>
            The world responds to consistency.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ## 🎭 The Marketplace Debate
    
    A conflict is unfolding in the marketplace square. Three factions,
    three perspectives, one contested space.
    
    **What you'll experience:**
    - Meet Malrik (Skeptical), Elenya (Empathetic), and Coren (Integrator)
    - Choose your approach to their conflict
    - Watch the world respond to your trait pattern
    - See how coherence affects dialogue depth
    
    ### Key Concepts
    
    **Traits**: Empathy, Skepticism, Integration, Awareness  
    **Coherence**: Consistency between declared traits and behavior  
    **NPC Trust**: How much NPCs reveal depends on your coherence  
    **Dialogue Depth**: Coherent players unlock deeper conversations  
    
    ---
    """)
    
    if st.button("🚀 Begin the Marketplace Debate", use_container_width=True):
        st.session_state.scene_phase = "intro"
        st.rerun()

def render_intro_phase() -> None:
    """Render scene introduction and entry choices"""
    st.markdown("## 🎭 The Marketplace Square")
    
    # Show intro narration
    scene = st.session_state.marketplace_scene
    st.markdown(scene['intro_narration'])
    
    st.markdown("---")
    st.markdown("### How do you approach?")
    
    # Get entry choices
    intro_choices = scene['intro_choices']
    
    for choice in intro_choices:
        if st.button(
            choice['text'],
            key=choice['choice_id'],
            use_container_width=True
        ):
            # Record trait if applicable
            if choice.get('trait_choice'):
                record_trait_choice(
                    choice_id=choice['choice_id'],
                    choice_text=choice['text'],
                    trait=choice['trait_choice'],
                    weight=choice.get('trait_weight', 0.2),
                )
            
            st.session_state.current_entry_choice = choice
            st.session_state.scene_phase = "setup"
            st.rerun()

def render_setup_phase() -> None:
    """Render debate setup narration"""
    st.markdown("## 🗣️ The Debate Unfolds")
    
    scene = st.session_state.marketplace_scene
    st.markdown(scene['setup_narration'])
    
    # Show what NPCs think of player so far
    report = st.session_state.coherence_calculator.get_coherence_report()
    
    st.markdown("---")
    st.markdown("### NPC Perceptions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        malrik_conflict = st.session_state.npc_response_engine.get_npc_conflict_level('Malrik')
        st.info(f"**Malrik** ({malrik_conflict})")
    
    with col2:
        elenya_conflict = st.session_state.npc_response_engine.get_npc_conflict_level('Elenya')
        st.info(f"**Elenya** ({elenya_conflict})")
    
    with col3:
        coren_conflict = st.session_state.npc_response_engine.get_npc_conflict_level('Coren')
        st.info(f"**Coren** ({coren_conflict})")
    
    st.markdown("---")
    
    if st.button("Continue to dialogue choices →", use_container_width=True):
        st.session_state.show_branching = True
        st.rerun()

def render_branching_phase() -> None:
    """Render main dialogue branching choices"""
    st.markdown("## 💭 What Do You Say?")
    
    # Get available choices based on coherence
    profiler = st.session_state.trait_profiler
    report = st.session_state.coherence_calculator.get_coherence_report()
    
    npc_conflicts = {
        'Malrik': st.session_state.npc_response_engine.get_npc_conflict_level('Malrik'),
        'Elenya': st.session_state.npc_response_engine.get_npc_conflict_level('Elenya'),
        'Coren': st.session_state.npc_response_engine.get_npc_conflict_level('Coren'),
    }
    
    scene = st.session_state.marketplace_scene
    choices = scene['get_branching_choices'](
        coherence_level=report.overall_coherence,
        player_primary_trait=report.primary_pattern,
        npc_conflicts=npc_conflicts
    )
    
    # Show coherence gating info
    st.info(f"**Coherence: {int(report.overall_coherence)}/100** - {report.coherence_status if hasattr(report, 'coherence_status') else report.level.name}")
    
    # Render choices
    for i, choice in enumerate(choices):
        locked = choice.get('coherence_locked', False) and report.overall_coherence < 60
        
        choice_text = choice['text']
        if locked:
            choice_text += " 🔒 (Requires coherence)"
        
        if st.button(
            choice_text,
            key=f"choice_{i}",
            use_container_width=True,
            disabled=locked
        ):
            # Record the trait choice
            record_trait_choice(
                choice_id=choice['choice_id'],
                choice_text=choice['text'],
                trait=choice['primary_trait'],
                weight=choice['trait_weight'],
                secondary=choice.get('secondary_trait'),
                secondary_weight=choice.get('secondary_weight', 0),
                npc_name=choice['npc_name'],
            )
            
            # Show response
            st.markdown("---")
            st.markdown("### 🎭 The Response")
            st.markdown(f"<div class='npc-response'>{choice['response']}</div>", unsafe_allow_html=True)
            
            # Show consequence
            st.markdown(f"**Consequence**: {choice['consequence']}")
            
            # Update coherence for display
            st.session_state.show_branching = False
            
            if st.button("See the Resolution →", use_container_width=True):
                st.session_state.scene_phase = "resolution"
                st.rerun()
            
            return

def render_resolution_phase() -> None:
    """Render scene resolution"""
    st.markdown("## 📖 The Resolution")
    
    # Get last choice made
    if st.session_state.choices_log:
        last_choice_id = st.session_state.choices_log[-1]['choice_id']
        
        scene = st.session_state.marketplace_scene
        choices = scene['intro_choices'] + [
            # Simplified - would need to reconstruct full choices
        ]
        
        # Find matching choice
        for choice in choices:
            if choice.get('choice_id') == last_choice_id:
                resolution = scene['get_resolution_narration'](choice)
                st.markdown(resolution)
                break
    
    st.markdown("---")
    st.markdown(scene['exit_narration'])
    
    st.markdown("---")
    st.success("✨ Marketplace Debate Complete")
    
    if st.button("🔄 Reset and Try Different Choices", use_container_width=True):
        st.session_state.trait_profiler = TraitProfiler("Player")
        st.session_state.coherence_calculator = CoherenceCalculator(st.session_state.trait_profiler)
        st.session_state.npc_response_engine = NPCResponseEngine(st.session_state.trait_profiler)
        st.session_state.scene_phase = "welcome"
        st.session_state.choices_log = []
        st.rerun()

# ============================================================================
# MAIN RENDERING
# ============================================================================

def main():
    """Main application"""
    
    # Render sidebar
    st.sidebar.markdown("# 📊 Trait Dashboard")
    render_sidebar_info()
    render_trait_meters()
    render_coherence_status()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📚 How Traits Work
    
    Your choices build trait patterns. NPCs notice patterns, not individual choices.
    
    - **Empathy**: Comfort with emotion
    - **Skepticism**: Critical questioning  
    - **Integration**: Holding multiple truths
    - **Awareness**: Noticing patterns
    
    **High Coherence** → NPCs reveal more  
    **Low Coherence** → NPCs stay guarded
    """)
    
    # Main content
    phase = st.session_state.scene_phase
    
    if phase == "welcome":
        render_welcome()
    elif phase == "intro":
        render_intro_phase()
    elif phase == "setup":
        render_setup_phase()
    elif phase == "branching" or st.session_state.show_branching:
        render_branching_phase()
    elif phase == "resolution":
        render_resolution_phase()

if __name__ == "__main__":
    main()
