#!/usr/bin/env python3
"""
Punctuation Cleaner: Anti-dash post-processing filter.

Automatically detects em dashes and rewrites them into style-appropriate
alternatives based on glyph tone pool. Ensures consistent, non-canned punctuation
across all responses.
"""

import json
import os
import random
import re
import signal
from typing import Dict, Optional, Tuple

import logging

logger = logging.getLogger(__name__)


class TimeoutError(Exception):
    """Raised when an operation exceeds timeout."""
    pass


class PunctuationCleaner:
    """Cleans em dashes from responses and replaces with style-appropriate punctuation."""

    def __init__(self, style_matrix_path: Optional[str] = None):
        """Initialize the cleaner with style matrix.
        
        Args:
            style_matrix_path: Path to style_matrix.json. If None, uses default location.
        """
        self.style_matrix = {}
        self.tone_pool_map = {}
        
        if style_matrix_path is None:
            style_matrix_path = os.path.join(
                os.path.dirname(__file__), "style_matrix.json"
            )
        
        self._load_style_matrix(style_matrix_path)

    def _load_style_matrix(self, path: str) -> None:
        """Load the style matrix from JSON file."""
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.style_matrix = data.get("style_matrix", {})
                    logger.debug(f"Loaded style matrix from {path}")
            else:
                logger.warning(f"Style matrix not found at {path}, using minimal defaults")
                self._set_defaults()
        except Exception as e:
            logger.warning(f"Failed to load style matrix: {e}, using minimal defaults")
            self._set_defaults()

    def _set_defaults(self) -> None:
        """Set minimal default style matrix if loading fails."""
        self.style_matrix = {
            "pools": {
                "Grounded": {
                    "rotation_bank": ["You're moving through this. That movement itself is valid."]
                },
                "Reflective": {
                    "rotation_bank": ["That's part of the passage. It deserves recognition."]
                },
                "Empathetic": {
                    "rotation_bank": ["I hear you, that's real, and it matters."]
                },
                "Encouraging": {
                    "rotation_bank": ["This challenge is real. It's not permanent."]
                },
                "Clarifying": {
                    "rotation_bank": ["It's okay not to know. That's part of the process."]
                },
            },
            "mapping_rules": {
                "default": "Grounded",
                "keywords": {},
            },
            "substitution_rules": {
                "Grounded": {"replacement": ". "},
                "Reflective": {"replacement": ": "},
                "Empathetic": {"replacement": ", "},
                "Encouraging": {"replacement": ". "},
                "Clarifying": {"replacement": ". "},
            },
        }

    def detect_tone_pool(self, glyph_name: Optional[str]) -> str:
        """Map a glyph name to its tone pool.
        
        Args:
            glyph_name: Name of the glyph (e.g., "Spiral Containment")
            
        Returns:
            Tone pool name (Grounded, Reflective, Empathetic, Encouraging, Clarifying)
        """
        if not glyph_name:
            return self.style_matrix.get("mapping_rules", {}).get("default", "Grounded")
        
        glyph_lower = glyph_name.lower()
        mapping_rules = self.style_matrix.get("mapping_rules", {})
        keywords = mapping_rules.get("keywords", {})
        
        # Check for keyword matches in glyph name
        for keyword, pool in keywords.items():
            if keyword in glyph_lower:
                return pool
        
        # Default if no match
        return mapping_rules.get("default", "Grounded")

    def get_substitution_rule(self, tone_pool: str) -> str:
        """Get the substitution replacement string for a tone pool.
        
        Args:
            tone_pool: One of: Grounded, Reflective, Empathetic, Encouraging, Clarifying
            
        Returns:
            Replacement string (". ", ": ", ", ", etc.)
        """
        rules = self.style_matrix.get("substitution_rules", {})
        return rules.get(tone_pool, {}).get("replacement", ". ")

    def clean_em_dashes(self, text: str, tone_pool: str) -> str:
        """Remove em dashes and replace with style-appropriate punctuation.
        
        Args:
            text: Response text that may contain em dashes
            tone_pool: Tone pool to determine replacement style
            
        Returns:
            Cleaned text with em dashes replaced
        """
        if not text:
            return text
        
        # Get the appropriate replacement for this tone pool
        replacement = self.get_substitution_rule(tone_pool)
        
        # Replace em dashes and double hyphens
        # Handle spaces around dashes flexibly
        cleaned = re.sub(r"\s*—\s*", replacement, text)
        cleaned = re.sub(r"\s*--\s*", replacement, cleaned)
        
        return cleaned

    def diversify_closing(self, response: str, tone_pool: str) -> str:
        """Preserve response as-is.
        
        NOTE: This function is disabled. The rotation banks are for configuration
        reference only - actual response generation happens in DynamicResponseComposer.
        Replacing the closing sentence here breaks context-specific responses.
        
        Args:
            response: Full response text
            tone_pool: Tone pool for selecting appropriate closing (unused)
            
        Returns:
            Response unchanged
        """
        return response

    def process_response(
        self, 
        response: str, 
        glyph_name: Optional[str] = None,
        diversify: bool = False
    ) -> str:
        """Full processing pipeline: detect tone, clean dashes.
        
        DISABLED: This was causing responses to become generic/repetitive.
        
        Args:
            response: Raw response text
            glyph_name: Optional glyph name to determine tone
            diversify: DISABLED - kept for backward compatibility only
            
        Returns:
            Response unchanged (cleaner disabled)
        """
        # Return response unchanged - the response builder already creates
        # well-formed, contextual responses. Attempting to post-process them
        # was making them generic.
        return response


# Singleton instance for easy import and use
_cleaner_instance: Optional[PunctuationCleaner] = None


def get_cleaner() -> PunctuationCleaner:
    """Get or create the singleton PunctuationCleaner instance."""
    global _cleaner_instance
    if _cleaner_instance is None:
        _cleaner_instance = PunctuationCleaner()
    return _cleaner_instance


def clean_response(
    response: str,
    glyph_name: Optional[str] = None,
    diversify: bool = True
) -> str:
    """Convenience function to clean a response.
    
    Args:
        response: Response text to clean
        glyph_name: Optional glyph name for tone detection
        diversify: Whether to diversify generic closings
        
    Returns:
        Cleaned response
    """
    cleaner = get_cleaner()
    return cleaner.process_response(response, glyph_name, diversify)


if __name__ == "__main__":
    # Quick test
    test_responses = [
        ("You're not alone—many brilliant people struggle with math.", "Spiral Containment"),
        ("You're naming what you're experiencing—that kind of understanding requires passage.", "Recursive Ache"),
        ("You're in territory without a map—the alone you're feeling is the unknown.", "Still Recognition"),
    ]
    
    cleaner = PunctuationCleaner()
    
    for response, glyph in test_responses:
        print(f"\nGlyph: {glyph}")
        print(f"Original: {response}")
        pool = cleaner.detect_tone_pool(glyph)
        print(f"Tone Pool: {pool}")
        cleaned = cleaner.process_response(response, glyph, diversify=False)
        print(f"Cleaned: {cleaned}")
