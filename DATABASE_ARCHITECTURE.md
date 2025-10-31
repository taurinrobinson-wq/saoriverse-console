"""
DATABASE ACCESS & LEXICON INTEGRATION SYSTEM
FirstPerson Emotional OS - Complete Architecture Overview

This document maps all the code paths that access large lexicon databases
and integrate them into the signal parsing and glyph matching system.
"""

# ============================================================================
# 1. DATABASE ARCHITECTURE
# ============================================================================

DATABASE_LOCATIONS = {
    "primary": {
        "path": "/Users/taurinrobinson/saoriverse-console/emotional_os/glyphs/glyphs.db",
        "table": "glyph_lexicon",
        "records": 292,
        "columns": ["id", "voltage_pair", "glyph_name", "description", "gate", "activation_signals"]
    },
    "csv_export": {
        "path": "/Users/taurinrobinson/saoriverse-console/glyph_lexicon_rows.csv",
        "records": 292,
        "sync_status": "Current (Oct 30, 2025)"
    }
}

# ============================================================================
# 2. SIGNAL LEXICON FILES (JSON-based keyword mapping)
# ============================================================================

SIGNAL_LEXICONS = {
    "base_signal_lexicon": {
        "path": "parser/signal_lexicon.json",
        "keywords": 152,
        "maps_to": "voltage signals (α, β, γ, δ, ε, θ, λ, Ω)",
        "loaded_by": ["signal_parser.py", "emotional_os/glyphs/signal_parser.py"]
    },
    "learned_lexicon": {
        "path": "parser/learned_lexicon.json",
        "keywords": 9,
        "maps_to": "voltage signals",
        "auto_generated": True,
        "merged_with": "base_signal_lexicon at runtime"
    }
}

# ============================================================================
# 3. CODE THAT ACCESSES THE DATABASE
# ============================================================================

DATABASE_ACCESS_CODE = {
    "signal_parser.py": {
        "location": "/Users/taurinrobinson/saoriverse-console/parser/signal_parser.py",
        "key_function": "fetch_glyphs(gates, db_path='glyphs.db')",
        "what_it_does": """
        1. Takes list of activated gates (Gate 2, 4, 5, 6, 9, 10)
        2. Queries SQLite database: SELECT glyph_name, description, gate FROM glyph_lexicon WHERE gate IN (...)
        3. Returns matching glyphs (typically 2-10 glyphs per gate)
        4. Returns as List[Dict] with keys: glyph_name, description, gate
        """,
        "called_from": [
            "main_v2.py (Streamlit UI)",
            "emotional_os/deploy/modules/ui.py",
            "Various test scripts"
        ]
    },
    
    "emotional_os/glyphs/signal_parser.py": {
        "location": "/Users/taurinrobinson/saoriverse-console/emotional_os/glyphs/signal_parser.py",
        "key_function": "parse_input(input_text, lexicon_path, db_path='glyphs.db', conversation_context)",
        "what_it_does": """
        MAIN ORCHESTRATION FUNCTION - Complete pipeline:
        
        1. load_signal_map(lexicon_path)
           - Loads base signal lexicon (JSON)
           - Loads learned lexicon (JSON)
           - Merges both into combined_lexicon
           
        2. parse_signals(input_text, signal_map)
           - Fuzzy matches keywords against input
           - Returns List[Dict] with keyword, signal, voltage, tone
           
        3. evaluate_gates(signals)
           - Maps voltage signals to ECM gates
           - Returns activated gates
           
        4. fetch_glyphs(gates, db_path)
           - Queries SQLite database
           - Returns matching glyphs from glyph_lexicon
           
        5. select_best_glyph_and_response(glyphs, signals)
           - Scores glyphs based on emotional relevance
           - Returns (best_glyph, contextual_response)
           
        RETURNS: {
            "timestamp": ISO timestamp,
            "input": original text,
            "signals": parsed signals,
            "gates": activated gates,
            "glyphs": all matching glyphs,
            "best_glyph": highest scored glyph,
            "ritual_prompt": ritual suggestion,
            "voltage_response": contextual emotional response,
            "debug_sql": SQL query used,
            "debug_glyph_rows": database rows retrieved
        }
        """,
        "database_access": "SQLite3 via sqlite3.connect(db_path)",
        "error_handling": "Try/except for OperationalError, returns empty list on failure"
    }
}

# ============================================================================
# 4. STREAMLIT UI INTEGRATION
# ============================================================================

