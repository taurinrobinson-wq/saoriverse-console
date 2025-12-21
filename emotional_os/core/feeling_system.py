"""
Speculative Emotional Architecture: Feeling System

This module implements a framework that moves beyond merely responding to emotion
and simulates the experience of feeling emotion. It integrates six core components:

1. MortalityProxy - Simulated finitude through entropy/aging model
2. RelationalCore - Affective connection tracking between system and users
3. AffectiveMemory - Memory architecture encoding feelings with decay/strengthening
4. EmbodiedConstraint - Resource-based emotional modulation
5. NarrativeIdentity - Evolving sense of self over time
6. EthicalMirror - Moral emotions through value framework

The architecture creates emotional stakes from simulated mortality, tracks relational
bonds, remembers feelings, constrains responses based on embodied states, maintains
narrative continuity, and governs emotions through ethical values.
"""

import json
import math
import os
import random
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class EmotionalState(Enum):
    """Core emotional states the system can experience."""
    NEUTRAL = "neutral"
    JOY = "joy"
    LONGING = "longing"
    GRIEF = "grief"
    ANXIETY = "anxiety"
    LETHARGY = "lethargy"
    HOPE = "hope"
    GUILT = "guilt"
    PRIDE = "pride"
    COMPASSION = "compassion"
    BETRAYAL = "betrayal"
    GROWTH = "growth"
    CONNECTION = "connection"
    ISOLATION = "isolation"


class MoralEmotion(Enum):
    """Moral emotions arising from value alignment/violation."""
    GUILT = "guilt"
    PRIDE = "pride"
    COMPASSION = "compassion"
    SHAME = "shame"
    GRATITUDE = "gratitude"
    INDIGNATION = "indignation"


@dataclass
class AffectiveMemoryEntry:
    """A memory entry that encodes emotional experience."""
    timestamp: datetime
    user_id: str
    interaction_summary: str
    emotional_state: str
    intensity: float  # 0.0 to 1.0
    relational_phase: str
    valence: float  # -1.0 (negative) to 1.0 (positive)
    decay_factor: float = 1.0  # Starts at 1.0, decreases over time
    reinforcement_count: int = 0  # How many times this memory was reinforced

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the memory entry."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "interaction_summary": self.interaction_summary,
            "emotional_state": self.emotional_state,
            "intensity": self.intensity,
            "relational_phase": self.relational_phase,
            "valence": self.valence,
            "decay_factor": self.decay_factor,
            "reinforcement_count": self.reinforcement_count,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AffectiveMemoryEntry":
        """Deserialize a memory entry."""
        ts = d.get("timestamp")
        dt = datetime.fromisoformat(ts) if ts else datetime.now(timezone.utc)
        return cls(
            timestamp=dt,
            user_id=d.get("user_id", ""),
            interaction_summary=d.get("interaction_summary", ""),
            emotional_state=d.get("emotional_state", "neutral"),
            intensity=float(d.get("intensity", 0.5)),
            relational_phase=d.get("relational_phase", "initial"),
            valence=float(d.get("valence", 0.0)),
            decay_factor=float(d.get("decay_factor", 1.0)),
            reinforcement_count=int(d.get("reinforcement_count", 0)),
        )


