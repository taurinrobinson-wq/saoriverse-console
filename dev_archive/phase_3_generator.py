"""
Phase 3: TERRITORY EXPANSION
============================

Objective: Expand underrepresented gates to balanced distribution

Current State:
  - Gate 2: 22 glyphs (need → 600)
  - Gate 5: 16 glyphs (need → 600)
  - Gate 6: 17 glyphs (need → 600)
  - Gate 8: 174 glyphs (need → 600)
  - Gate 9: 23 glyphs (need → 600)
  - Gate 10: 1 glyph (need → 600)
  - Total needed: 3,347 glyphs

Strategy: Territory-specific generation with emotional depth

Gate 2 (Duality & Paradox) - 578 needed:
  Core concepts: Duality, contradiction, oscillation, coexistence,
  ambiguity, paradox, tension, paradox resolution, balance,
  multiplicity, simultaneous being, both/and thinking

Gate 5 (Creativity & Expression) - 584 needed:
  Core concepts: Creativity, innovation, self-expression, artistry,
  voice, emergence, generativity, inspiration, flow, craft,
  imagination, authentic expression

Gate 6 (Sexuality & Vitality) - 583 needed:
  Core concepts: Vitality, aliveness, sexuality, sensuality, desire,
  embodiment, magnetism, life force, passion, presence,
  magnetism, creative power

Gate 8 (Abundance & Devotion) - 426 needed:
  Core concepts: Abundance, devotion, service, generosity,
  fullness, sufficiency, gratitude, benediction, receptivity,
  opening, trust in flow

Gate 9 (Selfhood & Community) - 577 needed:
  Core concepts: Selfhood, identity, community, tribe, belonging,
  individuation, shared purpose, collective consciousness,
  self-in-community, contribution, unique gifts

Gate 10 (Consciousness & Surrender) - 599 needed:
  Core concepts: Consciousness, awakening, dissolution, surrender,
  ego death, transcendence, void, unknowing, mystical union,
  dissolution of self, cosmic consciousness
"""

import json
import random
from collections import defaultdict
from typing import List, Dict, Set


