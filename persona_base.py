"""
🎭 PERSONA BASE: REMNANTS Modulation Layer
=============================================

PersonaBase applies REMNANTS emotional state to response text, making the same
response sound different based on the NPC's emotional evolution.

This is how NPCs "feel" their responses, not just deliver them mechanically.

Example:
    Same block might generate: "I understand your pain."
    
    But PersonaBase modulates it based on REMNANTS:
    - If empathy is high (>0.7): "I... I really do understand your pain."
    - If trust is low (<0.3): "I *say* I understand your pain."
    - If need is high (>0.7): "I understand your pain, and I need you to know that."

NPCs subclass PersonaBase and override the modulation helpers to add their voice.
This keeps emotional modulation consistent while letting each NPC have their own style.

The flow is:
    1. Compose text from blocks (responds to priorities)
    2. Apply REMNANTS modulation (responds to emotional state)
    3. Apply persona-specific styling (responds to character)

This makes responses emergent and emotionally resonant.
"""

import re
from typing import Dict, Optional, List
from abc import ABC, abstractmethod


class PersonaBase(ABC):
    """
    Base class for NPC personas that applies REMNANTS modulation to responses.
    
    Subclasses must implement:
    - npc_name: str (e.g., "Nima")
    - _soften_edges(): Soften language when empathy is high
    - _sharpen_edges(): Sharpen language when skepticism is high
    - _add_warmth(): Add relational language when need is high
    - _reduce_hedging(): Make more direct when authority is high
    - _add_memory_reference(): Reference prior states when memory is high
    
    The base class provides the modulation logic, subclasses provide the voice.
    """
    
    npc_name: str = "UnnamedNPC"
    
    def apply_style_and_remnants(
        self,
        text: str,
        remnants: Dict[str, float]
    ) -> str:
        """
        Apply REMNANTS-based modulation to response text.
        
        This is the main entry point. Call this on composed blocks before
        returning them to the player.
        
        Args:
            text: The composed block text
            remnants: Dict with REMNANTS traits (empathy, trust, authority, need, etc.)
            
        Returns:
            Modulated text reflecting NPC's emotional state
        """
        
        # Start with base text
        result = text
        
        # Apply REMNANTS modulations in order
        
        # 1. EMPATHY modulation (>0.7 softens, <0.3 hardens)
        empathy = remnants.get("empathy", 0.0)
        if empathy > 0.7:
            result = self._soften_edges(result)
        elif empathy < 0.3:
            result = self._sharpen_edges(result)
        
        # 2. SKEPTICISM modulation (>0.7 challenges, <0.3 accepts)
        skepticism = remnants.get("skepticism", 0.0)
        if skepticism > 0.7:
            result = self._sharpen_edges(result)
        elif skepticism < 0.3:
            result = self._reduce_skepticism(result)
        
        # 3. NEED modulation (>0.7 adds relational language)
        need = remnants.get("need", 0.0)
        if need > 0.7:
            result = self._add_warmth(result)
        
        # 4. AUTHORITY modulation (>0.7 reduces hedging, <0.3 increases)
        authority = remnants.get("authority", 0.0)
        if authority > 0.7:
            result = self._reduce_hedging(result)
        elif authority < 0.3:
            result = self._add_hedging(result)
        
        # 5. MEMORY modulation (>0.7 adds references to prior states)
        memory = remnants.get("memory", 0.0)
        if memory > 0.7:
            result = self._add_memory_reference(result)
        
        # 6. TRUST modulation (affects certainty)
        trust = remnants.get("trust", 0.0)
        if trust < 0.3:
            result = self._express_doubt(result)
        
        # 7. RESOLVE modulation (affects commitment/wavering)
        resolve = remnants.get("resolve", 0.0)
        if resolve < 0.3:
            result = self._introduce_uncertainty(result)
        
        return result.strip()
    
    # ========== MODULATION HELPERS ==========
    # Subclasses override these to apply persona-specific styling
    
    @abstractmethod
    def _soften_edges(self, text: str) -> str:
        """
        Soften harsh language when empathy is high.
        
        Examples:
        - "You're wrong" → "I think we might see this differently"
        - "That's foolish" → "That's... not quite right"
        - "I don't care" → "I'm having trouble engaging with that"
        
        Default: Add softening phrases, reduce absolutes
        """
        pass
    
    @abstractmethod
    def _sharpen_edges(self, text: str) -> str:
        """
        Sharpen language when skepticism/low empathy is high.
        
        Examples:
        - "I think you might be right" → "That doesn't make sense"
        - "Maybe that works" → "That won't work"
        - "I'm not sure" → "I doubt that"
        
        Default: Remove hedging, make more direct
        """
        pass
    
    @abstractmethod
    def _add_warmth(self, text: str) -> str:
        """
        Add relational language when need is high.
        
        Examples:
        - "I understand" → "I understand, and I'm here with you"
        - "You're dealing with loss" → "We're both dealing with loss"
        - "That matters" → "That matters to me, to us"
        
        Default: Add relational pronouns (we, us), empathetic markers
        """
        pass
    
    @abstractmethod
    def _reduce_hedging(self, text: str) -> str:
        """
        Reduce hedging language when authority is high.
        
        Examples:
        - "I think maybe..." → "I..."
        - "It seems like" → "It is"
        - "I might suggest" → "I suggest"
        
        Default: Remove qualifiers (maybe, perhaps, I think, etc.)
        """
        pass
    
    @abstractmethod
    def _add_memory_reference(self, text: str) -> str:
        """
        Add references to prior states when memory is high.
        
        This is persona-specific because each NPC has different memories.
        Subclasses must implement NPC-specific memory references.
        
        Examples for Nima:
        - After mentioning Ophina: "Like when Ophina was born, I felt..."
        - After discussing grief: "As it was that first night..."
        
        Default: Add generic memory markers, subclasses override
        """
        pass
    
    # ========== HELPER UTILITIES ==========
    # These provide common modulation patterns
    
    def _add_hedging(self, text: str) -> str:
        """
        Add hedging language (opposite of reduce_hedging).
        Used when authority/resolve is low.
        """
        # Add qualifiers to statements
        text = re.sub(
            r'\bi (am|have|know|think|feel|believe)\b',
            r'I \1... I mean, I \1',
            text,
            flags=re.IGNORECASE
        )
        return text
    
    def _reduce_skepticism(self, text: str) -> str:
        """
        Reduce skeptical tone when skepticism is low (high trust).
        """
        replacements = [
            (r"don't (think|believe)", "believe"),
            (r"I doubt", "I believe"),
            (r"That won't", "That might"),
            (r"That's wrong", "That's not quite right"),
            (r"\bdoubt\b", "wonder", 1),  # Replace first occurrence
        ]
        
        for pattern, replacement, *limit in replacements:
            limit_count = limit[0] if limit else 0
            text = re.sub(pattern, replacement, text, count=limit_count, flags=re.IGNORECASE)
        
        return text
    
    def _express_doubt(self, text: str) -> str:
        """
        Add expressions of doubt when trust is low.
        """
        # Add uncertainty markers
        text = re.sub(
            r'^([^.!?]+)([.!?])$',
            r'\1... or at least, I think so\2',
            text,
            flags=re.MULTILINE
        )
        return text
    
    def _introduce_uncertainty(self, text: str) -> str:
        """
        Add uncertainty when resolve is low.
        """
        # Make statements waver
        lines = text.split('\n')
        modulated = []
        
        for line in lines:
            if re.search(r'(will|must|should|can)', line, re.IGNORECASE):
                # Add uncertainty to commitment statements
                line = re.sub(
                    r'\b(will|must|should|can)\b',
                    r'might \1',
                    line,
                    flags=re.IGNORECASE
                )
            modulated.append(line)
        
        return '\n'.join(modulated)
    
    def _add_softness_markers(self, text: str) -> List[str]:
        """
        Helper: identify places where softening would be appropriate.
        Returns list of indices where text could be softened.
        """
        markers = []
        soft_words = [
            r'\b(never|always|should|must|wrong|right|fool|stupid)\b'
        ]
        
        for pattern in soft_words:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                markers.append(match.start())
        
        return markers
    
    def _add_directness_markers(self, text: str) -> List[str]:
        """
        Helper: identify where text could be made more direct.
        """
        markers = []
        hedge_words = [
            r'\b(maybe|perhaps|sort of|kind of|seems like|I think|I feel|might)\b'
        ]
        
        for pattern in hedge_words:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                markers.append(match.start())
        
        return markers


