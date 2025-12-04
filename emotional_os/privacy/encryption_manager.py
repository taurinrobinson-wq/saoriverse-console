"""
Encryption Manager - Handle AES-256 encryption/decryption for user data

All sensitive data (conversations, profiles) encrypted at rest with AES-256.
Decrypted in memory only when needed after authentication.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
from datetime import datetime

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Manage AES-256 encryption for user data.
    
    Each user has their own encryption key derived from their password.
    Data encrypted: conversations, profile, preferences
    Data not encrypted: user_id_hashed (needed for queries), timestamps
    """
    
    def __init__(self, salt: str = "firstperson_encryption_salt_v1"):
        self.salt = salt.encode('utf-8')
    
    def derive_key_from_password(self, user_id: str, password: str) -> bytes:
        """
        Derive encryption key from user's password.
        
        Args:
            user_id: User identifier (for uniqueness)
            password: User's password
        
        Returns:
            Encryption key (bytes)
        """
        # Combine salt with user_id for per-user uniqueness
        combined_salt = self.salt + user_id.encode('utf-8')
        
        # PBKDF2 to derive key from password
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 32 bytes = 256 bits
            salt=combined_salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
        return key
    
    def encrypt_data(self, data: Dict[str, Any], encryption_key: bytes) -> str:
        """
        Encrypt data to encrypted blob.
        
        Args:
            data: Dictionary to encrypt (will be JSON serialized)
            encryption_key: Encryption key from derive_key_from_password()
        
        Returns:
            Encrypted blob (base64 encoded string)
        """
        try:
            fernet = Fernet(encryption_key)
            json_data = json.dumps(data)
            encrypted = fernet.encrypt(json_data.encode('utf-8'))
            return encrypted.decode('utf-8')  # Return as string for storage
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_blob: str, encryption_key: bytes) -> Dict[str, Any]:
        """
        Decrypt encrypted blob back to data.
        
        Args:
            encrypted_blob: Encrypted blob (from encrypt_data)
            encryption_key: Encryption key from derive_key_from_password()
        
        Returns:
            Decrypted dictionary
        """
        try:
            fernet = Fernet(encryption_key)
            decrypted = fernet.decrypt(encrypted_blob.encode('utf-8'))
            data = json.loads(decrypted.decode('utf-8'))
            return data
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_conversation(
        self,
        user_id: str,
        password: str,
        conversation_data: Dict[str, Any]
    ) -> Tuple[str, str]:
        """
        Encrypt a conversation for storage.
        
        Args:
            user_id: User identifier
            password: User's password (for key derivation)
            conversation_data: Conversation to encrypt
        
        Returns:
            (encrypted_blob, user_id_hashed) tuple
        """
        key = self.derive_key_from_password(user_id, password)
        encrypted = self.encrypt_data(conversation_data, key)
        user_id_hashed = self._hash_user_id(user_id)
        return encrypted, user_id_hashed
    
    def decrypt_conversation(
        self,
        user_id: str,
        password: str,
        encrypted_blob: str
    ) -> Dict[str, Any]:
        """
        Decrypt a stored conversation.
        
        Args:
            user_id: User identifier
            password: User's password
            encrypted_blob: Encrypted conversation blob
        
        Returns:
            Decrypted conversation dictionary
        """
        key = self.derive_key_from_password(user_id, password)
        return self.decrypt_data(encrypted_blob, key)
    
    def encrypt_user_profile(
        self,
        user_id: str,
        password: str,
        profile: Dict[str, Any]
    ) -> str:
        """Encrypt user profile (name, email, preferences)."""
        key = self.derive_key_from_password(user_id, password)
        return self.encrypt_data(profile, key)
    
    def decrypt_user_profile(
        self,
        user_id: str,
        password: str,
        encrypted_profile: str
    ) -> Dict[str, Any]:
        """Decrypt user profile."""
        key = self.derive_key_from_password(user_id, password)
        return self.decrypt_data(encrypted_profile, key)
    
    @staticmethod
    def _hash_user_id(user_id: str) -> str:
        """Hash user ID for database queries (one-way, irreversible)."""
        import hashlib
        return hashlib.sha256(user_id.encode('utf-8')).hexdigest()


