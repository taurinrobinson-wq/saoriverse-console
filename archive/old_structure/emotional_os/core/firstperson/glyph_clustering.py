"""
Phase 2.5: Glyph Clustering
Multi-dimensional glyph grouping based on semantic similarity, emotional resonance,
and user preferences. Enables discovery of related glyphs and preference propagation.
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple
import math
from collections import defaultdict


@dataclass
class GlyphVector:
    """Multi-dimensional representation of a glyph."""
    glyph_name: str
    # Semantic dimensions (0.0-1.0)
    warmth: float = 0.5
    energy: float = 0.5
    depth: float = 0.5
    hope: float = 0.5
    # Emotional dimensions
    arousal: float = 0.5
    valence: float = 0.5
    # User preference dimensions (if available)
    avg_effectiveness: float = 0.5
    avg_acceptance_rate: float = 0.5

    def distance_to(self, other: 'GlyphVector') -> float:
        """Calculate Euclidean distance to another glyph."""
        dims = [
            self.warmth, self.energy, self.depth, self.hope,
            self.arousal, self.valence
        ]
        other_dims = [
            other.warmth, other.energy, other.depth, other.hope,
            other.arousal, other.valence
        ]

        sum_squared_diff = sum((d1 - d2) ** 2 for d1,
                               d2 in zip(dims, other_dims))
        return math.sqrt(sum_squared_diff)

    def similarity_to(self, other: 'GlyphVector') -> float:
        """Calculate similarity score (0.0-1.0) to another glyph."""
        distance = self.distance_to(other)
        # Maximum distance in 6D space where all dims are [0,1]
        max_distance = math.sqrt(6.0)
        return 1.0 - (distance / max_distance)


class GlyphCluster:
    """Group of semantically similar glyphs."""

    def __init__(self, cluster_id: str, name: str, theme: str):
        """Initialize a glyph cluster."""
        self.cluster_id = cluster_id
        self.name = name
        self.theme = theme  # e.g., "warmth", "energy", "clarity"
        self.members: Dict[str, GlyphVector] = {}
        self.centroid: Optional[GlyphVector] = None

    def add_member(self, glyph_vector: GlyphVector) -> None:
        """Add a glyph to the cluster."""
        self.members[glyph_vector.glyph_name] = glyph_vector
        self._update_centroid()

    def remove_member(self, glyph_name: str) -> None:
        """Remove a glyph from the cluster."""
        if glyph_name in self.members:
            del self.members[glyph_name]
            self._update_centroid()

    def _update_centroid(self) -> None:
        """Update cluster centroid based on members."""
        if not self.members:
            self.centroid = None
            return

        member_list = list(self.members.values())
        num_members = len(member_list)

        # Calculate average across all dimensions
        self.centroid = GlyphVector(
            glyph_name=f"centroid_{self.cluster_id}",
            warmth=sum(m.warmth for m in member_list) / num_members,
            energy=sum(m.energy for m in member_list) / num_members,
            depth=sum(m.depth for m in member_list) / num_members,
            hope=sum(m.hope for m in member_list) / num_members,
            arousal=sum(m.arousal for m in member_list) / num_members,
            valence=sum(m.valence for m in member_list) / num_members,
            avg_effectiveness=sum(
                m.avg_effectiveness for m in member_list) / num_members,
            avg_acceptance_rate=sum(
                m.avg_acceptance_rate for m in member_list) / num_members,
        )

    def get_closest_members(self, glyph_name: str, limit: int = 3) -> List[Tuple[str, float]]:
        """Get glyphs closest to a given glyph within this cluster."""
        if glyph_name not in self.members:
            return []

        target = self.members[glyph_name]
        similarities = []

        for other_name, other_vector in self.members.items():
            if other_name == glyph_name:
                continue
            sim = target.similarity_to(other_vector)
            similarities.append((other_name, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]

    def get_alternatives(self, effectiveness_threshold: float = 0.5) -> List[str]:
        """Get alternative glyphs with high effectiveness."""
        return [
            name for name, vector in self.members.items()
            if vector.avg_effectiveness > effectiveness_threshold
        ]


class GlyphClusteringEngine:
    """Manages glyph clustering and discovery."""

    def __init__(self):
        """Initialize clustering engine."""
        self.vectors: Dict[str, GlyphVector] = {}
        self.clusters: Dict[str, GlyphCluster] = {}
        self._glyph_to_clusters: Dict[str, Set[str]] = defaultdict(set)
        self._initialize_default_clusters()

    def _initialize_default_clusters(self) -> None:
        """Create default semantic clusters."""
        default_clusters = [
            ("warmth_cluster", "Warmth & Compassion", "warmth"),
            ("energy_cluster", "Energy & Vitality", "energy"),
            ("clarity_cluster", "Clarity & Understanding", "depth"),
            ("hope_cluster", "Hope & Possibility", "hope"),
            ("balance_cluster", "Balance & Integration", "equilibrium"),
        ]

        for cluster_id, name, theme in default_clusters:
            cluster = GlyphCluster(cluster_id, name, theme)
            self.clusters[cluster_id] = cluster

    def add_glyph(self, glyph_vector: GlyphVector, cluster_ids: Optional[List[str]] = None) -> None:
        """Add a glyph with optional cluster assignment."""
        self.vectors[glyph_vector.glyph_name] = glyph_vector

        if cluster_ids is None:
            # Auto-assign to cluster based on highest dimension
            dimensions = {
                "warmth_cluster": glyph_vector.warmth,
                "energy_cluster": glyph_vector.energy,
                "clarity_cluster": glyph_vector.depth,
                "hope_cluster": glyph_vector.hope,
            }
            best_cluster = max(dimensions, key=dimensions.get)
            cluster_ids = [best_cluster]

        for cluster_id in cluster_ids:
            if cluster_id in self.clusters:
                self.clusters[cluster_id].add_member(glyph_vector)
                self._glyph_to_clusters[glyph_vector.glyph_name].add(
                    cluster_id)

    def find_similar_glyphs(
        self,
        glyph_name: str,
        similarity_threshold: float = 0.6,
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """Find glyphs similar to a target glyph."""
        if glyph_name not in self.vectors:
            return []

        target = self.vectors[glyph_name]
        similarities = []

        for other_name, other_vector in self.vectors.items():
            if other_name == glyph_name:
                continue

            sim = target.similarity_to(other_vector)
            if sim >= similarity_threshold:
                similarities.append((other_name, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]

    def find_complementary_glyphs(self, glyph_name: str, limit: int = 3) -> List[Tuple[str, float]]:
        """Find glyphs that complement a glyph (opposite in some dimensions)."""
        if glyph_name not in self.vectors:
            return []

        target = self.vectors[glyph_name]
        complementary = []

        for other_name, other_vector in self.vectors.items():
            if other_name == glyph_name:
                continue

            # Complementary means opposite on emotional axes
            valence_complement = abs(target.valence - other_vector.valence)
            arousal_complement = abs(target.arousal - other_vector.arousal)
            depth_complement = abs(target.depth - other_vector.depth)

            complement_score = (valence_complement +
                                arousal_complement + depth_complement) / 3.0

            complementary.append((other_name, complement_score))

        complementary.sort(key=lambda x: x[1], reverse=True)
        return complementary[:limit]

    def get_cluster_for_glyph(self, glyph_name: str) -> Optional[GlyphCluster]:
        """Get primary cluster for a glyph."""
        cluster_ids = self._glyph_to_clusters.get(glyph_name, set())
        if cluster_ids:
            return self.clusters.get(list(cluster_ids)[0])
        return None

    def get_glyphs_by_emotional_state(
        self,
        arousal: float,
        valence: float,
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """Get glyphs best suited for an emotional state."""
        target = GlyphVector(
            glyph_name="emotional_state",
            arousal=arousal,
            valence=valence
        )

        matches = []
        for name, vector in self.vectors.items():
            # Focus on emotional dimensions
            emotional_distance = math.sqrt(
                (vector.arousal - arousal) ** 2 +
                (vector.valence - valence) ** 2
            )
            match_score = 1.0 - (emotional_distance / math.sqrt(2.0))
            matches.append((name, match_score))

        matches.sort(key=lambda x: x[1], reverse=True)
        return [(name, score) for name, score in matches if score > 0.5][:limit]

    def propagate_preference(
        self,
        glyph_name: str,
        preference_direction: str = "similar"
    ) -> List[Tuple[str, float]]:
        """
        Propagate preference from one glyph to related glyphs.

        Args:
            glyph_name: Source glyph
            preference_direction: "similar" (same theme) or "complementary" (opposite)

        Returns:
            List of (glyph_name, confidence) tuples
        """
        if preference_direction == "similar":
            return self.find_similar_glyphs(glyph_name, similarity_threshold=0.5)
        else:
            return self.find_complementary_glyphs(glyph_name)

    def get_cluster_summary(self) -> Dict[str, Dict]:
        """Get summary of all clusters."""
        summary = {}

        for cluster_id, cluster in self.clusters.items():
            summary[cluster_id] = {
                "name": cluster.name,
                "theme": cluster.theme,
                "member_count": len(cluster.members),
                "members": list(cluster.members.keys()),
                "centroid": {
                    "warmth": cluster.centroid.warmth,
                    "energy": cluster.centroid.energy,
                    "depth": cluster.centroid.depth,
                    "hope": cluster.centroid.hope,
                } if cluster.centroid else None,
            }

        return summary

    def recommend_by_cluster(
        self,
        glyph_name: str,
        limit: int = 3
    ) -> List[Tuple[str, str, float]]:
        """
        Recommend glyphs from same cluster as target glyph.

        Returns:
            List of (glyph_name, cluster_name, score) tuples
        """
        cluster = self.get_cluster_for_glyph(glyph_name)
        if not cluster:
            return []

        recommendations = []
        if cluster.centroid:
            for member_name in cluster.members.keys():
                if member_name == glyph_name:
                    continue
                member = cluster.members[member_name]
                sim = member.similarity_to(cluster.centroid)
                recommendations.append((member_name, cluster.name, sim))

        recommendations.sort(key=lambda x: x[2], reverse=True)
        return recommendations[:limit]
