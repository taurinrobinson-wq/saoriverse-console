"""
🧠 REMNANTS-SEMANTIC BRIDGE
===========================

Maps semantic engine outputs to REMNANTS emotional state.

This is where the semantic engine feeds the emotional OS.

The semantic engine extracts:
- contradictions
- identity injuries  
- stance arcs
- pacing progressions
- trust development
- agency loss/reclamation

The REMNANTS engine tracks:
- glyph resonance
- faction allegiance
- emotional wounds
- power dynamics
- ritual potential

This bridge connects them:
SEMANTIC FINDING          →  REMNANTS MAPPING
contradictions            →  glyph instability
identity_injury           →  shadow glyphs
stance arc                →  faction drift
trust progression         →  resonance growth
pacing changes            →  attunement shifts
agency loss               →  power vulnerability
emotional_weight          →  overall resonance
readiness                 →  ritual readiness
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime

try:
    from semantic_parsing_schema import SemanticLayer
    from continuity_engine import ConversationContinuity
except ImportError:
    print("Warning: Could not import semantic modules")


class SemanticToRemnantsMapping(Enum):
    """Enumeration of all mappings from semantic → REMNANTS."""
    
    # Semantic → Emotional State
    CONTRADICTIONS_TO_GLYPH_INSTABILITY = "contradictions → glyph_instability"
    IDENTITY_INJURY_TO_SHADOW_GLYPHS = "identity_signals → identity_injury_level"
    STANCE_TO_FACTION_RESONANCE = "stance → faction_alignment"
    PACING_TO_ATTUNEMENT = "pacing → attunement_level"
    EMOTIONAL_WEIGHT_TO_RESONANCE = "emotional_weight → overall_resonance"
    TRUST_PROGRESSION_TO_BOND_DEPTH = "trust_arc → npc_bond_depth"
    AGENCY_LOSS_TO_POWER_VULNERABILITY = "agency_loss → power_vulnerability"
    READINESS_TO_RITUAL_READINESS = "readiness → ritual_readiness"


@dataclass
class SemanticRemnantsMapping:
    """Single semantic finding and its REMNANTS impact."""
    
    mapping_type: SemanticToRemnantsMapping
    semantic_value: Any
    remnants_field: str
    remnants_delta: float  # How much to change the field
    emotional_weight: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RemnantsUpdate:
    """Complete REMNANTS update from a single semantic analysis."""
    
    player_id: str
    npc_id: str
    
    # Direct field updates
    glyph_instability: float = 0.0
    identity_injury_level: float = 0.0
    faction_alignment: Optional[str] = None
    attunement_level: float = 0.0
    overall_resonance: float = 0.0
    npc_bond_depths: Dict[str, float] = field(default_factory=dict)
    power_vulnerability: float = 0.0
    ritual_readiness: float = 0.0
    
    # Metadata
    active_contradictions: List[str] = field(default_factory=list)
    identity_markers: List[str] = field(default_factory=list)
    pacing_needs: str = ""
    emotional_weight: float = 0.0
    
    # Arcs for analytics
    stance_arc: List[str] = field(default_factory=list)
    pacing_arc: List[str] = field(default_factory=list)
    trust_arc: List[float] = field(default_factory=list)
    
    timestamp: datetime = field(default_factory=datetime.now)


class RemnantsSemanticBridge:
    """
    Translates semantic findings into REMNANTS state updates.
    
    This is the integration layer between:
    - Semantic engine (universal emotional logic)
    - REMNANTS engine (Velinor-specific emotional state)
    
    Flow:
    1. Semantic engine parses player message → SemanticLayer
    2. ContinuityEngine tracks progression → ConversationContinuity
    3. Bridge maps semantic → REMNANTS
    4. RemnantsEngine updates emotional OS
    
    The result: NPCs perceive the player's emotional state as REMNANTS.
    """
    
    def __init__(self):
        # Mapping rules for each semantic attribute
        self.contradiction_to_instability_ratio = 0.25  # Each contradiction = 0.25 instability
        self.identity_injury_ratio = 0.2  # Each identity marker = 0.2 injury
        self.pacing_attunement_map = {
            "BRACING": 0.4,
            "TESTING_SAFETY": 0.5,
            "GRADUAL_REVEAL": 0.7,
            "CONTEXTUAL_GROUNDING": 0.6,
            "EMOTIONAL_EMERGENCE": 0.8,
        }
        self.stance_resonance_map = {
            "BRACING": 0.3,
            "TESTING_SAFETY": 0.4,
            "REVEALING": 0.6,
            "AMBIVALENT": 0.5,
            "DEFENSIVE": 0.2,
            "SEEKING": 0.7,
            "INTEGRATING": 0.8,
        }
    
    def map_semantic_to_remnants(
        self,
        player_id: str,
        npc_id: str,
        semantic_layer: SemanticLayer,
        continuity: ConversationContinuity,
    ) -> RemnantsUpdate:
        """
        Convert semantic findings to REMNANTS update.
        
        This is where the semantic engine's understanding of emotional meaning
        becomes the REMNANTS engine's understanding of player state.
        
        Args:
            player_id: Unique player identifier
            npc_id: NPC being talked to (affects NPC-specific bond)
            semantic_layer: Parsed semantic attributes
            continuity: Conversation history and progression
        
        Returns:
            RemnantsUpdate with all calculated fields
        """
        
        update = RemnantsUpdate(player_id=player_id, npc_id=npc_id)
        
        # ============================================
        # CONTRADICTIONS → GLYPH INSTABILITY
        # ============================================
        
        if semantic_layer.contradictions:
            # Each contradiction destabilizes glyphs
            contradiction_count = len(semantic_layer.contradictions)
            update.glyph_instability = contradiction_count * self.contradiction_to_instability_ratio
            update.active_contradictions = semantic_layer.contradictions
            
            # High instability can trigger glyph mutations
            if update.glyph_instability > 0.75:
                # Glyphs becoming unstable - may need ritual or care
                pass
        
        # ============================================
        # IDENTITY SIGNALS → IDENTITY INJURY
        # ============================================
        
        if semantic_layer.identity_signals:
            # Each identity signal indicates potential wound
            signal_count = len(semantic_layer.identity_signals)
            update.identity_injury_level = signal_count * self.identity_injury_ratio
            update.identity_markers = semantic_layer.identity_signals
            
            # Identity injuries affect resonance
            update.overall_resonance -= update.identity_injury_level * 0.3
        
        # ============================================
        # STANCE → FACTION ALIGNMENT
        # ============================================
        
        if semantic_layer.stance:
            update.faction_alignment = str(semantic_layer.stance)
            
            # Map stance to resonance baseline
            stance_str = str(semantic_layer.stance).upper()
            base_resonance = self.stance_resonance_map.get(stance_str, 0.5)
            update.overall_resonance = base_resonance
            
            # Bracing stance = lower alignment
            # Seeking stance = higher alignment
            if "BRACING" in stance_str:
                update.overall_resonance *= 0.7
            elif "SEEKING" in stance_str:
                update.overall_resonance *= 1.2
        
        # ============================================
        # PACING → ATTUNEMENT
        # ============================================
        
        if semantic_layer.pacing:
            pacing_str = str(semantic_layer.pacing).upper()
            attunement = self.pacing_attunement_map.get(pacing_str, 0.5)
            update.attunement_level = attunement
            update.pacing_needs = str(semantic_layer.pacing)
            
            # If pacing is BRACING, player needs slower interaction
            # If pacing is EMOTIONAL_EMERGENCE, player is ready for depth
        
        # ============================================
        # EMOTIONAL WEIGHT → RESONANCE
        # ============================================
        
        update.emotional_weight = semantic_layer.emotional_weight
        
        # High emotional weight means resonance is active/volatile
        # Low emotional weight means steady/grounded
        if semantic_layer.emotional_weight > 0.7:
            # High intensity - glyphs may be activated
            update.ritual_readiness = 0.8
        elif semantic_layer.emotional_weight < 0.3:
            # Low intensity - steady, contemplative
            update.ritual_readiness = 0.3
        else:
            # Medium - balanced
            update.ritual_readiness = 0.5
        
        # ============================================
        # TRUST PROGRESSION → NPC BOND DEPTH
        # ============================================
        
        if continuity:
            trust_level = continuity.get_trust_level()
            update.npc_bond_depths[npc_id] = trust_level
            update.trust_arc = continuity.get_trust_arc()
            
            # Trust progression maps to bond depth
            # High trust = deep NPC connection = access to deeper dialogue
        
        # ============================================
        # PACING ARC → ATTUNEMENT TRAJECTORY
        # ============================================
        
        if continuity:
            pacing_arc = continuity.get_pacing_arc()
            update.pacing_arc = pacing_arc
            
            # If pacing has been slowing, player may need containment
            # If pacing has been quickening, player may be getting ready for depth
        
        # ============================================
        # STANCE ARC → FACTION DRIFT
        # ============================================
        
        if continuity:
            stance_arc = continuity.get_stance_arc()
            update.stance_arc = stance_arc
            
            # Track how player's emotional stance is evolving
            # Is player moving toward faction alignment or away?
        
        # ============================================
        # AGENCY LOSS/RECOVERY → POWER DYNAMICS
        # ============================================
        
        if continuity:
            agency_trajectory = continuity.agency_loss_trajectory
            
            # Map agency loss to power vulnerability
            agency_loss_count = len([x for x in agency_trajectory if x < 0.5])
            update.power_vulnerability = min(agency_loss_count * 0.2, 1.0)
            
            # High agency loss = vulnerable to influence
            # High agency recovery = powerful, autonomous
        
        # ============================================
        # CONTRADICTIONS CARRYING → ONGOING EFFECTS
        # ============================================
        
        active_contradictions = continuity.get_active_contradictions()
        if active_contradictions:
            # Contradictions persist across turns
            # Each turn they're active adds to glyph instability
            update.glyph_instability = max(
                update.glyph_instability,
                len(active_contradictions) * self.contradiction_to_instability_ratio
            )
        
        return update
    
    def compute_agency_trajectory_impact(
        self,
        continuity: ConversationContinuity,
    ) -> Tuple[float, str]:
        """
        Analyze agency trajectory and return impact assessment.
        
        Returns:
            (power_vulnerability: 0.0-1.0, status: str)
            
        Status examples:
            "recovering" - player regaining agency
            "sustained" - player maintaining agency
            "vulnerable" - player has lost significant agency
            "critical" - player in severe vulnerability
        """
        
        trajectory = continuity.agency_loss_trajectory
        
        if not trajectory:
            return (0.0, "grounded")
        
        # Analyze trend
        recent_3 = trajectory[-3:] if len(trajectory) >= 3 else trajectory
        avg_recent = sum(recent_3) / len(recent_3)
        
        # Calculate vulnerability
        vulnerability = max(0.0, 1.0 - avg_recent)
        
        # Determine status
        if vulnerability > 0.7:
            status = "critical"
        elif vulnerability > 0.5:
            status = "vulnerable"
        elif avg_recent < 0.4:
            status = "recovering"
        else:
            status = "sustained"
        
        return (vulnerability, status)
    
    def compute_identity_injury_severity(
        self,
        semantic_layer: SemanticLayer,
        continuity: ConversationContinuity,
    ) -> Tuple[float, str]:
        """
        Assess identity injury severity and trajectory.
        
        Returns:
            (severity: 0.0-1.0, trajectory: str)
            
        Trajectory examples:
            "acute" - fresh identity wound
            "persistent" - ongoing injury
            "healing" - recovering
            "resolved" - integrated
        """
        
        current_injury = len(semantic_layer.identity_signals) * self.identity_injury_ratio
        
        # Check continuity for trend
        if continuity:
            identity_history = continuity.all_identity_signals
            recent_count = len([x for x in identity_history[-3:] if x])
            
            if recent_count > current_injury * 3:
                trajectory = "acute"
            elif recent_count > current_injury:
                trajectory = "persistent"
            else:
                trajectory = "healing"
        else:
            trajectory = "acute"
        
        return (current_injury, trajectory)
    
    def compute_contradiction_complexity(
        self,
        continuity: ConversationContinuity,
    ) -> Tuple[float, List[str], str]:
        """
        Assess contradiction system complexity.
        
        Returns:
            (complexity_score: 0.0-1.0, active_contradictions: List[str], pattern: str)
            
        Pattern examples:
            "simple" - 1 contradiction
            "complex" - 2-3 contradictions
            "systemic" - 4+ contradictions (glyph unstable)
        """
        
        active = continuity.get_active_contradictions()
        count = len(active)
        
        # Complexity is nonlinear (multiple contradictions compound)
        complexity = min((count / 4.0) ** 1.5, 1.0)
        
        if count <= 1:
            pattern = "simple"
        elif count <= 3:
            pattern = "complex"
        else:
            pattern = "systemic"
        
        return (complexity, active, pattern)
    
    def compute_readiness_for_depth(
        self,
        semantic_layer: SemanticLayer,
        continuity: ConversationContinuity,
    ) -> Tuple[float, str]:
        """
        Assess whether player is ready for deeper engagement.
        
        Factors:
        - semantic_layer.readiness flag
        - trust level (high trust = ready)
        - contradiction carrying (can hold paradox = ready)
        - agency level (stable agency = ready)
        - identity integration (processed injuries = ready)
        
        Returns:
            (readiness_score: 0.0-1.0, recommendation: str)
            
        Recommendation examples:
            "slow_down" - overwhelming, needs containment
            "maintain_pace" - steady, continue current pacing
            "deepen" - ready for vulnerability
            "accelerate" - ready for rapid emotional work
        """
        
        readiness_score = 0.0
        
        # Factor 1: Explicit readiness flag
        if getattr(semantic_layer, 'readiness', False):
            readiness_score += 0.3
        
        # Factor 2: Trust level
        if continuity:
            trust = continuity.get_trust_level()
            readiness_score += trust * 0.25  # 0.0-0.25
        
        # Factor 3: Can hold contradictions
        if continuity:
            _, _, pattern = self.compute_contradiction_complexity(continuity)
            if pattern == "complex":
                readiness_score += 0.2
        
        # Factor 4: Agency stability
        if continuity:
            vulnerability, status = self.compute_agency_trajectory_impact(continuity)
            if status == "sustained":
                readiness_score += 0.15
        
        # Factor 5: Identity integration
        if continuity:
            injury, trajectory = self.compute_identity_injury_severity(semantic_layer, continuity)
            if trajectory == "healing":
                readiness_score += 0.1
        
        # Emotional weight consideration
        if semantic_layer.emotional_weight > 0.8:
            # High emotional weight = less ready for depth
            readiness_score *= 0.7
        
        # Determine recommendation
        if readiness_score < 0.2:
            recommendation = "slow_down"
        elif readiness_score < 0.4:
            recommendation = "maintain_pace"
        elif readiness_score < 0.7:
            recommendation = "deepen"
        else:
            recommendation = "accelerate"
        
        return (min(readiness_score, 1.0), recommendation)


# ============================================
# HELPER FUNCTIONS
# ============================================

def assess_emotional_state(
    semantic_layer: SemanticLayer,
    continuity: ConversationContinuity,
) -> Dict[str, Any]:
    """
    Comprehensive assessment of player's emotional state.
    
    Returns assessment across all dimensions:
    - glyph instability
    - identity injury
    - trust level
    - agency status
    - readiness for depth
    - pacing needs
    """
    
    bridge = RemnantsSemanticBridge()
    
    agency_vuln, agency_status = bridge.compute_agency_trajectory_impact(continuity)
    identity_sev, identity_traj = bridge.compute_identity_injury_severity(semantic_layer, continuity)
    contradiction_comp, active_contra, contra_pattern = bridge.compute_contradiction_complexity(continuity)
    readiness, depth_rec = bridge.compute_readiness_for_depth(semantic_layer, continuity)
    
    return {
        "glyph_instability": contradiction_comp,
        "identity_injury": identity_sev,
        "identity_trajectory": identity_traj,
        "trust_level": continuity.get_trust_level() if continuity else 0.5,
        "agency_vulnerability": agency_vuln,
        "agency_status": agency_status,
        "active_contradictions": active_contra,
        "contradiction_pattern": contra_pattern,
        "readiness_for_depth": readiness,
        "depth_recommendation": depth_rec,
        "pacing_needs": str(semantic_layer.pacing) if semantic_layer.pacing else "unknown",
        "emotional_weight": semantic_layer.emotional_weight if semantic_layer else 0.5,
    }
