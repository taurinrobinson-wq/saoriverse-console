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
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

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
        self.supabase_url = supabase_url or st.secrets.get("supabase", {}).get("url")
        self.supabase_key = supabase_key or st.secrets.get("supabase", {}).get("key")
        self.base_url = self._normalize_supabase_url(self.supabase_url) if self.supabase_url else None
    
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
        return {
            'Content-Type': 'application/json',
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Prefer': 'return=representation'
        }
    
    def save_conversation(self, conversation_id: str, title: str, messages: List[Dict], 
                         processing_mode: str = "hybrid") -> Tuple[bool, str]:
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
                'user_id': self.user_id,
                'conversation_id': conversation_id,
                'title': title,
                'messages': json.dumps(messages),
                'processing_mode': processing_mode,
                'updated_at': datetime.now().isoformat(),
                'message_count': len(messages)
            }
            
            # Upsert: insert if new, update if exists
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=[payload],
                timeout=10
            )
            
            if response.status_code in (200, 201):
                return True, "Conversation saved successfully"
            else:
                return False, f"Failed to save conversation (HTTP {response.status_code})"
        
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
                'select': 'conversation_id,title,updated_at,message_count,processing_mode',
                'user_id': f'eq.{self.user_id}',
                'order': 'updated_at.desc',
                'limit': '100'
            }
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                conversations = response.json()
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
            params = {
                'conversation_id': f'eq.{conversation_id}',
                'user_id': f'eq.{self.user_id}'
            }
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                conversations = response.json()
                if conversations:
                    conv = conversations[0]
                    # Parse messages JSON string
                    if isinstance(conv.get('messages'), str):
                        conv['messages'] = json.loads(conv['messages'])
                    return conv
            return None
        
        except Exception as e:
            logger.debug(f"Error loading conversation: {e}")
            return None
    
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
        """Rename a conversation."""
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
                'title': new_title,
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
    
    for conv in conversations:
        col1, col2, col3 = st.sidebar.columns([3, 1, 1])
        
        with col1:
            # Click to load conversation
            if st.button(
                f"💬 {conv['title']}",
                key=f"load_conv_{conv['conversation_id']}",
                use_container_width=True
            ):
                st.session_state['selected_conversation'] = conv['conversation_id']
                st.session_state['conversation_title'] = conv['title']
                st.rerun()
        
        with col2:
            # Rename button
            if st.button("✏️", key=f"rename_{conv['conversation_id']}", help="Rename"):
                st.session_state[f"renaming_{conv['conversation_id']}"] = True
                st.rerun()
        
        with col3:
            # Delete button
            if st.button("🗑️", key=f"delete_{conv['conversation_id']}", help="Delete"):
                success, message = manager.delete_conversation(conv['conversation_id'])
                if success:
                    st.sidebar.success(message)
                    st.rerun()
                else:
                    st.sidebar.error(message)
        
        # Handle rename dialog
        if st.session_state.get(f"renaming_{conv['conversation_id']}", False):
            new_title = st.sidebar.text_input(
                "New title:",
                value=conv['title'],
                key=f"rename_input_{conv['conversation_id']}"
            )
            col_a, col_b = st.sidebar.columns(2)
            with col_a:
                if st.button("Save", key=f"save_rename_{conv['conversation_id']}"):
                    success, message = manager.rename_conversation(conv['conversation_id'], new_title)
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