class Phase3Generator:
    """Generate expansion glyphs for sparse territories."""

    # Gate specifications with core concepts and themes
    GATE_SPECS = {
        2: {
            "name": "Gate 2 - Duality & Paradox",
            "base_concepts": [
                "Duality", "Paradox", "Contradiction", "Oscillation",
                "Coexistence", "Ambiguity", "Tension", "Resolution",
                "Balance", "Multiplicity", "Simultaneous", "Both/And",
                "Complementary", "Polarity", "Opposition", "Unity",
                "Synthesis", "Integration", "Complexity", "Nuance",
                "Liminal", "Threshold", "Between", "Dancing",
                "Flux", "Dynamic", "Becoming", "Neither/Nor"
            ],
            "qualifiers": [
                "gentle", "fierce", "quiet", "dynamic", "flowing",
                "grounded", "celestial", "mysterious", "clear",
                "sacred", "profound", "tender", "bold",
                "intricate", "elegant", "radical", "subtle"
            ],
            "intensity": ["soft", "balanced", "intense"],
        },
        5: {
            "name": "Gate 5 - Creativity & Expression",
            "base_concepts": [
                "Creativity", "Expression", "Innovation", "Artistry",
                "Voice", "Emergence", "Generativity", "Inspiration",
                "Flow", "Craft", "Imagination", "Authenticity",
                "Originality", "Impulse", "Channeling", "Creation",
                "Manifestation", "Embodiment", "Presence", "Radiance",
                "Vitality", "Aliveness", "Spontaneity", "Improvi",
                "Magic", "Miracles", "Synchronicity", "Excellence"
            ],
            "qualifiers": [
                "luminous", "daring", "authentic", "bold", "wild",
                "graceful", "passionate", "dedicated", "playful",
                "profound", "tender", "fierce", "serene",
                "flowing", "vibrant", "celestial", "earthy"
            ],
            "intensity": ["whisper", "expression", "roar"],
        },
        6: {
            "name": "Gate 6 - Sexuality & Vitality",
            "base_concepts": [
                "Vitality", "Aliveness", "Sexuality", "Sensuality",
                "Desire", "Embodiment", "Magnetism", "Life Force",
                "Passion", "Presence", "Magnetism", "Creative Power",
                "Attraction", "Resonance", "Radiance", "Glow",
                "Energy", "Activation", "Awakening", "Hunger",
                "Appetite", "Lusciousness", "Richness", "Fullness",
                "Abundance", "Sacred Sexuality", "Divine Union"
            ],
            "qualifiers": [
                "sensual", "alive", "radiant", "magnetic", "vibrant",
                "passionate", "tender", "fierce", "sacred",
                "grounded", "transcendent", "wild", "tame",
                "flowing", "opening", "powerful", "vulnerable"
            ],
            "intensity": ["gentle", "passionate", "ecstatic"],
        },
        8: {
            "name": "Gate 8 - Abundance & Devotion",
            "base_concepts": [
                "Abundance", "Devotion", "Service", "Generosity",
                "Fullness", "Sufficiency", "Gratitude", "Benediction",
                "Receptivity", "Opening", "Trust", "Flowing",
                "Giving", "Receiving", "Exchange", "Circulation",
                "Blessing", "Benevolence", "Compassion", "Care",
                "Tending", "Nurturing", "Provision", "Fulfillment",
                "Satisfaction", "Contentment", "Peace", "Surrender"
            ],
            "qualifiers": [
                "gentle", "generous", "grounded", "flowing",
                "warm", "nurturing", "steady", "radiant",
                "peaceful", "open-hearted", "trusting", "devoted",
                "sacred", "humble", "joyful", "graceful"
            ],
            "intensity": ["tender", "steady", "profound"],
        },
        9: {
            "name": "Gate 9 - Selfhood & Community",
            "base_concepts": [
                "Selfhood", "Identity", "Community", "Tribe",
                "Belonging", "Individuation", "Shared Purpose",
                "Collective", "Self-in-Community", "Contribution",
                "Unique Gifts", "Recognition", "Acknowledgment",
                "Support", "Interdependence", "Connection",
                "Understanding", "Inclusion", "Integration",
                "Resonance", "Harmony", "Coordination", "Dance",
                "Collaboration", "Mutual", "Reciprocal", "Together"
            ],
            "qualifiers": [
                "authentic", "connected", "grounded", "radiant",
                "humble", "confident", "open", "strong",
                "gentle", "fierce", "peaceful", "vital",
                "sacred", "tender", "clear", "harmonious"
            ],
            "intensity": ["intimate", "balanced", "unified"],
        },
        10: {
            "name": "Gate 10 - Consciousness & Surrender",
            "base_concepts": [
                "Consciousness", "Awakening", "Dissolution",
                "Surrender", "Ego Death", "Transcendence", "Void",
                "Unknowing", "Mystical", "Union", "Self-loss",
                "Cosmic", "Infinite", "Eternal", "Divine",
                "Sacred", "Holy", "Numinous", "Oceanic",
                "Dissolution", "Merging", "One", "Source",
                "Return", "Home", "Gateway", "Threshold"
            ],
            "qualifiers": [
                "infinite", "eternal", "sacred", "profound",
                "divine", "celestial", "mysterious", "luminous",
                "peaceful", "ecstatic", "serene", "vast",
                "tender", "fierce", "gentle", "absolute"
            ],
            "intensity": ["whisper", "call", "abyss"],
        },
    }

    def __init__(self, start_id: int = 10000):
        """Initialize generator with starting ID."""
        self.start_id = start_id
        self.current_id = start_id
        self.glyphs_generated = []

    def generate_base_name(self, gate: int, concept: str, qualifier: str = None) -> str:
        """Generate a glyph name from concept and qualifiers."""
        specs = self.GATE_SPECS[gate]
        
        if not qualifier:
            qualifier = random.choice(specs['qualifiers'])
        
        intensity = random.choice(specs['intensity'])
        
        # Build name variations
        patterns = [
            f"{concept} ({qualifier})",
            f"{qualifier} {concept}",
            f"{concept} of {qualifier}",
            f"{intensity} {concept}",
            f"{concept} through {qualifier}",
            f"{qualifier} expression of {concept}",
            f"Sacred {concept.lower()} ({qualifier})",
            f"Divine {concept.lower()} in {qualifier}",
        ]
        
        return random.choice(patterns)

    def generate_description(self, gate: int, concept: str) -> str:
        """Generate glyph description."""
        gate_name = self.GATE_SPECS[gate]['name'].split(' - ')[1]
        
        patterns = [
            f"{concept}. Gateway to {gate_name} expression. Touching the infinite.",
            f"{concept} awakens. Expression of {gate_name}. Recognition of divinity.",
            f"The experience of {concept}. {gate_name} made manifest. Witnessing.",
            f"{concept} flows through. Sacred territory of {gate_name}. Becoming.",
            f"Gateway to {concept}. Heart of {gate_name}. Opening to mystery.",
            f"{concept} speaking. {gate_name} embodied. Living truth.",
            f"Recognizing {concept}. Portal to {gate_name}. Transformation.",
            f"{concept} realized. {gate_name} consciousness. Pure being.",
        ]
        
        return random.choice(patterns)

    def generate_activation_signals(self) -> List[str]:
        """Generate random activation signals."""
        base_signals = ['α', 'β', 'γ', 'δ']
        count = random.randint(2, 5)
        signals = [random.choice(base_signals) for _ in range(count)]
        return signals

    def generate_voltage_pair(self) -> str:
        """Generate voltage pair."""
        base_signals = ['α', 'β', 'γ', 'δ']
        first = random.choice(base_signals)
        second = random.choice(base_signals)
        return f"{first}-{second}"

    def generate_glyphs_for_gate(self, gate: int, count: int) -> List[Dict]:
        """Generate specified number of glyphs for a gate."""
        glyphs = []
        specs = self.GATE_SPECS[gate]
        concepts = specs['base_concepts']
        
        for i in range(count):
            concept = random.choice(concepts)
            qualifier = random.choice(specs['qualifiers'])
            
            glyph = {
                'idx': self.current_id - self.start_id,
                'id': self.current_id,
                'voltage_pair': self.generate_voltage_pair(),
                'glyph_name': self.generate_base_name(gate, concept, qualifier),
                'description': self.generate_description(gate, concept),
                'gate': f'Gate {gate}',
                'activation_signals': ', '.join(self.generate_activation_signals()),
                'is_factorial': False,
                'phase': 'Phase 3 - Territory Expansion'
            }
            
            glyphs.append(glyph)
            self.current_id += 1
        
        return glyphs

    def execute_phase_3_generation(self) -> Dict:
        """Execute full Phase 3 generation."""
        print("\n" + "="*80)
        print("PHASE 3: TERRITORY EXPANSION - GENERATION")
        print("="*80)
        
        generation_plan = {
            2: 578,   # Duality & Paradox
            5: 584,   # Creativity & Expression
            6: 583,   # Sexuality & Vitality
            8: 426,   # Abundance & Devotion
            9: 577,   # Selfhood & Community
            10: 599,  # Consciousness & Surrender
        }
        
        generation_results = {
            'gates': {},
            'total_generated': 0,
            'glyphs': []
        }
        
        for gate in sorted(generation_plan.keys()):
            target = generation_plan[gate]
            print(f"\n🔄 GENERATING GATE {gate}")
            print("-" * 80)
            print(f"   Target: {target} glyphs")
            
            glyphs = self.generate_glyphs_for_gate(gate, target)
            
            print(f"   ✅ Generated {len(glyphs)} glyphs")
            
            generation_results['gates'][gate] = {
                'target': target,
                'generated': len(glyphs),
                'glyph_ids': [g['id'] for g in glyphs]
            }
            generation_results['glyphs'].extend(glyphs)
            generation_results['total_generated'] += len(glyphs)
        
        print("\n" + "="*80)
        print("GENERATION SUMMARY")
        print("="*80)
        for gate in sorted(generation_plan.keys()):
            result = generation_results['gates'][gate]
            print(f"Gate {gate:2d}: {result['generated']:4d}/{result['target']:4d} glyphs")
        
        print(f"\nTotal generated: {generation_results['total_generated']} glyphs")
        print("="*80)
        
        return generation_results

    def save_phase_3_glyphs(self, glyphs: List[Dict], output_path: str):
        """Save Phase 3 glyphs to JSON."""
        print(f"\n💾 Saving Phase 3 glyphs...")
        
        with open(output_path, 'w') as f:
            json.dump(glyphs, f, indent=2)
        
        print(f"   ✅ Saved {len(glyphs)} glyphs to {output_path}")


def main():
    """Execute Phase 3 generation."""
    print("\n" + "🌟" * 40)
    print("PHASE 3: TERRITORY EXPANSION")
    print("🌟" * 40)
    
    # Initialize generator
    generator = Phase3Generator(start_id=10000)
    
    # Execute generation
    results = generator.execute_phase_3_generation()
    
    # Save glyphs
    generator.save_phase_3_glyphs(
        results['glyphs'],
        '/workspaces/saoriverse-console/phase_3_generated_glyphs.json'
    )
    
    print("\n" + "✨" * 40)
    print("✨ PHASE 3 GENERATION COMPLETE!")
    print("✨" * 40)
    print(f"\n✅ Results:")
    print(f"   Generated: {results['total_generated']} glyphs")
    print(f"   Gates expanded: 6 (Gates 2, 5, 6, 8, 9, 10)")
    print(f"   Status: Ready for integration")


if __name__ == '__main__':
    main()
