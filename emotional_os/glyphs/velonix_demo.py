#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VELΩNIX Integration and Demo

Shows how to integrate the VELΩNIX Reaction Engine into
applications, Streamlit UI, and ritual systems.
"""

import logging
from typing import Dict, List, Optional

from .velonix_reaction_engine import (
    VelonixReactionEngine,
    get_velonix_engine,
)
from .velonix_visualizer import (
    VelonixVisualizer,
    RitualPromptSystem,
    EmotionalArchive,
)

logger = logging.getLogger(__name__)


class VelonixIntegration:
    """Integration layer for VELΩNIX engine with applications."""
    
    def __init__(self):
        """Initialize the integration layer."""
        self.engine = get_velonix_engine()
        self.visualizer = VelonixVisualizer(self.engine)
        self.archive = EmotionalArchive("velonix_legacy")
    
    def process_emotional_inputs(
        self,
        element_symbols: List[str],
        catalyst_symbol: Optional[str] = None,
        user_notes: str = "",
        verbose: bool = False
    ) -> Optional[Dict]:
        """
        Process emotional inputs and generate complete reaction output.
        
        Args:
            element_symbols: Symbols of emotional elements (e.g., ["Lg", "Gf"])
            catalyst_symbol: Optional catalyst element symbol
            user_notes: User's reflection on the reaction
            verbose: Enable detailed logging
        
        Returns:
            Complete reaction package with visualization and ritual
        """
        # Execute the reaction
        reaction = self.engine.react(element_symbols, catalyst_symbol, verbose=verbose)
        
        if not reaction:
            if verbose:
                logger.warning(f"No reaction found for {element_symbols} + {catalyst_symbol}")
            return None
        
        # Extract elements
        result_element = reaction['result_element']
        input_elements = reaction['inputs']
        catalyst_element = reaction['catalyst']
        trace_outcome = reaction['trace_outcome']
        
        # Generate visualizations
        svg_reaction = self.visualizer.generate_reaction_visualization(
            inputs=input_elements,
            result=result_element,
            catalyst=catalyst_element
        )
        
        # Generate narrative
        narrative = self.visualizer.generate_reaction_narrative(
            inputs=input_elements,
            result=result_element,
            catalyst=catalyst_element,
            trace_outcome=trace_outcome
        )
        
        # Generate ritual prompt
        ritual_prompt = RitualPromptSystem.generate_ritual_prompt(
            result_element=result_element,
            trace_outcome=trace_outcome
        )
        
        # Archive the reaction
        self.archive.log_reaction(
            reaction_result=reaction,
            ritual_prompt=ritual_prompt,
            user_notes=user_notes
        )
        
        # Compile complete output
        complete_output = {
            'success': True,
            'reaction': reaction,
            'svg_visualization': svg_reaction,
            'narrative': narrative,
            'ritual_prompt': ritual_prompt,
            'element_symbols': element_symbols,
            'catalyst_symbol': catalyst_symbol,
            'result_symbol': result_element.symbol,
        }
        
        if verbose:
            logger.info("Emotional reaction processed successfully")
        
        return complete_output
    
    def explore_available_reactions(
        self,
        current_elements: List[str]
    ) -> List[Dict]:
        """
        Show what reactions are possible from current emotional state.
        
        Args:
            current_elements: Symbols of elements currently present
        
        Returns:
            List of possible reactions
        """
        return self.engine.find_possible_reactions(current_elements)
    
    def get_element_info(self, symbol: str) -> Optional[Dict]:
        """Get detailed information about an element."""
        element = self.engine.get_element(symbol)
        if element:
            return {
                'element': element.to_dict(),
                'svg': self.visualizer.generate_svg_element(element),
                'animation': self.visualizer.generate_motion_animation(element),
            }
        return None
    
    def get_archive_summary(self) -> Dict:
        """Get a summary of the emotional archive."""
        entries = self.archive.get_entries()
        
        return {
            'total_reactions': len(entries),
            'archive_name': self.archive.archive_name,
            'recent_entries': entries[-5:] if entries else [],
            'narrative': self.archive.export_as_narrative(),
        }


def demo_basic_reaction():
    """Demo: Execute a basic reaction."""
    print("\n" + "=" * 70)
    print("VELΩNIX REACTION ENGINE DEMO — Basic Reaction")
    print("=" * 70 + "\n")
    
    engine = get_velonix_engine()
    
    # Reaction: Longing + Grief → Tenderness
    print("Scenario: Longing + Grief → Tenderness\n")
    
    reaction = engine.react(["Lg", "Gf"], verbose=True)
    
    if reaction:
        print(f"\n✓ Result Element: {reaction['result_element'].name}")
        print(f"  Symbol: {reaction['result_element'].symbol}")
        print(f"  Tone: {reaction['result_element'].tone}")
        print(f"\nTrace Outcome:\n{reaction['trace_outcome']}")
    else:
        print("✗ No reaction found")


def demo_with_catalyst():
    """Demo: Reaction with catalyst."""
    print("\n" + "=" * 70)
    print("VELΩNIX REACTION ENGINE DEMO — Reaction with Catalyst")
    print("=" * 70 + "\n")
    
    engine = get_velonix_engine()
    
    # Reaction: Rage + Forgiveness (catalyzed by Resilience) → Presence
    print("Scenario: Rage + Forgiveness (catalyzed by Resilience) → Presence\n")
    
    reaction = engine.react(["Rg", "Fg"], catalyst="Rv", verbose=True)
    
    if reaction:
        print(f"\n✓ Result Element: {reaction['result_element'].name}")
        print(f"  Symbol: {reaction['result_element'].symbol}")
        print(f"\nTrace Outcome:\n{reaction['trace_outcome']}")
    else:
        print("✗ No reaction found")


def demo_full_integration():
    """Demo: Full integration with visualization and ritual."""
    print("\n" + "=" * 70)
    print("VELΩNIX INTEGRATION DEMO — Complete Flow")
    print("=" * 70 + "\n")
    
    integration = VelonixIntegration()
    
    # Process emotional inputs
    result = integration.process_emotional_inputs(
        element_symbols=["Lg", "Gf"],
        user_notes="I'm feeling the weight of missing someone, but it's becoming tender.",
        verbose=True
    )
    
    if result:
        print("\n" + result['narrative'])
        
        print("\n📿 RITUAL PROMPT FOR INTEGRATION:")
        print(f"   Element: {result['ritual_prompt']['element_name']}")
        print(f"   Tone: {result['ritual_prompt']['tone']}")
        print(f"\n   {result['ritual_prompt']['prompt']}")
        
        print("\n✓ Archive has recorded this transformation.")
    else:
        print("✗ Reaction processing failed")


def demo_explore_reactions():
    """Demo: Explore available reactions from current emotional state."""
    print("\n" + "=" * 70)
    print("VELΩNIX DEMO — Explore Possible Reactions")
    print("=" * 70 + "\n")
    
    engine = get_velonix_engine()
    
    current_elements = ["Lg", "Gf", "St", "Rv"]
    print(f"Current emotional elements: {current_elements}\n")
    
    possible = engine.find_possible_reactions(current_elements)
    
    if possible:
        print(f"Found {len(possible)} possible reactions:\n")
        for i, reaction in enumerate(possible, 1):
            inputs = " + ".join([e.name for e in reaction['inputs']])
            catalyst = f" (cat: {reaction['catalyst'].name})" if reaction['catalyst'] else ""
            result = reaction['result'].name if reaction['result'] else "?"
            print(f"{i}. {inputs}{catalyst} → {result}")
            print(f"   {reaction['trace_outcome']}\n")
    else:
        print("No possible reactions found with these elements.")


def demo_list_elements():
    """Demo: List all emotional elements."""
    print("\n" + "=" * 70)
    print("VELΩNIX DEMO — All Emotional Elements")
    print("=" * 70 + "\n")
    
    engine = get_velonix_engine()
    
    elements = engine.list_elements()
    
    print(f"Total Elements: {len(elements)}\n")
    
    for element in sorted(elements, key=lambda e: e.symbol):
        print(f"  {element.symbol:3} | {element.name:15} | {element.tone:20} | {element.valence}")


def demo_visualization():
    """Demo: Generate visualization."""
    print("\n" + "=" * 70)
    print("VELΩNIX DEMO — Visualization Generation")
    print("=" * 70 + "\n")
    
    engine = get_velonix_engine()
    visualizer = VelonixVisualizer(engine)
    
    # Get elements
    lg = engine.get_element("Lg")
    gf = engine.get_element("Gf")
    td = engine.get_element("Td")
    
    if lg and gf and td:
        # Generate SVG
        svg = visualizer.generate_reaction_visualization(
            inputs=[lg, gf],
            result=td
        )
        
        print("Generated SVG visualization (abbreviated):")
        print(svg[:200] + "...\n")
        
        # Generate narrative
        narrative = visualizer.generate_reaction_narrative(
            inputs=[lg, gf],
            result=td,
            trace_outcome="Longing held in grief metabolizes into Tenderness"
        )
        
        print("Generated Narrative:")
        print(narrative)


def run_all_demos():
    """Run all available demos."""
    demos = [
        ("Basic Reaction", demo_basic_reaction),
        ("Reaction with Catalyst", demo_with_catalyst),
        ("List Elements", demo_list_elements),
        ("Explore Reactions", demo_explore_reactions),
        ("Visualization", demo_visualization),
        ("Full Integration", demo_full_integration),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n✗ Demo '{name}' encountered an error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "─" * 70)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(name)s - %(levelname)s - %(message)s'
    )
    
    run_all_demos()
