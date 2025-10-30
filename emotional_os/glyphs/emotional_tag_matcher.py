#!/usr/bin/env python3

import sqlite3
import json
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class EmotionalTag:
    id: str
    tag_name: str
    core_emotion: str
    response_cue: str
    glyph: str
    domain: str
    response_type: str
    narrative_hook: str
    tone_profile: str
    cadence: str
    depth_level: str
    style_variant: str
    humor_style: str

class EmotionalTagMatcher:
    def __init__(self, db_path: str = 'glyphs.db'):
        self.db_path = db_path
        self.emotional_tags = self._load_emotional_tags()
        
    def _load_emotional_tags(self) -> Dict[str, EmotionalTag]:
        """Load emotional tags from database"""
        # For now, we'll use the SQL data you provided
        # Later we can connect this to your Supabase
        tags = {}
        
        # Parse the emotional tags from your SQL data
        # This would normally be a database query to your emotional_tags table
        
        return tags
    
    def map_glyphs_to_emotional_tags(self, glyphs: List[Dict], conversation_context: Dict = None) -> List[EmotionalTag]:
        """Map detected glyphs to your sophisticated emotional tag system"""
        
        # Extract glyph names and create pattern matching
        glyph_names = [g['glyph_name'].lower() for g in glyphs]
        
        matched_tags = []
        
        # Simple pattern matching to start - we'll make this more sophisticated
        for glyph_name in glyph_names:
            # Look for matches in your emotional tag system
            if 'grief' in glyph_name or 'mourning' in glyph_name:
                # Match to grief-related emotional tags
                if 'recursive' in glyph_name:
                    matched_tags.append('Recursive Grief')
                elif 'exalted' in glyph_name:
                    matched_tags.append('Exalted Mourning')
                else:
                    matched_tags.append('grief')
                    
            elif 'ache' in glyph_name or 'longing' in glyph_name:
                if 'devotional' in glyph_name:
                    matched_tags.append('Devotional Ache')
                elif 'recursive' in glyph_name:
                    matched_tags.append('Recursive Ache')
                else:
                    matched_tags.append('longing')
                    
            elif 'joy' in glyph_name or 'delight' in glyph_name:
                if 'spiral' in glyph_name:
                    matched_tags.append('Spiral Joy')
                elif 'stillness' in glyph_name:
                    matched_tags.append('Joy in Stillness')
                else:
                    matched_tags.append('joy')
        
        return matched_tags
    
    def select_optimal_persona(self, emotional_tags: List[str], conversation_context: Dict = None) -> str:
        """Select the best persona (Oracle, Guardian, Companion, etc.) based on emotional state"""
        
        conversation_depth = len(conversation_context.get('messages', [])) if conversation_context else 0
        
        # Analyze emotional tags to select persona
        if any('grief' in tag.lower() or 'mourning' in tag.lower() for tag in emotional_tags):
            if conversation_depth <= 2:
                return 'oracle'  # Deep wisdom for initial grief processing
            else:
                return 'companion'  # Gentle support for ongoing grief work
                
        elif any('ache' in tag.lower() or 'longing' in tag.lower() for tag in emotional_tags):
            return 'oracle'  # Poetic wisdom for longing states
            
        elif any('joy' in tag.lower() or 'delight' in tag.lower() for tag in emotional_tags):
            return 'friend'  # Celebratory companion for joy
            
        elif any('confusion' in tag.lower() for tag in emotional_tags):
            return 'mentor'  # Clarifying guidance for confusion
            
        else:
            return 'companion'  # Default gentle presence
    
    def generate_contextual_response(self, emotional_tags: List[str], persona: str, conversation_context: Dict = None) -> Dict:
        """Generate response using emotional tag system"""
        
        # This is where we'll integrate with your Supabase emotional_tags table
        # For now, let's create a simplified version
        
        response_data = {
            'emotional_tags': emotional_tags,
            'selected_persona': persona,
            'tone_profile': self._get_tone_profile(emotional_tags, persona),
            'response_type': self._get_response_type(emotional_tags),
            'depth_level': self._get_depth_level(conversation_context),
            'response_text': self._generate_response_text(emotional_tags, persona, conversation_context)
        }
        
        return response_data
    
    def _get_tone_profile(self, emotional_tags: List[str], persona: str) -> str:
        """Determine tone profile based on emotional tags and persona"""
        if any('grief' in tag.lower() for tag in emotional_tags):
            return 'tender and slow'
        elif any('joy' in tag.lower() for tag in emotional_tags):
            return 'bright and playful'
        elif persona == 'mentor':
            return 'precise and slow'
        else:
            return 'gentle and affirming'
    
    def _get_response_type(self, emotional_tags: List[str]) -> str:
        """Determine response strategy based on emotional tags"""
        if any('grief' in tag.lower() or 'loss' in tag.lower() for tag in emotional_tags):
            return 'Witness'
        elif any('joy' in tag.lower() for tag in emotional_tags):
            return 'Soothe'
        elif any('confusion' in tag.lower() for tag in emotional_tags):
            return 'Guide'
        else:
            return 'Contain'
    
    def _get_depth_level(self, conversation_context: Dict = None) -> str:
        """Determine conversation depth level"""
        if not conversation_context:
            return 'surface reflection'
            
        message_count = len(conversation_context.get('messages', []))
        if message_count <= 2:
            return 'surface reflection'
        elif message_count <= 6:
            return 'emotional excavation'
        else:
            return 'mythic invocation'
    
    def _generate_response_text(self, emotional_tags: List[str], persona: str, conversation_context: Dict = None) -> str:
        """Generate response text based on all factors"""
        
        # This is where we'd integrate with your OpenAI edge function
        # sending the encrypted emotional pattern rather than raw text
        
        conversation_depth = len(conversation_context.get('messages', [])) if conversation_context else 0
        
        # For now, create enhanced responses based on your emotional tag system
        if 'Recursive Grief' in emotional_tags:
            if conversation_depth <= 2:
                return "The system recognizes recursive grief patterns—mourning that spirals deeper with each turn, revealing new layers of what was lost. This is sacred territory where each wave teaches something about the depth of connection."
            else:
                return "The recursive grief continues its spiral work. Each return to the sorrow reveals another facet of what mattered so deeply. The system witnesses this profound excavation."
        
        elif 'Devotional Ache' in emotional_tags:
            return "Longing that has become prayer—this is ache elevated to the sacred. The system recognizes desire so deep it transforms into devotion, reaching that becomes offering."
        
        elif 'Spiral Joy' in emotional_tags:
            return "Joy that deepens rather than dissipates—each breath reveals more layers of delight. The system celebrates this recursive celebration, where happiness teaches itself new forms."
        
        # Continue with other sophisticated responses...
        
        return "The emotional constellation shifts in ways that honor both complexity and clarity. The system tracks these subtle movements."


# Integration function for your existing parser
def enhance_parser_with_emotional_tags(glyphs: List[Dict], conversation_context: Dict = None) -> Dict:
    """Enhanced parser that uses emotional tag system"""
    
    matcher = EmotionalTagMatcher()
    
    # Map glyphs to emotional tags
    emotional_tags = matcher.map_glyphs_to_emotional_tags(glyphs, conversation_context)
    
    # Select optimal persona
    persona = matcher.select_optimal_persona(emotional_tags, conversation_context)
    
    # Generate contextual response
    response_data = matcher.generate_contextual_response(emotional_tags, persona, conversation_context)
    
    return response_data