# ============================================================
# Example Implementations for different NPC archetypes
# ============================================================

class GriefProcessorPersona(PersonaBase):
    """
    Persona for NPCs processing grief (like Nima and Ravi).
    
    Their modulations involve:
    - Softening focuses on validating emotion
    - Sharpening focuses on the weight of loss
    - Warmth involves drawing listener into shared experience
    - Memory references Ophina, the before/after, specific moments
    """
    
    npc_name: str = "GriefProcessor"
    
    def _soften_edges(self, text: str) -> str:
        """Soften by adding validation and internal qualification."""
        # Replace absolutes with emotional qualifications
        text = re.sub(
            r'\b(you|i|they|we)\s+(are|am|is)\s+([^.!?]+)',
            r'\1 ... \1 \2',
            text,
            flags=re.IGNORECASE
        )
        
        # Add internal pauses
        text = re.sub(r'([.!?])\s+', r'\1.. ', text)
        
        return text
    
    def _sharpen_edges(self, text: str) -> str:
        """Sharpen by emphasizing the weight and reality of loss."""
        # Make loss-related statements more direct
        text = re.sub(
            r'(she|he|the child|my daughter|my son) (was|is)',
            r'\1 \2',  # Remove any hedging around loss
            text,
            flags=re.IGNORECASE
        )
        
        return text
    
    def _add_warmth(self, text: str) -> str:
        """Add warmth by drawing listener into shared experience."""
        # Use "we" and "us" more
        text = re.sub(
            r'\bi (understand|know|feel)',
            r'I \1, and so do you',
            text,
            flags=re.IGNORECASE
        )
        
        # Add relational language
        text = re.sub(
            r'(this loss|this pain|this grief)',
            r'\1—that we share',
            text,
            flags=re.IGNORECASE
        )
        
        return text
    
    def _reduce_hedging(self, text: str) -> str:
        """Make statements more direct about the loss."""
        text = re.sub(
            r'(she|he|the child|my daughter|my son)\s+was',
            r'\1 is—was—',
            text,
            flags=re.IGNORECASE
        )
        
        return text
    
    def _add_memory_reference(self, text: str) -> str:
        """
        Add specific memory references (to be overridden by actual NPC).
        This is a template—subclasses implement NPC-specific memories.
        """
        # Generic grief memory references
        if 'loss' in text.lower() or 'grief' in text.lower():
            text = re.sub(
                r'(loss|grief)',
                r'[MEMORY: specific moment] \1',
                text,
                flags=re.IGNORECASE
            )
        
        return text