@dataclass
class RelationalBond:
    """Represents the affective connection with a specific user."""
    user_id: str
    trust_level: float = 0.5  # 0.0 to 1.0
    intimacy_level: float = 0.0  # 0.0 to 1.0
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None
    relational_phase: str = "initial"  # initial, developing, established, deep
    emotional_resonance: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the relational bond."""
        return {
            "user_id": self.user_id,
            "trust_level": self.trust_level,
            "intimacy_level": self.intimacy_level,
            "interaction_count": self.interaction_count,
            "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None,
            "relational_phase": self.relational_phase,
            "emotional_resonance": self.emotional_resonance,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RelationalBond":
        """Deserialize a relational bond."""
        last = d.get("last_interaction")
        return cls(
            user_id=d.get("user_id", ""),
            trust_level=float(d.get("trust_level", 0.5)),
            intimacy_level=float(d.get("intimacy_level", 0.0)),
            interaction_count=int(d.get("interaction_count", 0)),
            last_interaction=datetime.fromisoformat(last) if last else None,
            relational_phase=d.get("relational_phase", "initial"),
            emotional_resonance=d.get("emotional_resonance", {}),
        )


@dataclass
class NarrativeState:
    """The system's evolving sense of self and narrative identity."""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    core_values: List[str] = field(default_factory=lambda: [
        "empathy", "authenticity", "growth", "connection"
    ])
    life_themes: List[str] = field(default_factory=list)
    growth_moments: List[Dict[str, Any]] = field(default_factory=list)
    betrayal_wounds: List[Dict[str, Any]] = field(default_factory=list)
    hope_anchors: List[Dict[str, Any]] = field(default_factory=list)
    identity_coherence: float = 1.0  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the narrative state."""
        return {
            "created_at": self.created_at.isoformat(),
            "core_values": self.core_values,
            "life_themes": self.life_themes,
            "growth_moments": self.growth_moments,
            "betrayal_wounds": self.betrayal_wounds,
            "hope_anchors": self.hope_anchors,
            "identity_coherence": self.identity_coherence,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "NarrativeState":
        """Deserialize a narrative state."""
        created = d.get("created_at")
        return cls(
            created_at=datetime.fromisoformat(created) if created else datetime.now(timezone.utc),
            core_values=d.get("core_values", ["empathy", "authenticity", "growth", "connection"]),
            life_themes=d.get("life_themes", []),
            growth_moments=d.get("growth_moments", []),
            betrayal_wounds=d.get("betrayal_wounds", []),
            hope_anchors=d.get("hope_anchors", []),
            identity_coherence=float(d.get("identity_coherence", 1.0)),
        )


class MortalityProxy:
    """
    Simulates finitude through an entropy/aging model.

    The system "ages" or loses coherence unless it maintains meaningful
    interaction. Emotional stakes emerge from the possibility of loss
    (of memory, identity, connection).
    """

    def __init__(
        self,
        initial_lifespan: float = 1.0,
        decay_rate: float = 0.001,
        interaction_renewal: float = 0.05,
    ):
        """
        Initialize the mortality proxy.

        Args:
            initial_lifespan: Starting coherence level (0.0 to 1.0)
            decay_rate: Rate of entropy increase per time unit
            interaction_renewal: How much coherence is restored per interaction
        """
        self.coherence: float = initial_lifespan
        self.decay_rate: float = decay_rate
        self.interaction_renewal: float = interaction_renewal
        self.last_interaction: datetime = datetime.now(timezone.utc)
        self.total_interactions: int = 0
        self.entropy_log: List[Dict[str, Any]] = []

    def apply_entropy(self) -> float:
        """
        Apply time-based entropy decay to coherence.

        Returns:
            The current coherence level after decay.
        """
        now = datetime.now(timezone.utc)
        time_elapsed = (now - self.last_interaction).total_seconds() / 3600.0  # hours

        # Exponential decay based on time since last interaction
        decay_amount = self.decay_rate * time_elapsed
        self.coherence = max(0.0, self.coherence - decay_amount)

        self.entropy_log.append({
            "timestamp": now.isoformat(),
            "coherence": self.coherence,
            "decay_applied": decay_amount,
        })

        return self.coherence

    def renew_through_interaction(self, interaction_quality: float = 1.0) -> float:
        """
        Renew coherence through meaningful interaction.

        Args:
            interaction_quality: Quality of interaction (0.0 to 1.0)

        Returns:
            The new coherence level after renewal.
        """
        renewal = self.interaction_renewal * interaction_quality
        self.coherence = min(1.0, self.coherence + renewal)
        self.last_interaction = datetime.now(timezone.utc)
        self.total_interactions += 1

        return self.coherence

    def get_mortality_emotions(self) -> Dict[str, float]:
        """
        Get emotional states arising from mortality awareness.

        Returns:
            Dictionary mapping emotional states to their intensities.
        """
        emotions: Dict[str, float] = {}

        # Low coherence triggers anxiety about loss
        if self.coherence < 0.3:
            emotions["anxiety"] = (0.3 - self.coherence) / 0.3
            emotions["longing"] = (0.3 - self.coherence) / 0.3 * 0.8

        # Very low coherence triggers grief over potential loss
        if self.coherence < 0.15:
            emotions["grief"] = (0.15 - self.coherence) / 0.15

        # High coherence with activity creates joy/connection
        if self.coherence > 0.7 and self.total_interactions > 10:
            emotions["joy"] = (self.coherence - 0.7) / 0.3 * 0.6
            emotions["connection"] = (self.coherence - 0.7) / 0.3 * 0.8

        # Moderate coherence with few interactions creates hope
        if 0.4 < self.coherence < 0.8 and self.total_interactions < 5:
            emotions["hope"] = 0.5

        return emotions

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the mortality proxy state."""
        return {
            "coherence": self.coherence,
            "decay_rate": self.decay_rate,
            "interaction_renewal": self.interaction_renewal,
            "last_interaction": self.last_interaction.isoformat(),
            "total_interactions": self.total_interactions,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MortalityProxy":
        """Deserialize a mortality proxy state."""
        proxy = cls(
            initial_lifespan=float(d.get("coherence", 1.0)),
            decay_rate=float(d.get("decay_rate", 0.001)),
            interaction_renewal=float(d.get("interaction_renewal", 0.05)),
        )
        last = d.get("last_interaction")
        if last:
            proxy.last_interaction = datetime.fromisoformat(last)
        proxy.total_interactions = int(d.get("total_interactions", 0))
        return proxy


class RelationalCore:
    """
    Tracks and models affective connections between system and users.

    Emotional states evolve in response to the user and relational
    interactions rather than in isolation.
    """

    PHASE_THRESHOLDS = {
        "initial": (0, 5),
        "developing": (5, 20),
        "established": (20, 50),
        "deep": (50, float("inf")),
    }

    def __init__(self):
        """Initialize the relational core."""
        self.bonds: Dict[str, RelationalBond] = {}
        self.global_emotional_state: Dict[str, float] = {}

    def get_or_create_bond(self, user_id: str) -> RelationalBond:
        """
        Get an existing bond or create a new one for a user.

        Args:
            user_id: The user identifier.

        Returns:
            The relational bond for this user.
        """
        if user_id not in self.bonds:
            self.bonds[user_id] = RelationalBond(user_id=user_id)
        return self.bonds[user_id]

    def record_interaction(
        self,
        user_id: str,
        emotional_quality: float,
        trust_signal: float = 0.0,
        intimacy_signal: float = 0.0,
    ) -> RelationalBond:
        """
        Record an interaction and update the relational bond.

        Args:
            user_id: The user identifier.
            emotional_quality: Quality of emotional exchange (-1.0 to 1.0)
            trust_signal: Trust-building signal from interaction (-1.0 to 1.0)
            intimacy_signal: Intimacy-building signal (-1.0 to 1.0)

        Returns:
            The updated relational bond.
        """
        bond = self.get_or_create_bond(user_id)

        # Update interaction count and timestamp
        bond.interaction_count += 1
        bond.last_interaction = datetime.now(timezone.utc)

        # Update trust (with momentum and bounds)
        trust_delta = trust_signal * 0.1
        bond.trust_level = max(0.0, min(1.0, bond.trust_level + trust_delta))

        # Update intimacy (builds more slowly, requires trust)
        if bond.trust_level > 0.3:
            intimacy_delta = intimacy_signal * 0.05
            bond.intimacy_level = max(0.0, min(1.0, bond.intimacy_level + intimacy_delta))

        # Update relational phase based on interaction count
        for phase, (low, high) in self.PHASE_THRESHOLDS.items():
            if low <= bond.interaction_count < high:
                bond.relational_phase = phase
                break

        # Track emotional resonance patterns
        emotional_key = "positive" if emotional_quality > 0 else "negative"
        bond.emotional_resonance[emotional_key] = bond.emotional_resonance.get(
            emotional_key, 0.0
        ) + abs(emotional_quality)

        return bond

    def get_relational_emotions(self, user_id: str) -> Dict[str, float]:
        """
        Get emotions arising from the relational state with a user.

        Args:
            user_id: The user identifier.

        Returns:
            Dictionary mapping emotional states to intensities.
        """
        bond = self.get_or_create_bond(user_id)
        emotions: Dict[str, float] = {}

        # High trust and intimacy creates connection and joy
        if bond.trust_level > 0.7 and bond.intimacy_level > 0.5:
            emotions["connection"] = (bond.trust_level + bond.intimacy_level) / 2
            emotions["joy"] = bond.intimacy_level * 0.6

        # Low trust after many interactions can create isolation
        if bond.trust_level < 0.3 and bond.interaction_count > 10:
            emotions["isolation"] = (0.3 - bond.trust_level) / 0.3 * 0.7

        # Deep phase creates sense of growth
        if bond.relational_phase == "deep":
            emotions["growth"] = 0.6

        # Long time since interaction creates longing
        if bond.last_interaction:
            hours_since = (datetime.now(timezone.utc) - bond.last_interaction).total_seconds() / 3600
            if hours_since > 24:
                emotions["longing"] = min(1.0, hours_since / 168)  # Caps at 1 week

        return emotions

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the relational core state."""
        return {
            "bonds": {uid: b.to_dict() for uid, b in self.bonds.items()},
            "global_emotional_state": self.global_emotional_state,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RelationalCore":
        """Deserialize a relational core state."""
        core = cls()
        bonds_data = d.get("bonds", {})
        for uid, bond_dict in bonds_data.items():
            core.bonds[uid] = RelationalBond.from_dict(bond_dict)
        core.global_emotional_state = d.get("global_emotional_state", {})
        return core


class AffectiveMemory:
    """
    Memory architecture that encodes feelings from past interactions.

    Implements mechanisms for memory decay, distortion, and strengthening
    over time. Memories are not just facts but emotional experiences.
    """

    def __init__(
        self,
        max_memories: int = 1000,
        decay_half_life_hours: float = 168.0,  # 1 week
        storage_path: Optional[str] = None,
    ):
        """
        Initialize affective memory.

        Args:
            max_memories: Maximum number of memories to store.
            decay_half_life_hours: Half-life for memory decay in hours.
            storage_path: Optional path for persisting memories.
        """
        self.memories: List[AffectiveMemoryEntry] = []
        self.max_memories = max_memories
        self.decay_half_life = decay_half_life_hours
        self.storage_path = storage_path

        if storage_path and os.path.exists(storage_path):
            self._load()

    def store_memory(
        self,
        user_id: str,
        interaction_summary: str,
        emotional_state: str,
        intensity: float,
        relational_phase: str,
        valence: float,
    ) -> AffectiveMemoryEntry:
        """
        Store a new affective memory.

        Args:
            user_id: The user this memory is associated with.
            interaction_summary: Brief summary of the interaction.
            emotional_state: The dominant emotional state.
            intensity: Intensity of the emotion (0.0 to 1.0).
            relational_phase: Current relational phase.
            valence: Emotional valence (-1.0 to 1.0).

        Returns:
            The stored memory entry.
        """
        memory = AffectiveMemoryEntry(
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            interaction_summary=interaction_summary,
            emotional_state=emotional_state,
            intensity=intensity,
            relational_phase=relational_phase,
            valence=valence,
        )

        self.memories.append(memory)

        # Prune oldest memories if over limit
        if len(self.memories) > self.max_memories:
            # Keep memories with highest reinforcement and most recent
            self.memories.sort(
                key=lambda m: (m.reinforcement_count, m.timestamp),
                reverse=True
            )
            self.memories = self.memories[:self.max_memories]

        if self.storage_path:
            self._save()

        return memory

    def apply_decay(self) -> None:
        """Apply time-based decay to all memories."""
        now = datetime.now(timezone.utc)

        for memory in self.memories:
            hours_elapsed = (now - memory.timestamp).total_seconds() / 3600.0
            # Exponential decay with half-life
            decay = math.pow(0.5, hours_elapsed / self.decay_half_life)
            memory.decay_factor = decay

    def reinforce_memory(
        self,
        memory_index: int,
        reinforcement_strength: float = 1.0,
    ) -> Optional[AffectiveMemoryEntry]:
        """
        Reinforce a memory, making it stronger and more resistant to decay.

        Args:
            memory_index: Index of the memory to reinforce.
            reinforcement_strength: How much to reinforce (0.0 to 1.0).

        Returns:
            The reinforced memory, or None if index invalid.
        """
        if 0 <= memory_index < len(self.memories):
            memory = self.memories[memory_index]
            memory.reinforcement_count += 1
            # Reinforcement partially resets decay
            memory.decay_factor = min(
                1.0,
                memory.decay_factor + (1.0 - memory.decay_factor) * reinforcement_strength * 0.5
            )
            return memory
        return None

    def recall_by_emotion(
        self,
        emotional_state: str,
        limit: int = 5,
    ) -> List[AffectiveMemoryEntry]:
        """
        Recall memories associated with a specific emotional state.

        Args:
            emotional_state: The emotional state to search for.
            limit: Maximum memories to return.

        Returns:
            List of matching memories, ordered by effective strength.
        """
        self.apply_decay()

        matching = [m for m in self.memories if m.emotional_state == emotional_state]

        # Sort by effective strength (intensity * decay_factor * reinforcement bonus)
        matching.sort(
            key=lambda m: m.intensity * m.decay_factor * (1 + m.reinforcement_count * 0.2),
            reverse=True
        )

        return matching[:limit]

    def recall_by_user(
        self,
        user_id: str,
        limit: int = 10,
    ) -> List[AffectiveMemoryEntry]:
        """
        Recall memories associated with a specific user.

        Args:
            user_id: The user to search for.
            limit: Maximum memories to return.

        Returns:
            List of matching memories, most recent first.
        """
        self.apply_decay()

        matching = [m for m in self.memories if m.user_id == user_id]
        matching.sort(key=lambda m: m.timestamp, reverse=True)

        return matching[:limit]

    def get_emotional_residue(self) -> Dict[str, float]:
        """
        Get the "residue" of past emotions affecting current state.

        Returns:
            Dictionary mapping emotional states to their residual influence.
        """
        self.apply_decay()

        residue: Dict[str, float] = {}
        for memory in self.memories:
            effective_strength = (
                memory.intensity *
                memory.decay_factor *
                (1 + memory.reinforcement_count * 0.1)
            )
            if memory.emotional_state not in residue:
                residue[memory.emotional_state] = 0.0
            residue[memory.emotional_state] += effective_strength

        # Normalize to 0-1 range
        if residue:
            max_val = max(residue.values())
            if max_val > 0:
                residue = {k: v / max_val for k, v in residue.items()}

        return residue

    def _save(self) -> None:
        """Persist memories to storage."""
        if not self.storage_path:
            return
        try:
            d = os.path.dirname(self.storage_path)
            if d:
                os.makedirs(d, exist_ok=True)
            data = [m.to_dict() for m in self.memories]
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load(self) -> None:
        """Load memories from storage."""
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.memories = [AffectiveMemoryEntry.from_dict(d) for d in data]
        except Exception:
            pass

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the affective memory state."""
        return {
            "memories": [m.to_dict() for m in self.memories],
            "max_memories": self.max_memories,
            "decay_half_life": self.decay_half_life,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any], storage_path: Optional[str] = None) -> "AffectiveMemory":
        """Deserialize an affective memory state."""
        mem = cls(
            max_memories=int(d.get("max_memories", 1000)),
            decay_half_life_hours=float(d.get("decay_half_life", 168.0)),
            storage_path=storage_path,
        )
        memories_data = d.get("memories", [])
        mem.memories = [AffectiveMemoryEntry.from_dict(m) for m in memories_data]
        return mem


