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
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

try:
    import requests
except Exception:
    requests = None

import streamlit as st

logger = logging.getLogger(__name__)


def _mask_key(key: Optional[str]) -> str:
    """Return a masked representation of a key for safe logging.

    Shows only leading/trailing characters with middle elided so logs
    can help debug which key is being used without revealing secrets.
    """
    try:
        if not key:
            return "<none>"
        s = str(key)
        # If it contains spaces (e.g. 'Bearer <token>'), mask the token part
        if ' ' in s:
            parts = s.split(' ', 1)
            prefix = parts[0]
            token = parts[1]
            if len(token) <= 8:
                tmask = token[:2] + '...' + token[-2:]
            else:
                tmask = token[:4] + '...' + token[-4:]
            return f"{prefix} {tmask}"
        if len(s) <= 8:
            return s[:2] + '...' + s[-2:]
        return s[:4] + '...' + s[-4:]
    except Exception:
        return "<masked>"


def generate_auto_name_with_glyphs(first_message: str, max_length: int = 50) -> Tuple[str, List[str]]:
    """
    Generate a conversation name from the first user message using glyph-based naming.

    Returns:
        tuple: (conversation_name, list_of_glyph_names)

    Creates names like "Tuesday Threshold–Flame–Echo" based on:
    - Day of week (optional) 
    - Top 3 glyphs detected from the first message
    """
    if not first_message:
        return "New Conversation", []

    try:
        # Import required modules for glyph detection
        from emotional_os.core.signal_parser import parse_signals, evaluate_gates, load_signal_map
        from emotional_os.core.paths import signal_lexicon_path
        import datetime
        import json
        import os

        # Load glyph lexicon from JSON file
        glyph_file_paths = [
            'data/glyph_lexicon_rows.json',
            '/workspaces/saoriverse-console/data/glyph_lexicon_rows.json',
            os.path.join(os.getcwd(), 'data', 'glyph_lexicon_rows.json')
        ]

        all_glyphs = None
        for path in glyph_file_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        all_glyphs = json.load(f)
                    break
            except Exception:
                continue

        if not all_glyphs:
            # Fallback to traditional naming if no glyphs available
            return _generate_traditional_name(first_message, max_length), []

        # Parse signals and gates from the message
        lexicon_path = str(signal_lexicon_path())
        signal_map = load_signal_map(lexicon_path)
        signals = parse_signals(first_message, signal_map)
        gates = evaluate_gates(signals)

        # Find matching glyphs
        matching_glyphs = []
        for glyph in all_glyphs:
            glyph_gate = glyph.get('gate', '')
            if glyph_gate in gates:
                matching_glyphs.append(glyph)

        # Extract glyph names (up to 3)
        glyph_names = []
        for glyph in matching_glyphs[:3]:
            name = glyph.get('glyph_name', '')
            if name:
                glyph_names.append(name)

        # Build the name
        if glyph_names:
            # Join with em-dash for elegance
            glyph_string = "–".join(glyph_names)

            # Add day of week if there's room
            today = datetime.datetime.now().strftime("%A")
            if len(glyph_string) + len(today) + 1 <= max_length:
                title = f"{today} {glyph_string}"
            else:
                title = glyph_string

            return title, glyph_names
        else:
            # Fallback to traditional approach if no glyphs detected
            fallback_name = _generate_traditional_name(
                first_message, max_length)
            return fallback_name, []

    except Exception as e:
        # Graceful fallback if glyph system fails
        fallback_name = _generate_traditional_name(first_message, max_length)
        return fallback_name, []


def generate_auto_name(first_message: str, max_length: int = 50) -> str:
    """
    Generate a conversation name from the first user message using glyph-based naming.

    Creates names like "Tuesday Threshold–Flame–Echo" based on:
    - Day of week (optional) 
    - Top 3 glyphs detected from the first message
    """
    name, _ = generate_auto_name_with_glyphs(first_message, max_length)
    return name


