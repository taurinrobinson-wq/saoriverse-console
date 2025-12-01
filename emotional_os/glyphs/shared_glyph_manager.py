#!/usr/bin/env python3
"""
Shared Glyph Manager

Handles the architecture that allows:
- ALL users contribute to a SHARED glyph database
- But EACH user sees a personalized experience
- Glyph versioning and consensus weighting
- User segregation at query level, not database level

Key insight: Separation happens in the queries and presentation layer,
not in the storage layer. One unified glyphs.db, but infinite user views.
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class SharedGlyphManager:
    """
    Manages the shared glyph database while maintaining per-user segregation.

    Database Architecture:
    - glyph_lexicon: Base glyphs (shared across all users)
    - glyph_versions: Track evolution of each glyph over time
    - glyph_usage_log: Track how each glyph is used across users
    - user_glyph_preferences: Track which glyphs each user adopts
    - glyph_candidates: Candidate glyphs awaiting consensus promotion
    """

    def __init__(self, db_path: Optional[str] = None):
        # Default to an absolute DB path within the package to avoid test cwd issues
        if not db_path:
            db_path = os.path.join(os.path.dirname(__file__), "glyphs.db")
        self.db_path = db_path
        self._ensure_shared_tables()

    def _ensure_shared_tables(self):
        """Create shared glyph management tables."""
        try:
            # Ensure DB directory exists to avoid sqlite3 'unable to open database file'
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Core: Track glyph versioning
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS glyph_versions (
                    id INTEGER PRIMARY KEY,
                    glyph_name TEXT NOT NULL,
                    version_num INTEGER,
                    description TEXT,
                    emotional_signal TEXT,
                    gates TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    adoption_count INTEGER DEFAULT 0,
                    quality_score REAL DEFAULT 0.5,
                    is_active BOOLEAN DEFAULT 0,
                    UNIQUE(glyph_name, version_num)
                )
            """
            )

            # Track user preferences (which glyph versions they prefer)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_glyph_preferences (
                    id INTEGER PRIMARY KEY,
                    user_hash TEXT NOT NULL,
                    glyph_name TEXT NOT NULL,
                    version_num INTEGER,
                    first_encountered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    usage_count INTEGER DEFAULT 0,
                    rating INTEGER DEFAULT -1,
                    UNIQUE(user_hash, glyph_name)
                )
            """
            )

            # Track glyph quality over time (consensus system)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS glyph_consensus (
                    id INTEGER PRIMARY KEY,
                    glyph_name TEXT UNIQUE NOT NULL,
                    total_users_adopted INTEGER DEFAULT 0,
                    positive_feedback_count INTEGER DEFAULT 0,
                    negative_feedback_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    consensus_strength REAL DEFAULT 0.0
                )
            """
            )

            # Track emotional territory coverage
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS emotional_territory (
                    id INTEGER PRIMARY KEY,
                    emotional_area TEXT UNIQUE NOT NULL,
                    primary_glyphs TEXT,
                    coverage_quality REAL,
                    needs_development BOOLEAN DEFAULT 0,
                    last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error creating shared tables: {e}")

    # ===== USER SEGREGATION (How users see glyphs) =====

    def get_glyphs_for_user(
        self, user_hash: str, emotional_signal: Optional[str] = None, gates: Optional[List[str]] = None, top_k: int = 5
    ) -> List[Dict]:
        """
        Get glyphs that are:
        1. Relevant to user's emotional context
        2. Adopted by user or highly consensual
        3. Ranked by adoption and quality

        CRITICAL: Different users can see different orderings of the same glyphs
        based on personal adoption history, but all glyphs come from shared DB.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Query: Get glyphs matching signal/gates, ordered by:
            # 1. User adoption (does this user use it?)
            # 2. Consensus (how many users adopted it?)
            # 3. Quality (how well does it work?)

            query = """
                SELECT DISTINCT
                    gv.glyph_name,
                    gv.description,
                    gv.gates,
                    gv.created_at,
                    COALESCE(ugp.usage_count, 0) as user_usage,
                    gc.total_users_adopted,
                    gc.consensus_strength,
                    gv.quality_score
                FROM glyph_versions gv
                LEFT JOIN glyph_consensus gc ON gv.glyph_name = gc.glyph_name
                LEFT JOIN user_glyph_preferences ugp ON 
                    gv.glyph_name = ugp.glyph_name AND ugp.user_hash = ?
                WHERE gv.is_active = 1
            """

            params: List = [user_hash]

            # Add emotional signal filter if provided
            if emotional_signal:
                query += " AND gv.emotional_signal = ?"
                params.append(emotional_signal)

            # Add gate filter if provided
            if gates:
                gate_conditions = " OR ".join(["gv.gates LIKE ?" for _ in gates])
                query += f" AND ({gate_conditions})"
                params.extend([f"%{g}%" for g in gates])

            # Order by: personal usage first, then consensus, then quality
            query += """
                ORDER BY 
                    user_usage DESC,
                    gc.consensus_strength DESC,
                    gv.quality_score DESC
                LIMIT ?
            """
            params.append(str(top_k))

            cursor.execute(query, params)
            results = cursor.fetchall()

            glyphs = []
            for row in results:
                glyphs.append(
                    {
                        "name": row[0],
                        "description": row[1],
                        "gates": json.loads(row[2]) if row[2] else [],
                        "created_at": row[3],
                        "user_adoption": row[4],  # How much THIS user uses it
                        "global_adoption": row[5],  # How many users total
                        "consensus_strength": row[6],  # Agreement level
                        "quality_score": row[7],
                    }
                )

            conn.close()
            return glyphs

        except Exception as e:
            print(f"Error fetching user glyphs: {e}")
            return []

    def get_system_view_glyphs(self, top_k: int = 20) -> List[Dict]:
        """
        Get most consensually-accepted glyphs (for admin/system view).
        Shows strongest consensus glyphs regardless of individual user paths.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    gv.glyph_name,
                    gv.description,
                    gv.gates,
                    gc.total_users_adopted,
                    gc.consensus_strength,
                    gv.quality_score
                FROM glyph_versions gv
                LEFT JOIN glyph_consensus gc ON gv.glyph_name = gc.glyph_name
                WHERE gv.is_active = 1
                ORDER BY gc.consensus_strength DESC, gc.total_users_adopted DESC
                LIMIT ?
            """,
                (top_k,),
            )

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    "name": row[0],
                    "description": row[1],
                    "gates": json.loads(row[2]) if row[2] else [],
                    "adoption": row[3],
                    "consensus": row[4],
                    "quality": row[5],
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error getting system view: {e}")
            return []

    # ===== USER ADOPTION (How to build consensus) =====

    def record_glyph_adoption(self, user_hash: str, glyph_name: str, quality_rating: Optional[int] = None) -> bool:
        """
        Record that a user adopted/used a glyph.
        This is HOW the system learns globally.

        When user uses a glyph, they're voting for it.
        High adoption + high ratings = strong consensus.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Record in user preferences
            cursor.execute(
                """
                INSERT INTO user_glyph_preferences
                (user_hash, glyph_name, usage_count, rating)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(user_hash, glyph_name) DO UPDATE SET
                    usage_count = usage_count + 1,
                    last_used = CURRENT_TIMESTAMP,
                    rating = COALESCE(?, rating)
            """,
                (user_hash, glyph_name, quality_rating, quality_rating),
            )

            # Update consensus (aggregate usage)
            cursor.execute(
                """
                SELECT COUNT(DISTINCT user_hash) FROM user_glyph_preferences
                WHERE glyph_name = ?
            """,
                (glyph_name,),
            )

            adoption_count = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO glyph_consensus
                (glyph_name, total_users_adopted)
                VALUES (?, ?)
                ON CONFLICT(glyph_name) DO UPDATE SET
                    total_users_adopted = ?
            """,
                (glyph_name, adoption_count, adoption_count),
            )

            # Update quality score if feedback provided
            if quality_rating is not None:
                if quality_rating > 0:
                    cursor.execute(
                        """
                        UPDATE glyph_consensus SET positive_feedback_count = positive_feedback_count + 1
                        WHERE glyph_name = ?
                    """,
                        (glyph_name,),
                    )
                elif quality_rating < 0:
                    cursor.execute(
                        """
                        UPDATE glyph_consensus SET negative_feedback_count = negative_feedback_count + 1
                        WHERE glyph_name = ?
                    """,
                        (glyph_name,),
                    )

            # Calculate consensus strength
            cursor.execute(
                """
                SELECT total_users_adopted, positive_feedback_count, negative_feedback_count
                FROM glyph_consensus WHERE glyph_name = ?
            """,
                (glyph_name,),
            )

            row = cursor.fetchone()
            if row:
                total, pos, neg = row
                consensus_strength = (pos - neg) / max(total, 1)
                # Clamp -1 to 1
                consensus_strength = max(-1.0, min(1.0, consensus_strength))

                cursor.execute(
                    """
                    UPDATE glyph_consensus SET consensus_strength = ?
                    WHERE glyph_name = ?
                """,
                    (consensus_strength, glyph_name),
                )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error recording adoption: {e}")
            return False

    # ===== GLYPH VERSIONING (How to track evolution) =====

    def create_glyph_version(
        self, glyph_name: str, description: str, emotional_signal: str, gates: List[str], created_by: str
    ) -> int:
        """
        Create a new version of a glyph.
        Glyphs evolve as users refine them.

        Returns: version number (1, 2, 3, ...)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get next version number
            cursor.execute("SELECT MAX(version_num) FROM glyph_versions WHERE glyph_name = ?", (glyph_name,))
            last_version = cursor.fetchone()[0]
            next_version = (last_version or 0) + 1

            # Insert new version
            cursor.execute(
                """
                INSERT INTO glyph_versions
                (glyph_name, version_num, description, emotional_signal, gates, created_by, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
                (glyph_name, next_version, description, emotional_signal, json.dumps(gates), created_by),
            )

            # Deactivate previous version
            if last_version:
                cursor.execute(
                    """
                    UPDATE glyph_versions SET is_active = 0
                    WHERE glyph_name = ? AND version_num = ?
                """,
                    (glyph_name, last_version),
                )

            conn.commit()
            conn.close()

            return next_version

        except Exception as e:
            print(f"Error creating glyph version: {e}")
            return 0

    def get_glyph_history(self, glyph_name: str) -> List[Dict]:
        """Get the evolution history of a glyph."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT version_num, description, created_at, created_by, adoption_count, quality_score, is_active
                FROM glyph_versions
                WHERE glyph_name = ?
                ORDER BY version_num ASC
            """,
                (glyph_name,),
            )

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    "version": row[0],
                    "description": row[1],
                    "created_at": row[2],
                    "created_by": row[3],
                    "adoption": row[4],
                    "quality": row[5],
                    "active": bool(row[6]),
                }
                for row in results
            ]

        except Exception as e:
            print(f"Error getting glyph history: {e}")
            return []

    # ===== EMOTIONAL TERRITORY MAPPING =====

    def analyze_coverage_gaps(self) -> Dict:
        """
        Identify emotional territories that are under-served.
        This guides future glyph generation.

        Returns dictionary of emotional areas and coverage status.
        """

        emotional_territories = {
            "grief": ["death", "loss", "mourning", "absence", "gone"],
            "longing": ["missing", "yearning", "distant", "unreachable"],
            "containment": ["holding", "suppressing", "masked", "hidden"],
            "insight": ["understanding", "realization", "clarity", "epiphany"],
            "joy": ["happiness", "elation", "celebration", "lightness"],
            "devotion": ["commitment", "loyalty", "dedication", "service"],
            "recognition": ["seen", "known", "accepted", "belonging"],
            "shame": ["embarrassment", "humiliation", "exposure", "unworthiness"],
            "fear": ["terror", "anxiety", "dread", "uncertainty"],
            "love": ["affection", "tenderness", "care", "connection"],
        }

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            coverage_report = {}

            for territory, keywords in emotional_territories.items():
                # Count glyphs that touch this territory
                query_parts = " OR ".join(["description LIKE ?" for _ in keywords])
                cursor.execute(
                    f"SELECT COUNT(*) FROM glyph_versions WHERE ({query_parts}) AND is_active = 1",
                    [f"%{k}%" for k in keywords],
                )

                glyph_count = cursor.fetchone()[0]

                # Coverage quality: 0-3 glyphs = poor, 4-7 = fair, 8+ = strong
                if glyph_count == 0:
                    quality = "CRITICAL"
                    needs_dev = True
                elif glyph_count < 4:
                    quality = "POOR"
                    needs_dev = True
                elif glyph_count < 8:
                    quality = "FAIR"
                    needs_dev = False
                else:
                    quality = "STRONG"
                    needs_dev = False

                coverage_report[territory] = {
                    "coverage_quality": quality,
                    "glyph_count": glyph_count,
                    "needs_development": needs_dev,
                    "keywords": keywords,
                }

            conn.close()
            return coverage_report

        except Exception as e:
            print(f"Error analyzing coverage: {e}")
            return {}

    def recommend_new_glyphs_for_gaps(self) -> List[Dict]:
        """
        Based on coverage analysis, recommend emotional territories
        that should have new glyphs generated.
        """

        coverage = self.analyze_coverage_gaps()
        recommendations = []

        for territory, info in coverage.items():
            if info["needs_development"]:
                recommendations.append(
                    {
                        "emotional_territory": territory,
                        "priority": "CRITICAL" if info["coverage_quality"] == "CRITICAL" else "HIGH",
                        "current_coverage": info["glyph_count"],
                        "gap_description": f"Only {info['glyph_count']} glyph(s) cover this territory",
                        "suggested_keywords": info["keywords"],
                    }
                )

        return sorted(recommendations, key=lambda x: x["current_coverage"])

    # ===== SYSTEM HEALTH MONITORING =====

    def get_system_health_report(self) -> Dict:
        """
        Get comprehensive report on system learning progress.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Total glyphs
            cursor.execute("SELECT COUNT(*) FROM glyph_versions WHERE is_active = 1")
            total_glyphs = cursor.fetchone()[0]

            # Total users
            cursor.execute("SELECT COUNT(DISTINCT user_hash) FROM user_glyph_preferences")
            total_users = cursor.fetchone()[0]

            # Average adoption (glyphs per user)
            cursor.execute(
                """
                SELECT AVG(usage_count) FROM user_glyph_preferences
            """
            )
            avg_adoption = cursor.fetchone()[0] or 0

            # Strongest consensus glyphs
            cursor.execute(
                """
                SELECT COUNT(*) FROM glyph_consensus WHERE consensus_strength > 0.5
            """
            )
            strong_consensus = cursor.fetchone()[0]

            # Pending candidates
            cursor.execute(
                """
                SELECT COUNT(*) FROM glyph_candidates WHERE promoted_to_production = 0
            """
            )
            pending_candidates = cursor.fetchone()[0]

            conn.close()

            return {
                "total_active_glyphs": total_glyphs,
                "unique_users_contributed": total_users,
                "average_glyph_usage": round(avg_adoption, 2),
                "glyphs_with_strong_consensus": strong_consensus,
                "pending_candidate_glyphs": pending_candidates,
                "system_coverage": self.analyze_coverage_gaps(),
                "recommendations": self.recommend_new_glyphs_for_gaps(),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": str(e)}


# Convenience function
def get_user_segregated_view(
    user_hash: str, emotional_signal: str, gates: List[str], manager: Optional[SharedGlyphManager] = None
) -> List[Dict]:
    """
    Get glyphs for a user, ordered by their personal adoption history.
    This IS how user segregation works: different query results per user,
    but all from the same shared database.
    """

    if not manager:
        manager = SharedGlyphManager()

    return manager.get_glyphs_for_user(user_hash=user_hash, emotional_signal=emotional_signal, gates=gates, top_k=5)