STREAMLIT_INTEGRATION = {
    "main_v2.py": {
        "location": "/Users/taurinrobinson/saoriverse-console/main_v2.py",
        "imports": [
            "from emotional_os.deploy.modules.auth import SaoynxAuthentication",
            "from emotional_os.deploy.modules.ui import render_main_app"
        ],
        "how_it_uses_glyphs": """
        Calls render_main_app() which:
        - Displays chat interface
        - Processes user messages through signal parser
        - Displays resonant glyph and contextual response
        - Shows processing time and mode
        """
    },
    
    "emotional_os/deploy/modules/ui.py": {
        "location": "/Users/taurinrobinson/saoriverse-console/emotional_os/deploy/modules/ui.py",
        "imports": "from emotional_os.glyphs.signal_parser import parse_input",
        "glyph_processing": """
        Lines 285, 340: Calls parse_input() with:
        - input_text: user's message
        - lexicon_path: path to signal lexicon
        - db_path: path to glyphs database
        
        Displays:
        - best_glyph['glyph_name'] as "Resonant Glyph"
        - voltage_response as system response
        - Processing time
        """
    }
}

# ============================================================================
# 5. DATABASE QUERY PATTERNS
# ============================================================================

QUERY_PATTERNS = {
    "fetch_glyphs_by_gates": {
        "sql": "SELECT glyph_name, description, gate FROM glyph_lexicon WHERE gate IN (?, ?, ?, ...)",
        "used_by": ["signal_parser.py", "emotional_os/glyphs/signal_parser.py"],
        "example_gates": ["Gate 4", "Gate 5", "Gate 6"],
        "typical_results": "2-15 glyphs per gate combination"
    },
    
    "count_total_glyphs": {
        "sql": "SELECT COUNT(*) FROM glyph_lexicon",
        "result": 292
    },
    
    "explore_glyphs_by_voltage": {
        "sql": "SELECT voltage_pair, glyph_name FROM glyph_lexicon WHERE voltage_pair LIKE ?",
        "used_by": "Analysis and debugging scripts"
    }
}

# ============================================================================
# 6. SIGNAL LEXICON ENHANCEMENT SYSTEM
# ============================================================================

LEXICON_ENHANCEMENT = {
    "integrate_glyph_lexicons.py": {
        "location": "/Users/taurinrobinson/saoriverse-console/integrate_glyph_lexicons.py",
        "purpose": "Convert CSV glyph data into signal keywords",
        "functions": {
            "load_glyph_lexicon_from_csv": "Load 292 glyphs from CSV",
            "generate_keywords_from_glyph_name": "Extract emotion words from glyph names",
            "generate_keywords_from_description": "Extract keywords from descriptions",
            "create_glyph_signal_mapping": "Create keyword→signal mappings",
            "enhance_signal_lexicon": "Merge glyph keywords into signal lexicon",
            "create_glyph_name_index": "Create fast lookup index"
        }
    },
    
    "learned_lexicon_system": {
        "file": "parser/learned_lexicon.json",
        "purpose": "Auto-learned keywords from user interactions",
        "keys": ["something", "dealing", "like", "system", "good", "enough", "better", "deeply", "compelled"],
        "signal_mapping": "Most mapped to 'ε' (insight)"
    }
}

# ============================================================================
# 7. VOLTAGE SIGNAL SYSTEM (Core Emotional Encoding)
# ============================================================================

VOLTAGE_SIGNALS = {
    "α": {
        "name": "Attunement/Devotion",
        "gates": ["Gate 6", "Gate 9"],
        "emotional_themes": ["sacred", "vow", "devotion", "offering", "purpose", "joy", "exaltation"],
        "keywords": ["devotional", "vow", "sacred", "offering", "embrace", "purpose"]
    },
    "β": {
        "name": "Boundary/Recognition",
        "gates": ["Gate 2", "Gate 9"],
        "emotional_themes": ["protection", "containment", "being seen", "held", "witnessed"],
        "keywords": ["boundary", "containment", "protection", "seen", "recognized", "worthy"]
    },
    "γ": {
        "name": "Ache/Longing",
        "gates": ["Gate 4", "Gate 9"],
        "emotional_themes": ["grief", "yearning", "longing", "loss", "desire", "depth"],
        "keywords": ["ache", "grief", "missing", "yearning", "longing", "fail", "terrified", "betrayed"]
    },
    "δ": {
        "name": "Stillness/Equilibrium",
        "gates": ["Gate 5"],
        "emotional_themes": ["peace", "quiet", "held", "balanced", "waiting", "pause"],
        "keywords": ["stillness", "peace", "calm", "silence", "quiet", "balanced"]
    },
    "ε": {
        "name": "Insight/Clarity",
        "gates": ["Gate 5", "Gate 6", "Gate 9"],
        "emotional_themes": ["understanding", "revelation", "spiral knowledge", "truth", "clarity"],
        "keywords": ["insight", "clarity", "knowing", "truth", "spiral", "understand"]
    },
    "θ": {
        "name": "Ceremony/Grief",
        "gates": ["Gate 2", "Gate 4", "Gate 10"],
        "emotional_themes": ["ritual", "sacred mourning", "collapse", "ceremony", "honoring"],
        "keywords": ["ceremony", "ritual", "sacred", "reverent", "mourning", "collapse"]
    },
    "λ": {
        "name": "Joy/Fulfillment",
        "gates": ["Gate 5"],
        "emotional_themes": ["joy", "delight", "happiness", "fulfillment", "celebration"],
        "keywords": ["joy", "excited", "proud", "happy", "grateful", "celebrate"]
    },
    "Ω": {
        "name": "Recognition/Mirror",
        "gates": ["Gate 6", "Gate 9"],
        "emotional_themes": ["being seen", "mutual recognition", "authentic meeting", "mirroring"],
        "keywords": ["recognition", "seen", "witnessed", "understood", "authentic", "genuine"]
    }
}

