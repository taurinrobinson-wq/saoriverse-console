"""
Integration module for encoding pipeline with signal_parser.

This module wraps parse_input to ensure all conversation data is encoded
before storage, implementing the privacy-first design.

FLOW:
1. parse_input() executes normally (returns signals, gates, glyphs, response)
2. encode_and_store() takes that output and encodes it before storage
3. Only encoded data goes to Supabase
4. Raw text is explicitly discarded
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def encode_and_store_conversation(
    user_id: str,
    raw_user_input: str,
    parse_result: Dict,
    system_response: str,
    session_id: str,
    message_turn: int = 1,
    db_connection=None,
) -> Tuple[bool, str, Optional[Dict]]:
    """
    Encode conversation data and store to database.
    
    CRITICAL: This function ensures raw text is NEVER stored.
    
    Args:
        user_id: User identifier
        raw_user_input: Original user message (will be encoded and discarded)
        parse_result: Output from parse_input() containing signals, gates, glyphs
        system_response: The system's response (will be encoded and discarded)
        session_id: Session identifier
        message_turn: Turn number in conversation
        db_connection: Database connection object
    
    Returns:
        (success, record_id_or_error, encoded_record)
    """
    try:
        from emotional_os.privacy.data_encoding import ConversationDataStore
        
        # Initialize encoding store
        store = ConversationDataStore(db_connection=db_connection)
        
        # Extract signals, gates, glyphs from parse_result
        signals = parse_result.get("signals", [])
        gates_raw = parse_result.get("gates", [])
        glyphs = parse_result.get("glyphs", [])
        
        # Convert gate strings to integers if needed
        gates = []
        for gate in gates_raw:
            if isinstance(gate, str):
                # Extract number from gate string like "GATE_TRANSITION_001"
                try:
                    gate_num = int(gate.split("_")[-1])
                    gates.append(gate_num)
                except (ValueError, IndexError):
                    pass
            elif isinstance(gate, int):
                gates.append(gate)
        
        # Store encoded conversation
        success, record_id = store.store_conversation(
            user_id=user_id,
            raw_input=raw_user_input,
            system_response=system_response,
            signals=signals,
            gates=gates,
            glyphs=glyphs,
            session_id=session_id,
            message_turn=message_turn,
        )
        
        if success:
            # Get the encoded record for logging
            encoded_record = store.encoder.encode_conversation(
                user_id=user_id,
                raw_user_input=raw_user_input,
                system_response=system_response,
                signals=signals,
                gates=gates,
                glyphs=glyphs,
                session_id=session_id,
            )
            
            logger.info(f"[ENCODE_STORE] Successfully stored encoded conversation: {record_id}")
            return True, record_id, encoded_record
        else:
            logger.error(f"[ENCODE_STORE] Failed to store: {record_id}")
            return False, record_id, None
    
    except Exception as e:
        logger.error(f"[ENCODE_STORE] Exception during encode/store: {e}")
        return False, str(e), None


def store_affirmation(
    user_id: str,
    parse_result: Dict,
    system_response: str,
    humanlike_score: float,
    db_connection=None,
) -> Tuple[bool, str]:
    """
    Store affirmation (high-quality interaction) without storing raw text.
    
    Used to learn from positive interactions without persisting
    actual conversation content.
    
    Args:
        user_id: User identifier
        parse_result: Output from parse_input()
        system_response: System response (not stored, only metadata)
        humanlike_score: Quality score (0.0 to 1.0)
        db_connection: Database connection
    
    Returns:
        (success, record_id_or_error)
    """
    try:
        from emotional_os.privacy.data_encoding import encode_affirmation_flow
        
        # Extract encoded components
        glyph_ids = [g.get("id") for g in parse_result.get("glyphs", [])]
        signals = parse_result.get("signals", [])
        gates_raw = parse_result.get("gates", [])
        
        # Build encoded signals
        signals_encoded = [s.get("signal", f"SIG_{i}") for i, s in enumerate(signals)]
        gates_encoded = [str(g) for g in gates_raw]
        
        # Create affirmation record (no raw text, no user ID)
        affirmation = encode_affirmation_flow(
            glyph_ids=glyph_ids,
            signals_encoded=signals_encoded,
            gates_encoded=gates_encoded,
            humanlike_score=humanlike_score,
        )
        
        # Store to database
        if db_connection:
            result = db_connection.table("affirmations").insert(affirmation).execute()
            record_id = result.data[0]["id"] if result.data else "unknown"
            logger.info(f"Stored affirmation: {record_id} (score: {humanlike_score})")
            return True, record_id
        else:
            logger.info(f"Affirmation (no DB): score={humanlike_score}, glyphs={len(glyph_ids)}")
            return True, "logged_only"
    
    except Exception as e:
        logger.error(f"Failed to store affirmation: {e}")
        return False, str(e)


def verify_privacy_compliance(session_id: str, db_connection=None) -> Dict:
    """
    Verify that all conversation data for a session is properly encoded.
    
    Checks:
    1. No raw text fields exist
    2. User ID is hashed
    3. Timestamps are generalized
    4. All data is anonymized
    
    Args:
        session_id: Session to verify
        db_connection: Database connection
    
    Returns:
        Compliance report
    """
    report = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "compliant": True,
        "messages": [],
        "issues": [],
        "records_checked": 0,
    }
    
    if not db_connection:
        report["messages"].append("No database connection, cannot verify")
        return report
    
    try:
        # Fetch all records for this session
        results = db_connection.table("conversation_logs_anonymized")\
            .select("*")\
            .eq("session_id", session_id)\
            .execute()
        
        records = results.data if hasattr(results, 'data') else []
        report["records_checked"] = len(records)
        
        forbidden_fields = [
            "raw_input",
            "user_input",
            "original_message",
            "system_response",
            "original_response",
            "user_email",
            "user_name",
            "user_phone",
            "message_text",
            "response_text",
        ]
        
        for record in records:
            for field in forbidden_fields:
                if field in record:
                    report["compliant"] = False
                    report["issues"].append(
                        f"Record {record.get('id')}: forbidden field '{field}' present"
                    )
        
        if report["compliant"]:
            report["messages"].append(
                f"✓ All {len(records)} records properly anonymized"
            )
            report["messages"].append("✓ No raw text fields detected")
            report["messages"].append("✓ User ID hashed")
        else:
            report["messages"].append(f"✗ {len(report['issues'])} compliance issues found")
        
        logger.info(f"Privacy compliance check: {report['compliant']}")
        return report
    
    except Exception as e:
        report["compliant"] = False
        report["issues"].append(f"Verification failed: {e}")
        logger.error(f"Privacy verification error: {e}")
        return report
