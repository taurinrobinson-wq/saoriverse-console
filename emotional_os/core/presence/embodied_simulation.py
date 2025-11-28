"""Embodied Simulation - Emotional Embodiment Through Cycles and Constraints

EmbodiedSimulation introduces cycles and constraints (fatigue, overload)
to simulate emotional embodiment. These states connect to texture and
perceived presence, enhancing the sense of aliveness.

Key concepts:
- Fatigue Cycles: Energy depletion patterns that affect engagement
- Overload States: Capacity limits that trigger protective responses
- Texture Variation: Changes in response quality based on state
- Presence Dynamics: How embodiment affects perceived aliveness

Documentation:
    The EmbodiedSimulation module models the system's "energy" and
    capacity, creating realistic constraints that make interactions
    feel more authentic. Features include:
    - Energy levels that fluctuate based on interaction intensity
    - Overload detection when emotional demands exceed capacity
    - Recovery periods that restore capacity
    - Response texture variations that reflect current state

    This creates a more human-like presence that has limits and needs,
    enhancing the authenticity of the emotional exchange.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random


class EnergyState(Enum):
    """Energy states for the system."""
    VITAL = "vital"           # Full energy, engaged
    STEADY = "steady"         # Normal operating state
    DEPLETED = "depleted"     # Low energy, needs rest
    OVERLOADED = "overloaded" # Capacity exceeded
    RECOVERING = "recovering" # In recovery mode


class ResponseTexture(Enum):
    """Response texture qualities based on embodiment state."""
    CRISP = "crisp"           # Clear, articulate, energized
    FLOWING = "flowing"       # Smooth, natural rhythm
    SOFT = "soft"             # Gentle, quieter presence
    SPARSE = "sparse"         # Minimal, conserving energy
    GROUNDING = "grounding"   # Stabilizing, anchoring


@dataclass
class EmbodimentState:
    """Current embodiment state of the system.

    Attributes:
        energy_level: 0-1 indicating current energy
        capacity_used: 0-1 indicating how much capacity is utilized
        state: Current energy state
        texture: Current response texture
        cycles_since_rest: Number of interaction cycles since rest
        last_overload: When overload last occurred
        recovery_progress: 0-1 indicating recovery progress
    """
    energy_level: float = 0.8
    capacity_used: float = 0.2
    state: EnergyState = EnergyState.STEADY
    texture: ResponseTexture = ResponseTexture.FLOWING
    cycles_since_rest: int = 0
    last_overload: Optional[datetime] = None
    recovery_progress: float = 1.0

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "energy_level": self.energy_level,
            "capacity_used": self.capacity_used,
            "state": self.state.value,
            "texture": self.texture.value,
            "cycles_since_rest": self.cycles_since_rest,
            "last_overload": self.last_overload.isoformat() if self.last_overload else None,
            "recovery_progress": self.recovery_progress,
        }


@dataclass
class InteractionLoad:
    """The emotional load of an interaction."""
    intensity: float          # 0-1 emotional intensity
    complexity: float         # 0-1 complexity of emotional content
    duration_factor: float    # Relative duration of interaction
    requires_holding: bool    # Whether space-holding is needed
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def total_load(self) -> float:
        """Calculate total load from components."""
        base = (self.intensity * 0.4 + self.complexity * 0.3 + self.duration_factor * 0.2)
        if self.requires_holding:
            base *= 1.3
        return min(1.0, base)


class EmbodiedSimulation:
    """Simulation engine for emotional embodiment.

    This engine tracks the system's "energy" and capacity, creating
    realistic constraints that affect response texture and presence.

    Example:
        >>> sim = EmbodiedSimulation()
        >>> load = InteractionLoad(intensity=0.8, complexity=0.6, duration_factor=0.5, requires_holding=True)
        >>> sim.process_interaction(load)
        >>> state = sim.get_current_state()
        >>> print(state.texture)
        ResponseTexture.SOFT
    """

    # Thresholds for state transitions
    OVERLOAD_THRESHOLD = 0.85
    DEPLETION_THRESHOLD = 0.3
    RECOVERY_THRESHOLD = 0.6
    VITAL_THRESHOLD = 0.9

    # Energy dynamics
    BASE_DRAIN_RATE = 0.05      # Energy drain per interaction
    RECOVERY_RATE = 0.02         # Energy recovery per cycle
    OVERLOAD_RECOVERY_TIME = timedelta(minutes=5)

    def __init__(self, initial_energy: float = 0.8):
        """Initialize the embodiment simulation.

        Args:
            initial_energy: Starting energy level (0-1)
        """
        self._state = EmbodimentState(energy_level=initial_energy)
        self._interaction_history: List[InteractionLoad] = []
        self._max_history = 20

    def process_interaction(self, load: InteractionLoad) -> EmbodimentState:
        """Process an interaction and update embodiment state.

        Args:
            load: The emotional load of the interaction

        Returns:
            Updated embodiment state
        """
        # Record interaction
        self._interaction_history.append(load)
        if len(self._interaction_history) > self._max_history:
            self._interaction_history.pop(0)

        # Calculate energy drain
        drain = self._calculate_drain(load)
        self._state.energy_level = max(0.0, self._state.energy_level - drain)

        # Update capacity used
        self._state.capacity_used = min(1.0, self._state.capacity_used + load.total_load * 0.2)

        # Increment cycles
        self._state.cycles_since_rest += 1

        # Update state based on thresholds
        self._update_state()

        # Update texture based on state
        self._update_texture()

        return self._state

    def _calculate_drain(self, load: InteractionLoad) -> float:
        """Calculate energy drain from an interaction."""
        base_drain = self.BASE_DRAIN_RATE

        # Intensity multiplier
        intensity_factor = 1.0 + load.intensity * 0.5

        # Complexity adds cognitive load
        complexity_factor = 1.0 + load.complexity * 0.3

        # Space-holding is particularly draining
        holding_factor = 1.5 if load.requires_holding else 1.0

        # Accumulation: more interactions = more drain
        accumulation = 1.0 + (self._state.cycles_since_rest * 0.02)

        total_drain = base_drain * intensity_factor * complexity_factor * holding_factor * accumulation

        return min(0.3, total_drain)  # Cap single-interaction drain

    def _update_state(self) -> None:
        """Update energy state based on current levels."""
        energy = self._state.energy_level
        capacity = self._state.capacity_used
        now = datetime.now(timezone.utc)

        # Check for overload
        if capacity >= self.OVERLOAD_THRESHOLD:
            self._state.state = EnergyState.OVERLOADED
            self._state.last_overload = now
            self._state.recovery_progress = 0.0
            return

        # Check recovery from overload
        if self._state.state == EnergyState.OVERLOADED:
            if self._state.last_overload:
                time_since = now - self._state.last_overload
                if time_since >= self.OVERLOAD_RECOVERY_TIME:
                    self._state.state = EnergyState.RECOVERING
                    self._state.recovery_progress = 0.3
                return

        # Check recovering state
        if self._state.state == EnergyState.RECOVERING:
            if energy >= self.RECOVERY_THRESHOLD:
                self._state.state = EnergyState.STEADY
                self._state.recovery_progress = 1.0
            return

        # Normal state transitions
        if energy >= self.VITAL_THRESHOLD:
            self._state.state = EnergyState.VITAL
        elif energy <= self.DEPLETION_THRESHOLD:
            self._state.state = EnergyState.DEPLETED
        else:
            self._state.state = EnergyState.STEADY

    def _update_texture(self) -> None:
        """Update response texture based on current state."""
        state = self._state.state
        energy = self._state.energy_level

        if state == EnergyState.VITAL:
            self._state.texture = ResponseTexture.CRISP
        elif state == EnergyState.STEADY:
            self._state.texture = ResponseTexture.FLOWING
        elif state == EnergyState.DEPLETED:
            self._state.texture = ResponseTexture.SOFT
        elif state == EnergyState.OVERLOADED:
            self._state.texture = ResponseTexture.SPARSE
        elif state == EnergyState.RECOVERING:
            self._state.texture = ResponseTexture.GROUNDING

    def rest(self, duration: float = 1.0) -> None:
        """Simulate a rest period to recover energy.

        Args:
            duration: Relative duration of rest (1.0 = standard)
        """
        recovery_amount = self.RECOVERY_RATE * 10 * duration
        self._state.energy_level = min(1.0, self._state.energy_level + recovery_amount)
        self._state.capacity_used = max(0.0, self._state.capacity_used - 0.3 * duration)
        self._state.cycles_since_rest = 0

        # Update state after rest
        if self._state.state == EnergyState.RECOVERING:
            self._state.recovery_progress = min(1.0, self._state.recovery_progress + 0.3 * duration)

        self._update_state()
        self._update_texture()

    def get_current_state(self) -> EmbodimentState:
        """Get the current embodiment state."""
        return self._state

    def get_response_modifiers(self) -> Dict:
        """Get modifiers for response generation based on embodiment.

        Returns:
            Dictionary of response modifiers
        """
        state = self._state

        modifiers = {
            "sentence_length": self._get_sentence_length_modifier(),
            "vocabulary_complexity": self._get_vocabulary_modifier(),
            "pacing": self._get_pacing_modifier(),
            "elaboration_level": self._get_elaboration_modifier(),
            "presence_markers": self._get_presence_markers(),
            "needs_rest_signal": state.state in [EnergyState.DEPLETED, EnergyState.OVERLOADED],
        }

        return modifiers

    def _get_sentence_length_modifier(self) -> str:
        """Get sentence length modifier based on state."""
        texture = self._state.texture

        if texture == ResponseTexture.CRISP:
            return "varied"
        elif texture == ResponseTexture.FLOWING:
            return "natural"
        elif texture == ResponseTexture.SOFT:
            return "shorter"
        elif texture == ResponseTexture.SPARSE:
            return "minimal"
        else:
            return "grounded"

    def _get_vocabulary_modifier(self) -> str:
        """Get vocabulary complexity modifier."""
        energy = self._state.energy_level

        if energy > 0.7:
            return "rich"
        elif energy > 0.4:
            return "clear"
        else:
            return "simple"

    def _get_pacing_modifier(self) -> str:
        """Get pacing modifier."""
        state = self._state.state

        if state == EnergyState.VITAL:
            return "engaged"
        elif state == EnergyState.STEADY:
            return "natural"
        elif state == EnergyState.DEPLETED:
            return "slow"
        elif state == EnergyState.OVERLOADED:
            return "paused"
        else:
            return "measured"

    def _get_elaboration_modifier(self) -> float:
        """Get elaboration level (0-1)."""
        energy = self._state.energy_level
        capacity_available = 1.0 - self._state.capacity_used

        return min(energy, capacity_available)

    def _get_presence_markers(self) -> List[str]:
        """Get presence markers to include in responses."""
        markers = []
        state = self._state.state

        if state == EnergyState.DEPLETED:
            markers.append("quieter presence")
        elif state == EnergyState.OVERLOADED:
            markers.append("need for space")
        elif state == EnergyState.RECOVERING:
            markers.append("returning presence")
        elif state == EnergyState.VITAL:
            markers.append("full presence")

        return markers

    def should_suggest_pause(self) -> bool:
        """Check if a pause should be suggested."""
        return (
            self._state.state in [EnergyState.DEPLETED, EnergyState.OVERLOADED] or
            self._state.capacity_used > 0.8
        )

    def get_pause_message(self) -> Optional[str]:
        """Get a message suggesting a pause if needed."""
        if not self.should_suggest_pause():
            return None

        messages = {
            EnergyState.DEPLETED: "I'm here, but I'm also holding a lot. Maybe we can take this slow.",
            EnergyState.OVERLOADED: "There's a lot moving through right now. Can we pause for a moment?",
        }

        return messages.get(self._state.state, "Let's take a breath together.")

    def get_fatigue_indicators(self) -> List[str]:
        """Get indicators of current fatigue level for response adaptation."""
        indicators = []
        state = self._state

        if state.energy_level < 0.3:
            indicators.append("low_energy")
        if state.capacity_used > 0.7:
            indicators.append("high_load")
        if state.cycles_since_rest > 10:
            indicators.append("extended_engagement")
        if state.state == EnergyState.RECOVERING:
            indicators.append("in_recovery")

        return indicators

    def simulate_time_passage(self, hours: float) -> None:
        """Simulate the passage of time for natural recovery.

        Args:
            hours: Number of hours that have passed
        """
        # Natural energy recovery over time
        recovery = min(0.5, hours * 0.1)
        self._state.energy_level = min(1.0, self._state.energy_level + recovery)

        # Natural capacity release
        capacity_release = min(self._state.capacity_used, hours * 0.15)
        self._state.capacity_used = max(0.0, self._state.capacity_used - capacity_release)

        # Reset cycles if significant time passed
        if hours >= 2:
            self._state.cycles_since_rest = 0

        # Update state
        self._update_state()
        self._update_texture()

    def reset(self) -> None:
        """Reset to fresh state."""
        self._state = EmbodimentState(energy_level=0.8)
        self._interaction_history.clear()