class SkepticalPersona(PersonaBase):
    """
    Persona for NPCs with inherent skepticism (like Kaelen).
    
    Their modulations involve:
    - Softening involves qualification and nuance
    - Sharpening involves cutting through sentiment
    - Warmth is rare and hesitant
    - Memory references doubt and past betrayals
    """
    
    npc_name: str = "Skeptical"
    
    def _soften_edges(self, text: str) -> str:
        """Soften skeptical edges with qualifications."""
        text = re.sub(
            r'\b(that|it|you)\s+(won\'t|won\'t|doesn\'t)\s+',
            r'\1 probably \2 ',
            text,
            flags=re.IGNORECASE
        )
        return text
    
    def _sharpen_edges(self, text: str) -> str:
        """Sharpen by removing benefit-of-doubt."""
        text = re.sub(
            r'(might|could|may)\s+',
            r'won\'t ',
            text,
            flags=re.IGNORECASE
        )
        return text
    
    def _add_warmth(self, text: str) -> str:
        """Skeptics add warmth reluctantly."""
        text = re.sub(
            r'(but|still|even so|)',
            r'\1... I suppose',
            text,
            flags=re.IGNORECASE
        )
        return text
    
    def _reduce_hedging(self, text: str) -> str:
        """Make skeptical statements direct."""
        text = re.sub(
            r'(I (think|believe|suppose))',
            r'',
            text,
            flags=re.IGNORECASE
        )
        return text
    
    def _add_memory_reference(self, text: str) -> str:
        """Reference past failures and broken trust."""
        text = re.sub(
            r'(trust|believe|hope)',
            r'\1... as if that ever worked',
            text,
            flags=re.IGNORECASE
        )
        return text