# ============================================================================
# 8. GATE SYSTEM (Emotional Complexity Levels)
# ============================================================================

GATES = {
    "Gate 2": {
        "signals": ["β", "θ"],
        "emotional_level": "Binary/Simple",
        "examples": ["Held Grief", "Boundary of Recognition"]
    },
    "Gate 4": {
        "signals": ["γ", "θ"],
        "emotional_level": "Layered Grief & Longing",
        "examples": ["Recursive Ache", "Acheful Mourning", "Spiral Ache"]
    },
    "Gate 5": {
        "signals": ["λ", "ε", "δ"],
        "emotional_level": "Complex Joy/Peace/Insight",
        "examples": ["Joy in Stillness", "Spiral Joy", "Joyful Insight"]
    },
    "Gate 6": {
        "signals": ["α", "Ω", "ε"],
        "emotional_level": "Spiritual/Devotional",
        "examples": ["Exalted Ache", "Devotional Fulfillment", "Ecstatic Recognition"]
    },
    "Gate 9": {
        "signals": ["α", "β", "γ", "δ", "ε", "Ω", "θ"],
        "emotional_level": "Full Spectrum Recognition",
        "examples": ["Recognized Ache", "Recognized Joy", "Mutual Mirror"]
    },
    "Gate 10": {
        "signals": ["θ"],
        "emotional_level": "Sacred Collapse",
        "examples": ["Ceremonial Collapse"]
    }
}

# ============================================================================
# 9. TESTING & VERIFICATION
# ============================================================================

TESTING_SCRIPTS = {
    "test_signal_matching.py": {
        "location": "/Users/taurinrobinson/saoriverse-console/test_signal_matching.py",
        "tests": 14,
        "messages_tested": [
            "Joy", "Sunset", "Grief", "Loneliness", "Betrayal", "Fury",
            "Fear", "Anxiety", "Love", "Gratitude", "Overwhelm", "Exhaustion",
            "Hope", "Light"
        ],
        "coverage": "All signal detection working"
    },
    
    "test_glyph_messages.py": {
        "location": "/Users/taurinrobinson/saoriverse-console/test_glyph_messages.py",
        "categories": 15,
        "total_messages": 100+
    }
}

# ============================================================================
# 10. PRODUCTION DEPLOYMENT
# ============================================================================

PRODUCTION_SETUP = {
    "live_at": "https://firstperson.chat",
    "platform": "Railway",
    "database": "emotional_os/glyphs/glyphs.db (local SQLite)",
    "signal_lexicon": "parser/signal_lexicon.json (152 keywords)",
    "processing_mode": "local (no external API dependency)",
    "performance": {
        "signal_parsing": "0.00-0.02s",
        "glyph_lookup": "0.01s",
        "total_latency": "0.02s per message"
    }
}

# ============================================================================
# SUMMARY
# ============================================================================

"""
The FirstPerson Emotional OS has a complete end-to-end system for:

✓ Loading 292 emotional glyphs from SQLite database
✓ Matching user input against 152+ emotional keywords
✓ Mapping keywords to voltage signals (α-θ, λ, Ω)
✓ Activating appropriate emotional gates (Gate 2-10)
✓ Retrieving contextually relevant glyphs
✓ Generating emotionally-tuned responses
✓ Learning new keywords over time

All code paths are in place and functional.
The system is live and processing messages on firstperson.chat.
"""
