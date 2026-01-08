#!/usr/bin/env python3
"""
Conversation Archetype Library

Stores learned dialogue patterns extracted from successful conversations.
Each archetype contains the rules, cues, principles, and tone guidelines
derived from lived dialogue via the playwright/organizer workflow.

Archetypes are NOT canned responses — they're reusable rule sets that the
system applies dynamically to generate fresh responses in similar contexts.
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime


class ConversationArchetype:
    """Single archetype pattern extracted from dialogue."""
    
    def __init__(
        self,
        name: str,
        entry_cues: List[str],
        response_principles: List[str],
        continuity_bridges: List[str],
        tone_guidelines: List[str],
        pattern_template: Optional[str] = None,
        success_weight: float = 1.0,
        created_at: Optional[str] = None,
    ):
        """Initialize an archetype.
        
        Args:
            name: Archetype name (e.g., "ReliefToGratitude")
            entry_cues: Keywords/signals that trigger this pattern
            response_principles: Core rules the system follows
            continuity_bridges: How to carry forward prior context
            tone_guidelines: Style, pacing, emotional calibration rules
            pattern_template: Optional description of response flow
            success_weight: How successful this archetype has been (0-1 scale)
            created_at: ISO timestamp of creation
        """
        self.name = name
        self.entry_cues = entry_cues
        self.response_principles = response_principles
        self.continuity_bridges = continuity_bridges
        self.tone_guidelines = tone_guidelines
        self.pattern_template = pattern_template or ""
        self.success_weight = success_weight
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.usage_count = 0
        self.success_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize archetype to dictionary."""
        return {
            "name": self.name,
            "entry_cues": self.entry_cues,
            "response_principles": self.response_principles,
            "continuity_bridges": self.continuity_bridges,
            "tone_guidelines": self.tone_guidelines,
            "pattern_template": self.pattern_template,
            "success_weight": self.success_weight,
            "created_at": self.created_at,
            "usage_count": self.usage_count,
            "success_count": self.success_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationArchetype":
        """Deserialize archetype from dictionary."""
        archetype = cls(
            name=data.get("name", "Unnamed"),
            entry_cues=data.get("entry_cues", []),
            response_principles=data.get("response_principles", []),
            continuity_bridges=data.get("continuity_bridges", []),
            tone_guidelines=data.get("tone_guidelines", []),
            pattern_template=data.get("pattern_template", ""),
            success_weight=data.get("success_weight", 1.0),
            created_at=data.get("created_at"),
        )
        archetype.usage_count = data.get("usage_count", 0)
        archetype.success_count = data.get("success_count", 0)
        return archetype
    
    def matches_context(self, user_input: str, prior_context: Optional[str] = None) -> float:
        """Score how well this archetype matches the current context.
        
        Args:
            user_input: Current user message
            prior_context: Optional prior messages/emotional state
            
        Returns:
            Match score 0-1 (1.0 = perfect match)
        """
        combined = f"{prior_context or ''} {user_input}".lower()
        
        cue_matches = sum(1 for cue in self.entry_cues if cue.lower() in combined)
        max_cues = len(self.entry_cues) if self.entry_cues else 1
        
        # Score based on how many cues matched + success weight
        cue_score = min(cue_matches / max_cues, 1.0) if max_cues > 0 else 0.0
        final_score = (cue_score * 0.7) + (self.success_weight * 0.3)
        
        return final_score
    
    def record_usage(self, success: bool) -> None:
        """Record that this archetype was used and whether it succeeded."""
        self.usage_count += 1
        if success:
            self.success_count += 1
        
        # Update success weight (exponential smoothing)
        if self.usage_count > 0:
            success_rate = self.success_count / self.usage_count
            self.success_weight = (self.success_weight * 0.7) + (success_rate * 0.3)


class ArchetypeLibrary:
    """Manages the growing library of conversation archetypes."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize the archetype library.
        
        Args:
            storage_path: Path to JSON file for persistence
        """
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__),
            "archetype_library.json"
        )
        self.archetypes: Dict[str, ConversationArchetype] = {}
        self._load_from_disk()
        self._initialize_default_archetypes()
    
    def _initialize_default_archetypes(self) -> None:
        """Initialize with the first learned archetype from your dialogue."""
        if "ReliefToGratitude" not in self.archetypes:
            relief_to_gratitude = ConversationArchetype(
                name="ReliefToGratitude",
                entry_cues=[
                    "relief", "gratitude", "hug", "melted away", "wonderful feeling",
                    "joy mixed with sorrow", "needed", "happy", "precious", "sweet moment"
                ],
                response_principles=[
                    "Validate positive moment warmly",
                    "Balance empathy across mixed emotions",
                    "Invite elaboration with gentle questions",
                    "Avoid judgment or prescriptive advice",
                    "Hold space for joy without dismissing underlying sorrow"
                ],
                continuity_bridges=[
                    "Connect gratitude to prior overwhelm",
                    "Tie new disclosures into ongoing context",
                    "Carry forward themes into deeper exploration",
                    "Remember what came before without dwelling"
                ],
                tone_guidelines=[
                    "Warm and embracing language",
                    "Gentle pacing with validation first",
                    "Mirror user's expressive metaphors",
                    "Proportional empathy — not overblown, not clinical",
                    "Use concrete details (hugs, silence, consistency)"
                ],
                pattern_template="[Acknowledge relief] + [Balance joy/sorrow] + [Gentle probe into complexity] + [Deepen understanding]",
                success_weight=1.0,
            )
            self.archetypes["ReliefToGratitude"] = relief_to_gratitude
        
        if "OverwhelmToReflection" not in self.archetypes:
            overwhelm_to_reflection = ConversationArchetype(
                name="OverwhelmToReflection",
                entry_cues=[
                    "fragile", "overwhelmed", "stress at work", "drowning", "nothing to anchor",
                    "doesn't make sense", "what's it all for", "pummeled", "purpose", "identity",
                    "lawyer", "advocacy", "grind", "drowned out", "fulfilling", "lost sight"
                ],
                response_principles=[
                    "Validate feelings of overwhelm without dismissing",
                    "Offer gentle scaffolding but retract if burdensome",
                    "Invite reflection on deeper meaning and purpose",
                    "Mirror user's values and identity anchors",
                    "Encourage exploration of alternative sources of fulfillment",
                    "Help connect personal values to daily actions",
                    "Move from immediate stress to existential questioning"
                ],
                continuity_bridges=[
                    "Connect overwhelm to work stress to existential questioning",
                    "Carry forward themes of purpose and identity",
                    "Link professional values with personal interests",
                    "Use user's metaphors (anchor, grind, drowning, meditative)",
                    "Remember what gives meaning when work doesn't",
                    "Hold space for complexity (multiple roles, competing values)"
                ],
                tone_guidelines=[
                    "Gentle, validating language with empathetic understanding",
                    "Self-correction when suggestion feels burdensome",
                    "Conversational pacing: validate → probe → reflect → expand",
                    "Mirror user's metaphorical and expressive language",
                    "Curious without being prescriptive",
                    "Honor the existential nature of the questioning",
                    "Acknowledge both professional and personal identity"
                ],
                pattern_template="[Validate overwhelm] + [Gently offer scaffolding] + [Invite deeper questioning] + [Reflect identity/values] + [Explore alternative fulfillment]",
                success_weight=1.0,
            )
            self.archetypes["OverwhelmToReflection"] = overwhelm_to_reflection
    
    def add_archetype(self, archetype: ConversationArchetype) -> None:
        """Add a new archetype to the library."""
        self.archetypes[archetype.name] = archetype
        self._save_to_disk()
    
    def get_best_match(
        self,
        user_input: str,
        prior_context: Optional[str] = None,
        threshold: float = 0.3,
    ) -> Optional[ConversationArchetype]:
        """Find the best-matching archetype for current context.
        
        Args:
            user_input: Current user message
            prior_context: Optional prior emotional context
            threshold: Minimum score to consider a match
            
        Returns:
            Best matching archetype, or None if no good match
        """
        best_match = None
        best_score = threshold
        
        for archetype in self.archetypes.values():
            score = archetype.matches_context(user_input, prior_context)
            if score > best_score:
                best_score = score
                best_match = archetype
        
        return best_match
    
    def get_all_matches(
        self,
        user_input: str,
        prior_context: Optional[str] = None,
        threshold: float = 0.2,
    ) -> List[tuple[ConversationArchetype, float]]:
        """Get all archetypes that match the context, sorted by score.
        
        Returns:
            List of (archetype, score) tuples, highest score first
        """
        matches = []
        for archetype in self.archetypes.values():
            score = archetype.matches_context(user_input, prior_context)
            if score >= threshold:
                matches.append((archetype, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def record_usage(self, archetype_name: str, success: bool) -> None:
        """Record that an archetype was used and whether it succeeded."""
        if archetype_name in self.archetypes:
            self.archetypes[archetype_name].record_usage(success)
            self._save_to_disk()
    
    def _save_to_disk(self) -> None:
        """Persist archetype library to JSON."""
        try:
            data = {
                name: archetype.to_dict()
                for name, archetype in self.archetypes.items()
            }
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            import logging
            logging.error(f"Failed to save archetype library: {e}")
    
    def _load_from_disk(self) -> None:
        """Load archetype library from JSON if it exists."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for name, archetype_data in data.items():
                        archetype = ConversationArchetype.from_dict(archetype_data)
                        self.archetypes[name] = archetype
        except Exception as e:
            import logging
            logging.error(f"Failed to load archetype library: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize entire library."""
        return {
            name: archetype.to_dict()
            for name, archetype in self.archetypes.items()
        }


# Global instance
_archetype_library: Optional[ArchetypeLibrary] = None


def get_archetype_library() -> ArchetypeLibrary:
    """Get or create the global archetype library."""
    global _archetype_library
    if _archetype_library is None:
        _archetype_library = ArchetypeLibrary()
    return _archetype_library