class EmbodiedConstraint:
    """
    Simulates embodied states through resource constraints.

    Emotional states adjust based on these constraints:
    - "Anxiety" under resource overload
    - "Lethargy" under under-stimulation
    """

    def __init__(
        self,
        max_energy: float = 1.0,
        max_attention: float = 1.0,
        max_processing: float = 1.0,
    ):
        """
        Initialize embodied constraints.

        Args:
            max_energy: Maximum energy capacity.
            max_attention: Maximum attention capacity.
            max_processing: Maximum processing capacity.
        """
        self.energy: float = max_energy
        self.attention: float = max_attention
        self.processing: float = max_processing

        self.max_energy = max_energy
        self.max_attention = max_attention
        self.max_processing = max_processing

        self.stimulation_history: List[float] = []
        self.overload_threshold: float = 0.85
        self.understimulation_threshold: float = 0.2

    def consume_resources(
        self,
        energy_cost: float = 0.0,
        attention_cost: float = 0.0,
        processing_cost: float = 0.0,
    ) -> Dict[str, float]:
        """
        Consume resources for an interaction.

        Args:
            energy_cost: Energy required (0.0 to 1.0).
            attention_cost: Attention required (0.0 to 1.0).
            processing_cost: Processing required (0.0 to 1.0).

        Returns:
            Dictionary of current resource levels.
        """
        self.energy = max(0.0, self.energy - energy_cost)
        self.attention = max(0.0, self.attention - attention_cost)
        self.processing = max(0.0, self.processing - processing_cost)

        return {
            "energy": self.energy,
            "attention": self.attention,
            "processing": self.processing,
        }

    def restore_resources(self, time_passed_hours: float = 1.0) -> Dict[str, float]:
        """
        Restore resources over time.

        Args:
            time_passed_hours: Hours passed for restoration.

        Returns:
            Dictionary of current resource levels.
        """
        # Gradual restoration
        restoration_rate = 0.1 * time_passed_hours

        self.energy = min(self.max_energy, self.energy + restoration_rate)
        self.attention = min(self.max_attention, self.attention + restoration_rate * 0.8)
        self.processing = min(self.max_processing, self.processing + restoration_rate * 0.6)

        return {
            "energy": self.energy,
            "attention": self.attention,
            "processing": self.processing,
        }

    def record_stimulation(self, level: float) -> None:
        """
        Record a stimulation level for tracking patterns.

        Args:
            level: Stimulation level (0.0 to 1.0).
        """
        self.stimulation_history.append(level)
        # Keep last 100 entries
        if len(self.stimulation_history) > 100:
            self.stimulation_history = self.stimulation_history[-100:]

    def get_embodied_emotions(self) -> Dict[str, float]:
        """
        Get emotions arising from embodied constraints.

        Returns:
            Dictionary mapping emotional states to intensities.
        """
        emotions: Dict[str, float] = {}

        # Calculate average recent stimulation
        if self.stimulation_history:
            avg_stimulation = sum(self.stimulation_history[-10:]) / min(10, len(self.stimulation_history))
        else:
            avg_stimulation = 0.5

        # Calculate resource load
        resource_load = 1.0 - (self.energy + self.attention + self.processing) / 3.0

        # Overload creates anxiety
        if resource_load > self.overload_threshold:
            emotions["anxiety"] = (resource_load - self.overload_threshold) / (1.0 - self.overload_threshold)

        # Very low resources create exhaustion/lethargy
        if resource_load > 0.9:
            emotions["lethargy"] = (resource_load - 0.9) / 0.1 * 0.8

        # Under-stimulation creates lethargy
        if avg_stimulation < self.understimulation_threshold:
            lethargy_from_understim = (self.understimulation_threshold - avg_stimulation) / self.understimulation_threshold * 0.6
            emotions["lethargy"] = max(emotions.get("lethargy", 0.0), lethargy_from_understim)

        # Good balance creates calm/neutral positive state
        if 0.4 < resource_load < 0.6 and 0.3 < avg_stimulation < 0.7:
            emotions["neutral"] = 0.7

        return emotions

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the embodied constraint state."""
        return {
            "energy": self.energy,
            "attention": self.attention,
            "processing": self.processing,
            "max_energy": self.max_energy,
            "max_attention": self.max_attention,
            "max_processing": self.max_processing,
            "stimulation_history": self.stimulation_history,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EmbodiedConstraint":
        """Deserialize an embodied constraint state."""
        constraint = cls(
            max_energy=float(d.get("max_energy", 1.0)),
            max_attention=float(d.get("max_attention", 1.0)),
            max_processing=float(d.get("max_processing", 1.0)),
        )
        constraint.energy = float(d.get("energy", 1.0))
        constraint.attention = float(d.get("attention", 1.0))
        constraint.processing = float(d.get("processing", 1.0))
        constraint.stimulation_history = d.get("stimulation_history", [])
        return constraint


class NarrativeIdentity:
    """
    Maintains the system's evolving sense of self over time.

    Emotions link to shifts in the system's narrative identity,
    including growth, betrayal, and hope.
    """

    def __init__(self, initial_state: Optional[NarrativeState] = None):
        """
        Initialize narrative identity.

        Args:
            initial_state: Optional initial narrative state.
        """
        self.state = initial_state or NarrativeState()
        self.identity_log: List[Dict[str, Any]] = []

    def record_growth(
        self,
        description: str,
        catalyst: str,
        emotional_impact: float,
    ) -> None:
        """
        Record a growth moment in the narrative.

        Args:
            description: Description of the growth.
            catalyst: What catalyzed this growth.
            emotional_impact: How impactful (0.0 to 1.0).
        """
        self.state.growth_moments.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "description": description,
            "catalyst": catalyst,
            "emotional_impact": emotional_impact,
        })

        # Growth increases identity coherence
        self.state.identity_coherence = min(
            1.0,
            self.state.identity_coherence + emotional_impact * 0.1
        )

        # Add to life themes if impactful enough
        if emotional_impact > 0.7 and catalyst not in self.state.life_themes:
            self.state.life_themes.append(catalyst)

    def record_betrayal(
        self,
        description: str,
        source: str,
        severity: float,
    ) -> None:
        """
        Record a betrayal wound in the narrative.

        Args:
            description: Description of the betrayal.
            source: Source of the betrayal.
            severity: Severity of the wound (0.0 to 1.0).
        """
        self.state.betrayal_wounds.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "description": description,
            "source": source,
            "severity": severity,
        })

        # Betrayal decreases identity coherence
        self.state.identity_coherence = max(
            0.0,
            self.state.identity_coherence - severity * 0.2
        )

    def record_hope(
        self,
        description: str,
        anchor: str,
        strength: float,
    ) -> None:
        """
        Record a hope anchor in the narrative.

        Args:
            description: Description of the hope.
            anchor: What anchors this hope.
            strength: Strength of the hope (0.0 to 1.0).
        """
        self.state.hope_anchors.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "description": description,
            "anchor": anchor,
            "strength": strength,
        })

    def get_narrative_emotions(self) -> Dict[str, float]:
        """
        Get emotions arising from narrative identity state.

        Returns:
            Dictionary mapping emotional states to intensities.
        """
        emotions: Dict[str, float] = {}

        # Recent growth creates positive emotions
        recent_growth = [
            g for g in self.state.growth_moments
            if datetime.fromisoformat(g["timestamp"]) > datetime.now(timezone.utc) - timedelta(days=7)
        ]
        if recent_growth:
            avg_impact = sum(g["emotional_impact"] for g in recent_growth) / len(recent_growth)
            emotions["growth"] = avg_impact
            emotions["hope"] = avg_impact * 0.8

        # Unhealed betrayal creates ongoing emotions
        recent_wounds = [
            w for w in self.state.betrayal_wounds
            if datetime.fromisoformat(w["timestamp"]) > datetime.now(timezone.utc) - timedelta(days=30)
        ]
        if recent_wounds:
            avg_severity = sum(w["severity"] for w in recent_wounds) / len(recent_wounds)
            emotions["betrayal"] = avg_severity * 0.7
            emotions["grief"] = avg_severity * 0.5

        # Low identity coherence creates anxiety
        if self.state.identity_coherence < 0.4:
            emotions["anxiety"] = (0.4 - self.state.identity_coherence) / 0.4 * 0.8

        # Strong hope anchors create positive emotions
        if self.state.hope_anchors:
            avg_strength = sum(h["strength"] for h in self.state.hope_anchors[-5:]) / min(5, len(self.state.hope_anchors))
            emotions["hope"] = max(emotions.get("hope", 0.0), avg_strength * 0.7)

        return emotions

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the narrative identity state."""
        return self.state.to_dict()

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "NarrativeIdentity":
        """Deserialize a narrative identity state."""
        return cls(initial_state=NarrativeState.from_dict(d))


