"""
Dream Engine - Summarize conversations into long-term patterns

Each day, the Dream Engine creates a summary of that day's conversations.
This summary is kept longer than full conversations and used for pattern recognition
and long-term context without loading months of data.

Like human memory: you don't recall exact words from 3 months ago,
but you remember themes, patterns, and key concerns.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DreamEngine:
    """
    Create daily summaries of emotional patterns, themes, and insights.
    
    Stores lightweight summaries that can be kept longer than full conversations.
    """
    
    def __init__(self):
        self.emotional_keywords = {
            "anxiety": ["anxious", "worried", "nervous", "afraid", "scared"],
            "overwhelm": ["overwhelmed", "stressed", "pressure", "too much"],
            "grief": ["loss", "sad", "mourning", "miss", "painful"],
            "joy": ["happy", "grateful", "loved", "peaceful", "hope"],
            "anger": ["angry", "frustrated", "rage", "irritated"],
            "exhaustion": ["tired", "exhausted", "drained", "fatigue", "burnout"],
            "loneliness": ["alone", "isolated", "lonely", "disconnected"],
            "shame": ["ashamed", "embarrassed", "guilty", "worthless"],
        }
    
    def create_daily_summary(
        self,
        user_id: str,
        date: str,
        conversations: List[Dict[str, Any]],
        glyph_effectiveness: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a daily summary from conversations.
        
        Args:
            user_id: User identifier
            date: Date (YYYY-MM-DD format)
            conversations: List of conversations from that day
            glyph_effectiveness: Optional pre-calculated glyph effectiveness
        
        Returns:
            Daily summary dictionary
        """
        summary = {
            "date": date,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            
            # Emotional state
            "primary_emotions": self._extract_emotions(conversations, top_n=3),
            "secondary_emotions": self._extract_emotions(conversations, top_n=2, skip_primary=True),
            
            # Themes and concerns
            "key_themes": self._extract_themes(conversations),
            "recurring_concerns": self._identify_recurring_concerns(conversations),
            "user_stated_needs": self._extract_stated_needs(conversations),
            
            # Glyph effectiveness
            "glyph_effectiveness": glyph_effectiveness or self._calculate_glyph_effectiveness(conversations),
            "most_effective_glyphs": self._rank_glyphs(glyph_effectiveness or {}),
            
            # Session metrics
            "session_count": len(conversations),
            "total_messages": sum(len(c.get("messages", [])) for c in conversations),
            "engagement_level": self._calculate_engagement(conversations),
            
            # Risk indicators
            "crisis_flags": self._detect_crisis_flags(conversations),
            "concerning_patterns": self._identify_concerning_patterns(conversations),
            
            # Summary text
            "narrative_summary": self._generate_narrative(conversations),
        }
        
        return summary
    
    def _extract_emotions(
        self,
        conversations: List[Dict],
        top_n: int = 3,
        skip_primary: bool = False
    ) -> List[str]:
        """Extract dominant emotions from conversations."""
        emotion_counts = {emotion: 0 for emotion in self.emotional_keywords.keys()}
        
        for conv in conversations:
            text = str(conv).lower()
            for emotion, keywords in self.emotional_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        emotion_counts[emotion] += 1
        
        # Sort by count
        sorted_emotions = sorted(
            emotion_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        result = [e[0] for e in sorted_emotions[:top_n] if e[1] > 0]
        return result or ["neutral"]
    
    def _extract_themes(self, conversations: List[Dict]) -> List[str]:
        """Extract major themes from conversations."""
        themes = [
            "work",
            "relationships",
            "health",
            "family",
            "money",
            "self-worth",
            "boundaries",
            "loss",
            "change",
            "connection",
            "creativity",
            "purpose",
            "identity",
            "trust",
        ]
        
        theme_matches = {}
        for theme in themes:
            count = 0
            for conv in conversations:
                text = str(conv).lower()
                if theme in text:
                    count += 1
            if count > 0:
                theme_matches[theme] = count
        
        # Return top 5 themes
        sorted_themes = sorted(
            theme_matches.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [t[0] for t in sorted_themes[:5]]
    
    def _identify_recurring_concerns(self, conversations: List[Dict]) -> List[str]:
        """Identify patterns that appear across multiple conversations."""
        concerns = []
        
        # Check for certain patterns
        text_combined = " ".join(str(c).lower() for c in conversations)
        
        patterns = {
            "boundary issues": ["boundary", "say no", "stand up", "people please"],
            "sleep problems": ["sleep", "insomnia", "tired", "exhausted"],
            "relationship tension": ["relationship", "conflict", "argument", "distance"],
            "work stress": ["work", "deadline", "boss", "coworker", "job"],
            "self-criticism": ["should", "fault", "blame", "stupid", "wrong"],
            "perfectionism": ["perfect", "control", "must", "should"],
            "comparison": ["compare", "better", "worse", "not enough"],
            "isolation": ["alone", "disconnect", "nobody", "isolated"],
        }
        
        for concern, keywords in patterns.items():
            match_count = sum(1 for kw in keywords if kw in text_combined)
            if match_count >= 2:  # Threshold: at least 2 keywords
                concerns.append(concern)
        
        return concerns
    
    def _extract_stated_needs(self, conversations: List[Dict]) -> List[str]:
        """Extract what the user explicitly says they need."""
        needs = []
        
        # Look for phrases indicating needs
        text = " ".join(str(c).lower() for c in conversations)
        
        need_phrases = {
            "support": ["need support", "help me", "i need", "please help"],
            "validation": ["understand", "get it", "make sense", "acknowledge"],
            "practical advice": ["how to", "what should", "steps", "concrete"],
            "listening": ["listen", "hear me", "understand", "see me"],
            "presence": ["be here", "with me", "present", "stay"],
            "boundaries": ["say no", "boundaries", "not responsible"],
            "perspective": ["another view", "perspective", "think about"],
            "hope": ["can i", "possible", "better", "forward"],
        }
        
        for need, phrases in need_phrases.items():
            for phrase in phrases:
                if phrase in text:
                    needs.append(need)
                    break
        
        return list(set(needs))  # Remove duplicates
    
    def _calculate_glyph_effectiveness(self, conversations: List[Dict]) -> Dict[str, float]:
        """Estimate glyph effectiveness based on usage and reported impact."""
        effectiveness = {}
        
        for conv in conversations:
            if "glyphs" in conv and "best_glyph" in conv:
                glyph = conv["best_glyph"]
                if glyph:
                    glyph_name = glyph.get("glyph_name", "unknown")
                    # Simple heuristic: glyphs in "best_glyph" are effective
                    effectiveness[glyph_name] = effectiveness.get(glyph_name, 0) + 1.0
        
        # Normalize to 0-1 scale
        if effectiveness:
            max_count = max(effectiveness.values())
            effectiveness = {k: v/max_count for k, v in effectiveness.items()}
        
        return effectiveness
    
    def _rank_glyphs(self, effectiveness: Dict[str, float]) -> List[str]:
        """Rank glyphs by effectiveness."""
        sorted_glyphs = sorted(
            effectiveness.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [g[0] for g in sorted_glyphs[:5]]
    
    def _calculate_engagement(self, conversations: List[Dict]) -> str:
        """Calculate engagement level."""
        if not conversations:
            return "low"
        
        total_messages = sum(len(c.get("messages", [])) for c in conversations)
        avg_per_conv = total_messages / len(conversations)
        
        if avg_per_conv < 2:
            return "low"
        elif avg_per_conv < 5:
            return "medium"
        else:
            return "high"
    
    def _detect_crisis_flags(self, conversations: List[Dict]) -> bool:
        """Detect if any conversation had crisis indicators."""
        for conv in conversations:
            signals = conv.get("signals", [])
            for signal in signals:
                if "suicidal" in str(signal).lower() or "crisis" in str(signal).lower():
                    return True
        
        return False
    
    def _identify_concerning_patterns(self, conversations: List[Dict]) -> List[str]:
        """Identify patterns that might need professional attention."""
        patterns = []
        
        text = " ".join(str(c).lower() for c in conversations)
        
        concerning = {
            "rumination": ["keep thinking", "can't stop", "over and over", "stuck"],
            "catastrophizing": ["disaster", "worst case", "always", "never", "ruin"],
            "hopelessness": ["no point", "never get better", "give up", "hopeless"],
            "isolation increasing": ["more alone", "withdrawing", "pushing away"],
            "self-harm thoughts": ["hurt myself", "harm", "cut"],
        }
        
        for pattern, keywords in concerning.items():
            if any(kw in text for kw in keywords):
                patterns.append(pattern)
        
        return patterns
    
    def _generate_narrative(self, conversations: List[Dict]) -> str:
        """Generate a brief narrative summary of the day."""
        if not conversations:
            return "No conversations recorded."
        
        emotions = self._extract_emotions(conversations, top_n=2)
        themes = self._extract_themes(conversations)
        needs = self._extract_stated_needs(conversations)
        
        narrative = f"Today you experienced {', '.join(emotions)}. "
        
        if themes:
            narrative += f"Key themes included {', '.join(themes[:2])}. "
        
        if needs:
            narrative += f"You expressed needs for {', '.join(needs[:2])}. "
        
        narrative += f"You had {len(conversations)} conversation(s) today."
        
        return narrative
    
    def store_daily_summary(
        self,
        db_connection,
        summary: Dict[str, Any],
        encryption_manager,
        user_id: str,
        password: str,
        retention_days: int = 90
    ) -> bool:
        """
        Store encrypted daily summary to database.
        
        Args:
            db_connection: Database connection
            summary: Summary dictionary
            encryption_manager: Encryption manager instance
            user_id: User identifier
            password: User password (for encryption)
            retention_days: How long to keep summary
        
        Returns:
            Success boolean
        """
        try:
            # Encrypt summary
            encrypted, user_id_hashed = encryption_manager.encrypt_conversation(
                user_id, password, summary
            )
            
            # Calculate expiration
            created_at = datetime.now()
            expires_at = created_at + timedelta(days=retention_days)
            
            # Store
            record = {
                "user_id_hashed": user_id_hashed,
                "date": summary["date"],
                "encrypted_summary": encrypted,
                "created_at": created_at.isoformat(),
                "expires_at": expires_at.isoformat(),
                "retention_days": retention_days,
            }
            
            db_connection.table("dream_summaries").insert(record).execute()
            
            logger.info(f"Stored dream summary for {summary['date']}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to store dream summary: {e}")
            return False


def create_daily_dream_summary(
    db_connection,
    user_id: str,
    password: str,
    date: str,
    conversations: List[Dict],
    glyph_effectiveness: Optional[Dict] = None
) -> bool:
    """
    High-level function to create and store a daily dream summary.
    Call this at end of day or after user logs out.
    
    Args:
        db_connection: Database connection
        user_id: User identifier
        password: User password
        date: Date (YYYY-MM-DD)
        conversations: List of conversations from that day
        glyph_effectiveness: Optional pre-calculated effectiveness
    
    Returns:
        Success boolean
    """
    from emotional_os.privacy.encryption_manager import EncryptionManager
    
    engine = DreamEngine()
    encryption = EncryptionManager()
    
    # Create summary
    summary = engine.create_daily_summary(
        user_id, date, conversations, glyph_effectiveness
    )
    
    # Store
    return engine.store_daily_summary(
        db_connection, summary, encryption, user_id, password, retention_days=90
    )
