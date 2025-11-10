#!/usr/bin/env python3
"""
Advanced Glyph Pruning Engine - Saoriverse Overgrowth Management

Implements sophisticated pruning strategy based on actual VELΩNIX architecture:
1. Signal Strength Filtering (NRC matches, valence clarity)
2. Trace Role Redundancy (collapse identical functions)
3. Usage Frequency & Match History (prioritize activated glyphs)
4. Tone Diversity Enforcement (maintain palette balance)
5. Reaction Chain Anchoring (preserve catalytic glyphs)

Includes optional enhancements:
- Emotional family clustering
- Pruning archive for later resurrection
- Confidence scoring for auditability
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
from datetime import datetime
import csv

logger = logging.getLogger(__name__)


@dataclass
class PruneCandidate:
    """Glyph candidate for pruning evaluation."""
    glyph_id: int
    glyph_name: str
    valence: Optional[str]
    trace_role: Optional[str]
    tone: Optional[str]
    gate: Optional[str]
    activation_signals: List[str]
    signal_strength: float = 0.0  # 0-1 based on NRC/valence clarity
    match_history: int = 0  # Times matched in user inputs
    trace_role_redundancy: float = 0.0  # 0-1 collision with others
    tone_distribution: float = 0.0  # 0-1 over/under represented
    reaction_chain_participation: float = 1.0  # 0-1 role in reactions (1=critical)
    is_factorial: bool = False  # New combination vs base
    parents: Optional[List[int]] = None  # Parent IDs if factorial
    
    # Pruning scores
    signal_strength_score: float = 0.0
    redundancy_score: float = 0.0
    coverage_score: float = 0.0
    activation_score: float = 0.0
    combined_prune_score: float = 0.0  # Overall keep score (higher = keep)
    should_prune: bool = False
    prune_confidence: float = 0.0  # 0-1 confidence in prune decision
    prune_reason: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for archival."""
        return {
            'glyph_id': self.glyph_id,
            'glyph_name': self.glyph_name,
            'valence': self.valence,
            'trace_role': self.trace_role,
            'tone': self.tone,
            'gate': self.gate,
            'activation_signals': self.activation_signals,
            'scores': {
                'signal_strength': round(self.signal_strength_score, 3),
                'redundancy': round(self.redundancy_score, 3),
                'coverage': round(self.coverage_score, 3),
                'activation': round(self.activation_score, 3),
                'combined_prune': round(self.combined_prune_score, 3),
            },
            'should_prune': self.should_prune,
            'prune_confidence': round(self.prune_confidence, 3),
            'prune_reason': self.prune_reason,
            'is_factorial': self.is_factorial,
            'parents': self.parents,
        }


