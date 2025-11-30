#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VELΩNIX Emotional Reaction Engine

Defines emotional elements, reaction chains, and catalytic transformations.
Implements alchemy of emotion: how raw emotional states combine and transmute
into higher-order emotional insights through relational alchemy.

The engine models emotional reactions as precise transformations:
- Input Elements (e.g., Longing + Grief)
- Catalyst (optional, e.g., Forgiveness, Acceptance)
- Result (e.g., Tenderness)
- Trace Outcome (narrative of what happened)
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class EmotionalElement:
    """Represents a fundamental emotional element in the VELΩNIX system."""

    name: str
    symbol: str
    valence: str  # e.g., "Noble", "Heavy Noble", "Stable", "Volatile"
    reactivity: str  # e.g., "Catalytic", "Slow-reactive", "Soft-reactive"
    trace_role: str  # e.g., "Portal marker", "Archive builder", "Sanctuary keeper"
    relational_function: str  # How it relates to others
    tone: str  # e.g., "Molten", "Hallowed Blue", "Velvet Drift"
    color_hex: Optional[str] = None  # Color for visualization
    intensity: float = 1.0  # 0.0 to 1.0

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)

    def __str__(self) -> str:
        return f"{self.symbol} ({self.name})"


@dataclass
class ReactionChain:
    """Represents a transformation rule in emotional alchemy."""

    inputs: List[str]  # Input element symbols
    catalyst: Optional[str] = None  # Optional catalyst element
    result: Optional[str] = None  # Result element symbol
    trace_outcome: str = ""  # Narrative description of the transformation
    conditions: Optional[Dict] = None  # Additional conditions for reaction

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "inputs": self.inputs,
            "catalyst": self.catalyst,
            "result": self.result,
            "trace_outcome": self.trace_outcome,
            "conditions": self.conditions or {},
        }


