#!/usr/bin/env python3
"""
Hybrid Processor with Dynamic Glyph Evolution

Extends the conversation pipeline to automatically:
1. Learn from user-AI exchanges through hybrid processor
2. Expand lexicon with adaptive signal extraction
3. Detect new emotional patterns
4. Generate new glyphs dynamically
5. Make new glyphs available for next dialogue turns

This is the complete integration point for the full system.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from uuid import uuid4

# Local-learning primitives
try:
    from learning.local_learner import LocalLearner

    LOCAL_LEARNER_AVAILABLE = True
except Exception:
    LocalLearner = None
    LOCAL_LEARNER_AVAILABLE = False

# optional writer for staging near-duplicates
try:
    from learning.writer import DEFAULT_LEARNING_DIR, append_event
except Exception:
    append_event = None
    DEFAULT_LEARNING_DIR = None

# Import lexicon-aware response generation
try:
    from lexicon_aware_response_generator import LexiconAwareResponseGenerator

    LEXICON_AWARE_AVAILABLE = True
except ImportError:
    LEXICON_AWARE_AVAILABLE = False

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class LocalEvolution:
    """Lightweight local-only evolution handler with deduplication.

    Adds a normalized-phrase deduplication check against an on-disk
    glyph lexicon and (optionally) `relational_memory`. Near-duplicates
    are staged to a JSONL file rather than emitted as new glyphs.
    """

    def __init__(self, learner: Optional[Any] = None, accept_threshold: float = 0.8):
        if learner is None:
            if LOCAL_LEARNER_AVAILABLE:
                learner = LocalLearner()
            else:
                raise RuntimeError("No LocalLearner available for LocalEvolution")

        self.learner = learner
        self.accept_threshold = accept_threshold

        # Deduplication cache (normalized phrases)
        self._existing_normalized = set()
        self._lexicon_loaded = False
        # staging file for near-duplicates
        self._near_dup_staging = None
        if DEFAULT_LEARNING_DIR:
            self._near_dup_staging = os.path.join(DEFAULT_LEARNING_DIR, "near_duplicate_staging.jsonl")

        # pre-load lexicon if available (best-effort)
        try:
            self._load_existing_lexicon()
        except Exception:
            pass

    def process_dialogue_exchange(
        self,
        *,
        user_id: str,
        conversation_id: str,
        user_input: str,
        ai_response: str,
        emotional_signals: List[Dict],
        glyphs: Optional[List[Dict]] = None,
    ) -> Dict:
        """Process a dialogue exchange and persist candidate learning events.

        Returns a dict with keys: learning_result, lexicon_updates,
        new_glyphs_generated, pattern_analysis
        """
        candidate = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "user_input": user_input,
            "ai_response": ai_response,
            "signals": emotional_signals or [],
            "glyphs": glyphs or [],
        }

        # Compute a confidence score for the candidate (without yet persisting)
        confidence = None
        try:
            confidence = self.learner.score_candidate(candidate)
        except Exception:
            confidence = None

        # Deduplication check: normalized phrase comparison + recent memory lookup
        dedup_reason = None
        is_duplicate = False
        try:
            cand_norm = self._normalize(user_input)
            # exact match check against loaded lexicon cache
            if cand_norm in self._existing_normalized:
                is_duplicate = True
                dedup_reason = f"exact match existing glyph: '{user_input}'"
            else:
                # check recent relational memory for overlaps
                try:
                    import relational_memory

                    recent = relational_memory.list_recent(500)
                    for cap in recent or []:
                        text = None
                        if hasattr(cap, "text"):
                            text = getattr(cap, "text")
                        elif hasattr(cap, "payload"):
                            try:
                                text = str(getattr(cap, "payload"))
                            except Exception:
                                text = None
                        else:
                            try:
                                text = str(cap)
                            except Exception:
                                text = None

                        if not text:
                            continue
                        if self._token_similarity(cand_norm, self._normalize(text)) >= 0.9:
                            is_duplicate = True
                            dedup_reason = f"similar to recent memory: '{text[:80]}'"
                            break
                except Exception:
                    # relational memory not present or failed
                    pass

                # If still not duplicate, check lexicon entries with token-overlap similarity
                if not is_duplicate and self._existing_normalized:
                    for existing in self._existing_normalized:
                        if self._token_similarity(cand_norm, existing) >= 0.9:
                            is_duplicate = True
                            dedup_reason = f"similar to existing glyph: '{existing}'"
                            break
        except Exception:
            # Any dedup error should not stop processing
            dedup_reason = None

        # Attach dedup metadata to candidate so audit trail contains reason
        if dedup_reason:
            candidate["dedup_reason"] = dedup_reason
            candidate["dedup"] = True
        else:
            candidate["dedup"] = False

        # Stage the candidate and persist
        try:
            self.learner.collect_candidate(candidate, source="local_evolution")
            self.learner.persist()
        except Exception:
            logger.exception("Failed to persist candidate")

        new_glyphs = []
        # If duplicate found, stage the near-duplicate and do not emit a glyph
        if is_duplicate:
            # write a near-duplicate staging record
            staging_evt = {
                "source": "local_evolution",
                "event_type": "near_duplicate",
                "payload": candidate,
                "confidence": confidence,
                "match_reason": dedup_reason,
            }
            try:
                if append_event and self._near_dup_staging:
                    append_event(self._near_dup_staging, staging_evt)
            except Exception:
                logger.exception("Failed to write near-duplicate staging event")
        else:
            # Only create a new glyph when confidence is high and it's not a duplicate
            if confidence is not None and confidence >= self.accept_threshold:
                glyph = {
                    "id": str(uuid4()),
                    "name": f"auto_{user_id}_{conversation_id}",
                    "symbol": "⚑",
                    "core_emotions": [s.get("signal") or s.get("name") for s in (emotional_signals or [])],
                    "examples": [user_input[:200]],
                    "confidence": confidence,
                }
                new_glyphs.append(glyph)

        return {
            "learning_result": {"success": True, "persisted": True, "confidence": confidence},
            "lexicon_updates": {},
            "new_glyphs_generated": new_glyphs,
            "pattern_analysis": [],
        }

    # -- Dedup utilities --
    def _normalize(self, text: str) -> str:
        """Normalize text for lightweight deduplication: lowercase, remove punctuation, collapse whitespace."""
        if text is None:
            return ""
        # Remove punctuation and non-word chars, keep unicode word chars and spaces
        cleaned = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
        cleaned = cleaned.lower()
        cleaned = " ".join(cleaned.split())
        return cleaned

    def _token_similarity(self, a: str, b: str) -> float:
        """Simple token overlap similarity: intersection/union of token sets."""
        if not a or not b:
            return 0.0
        ta = set(a.split())
        tb = set(b.split())
        if not ta or not tb:
            return 0.0
        inter = ta.intersection(tb)
        union = ta.union(tb)
        return float(len(inter)) / float(len(union))

    def _load_existing_lexicon(self) -> None:
        """Load existing glyph lexicon rows into normalized cache (best-effort)."""
        if self._lexicon_loaded:
            return
        self._lexicon_loaded = True
        try:
            lexpath = os.path.normpath(
                os.path.join(os.path.dirname(__file__), "..", "..", "glyph_lexicon_rows_before_phase3.json")
            )
            if os.path.exists(lexpath):
                try:
                    with open(lexpath, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                        if isinstance(data, list):
                            for row in data:
                                # consider name and examples
                                if isinstance(row, dict):
                                    name = row.get("name") or row.get("phrase") or ""
                                    if name:
                                        self._existing_normalized.add(self._normalize(str(name)))
                                    ex = row.get("examples") or row.get("example") or []
                                    if isinstance(ex, list):
                                        for e in ex:
                                            try:
                                                self._existing_normalized.add(self._normalize(str(e)))
                                            except Exception:
                                                continue
                        else:
                            # not an array, ignore
                            pass
                except Exception:
                    # Could not parse lexicon — ignore
                    pass
        except Exception:
            pass


class HybridProcessorWithEvolution:
    """
    Complete processing pipeline with dynamic glyph evolution.

    Integration flow:
    Conversation Input → Signal Extraction (Adaptive) → Lexicon Learning → Pattern Detection → Glyph Generation
    ↑                                                                                               ↓
    └─────────────────── New Glyphs Available for System Use ──────────────────────────────────┘
    """

    def __init__(
        self,
        hybrid_learner,
        adaptive_extractor,
        dynamic_glyph_evolution,
        user_id: str = "default",
        auto_track_conversations: bool = True,
    ):
        """Initialize the integrated processor.

        Args:
            hybrid_learner: HybridLearnerWithUserOverrides instance
            adaptive_extractor: AdaptiveSignalExtractor for discovering new dimensions
            dynamic_glyph_evolution: DynamicGlyphEvolution instance
            user_id: Default user identifier
            auto_track_conversations: Whether to auto-generate conversation IDs
        """
        # Accept either a hybrid learner or a local learner-like object.
        self.learner = hybrid_learner
        self.extractor = adaptive_extractor
        # evolution may be a complex dynamic_glyph_evolution or a simple
        # local fallback implementing `process_dialogue_exchange`.
        self.evolution = dynamic_glyph_evolution
        self.user_id = user_id
        self.auto_track_conversations = auto_track_conversations

        # Initialize lexicon-aware response generator
        self.lexicon_aware_generator = None
        if LEXICON_AWARE_AVAILABLE:
            self.lexicon_aware_generator = LexiconAwareResponseGenerator(hybrid_learner=hybrid_learner)

        self.conversation_history = []
        self.generated_glyphs = []

        logger.info("[HYBRID PROCESSOR] Initialized with dynamic glyph evolution")
        logger.info("  - Hybrid Learner: ready")
        logger.info(f"  - Adaptive Extractor: {adaptive_extractor.__class__.__name__ if adaptive_extractor else 'N/A'}")
        logger.info("  - Glyph Evolution: connected")
        if self.lexicon_aware_generator:
            logger.info("  - Lexicon-Aware Generator: ready")
            logger.info("    → Responses will be personalized based on learned patterns")

    def process_user_message(
        self,
        user_message: str,
        ai_response: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        glyphs: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Process a user-AI exchange through the full pipeline.

        Args:
            user_message: User's input
            ai_response: AI's response
            user_id: User identifier (uses default if not provided)
            conversation_id: Conversation ID (auto-generates if not provided)
            glyphs: Pre-identified glyphs (optional)

        Returns:
            Complete result with learning, lexicon updates, and new glyphs
        """
        if user_id is None:
            user_id = self.user_id

        if conversation_id is None:
            if self.auto_track_conversations:
                conversation_id = str(uuid4())[:8]
            else:
                conversation_id = "unknown"

        logger.info(f"\n[PROCESSING] User message from {user_id}")
        logger.info(f"  Conversation: {conversation_id}")

        result = {
            "status": "processing",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "user_message": user_message,
            "ai_response": ai_response,
            "pipeline_stages": {},
        }

        try:
            # STAGE 1: Extract signals (adaptive - may discover new dimensions)
            logger.info("[STAGE 1] Signal Extraction (Adaptive)")
            emotional_signals = self._extract_signals(user_message, ai_response)
            signal_names = [s.get("signal") or s.get("name") for s in emotional_signals]
            result["pipeline_stages"]["signal_extraction"] = {
                "signals_found": len(emotional_signals),
                "signals": signal_names,
            }
            logger.info(f"  ✓ Extracted {len(emotional_signals)} signals")
            if emotional_signals:
                signal_str = ", ".join([str(s) for s in signal_names if s])
                logger.info(f"    Signals: {signal_str}")

            # STAGE 2: Learning (local-first)
            logger.info("[STAGE 2] Learning (local-first)")
            learning_result = self.evolution.process_dialogue_exchange(
                user_id=user_id,
                conversation_id=conversation_id,
                user_input=user_message,
                ai_response=ai_response,
                emotional_signals=emotional_signals,
                glyphs=glyphs,
            )
            result["pipeline_stages"]["hybrid_learning"] = learning_result
            logger.info(f"  ✓ Learning complete: {learning_result.get('learning_result', {}).get('success', False)}")

            # STAGE 3: Lexicon Updates
            logger.info("[STAGE 3] Lexicon Analysis")
            lexicon_info = learning_result.get("lexicon_updates", {})
            result["pipeline_stages"]["lexicon"] = lexicon_info
            if lexicon_info:
                logger.info(f"  ✓ Lexicon contains {lexicon_info.get('signal_count', 0)} signals")

            # STAGE 4: Pattern Detection & Glyph Generation
            logger.info("[STAGE 4] Pattern Detection & Glyph Generation")
            new_glyphs = learning_result.get("new_glyphs_generated", [])
            patterns = learning_result.get("pattern_analysis", [])

            glyph_result = {
                "new_glyphs_count": len(new_glyphs),
                "patterns_detected": len(patterns) if patterns else 0,
                "new_glyphs": [g.to_dict() if hasattr(g, "to_dict") else g for g in new_glyphs],
            }
            result["pipeline_stages"]["glyph_generation"] = glyph_result

            if new_glyphs:
                logger.info(f"  ✓ Generated {len(new_glyphs)} new glyphs:")
                for glyph in new_glyphs:
                    glyph_dict = glyph.to_dict() if hasattr(glyph, "to_dict") else glyph
                    logger.info(f"    - {glyph_dict.get('symbol', '?')} {glyph_dict.get('name', '?')}")
                    self.generated_glyphs.append(glyph_dict)
            else:
                logger.info("  ℹ No new glyphs generated (need more pattern frequency)")

            # Add to conversation history
            self.conversation_history.append(
                {
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "user_message": user_message,
                    "ai_response": ai_response,
                    "signals": emotional_signals,
                    "new_glyphs": new_glyphs,
                    "result": result,
                }
            )

            result["status"] = "success"

        except Exception as e:
            logger.error(f"Error in processing pipeline: {e}", exc_info=True)
            result["status"] = "error"
            result["error"] = str(e)

        logger.info(f"[DONE] Processing complete for {user_id}\n")

        return result

    def _extract_signals(
        self,
        user_message: str,
        ai_response: str,
    ) -> List[Dict]:
        """Extract emotional signals using adaptive extractor."""
        try:
            combined_text = user_message + " " + ai_response

            if self.extractor:
                signals = self.extractor.extract_signals(combined_text)
            else:
                # Fallback to poetry extractor
                from emotional_os.learning.poetry_signal_extractor import (
                    get_poetry_extractor,
                )

                extractor = get_poetry_extractor()
                signals = extractor.extract_signals(combined_text)

            return signals if signals else []
        except Exception as e:
            logger.warning(f"Signal extraction failed: {e}")
            return []

    def get_all_generated_glyphs(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all glyphs generated during this session."""
        glyphs = self.generated_glyphs
        if limit:
            glyphs = glyphs[-limit:]
        return glyphs

    def get_conversation_summary(self, conversation_id: str) -> Dict:
        """Get summary of a specific conversation."""
        conv_data = [c for c in self.conversation_history if c["conversation_id"] == conversation_id]

        if not conv_data:
            return {"found": False}

        summary = {
            "found": True,
            "conversation_id": conversation_id,
            "turns": len(conv_data),
            "all_signals": [],
            "all_glyphs_generated": [],
            "user_id": conv_data[0].get("user_id"),
        }

        for turn in conv_data:
            summary["all_signals"].extend(turn.get("signals", []))
            summary["all_glyphs_generated"].extend(turn.get("new_glyphs", []))

        return summary

    def print_session_summary(self):
        """Print summary of all processing in this session."""
        print("\n" + "=" * 80)
        print("HYBRID PROCESSOR SESSION SUMMARY")
        print("=" * 80)

        print(f"\nTotal conversations processed: {len(set(c['conversation_id'] for c in self.conversation_history))}")
        print(f"Total turns processed: {len(self.conversation_history)}")
        print(f"Total new glyphs generated: {len(self.generated_glyphs)}")

        if self.generated_glyphs:
            print("\nNEW GLYPHS GENERATED:")
            for i, glyph in enumerate(self.generated_glyphs, 1):
                emotions = " + ".join(glyph.get("core_emotions", []))
                print(f"  {i}. {glyph.get('symbol', '?')} {glyph.get('name', '?')} ({emotions})")

        print("\n" + "=" * 80 + "\n")

    def export_session_glyphs(self, output_file: str) -> Dict:
        """Export all session-generated glyphs to file."""
        try:
            export_data = {
                "source": "hybrid_processor_session",
                "glyphs": self.generated_glyphs,
                "count": len(self.generated_glyphs),
            }

            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"✓ Exported {len(self.generated_glyphs)} glyphs to {output_file}")
            return {"success": True, "count": len(self.generated_glyphs), "file": output_file}

        except Exception as e:
            logger.error(f"Failed to export glyphs: {e}")
            return {"success": False, "error": str(e)}

    def enhance_response_with_learned_context(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        conversation_context: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Enhance a response using learned lexicon context.

        This is called BEFORE generating an AI response to get personalization
        guidance based on what the system has learned about the user.

        Args:
            user_message: User's input
            user_id: User identifier
            conversation_context: Previous messages for context

        Returns:
            Dict with personalized response, associations, and confidence
        """
        if user_id is None:
            user_id = self.user_id

        if not self.lexicon_aware_generator:
            logger.warning("Lexicon-aware generator not available")
            return {}

        result = self.lexicon_aware_generator.generate_response(
            user_message=user_message,
            user_id=user_id,
            conversation_context=conversation_context,
        )

        logger.info(f"[LEXICON-AWARE] Personalization level: {result.get('personalization_level')}")
        if result.get("trigger_keywords"):
            logger.info(f"  Learned associations: {result.get('trigger_keywords')}")

        return result


# Factory function for easy setup
def create_integrated_processor(
    hybrid_learner,
    adaptive_extractor=None,
    user_id: str = "default",
) -> HybridProcessorWithEvolution:
    """
    Factory to create an integrated processor with all components.

    Args:
        hybrid_learner: HybridLearnerWithUserOverrides instance
        adaptive_extractor: AdaptiveSignalExtractor (optional, will use standard if not provided)
        user_id: Default user ID

    Returns:
        Fully initialized HybridProcessorWithEvolution instance
    """
    # Prefer the project's dynamic glyph evolution if available; otherwise
    # fall back to a lightweight local-only evolution implementation.
    try:
        from dynamic_glyph_evolution import integrate_evolution_with_processor

        # Create evolution system
        evolution = integrate_evolution_with_processor(
            hybrid_learner=hybrid_learner,
            adaptive_extractor=adaptive_extractor,
        )
    except Exception:
        logger.info("Dynamic glyph evolution integration not available — using LocalEvolution fallback")
        # Use the provided hybrid_learner if it looks like a LocalLearner,
        # otherwise construct a LocalLearner for persistence.
        try:
            if hybrid_learner is not None and hasattr(hybrid_learner, "collect_candidate"):
                local_learner = hybrid_learner
            else:
                local_learner = LocalLearner()
        except Exception:
            local_learner = LocalLearner()

        evolution = LocalEvolution(learner=local_learner)

    # Create integrated processor
    processor = HybridProcessorWithEvolution(
        hybrid_learner=hybrid_learner,
        adaptive_extractor=adaptive_extractor,
        dynamic_glyph_evolution=evolution,
        user_id=user_id,
    )

    logger.info("\n✓ FULL INTEGRATION COMPLETE")
    logger.info("  Pipeline: Dialogue → Signals → Learning → Patterns → Glyphs")
    logger.info("  Ready for live conversations\n")

    return processor


if __name__ == "__main__":
    print("Hybrid Processor with Dynamic Glyph Evolution")
    print("=" * 80)
    print("\nUsage:")
    print("  from hybrid_processor_with_evolution import create_integrated_processor")
    print("  processor = create_integrated_processor(hybrid_learner, adaptive_extractor)")
    print("  result = processor.process_user_message(user_msg, ai_response)")
    print("\nThe processor automatically:")
    print("  1. Extracts signals (adaptive - discovers new dimensions)")
    print("  2. Learns through hybrid processor (user + shared lexicon)")
    print("  3. Detects patterns in dialogue")
    print("  4. Generates new glyphs from patterns")
    print("  5. Makes glyphs available for system use")
    print("=" * 80)