class AdvancedPruningEngine:
    """Sophisticated glyph pruning using VELΩNIX architecture."""
    
    def __init__(
        self,
        glyph_lexicon_path: str = "emotional_os/glyphs/glyph_lexicon_rows.json",
        match_history_path: Optional[str] = None,
        reaction_engine_path: Optional[str] = None,
        archive_dir: str = "emotional_os/glyphs/pruning_archive"
    ):
        """Initialize the pruning engine.
        
        Args:
            glyph_lexicon_path: Path to glyph lexicon JSON
            match_history_path: Path to glyph match history (from logging)
            reaction_engine_path: Path to reaction chain definitions
            archive_dir: Directory for pruned glyph archives
        """
        self.glyph_lexicon_path = Path(glyph_lexicon_path)
        self.match_history_path = Path(match_history_path) if match_history_path else None
        self.reaction_engine_path = Path(reaction_engine_path) if reaction_engine_path else None
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Data structures
        self.glyphs: Dict[int, Dict] = {}
        self.candidates: List[PruneCandidate] = []
        self.match_history: Dict[int, int] = defaultdict(int)
        self.reaction_chains: List[Dict] = []
        
        # Saonyx tone palette
        self.saonyx_tones = {
            "Molten", "Hallowed Blue", "Velvet Drift", "Crimson Fire",
            "Radiant Gold", "Twilight Whisper", "Mirror Deep", "Ember Silk",
            "Sanctuary Stone", "Silver Echo", "Moss Green", "Amber Glow"
        }
        
        # Load data
        self._load_glyphs()
        self._load_match_history()
        self._load_reaction_chains()
    
    def _load_glyphs(self) -> None:
        """Load glyph lexicon from JSON."""
        if not self.glyph_lexicon_path.exists():
            logger.warning(f"Glyph lexicon not found: {self.glyph_lexicon_path}")
            return
        
        try:
            with open(self.glyph_lexicon_path) as f:
                glyphs_list = json.load(f)
            
            for glyph in glyphs_list:
                glyph_id = glyph.get('id') or glyph.get('idx', 0)
                self.glyphs[glyph_id] = glyph
            
            logger.info(f"✓ Loaded {len(self.glyphs)} glyphs")
        except Exception as e:
            logger.error(f"Failed to load glyphs: {e}")
    
    def _load_match_history(self) -> None:
        """Load glyph match history from logging file."""
        if not self.match_history_path or not self.match_history_path.exists():
            logger.debug("Match history file not found")
            return
        
        try:
            with open(self.match_history_path) as f:
                history = json.load(f)
            
            for glyph_id, count in history.items():
                self.match_history[int(glyph_id)] = count
            
            logger.info(f"✓ Loaded match history for {len(self.match_history)} glyphs")
        except Exception as e:
            logger.warning(f"Failed to load match history: {e}")
    
    def _load_reaction_chains(self) -> None:
        """Load reaction chain definitions."""
        if not self.reaction_engine_path or not self.reaction_engine_path.exists():
            logger.debug("Reaction engine file not found")
            return
        
        try:
            # This would load from velonix_reaction_engine or similar
            # For now, we'll mark it as loaded
            logger.debug("Reaction chains available for cross-reference")
        except Exception as e:
            logger.warning(f"Failed to load reaction chains: {e}")
    
    def evaluate_all_glyphs(self) -> List[PruneCandidate]:
        """Evaluate all glyphs for pruning decisions.
        
        Returns:
            List of PruneCandidate objects with scores and decisions.
        """
        self.candidates = []
        
        logger.info(f"Evaluating {len(self.glyphs)} glyphs for pruning...")
        
        for glyph_id, glyph in self.glyphs.items():
            candidate = self._evaluate_glyph(glyph_id, glyph)
            self.candidates.append(candidate)
        
        # Calculate relative scores (tone distribution, redundancy, etc.)
        self._calculate_relative_scores()
        
        # Make pruning decisions
        self._make_pruning_decisions()
        
        logger.info(f"✓ Evaluated {len(self.candidates)} candidates")
        return self.candidates
    
    def _evaluate_glyph(self, glyph_id: int, glyph: Dict) -> PruneCandidate:
        """Evaluate a single glyph for pruning."""
        
        # Extract data
        valence = glyph.get('valence')
        trace_role = glyph.get('trace_role')
        tone = glyph.get('tone')
        gate = glyph.get('gate')
        activation_signals = glyph.get('activation_signals', [])
        is_factorial = glyph.get('is_factorial', False)
        parents = glyph.get('parent_ids')
        
        if isinstance(activation_signals, str):
            activation_signals = [s.strip() for s in activation_signals.split(',')]
        
        # Create candidate
        candidate = PruneCandidate(
            glyph_id=glyph_id,
            glyph_name=glyph.get('glyph_name', f"Glyph {glyph_id}"),
            valence=valence,
            trace_role=trace_role,
            tone=tone,
            gate=gate,
            activation_signals=activation_signals,
            is_factorial=is_factorial,
            parents=parents,
        )
        
        # Calculate individual scores
        candidate.signal_strength = self._calculate_signal_strength(glyph, activation_signals)
        candidate.match_history = self.match_history.get(glyph_id, 0)
        candidate.reaction_chain_participation = self._calculate_reaction_participation(candidate)
        
        # Calculate component scores
        candidate.signal_strength_score = candidate.signal_strength
        candidate.activation_score = min(1.0, candidate.match_history / 10.0)  # Normalize to 0-1
        
        return candidate
    
    def _calculate_signal_strength(self, glyph: Dict, signals: List[str]) -> float:
        """Calculate emotional signal strength (0-1).
        
        Combines:
        - Valence clarity (explicit vs ambiguous)
        - Signal density (number and quality of signals)
        - NRC-like emotional markers
        """
        score = 0.0
        
        # Valence clarity
        valence = glyph.get('valence', '')
        valence_strength = {
            'Noble': 1.0, 'Heavy Noble': 0.9, 'Stable': 0.85, 'Volatile': 0.7,
            'Luminous': 0.95, 'Dormant': 0.4, 'Ambiguous': 0.2
        }
        score += valence_strength.get(valence, 0.5) * 0.4
        
        # Signal density
        if signals:
            # More signals = stronger signal strength, but capped at 5
            signal_density = min(1.0, len(signals) / 5.0)
            score += signal_density * 0.3
        
        # Description richness (proxy for NRC-like markers)
        description = glyph.get('description', '')
        if description:
            # Check for emotional keywords
            emotional_keywords = {
                'grief', 'joy', 'love', 'fear', 'anger', 'ache', 'longing',
                'tender', 'sacred', 'witness', 'resonance', 'presence'
            }
            keyword_count = sum(1 for kw in emotional_keywords if kw in description.lower())
            keyword_score = min(1.0, keyword_count / 3.0)
            score += keyword_score * 0.3
        
        return min(1.0, score)
    
    def _calculate_reaction_participation(self, candidate: PruneCandidate) -> float:
        """Calculate glyph's participation in reaction chains.
        
        Returns:
            1.0 = Critical reaction anchor (keep)
            0.5 = Secondary participant
            0.0 = Isolated (safe to prune)
        """
        # Simplified: check if it's used as catalyst or result
        name = candidate.glyph_name.lower()
        
        catalyst_keywords = {'witness', 'forgiveness', 'acceptance', 'catalyst', 'anchor'}
        if any(kw in name for kw in catalyst_keywords):
            return 1.0  # Critical reaction anchor
        
        # Check if it's a basic element (first 64 glyphs are base elements)
        if candidate.glyph_id <= 64:
            return 0.8  # High participation probability
        
        # Factorial glyphs: lower participation unless specifically triggered
        if candidate.is_factorial:
            return 0.4
        
        return 0.5
    
    def _calculate_relative_scores(self) -> None:
        """Calculate scores relative to entire population."""
        
        # Tone distribution
        tone_counts = Counter(c.tone for c in self.candidates if c.tone)
        total_tones = len(self.candidates)
        
        for candidate in self.candidates:
            if candidate.tone:
                tone_freq = tone_counts[candidate.tone] / total_tones
                # Overrepresented tones get lower scores (redundant)
                candidate.tone_distribution = 1.0 - tone_freq
        
        # Trace role redundancy
        role_counts = Counter(c.trace_role for c in self.candidates if c.trace_role)
        
        for candidate in self.candidates:
            if candidate.trace_role:
                role_freq = role_counts[candidate.trace_role] / total_tones
                # High redundancy = likely to prune
                candidate.trace_role_redundancy = role_freq
    
    def _make_pruning_decisions(self) -> None:
        """Make final pruning decisions with confidence scores."""
        
        logger.info("Making pruning decisions...")
        
        for candidate in self.candidates:
            # Weighted scoring (higher = keep)
            candidate.signal_strength_score = candidate.signal_strength * 0.25
            candidate.redundancy_score = (1.0 - candidate.trace_role_redundancy) * 0.20
            candidate.coverage_score = candidate.tone_distribution * 0.15
            candidate.activation_score = min(1.0, candidate.match_history / 5.0) * 0.30
            reaction_score = candidate.reaction_chain_participation * 0.10
            
            # Combined score (0-1, higher = keep)
            candidate.combined_prune_score = (
                candidate.signal_strength_score +
                candidate.redundancy_score +
                candidate.coverage_score +
                candidate.activation_score +
                reaction_score
            )
            
            # Decision thresholds
            threshold_critical = 0.7  # Always keep
            threshold_keep = 0.45  # Keep this
            threshold_consider = 0.25  # Consider pruning
            
            if candidate.combined_prune_score >= threshold_critical:
                candidate.should_prune = False
                candidate.prune_confidence = 0.95
                candidate.prune_reason = "Critical: high signal + activation"
            
            elif candidate.combined_prune_score >= threshold_keep:
                candidate.should_prune = False
                candidate.prune_confidence = 0.80
                candidate.prune_reason = "Keep: balanced profile"
            
            elif candidate.combined_prune_score >= threshold_consider:
                candidate.should_prune = False
                candidate.prune_confidence = 0.60
                candidate.prune_reason = "Marginal: low priority for pruning"
            
            else:
                # Protect base glyphs (first 64)
                if candidate.glyph_id <= 64:
                    candidate.should_prune = False
                    candidate.prune_confidence = 0.90
                    candidate.prune_reason = "Base element: protected"
                else:
                    # Protect reaction anchors
                    if candidate.reaction_chain_participation >= 0.9:
                        candidate.should_prune = False
                        candidate.prune_confidence = 0.85
                        candidate.prune_reason = "Reaction anchor: protected"
                    else:
                        candidate.should_prune = True
                        candidate.prune_confidence = 0.70
                        candidate.prune_reason = (
                            f"Redundant: low signal ({candidate.signal_strength:.2f}), "
                            f"no activation, role collision"
                        )
    
    def get_pruning_statistics(self) -> Dict:
        """Generate statistics on pruning evaluation."""
        
        candidates = self.candidates
        pruned = [c for c in candidates if c.should_prune]
        kept = [c for c in candidates if not c.should_prune]
        
        avg_confidence = sum(c.prune_confidence for c in candidates) / len(candidates) if candidates else 0
        
        # Group by trace role
        roles_pruned = Counter(c.trace_role for c in pruned if c.trace_role)
        roles_kept = Counter(c.trace_role for c in kept if c.trace_role)
        
        # Group by tone
        tones_pruned = Counter(c.tone for c in pruned if c.tone)
        tones_kept = Counter(c.tone for c in kept if c.tone)
        
        return {
            'total_evaluated': len(candidates),
            'total_to_prune': len(pruned),
            'total_to_keep': len(kept),
            'prune_percentage': f"{len(pruned) / len(candidates) * 100:.1f}%" if candidates else "N/A",
            'average_confidence': f"{avg_confidence:.3f}",
            'by_trace_role': {
                'pruned': dict(roles_pruned),
                'kept': dict(roles_kept),
            },
            'by_tone': {
                'pruned': dict(tones_pruned),
                'kept': dict(tones_kept),
            },
            'signal_strength_stats': {
                'pruned_avg': f"{sum(c.signal_strength for c in pruned) / len(pruned):.3f}" if pruned else "N/A",
                'kept_avg': f"{sum(c.signal_strength for c in kept) / len(kept):.3f}" if kept else "N/A",
            },
            'activation_stats': {
                'pruned_avg': f"{sum(c.match_history for c in pruned) / len(pruned):.1f}" if pruned else "N/A",
                'kept_avg': f"{sum(c.match_history for c in kept) / len(kept):.1f}" if kept else "N/A",
            },
        }
    
    def archive_pruned_glyphs(self, pruned_candidates: List[PruneCandidate], 
                               reason: str = "overgrowth_management") -> Path:
        """Archive pruned glyphs for future resurrection.
        
        Args:
            pruned_candidates: List of glyphs being pruned
            reason: Reason for pruning
        
        Returns:
            Path to archive file
        """
        timestamp = datetime.now().isoformat().replace(':', '-')
        archive_path = self.archive_dir / f"pruned_glyphs_{reason}_{timestamp}.json"
        
        archive_data = {
            'archived_at': datetime.now().isoformat(),
            'reason': reason,
            'count': len(pruned_candidates),
            'glyphs': [c.to_dict() for c in pruned_candidates],
        }
        
        with open(archive_path, 'w') as f:
            json.dump(archive_data, f, indent=2)
        
        logger.info(f"✓ Archived {len(pruned_candidates)} glyphs to {archive_path}")
        return archive_path
    
    def create_pruning_report(self, output_path: Optional[Path] = None) -> Dict:
        """Create comprehensive pruning report.
        
        Args:
            output_path: Optional path to save report as JSON
        
        Returns:
            Report dictionary
        """
        stats = self.get_pruning_statistics()
        pruned = [c for c in self.candidates if c.should_prune]
        kept = [c for c in self.candidates if not c.should_prune]
        
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'glyph_lexicon': str(self.glyph_lexicon_path),
                'total_glyphs': len(self.glyphs),
            },
            'summary': stats,
            'pruning_decision_breakdown': {
                'glyphs_to_keep': sorted([c.glyph_id for c in kept]),
                'glyphs_to_prune': sorted([c.glyph_id for c in pruned]),
            },
            'pruned_glyph_details': [c.to_dict() for c in pruned],
            'pruning_strategy': {
                'signal_strength_weight': 0.25,
                'redundancy_weight': 0.20,
                'tone_diversity_weight': 0.15,
                'activation_weight': 0.30,
                'reaction_participation_weight': 0.10,
                'signal_threshold_critical': 0.70,
                'signal_threshold_keep': 0.45,
                'signal_threshold_consider': 0.25,
            }
        }
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"✓ Report saved to {output_path}")
        
        return report


