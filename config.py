# Auto-Evolving Glyph System Configuration
# Copy this file to config.py and update with your actual Supabase credentials

# =============================================================================
# SUPABASE CONFIGURATION
# =============================================================================
# Replace these with your actual Supabase project details

SUPABASE_URL = "https://gyqzyuvuuyfjxnramkfq.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5cXp5dXZ1dXlmanhucmFta2ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0NjcyMDAsImV4cCI6MjA3MTA0MzIwMH0.4SpC34q7lcURBX4hujkTGqICdSM6ZWASCENnRs5rkS8"  
SUPABASE_FUNCTION_URL = "https://gyqzyuvuuyfjxnramkfq.supabase.co/functions/v1/saori-fixed"

# =============================================================================
# EVOLUTION SETTINGS
# =============================================================================

# Enable/disable automatic glyph evolution
ENABLE_AUTO_EVOLUTION = True

# How often to check for new patterns (every N conversations)
# Lower values = more frequent checking, higher values = less frequent
EVOLUTION_FREQUENCY = 5

# How many times a pattern must appear before creating a glyph
# Higher values = more conservative, lower values = more creative
MIN_PATTERN_FREQUENCY = 3

# How novel a pattern must be to warrant a new glyph (0.0 - 1.0)
# Higher values = only very unique patterns, lower values = more patterns qualify
NOVELTY_THRESHOLD = 0.7

# =============================================================================
# LOGGING & DEBUGGING
# =============================================================================

# Logging level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# Whether to save logs to files
LOG_TO_FILE = True

# Directory for log files
LOG_DIRECTORY = "logs"

# =============================================================================
# DATABASE SETTINGS  
# =============================================================================

# Whether to backup generated glyphs to SQL files
BACKUP_TO_SQL = True

# Directory for SQL backup files
SQL_BACKUP_DIRECTORY = "generated"

# =============================================================================
# ADVANCED SETTINGS
# =============================================================================

# Timeout for Supabase requests (seconds)
REQUEST_TIMEOUT = 30

# Maximum number of glyphs to generate per conversation
MAX_GLYPHS_PER_CONVERSATION = 2

# Whether to analyze Saori's responses for patterns (in addition to user input)
ANALYZE_SAORI_RESPONSES = True

# =============================================================================
# EXAMPLE USAGE
# =============================================================================
"""
from config import *
from evolving_glyph_integrator import EvolvingGlyphIntegrator

# Initialize the evolving system
integrator = EvolvingGlyphIntegrator(
    supabase_function_url=SUPABASE_FUNCTION_URL,
    supabase_anon_key=SUPABASE_ANON_KEY,
    supabase_url=SUPABASE_URL,
    enable_auto_evolution=ENABLE_AUTO_EVOLUTION,
    evolution_frequency=EVOLUTION_FREQUENCY
)

# Process a conversation with evolution
result = integrator.process_conversation_with_evolution(
    message="I'm feeling this profound mixture of joy and sadness",
    conversation_context={"session_id": "user123"}
)

# Check if new glyphs were generated
if result['new_glyphs_generated']:
    print(f"Generated {len(result['new_glyphs_generated'])} new glyphs!")
    for glyph in result['new_glyphs_generated']:
        print(f"- {glyph['tag_name']} ({glyph['glyph']})")

# Get evolution statistics
stats = integrator.get_evolution_stats()
print(f"Conversations processed: {stats['conversations_processed']}")
print(f"Patterns detected: {stats.get('detected_patterns_count', 0)}")
"""