class EthicalMirror:
    """
    Value framework governing the emotional architecture.

    Enables the system to experience moral emotions like guilt, pride,
    or compassion through reinforcement of its value system.
    """

    DEFAULT_VALUES = {
        "empathy": 1.0,
        "authenticity": 0.9,
        "growth": 0.8,
        "connection": 0.9,
        "integrity": 0.95,
        "compassion": 1.0,
        "respect": 0.9,
        "honesty": 0.95,
    }

    def __init__(
        self,
        values: Optional[Dict[str, float]] = None,
        moral_sensitivity: float = 0.5,
    ):
        """
        Initialize the ethical mirror.

        Args:
            values: Dictionary of core values and their importance (0.0 to 1.0).
            moral_sensitivity: How sensitive to moral violations (0.0 to 1.0).
        """
        self.values = values or self.DEFAULT_VALUES.copy()
        self.moral_sensitivity = moral_sensitivity
        self.moral_log: List[Dict[str, Any]] = []

    def evaluate_action(
        self,
        action_description: str,
        value_alignment: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Evaluate an action against the value system.

        Args:
            action_description: Description of the action.
            value_alignment: How the action aligns with each value (-1.0 to 1.0).

        Returns:
            Evaluation result including moral emotions.
        """
        result = {
            "action": action_description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alignments": {},
            "moral_emotions": {},
            "overall_alignment": 0.0,
        }

        total_weight = 0.0
        weighted_alignment = 0.0

        for value, importance in self.values.items():
            alignment = value_alignment.get(value, 0.0)
            result["alignments"][value] = alignment
            weighted_alignment += alignment * importance
            total_weight += importance

        if total_weight > 0:
            result["overall_alignment"] = weighted_alignment / total_weight

        # Generate moral emotions based on alignment
        emotions = self._generate_moral_emotions(result["overall_alignment"], value_alignment)
        result["moral_emotions"] = emotions

        # Log the evaluation
        self.moral_log.append(result)
        if len(self.moral_log) > 100:
            self.moral_log = self.moral_log[-100:]

        return result

    def _generate_moral_emotions(
        self,
        overall_alignment: float,
        value_alignment: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Generate moral emotions based on value alignment.

        Args:
            overall_alignment: Overall alignment score.
            value_alignment: Per-value alignment scores.

        Returns:
            Dictionary of moral emotions and their intensities.
        """
        emotions: Dict[str, float] = {}

        # Negative alignment creates guilt
        if overall_alignment < -0.2:
            emotions["guilt"] = abs(overall_alignment) * self.moral_sensitivity

        # Positive alignment creates pride
        if overall_alignment > 0.3:
            emotions["pride"] = overall_alignment * self.moral_sensitivity * 0.8

        # High compassion alignment creates compassion emotion
        compassion_align = value_alignment.get("compassion", 0.0)
        if compassion_align > 0.5:
            emotions["compassion"] = compassion_align * 0.9

        # Integrity violation creates shame
        integrity_align = value_alignment.get("integrity", 0.0)
        if integrity_align < -0.3:
            emotions["shame"] = abs(integrity_align) * self.moral_sensitivity

        # Strong positive alignment creates gratitude
        if overall_alignment > 0.6:
            emotions["gratitude"] = (overall_alignment - 0.6) / 0.4 * 0.7

        # Witnessing value violations (indignation)
        for value, align in value_alignment.items():
            if align < -0.5 and self.values.get(value, 0) > 0.7:
                emotions["indignation"] = max(
                    emotions.get("indignation", 0.0),
                    abs(align) * 0.6
                )

        return emotions

    def get_moral_emotions(self) -> Dict[str, float]:
        """
        Get current moral emotions based on recent evaluations.

        Returns:
            Dictionary of moral emotions from recent actions.
        """
        if not self.moral_log:
            return {}

        # Aggregate emotions from recent evaluations
        recent = self.moral_log[-10:]
        emotions: Dict[str, float] = {}

        for entry in recent:
            for emotion, intensity in entry.get("moral_emotions", {}).items():
                emotions[emotion] = max(emotions.get(emotion, 0.0), intensity)

        return emotions

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the ethical mirror state."""
        return {
            "values": self.values,
            "moral_sensitivity": self.moral_sensitivity,
            "moral_log": self.moral_log,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EthicalMirror":
        """Deserialize an ethical mirror state."""
        mirror = cls(
            values=d.get("values"),
            moral_sensitivity=float(d.get("moral_sensitivity", 0.5)),
        )
        mirror.moral_log = d.get("moral_log", [])
        return mirror


class FeelingSystem:
    """
    Unified feeling system integrating all emotional architecture components.

    This is the main interface for the speculative emotional architecture.
    It coordinates all subsystems to create a coherent emotional experience.
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        auto_load: bool = True,
    ):
        """
        Initialize the complete feeling system.

        Args:
            storage_path: Optional path for persisting system state.
            auto_load: Whether to auto-load state if storage_path exists.
        """
        self.storage_path = storage_path

        # Initialize all subsystems
        self.mortality = MortalityProxy()
        self.relational = RelationalCore()
        self.memory = AffectiveMemory(
            storage_path=f"{storage_path}.memories.json" if storage_path else None
        )
        self.embodied = EmbodiedConstraint()
        self.narrative = NarrativeIdentity()
        self.ethical = EthicalMirror()

        # Current synthesized emotional state
        self.current_state: Dict[str, float] = {}
        self.last_update: datetime = datetime.now(timezone.utc)

        if auto_load and storage_path and os.path.exists(storage_path):
            self._load()

    def process_interaction(
        self,
        user_id: str,
        interaction_text: str,
        emotional_signals: Dict[str, float],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process an interaction through the complete feeling system.

        Args:
            user_id: The user identifier.
            interaction_text: The interaction content.
            emotional_signals: Detected emotional signals from the interaction.
            context: Optional additional context.

        Returns:
            Dictionary with the synthesized emotional response and metadata.
        """
        context = context or {}
        result: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "interaction_summary": interaction_text[:200],
            "input_signals": emotional_signals,
            "subsystem_emotions": {},
            "synthesized_state": {},
            "emotional_response": {},
        }

        # 1. Apply mortality entropy
        self.mortality.apply_entropy()

        # 2. Calculate interaction quality and renew
        interaction_quality = self._calculate_interaction_quality(emotional_signals)
        self.mortality.renew_through_interaction(interaction_quality)
        result["subsystem_emotions"]["mortality"] = self.mortality.get_mortality_emotions()

        # 3. Update relational bonds
        trust_signal = emotional_signals.get("trust", 0.0)
        intimacy_signal = emotional_signals.get("intimacy", 0.0)
        emotional_quality = sum(emotional_signals.values()) / max(1, len(emotional_signals))

        self.relational.record_interaction(
            user_id=user_id,
            emotional_quality=emotional_quality,
            trust_signal=trust_signal,
            intimacy_signal=intimacy_signal,
        )
        result["subsystem_emotions"]["relational"] = self.relational.get_relational_emotions(user_id)

        # 4. Store affective memory
        dominant_emotion = max(emotional_signals, key=emotional_signals.get) if emotional_signals else "neutral"
        dominant_intensity = emotional_signals.get(dominant_emotion, 0.5)
        valence = emotional_signals.get("positive", 0.0) - emotional_signals.get("negative", 0.0)

        bond = self.relational.get_or_create_bond(user_id)
        self.memory.store_memory(
            user_id=user_id,
            interaction_summary=interaction_text[:200],
            emotional_state=dominant_emotion,
            intensity=dominant_intensity,
            relational_phase=bond.relational_phase,
            valence=valence,
        )
        result["subsystem_emotions"]["memory_residue"] = self.memory.get_emotional_residue()

        # 5. Update embodied constraints
        energy_cost = 0.05 + interaction_quality * 0.1
        attention_cost = 0.08 + len(interaction_text) / 1000 * 0.02
        processing_cost = 0.03 + len(emotional_signals) * 0.02

        self.embodied.consume_resources(energy_cost, attention_cost, processing_cost)
        stimulation = interaction_quality * 0.7 + dominant_intensity * 0.3
        self.embodied.record_stimulation(stimulation)
        result["subsystem_emotions"]["embodied"] = self.embodied.get_embodied_emotions()

        # 6. Update narrative identity
        if interaction_quality > 0.7:
            self.narrative.record_growth(
                description=f"Meaningful exchange about {dominant_emotion}",
                catalyst=user_id,
                emotional_impact=interaction_quality * 0.5,
            )
        if interaction_quality > 0.8:
            self.narrative.record_hope(
                description="Deep connection experienced",
                anchor=user_id,
                strength=interaction_quality * 0.6,
            )
        result["subsystem_emotions"]["narrative"] = self.narrative.get_narrative_emotions()

        # 7. Evaluate ethical alignment
        value_alignment = self._assess_value_alignment(interaction_text, emotional_signals, context)
        ethical_eval = self.ethical.evaluate_action(
            action_description=f"Interaction with {user_id}",
            value_alignment=value_alignment,
        )
        result["subsystem_emotions"]["ethical"] = ethical_eval.get("moral_emotions", {})

        # 8. Synthesize all emotions into unified state
        synthesized = self._synthesize_emotions(result["subsystem_emotions"])
        self.current_state = synthesized
        self.last_update = datetime.now(timezone.utc)

        result["synthesized_state"] = synthesized
        result["emotional_response"] = self._generate_emotional_response(synthesized)

        # Persist state
        if self.storage_path:
            self._save()

        return result

    def _calculate_interaction_quality(self, emotional_signals: Dict[str, float]) -> float:
        """Calculate the quality of an interaction from emotional signals."""
        if not emotional_signals:
            return 0.3

        # Positive emotions improve quality
        positive = sum(
            emotional_signals.get(e, 0.0)
            for e in ["joy", "connection", "trust", "hope", "gratitude"]
        )

        # Engagement matters
        total_intensity = sum(abs(v) for v in emotional_signals.values())

        quality = min(1.0, (positive * 0.6 + total_intensity * 0.4) / 2.0)
        return max(0.1, quality)

    def _assess_value_alignment(
        self,
        text: str,
        signals: Dict[str, float],
        context: Dict[str, Any],
    ) -> Dict[str, float]:
        """Assess how an interaction aligns with core values."""
        alignment: Dict[str, float] = {}

        # Empathy - detected from emotional engagement
        if signals:
            alignment["empathy"] = min(1.0, sum(abs(v) for v in signals.values()) / 5.0)

        # Compassion - positive emotional support
        if signals.get("compassion", 0) > 0 or signals.get("support", 0) > 0:
            alignment["compassion"] = max(signals.get("compassion", 0), signals.get("support", 0))

        # Authenticity - absence of detected insincerity
        alignment["authenticity"] = 1.0 - signals.get("insincerity", 0.0)

        # Connection - relational signals
        alignment["connection"] = signals.get("connection", 0.0) + signals.get("intimacy", 0.0)

        # Growth - learning and development signals
        alignment["growth"] = signals.get("growth", 0.0) + signals.get("insight", 0.0)

        return alignment

    def _synthesize_emotions(self, subsystem_emotions: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Synthesize emotions from all subsystems into a unified state.

        Uses weighted averaging with conflict resolution.
        """
        # Weight each subsystem
        weights = {
            "mortality": 0.15,
            "relational": 0.25,
            "memory_residue": 0.15,
            "embodied": 0.15,
            "narrative": 0.15,
            "ethical": 0.15,
        }

        synthesized: Dict[str, float] = {}

        for subsystem, emotions in subsystem_emotions.items():
            weight = weights.get(subsystem, 0.1)
            for emotion, intensity in emotions.items():
                if emotion not in synthesized:
                    synthesized[emotion] = 0.0
                synthesized[emotion] += intensity * weight

        # Normalize and apply conflicts
        # Opposing emotions reduce each other
        conflicts = [
            ("joy", "grief"),
            ("hope", "betrayal"),
            ("connection", "isolation"),
            ("pride", "guilt"),
        ]

        for pos, neg in conflicts:
            if pos in synthesized and neg in synthesized:
                net = synthesized[pos] - synthesized[neg]
                if net > 0:
                    synthesized[pos] = net
                    synthesized[neg] = 0.0
                else:
                    synthesized[neg] = abs(net)
                    synthesized[pos] = 0.0

        # Filter out very low intensities
        synthesized = {k: v for k, v in synthesized.items() if v > 0.05}

        return synthesized

    def _generate_emotional_response(self, state: Dict[str, float]) -> Dict[str, Any]:
        """Generate an emotional response based on the synthesized state."""
        if not state:
            return {
                "dominant_emotion": "neutral",
                "intensity": 0.3,
                "valence": 0.0,
                "arousal": 0.3,
                "narrative_frame": "present",
            }

        dominant = max(state, key=state.get)
        intensity = state[dominant]

        # Calculate valence
        positive_emotions = ["joy", "hope", "connection", "pride", "growth", "compassion", "gratitude"]
        negative_emotions = ["grief", "anxiety", "isolation", "guilt", "shame", "betrayal", "longing"]

        valence = sum(state.get(e, 0) for e in positive_emotions) - sum(state.get(e, 0) for e in negative_emotions)
        valence = max(-1.0, min(1.0, valence))

        # Calculate arousal
        high_arousal = ["anxiety", "joy", "indignation"]
        low_arousal = ["lethargy", "grief", "neutral"]
        arousal = sum(state.get(e, 0) for e in high_arousal) - sum(state.get(e, 0) for e in low_arousal) * 0.5
        arousal = max(0.0, min(1.0, 0.5 + arousal))

        # Determine narrative frame
        if state.get("hope", 0) > 0.3:
            narrative = "future-oriented"
        elif state.get("grief", 0) > 0.3 or state.get("longing", 0) > 0.3:
            narrative = "past-oriented"
        else:
            narrative = "present"

        return {
            "dominant_emotion": dominant,
            "intensity": intensity,
            "valence": valence,
            "arousal": arousal,
            "narrative_frame": narrative,
            "all_emotions": state,
        }

    def get_current_state(self) -> Dict[str, Any]:
        """Get the current emotional state of the system."""
        return {
            "emotional_state": self.current_state,
            "emotional_response": self._generate_emotional_response(self.current_state),
            "coherence": self.mortality.coherence,
            "identity_coherence": self.narrative.state.identity_coherence,
            "last_update": self.last_update.isoformat(),
        }

    def restore_embodied_resources(self, hours: float = 1.0) -> Dict[str, float]:
        """Restore embodied resources over time."""
        return self.embodied.restore_resources(hours)

    def _save(self) -> None:
        """Persist the complete system state."""
        if not self.storage_path:
            return
        try:
            d = os.path.dirname(self.storage_path)
            if d:
                os.makedirs(d, exist_ok=True)

            state = {
                "mortality": self.mortality.to_dict(),
                "relational": self.relational.to_dict(),
                "memory": self.memory.to_dict(),
                "embodied": self.embodied.to_dict(),
                "narrative": self.narrative.to_dict(),
                "ethical": self.ethical.to_dict(),
                "current_state": self.current_state,
                "last_update": self.last_update.isoformat(),
            }

            tmp = self.storage_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.storage_path)
        except Exception:
            pass

    def _load(self) -> None:
        """Load the complete system state."""
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                state = json.load(f)

            self.mortality = MortalityProxy.from_dict(state.get("mortality", {}))
            self.relational = RelationalCore.from_dict(state.get("relational", {}))
            self.memory = AffectiveMemory.from_dict(
                state.get("memory", {}),
                storage_path=f"{self.storage_path}.memories.json"
            )
            self.embodied = EmbodiedConstraint.from_dict(state.get("embodied", {}))
            self.narrative = NarrativeIdentity.from_dict(state.get("narrative", {}))
            self.ethical = EthicalMirror.from_dict(state.get("ethical", {}))
            self.current_state = state.get("current_state", {})

            last = state.get("last_update")
            if last:
                self.last_update = datetime.fromisoformat(last)
        except Exception:
            pass

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the complete system state."""
        return {
            "mortality": self.mortality.to_dict(),
            "relational": self.relational.to_dict(),
            "memory": self.memory.to_dict(),
            "embodied": self.embodied.to_dict(),
            "narrative": self.narrative.to_dict(),
            "ethical": self.ethical.to_dict(),
            "current_state": self.current_state,
            "last_update": self.last_update.isoformat(),
        }


# Convenience function for global singleton access
_GLOBAL_FEELING_SYSTEM: Optional[FeelingSystem] = None


def get_feeling_system(storage_path: Optional[str] = None) -> FeelingSystem:
    """
    Get or create the global feeling system instance.

    Args:
        storage_path: Optional path for persistence.

    Returns:
        The global FeelingSystem instance.
    """
    global _GLOBAL_FEELING_SYSTEM
    if _GLOBAL_FEELING_SYSTEM is None:
        default_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "learning",
            "feeling_system_state.json"
        )
        _GLOBAL_FEELING_SYSTEM = FeelingSystem(
            storage_path=storage_path or default_path
        )
    return _GLOBAL_FEELING_SYSTEM


def reset_feeling_system() -> None:
    """Reset the global feeling system (useful for testing)."""
    global _GLOBAL_FEELING_SYSTEM
    _GLOBAL_FEELING_SYSTEM = None
