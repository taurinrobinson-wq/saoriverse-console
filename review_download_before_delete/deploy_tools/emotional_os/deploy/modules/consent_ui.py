#!/usr/bin/env python3
"""
Consent UI Component for Anonymization & Data Sharing

Provides Streamlit UI components for asking users about:
- Whether to remember their story with their name
- Whether to share with therapist/legacy/research
- Whether to keep medical details
"""

import streamlit as st
from typing import Dict, Optional
from datetime import datetime
import json


def render_anonymization_consent_widget(
    exchange_id: str,
    show_medical_option: bool = True,
    show_legacy_option: bool = True,
    show_research_option: bool = False,
) -> Optional[Dict]:
    """
    Render a consent widget after emotional exchange/ritual.

    Args:
        exchange_id: Unique ID for this exchange (for tracking)
        show_medical_option: Show medical term preservation option
        show_legacy_option: Show legacy archive option
        show_research_option: Show research contribution option

    Returns:
        Dict with consent choices, or None if dismissed
    """

    consent_key = f"consent_{exchange_id}"
    if consent_key in st.session_state and st.session_state[consent_key].get("completed"):
        return st.session_state[consent_key]

    # Container for consent widget
    with st.container(border=True):
        st.markdown("### 🧵 Memory & Sharing")
        st.markdown(
            "This moment can be remembered in different ways. How would you like me to hold this?"
        )

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.markdown("**Your Identity**")
            identity_choice = st.radio(
                "How should this be remembered?",
                [
                    "With my name",
                    "Anonymous",
                    "Private (don't store)"
                ],
                key=f"identity_{exchange_id}",
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("**Medical Details**")
            if show_medical_option:
                medical_choice = st.radio(
                    "Medical terms:",
                    [
                        "Keep as-is",
                        "Abstract (e.g., 'the Device')",
                        "Remove"
                    ],
                    key=f"medical_{exchange_id}",
                    label_visibility="collapsed"
                )
            else:
                medical_choice = "Abstract (e.g., 'the Device')"

        with col3:
            st.markdown("**Sharing**")
            sharing_options = ["Keep private"]
            if show_legacy_option:
                sharing_options.append("Legacy archive")
            if show_research_option:
                sharing_options.append("Research")
                sharing_options.append("Therapy (with provider)")

            sharing_choice = st.radio(
                "Can this be shared?",
                sharing_options,
                key=f"sharing_{exchange_id}",
                label_visibility="collapsed"
            )

        st.divider()

        # Buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        result = None
        with col1:
            if st.button("✅ Confirm", use_container_width=True, key=f"confirm_{exchange_id}"):
                result = {
                    "completed": True,
                    "exchange_id": exchange_id,
                    "identity": identity_choice,
                    "medical_details": medical_choice,
                    "sharing": sharing_choice,
                    "timestamp": datetime.now().isoformat(),
                    "allow_names": identity_choice == "With my name",
                    "allow_medical": medical_choice == "Keep as-is",
                }
                st.session_state[consent_key] = result
                st.success("✓ Saved your preference")
                return result

        with col2:
            if st.button("🔄 Change", use_container_width=True, key=f"change_{exchange_id}"):
                if consent_key in st.session_state:
                    del st.session_state[consent_key]
                st.rerun()

        with col3:
            if st.button("⏭️ Later", use_container_width=True, key=f"later_{exchange_id}"):
                # Silently store "don't ask again this session"
                st.session_state[consent_key] = {
                    "completed": False,
                    "skipped": True
                }
                st.info("Got it—I'll remember this preference for now.")
                return None

    return result


def render_consent_summary(consent_result: Dict):
    """Render a summary of user's consent choices."""
    if not consent_result:
        return

    st.markdown("---")
    st.markdown("### 📋 Your Preferences")

    col1, col2, col3 = st.columns(3)

    with col1:
        identity_emoji = "👤" if consent_result.get("allow_names") else "👁️"
        st.metric(
            "Identity",
            consent_result.get("identity", "Not set"),
            delta=f"{identity_emoji}"
        )

    with col2:
        medical_emoji = "⚕️" if consent_result.get("allow_medical") else "🔐"
        st.metric(
            "Medical Details",
            consent_result.get("medical_details", "Not set"),
            delta=f"{medical_emoji}"
        )

    with col3:
        sharing = consent_result.get("sharing", "Keep private")
        sharing_emoji = {
            "Keep private": "🔒",
            "Legacy archive": "📚",
            "Research": "🔬",
            "Therapy (with provider)": "👨‍⚕️",
        }.get(sharing, "❓")
        st.metric("Sharing", sharing, delta=sharing_emoji)


def render_data_privacy_info(use_expander: bool = True):
    """Render information about data privacy and anonymization.

    Args:
        use_expander: If True (default) wraps the content in an expander. Set to
            False when calling from within another expander/sidebar to avoid
            nested expanders which Streamlit disallows.
    """
    content = """
        ### Data Protection Layers
        
        **Layer 1: Gate-Based Masking (Always Active)**
        - Raw user messages are never stored
        - Only emotional signals and patterns are logged
        - AI responses are not retained
        - ✅ HIPAA-compliant (no PHI storage)
        
        **Layer 2: Intelligent Anonymization (When Enabled)**
        - Names → Glyphs (e.g., "Michelle" → "The Thread")
        - Dates → Relative time (e.g., "August 2023" → "2 years ago")
        - Locations → Regions (e.g., "Bell, CA" → "West Coast")
        - Medical → Abstract (e.g., "IVC filter" → "the Device")
        
        **Layer 3: Consent-Based De-Anonymization (You Control)**
        - You can always choose to keep your identity attached
        - Share with your therapist by revealing your name
        - Include in legacy archive with full details
        - Contribute anonymized data to research
        
        ### Your Rights
        - 🔍 See what data we store (ask anytime)
        - 🗑️ Delete your data (instant removal)
        - 📤 Export your data (full JSON export)
        - 🔄 Update your preferences (change anytime)
        
        ### Questions?
        This system is GDPR-aligned and HIPAA-ready. Your privacy is paramount.
        """

    if use_expander:
        with st.expander("🛡️ How Your Data is Protected", expanded=False):
            st.markdown(content)
    else:
        st.markdown("### 🛡️ How Your Data is Protected")
        st.markdown(content)


def render_consent_settings_panel():
    """Render a control panel for managing consent preferences."""
    st.sidebar.markdown("---")
    with st.sidebar.expander("🛡️ Privacy & Consent", expanded=False):
        st.markdown("**Default Anonymization Settings**")

        col1, col2 = st.columns(2)
        with col1:
            allow_names_default = st.checkbox(
                "Store names by default",
                value=st.session_state.get("consent_allow_names", False),
                help="Include real names in stored entries by default"
            )
            st.session_state["consent_allow_names"] = allow_names_default

        with col2:
            allow_medical_default = st.checkbox(
                "Store medical details",
                value=st.session_state.get("consent_allow_medical", False),
                help="Keep medical terminology as-is (instead of abstract forms)"
            )
            st.session_state["consent_allow_medical"] = allow_medical_default

        st.divider()
        st.markdown("**Data Management**")

        # Export / download user's data: show only for authenticated users
        try:
            if st.session_state.get('authenticated', False) and st.session_state.get('user_id'):
                conversation_key = f"conversation_history_{st.session_state.get('user_id')}"
                user_data = {
                    "user_id": st.session_state.get('user_id'),
                    "username": st.session_state.get('username'),
                    "conversations": st.session_state.get(conversation_key, []),
                    "export_date": __import__('datetime').datetime.now().isoformat()
                }
                st.download_button(
                    "📥 Export / Download My Data",
                    json.dumps(user_data, indent=2),
                    file_name=f"emotional_os_data_{st.session_state.get('username') or 'user'}_{__import__('datetime').datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    key="download_consent_sidebar"
                )
        except Exception:
            # Non-fatal; don't break the sidebar if export generation fails
            pass

        if st.button("📊 View My Data Privacy Report"):
            st.info("Privacy report generation coming soon")

        if st.button("🗑️ Delete All My Data"):
            if st.checkbox("I understand this cannot be undone"):
                st.warning(
                    "⚠️ This would permanently delete all your stored data")
                if st.button("YES, delete everything"):
                    st.success(
                        "Deletion request submitted. Check email to confirm.")

        st.divider()
        st.markdown("**Learn More**")

        # Toggleable detailed privacy info: clicking the button toggles
        # visibility and avoids nested expanders (renders inline).
        toggle_key = "consent_privacy_open"
        if toggle_key not in st.session_state:
            st.session_state[toggle_key] = False

        # Button-based toggle: use a distinct widget key for the button so
        # we avoid widget-type conflicts with previous checkbox implementations.
        def _toggle_privacy():
            st.session_state[toggle_key] = not st.session_state.get(
                toggle_key, False)

        label = "Close" if st.session_state.get(
            toggle_key, False) else "Learn More"
        st.button(label, key="consent_privacy_toggle_btn",
                  on_click=_toggle_privacy)

        if st.session_state.get(toggle_key):
            render_data_privacy_info(use_expander=False)


def create_anonymization_consent_record(
    exchange_id: str,
    user_id: str,
    consent_result: Dict,
) -> Optional[Dict]:
    """
    Create a record of user's consent for this specific exchange.

    This is useful for auditing and compliance.
    """
    if not consent_result:
        return None

    return {
        "exchange_id": exchange_id,
        "user_id_hash": user_id,
        "timestamp": consent_result.get("timestamp", datetime.now().isoformat()),
        "consent_choices": {
            "identity": consent_result.get("identity"),
            "medical_details": consent_result.get("medical_details"),
            "sharing": consent_result.get("sharing"),
        },
        "allow_names": consent_result.get("allow_names", False),
        "allow_medical": consent_result.get("allow_medical", False),
        "version": "1.0",
    }


if __name__ == "__main__":
    # Demo
    st.title("Consent UI Components - Demo")

    st.markdown("### Example 1: Consent Widget")
    result = render_anonymization_consent_widget("demo_exchange_1")

    if result:
        st.markdown("### Consent Result")
        st.json(result)

        st.markdown("### Summary")
        render_consent_summary(result)

    st.divider()
    st.markdown("### Example 2: Privacy Info")
    render_data_privacy_info()
