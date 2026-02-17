"""Dominant Bot Orchestrator for FirstPerson.

The executive/compiler layer: Observes responses, detects mismatches,
creates proto-glyphs, clusters them, and decides when to synthesize new glyphs.

NEVER responds to user, NEVER blocks conversation.
Runs asynchronously between sessions or in background.

Pipeline:
  1. Observe subordinate bot's response
  2. Parse emotional content deeply
  3. Compare to existing glyphs
  4. If mismatch -> create proto-glyph
  5. Periodically cluster and analyze
  6. If cluster stabilizes -> initiate synthesis
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import numpy as np
from scipy.spatial.distance import cosine
from datetime import datetime


@dataclass
class DominantBotAnalysis:
    """Analysis of a subordinate bot response."""
    should_create_proto: bool
    should_synthesize: bool
    confidence: float
    mismatch_degree: float  # 0-1, how different from existing glyphs
    recommended_action: str  # "observe", "create_proto", "synthesize"
    analysis_metadata: Dict = None


class DominantBotOrchestrator:
    """Watches and learns from subordinate bot responses."""

    def __init__(
        self,
        proto_glyph_manager,
        glyph_synthesizer=None,
        local_parser=None,
    ):
        """Initialize dominant bot orchestrator.
        
        Args:
            proto_glyph_manager: ProtoGlyphManager instance
            glyph_synthesizer: Optional GlyphSynthesizer (for OpenAI calls)
            local_parser: Optional function to parse emotional content locally
        """
        self.proto_manager = proto_glyph_manager
        self.synthesizer = glyph_synthesizer
        self.local_parser = local_parser
        self.observations = []
        self.current_glyphs = {}
        self.synthesis_candidates = []

    def observe_exchange(
        self,
        user_input: str,
        subordinate_response: Dict,
        emotional_vector: List[float],
    ) -> DominantBotAnalysis:
        """Observe an exchange and decide if new learning is needed.
        
        Called asynchronously after subordinate bot responds.
        Does NOT block the conversation.
        
        Args:
            user_input: The user's message
            subordinate_response: The subordinate bot's response metadata
            emotional_vector: Parsed emotional vector
            
        Returns:
            DominantBotAnalysis with recommendations
        """
        # Store observation
        observation = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "subordinate_response": subordinate_response,
            "emotional_vector": emotional_vector,
        }
        self.observations.append(observation)
        
        # Step 1: Check if subordinate's glyph match was weak
        subordinate_confidence = subordinate_response.get("confidence", 0.0)
        is_weak_match = subordinate_confidence < 0.6
        
        if not is_weak_match:
            return DominantBotAnalysis(
                should_create_proto=False,
                should_synthesize=False,
                confidence=0.0,
                mismatch_degree=0.0,
                recommended_action="observe",
                analysis_metadata={"reason": "strong_match"},
            )
        
        # Step 2: Perform deep emotional analysis
        deep_analysis = self._analyze_emotional_pattern(
            user_input,
            emotional_vector,
        )
        
        # Step 3: Check for mismatch with existing glyphs
        mismatch_degree = self._compute_mismatch_degree(
            emotional_vector,
            deep_analysis,
        )
        
        # Step 4: Decide on action
        should_create_proto = mismatch_degree > 0.4
        should_synthesize = mismatch_degree > 0.8
        
        # Step 5: If creating proto, do it
        if should_create_proto:
            proto_id = self.proto_manager.create_proto_glyph(
                emotional_vector=emotional_vector,
                example_text=user_input,
                context={
                    "subordinate_match": subordinate_response.get("glyph_name"),
                    "subordinate_confidence": subordinate_confidence,
                },
                confidence=subordinate_confidence,
            )
            analysis_metadata = {
                "proto_id": proto_id,
                "mismatch_reason": deep_analysis.get("mismatch_reason"),
            }
        else:
            analysis_metadata = {}
        
        return DominantBotAnalysis(
            should_create_proto=should_create_proto,
            should_synthesize=should_synthesize,
            confidence=mismatch_degree,
            mismatch_degree=mismatch_degree,
            recommended_action="create_proto" if should_create_proto else "observe",
            analysis_metadata=analysis_metadata,
        )

    def cluster_and_analyze_periodic(
        self,
        similarity_threshold: float = 0.8,
        min_cluster_size: int = 2,
    ) -> List[Dict]:
        """Periodically cluster proto-glyphs and identify synthesis candidates.
        
        Call this every hour or daily.
        
        Args:
            similarity_threshold: Minimum similarity to group (0-1)
            min_cluster_size: Minimum proto-glyphs per cluster
            
        Returns:
            List of promising clusters for synthesis
        """
        # Cluster all proto-glyphs
        clusters = self.proto_manager.cluster_proto_glyphs(
            similarity_threshold=similarity_threshold,
            min_cluster_size=min_cluster_size,
        )
        
        # Get stable clusters
        stable_clusters = self.proto_manager.get_stable_clusters(
            stability_threshold=0.75,
            min_size=3,
        )
        
        # Identify synthesis candidates
        candidates = []
        for cluster in stable_clusters:
            candidate = {
                "cluster_id": cluster.cluster_id,
                "proto_ids": cluster.proto_ids,
                "centroid": cluster.centroid,
                "size": cluster.size,
                "stability_score": cluster.stability_score,
                "ready_for_synthesis": True,
            }
            candidates.append(candidate)
        
        self.synthesis_candidates = candidates
        return candidates

    def should_synthesize_glyph(
        self,
        cluster_id: str,
        min_stability: float = 0.75,
        min_examples: int = 5,
    ) -> bool:
        """Check if a cluster is ready for OpenAI synthesis.
        
        Args:
            cluster_id: Cluster to evaluate
            min_stability: Minimum stability score
            min_examples: Minimum total examples
            
        Returns:
            True if ready for synthesis
        """
        if cluster_id not in self.proto_manager.clusters:
            return False
        
        cluster = self.proto_manager.clusters[cluster_id]
        
        # Check stability
        if cluster.stability_score < min_stability:
            return False
        
        # Check example count
        total_examples = sum(
            len(self.proto_manager.proto_glyphs[pid].example_texts)
            for pid in cluster.proto_ids
        )
        
        if total_examples < min_examples:
            return False
        
        return True

    def _analyze_emotional_pattern(
        self,
        user_input: str,
        emotional_vector: List[float],
    ) -> Dict:
        """Perform deep emotional analysis using local tools.
        
        Args:
            user_input: The user's message
            emotional_vector: Already-parsed emotional vector
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "emotional_vector": emotional_vector,
            "dominant_emotion": self._identify_dominant_emotion(emotional_vector),
            "emotional_blend": self._compute_emotional_blend(emotional_vector),
            "narrative_signal": self._extract_narrative_signal(user_input),
            "mismatch_reason": None,
        }
        
        return analysis

    def _compute_mismatch_degree(
        self,
        emotional_vector: List[float],
        deep_analysis: Dict,
    ) -> float:
        """Compute how different this pattern is from existing glyphs.
        
        Args:
            emotional_vector: Current emotional vector
            deep_analysis: Deep analysis results
            
        Returns:
            Mismatch degree (0-1, higher = more novel)
        """
        if not self.current_glyphs:
            return 0.5  # Moderate novelty if no glyphs yet
        
        # Find minimum distance to any existing glyph
        min_distance = 1.0
        
        for glyph in self.current_glyphs.values():
            glyph_vector = glyph.get("emotional_vector", [])
            if len(glyph_vector) == len(emotional_vector):
                distance = cosine(emotional_vector, glyph_vector)
                min_distance = min(min_distance, distance)
        
        # Convert distance to mismatch (0 = perfect match, 1 = completely novel)
        # Distance range is 0-2 (cosine), normalize to 0-1
        mismatch = min(1.0, min_distance / 2.0)
        
        return mismatch

    def _identify_dominant_emotion(
        self,
        emotional_vector: List[float],
    ) -> str:
        """Identify the strongest emotion in vector."""
        # Simple: assume standard order [anger, joy, trust, fear, surprise, sadness, disgust, anticipation]
        emotions = [
            "anger", "joy", "trust", "fear",
            "surprise", "sadness", "disgust", "anticipation"
        ]
        if len(emotional_vector) >= len(emotions):
            max_idx = np.argmax(emotional_vector[:len(emotions)])
            return emotions[max_idx]
        return "neutral"

    def _compute_emotional_blend(
        self,
        emotional_vector: List[float],
    ) -> List[Tuple[str, float]]:
        """Identify secondary emotions."""
        emotions = [
            "anger", "joy", "trust", "fear",
            "surprise", "sadness", "disgust", "anticipation"
        ]
        scores = emotional_vector[:len(emotions)]
        blend = [(emotions[i], float(score)) for i, score in enumerate(scores) if score > 0.2]
        return sorted(blend, key=lambda x: x[1], reverse=True)

    def _extract_narrative_signal(
        self,
        user_input: str,
    ) -> Dict:
        """Extract narrative themes from user input."""
        # Simple markers for narrative content
        return {
            "has_event": any(word in user_input.lower() for word in ["happened", "occurred", "did", "was"]),
            "has_question": user_input.strip().endswith("?"),
            "has_negation": any(word in user_input.lower() for word in ["no", "not", "neither", "never"]),
            "has_emotion_word": any(word in user_input.lower() for word in ["feel", "felt", "sad", "happy", "angry", "afraid"]),
        }