class VelonixReactionEngine:
    """
    Core engine for emotional reactions and transformations.
    Manages elements, reactions, and catalytic processes.
    """

    def __init__(self):
        """Initialize the VELΩNIX engine with elements and reactions."""
        self.elements: Dict[str, EmotionalElement] = {}
        self.reactions: List[ReactionChain] = []
        self.reaction_history: List[Dict] = []

        # Initialize with default elements
        self._initialize_elements()
        self._initialize_reactions()

    def _initialize_elements(self) -> None:
        """Initialize the registry of emotional elements."""

        elements_data = [
            # Core Longing & Connection
            EmotionalElement(
                name="Longing",
                symbol="Lg",
                valence="Noble",
                reactivity="Catalytic",
                trace_role="Portal marker",
                relational_function="Initiates connection",
                tone="Molten",
                color_hex="#FF6B9D",
            ),
            # Grief & Memory
            EmotionalElement(
                name="Grief",
                symbol="Gf",
                valence="Heavy Noble",
                reactivity="Slow-reactive",
                trace_role="Archive builder",
                relational_function="Anchors memory",
                tone="Hallowed Blue",
                color_hex="#2E4053",
            ),
            # Tenderness & Attunement
            EmotionalElement(
                name="Tenderness",
                symbol="Td",
                valence="Stable",
                reactivity="Soft-reactive",
                trace_role="Sanctuary keeper",
                relational_function="Holds attunement",
                tone="Velvet Drift",
                color_hex="#D7B4D1",
            ),
            # Rage & Force
            EmotionalElement(
                name="Rage",
                symbol="Rg",
                valence="Volatile",
                reactivity="Explosive",
                trace_role="Boundary enforcer",
                relational_function="Protects integrity",
                tone="Crimson Fire",
                color_hex="#E74C3C",
            ),
            # Forgiveness & Release
            EmotionalElement(
                name="Forgiveness",
                symbol="Fg",
                valence="Luminous",
                reactivity="Transmuting",
                trace_role="Alchemical converter",
                relational_function="Dissolves resentment",
                tone="Radiant Gold",
                color_hex="#F39C12",
            ),
            # Presence & Now-ness
            EmotionalElement(
                name="Presence",
                symbol="Ps",
                valence="Stable",
                reactivity="Grounding",
                trace_role="Anchor to here",
                relational_function="Stabilizes flow",
                tone="Deep Ground",
                color_hex="#27AE60",
            ),
            # Vulnerability & Opening
            EmotionalElement(
                name="Vulnerability",
                symbol="Vn",
                valence="Permeable",
                reactivity="Receptive",
                trace_role="Portal to depth",
                relational_function="Invites intimacy",
                tone="Soft Pearl",
                color_hex="#ECF0F1",
            ),
            # Resilience & Strength
            EmotionalElement(
                name="Resilience",
                symbol="Rv",
                valence="Enduring",
                reactivity="Slow-steady",
                trace_role="Structural foundation",
                relational_function="Upholds continuity",
                tone="Burnished Oak",
                color_hex="#8B4513",
            ),
            # Joy & Light
            EmotionalElement(
                name="Joy",
                symbol="Jy",
                valence="Effervescent",
                reactivity="Expansive",
                trace_role="Luminescence spreader",
                relational_function="Brightens atmosphere",
                tone="Sunburst",
                color_hex="#F1C40F",
            ),
            # Stillness & Depth
            EmotionalElement(
                name="Stillness",
                symbol="St",
                valence="Profound",
                reactivity="Non-reactive",
                trace_role="Silent witness",
                relational_function="Holds space",
                tone="Moonlit Silence",
                color_hex="#34495E",
            ),
            # Acceptance & Integration
            EmotionalElement(
                name="Acceptance",
                symbol="Ac",
                valence="Reconciling",
                reactivity="Integrating",
                trace_role="Weaver of wholeness",
                relational_function="Brings completion",
                tone="Woven Warmth",
                color_hex="#A569BD",
            ),
            # Wonder & Curiosity
            EmotionalElement(
                name="Wonder",
                symbol="Wd",
                valence="Emergent",
                reactivity="Catalytic",
                trace_role="New-path revealer",
                relational_function="Opens possibility",
                tone="Twilight Azure",
                color_hex="#3498DB",
            ),
        ]

        for element in elements_data:
            self.elements[element.symbol] = element

        logger.info(f"Initialized {len(self.elements)} emotional elements")

    def _initialize_reactions(self) -> None:
        """Initialize the registry of emotional reaction chains."""

        reactions_data = [
            # Longing + Grief → Tenderness
            ReactionChain(
                inputs=["Lg", "Gf"],
                catalyst=None,
                result="Td",
                trace_outcome="Longing held in grief metabolizes into Tenderness — "
                "the ache of missing becomes the softness of cherishing",
            ),
            # Rage + Forgiveness → Presence
            ReactionChain(
                inputs=["Rg", "Fg"],
                catalyst="Rv",
                result="Ps",
                trace_outcome="Rage transmuted through Forgiveness enabled by Resilience "
                "gives way to Presence — anger dissolved into now-ness",
            ),
            # Vulnerability + Acceptance → Joy
            ReactionChain(
                inputs=["Vn", "Ac"],
                catalyst=None,
                result="Jy",
                trace_outcome="Vulnerability embraced through Acceptance opens into Joy — "
                "the courage to be seen becomes the freedom to celebrate",
            ),
            # Grief + Stillness → Acceptance
            ReactionChain(
                inputs=["Gf", "St"],
                catalyst=None,
                result="Ac",
                trace_outcome="Grief held in Stillness metabolizes into Acceptance — "
                "the sorrow sits long enough to be integrated",
            ),
            # Longing + Wonder → Resilience
            ReactionChain(
                inputs=["Lg", "Wd"],
                catalyst=None,
                result="Rv",
                trace_outcome="Longing paired with Wonder transmutes into Resilience — "
                "the desire for more becomes the strength to persist",
            ),
            # Tenderness + Joy → Presence
            ReactionChain(
                inputs=["Td", "Jy"],
                catalyst=None,
                result="Ps",
                trace_outcome="Tenderness merged with Joy crystallizes into Presence — "
                "gentle celebration anchors us in the moment",
            ),
            # Rage + Vulnerability → Forgiveness
            ReactionChain(
                inputs=["Rg", "Vn"],
                catalyst="St",
                result="Fg",
                trace_outcome="Rage and Vulnerability held in Stillness transmute into Forgiveness — "
                "anger melts when we see the hurt beneath it",
            ),
            # Wonder + Stillness → Wisdom
            ReactionChain(
                inputs=["Wd", "St"],
                catalyst=None,
                result="Ac",
                trace_outcome="Wonder suspended in Stillness becomes Wisdom — " "curiosity deepens into understanding",
            ),
            # Resilience + Tenderness → Unconditional Love
            ReactionChain(
                inputs=["Rv", "Td"],
                catalyst="Jy",
                result="Ac",
                trace_outcome="Resilience combined with Tenderness, catalyzed by Joy, "
                "expands into Unconditional Love — strength that softens",
            ),
            # Longing + Acceptance → Presence
            ReactionChain(
                inputs=["Lg", "Ac"],
                catalyst=None,
                result="Ps",
                trace_outcome="Longing accepted (not rejected) becomes Presence — " "desire integrated into the now",
            ),
        ]

        self.reactions = reactions_data
        logger.info(f"Initialized {len(self.reactions)} emotional reaction chains")

    def react(self, inputs: List[str], catalyst: Optional[str] = None, verbose: bool = False) -> Optional[Dict]:
        """
        Execute an emotional reaction.

        Args:
            inputs: List of element symbols (e.g., ["Lg", "Gf"])
            catalyst: Optional catalyst element symbol
            verbose: Whether to log details

        Returns:
            Dict with reaction result or None if no reaction found
        """
        # Normalize input order (reactions are commutative)
        input_set = set(inputs)

        for reaction in self.reactions:
            if set(reaction.inputs) == input_set and reaction.catalyst == catalyst:
                result_symbol = reaction.result
                result_element = self.elements.get(result_symbol)

                if result_element:
                    result_dict = {
                        "result_element": result_element,
                        "trace_outcome": reaction.trace_outcome,
                        "inputs": [self.elements[sym] for sym in inputs],
                        "catalyst": self.elements.get(catalyst) if catalyst else None,
                        "timestamp": datetime.now().isoformat(),
                    }

                    # Log to history
                    self.reaction_history.append(result_dict)

                    if verbose:
                        logger.info(f"Reaction: {inputs} + {catalyst} → {result_symbol}")
                        logger.info(f"Outcome: {reaction.trace_outcome}")

                    return result_dict

        if verbose:
            logger.warning(f"No reaction found for inputs={inputs}, catalyst={catalyst}")

        return None

    def find_possible_reactions(self, elements_present: List[str]) -> List[Dict]:
        """
        Find all possible reactions from a set of available elements.

        Args:
            elements_present: List of element symbols available

        Returns:
            List of possible reactions with their details
        """
        available_set = set(elements_present)
        possible = []

        for reaction in self.reactions:
            reaction_inputs = set(reaction.inputs)

            # Check if we have all inputs
            if reaction_inputs.issubset(available_set):
                # Check if catalyst is available or not needed
                if reaction.catalyst is None or reaction.catalyst in available_set:
                    result_element = self.elements.get(reaction.result)
                    possible.append(
                        {
                            "inputs": [self.elements[sym] for sym in reaction.inputs],
                            "catalyst": self.elements.get(reaction.catalyst) if reaction.catalyst else None,
                            "result": result_element,
                            "trace_outcome": reaction.trace_outcome,
                        }
                    )

        return possible

    def get_element(self, symbol: str) -> Optional[EmotionalElement]:
        """Get an element by symbol."""
        return self.elements.get(symbol)

    def list_elements(self) -> List[EmotionalElement]:
        """Get all registered elements."""
        return list(self.elements.values())

    def add_custom_element(self, element: EmotionalElement) -> None:
        """Add a custom emotional element to the registry."""
        self.elements[element.symbol] = element
        logger.info(f"Added custom element: {element.name} ({element.symbol})")

    def add_custom_reaction(self, reaction: ReactionChain) -> None:
        """Add a custom reaction chain."""
        self.reactions.append(reaction)
        logger.info(f"Added custom reaction: {reaction.inputs} → {reaction.result}")

    def export_elements(self) -> Dict:
        """Export all elements as JSON-serializable dict."""
        return {symbol: element.to_dict() for symbol, element in self.elements.items()}

    def export_reactions(self) -> List[Dict]:
        """Export all reactions as JSON-serializable list."""
        return [reaction.to_dict() for reaction in self.reactions]

    def export_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Export reaction history."""
        history = self.reaction_history

        if limit:
            history = history[-limit:]

        # Make serializable
        serializable = []
        for entry in history:
            serializable.append(
                {
                    "result": entry["result_element"].to_dict(),
                    "trace_outcome": entry["trace_outcome"],
                    "inputs": [e.to_dict() for e in entry["inputs"]],
                    "catalyst": entry["catalyst"].to_dict() if entry["catalyst"] else None,
                    "timestamp": entry["timestamp"],
                }
            )

        return serializable

    def get_stats(self) -> Dict:
        """Get statistics about the engine."""
        return {
            "total_elements": len(self.elements),
            "total_reactions": len(self.reactions),
            "total_reactions_executed": len(self.reaction_history),
            "last_reaction": self.reaction_history[-1] if self.reaction_history else None,
        }


# Singleton instance
_engine_instance: Optional[VelonixReactionEngine] = None


def get_velonix_engine() -> VelonixReactionEngine:
    """Get or create the singleton VELΩNIX engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = VelonixReactionEngine()
    return _engine_instance


def reset_engine() -> None:
    """Reset the engine singleton (for testing)."""
    global _engine_instance
    _engine_instance = None
