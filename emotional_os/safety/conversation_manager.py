from typing import Optional, Dict
from datetime import datetime

from .sanctuary_handler import (
    classify_risk,
    build_consent_prompt,
    handle_consent_reply,
    make_privacy_safe_log,
)

try:
    # parse_input is the canonical message analyzer
    from emotional_os.glyphs.signal_parser import parse_input
except Exception:
    # If the parser is not available, define a stub so imports don't fail in tests
    def parse_input(*args, **kwargs):
        return {"voltage_response": "(parser not available)", "signals": []}


class SanctuaryConversationManager:
    """Manage per-session consent flows and route messages accordingly.

    Minimal in-memory session store is used for demo/testing. For production,
    replace with a persistent session store.
    """

    def __init__(self):
        # session_id -> state dict (pending_consent: bool, risk_level: str)
        self._sessions: Dict[str, Dict] = {}

    def _get_session(self, session_id: str) -> Dict:
        return self._sessions.setdefault(session_id, {"pending_consent": False, "risk_level": "none"})

    def process_user_message(
        self,
        session_id: str,
        user_hash: Optional[str],
        message: str,
        lexicon_path: str = "parser/signal_lexicon.json",
        db_path: str = "emotional_os/glyphs/glyphs.db",
    ) -> Dict:
        """Process a user message. If a consent prompt is pending for the session,
        route the message to `handle_consent_reply`. Otherwise, analyze the message
        and, if risk is detected, return a consent prompt and mark session as pending.

        Returns a dict with fields depending on the result:
          - type: 'consent_prompt' | 'consent_reply' | 'analysis'
          - payload: prompt text, or reply result, or parse_input result
          - log: privacy-safe derived log entry (optional)
        """
        session = self._get_session(session_id)

        # If we're waiting on user's consent reply, handle it
        if session.get("pending_consent"):
            risk = session.get("risk_level", "high")
            reply_result = handle_consent_reply(message, risk)

            # Log privacy-safe event
            log_entry = make_privacy_safe_log(user_hash or "anonymous", risk, reply_result.get("action", "unknown"))
            log_entry["timestamp"] = datetime.utcnow().isoformat()

            # Clear pending consent
            session["pending_consent"] = False
            session["risk_level"] = "none"

            return {"type": "consent_reply", "payload": reply_result, "log": log_entry}

        # No pending consent: classify risk first
        risk = classify_risk(message)
        if risk != "none":
            # Set session to expect reply and present consent prompt
            session["pending_consent"] = True
            session["risk_level"] = risk
            prompt = build_consent_prompt(risk)

            # Privacy-safe log for detection event
            log_entry = make_privacy_safe_log(user_hash or "anonymous", risk, "prompted")
            log_entry["timestamp"] = datetime.utcnow().isoformat()

            return {"type": "consent_prompt", "payload": prompt, "log": log_entry}

        # Safe/no risk: fall back to normal parsing
        analysis = parse_input(message, lexicon_path=lexicon_path, db_path=db_path)
        return {"type": "analysis", "payload": analysis}
