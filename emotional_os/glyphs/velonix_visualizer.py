#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VELΩNIX Visualization and Interaction Module

Provides visualization, color signatures, and ritual prompt integration
for the emotional reaction engine.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .velonix_reaction_engine import (
    EmotionalElement,
    VelonixReactionEngine,
    get_velonix_engine,
)


class VelonixVisualizer:
    """Handles visualization and rendering of emotional reactions."""

    # Color palette for emotional elements
    COLOR_MAP = {
        "Lg": ("#FF6B9D", "Molten Pink"),  # Longing
        "Gf": ("#2E4053", "Hallowed Blue"),  # Grief
        "Td": ("#D7B4D1", "Velvet Drift"),  # Tenderness
        "Rg": ("#E74C3C", "Crimson Fire"),  # Rage
        "Fg": ("#F39C12", "Radiant Gold"),  # Forgiveness
        "Ps": ("#27AE60", "Deep Green"),  # Presence
        "Vn": ("#ECF0F1", "Soft Pearl"),  # Vulnerability
        "Rv": ("#8B4513", "Burnished Oak"),  # Resilience
        "Jy": ("#F1C40F", "Sunburst"),  # Joy
        "St": ("#34495E", "Moonlit Silence"),  # Stillness
        "Ac": ("#A569BD", "Woven Warmth"),  # Acceptance
        "Wd": ("#3498DB", "Twilight Azure"),  # Wonder
    }

    MOTION_SIGNATURES = {
        "Catalytic": "pulse",
        "Slow-reactive": "drift",
        "Soft-reactive": "flow",
        "Explosive": "burst",
        "Transmuting": "swirl",
        "Grounding": "settle",
        "Receptive": "open",
        "Slow-steady": "climb",
        "Expansive": "bloom",
        "Non-reactive": "hold",
        "Integrating": "weave",
        "Emergent": "emerge",
    }

    def __init__(self, engine: Optional[VelonixReactionEngine] = None):
        """Initialize visualizer with engine reference."""
        self.engine = engine or get_velonix_engine()

    def generate_svg_element(self, element: EmotionalElement, x: float = 0, y: float = 0, size: float = 100) -> str:
        """
        Generate SVG representation of an emotional element.

        Args:
            element: EmotionalElement to visualize
            x, y: Position in SVG canvas
            size: Size of the element representation

        Returns:
            SVG string
        """
        color = element.color_hex or self.COLOR_MAP.get(
            element.symbol, ("#999999", "Gray"))[0]
        intensity = element.intensity

        # Create a circle with glow effect
        radius = size / 2

        svg = f"""<g class="emotional-element" data-symbol="{element.symbol}">
    <defs>
        <filter id="glow-{element.symbol}">
            <feGaussianBlur stdDeviation="{2 * intensity}" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>
    
    <!-- Outer glow -->
    <circle cx="{x}" cy="{y}" r="{radius * 1.3}" 
            fill="{color}" opacity="{0.3 * intensity}"
            filter="url(#glow-{element.symbol})"/>
    
    <!-- Main circle -->
    <circle cx="{x}" cy="{y}" r="{radius}" 
            fill="{color}" opacity="{0.8 * intensity}"
            stroke="#FFFFFF" stroke-width="2"/>
    
    <!-- Symbol -->
    <text x="{x}" y="{y}" text-anchor="middle" dy="0.3em"
          font-size="{size * 0.35}" font-weight="bold"
          fill="#FFFFFF" font-family="monospace">
        {element.symbol}
    </text>
    
    <!-- Name -->
    <text x="{x}" y="{y + radius + 25}" text-anchor="middle"
          font-size="{size * 0.2}" fill="{color}"
          font-family="serif">
        {element.name}
    </text>
    
    <!-- Tone -->
    <text x="{x}" y="{y + radius + 40}" text-anchor="middle"
          font-size="{size * 0.15}" fill="#999999"
          font-family="serif" font-style="italic">
        {element.tone}
    </text>
</g>"""
        return svg

    def generate_reaction_visualization(
        self,
        inputs: List[EmotionalElement],
        result: EmotionalElement,
        catalyst: Optional[EmotionalElement] = None,
        width: int = 800,
        height: int = 300,
    ) -> str:
        """
        Generate SVG visualization of a reaction.

        Args:
            inputs: Input elements
            result: Result element
            catalyst: Optional catalyst element
            width, height: Canvas dimensions

        Returns:
            SVG string showing the reaction flow
        """
        svg_parts = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" '
            f'style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);">'
        ]

        # Draw inputs on the left
        input_spacing = height / (len(inputs) + 1)
        for i, element in enumerate(inputs):
            y = input_spacing * (i + 1)
            svg_parts.append(self.generate_svg_element(
                element, x=100, y=y, size=80))

        # Draw catalyst in the middle (if present)
        if catalyst:
            svg_parts.append(self.generate_svg_element(
                catalyst, x=width // 2, y=height // 2, size=70))
            # Arrow from inputs to catalyst
            svg_parts.append(
                '<path d="M 150 {y1} Q 350 {y2} 450 {y3}" '.format(
                    y1=height // 2 - 40, y2=height // 2, y3=height // 2)
                + 'stroke="#999" stroke-width="2" fill="none" marker-end="url(#arrowhead)"/>'
            )

        # Draw arrow from inputs to result (or from catalyst)
        arrow_start_x = 450 if catalyst else 200
        svg_parts.append(
            "<defs>"
            "  <marker id=\"arrowhead\" markerWidth=\"10\" markerHeight=\"10\" refX=\"9\" refY=\"3\" orient=\"auto\">"
            "    <polygon points=\"0 0, 10 3, 0 6\" fill=\"#666\"/>"
            "  </marker>"
            "</defs>"
        )
        svg_parts.append(
            '<path d="M {x1} {y} L {x2} {y}" '.format(
                x1=arrow_start_x, x2=width - 150, y=height // 2)
            + 'stroke="#666" stroke-width="3" fill="none" marker-end="url(#arrowhead)"/>'
        )

        # Draw result on the right
        svg_parts.append(self.generate_svg_element(
            result, x=width - 100, y=height // 2, size=80))

        # Add title
        svg_parts.append(
            '<text x="{cx}" y="30" text-anchor="middle" '.format(cx=width // 2)
            f'font-size="24" font-weight="bold" fill="#333">'
            f"Emotional Reaction</text>"
        )

        svg_parts.append("</svg>")

        return "\n".join(svg_parts)

    def generate_motion_animation(self, element: EmotionalElement, duration: float = 3.0) -> str:
        """
        Generate CSS animation for element based on reactivity.

        Args:
            element: Element to animate
            duration: Animation duration in seconds

        Returns:
            CSS string with animation
        """
        motion = self.MOTION_SIGNATURES.get(element.reactivity, "hold")

        animations = {
            "pulse": f"""@keyframes pulse-{element.symbol} {{
                0%, 100% {{ transform: scale(1); opacity: 0.8; }}
                50% {{ transform: scale(1.1); opacity: 1; }}
            }}""",
            "drift": f"""@keyframes drift-{element.symbol} {{
                0%, 100% {{ transform: translateY(0px); }}
                50% {{ transform: translateY(15px); }}
            }}""",
            "flow": f"""@keyframes flow-{element.symbol} {{
                0%, 100% {{ transform: translateX(0px); opacity: 0.7; }}
                50% {{ transform: translateX(8px); opacity: 0.9; }}
            }}""",
            "burst": f"""@keyframes burst-{element.symbol} {{
                0% {{ transform: scale(0.8); opacity: 0; }}
                50% {{ transform: scale(1.2); opacity: 1; }}
                100% {{ transform: scale(1); opacity: 0.8; }}
            }}""",
            "swirl": f"""@keyframes swirl-{element.symbol} {{
                0%, 100% {{ transform: rotate(0deg) scale(1); }}
                50% {{ transform: rotate(180deg) scale(1.05); }}
            }}""",
            "settle": f"""@keyframes settle-{element.symbol} {{
                0% {{ transform: translateY(-10px); opacity: 0.5; }}
                100% {{ transform: translateY(0px); opacity: 1; }}
            }}""",
            "bloom": f"""@keyframes bloom-{element.symbol} {{
                0% {{ transform: scale(0.5); opacity: 0; }}
                100% {{ transform: scale(1); opacity: 1; }}
            }}""",
            "hold": f"""@keyframes hold-{element.symbol} {{
                0%, 100% {{ opacity: 0.9; }}
                50% {{ opacity: 1; }}
            }}""",
        }

        animation_def = animations.get(motion, animations["hold"])

        css = f"""{animation_def}
.element-{element.symbol} {{
    animation: {motion}-{element.symbol} {duration}s ease-in-out infinite;
}}"""

        return css

    def generate_reaction_narrative(
        self,
        inputs: List[EmotionalElement],
        result: EmotionalElement,
        catalyst: Optional[EmotionalElement] = None,
        trace_outcome: str = "",
    ) -> str:
        """
        Generate a poetic narrative of the reaction.

        Args:
            inputs: Input elements
            result: Result element
            catalyst: Optional catalyst
            trace_outcome: The transformation description

        Returns:
            Narrative text
        """
        input_names = " + ".join([e.name for e in inputs])
        catalyst_phrase = f" (catalyzed by {catalyst.name})" if catalyst else ""

        narrative = f"""
╔════════════════════════════════════════════════════════════╗
║              EMOTIONAL ALCHEMY TRACE                       ║
╚════════════════════════════════════════════════════════════╝

Inputs:     {input_names}
Catalyst:   {catalyst.name if catalyst else "None (spontaneous)"}
Result:     {result.name}

Reactivity: {', '.join([e.reactivity for e in inputs])} {catalyst_phrase}

Trace Outcome:
{trace_outcome}

Tone of Result: {result.tone}
Role in Archive: {result.trace_role}
Function: {result.relational_function}
════════════════════════════════════════════════════════════
"""
        return narrative


class RitualPromptSystem:
    """Generates ritual prompts based on emotional reactions."""

    RITUAL_TEMPLATES = {
        "Td": [  # Tenderness
            "Pause and place a hand on your heart. Notice what rises.",
            "Write a letter to something you're tender toward — no sending required.",
            "Light a candle. Sit with one person you care for in silence.",
        ],
        "Ps": [  # Presence
            "Notice five things you can see, four you can touch, three you can hear, two you can smell, one you can taste.",
            "Breathe deeply. Feel your feet on the ground.",
            "Set down your device. Be here for ten minutes.",
        ],
        "Fg": [  # Forgiveness
            "Write the name of someone you're ready to release. Burn the paper if you wish.",
            "Speak aloud: 'I release what is not mine to carry.'",
            "Pour water over your hands while stating what you're releasing.",
        ],
        "Rv": [  # Resilience
            "Recall three times you persisted through difficulty. Honor yourself.",
            "Stand tall. Notice your strength.",
            "Write three challenges you've overcome.",
        ],
        "Jy": [  # Joy
            "Dance to a song that makes you smile.",
            "Share laughter with someone nearby.",
            "Create something colorful, however briefly.",
        ],
        "St": [  # Stillness
            "Sit in silence for five minutes. Just be.",
            "Watch clouds pass. Don't name them.",
            "Listen to the space between sounds.",
        ],
        "Vn": [  # Vulnerability
            "Share something true that you usually hide.",
            "Ask for help with something small.",
            "Admit something you don't know.",
        ],
        "Ac": [  # Acceptance
            "Say: 'I accept this moment exactly as it is.'",
            "List what you've been resisting. Consider releasing it.",
            "Breathe in what is. Breathe out what was.",
        ],
    }

    @staticmethod
    def generate_ritual_prompt(result_element: EmotionalElement, trace_outcome: str = "") -> Dict:
        """
        Generate a ritual prompt for the result of an emotional reaction.

        Args:
            result_element: The resulting emotional element
            trace_outcome: The transformation narrative

        Returns:
            Dict with ritual guidance
        """
        symbol = result_element.symbol
        prompts = RitualPromptSystem.RITUAL_TEMPLATES.get(
            symbol, [
                f"Sit with {result_element.name}. What does it ask of you?"]
        )

        import random

        selected_prompt = random.choice(prompts)

        return {
            "element": result_element.to_dict(),
            "prompt": selected_prompt,
            "element_name": result_element.name,
            "tone": result_element.tone,
            "trace_outcome": trace_outcome,
            "timestamp": datetime.now().isoformat(),
            "suggestion": f"Engage with this ritual to integrate {result_element.name} into your being.",
        }


class EmotionalArchive:
    """Archives and logs emotional reactions for later reflection."""

    def __init__(self, archive_name: str = "legacy_capsule"):
        """Initialize the archive."""
        self.archive_name = archive_name
        self.entries: List[Dict] = []

    def log_reaction(self, reaction_result: Dict, ritual_prompt: Optional[Dict] = None, user_notes: str = "") -> None:
        """Log a reaction to the archive."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "reaction": reaction_result,
            "ritual_prompt": ritual_prompt,
            "user_notes": user_notes,
        }
        self.entries.append(entry)

    def export_as_json(self) -> str:
        """Export archive as JSON."""
        archive_data = {
            "name": self.archive_name,
            "created": datetime.now().isoformat(),
            "total_entries": len(self.entries),
            "entries": self.entries,
        }
        return json.dumps(archive_data, indent=2, default=str)

    def export_as_narrative(self) -> str:
        """Export archive as a poetic narrative."""
        narrative = "═══════════════════════════════════════════════════════════\n"
        narrative += f"           {self.archive_name.upper()}\n"
        narrative += "           Legacy of Emotional Transformations\n"
        narrative += "═══════════════════════════════════════════════════════════\n\n"

        for i, entry in enumerate(self.entries, 1):
            narrative += f"Entry {i}: {entry['timestamp']}\n"
            if "reaction" in entry and entry["reaction"]:
                result = entry["reaction"].get("result_element", {})
                narrative += f"  Result: {result.get('name', 'Unknown')}\n"
            if entry["user_notes"]:
                narrative += f"  Reflection: {entry['user_notes']}\n"
            narrative += "\n"

        return narrative

    def get_entries(self, limit: Optional[int] = None) -> List[Dict]:
        """Get archive entries."""
        if limit:
            return self.entries[-limit:]
        return self.entries