def _generate_traditional_name(first_message: str, max_length: int = 50) -> str:
    """
    Traditional conversation naming fallback.
    """
    # Clean the text
    text = first_message.strip()[:100]

    # Remove common phrases
    phrases_to_remove = [
        r'i\s+(?:feel|think|believe|know|want|need)\s+',
        r'(?:can|could|would|should|do)\s+you\s+',
        r'(?:what|how|why|when|where)\s+(?:about|is|are|do|does)\s+',
    ]

    for phrase in phrases_to_remove:
        text = re.sub(phrase, '', text, flags=re.IGNORECASE)

    # Extract first meaningful sentence/phrase
    sentences = text.split('. ')
    if sentences:
        title = sentences[0]
    else:
        title = text

    # Clean up and limit length
    title = title.strip()
    if len(title) > max_length:
        # Truncate and add ellipsis
        title = title[:max_length-3] + "..."

    # Capitalize properly
    title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()

    return title


class ConversationManager:
    """Manages conversation persistence and retrieval."""

    def __init__(self, user_id: str, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.user_id = user_id
        self.supabase_url = supabase_url or st.secrets.get(
            "supabase", {}).get("url")

        # Try to get service role key first (bypasses RLS), then fall back to regular key
        service_role_key = (
            supabase_key or
            st.secrets.get("supabase", {}).get("service_role_key") or
            st.secrets.get("supabase", {}).get("service_role") or
            os.getenv("SUPABASE_SERVICE_ROLE_KEY") or
            st.secrets.get("supabase", {}).get("key")  # fallback to anon key
        )
        self.supabase_key = service_role_key
        self.base_url = self._normalize_supabase_url(
            self.supabase_url) if self.supabase_url else None

    def _normalize_supabase_url(self, url: str) -> str:
        """Extract base Supabase URL from function URL if needed."""
        if not url:
            return ""
        url = url.rstrip('/')
        if '/functions/' in url:
            return url.split('/functions/')[0]
        return url

    def _get_headers(self) -> Dict:
        """Get headers for Supabase API requests."""
        # Prefer using a stable anon/service key for the `apikey` header and
        # use a service role key for Authorization when available. If only a
        # user JWT is present in session state, fall back to that for
        # Authorization while leaving `apikey` as the anon key (that's the
        # recommended supabase pattern for browser-like requests).
        try:
            anon_key = None
            try:
                anon_key = st.secrets.get('supabase', {}).get('key')
            except Exception:
                anon_key = None

            # Fallback to environment variable if streamlit secrets are not used
            if not anon_key:
                anon_key = os.getenv(
                    'SUPABASE_ANON_KEY') or os.getenv('SUPABASE_KEY')

            # Determine auth token: prefer service role (self.supabase_key),
            # otherwise fall back to a user JWT in session state, then anon_key.
            auth_token = self.supabase_key or st.session_state.get(
                'user_jwt_token') if hasattr(st, 'session_state') else None
            if not auth_token:
                auth_token = anon_key

            headers = {
                'Content-Type': 'application/json',
                'apikey': anon_key or auth_token,
                'Authorization': f'Bearer {auth_token}' if auth_token else '',
                'Prefer': 'return=representation'
            }
            return headers
        except Exception:
            # Best-effort fallback
            return {
                'Content-Type': 'application/json',
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Prefer': 'return=representation'
            }

    def save_conversation(self, conversation_id: str, title: str, messages: List[Dict],
                          processing_mode: str = "hybrid", auto_name: Optional[str] = None,
                          custom_name: Optional[str] = None, glyphs_triggered: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Save or update a conversation to Supabase.

        Args:
            conversation_id: Unique conversation identifier
            title: Legacy title field (for backward compatibility)
            messages: List of conversation messages
            processing_mode: AI processing mode
            auto_name: Auto-generated glyph-based name
            custom_name: User-provided custom name (overrides auto_name)
            glyphs_triggered: List of emotional glyphs detected

        Returns: (success: bool, message: str)
        """
        if not self.base_url or not self.supabase_key:
            return False, "Supabase not configured"

        if not requests:
            return False, "Requests library not available"

        try:
            # First, save/update conversation metadata in conversations table
            conv_url = f"{self.base_url}/rest/v1/conversations"
            conv_payload = {
                'user_id': self.user_id,
                'conversation_id': conversation_id,
                'title': title,
                'auto_name': auto_name or title,
                'custom_name': custom_name,
                'glyphs_triggered': glyphs_triggered or [],
                'processing_mode': processing_mode,
                'message_count': len(messages),
                'updated_at': datetime.now().isoformat(),
                'first_message': messages[0]['content'] if messages else None
            }

            # Upsert conversation metadata
            # Build headers and log masked debug info before calling the API
            headers = self._get_headers()
            try:
                logger.info("Saving conversation metadata to %s apikey=%s Authorization=%s",
                            conv_url, _mask_key(headers.get('apikey')), _mask_key(headers.get('Authorization')))
            except Exception:
                pass

            conv_response = requests.post(
                conv_url,
                headers=headers,
                json=[conv_payload],
                timeout=10
            )

            if conv_response.status_code not in (200, 201):
                error_detail = conv_response.text if conv_response.text else "No error detail"
                logger.error(
                    f"Failed to save conversation metadata: HTTP {conv_response.status_code}, {error_detail}")
                return False, f"Failed to save conversation metadata (HTTP {conv_response.status_code}): {error_detail}"

            # Then, save individual messages to conversation_messages table
            msg_url = f"{self.base_url}/rest/v1/conversation_messages"
            msg_payloads = []
            for msg in messages:
                msg_payload = {
                    'user_id': self.user_id,
                    'conversation_id': conversation_id,
                    'role': msg.get('role', ''),
                    'message': msg.get('content', ''),
                    'first_name': msg.get('first_name', None),
                    'timestamp': datetime.now().isoformat()
                }
                msg_payloads.append(msg_payload)

            if msg_payloads:
                # Masked debug logging to help trace which credentials are used
                try:
                    headers_msg = self._get_headers()
                    logger.info("Saving conversation messages to %s apikey=%s Authorization=%s",
                                msg_url, _mask_key(headers_msg.get('apikey')), _mask_key(headers_msg.get('Authorization')))
                except Exception:
                    pass

                msg_response = requests.post(
                    msg_url,
                    headers=headers_msg,
                    json=msg_payloads,
                    timeout=10
                )

                if msg_response.status_code not in (200, 201):
                    error_detail = msg_response.text if msg_response.text else "No error detail"
                    logger.error(
                        f"Failed to save messages: HTTP {msg_response.status_code}, {error_detail}")
                    return False, f"Failed to save messages (HTTP {msg_response.status_code}): {error_detail}"

            return True, "Conversation saved successfully"

        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return False, f"Error saving conversation: {str(e)}"

    def load_conversations(self) -> List[Dict]:
        """
        Load all conversations for the user from Supabase.

        Returns: List of conversations with id, title, updated_at, message_count, messages
        """
        if not self.base_url or not self.supabase_key:
            return []

        if not requests:
            return []

        try:
            # First, load conversation metadata
            conv_url = f"{self.base_url}/rest/v1/conversations"
            conv_params = {
                'select': 'conversation_id,title,auto_name,custom_name,glyphs_triggered,processing_mode,message_count,updated_at,created_at',
                'user_id': f'eq.{self.user_id}',
                'archived': 'eq.false',
                'order': 'updated_at.desc',
                'limit': '100'
            }

            conv_response = requests.get(
                conv_url,
                headers=self._get_headers(),
                params=conv_params,
                timeout=10
            )

            if conv_response.status_code != 200:
                return []

            conversations = conv_response.json()
            if not isinstance(conversations, list):
                return []

            # For each conversation, load its messages
            for conv in conversations:
                conv_id = conv['conversation_id']
                msg_url = f"{self.base_url}/rest/v1/conversation_messages"
                msg_params = {
                    'select': 'role,message,first_name,timestamp',
                    'conversation_id': f'eq.{conv_id}',
                    'user_id': f'eq.{self.user_id}',
                    'order': 'timestamp.asc'
                }

                msg_response = requests.get(
                    msg_url,
                    headers=self._get_headers(),
                    params=msg_params,
                    timeout=10
                )

                if msg_response.status_code == 200:
                    messages = msg_response.json()
                    # Convert to the expected format
                    conv['messages'] = [
                        {
                            'role': msg['role'],
                            'content': msg['message'],
                            'first_name': msg.get('first_name')
                        }
                        for msg in messages
                    ]
                else:
                    conv['messages'] = []

                # Ensure glyphs_triggered is a list
                if not isinstance(conv.get('glyphs_triggered'), list):
                    conv['glyphs_triggered'] = []

                # Backward compatibility shim: translate any legacy "ai_preferred"
                # processing_mode values into the new representation where
                # processing_mode='hybrid' and prefer_ai=True.
                pm = conv.get('processing_mode')
                if pm == 'ai_preferred':
                    conv['processing_mode'] = 'hybrid'
                    conv['prefer_ai'] = True

            return conversations

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
            # Load conversation metadata
            conv_url = f"{self.base_url}/rest/v1/conversations"
            conv_params = {
                'conversation_id': f'eq.{conversation_id}',
                'user_id': f'eq.{self.user_id}'
            }

            conv_response = requests.get(
                conv_url,
                headers=self._get_headers(),
                params=conv_params,
                timeout=10
            )

            if conv_response.status_code != 200:
                return None

            conversations = conv_response.json()
            if not conversations:
                return None

            conv = conversations[0]

            # Load messages for this conversation
            msg_url = f"{self.base_url}/rest/v1/conversation_messages"
            msg_params = {
                'select': 'role,message,first_name,timestamp',
                'conversation_id': f'eq.{conversation_id}',
                'user_id': f'eq.{self.user_id}',
                'order': 'timestamp.asc'
            }

            msg_response = requests.get(
                msg_url,
                headers=self._get_headers(),
                params=msg_params,
                timeout=10
            )

            if msg_response.status_code == 200:
                messages = msg_response.json()
                # Convert to expected format
                conv['messages'] = [
                    {
                        'role': msg['role'],
                        'content': msg['message'],
                        'first_name': msg.get('first_name')
                    }
                    for msg in messages
                ]
            else:
                conv['messages'] = []

            # Ensure glyphs_triggered is a list
            if not isinstance(conv.get('glyphs_triggered'), list):
                conv['glyphs_triggered'] = []

            # Parse messages if it's stored as JSON string (backward compatibility)
            # (Though now messages come from separate table, this is for legacy)
            if isinstance(conv.get('messages'), str):
                try:
                    conv['messages'] = json.loads(conv['messages'])
                except:
                    conv['messages'] = []
            elif not isinstance(conv.get('messages'), list):
                conv['messages'] = []

            # Backward compatibility: map legacy ai_preferred to hybrid+prefer_ai
            if conv.get('processing_mode') == 'ai_preferred':
                conv['processing_mode'] = 'hybrid'
                conv['prefer_ai'] = True

            return conv

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
            params = {
                'select': 'persist_history,persist_confirmed',
                'user_id': f'eq.{self.user_id}'
            }
            response = requests.get(
                url, headers=self._get_headers(), params=params, timeout=6)
            if response.status_code == 200:
                rows = response.json()
                if rows and isinstance(rows, list) and len(rows) > 0:
                    row = rows[0]
                    prefs = {
                        'persist_history': bool(row.get('persist_history', False)),
                        'persist_confirmed': bool(row.get('persist_confirmed', False))
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
                'user_id': self.user_id,
                'persist_history': bool(prefs.get('persist_history', False)),
                'persist_confirmed': bool(prefs.get('persist_confirmed', False)),
                'updated_at': datetime.now().isoformat()
            }

            # Use upsert semantics: POST a single-item list. Supabase needs
            # appropriate DB constraints to upsert; this is best-effort.
            response = requests.post(
                url, headers=self._get_headers(), json=[payload], timeout=6)
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
            params = {
                'conversation_id': f'eq.{conversation_id}',
                'user_id': f'eq.{self.user_id}'
            }

            response = requests.delete(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=10
            )

            if response.status_code in (200, 204):
                return True, "Conversation deleted successfully"
            else:
                return False, f"Failed to delete conversation (HTTP {response.status_code})"

        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False, f"Error deleting conversation: {str(e)}"

    def rename_conversation(self, conversation_id: str, new_title: str) -> Tuple[bool, str]:
        """Rename a conversation by setting custom_name (overrides auto_name)."""
        if not self.base_url or not self.supabase_key:
            return False, "Supabase not configured"

        if not requests:
            return False, "Requests library not available"

        try:
            url = f"{self.base_url}/rest/v1/conversations"
            params = {
                'conversation_id': f'eq.{conversation_id}',
                'user_id': f'eq.{self.user_id}'
            }

            payload = {
                'custom_name': new_title,  # Set custom name
                'title': new_title,  # Keep title updated for backward compatibility
                'updated_at': datetime.now().isoformat()
            }

            response = requests.patch(
                url,
                headers=self._get_headers(),
                json=payload,
                params=params,
                timeout=10
            )

            if response.status_code in (200, 204):
                return True, "Conversation renamed successfully"
            else:
                return False, f"Failed to rename conversation (HTTP {response.status_code})"

        except Exception as e:
            logger.error(f"Error renaming conversation: {e}")
            return False, f"Error renaming conversation: {str(e)}"


def initialize_conversation_manager() -> Optional[ConversationManager]:
    """Initialize conversation manager from session state."""
    if 'user_id' not in st.session_state:
        return None

    return ConversationManager(st.session_state.user_id)


def load_all_conversations_to_sidebar(manager: ConversationManager) -> None:
    """Display all user's previous conversations in sidebar."""
    if not manager:
        return

    conversations = manager.load_conversations()

    if not conversations:
        st.sidebar.info("No previous conversations yet. Start a new one!")
        return

    st.sidebar.markdown("### 📚 Previous Conversations")

    # Optional: Time-based filtering
    if len(conversations) > 5:  # Only show filter if there are many conversations
        from datetime import datetime, timedelta

        filter_options = [
            "All conversations",
            "Last 7 days",
            "Last 30 days",
            "Last 3 months"
        ]

        time_filter = st.sidebar.selectbox(
            "📅 Filter by time:",
            filter_options,
            key="conversation_time_filter"
        )

        if time_filter != "All conversations":
            now = datetime.now()
            if time_filter == "Last 7 days":
                cutoff = now - timedelta(days=7)
            elif time_filter == "Last 30 days":
                cutoff = now - timedelta(days=30)
            elif time_filter == "Last 3 months":
                cutoff = now - timedelta(days=90)

            # Filter conversations by created_at or updated_at
            filtered_conversations = []
            for conv in conversations:
                try:
                    # Try updated_at first, then created_at
                    date_str = conv.get('updated_at') or conv.get('created_at')
                    if date_str:
                        # Parse ISO format date
                        conv_date = datetime.fromisoformat(
                            date_str.replace('Z', '+00:00'))
                        if conv_date >= cutoff:
                            filtered_conversations.append(conv)
                except Exception:
                    # Include conversations with unparseable dates
                    filtered_conversations.append(conv)

            conversations = filtered_conversations

            if not conversations:
                st.sidebar.info(
                    f"No conversations found in {time_filter.lower()}.")
                return

    for conv in conversations:
        col1, col2, col3 = st.sidebar.columns([3, 1, 1])

        # Determine display name: custom_name if present, else auto_name, else title
        display_name = (
            conv.get('custom_name') or
            conv.get('auto_name') or
            conv.get('title', 'Untitled Conversation')
        )

        with col1:
            # Click to load conversation
            if st.button(
                f"💬 {display_name}",
                key=f"load_conv_{conv['conversation_id']}",
                use_container_width=True
            ):
                st.session_state['selected_conversation'] = conv['conversation_id']
                st.session_state['conversation_title'] = display_name
                st.rerun()

        with col2:
            # Rename button
            if st.button("✏️", key=f"rename_{conv['conversation_id']}", help="Rename"):
                st.session_state[f"renaming_{conv['conversation_id']}"] = True
                st.rerun()

        with col3:
            # Delete button
            if st.button("🗑️", key=f"delete_{conv['conversation_id']}", help="Delete"):
                success, message = manager.delete_conversation(
                    conv['conversation_id'])
                if success:
                    st.sidebar.success(message)
                    st.rerun()
                else:
                    st.sidebar.error(message)

        # Handle rename dialog
        if st.session_state.get(f"renaming_{conv['conversation_id']}", False):
            new_title = st.sidebar.text_input(
                "New title:",
                value=display_name,
                key=f"rename_input_{conv['conversation_id']}"
            )
            col_a, col_b = st.sidebar.columns(2)
            with col_a:
                if st.button("Save", key=f"save_rename_{conv['conversation_id']}"):
                    success, message = manager.rename_conversation(
                        conv['conversation_id'], new_title or "Untitled Conversation")
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
