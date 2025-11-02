# Configuration for Auto-Evolving Glyph System
# Copy this to config.py and fill in your actual values

# Supabase Configuration
SUPABASE_URL = "https://your-project.supabase.co"  # Your Supabase project URL
SUPABASE_ANON_KEY = "your-anon-key-here"  # Your Supabase anon key
SUPABASE_FUNCTION_URL = "https://your-project.supabase.co/functions/v1/saori-fixed"  # Your edge function URL

# Glyph Generation Settings
ENABLE_AUTO_EVOLUTION = True  # Set to False to disable automatic glyph generation
EVOLUTION_FREQUENCY = 5  # Check for new glyphs every N conversations
MIN_PATTERN_FREQUENCY = 3  # Pattern must appear N times before generating glyph
NOVELTY_THRESHOLD = 0.7  # How novel a pattern must be (0.0-1.0)

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True  # Whether to log to files
LOG_DIRECTORY = "logs"  # Directory for log files

# Database Settings
BACKUP_TO_SQL = True  # Whether to backup generated glyphs to SQL files
SQL_BACKUP_DIRECTORY = "generated"  # Directory for SQL backup files

# Example usage in your code:
"""
from config import *
from evolving_glyph_integrator import EvolvingGlyphIntegrator

integrator = EvolvingGlyphIntegrator(
    supabase_function_url=SUPABASE_FUNCTION_URL,
    supabase_anon_key=SUPABASE_ANON_KEY,
    supabase_url=SUPABASE_URL,
    enable_auto_evolution=ENABLE_AUTO_EVOLUTION,
    evolution_frequency=EVOLUTION_FREQUENCY
)

# Process a conversation with auto-evolution
result = integrator.process_conversation_with_evolution(
    message="Your user's message here",
    conversation_context={"session_id": "123"}
)

if result['new_glyphs_generated']:
    print(f"Generated {len(result['new_glyphs_generated'])} new glyphs!")
"""
