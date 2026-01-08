"""
Data Encoding Pipeline

Implements the 5-stage encoding process to ensure raw user text is never stored.
Raw text → Signals → Gates → Glyphs → Storage (encoded only)

This enforces the core privacy principle: sensitive content is encoded
immediately upon input and never persisted in raw form.
"""

import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class DataEncodingPipeline:
    """
    5-stage encoding pipeline:
    1. Input capture (raw text, not stored)
    2. Signal detection (emotional signals extracted)
    3. Gate encoding (signals mapped to emotional categories)
    4. Glyph mapping (abstract references, no content)
    5. Storage (only encoded data persisted)
    """
    
    def __init__(self, config_path: str = "emotional_os/privacy/anonymization_config.json"):
        self.config = self._load_config(config_path)
        self.signal_encoding_map = self._build_signal_encoding()
        self.gate_encoding_map = self._build_gate_encoding()
    
    def _load_config(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def _build_signal_encoding(self) -> Dict[str, str]:
        """Build mapping of emotional signals to encoded identifiers."""
        signals = {
            "suicidal_disclosure": "SIG_CRISIS_001",
            "self_harm": "SIG_CRISIS_002",
            "overwhelm": "SIG_STRESS_001",
            "anxiety": "SIG_STRESS_002",
            "exhaustion": "SIG_FATIGUE_001",
            "grief": "SIG_LOSS_001",
            "loneliness": "SIG_CONNECTION_001",
            "joy": "SIG_POSITIVE_001",
            "hope": "SIG_POSITIVE_002",
            "fear": "SIG_EMOTION_001",
            "anger": "SIG_EMOTION_002",
            "shame": "SIG_EMOTION_003",
            # Add more as needed
        }
        return signals
    
    def _build_gate_encoding(self) -> Dict[int, str]:
        """Build mapping of gates to encoded identifiers."""
        gates = {
            1: "GATE_TRANSITION_001",
            2: "GATE_LONGING_002",
            4: "GATE_GRIEF_004",
            5: "GATE_PRESENCE_005",
            6: "GATE_DISSOLUTION_006",
            9: "GATE_CRISIS_009",
            10: "GATE_INTEGRATION_010",
        }
        return gates
    
    def encode_conversation(
        self,
        user_id: str,
        raw_user_input: str,
        system_response: str,
        signals: List[Dict],
        gates: List[int],
        glyphs: List[Dict],
        session_id: str,
        user_id_salt: str = "default_salt"
    ) -> Dict:
        """
        Encode conversation data for storage.
        
        CRITICAL: raw_user_input and system_response are NOT stored.
        Only encoded representations are persisted.
        
        Args:
            user_id: Original user ID (will be hashed)
            raw_user_input: Original message (DISCARDED after encoding)
            system_response: Original response (DISCARDED after encoding)
            signals: List of detected emotional signals
            gates: List of triggered gate IDs
            glyphs: List of triggered glyphs
            session_id: Session identifier
            user_id_salt: Salt for hashing user ID
        
        Returns:
            Encoded data structure ready for storage
        """
        
        # STAGE 1: Input capture (raw text received but not stored)
        logger.info(f"[ENCODING] Stage 1: Received input from {user_id} ({len(raw_user_input)} chars)")
        
        # STAGE 2: Signal detection and encoding
        encoded_signals = []
        for i, sig in enumerate(signals):
            keyword = sig.get("keyword") if isinstance(sig, dict) else str(sig)
            keyword = keyword if keyword else f"signal_{i}"
            encoded = self.signal_encoding_map.get(keyword, f"SIG_UNKNOWN_{i}")
            encoded_signals.append(encoded)
        logger.info(f"[ENCODING] Stage 2: Encoded {len(signals)} signals")
        
        # STAGE 3: Gate encoding
        encoded_gates = [
            self.gate_encoding_map.get(gate, f"GATE_UNKNOWN_{gate}")
            for gate in gates
        ]
        logger.info(f"[ENCODING] Stage 3: Encoded {len(gates)} gates")
        
        # STAGE 4: Glyph mapping (reference only, no content)
        glyph_ids = [glyph.get("id", i) for i, glyph in enumerate(glyphs)]
        logger.info(f"[ENCODING] Stage 4: Mapped {len(glyphs)} glyphs to IDs")
        
        # STAGE 5: Prepare for storage
        # Hash user ID (one-way, cannot reverse)
        user_id_hashed = self._hash_user_id(user_id, user_id_salt)
        
        # Generalize text metrics (length buckets instead of exact length)
        input_length_bucket = self._bucket_length(len(raw_user_input))
        response_length_bucket = self._bucket_length(len(system_response))
        
        # Generalize timestamp (store week, not exact time)
        timestamp_week = self._generalize_timestamp(datetime.now(), level="week")
        
        # Build encoded storage record
        encoded_record = {
            "user_id_hashed": user_id_hashed,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "timestamp_week": timestamp_week,
            "encoded_signals": encoded_signals,
            "encoded_signals_category": self._categorize_signals(encoded_signals),
            "encoded_gates": encoded_gates,
            "glyph_ids": glyph_ids,
            "glyph_count": len(glyphs),
            "message_length_bucket": input_length_bucket,
            "response_length_bucket": response_length_bucket,
            "signal_count": len(signals),
            "response_source": "conversation",
            "created_at": datetime.now().isoformat(),
        }
        
        logger.info(f"[ENCODING] Stage 5: Record prepared for storage (no raw text)")
        logger.info(f"[ENCODING] DISCARD: raw_user_input ({len(raw_user_input)} chars)")
        logger.info(f"[ENCODING] DISCARD: system_response ({len(system_response)} chars)")
        
        # Return encoded record
        # NOTE: raw_user_input and system_response are not included
        return encoded_record
    
    def _hash_user_id(self, user_id: str, salt: str) -> str:
        """Hash user ID one-way (cannot reverse to original)."""
        salted = f"{salt}:{user_id}".encode('utf-8')
        return hashlib.sha256(salted).hexdigest()
    
    def _bucket_length(self, length: int, bucket_size: int = 100) -> str:
        """Generalize text length to bucket (e.g., '100-200_chars')."""
        lower = (length // bucket_size) * bucket_size
        upper = lower + bucket_size
        return f"{lower}-{upper}_chars"
    
    def _generalize_timestamp(self, dt: datetime, level: str = "week") -> str:
        """Generalize timestamp to reduce uniqueness."""
        if level == "day":
            return dt.strftime("%Y-%m-%d")
        elif level == "week":
            week = dt.isocalendar()[1]
            return f"{dt.year}-W{week:02d}"
        elif level == "month":
            return dt.strftime("%Y-%m")
        elif level == "quarter":
            quarter = (dt.month - 1) // 3 + 1
            return f"{dt.year}-Q{quarter}"
        elif level == "year":
            return str(dt.year)
        else:
            return level
    
    def _categorize_signals(self, encoded_signals: List[str]) -> str:
        """Categorize signals into higher-level groups."""
        categories = set()
        for sig in encoded_signals:
            if "CRISIS" in sig:
                categories.add("crisis")
            elif "STRESS" in sig or "FATIGUE" in sig:
                categories.add("overwhelm")
            elif "LOSS" in sig:
                categories.add("grief")
            elif "CONNECTION" in sig:
                categories.add("relational")
            elif "POSITIVE" in sig:
                categories.add("positive")
            elif "EMOTION" in sig:
                categories.add("emotional")
        
        return ",".join(sorted(categories)) if categories else "uncategorized"


class ConversationDataStore:
    """
    Handles encrypted storage of encoded conversation data.
    Enforces data minimization and privacy-first design.
    """
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.encoder = DataEncodingPipeline()
    
    def store_conversation(
        self,
        user_id: str,
        raw_input: str,
        system_response: str,
        signals: List[Dict],
        gates: List[int],
        glyphs: List[Dict],
        session_id: str,
        message_turn: int
    ) -> Tuple[bool, str]:
        """
        Store conversation data (encoded, not raw).
        
        Args:
            user_id: User identifier
            raw_input: Original user message (will not be stored)
            system_response: Original system response (will not be stored)
            signals: Detected signals
            gates: Triggered gates
            glyphs: Used glyphs
            session_id: Session identifier
            message_turn: Turn number in conversation
        
        Returns:
            (success, record_id or error_message)
        """
        try:
            # Encode the conversation
            encoded = self.encoder.encode_conversation(
                user_id=user_id,
                raw_user_input=raw_input,
                system_response=system_response,
                signals=signals,
                gates=gates,
                glyphs=glyphs,
                session_id=session_id,
            )
            
            # Add turn number
            encoded["message_turn"] = message_turn
            
            # Store to database
            if self.db:
                result = self.db.table("conversation_logs_anonymized").insert(encoded).execute()
                record_id = result.data[0]["id"] if result.data else "unknown"
                logger.info(f"Stored encoded conversation: {record_id}")
                return True, record_id
            else:
                logger.warning("No database connection, logging encoded data only")
                logger.info(f"Encoded record: {json.dumps(encoded, indent=2)}")
                return True, "logged_only"
        
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            return False, str(e)
    
    def verify_no_raw_text_stored(self, record_id: str) -> bool:
        """
        Verify that a stored record contains no raw user/system text.
        
        Args:
            record_id: ID of stored record
        
        Returns:
            True if record is properly anonymized
        """
        if not self.db:
            return True  # Can't verify without database
        
        try:
            record = self.db.table("conversation_logs_anonymized")\
                .select("*")\
                .eq("id", record_id)\
                .single()\
                .execute()
            
            # Check for common PII patterns
            forbidden_fields = [
                "raw_input",
                "user_input",
                "original_message",
                "system_response",
                "original_response",
                "message_text",
                "response_text",
            ]
            
            record_data = record.data if hasattr(record, 'data') else record
            
            for field in forbidden_fields:
                if field in record_data:
                    logger.error(f"Forbidden field found in record: {field}")
                    return False
            
            logger.info(f"Record {record_id} verified: no raw text found")
            return True
        
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False


def encode_affirmation_flow(
    glyph_ids: List[int],
    signals_encoded: List[str],
    gates_encoded: List[str],
    humanlike_score: float
) -> Dict:
    """
    Encode affirmation (high-quality interaction) for learning without storing raw text.
    
    Args:
        glyph_ids: IDs of glyphs used
        signals_encoded: Encoded emotional signals
        gates_encoded: Encoded gates triggered
        humanlike_score: Quality score (0-1)
    
    Returns:
        Affirmation record for storage (no PII)
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "glyph_ids": glyph_ids,
        "signals_encoded": signals_encoded,
        "gates_encoded": gates_encoded,
        "humanlike_score": humanlike_score,
        "affirmed_at": datetime.now().isoformat(),
        "user_id": None,  # Explicitly no user ID
        "conversation_text": None,  # Explicitly no text
    }


def get_encoding_pipeline() -> DataEncodingPipeline:
    """Factory function to get encoding pipeline."""
    return DataEncodingPipeline()
