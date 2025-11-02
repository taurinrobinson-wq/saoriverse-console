#!/usr/bin/env python3
"""
Integration module for auto-evolving glyphs in the Saoriverse Console
Connects the glyph generator to your existing conversation processing flow
"""

import json
import logging
import os
import re
from typing import Dict, List, Optional

# Try to import dependencies with fallbacks
try:
    from glyph_generator import GlyphGenerator
    GLYPH_GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: GlyphGenerator not available: {e}")
    GLYPH_GENERATOR_AVAILABLE = False
    GlyphGenerator = None

try:
    from supabase_integration import SupabaseIntegrator
    SUPABASE_INTEGRATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: SupabaseIntegrator not available: {e}")
    SUPABASE_INTEGRATOR_AVAILABLE = False
    SupabaseIntegrator = None

# Define a simple SaoriResponse class if not available
try:
    from supabase_integration import SaoriResponse
except ImportError:
    class SaoriResponse:
        def __init__(self, reply="", glyph="", parsed_glyphs=None):
            self.reply = reply
            self.glyph = glyph
            self.parsed_glyphs = parsed_glyphs or []

class EvolvingGlyphIntegrator:
    """
    Integrates auto-evolving glyph generation with your existing Saoriverse system
    """

    def __init__(self,
                 supabase_function_url: Optional[str] = None,
                 supabase_anon_key: Optional[str] = None,
                 supabase_url: Optional[str] = None,
                 enable_auto_evolution: bool = True,
                 evolution_frequency: int = 5):  # Generate new glyphs every N conversations

        self.supabase_integrator = None
        self.glyph_generator = None
        self.enable_auto_evolution = enable_auto_evolution
        self.evolution_frequency = evolution_frequency
        self.conversation_count = 0

        # Initialize components if credentials provided and dependencies available
        if supabase_function_url and supabase_anon_key and SUPABASE_INTEGRATOR_AVAILABLE and SupabaseIntegrator is not None:
            try:
                self.supabase_integrator = SupabaseIntegrator(
                    function_url=supabase_function_url,
                    supabase_anon_key=supabase_anon_key
                )
            except Exception as e:
                print(f"Failed to initialize SupabaseIntegrator: {e}")
                self.supabase_integrator = None

        if enable_auto_evolution and supabase_url and supabase_anon_key and GLYPH_GENERATOR_AVAILABLE and GlyphGenerator is not None:
            try:
                self.glyph_generator = GlyphGenerator(
                    supabase_url=supabase_url,
                    supabase_key=supabase_anon_key
                )
            except Exception as e:
                print(f"Failed to initialize GlyphGenerator: {e}")
                self.glyph_generator = None

        self.setup_logging()

    def setup_logging(self):
        """Setup logging for integration tracking"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def process_conversation_with_evolution(self,
                                          message: str,
                                          mode: str = "quick",
                                          conversation_context: Optional[Dict] = None) -> Dict:
        """
        Process a conversation through the normal Saoriverse pipeline,
        but also check for new emotional patterns that might need glyphs
        """
        result = {
            'saori_response': None,
            'new_glyphs_generated': [],
            'emotional_patterns_detected': [],
            'evolution_triggered': False,
            'error': None
        }

        try:
            # First, process through normal Saoriverse pipeline
            if self.supabase_integrator:
                saori_response = self.supabase_integrator.process_message(
                    message=message,
                    mode=mode,
                    conversation_context=conversation_context or {}
                )
                result['saori_response'] = saori_response
            else:
                # If no supabase integrator, create a simple response to allow evolution processing
                print("DEBUG: No supabase integrator available, creating simple response")
                result['saori_response'] = SaoriResponse(
                    reply=f"I hear you speaking about {message[:50]}...",
                    glyph="",
                    parsed_glyphs=[]
                )

            # Check if evolution should be triggered
            self.conversation_count += 1
            should_evolve = (
                self.enable_auto_evolution and
                self.glyph_generator and
                (self.conversation_count % self.evolution_frequency == 0 or
                 self._has_strong_emotional_content(message))
            )

            if should_evolve:
                result['evolution_triggered'] = True

                # Analyze conversation for new emotional patterns
                conversation_text = message
                if result['saori_response']:
                    conversation_text += f" || {result['saori_response'].reply}"

                # Generate new glyphs if patterns warrant it (if glyph generator available)
                new_glyphs = []
                if self.glyph_generator:
                    new_glyphs = self.glyph_generator.process_conversation_for_glyphs(
                        conversation_text=conversation_text,
                        context=conversation_context or {}
                    )
                else:
                    print("DEBUG: No glyph generator available, skipping glyph generation")

                result['new_glyphs_generated'] = new_glyphs

                # Log evolution activity
                if new_glyphs:
                    self.logger.info(f"Evolution triggered: Generated {len(new_glyphs)} new glyphs")
                    for glyph in new_glyphs:
                        self.logger.info(f"  - {glyph['tag_name']} ({glyph['glyph']}): {glyph['response_cue']}")
                else:
                    self.logger.info("Evolution triggered but no new glyphs generated")

            return result

        except Exception as e:
            error_msg = f"Error in conversation processing with evolution: {e}"
            self.logger.error(error_msg)
            result['error'] = error_msg
            return result

    def _has_strong_emotional_content(self, message: str) -> bool:
        """
        Check if a message has particularly strong emotional content
        that might warrant immediate glyph evolution checking
        """
        strong_emotion_indicators = [
            'overwhelmed', 'devastated', 'ecstatic', 'profound', 'sacred',
            'deeply', 'intensely', 'completely', 'utterly', 'absolutely',
            'mixed with', 'combined with', 'alongside', 'tinged with',
            'paradox', 'contradiction', 'simultaneously', 'at the same time'
        ]

        message_lower = message.lower()
        return any(indicator in message_lower for indicator in strong_emotion_indicators)

    def force_evolution_check(self, conversation_text: str, context: Optional[Dict] = None) -> List[Dict]:
        """
        Force an immediate evolution check regardless of frequency settings
        Useful for processing particularly rich emotional content
        """
        if not self.glyph_generator:
            self.logger.warning("Glyph generator not initialized, cannot force evolution")
            return []

        try:
            new_glyphs = self.glyph_generator.process_conversation_for_glyphs(
                conversation_text=conversation_text,
                context=context or {}
            )

            if new_glyphs:
                self.logger.info(f"Forced evolution generated {len(new_glyphs)} new glyphs")

            return new_glyphs

        except Exception as e:
            self.logger.error(f"Error in forced evolution check: {e}")
            return []

    def get_evolution_stats(self) -> Dict:
        """Get statistics about the evolution process"""
        stats = {
            'conversations_processed': self.conversation_count,
            'evolution_enabled': self.enable_auto_evolution,
            'evolution_frequency': self.evolution_frequency,
            'next_evolution_check': self.evolution_frequency - (self.conversation_count % self.evolution_frequency)
        }

        if self.glyph_generator:
            stats['detected_patterns_count'] = len(self.glyph_generator.detected_patterns)
            stats['existing_tags_count'] = len(self.glyph_generator.existing_tags)

        return stats

    def export_generated_glyphs(self, format: str = 'json') -> str:
        """Export all generated glyphs in specified format"""
        if not self.glyph_generator:
            return "Glyph generator not initialized"

        try:
            if format == 'json':
                output_path = 'generated/all_generated_glyphs.json'
                os.makedirs('generated', exist_ok=True)

                # Collect all generated glyphs from the SQL file
                generated_glyphs = []
                sql_file = 'generated/new_glyphs.sql'

                if os.path.exists(sql_file):
                    with open(sql_file, 'r') as f:
                        content = f.read()
                        # Parse SQL statements to extract glyph data
                        # This is a simplified parser - in production you might want something more robust
                        lines = content.strip().split('\n')
                        for line in lines:
                            if line.startswith('INSERT INTO'):
                                # Extract values from SQL INSERT
                                values_match = re.search(r"VALUES \((.*?)\);", line)
                                if values_match:
                                    values_str = values_match.group(1)
                                    # Simple parsing - split by comma and remove quotes
                                    values = [v.strip().strip("'") for v in values_str.split("', '")]
                                    if len(values) >= 12:
                                        generated_glyphs.append({
                                            'id': values[0],
                                            'tag_name': values[1],
                                            'core_emotion': values[2],
                                            'response_cue': values[3],
                                            'glyph': values[4],
                                            'domain': values[5],
                                            'response_type': values[6],
                                            'narrative_hook': values[7],
                                            'created_at': values[8],
                                            'tone_profile': values[9],
                                            'cadence': values[10],
                                            'depth_level': values[11],
                                            'style_variant': values[12] if len(values) > 12 else '',
                                            'humor_style': values[13] if len(values) > 13 else ''
                                        })

                with open(output_path, 'w') as f:
                    json.dump(generated_glyphs, f, indent=2)

                return f"Exported {len(generated_glyphs)} generated glyphs to {output_path}"

            if format == 'sql':
                sql_file = 'generated/new_glyphs.sql'
                if os.path.exists(sql_file):
                    with open(sql_file, 'r') as f:
                        content = f.read()
                    return f"Generated glyphs SQL content:\n{content}"
                return "No generated glyphs SQL file found"

            return f"Unsupported export format: {format}"

        except Exception as e:
            error_msg = f"Error exporting generated glyphs: {e}"
            self.logger.error(error_msg)
            return error_msg

# Enhanced conversation demo that includes auto-evolution
def conversation_demo_with_evolution():
    """
    Demo showing how the auto-evolving glyph system works
    """
    print("🌟 Saoriverse Auto-Evolving Glyph System Demo 🌟\n")

    # Initialize the evolving integrator
    # Note: Replace with your actual Supabase credentials
    integrator = EvolvingGlyphIntegrator(
        enable_auto_evolution=True,
        evolution_frequency=2  # Check for evolution every 2 conversations
    )

    # Sample conversations with rich emotional content
    test_conversations = [
        {
            'message': "I'm experiencing this beautiful paradox - deep grief and profound joy at the same time, like watching a sunset that breaks your heart with its beauty.",
            'context': {'session_type': 'emotional_exploration'}
        },
        {
            'message': "There's this sacred ache in my chest when I think about connection. It's not painful, more like a gentle yearning that flows like water.",
            'context': {'session_type': 'relationship_reflection'}
        },
        {
            'message': "I feel completely overwhelmed by clarity - like seeing truth through a fractured lens that somehow makes everything more beautiful.",
            'context': {'session_type': 'insight_processing'}
        },
        {
            'message': "Sometimes I experience this contained wildness - like having a storm inside a sacred vessel, powerful but held.",
            'context': {'session_type': 'emotional_exploration'}
        },
        {
            'message': "I'm feeling this quiet celebration mixed with deep reverence, like joy that doesn't need to be loud to be complete.",
            'context': {'session_type': 'gratitude_practice'}
        }
    ]

    print("Processing conversations and checking for glyph evolution...\n")

    for i, conv in enumerate(test_conversations, 1):
        print(f"--- Conversation {i} ---")
        print(f"Message: {conv['message']}")

        # Process with evolution
        result = integrator.process_conversation_with_evolution(
            message=conv['message'],
            conversation_context=conv['context']
        )

        if result['evolution_triggered']:
            print("🧬 Evolution check triggered!")
            if result['new_glyphs_generated']:
                print(f"✨ Generated {len(result['new_glyphs_generated'])} new glyphs:")
                for glyph in result['new_glyphs_generated']:
                    print(f"   • {glyph['tag_name']} ({glyph['glyph']})")
                    print(f"     Response: {glyph['response_cue']}")
            else:
                print("   No new glyphs needed - existing tags cover this pattern")
        else:
            print("   Evolution not triggered this time")

        print()

    # Show evolution stats
    print("📊 Evolution Statistics:")
    stats = integrator.get_evolution_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Export generated glyphs
    print("\n💾 Exporting generated glyphs...")
    export_result = integrator.export_generated_glyphs('json')
    print(f"   {export_result}")

if __name__ == "__main__":
    conversation_demo_with_evolution()