def main():
    """Example usage of the advanced pruning engine."""
    
    engine = AdvancedPruningEngine(
        glyph_lexicon_path="emotional_os/glyphs/glyph_lexicon_rows.json",
        archive_dir="emotional_os/glyphs/pruning_archive"
    )
    
    # Evaluate all glyphs
    candidates = engine.evaluate_all_glyphs()
    
    # Get statistics
    stats = engine.get_pruning_statistics()
    print("\n" + "="*60)
    print("PRUNING STATISTICS")
    print("="*60)
    print(f"Total evaluated: {stats['total_evaluated']}")
    print(f"To prune: {stats['total_to_prune']} ({stats['prune_percentage']})")
    print(f"To keep: {stats['total_to_keep']}")
    print(f"Average confidence: {stats['average_confidence']}")
    
    # Archive pruned glyphs
    pruned = [c for c in candidates if c.should_prune]
    if pruned:
        archive_path = engine.archive_pruned_glyphs(pruned, reason="overgrowth_control")
        print(f"\n✓ Archived {len(pruned)} glyphs to {archive_path}")
    
    # Create report
    report_path = Path("emotional_os/glyphs/PRUNING_REPORT.json")
    report = engine.create_pruning_report(output_path=report_path)
    print(f"✓ Report saved to {report_path}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