class ConversationEncryptionLayer:
    """
    Handle encrypted storage and retrieval of conversations.
    """
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.encryption = EncryptionManager()
    
    def store_encrypted_conversation(
        self,
        user_id: str,
        password: str,
        conversation: Dict[str, Any],
        session_id: str,
        retention_days: int = 30
    ) -> Tuple[bool, str]:
        """
        Store encrypted conversation.
        
        Args:
            user_id: User identifier
            password: User password (for key derivation)
            conversation: Full conversation data
            session_id: Session identifier
            retention_days: How long to keep this conversation
        
        Returns:
            (success, record_id_or_error)
        """
        try:
            # Encrypt the conversation
            encrypted_blob, user_id_hashed = self.encryption.encrypt_conversation(
                user_id, password, conversation
            )
            
            # Calculate expiration
            from datetime import datetime, timedelta
            created_at = datetime.now()
            expires_at = created_at + timedelta(days=retention_days)
            
            # Store to database
            if self.db:
                record = {
                    "user_id_hashed": user_id_hashed,
                    "session_id": session_id,
                    "encrypted_content": encrypted_blob,
                    "created_at": created_at.isoformat(),
                    "expires_at": expires_at.isoformat(),
                    "retention_days": retention_days,
                }
                
                result = self.db.table("conversations_encrypted").insert(record).execute()
                record_id = result.data[0]["id"] if result.data else "unknown"
                
                logger.info(f"Stored encrypted conversation: {record_id}")
                return True, record_id
            else:
                logger.warning("No database connection, logging only")
                return True, "logged_only"
        
        except Exception as e:
            logger.error(f"Failed to store encrypted conversation: {e}")
            return False, str(e)
    
    def retrieve_encrypted_conversation(
        self,
        user_id: str,
        password: str,
        conversation_id: str
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Retrieve and decrypt a conversation.
        
        Args:
            user_id: User identifier
            password: User password (for decryption)
            conversation_id: Conversation ID
        
        Returns:
            (success, decrypted_conversation_or_none)
        """
        try:
            if not self.db:
                logger.warning("No database connection")
                return False, None
            
            # Fetch encrypted blob
            result = self.db.table("conversations_encrypted")\
                .select("encrypted_content")\
                .eq("id", conversation_id)\
                .single()\
                .execute()
            
            if not result.data:
                return False, None
            
            encrypted_blob = result.data[0]["encrypted_content"]
            
            # Decrypt
            decrypted = self.encryption.decrypt_conversation(
                user_id, password, encrypted_blob
            )
            
            return True, decrypted
        
        except Exception as e:
            logger.error(f"Failed to retrieve conversation: {e}")
            return False, None
    
    def get_user_recent_conversations(
        self,
        user_id: str,
        password: str,
        limit: int = 20
    ) -> list:
        """
        Get recent conversations (without decrypting - just metadata).
        
        Metadata is useful for showing conversation list without
        decrypting everything.
        
        Args:
            user_id: User identifier
            password: User password
            limit: Max conversations to return
        
        Returns:
            List of conversation metadata (encrypted_content not included)
        """
        try:
            if not self.db:
                return []
            
            user_id_hashed = EncryptionManager._hash_user_id(user_id)
            
            results = self.db.table("conversations_encrypted")\
                .select("id, session_id, created_at, expires_at, retention_days")\
                .eq("user_id_hashed", user_id_hashed)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return results.data if results.data else []
        
        except Exception as e:
            logger.error(f"Failed to get recent conversations: {e}")
            return []
    
    def delete_user_conversations(
        self,
        user_id: str
    ) -> Tuple[bool, str]:
        """
        Delete all conversations for a user (GDPR right to be forgotten).
        
        Args:
            user_id: User identifier
        
        Returns:
            (success, message)
        """
        try:
            if not self.db:
                return False, "No database connection"
            
            user_id_hashed = EncryptionManager._hash_user_id(user_id)
            
            # Delete all conversations
            self.db.table("conversations_encrypted")\
                .delete()\
                .eq("user_id_hashed", user_id_hashed)\
                .execute()
            
            # Log deletion for audit
            self.db.table("deletion_audit")\
                .insert({
                    "user_id_hashed": user_id_hashed,
                    "deleted_at": datetime.now().isoformat(),
                    "reason": "User requested deletion (GDPR)",
                })\
                .execute()
            
            logger.info(f"Deleted all conversations for user: {user_id_hashed}")
            return True, "All conversations deleted"
        
        except Exception as e:
            logger.error(f"Failed to delete conversations: {e}")
            return False, str(e)
    
    def cleanup_expired_conversations(self) -> int:
        """
        Delete conversations past their retention date.
        Should run daily.
        
        Returns:
            Number of conversations deleted
        """
        try:
            if not self.db:
                return 0
            
            # Find and delete expired
            result = self.db.table("conversations_encrypted")\
                .delete()\
                .lt("expires_at", datetime.now().isoformat())\
                .execute()
            
            count = len(result.data) if result.data else 0
            logger.info(f"Cleaned up {count} expired conversations")
            return count
        
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0


def get_encryption_manager() -> EncryptionManager:
    """Factory function."""
    return EncryptionManager()


def get_conversation_encryption_layer(db_connection=None) -> ConversationEncryptionLayer:
    """Factory function."""
    return ConversationEncryptionLayer(db_connection)
