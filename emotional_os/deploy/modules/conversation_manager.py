"""
Conversation Management Module

Handles:
- Conversation persistence to Supabase
- Auto-naming conversations based on first message
- Loading previous conversations
- Renaming/deleting conversations
- Session state management
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    import requests
except Exception:
    requests = None

import streamlit as st

logger = logging.getLogger(__name__)


def generate_auto_name(first_message: str, max_length: int = 50) -> str:
    """
    Generate a conversation name from the first user message.

    Similar to Microsoft Copilot's approach:
    - Extract key emotional terms or topics
    - Create a concise, meaningful title
    - Limit to max_length characters
    """
    if not first_message:
        return "New Conversation"

    # Clean the text
    text = first_message.strip()[:100]

    # Remove common phrases
    phrases_to_remove = [
        r"i\s+(?:feel|think|believe|know|want|need)\s+",
        r"(?:can|could|would|should|do)\s+you\s+",
        r"(?:what|how|why|when|where)\s+(?:about|is|are|do|does)\s+",
    ]

    for phrase in phrases_to_remove:
        text = re.sub(phrase, "", text, flags=re.IGNORECASE)

    # Extract first meaningful sentence/phrase
    sentences = text.split(". ")
    if sentences:
        title = sentences[0]
    else:
        title = text

    # Clean up and limit length
    title = title.strip()
    if len(title) > max_length:
        # Truncate and add ellipsis
        title = title[: max_length - 3] + "..."

    # Capitalize properly
    title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()

    return title


class ConversationManager:
    """Manages conversation persistence and retrieval."""

    def __init__(self, user_id: str, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.user_id = user_id
        # Prefer explicit args, then environment variables, then Streamlit secrets.
        self.supabase_url = supabase_url or os.environ.get("SUPABASE_URL") or st.secrets.get("supabase", {}).get("url")
        # Support both a service role key (preferred for server-side writes)
        # and the regular SUPABASE_KEY used in some deployments.
        self.supabase_key = (
            supabase_key
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("SUPABASE_KEY")
            or st.secrets.get("supabase", {}).get("service_role_key")
            or st.secrets.get("supabase", {}).get("key")
        )
        self.base_url = self._normalize_supabase_url(self.supabase_url) if self.supabase_url else None

    def _normalize_supabase_url(self, url: str) -> str:
        """Extract base Supabase URL from function URL if needed."""
        if not url:
            return ""
        url = url.rstrip("/")
        if "/functions/" in url:
            return url.split("/functions/")[0]
        return url

    def _get_headers(self) -> Dict:
        """Get headers for Supabase API requests."""
        return {
            "Content-Type": "application/json",
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Prefer": "return=representation",
        }

    def save_conversation(
        self, conversation_id: str, title: str, messages: List[Dict], processing_mode: str = "local"
    ) -> Tuple[bool, str]:
        """
        Save or update a conversation to Supabase.

        Returns: (success: bool, message: str)
        """
        if not self.base_url or not self.supabase_key:
            return False, "Supabase not configured"

        if not requests:
            return False, "Requests library not available"

        try:
            url = f"{self.base_url}/rest/v1/conversations"
            payload = {
                "user_id": self.user_id,
                "conversation_id": conversation_id,
                "title": title,
                "messages": json.dumps(messages),
                "processing_mode": processing_mode,
                "updated_at": datetime.now().isoformat(),
                "message_count": len(messages),
            }

            # Upsert: insert if new, update if exists
            response = requests.post(url, headers=self._get_headers(), json=[payload], timeout=10)

            if response.status_code in (200, 201):
                return True, "Conversation saved successfully"
            else:
                # Include response body to aid debugging (e.g., 401 Unauthorized from Supabase)
                try:
                    body = response.text
                except Exception:
                    body = "<unreadable response body>"
                logger.debug(f"save_conversation HTTP {response.status_code}: {body}")
                msg = f"Failed to save conversation (HTTP {response.status_code}): {body}"
                return False, msg

        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return False, f"Error saving conversation: {str(e)}"

    def load_conversations(self) -> List[Dict]:
        """
        Load all conversations for the user from Supabase.

        Returns: List of conversations with id, title, updated_at, message_count
        """
        if not self.base_url or not self.supabase_key:
            return []

        if not requests:
            return []

        try:
            url = f"{self.base_url}/rest/v1/conversations"
            params = {
                "select": "conversation_id,title,updated_at,message_count,processing_mode",
                "user_id": f"eq.{self.user_id}",
                "order": "updated_at.desc",
                "limit": "100",
            }

            response = requests.get(url, headers=self._get_headers(), params=params, timeout=10)

            if response.status_code == 200:
                conversations = response.json()
                # Backward compatibility shim: translate any legacy "ai_preferred"
                # processing_mode values into the new representation where
                # hybrid mode is removed and we migrate legacy preference to
                # local-only mode to avoid invoking remote AI by default.
                if isinstance(conversations, list):
                    for c in conversations:
                        pm = c.get("processing_mode")
                        if pm == "ai_preferred":
                            # Map legacy 'ai_preferred' → 'local' and clear
                            # 'prefer_ai' to avoid accidental remote AI calls.
                            c["processing_mode"] = "local"
                            c["prefer_ai"] = False
                return conversations if isinstance(conversations, list) else []
            else:
                return []

        except Exception as e:
            logger.debug(f"Error loading conversations: {e}")
            return []

    def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Load a specific conversation from Supabase.

        Returns: Dict with conversation data or None if not found
        """
        if not self.base_url or not self.supabase_key:
            return None

        if not requests:
            return None

        try:
            url = f"{self.base_url}/rest/v1/conversations"
            params = {"conversation_id": f"eq.{conversation_id}", "user_id": f"eq.{self.user_id}"}

            response = requests.get(url, headers=self._get_headers(), params=params, timeout=10)

            if response.status_code == 200:
                conversations = response.json()
                if conversations:
                    conv = conversations[0]
                    # Parse messages JSON string
                    if isinstance(conv.get("messages"), str):
                        conv["messages"] = json.loads(conv["messages"])
                    # Backward compatibility: map legacy ai_preferred into
                    # 'local' to avoid invoking remote AI by default.
                    if conv.get("processing_mode") == "ai_preferred":
                        conv["processing_mode"] = "local"
                        conv["prefer_ai"] = False
                    return conv
            return None

        except Exception as e:
            logger.debug(f"Error loading conversation: {e}")
            return None

    def load_user_preferences(self) -> Dict:
        """
        Load stored user preferences (best-effort) from Supabase.

        Returns a dict of preferences. If nothing is available returns an empty dict.
        """
        if not self.base_url or not self.supabase_key:
            return {}

        if not requests:
            return {}

        try:
            url = f"{self.base_url}/rest/v1/user_preferences"
            params = {"select": "persist_history,persist_confirmed", "user_id": f"eq.{self.user_id}"}
            response = requests.get(url, headers=self._get_headers(), params=params, timeout=6)
            if response.status_code == 200:
                rows = response.json()
                if rows and isinstance(rows, list) and len(rows) > 0:
                    row = rows[0]
                    prefs = {
                        "persist_history": bool(row.get("persist_history", False)),
                        "persist_confirmed": bool(row.get("persist_confirmed", False)),
                    }
                    return prefs
            return {}
        except Exception as e:
            logger.debug(f"Error loading user preferences: {e}")
            return {}

    def save_user_preferences(self, prefs: Dict) -> Tuple[bool, str]:
        """
        Save simple user preferences to Supabase (best-effort). Expects a dict
        containing keys like 'persist_history' and 'persist_confirmed'. Returns
        (success: bool, message: str).
        """
        if not self.base_url or not self.supabase_key:
            return False, "Supabase not configured"

        if not requests:
            return False, "Requests library not available"

        try:
            url = f"{self.base_url}/rest/v1/user_preferences"
            payload = {
                "user_id": self.user_id,
                "persist_history": bool(prefs.get("persist_history", False)),
                "persist_confirmed": bool(prefs.get("persist_confirmed", False)),
                "updated_at": datetime.now().isoformat(),
            }

            # Use upsert semantics: POST a single-item list. Supabase needs
            # appropriate DB constraints to upsert; this is best-effort.
            response = requests.post(url, headers=self._get_headers(), json=[payload], timeout=6)
            if response.status_code in (200, 201):
                return True, "Preferences saved"
            else:
                return False, f"Failed to save preferences (HTTP {response.status_code})"
        except Exception as e:
            logger.debug(f"Error saving user preferences: {e}")
            return False, str(e)

    def delete_conversation(self, conversation_id: str) -> Tuple[bool, str]:
        """Delete a conversation from Supabase."""
        if not self.base_url or not self.supabase_key:
            return False, "Supabase not configured"

        if not requests:
            return False, "Requests library not available"

        try:
            url = f"{self.base_url}/rest/v1/conversations"
            params = {"conversation_id": f"eq.{conversation_id}", "user_id": f"eq.{self.user_id}"}

            response = requests.delete(url, headers=self._get_headers(), params=params, timeout=10)

            if response.status_code in (200, 204):
                return True, "Conversation deleted successfully"
            else:
                return False, f"Failed to delete conversation (HTTP {response.status_code})"

        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False, f"Error deleting conversation: {str(e)}"

    def rename_conversation(self, conversation_id: str, new_title: str) -> Tuple[bool, str]:
        """Rename a conversation."""
        if not self.base_url or not self.supabase_key:
            return False, "Supabase not configured"

        if not requests:
            return False, "Requests library not available"

        try:
            url = f"{self.base_url}/rest/v1/conversations"
            params = {"conversation_id": f"eq.{conversation_id}", "user_id": f"eq.{self.user_id}"}

            payload = {"title": new_title, "updated_at": datetime.now().isoformat()}

            response = requests.patch(url, headers=self._get_headers(), json=payload, params=params, timeout=10)

            if response.status_code in (200, 204):
                return True, "Conversation renamed successfully"
            else:
                return False, f"Failed to rename conversation (HTTP {response.status_code})"

        except Exception as e:
            logger.error(f"Error renaming conversation: {e}")
            return False, f"Error renaming conversation: {str(e)}"


