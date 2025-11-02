import streamlit as st

from emotional_os.deploy.modules.auth import SaoynxAuthentication
from emotional_os.deploy.modules.ui import render_main_app, render_splash_interface

# Optional limbic integration (safe import)
try:
    from emotional_os.glyphs.limbic_integration import LimbicIntegrationEngine
    HAS_LIMBIC = True
except Exception:
    LimbicIntegrationEngine = None
    HAS_LIMBIC = False

# Page configuration
st.set_page_config(
    page_title="FirstPerson - Personal AI Companion",
    page_icon="graphics/FirstPerson-Logo.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Sidebar controls for integrations
    st.sidebar.markdown("## Integrations")
    enable_limbic = st.sidebar.checkbox("Enable Limbic-Adjacent Integration", value=st.session_state.get('enable_limbic', False))
    st.session_state['enable_limbic'] = enable_limbic

    # Initialize limbic engine if requested and available
    if enable_limbic and HAS_LIMBIC and 'limbic_engine' not in st.session_state:
        try:
            st.session_state['limbic_engine'] = LimbicIntegrationEngine()
            st.sidebar.success("Limbic engine initialized")
        except Exception as e:
            st.sidebar.error(f"Failed to initialize limbic engine: {e}")

    # Initialize authentication
    auth = SaoynxAuthentication()

    # --- Limbic demo controls and telemetry ---
    try:
        from emotional_os.glyphs.limbic_telemetry import (
            fetch_recent,
            init_db,
            record_event,
        )
    except Exception:
        # fallback to local import if running from root
        try:
            from emotional_os.glyphs.limbic_telemetry import (
                fetch_recent,
                init_db,
                record_event,
            )
        except Exception:
            record_event = None
            fetch_recent = None
            init_db = None

    # A/B test opt-in
    participate_ab = st.sidebar.checkbox("Participate in Limbic A/B test", value=st.session_state.get('ab_participate', False))
    st.session_state['ab_participate'] = participate_ab

    # Demo input and run button
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Limbic Demo")
    demo_input = st.sidebar.text_area("Demo input text", value=st.session_state.get('demo_input', "I feel so joyful and alive"))
    st.session_state['demo_input'] = demo_input

    # Assign A/B group once per session if participating
    import json
    import random
    import time
    from datetime import datetime
    if participate_ab and 'ab_group' not in st.session_state:
        st.session_state['ab_group'] = 'control' if random.random() < 0.5 else 'treatment'

    ab_group = st.session_state.get('ab_group', 'not_participating')

    run_demo = st.sidebar.button("Run Limbic Demo")

    # Load trauma lexicon for simple safety gating if available
    trauma_terms = set()
    try:
        import json
        import os
        trauma_path = os.path.join(os.path.dirname(__file__), 'emotional_os', 'safety', 'trauma_lexicon.json')
        if os.path.exists(trauma_path):
            with open(trauma_path, 'r', encoding='utf-8') as f:
                trauma_terms = set(json.load(f))
    except Exception:
        trauma_terms = set()

    if run_demo:
        # Validate limbic availability
        if not enable_limbic or not HAS_LIMBIC or 'limbic_engine' not in st.session_state:
            st.sidebar.error('Limbic engine not initialized. Enable it in Integrations first.')
        else:
            engine = st.session_state['limbic_engine']
            # Simple safety check
            lowered = demo_input.lower()
            safety_flag = any(t.lower() in lowered for t in trauma_terms) if trauma_terms else False

            # A/B: if participating and in control, do not apply enrichment
            apply_enrichment = True
            if participate_ab and ab_group == 'control':
                apply_enrichment = False

            start_ts = time.time()
            glyphs_generated = 0

            if safety_flag:
                st.sidebar.warning('Input matches trauma-sensitive terms. Enrichment will not be applied.')
                apply_enrichment = False

            if apply_enrichment:
                # Use emotion mapping (auto-detect by mapping or let engine decide)
                result = engine.process_emotion_with_limbic_mapping(demo_input)
                glyphs_generated = sum(len(v.get('glyph_sequences', {})) for v in result.get('limbic_mapping', {}).values())
                # Prefer visualizer if available
                try:
                    diagram = engine.visualizer.create_emotion_chiasmus_diagram(result.get('emotion', 'joy'))
                except Exception:
                    diagram = json.dumps(result.get('system_signals', {}), ensure_ascii=False, indent=2)
                st.sidebar.markdown('**Limbic Chiasmus**')
                st.sidebar.text_area('Chiasmus output', diagram, height=240)
            else:
                st.sidebar.markdown('**Baseline (no enrichment applied)**')
                st.sidebar.text_area('Baseline output', demo_input, height=120)

            latency_ms = (time.time() - start_ts) * 1000.0

            # Record telemetry
            if record_event:
                try:
                    if callable(init_db):
                        init_db()
                    record_event({
                        'timestamp': datetime.utcnow().isoformat(),
                        'user_id': st.session_state.get('user_id', 'demo_user'),
                        'input_text': demo_input,
                        'emotion': result.get('emotion', '') if apply_enrichment and isinstance(result, dict) else '',
                        'enrichment_applied': apply_enrichment,
                        'ab_group': ab_group,
                        'latency_ms': latency_ms,
                        'glyphs_generated': glyphs_generated,
                        'safety_flag': safety_flag
                    })
                except Exception as e:
                    st.sidebar.error(f'Failed to record telemetry: {e}')

    # Show recent telemetry in sidebar (if available)
    if fetch_recent:
        try:
            recent = fetch_recent(10)
            if recent:
                st.sidebar.markdown('---')
                st.sidebar.markdown('#### Recent Limbic Demo Events')
                for ev in recent[:6]:
                    en = 'Y' if ev.get('enrichment_applied') else 'N'
                    sf = 'Y' if ev.get('safety_flag') else 'N'
                    st.sidebar.markdown(f"- {ev['timestamp'][11:19]} | emo:{ev['emotion'] or '-'} | enr:{en} | grp:{ev['ab_group']} | glyphs:{ev['glyphs_generated']} | safe:{sf}")
        except Exception:
            pass
    # Check if user is authenticated
    if st.session_state.get('authenticated', False):
        render_main_app()
    else:
        render_splash_interface(auth)

if __name__ == "__main__":
    main()
