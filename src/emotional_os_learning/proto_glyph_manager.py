"""Proto-Glyph Manager for FirstPerson Learning System.

Handles creation, clustering, and consolidation of temporary emotional patterns
(proto-glyphs) into stable, reusable emotional categories (glyphs).

Pipeline:
  1. Detect emotional pattern mismatch
  2. Create proto-glyph (temporary storage)
  3. Cluster similar proto-glyphs
  4. Merge duplicates
  5. Promote stable clusters to glyphs
  6. Generate symbolic representation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import json
from pathlib import Path
from datetime import datetime
import numpy as np
from scipy.spatial.distance import cosine


@dataclass
class ProtoGlyph:
    """A temporary emotional pattern waiting consolidation."""
    proto_id: str
    emotional_vector: List[float]
    example_texts: List[str] = field(default_factory=list)
    timestamps: List[float] = field(default_factory=list)
    confidence: float = 0.5
    promoted: bool = False
    context: Dict = field(default_factory=dict)


@dataclass
class ProtoGlyphCluster:
    """A cluster of similar proto-glyphs ready for consolidation."""
    cluster_id: str
    proto_ids: List[str]
    centroid: List[float]
    similarity_scores: List[float]
    size: int = 0
    stability_score: float = 0.0


class ProtoGlyphManager:
    """Manages proto-glyphs and coordinates their consolidation into glyphs."""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize proto-glyph manager.
        
        Args:
            storage_path: Path to persist proto-glyphs (default: detected_patterns.json)
        """
        self.storage_path = Path(storage_path or "detected_patterns.json")
        self.proto_glyphs: Dict[str, ProtoGlyph] = {}
        self.clusters: Dict[str, ProtoGlyphCluster] = {}
        self.glyph_promotions: List[Dict] = []
        self._load_from_disk()

    def create_proto_glyph(
        self,
        emotional_vector: List[float],
        example_text: str,
        context: Optional[Dict] = None,
        confidence: float = 0.5,
    ) -> str:
        """Create a new proto-glyph from emotional vector and example.
        
        Args:
            emotional_vector: Emotional representation (e.g., [anger, joy, trust, ...])
            example_text: Sample text that triggered this pattern
            context: Additional context (user_id, conversation_id, etc.)
            confidence: Confidence in this pattern (0-1)
            
        Returns:
            proto_id of the newly created proto-glyph
        """
        proto_id = f"proto_{datetime.now().timestamp()}_{len(self.proto_glyphs)}"
        
        proto = ProtoGlyph(
            proto_id=proto_id,
            emotional_vector=emotional_vector,
            example_texts=[example_text],
            timestamps=[datetime.now().timestamp()],
            confidence=confidence,
            context=context or {}
        )
        
        self.proto_glyphs[proto_id] = proto
        self._save_to_disk()
        
        return proto_id

    def add_example_to_proto(
        self,
        proto_id: str,
        example_text: str,
        emotional_vector: Optional[List[float]] = None,
    ) -> bool:
        """Add another example to an existing proto-glyph.
        
        Args:
            proto_id: ID of proto-glyph to update
            example_text: New example text
            emotional_vector: Optional updated emotional vector (averages if provided)
            
        Returns:
            True if successful, False if proto_id not found
        """
        if proto_id not in self.proto_glyphs:
            return False
            
        proto = self.proto_glyphs[proto_id]
        proto.example_texts.append(example_text)
        proto.timestamps.append(datetime.now().timestamp())
        
        # Update vector by averaging with new observation
        if emotional_vector:
            old_vector = np.array(proto.emotional_vector)
            new_vector = np.array(emotional_vector)
            proto.emotional_vector = ((old_vector + new_vector) / 2).tolist()
            
            # Increase confidence slightly
            proto.confidence = min(1.0, proto.confidence + 0.05)
        
        self._save_to_disk()
        return True

    def cluster_proto_glyphs(
        self,
        similarity_threshold: float = 0.8,
        min_cluster_size: int = 2,
    ) -> List[ProtoGlyphCluster]:
        """Cluster similar proto-glyphs using cosine similarity.
        
        Args:
            similarity_threshold: Minimum similarity to group (0-1, default 0.8)
            min_cluster_size: Minimum proto-glyphs per cluster
            
        Returns:
            List of identified clusters
        """
        if not self.proto_glyphs:
            return []
        
        clusters = []
        processed = set()
        
        proto_list = list(self.proto_glyphs.values())
        
        for i, proto_a in enumerate(proto_list):
            if proto_a.proto_id in processed:
                continue
            
            cluster_members = [proto_a.proto_id]
            similarity_scores = [1.0]
            
            # Find similar proto-glyphs
            for j, proto_b in enumerate(proto_list[i + 1:], start=i + 1):
                if proto_b.proto_id in processed:
                    continue
                
                similarity = 1 - cosine(proto_a.emotional_vector, proto_b.emotional_vector)
                
                if similarity >= similarity_threshold:
                    cluster_members.append(proto_b.proto_id)
                    similarity_scores.append(similarity)
                    processed.add(proto_b.proto_id)
            
            # Only keep clusters of sufficient size
            if len(cluster_members) >= min_cluster_size:
                processed.add(proto_a.proto_id)
                
                # Calculate centroid
                vectors = [
                    self.proto_glyphs[pid].emotional_vector
                    for pid in cluster_members
                ]
                centroid = np.mean(vectors, axis=0).tolist()
                
                # Calculate stability (how similar members are)
                stability = np.mean(similarity_scores)
                
                cluster_id = f"cluster_{len(clusters)}_{datetime.now().timestamp()}"
                cluster = ProtoGlyphCluster(
                    cluster_id=cluster_id,
                    proto_ids=cluster_members,
                    centroid=centroid,
                    similarity_scores=similarity_scores,
                    size=len(cluster_members),
                    stability_score=stability,
                )
                clusters.append(cluster)
                self.clusters[cluster_id] = cluster
        
        return clusters

    def get_stable_clusters(
        self,
        stability_threshold: float = 0.75,
        min_size: int = 3,
    ) -> List[ProtoGlyphCluster]:
        """Get clusters that are stable enough for glyph promotion.
        
        Args:
            stability_threshold: Minimum stability score (0-1)
            min_size: Minimum number of examples in cluster
            
        Returns:
            List of stable clusters ready for promotion
        """
        stable = []
        
        for cluster in self.clusters.values():
            # Check criteria
            meets_stability = cluster.stability_score >= stability_threshold
            meets_size = cluster.size >= min_size
            
            # Check total examples across all proto-glyphs
            total_examples = sum(
                len(self.proto_glyphs[pid].example_texts)
                for pid in cluster.proto_ids
            )
            meets_evidence = total_examples >= 5
            
            if meets_stability and meets_size and meets_evidence:
                stable.append(cluster)
        
        return stable

    def promote_to_glyph(
        self,
        cluster: ProtoGlyphCluster,
        glyph_name: str,
        glyph_symbol: str,
        gate_logic: Optional[Dict] = None,
    ) -> Dict:
        """Promote a stable cluster to a new glyph.
        
        Args:
            cluster: ProtoGlyphCluster to promote
            glyph_name: Name for the new glyph
            glyph_symbol: Symbolic representation
            gate_logic: Optional gate activation logic
            
        Returns:
            Dictionary representing the new glyph
        """
        # Collect all examples
        all_examples = []
        for proto_id in cluster.proto_ids:
            proto = self.proto_glyphs[proto_id]
            all_examples.extend(proto.example_texts)
        
        glyph = {
            "glyph_id": f"glyph_{datetime.now().timestamp()}",
            "name": glyph_name,
            "symbol": glyph_symbol,
            "emotional_vector": cluster.centroid,
            "examples": all_examples[:10],  # Keep top 10 examples
            "created_from_cluster": cluster.cluster_id,
            "created_from_proto_count": len(cluster.proto_ids),
            "confidence": cluster.stability_score,
            "gate_logic": gate_logic or {},
            "created_at": datetime.now().isoformat(),
        }
        
        # Mark proto-glyphs as promoted
        for proto_id in cluster.proto_ids:
            self.proto_glyphs[proto_id].promoted = True
        
        # Record promotion
        self.glyph_promotions.append(glyph)
        self._save_to_disk()
        
        return glyph

    def merge_proto_glyphs(
        self,
        proto_ids: List[str],
        keep_id: Optional[str] = None,
    ) -> Optional[str]:
        """Merge multiple proto-glyphs into one.
        
        Args:
            proto_ids: List of proto-glyphs to merge
            keep_id: Which proto_id to keep (default: first one)
            
        Returns:
            ID of merged proto-glyph, or None if merge failed
        """
        if not proto_ids or any(pid not in self.proto_glyphs for pid in proto_ids):
            return None
        
        keep_id = keep_id or proto_ids[0]
        keeper = self.proto_glyphs[keep_id]
        
        # Collect all data
        all_examples = list(keeper.example_texts)
        all_timestamps = list(keeper.timestamps)
        vectors = [np.array(keeper.emotional_vector)]
        all_confidence = [keeper.confidence]
        
        # Merge others into keeper
        for pid in proto_ids:
            if pid == keep_id:
                continue
            
            proto = self.proto_glyphs[pid]
            all_examples.extend(proto.example_texts)
            all_timestamps.extend(proto.timestamps)
            vectors.append(np.array(proto.emotional_vector))
            all_confidence.append(proto.confidence)
            
            # Mark original as promoted (merged away)
            proto.promoted = True
        
        # Update keeper
        keeper.example_texts = all_examples
        keeper.timestamps = all_timestamps
        keeper.emotional_vector = np.mean(vectors, axis=0).tolist()
        keeper.confidence = np.mean(all_confidence)
        
        self._save_to_disk()
        return keep_id

    def _save_to_disk(self) -> None:
        """Persist proto-glyphs to JSON."""
        data = {
            "proto_glyphs": {
                pid: {
                    "proto_id": proto.proto_id,
                    "emotional_vector": proto.emotional_vector,
                    "example_texts": proto.example_texts,
                    "confidence": proto.confidence,
                    "promoted": proto.promoted,
                }
                for pid, proto in self.proto_glyphs.items()
            },
            "promotions": self.glyph_promotions,
            "last_saved": datetime.now().isoformat(),
        }
        
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_from_disk(self) -> None:
        """Load proto-glyphs from JSON if file exists."""
        if not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
            
            for proto_data in data.get("proto_glyphs", {}).values():
                proto = ProtoGlyph(
                    proto_id=proto_data["proto_id"],
                    emotional_vector=proto_data["emotional_vector"],
                    example_texts=proto_data["example_texts"],
                    confidence=proto_data["confidence"],
                    promoted=proto_data.get("promoted", False),
                )
                self.proto_glyphs[proto.proto_id] = proto
            
            self.glyph_promotions = data.get("promotions", [])
        except Exception as e:
            print(f"Warning: Could not load proto-glyphs from disk: {e}")