def initialize_conversation_manager() -> Optional[ConversationManager]:
    """Initialize conversation manager from session state."""
    if "user_id" not in st.session_state:
        return None

    return ConversationManager(st.session_state.user_id)


def load_all_conversations_to_sidebar(manager: ConversationManager) -> None:
    """Display all user's previous conversations in sidebar."""
    if not manager:
        return

    conversations = manager.load_conversations()

    # Merge any optimistic session-cached conversations so newly-created
    # conversations appear in the sidebar immediately even if server-side
    # persistence is still pending or failing. Cached items are prepended
    # and de-duplicated by `conversation_id`.
    try:
        cached = st.session_state.get("session_cached_conversations", [])
        if cached and isinstance(cached, list):
            seen = {c.get("conversation_id") for c in conversations if isinstance(c, dict) and c.get("conversation_id")}
            merged = []
            # Add cached first (fresh items)
            for c in cached:
                if not c:
                    continue
                cid = c.get("conversation_id")
                if not cid or cid in seen:
                    continue
                merged.append(c)
                seen.add(cid)
            # Then extend with server-provided conversations
            merged.extend([c for c in conversations if isinstance(c, dict)])
            conversations = merged
    except Exception:
        # Best-effort merge; if anything goes wrong, fall back to server list
        pass

    if not conversations:
        st.sidebar.info("No previous conversations yet. Start a new one!")
        return

    st.sidebar.markdown("### 📚 Previous Conversations")

    for conv in conversations:
        col1, col2, col3 = st.sidebar.columns([3, 1, 1])

        with col1:
            # Click to load conversation
            if st.button(f"💬 {conv['title']}", key=f"load_conv_{conv['conversation_id']}", use_container_width=True):
                try:
                    # Best-effort: load the conversation immediately using the manager
                    user_id = st.session_state.get("user_id")
                    conversation_key = f"conversation_history_{user_id}"
                    loaded = manager.load_conversation(conv["conversation_id"])
                    if loaded:
                        msgs = (
                            loaded.get("messages")
                            if isinstance(loaded.get("messages"), list)
                            else loaded.get("messages", [])
                        )
                        st.session_state[conversation_key] = msgs or []
                        st.session_state["current_conversation_id"] = loaded.get(
                            "conversation_id", conv["conversation_id"]
                        )
                        st.session_state["conversation_title"] = loaded.get("title", conv["title"])
                        try:
                            st.sidebar.success(f"Loaded: {st.session_state['conversation_title']}")
                        except Exception:
                            pass
                        st.rerun()

                except Exception:
                    # Fallback to the previous behavior if immediate load fails
                    st.session_state["selected_conversation"] = conv["conversation_id"]
                    st.session_state["conversation_title"] = conv["title"]
                    st.rerun()

        with col2:
            # Rename button
            if st.button("✏️", key=f"rename_{conv['conversation_id']}", help="Rename"):
                st.session_state[f"renaming_{conv['conversation_id']}"] = True
                st.rerun()

        with col3:
            # Delete button
            if st.button("🗑️", key=f"delete_{conv['conversation_id']}", help="Delete"):
                # If this conversation is an optimistic session-cached item,
                # remove it from the session cache and avoid calling the
                # server-side delete API which will fail for unsaved items.
                try:
                    cached = st.session_state.get("session_cached_conversations", [])
                    if isinstance(cached, list) and any(
                        c.get("conversation_id") == conv["conversation_id"] for c in cached
                    ):
                        st.session_state["session_cached_conversations"] = [
                            c for c in cached if c.get("conversation_id") != conv["conversation_id"]
                        ]
                        st.sidebar.success("Deleted local conversation")
                        st.rerun()
                except Exception:
                    pass

                success, message = manager.delete_conversation(conv["conversation_id"])
                if success:
                    st.sidebar.success(message)
                    st.rerun()
                else:
                    st.sidebar.error(message)

        # Handle rename dialog
        if st.session_state.get(f"renaming_{conv['conversation_id']}", False):
            new_title = st.sidebar.text_input(
                "New title:", value=conv["title"], key=f"rename_input_{conv['conversation_id']}"
            )
            col_a, col_b = st.sidebar.columns(2)
            with col_a:
                if st.button("Save", key=f"save_rename_{conv['conversation_id']}"):
                    success, message = manager.rename_conversation(conv["conversation_id"], new_title)
                    if success:
                        st.sidebar.success(message)
                        st.session_state[f"renaming_{conv['conversation_id']}"] = False
                        st.rerun()
                    else:
                        st.sidebar.error(message)
            with col_b:
                if st.button("Cancel", key=f"cancel_rename_{conv['conversation_id']}"):
                    st.session_state[f"renaming_{conv['conversation_id']}"] = False
                    st.rerun()


# Backwards compatibility shim
def generate_conversation_title(first_message: str, max_length: int = 50) -> str:
    """Compatibility wrapper for older tests/modules expecting
    `generate_conversation_title`. Delegates to `generate_auto_name`.
    """
    return generate_auto_name(first_message, max_length)
