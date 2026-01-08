"""
Audio Conversation UI Component

Streamlit UI for real-time audio conversation with FirstPerson
Provides visual feedback, recording controls, and conversation history
"""

import asyncio
import logging
from typing import Callable, Optional

import streamlit as st

from .audio_conversation_orchestrator import (
    AudioConversationOrchestrator,
    ConversationState,
)

logger = logging.getLogger(__name__)


class AudioConversationUI:
    """Streamlit UI wrapper for audio conversation"""
    
    def __init__(self, response_processor: Callable, session_state_key: str = "audio_orchestrator"):
        """
        Args:
            response_processor: Function(user_text, context) -> system_response
            session_state_key: Streamlit session state key for orchestrator persistence
        """
        self.response_processor = response_processor
        self.state_key = session_state_key
        
        # Initialize orchestrator in session state
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = AudioConversationOrchestrator(
                response_processor
            )
    
    @property
    def orchestrator(self) -> AudioConversationOrchestrator:
        """Get orchestrator from session state"""
        return st.session_state[self.state_key]
    
    def render(self, show_history: bool = True, max_height: int = 500):
        """
        Render full audio conversation UI
        
        Args:
            show_history: Whether to show conversation history
            max_height: Max height for history display (pixels)
        """
        st.markdown("---")
        st.subheader("🎤 Voice Conversation Mode")
        
        # Status indicator with color
        self._render_status_indicator()
        
        # Control buttons
        self._render_control_buttons()
        
        # Audio recording settings (collapsible)
        with st.expander("⚙️ Audio Settings"):
            self._render_audio_settings()
        
        # Conversation history
        if show_history and self.orchestrator.conversation_history:
            self._render_conversation_history(max_height)
    
    def _render_status_indicator(self):
        """Render status with color coding"""
        state = self.orchestrator.state
        
        # Color map
        colors = {
            ConversationState.IDLE: "🟢",
            ConversationState.RECORDING: "🔴",
            ConversationState.TRANSCRIBING: "🟡",
            ConversationState.PROCESSING: "🟡",
            ConversationState.SPEAKING: "🔵",
            ConversationState.PAUSED: "🟠",
            ConversationState.STOPPED: "⚫",
        }
        
        color_emoji = colors.get(state, "⚪")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown(f"### Status: {color_emoji}")
        
        with col2:
            st.info(f"**{state.value.upper()}**")
        
        with col3:
            if self.orchestrator.conversation_history:
                st.metric(
                    "Turns",
                    len(self.orchestrator.conversation_history)
                )
    
    def _render_control_buttons(self):
        """Render conversation control buttons"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button(
                "🎤 Start Listening",
                key="btn_start_audio",
                use_container_width=True
            ):
                self._start_audio_conversation()
        
        with col2:
            if st.button(
                "⏸️ Pause",
                key="btn_pause_audio",
                use_container_width=True,
                disabled=(self.orchestrator.state == ConversationState.IDLE)
            ):
                self.orchestrator.pause()
                st.rerun()
        
        with col3:
            if st.button(
                "▶️ Resume",
                key="btn_resume_audio",
                use_container_width=True,
                disabled=(self.orchestrator.state != ConversationState.PAUSED)
            ):
                self.orchestrator.resume()
                st.rerun()
        
        with col4:
            if st.button(
                "⏹️ Stop",
                key="btn_stop_audio",
                use_container_width=True,
                type="secondary"
            ):
                self.orchestrator.stop()
                st.rerun()
    
    def _render_audio_settings(self):
        """Render audio recording settings"""
        col1, col2 = st.columns(2)
        
        with col1:
            silence_duration = st.slider(
                "Silence Duration (s)",
                min_value=0.5,
                max_value=3.0,
                value=1.5,
                step=0.25,
                help="Time of silence to end recording"
            )
            self.orchestrator.recorder.silence_duration = silence_duration
        
        with col2:
            silence_threshold = st.slider(
                "Silence Threshold",
                min_value=0.01,
                max_value=0.1,
                value=0.02,
                step=0.01,
                help="Audio amplitude below this is considered silence"
            )
            self.orchestrator.recorder.silence_threshold = silence_threshold
    
    def _render_conversation_history(self, max_height: int = 500):
        """Render conversation history with expandable turns"""
        st.subheader(f"📝 Conversation History ({len(self.orchestrator.conversation_history)} turns)")
        
        for i, turn in enumerate(self.orchestrator.conversation_history, 1):
            with st.expander(
                f"Turn {i}: {turn.user_text[:50]}...",
                expanded=(i == len(self.orchestrator.conversation_history))
            ):
                st.write(f"**You**: {turn.user_text}")
                st.divider()
                st.write(f"**FirstPerson**: {turn.system_response}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Processing Time", f"{turn.processing_time:.2f}s")
                with col2:
                    st.metric("Audio", "✅" if turn.audio_played else "❌")
    
    def _start_audio_conversation(self):
        """Start the audio conversation loop"""
        with st.spinner("🎤 Initializing audio conversation..."):
            try:
                # Register UI update callback
                self.orchestrator.register_state_callback(
                    lambda state: st.session_state.update({"audio_state": state})
                )
                
                # Run conversation loop
                asyncio.run(self.orchestrator.run_conversation_loop())
                
                st.success("✅ Audio conversation complete!")
                st.rerun()
            except KeyboardInterrupt:
                st.warning("⚠️ Conversation interrupted by user")
            except Exception as e:
                st.error(f"❌ Error during audio conversation: {e}")
                logger.exception("Audio conversation error")


def render_audio_conversation(
    response_processor: Callable,
    show_settings: bool = True,
    show_history: bool = True
):
    """
    Convenience function to render audio conversation in Streamlit
    
    Args:
        response_processor: Function to process user input
        show_settings: Show audio settings section
        show_history: Show conversation history
    """
    ui = AudioConversationUI(response_processor)
    ui.render(show_history=show_history)


# Example usage for testing
if __name__ == "__main__":
    st.set_page_config(page_title="Audio Conversation Test", layout="wide")
    
    def demo_processor(user_text: str, context: dict) -> str:
        """Demo response processor"""
        return f"You said: {user_text}. This is a demo response."
    
    render_audio_conversation(demo_processor)
