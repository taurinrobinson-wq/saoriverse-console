#!/usr/bin/env python3
"""
Glyph Learning Engine - Real-time glyph generation from user inputs

When signal_parser fails to find a matching glyph, this module:
1. Analyzes emotional language patterns in the input
2. Finds closest existing glyphs by semantic similarity
3. Generates a new glyph candidate
4. Maps emotional signals to gates
5. Stores in shared database with metadata

Philosophy: The system learns through every interaction.
No user ever gets a templated response.
"""

import hashlib
import json
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional
import os

try:
    from parser.nrc_lexicon_loader import nrc
    HAS_NRC = True
except ImportError:
    HAS_NRC = False
    nrc = None


class GlyphLearner:
    """Learn and generate new glyphs from emotional input."""

    def __init__(self, db_path: Optional[str] = None):
        # Use an absolute path inside the package by default to avoid cwd-dependent failures
        if not db_path:
            db_path = os.path.join(os.path.dirname(__file__), 'glyphs.db')
        self.db_path = db_path
        self.nrc = nrc if HAS_NRC else None
        self._ensure_learning_tables()

    def _ensure_learning_tables(self):
        """Create learning tables if they don't exist."""
        try:
            # Ensure DB directory exists (mitigates cwd / cleanup race conditions in tests)
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Table for candidate glyphs (not yet in production)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS glyph_candidates (
                    id INTEGER PRIMARY KEY,
                    glyph_name TEXT UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    emotional_signal TEXT,
                    gates TEXT,
                    source_input TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confidence_score REAL,
                    validation_status TEXT DEFAULT 'pending',
                    usage_count INTEGER DEFAULT 0,
                    promoted_to_production BOOLEAN DEFAULT 0
                )
            """)

            # Track which glyphs are system-wide (used across multiple users)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS glyph_usage_log (
                    id INTEGER PRIMARY KEY,
                    glyph_name TEXT NOT NULL,
                    user_hash TEXT,
                    input_text TEXT,
                    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    relevance_score REAL,
                    user_validation INTEGER DEFAULT -1
                )
            """)

            # Emotional language patterns (for learning)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emotional_patterns (
                    id INTEGER PRIMARY KEY,
                    pattern TEXT UNIQUE NOT NULL,
                    emotional_category TEXT,
                    nrc_emotion TEXT,
                    intensity REAL,
                    frequency_count INTEGER DEFAULT 1,
                    associated_glyphs TEXT
                )
            """)

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error creating learning tables: {e}")

    def analyze_input_for_glyph_generation(
        self,
        input_text: str,
        signals: List[Dict],
        user_hash: Optional[str] = None
    ) -> Dict:
        """
        Analyze input when no glyph matches found.
        Generate candidate glyph with all metadata.
        """

        if not user_hash:
            user_hash = self._hash_user(input_text)

        # 1. Extract emotional language patterns
        emotional_terms = self._extract_emotional_language(input_text)
        nrc_analysis = self._analyze_with_nrc(input_text) if self.nrc else {}

        # 2. Find closest existing glyphs
        similar_glyphs = self._find_similar_glyphs(
            emotional_terms,
            nrc_analysis
        )

        # 3. Generate glyph candidate
        glyph_candidate = self._generate_glyph_candidate(
            input_text=input_text,
            emotional_terms=emotional_terms,
            nrc_analysis=nrc_analysis,
            signals=signals,
            similar_glyphs=similar_glyphs
        )

        # 4. Calculate confidence
        confidence = self._calculate_confidence(
            glyph_candidate,
            signals,
            emotional_terms
        )

        return {
            "glyph_name": glyph_candidate.get("name"),
            "description": glyph_candidate.get("description"),
            "emotional_signal": glyph_candidate.get("signal"),
            "gates": glyph_candidate.get("gates"),
            "emotional_terms": emotional_terms,
            "nrc_analysis": nrc_analysis,
            "similar_glyphs": similar_glyphs,
            "confidence_score": confidence,
            "metadata": {
                "source_input": input_text,
                "created_by": user_hash,
                "created_at": datetime.now().isoformat(),
                "learning_status": "candidate"
            }
        }

    def _extract_emotional_language(self, text: str) -> Dict[str, List[str]]:
        """Extract emotional vocabulary from input."""
        text_lower = text.lower()

        categories = {
            "intensity_words": [],
            "state_words": [],
            "relation_words": [],
            "time_words": [],
            "body_words": [],
        }

        # Intensity indicators
        intensity = ["so", "very", "deeply", "incredibly", "almost",
                     "barely", "overwhelming", "crushing", "suffocating"]
        for word in intensity:
            if word in text_lower:
                categories["intensity_words"].append(word)

        # Emotional states
        states = ["feel", "felt", "feeling", "seem",
                  "seemed", "appear", "sound", "taste", "smell"]
        for word in states:
            if word in text_lower:
                categories["state_words"].append(word)

        # Relational words
        relations = ["with", "without", "toward",
                     "away", "between", "among", "through"]
        for word in relations:
            if word in text_lower:
                categories["relation_words"].append(word)

        # Temporal markers
        times = ["now", "always", "never", "before", "after",
                 "during", "while", "when", "yesterday", "tomorrow"]
        for word in times:
            if word in text_lower:
                categories["time_words"].append(word)

        # Body/visceral language
        body = ["heart", "gut", "breath", "chest", "throat",
                "hands", "trembling", "aching", "burning", "numb"]
        for word in body:
            if word in text_lower:
                categories["body_words"].append(word)

        return categories

    def _analyze_with_nrc(self, text: str) -> Dict:
        """Use NRC lexicon for emotion classification."""
        if not self.nrc:
            return {}

        try:
            emotions = self.nrc.analyze_text(text)
            return emotions if emotions else {}
        except Exception:
            return {}

    def _find_similar_glyphs(
        self,
        emotional_terms: Dict,
        nrc_analysis: Dict,
        top_k: int = 3
    ) -> List[Dict]:
        """Find existing glyphs semantically similar to this input."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all existing glyphs
            cursor.execute(
                "SELECT glyph_name, description FROM glyph_lexicon LIMIT 50")
            existing_glyphs = cursor.fetchall()
            conn.close()

            # Score each glyph by semantic similarity
            scored = []
            for glyph_name, description in existing_glyphs:
                score = self._semantic_similarity_score(
                    description,
                    emotional_terms,
                    nrc_analysis
                )
                if score > 0.3:  # Only include if somewhat similar
                    scored.append({
                        "name": glyph_name,
                        "description": description,
                        "similarity_score": score
                    })

            # Return top K
            scored.sort(key=lambda x: x["similarity_score"], reverse=True)
            return scored[:top_k]

        except Exception:
            return []

    def _semantic_similarity_score(
        self,
        glyph_description: str,
        emotional_terms: Dict,
        nrc_analysis: Dict
    ) -> float:
        """Score how similar a glyph is to the emotional input."""
        score = 0.0

        # Check if glyph description contains emotional terms
        desc_lower = glyph_description.lower()

        for term_list in emotional_terms.values():
            for term in term_list:
                if term in desc_lower:
                    score += 0.1

        # Check NRC emotions match
        if nrc_analysis:
            for emotion in nrc_analysis.keys():
                if emotion.lower() in desc_lower:
                    score += 0.2

        return min(score, 1.0)  # Cap at 1.0

    def _generate_glyph_candidate(
        self,
        input_text: str,
        emotional_terms: Dict,
        nrc_analysis: Dict,
        signals: List[Dict],
        similar_glyphs: List[Dict]
    ) -> Dict:
        """Generate a new glyph candidate."""

        # 1. Create glyph name from emotional language + existing patterns
        name = self._generate_glyph_name(
            input_text,
            emotional_terms,
            nrc_analysis,
            similar_glyphs
        )

        # 2. Create description
        description = self._generate_glyph_description(
            input_text,
            emotional_terms,
            nrc_analysis,
            similar_glyphs
        )

        # 3. Map signals to gates
        gates = self._map_signals_to_gates(signals)

        # 4. Determine primary signal
        primary_signal = signals[0].get(
            "signal", "unknown") if signals else "unknown"

        return {
            "name": name,
            "description": description,
            "signal": primary_signal,
            "gates": gates
        }

    def _generate_glyph_name(
        self,
        input_text: str,
        emotional_terms: Dict,
        nrc_analysis: Dict,
        similar_glyphs: List[Dict]
    ) -> str:
        """Generate a meaningful glyph name."""

        # Extract key words from input
        key_words = []
        for word in input_text.split():
            if len(word) > 4 and word.lower() not in ['feel', 'feeling', 'felt']:
                key_words.append(word.lower().strip('.,!?'))

        # Use NRC emotion if available
        if nrc_analysis:
            primary_emotion = max(nrc_analysis.items(),
                                  key=lambda x: x[1])[0].title()
        else:
            primary_emotion = ""

        # Combine with emotional terms
        if emotional_terms.get("intensity_words"):
            intensity = emotional_terms["intensity_words"][0].title()
        else:
            intensity = ""

        # Build name: "Intensity + Emotion + State"
        parts = [p for p in [intensity, primary_emotion] if p]

        if key_words:
            parts.append(key_words[0].title())

        if not parts:
            parts = ["Emerging", "Emotion"]

        name = " ".join(parts[:2])  # Keep to 2 words max

        return name

    def _generate_glyph_description(
        self,
        input_text: str,
        emotional_terms: Dict,
        nrc_analysis: Dict,
        similar_glyphs: List[Dict]
    ) -> str:
        """Generate poetic glyph description."""

        # Extract essence from input
        essence = input_text[:100].strip()

        # Build description blending user language + existing patterns
        descriptions = [
            f"The emotion of: {essence}."
        ]

        # Add emotional category from NRC
        if nrc_analysis:
            emotions_detected = ", ".join(nrc_analysis.keys())
            descriptions.append(f"A convergence of {emotions_detected}.")

        # Add relational element
        if emotional_terms.get("relation_words"):
            relation = emotional_terms["relation_words"][0]
            descriptions.append(f"Movement {relation} sacred threshold.")

        # Reference similar glyphs
        if similar_glyphs:
            similar_names = [g["name"] for g in similar_glyphs[:2]]
            descriptions.append(
                f"Kin to {similar_names[0].lower()}, yet distinct in its calling."
            )

        return " ".join(descriptions)

    def _map_signals_to_gates(self, signals: List[Dict]) -> List[str]:
        """Map emotional signals to gate numbers."""
        if not signals:
            return ["Gate 5"]  # Default

        # Use signal voltages to determine gate
        gates = set()
        for signal in signals:
            voltage = signal.get("voltage", "medium")
            tone = signal.get("tone", "unknown")

            # Simple gate mapping (can be expanded)
            if voltage == "high":
                gates.add("Gate 4")  # High intensity
            elif voltage == "medium":
                gates.add("Gate 5")  # Medium
            else:
                gates.add("Gate 6")  # Low

            # Tone-based gate
            if tone in ["joy", "devotion", "recognition"]:
                gates.add("Gate 6")
            elif tone in ["grief", "longing"]:
                gates.add("Gate 4")

        return list(gates) if gates else ["Gate 5"]

    def _calculate_confidence(
        self,
        glyph_candidate: Dict,
        signals: List[Dict],
        emotional_terms: Dict
    ) -> float:
        """Calculate confidence in the generated glyph."""
        score = 0.5  # Start at neutral

        # Increase confidence if we have good signals
        if signals and len(signals) > 0:
            score += 0.2

        # Increase if we have emotional terms
        term_count = sum(len(v) for v in emotional_terms.values())
        if term_count > 3:
            score += 0.2

        # Cap at 1.0
        return min(score, 0.95)  # Leave room for human validation

    def log_glyph_candidate(self, candidate: Dict) -> bool:
        """Store candidate glyph in database."""
        metadata = candidate.get("metadata", {})

        sql = """
            INSERT INTO glyph_candidates
            (glyph_name, description, emotional_signal, gates, source_input, created_by, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(glyph_name) DO UPDATE SET
                description=excluded.description,
                emotional_signal=excluded.emotional_signal,
                gates=excluded.gates,
                source_input=excluded.source_input,
                created_by=excluded.created_by,
                confidence_score=excluded.confidence_score,
                validation_status='pending',
                usage_count = usage_count + 1
        """

        params = (
            candidate.get("glyph_name"),
            candidate.get("description"),
            candidate.get("emotional_signal"),
            json.dumps(candidate.get("gates", [])),
            metadata.get("source_input"),
            metadata.get("created_by"),
            candidate.get("confidence_score")
        )

        # Retry loop to mitigate transient 'database is locked' errors
        attempts = 0
        max_attempts = 3
        backoff = 0.1
        conn = None
        while attempts < max_attempts:
            try:
                conn = sqlite3.connect(self.db_path, timeout=10)
                # Prefer WAL mode to reduce writer contention
                try:
                    conn.execute("PRAGMA journal_mode=WAL;")
                except Exception:
                    pass

                cursor = conn.cursor()
                cursor.execute(sql, params)
                conn.commit()
                conn.close()
                return True
            except sqlite3.OperationalError as e:
                attempts += 1
                # If it's a lock, wait and retry a few times
                if 'locked' in str(e).lower() and attempts < max_attempts:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                print(f"Error logging glyph candidate: {e}")
                try:
                    if conn:
                        conn.close()
                except Exception:
                    pass
                return False
            except Exception as e:
                print(f"Error logging glyph candidate: {e}")
                try:
                    if conn:
                        conn.close()
                except Exception:
                    pass
                return False
        # If we exhausted retries, return False
        return False

    def log_glyph_usage(
        self,
        glyph_name: str,
        user_hash: str,
        input_text: str,
        relevance_score: float = 1.0
    ) -> bool:
        """Track glyph usage across users."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO glyph_usage_log
                (glyph_name, user_hash, input_text, relevance_score)
                VALUES (?, ?, ?, ?)
            """, (glyph_name, user_hash, input_text, relevance_score))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging usage: {e}")
            return False

    @staticmethod
    def _hash_user(identifier: str) -> str:
        """Create anonymous user hash."""
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]

    def promote_candidate_to_production(self, glyph_name: str) -> bool:
        """Move validated glyph from candidates to production."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get candidate
            cursor.execute(
                "SELECT description, emotional_signal, gates FROM glyph_candidates WHERE glyph_name = ?",
                (glyph_name,)
            )
            row = cursor.fetchone()

            if not row:
                return False

            description, signal, gates = row
            gates_list = json.loads(gates) if isinstance(gates, str) else gates

            # Insert into production glyph_lexicon
            cursor.execute("""
                INSERT INTO glyph_lexicon (glyph_name, description, gate)
                VALUES (?, ?, ?)
            """, (glyph_name, description, gates_list[0] if gates_list else "Gate 5"))

            # Mark candidate as promoted
            cursor.execute(
                "UPDATE glyph_candidates SET promoted_to_production = 1 WHERE glyph_name = ?",
                (glyph_name,)
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error promoting glyph: {e}")
            return False

    def get_learning_stats(self) -> Dict:
        """Get system learning statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM glyph_candidates WHERE validation_status = 'pending'")
            pending = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM glyph_candidates WHERE promoted_to_production = 1")
            promoted = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(DISTINCT glyph_name) FROM glyph_usage_log")
            unique_glyphs_used = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(DISTINCT user_hash) FROM glyph_usage_log")
            unique_users = cursor.fetchone()[0]

            conn.close()

            return {
                "pending_candidates": pending,
                "promoted_glyphs": promoted,
                "unique_glyphs_used": unique_glyphs_used,
                "unique_users": unique_users
            }
        except Exception as e:
            return {"error": str(e)}
