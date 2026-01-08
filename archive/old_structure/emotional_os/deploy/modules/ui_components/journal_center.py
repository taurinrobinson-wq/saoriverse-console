"""
Journal Center Component.

Handles personal logging, daily check-ins, self-care tracking,
boundary rituals, and reflective journaling.
"""

import datetime
import logging
import streamlit as st

logger = logging.getLogger(__name__)


def render_journal_center():
    """Render the complete journal center interface."""
    if not st.session_state.get("show_personal_log"):
        return

    try:
        st.markdown("### 📘 Journal & Self-Care Center")

        journal_type = st.selectbox(
            "Choose Journal Type",
            [
                "Personal Log",
                "Daily Emotional Check-In",
                "Self-Care Tracker",
                "Micro-Boundary Ritual",
                "Reflective Journal",
            ],
            key="journal_type_select",
        )

        if journal_type == "Personal Log":
            _render_personal_log()
        elif journal_type == "Daily Emotional Check-In":
            _render_daily_checkin()
        elif journal_type == "Self-Care Tracker":
            _render_self_care_tracker()
        elif journal_type == "Micro-Boundary Ritual":
            _render_boundary_ritual()
        elif journal_type == "Reflective Journal":
            _render_reflective_journal()

        if st.button("Close Journal Center"):
            st.session_state["show_personal_log"] = False
            st.rerun()

    except Exception as e:
        logger.debug(f"Error rendering journal center: {e}")


def _render_personal_log():
    """Render personal log form."""
    try:
        st.markdown(
            "Use this space to record a structured emotional entry. "
            "You'll log the date, event, mood, reflections, and insights."
        )

        date = st.date_input("Date", value=datetime.date.today())
        log_time = st.time_input("Time", value=datetime.datetime.now().time())
        event = st.text_area("Event", placeholder="What happened?")
        mood = st.text_input("Mood", placeholder="How did it feel?")
        reflections = st.text_area(
            "Reflections", placeholder="What's emerging emotionally?")
        insights = st.text_area(
            "Insights", placeholder="What truth or clarity surfaced?")

        if st.button("Conclude Log"):
            st.success("Your personal log has been saved.")
            _download_journal_entry(
                date, log_time, event, mood, reflections, insights)

    except Exception as e:
        logger.debug(f"Error rendering personal log: {e}")


def _render_daily_checkin():
    """Render daily emotional check-in form."""
    try:
        st.markdown(
            "Log your mood, stress level, and a short reflection for today.")

        checkin_date = st.date_input(
            "Date", value=datetime.date.today(), key="checkin_date")
        mood = st.selectbox(
            "Mood",
            ["Calm", "Stressed", "Sad", "Angry", "Joyful", "Fatigued", "Other"],
            key="checkin_mood",
        )
        stress = st.slider("Stress Level", 0, 10, 5, key="checkin_stress")
        reflection = st.text_area(
            "Reflection", placeholder="What's on your mind today?", key="checkin_reflection")

        if st.button("Save Check-In"):
            st.success("Your daily check-in has been saved.")
            _store_checkin_entry(checkin_date, mood, stress, reflection)

    except Exception as e:
        logger.debug(f"Error rendering daily check-in: {e}")


def _render_self_care_tracker():
    """Render self-care tracking form."""
    try:
        st.markdown("Track your self-care activities and routines.")

        activities = st.multiselect(
            "Self-Care Activities",
            ["Exercise", "Creative Work", "Peer Support", "Rest",
                "Healthy Meal", "Time Outdoors", "Other"],
            key="selfcare_activities",
        )
        notes = st.text_area(
            "Notes", placeholder="Any details or thoughts about your self-care today?", key="selfcare_notes")

        if st.button("Save Self-Care Entry"):
            st.success("Your self-care entry has been saved.")
            _store_selfcare_entry(activities, notes)

    except Exception as e:
        logger.debug(f"Error rendering self-care tracker: {e}")


def _render_boundary_ritual():
    """Render micro-boundary ritual form."""
    try:
        st.markdown("Mark a transition between work and personal time.")

        ritual_type = st.selectbox(
            "Ritual Type",
            ["Change Location", "Wash Hands",
                "Listen to Music", "Short Walk", "Other"],
            key="ritual_type",
        )
        ritual_notes = st.text_area(
            "Ritual Notes",
            placeholder="How did this ritual help you shift gears?",
            key="ritual_notes",
        )

        if st.button("Log Ritual"):
            st.success("Your boundary ritual has been logged.")
            _store_ritual_entry(ritual_type, ritual_notes)

    except Exception as e:
        logger.debug(f"Error rendering boundary ritual: {e}")


def _render_reflective_journal():
    """Render reflective journaling form."""
    try:
        st.markdown(
            "Write about your own reactions, growth, and challenges. "
            "No client details—just your personal journey."
        )

        journal_date = st.date_input(
            "Date", value=datetime.date.today(), key="reflective_date")
        entry = st.text_area(
            "Reflection Entry",
            placeholder="What's emerging for you emotionally or personally?",
            key="reflective_entry",
        )

        if st.button("Save Reflection"):
            st.success("Your reflection has been saved.")
            _store_reflection_entry(journal_date, entry)

    except Exception as e:
        logger.debug(f"Error rendering reflective journal: {e}")


def _download_journal_entry(date, time, event, mood, reflections, insights):
    """Provide journal entry download."""
    try:
        from emotional_os.deploy.modules.doc_export import generate_doc

        if callable(generate_doc):
            buf = generate_doc(date, time, event, mood, reflections, insights)
            try:
                data_bytes = buf.getvalue()
            except Exception:
                data_bytes = buf

            st.download_button(
                label="Download as Word Doc",
                data=data_bytes,
                file_name="personal_log.docx",
            )
        else:
            # Fallback to text
            fallback_text = (
                f"Date: {date}\nTime: {time}\nEvent: {event}\nMood: {mood}\n\n"
                f"Reflections:\n{reflections}\n\nInsights:\n{insights}"
            )
            st.download_button(
                label="Download as TXT",
                data=fallback_text.encode("utf-8"),
                file_name="personal_log.txt",
            )

    except Exception as e:
        logger.debug(f"Error downloading journal entry: {e}")


def _store_checkin_entry(date, mood, stress, reflection):
    """Store check-in entry in session."""
    try:
        key = f"checkin_{date.isoformat()}"
        st.session_state[key] = {
            "date": date.isoformat(),
            "mood": mood,
            "stress": stress,
            "reflection": reflection,
        }
    except Exception as e:
        logger.debug(f"Error storing check-in: {e}")


def _store_selfcare_entry(activities, notes):
    """Store self-care entry in session."""
    try:
        key = f"selfcare_{datetime.date.today().isoformat()}"
        st.session_state[key] = {
            "activities": activities,
            "notes": notes,
        }
    except Exception as e:
        logger.debug(f"Error storing self-care entry: {e}")


def _store_ritual_entry(ritual_type, notes):
    """Store ritual entry in session."""
    try:
        key = f"ritual_{datetime.date.today().isoformat()}"
        st.session_state[key] = {
            "type": ritual_type,
            "notes": notes,
        }
    except Exception as e:
        logger.debug(f"Error storing ritual entry: {e}")


def _store_reflection_entry(date, entry):
    """Store reflection entry in session."""
    try:
        key = f"reflection_{date.isoformat()}"
        st.session_state[key] = {
            "date": date.isoformat(),
            "content": entry,
        }
    except Exception as e:
        logger.debug(f"Error storing reflection: {e}")
