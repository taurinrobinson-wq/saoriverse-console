#!/usr/bin/env python3
"""
Comprehensive Scenario Testing Suite for Emotional OS
Tests the new 7,096-glyph database across diverse conversation scenarios.

This suite validates that the expanded and balanced glyph database
provides comprehensive coverage across all emotional territories and
ritual sequences.
"""

import json
from collections import defaultdict, Counter
from typing import List, Dict, Tuple


class ScenarioTester:
    """Test the Emotional OS against realistic conversation scenarios."""

    def __init__(self, glyph_file: str = "emotional_os/glyphs/glyph_lexicon_rows.json"):
        """Initialize tester with glyph database."""
        self.glyph_file = glyph_file
        self.glyphs = self.load_glyphs()
        self.gate_map = self._build_gate_map()
        self.scenario_results = []

    def load_glyphs(self) -> List[Dict]:
        """Load glyphs from JSON."""
        print(f"📖 Loading glyphs from {self.glyph_file}...")
        with open(self.glyph_file, 'r') as f:
            data = json.load(f)
            glyphs = data['glyphs'] if isinstance(data, dict) else data
        print(f"   ✅ Loaded {len(glyphs)} glyphs")
        return glyphs

    def _build_gate_map(self) -> Dict[int, List[Dict]]:
        """Build mapping of gates to glyphs."""
        gate_map = defaultdict(list)
        for glyph in self.glyphs:
            gate_str = glyph.get('gate', '').strip()
            if gate_str:
                try:
                    gate_num = int(gate_str.split()[-1])
                    gate_map[gate_num].append(glyph)
                except (ValueError, IndexError):
                    pass
        return dict(gate_map)

    def extract_emotional_keywords(self, text: str) -> List[str]:
        """Extract emotional keywords from text."""
        keywords = []
        emotional_terms = {
            # Grief & Loss
            'grief': ['grief', 'loss', 'mourning', 'lost', 'died', 'death', 'bereaved'],
            'sadness': ['sad', 'sadness', 'depressed', 'blue', 'melancholy', 'down', 
                       'disappointed', 'dejected'],  # Added NRC variants

            'loneliness': ['alone', 'lonely', 'isolated', 'solitary', 'abandoned'],

            # Joy & Connection (NRC-enriched)
            'joy': ['joy', 'joyful', 'happy', 'blissful', 'elated', 'delighted',
                   'excited', 'cheerful', 'content', 'pleased', 'hopeful', 'optimistic',
                   'peaceful', 'calm', 'serene', 'satisfied', 'grateful'],  # Added 11 NRC words
            'love': ['love', 'beloved', 'caring', 'affection', 'warmth', 'connected'],
            'gratitude': ['grateful', 'appreciate', 'thank', 'blessed', 'thankful'],

            # Fear & Anxiety (NRC-enriched)
            'fear': ['fear', 'afraid', 'scared', 'terrified', 'anxious', 'worry',
                    'worried', 'nervous', 'panicked'],  # Added 3 NRC variants
            'uncertainty': ['uncertain', 'unsure', 'doubtful', 'unclear', 'confused'],
            'vulnerability': ['vulnerable', 'exposed', 'helpless', 'weak'],

            # Transformation & Growth
            'transformation': ['transform', 'change', 'evolve', 'growth', 'becoming'],
            'creativity': ['creative', 'create', 'express', 'artistic', 'imagine'],
            'awakening': ['awaken', 'aware', 'conscious', 'realize', 'understand'],

            # Duality & Paradox (anger variants added)
            'paradox': ['paradox', 'contradiction', 'both', 'neither', 'tension'],
            'balance': ['balance', 'equilibrium', 'harmony', 'centered', 'aligned'],
            'anger': ['anger', 'angry', 'furious', 'rage', 'mad', 'frustrated', 'irritated',
                     'annoyed', 'hate', 'hostile'],  # Added 6 NRC anger words

            # Community & Self
            'belonging': ['belong', 'community', 'tribe', 'connection', 'accepted'],
            'identity': ['identity', 'self', 'authentic', 'genuine', 'true'],

            # Surrender & Transcendence
            'surrender': ['surrender', 'let go', 'release', 'accept', 'open'],
            'transcendence': ['transcend', 'transcendent', 'beyond', 'infinite', 'eternal', 'divine', 'enlighten', 'ultimate'],
        }

        text_lower = text.lower()
        for emotion, terms in emotional_terms.items():
            for term in terms:
                if term in text_lower:
                    keywords.append(emotion)
                    break

        return list(set(keywords))

    def find_matching_glyphs(self, keywords: List[str], max_results: int = 5) -> List[Dict]:
        """Find glyphs matching emotional keywords."""
        matching = []
        
        def normalize_word(word: str) -> str:
            """Remove common suffixes for better matching."""
            word_lower = word.lower()
            suffixes = ['ence', 'ency', 'ity', 'tion', 'sion', 'ness', 'ment', 'able', 'ible', 'ous']
            for suffix in suffixes:
                if word_lower.endswith(suffix):
                    return word_lower[:-len(suffix)]
            return word_lower
        
        def words_match(keyword: str, signal_text: str) -> bool:
            """Check if keyword matches signal text with stemming."""
            keyword_norm = normalize_word(keyword)
            signal_lower = signal_text.lower()
            
            # Direct substring match
            if keyword.lower() in signal_lower:
                return True
            # Normalized match
            if keyword_norm in signal_lower:
                return True
            # Check if any word in signal matches
            for signal_word in signal_lower.split():
                if normalize_word(signal_word) == keyword_norm:
                    return True
            return False

        # Process all keywords without breaking early
        for keyword in keywords:
            for glyph in self.glyphs:
                # Check activation_signals first (newly enhanced field)
                activation_signals = glyph.get('activation_signals', '')
                if isinstance(activation_signals, str):
                    activation_signals_text = activation_signals.lower()
                else:
                    activation_signals_text = str(activation_signals).lower()
                
                # Check glyph name and description as secondary
                glyph_name = glyph.get('glyph_name', '').lower()
                description = glyph.get('description', '').lower()
                
                # Use smart matching
                if words_match(keyword, activation_signals_text) or \
                   words_match(keyword, glyph_name) or \
                   words_match(keyword, description):
                    if glyph not in matching:
                        matching.append(glyph)

        # Return limited results per keyword, but all keywords represented
        return matching[:max_results * len(keywords)]

    def analyze_gate_coverage(self, glyphs: List[Dict]) -> Dict:
        """Analyze which gates are represented in matched glyphs."""
        gates = Counter()
        gate_names = {
            1: "Initiation & Emergence",
            2: "Duality & Paradox",
            3: "Dissolution & Transformation",
            4: "Foundation & Structure",
            5: "Creativity & Expression",
            6: "Sexuality & Vitality",
            7: "Depth & Mystery",
            8: "Abundance & Devotion",
            9: "Selfhood & Community",
            10: "Consciousness & Surrender",
            11: "Synchronicity & Flow",
            12: "Transcendence & Return",
        }

        for glyph in glyphs:
            gate_str = glyph.get('gate', '').strip()
            if gate_str:
                try:
                    gate_num = int(gate_str.split()[-1])
                    gates[gate_num] += 1
                except (ValueError, IndexError):
                    pass

        return {
            'gates': dict(gates),
            'gate_names': {g: gate_names[g] for g in gates},
            'coverage_percentage': (len(gates) / 12) * 100
        }

    def test_scenario(self, scenario_name: str, text: str, expected_gates: List[int] = None) -> Dict:
        """Test a single conversation scenario."""
        print(f"\n🧪 Testing Scenario: {scenario_name}")
        print("=" * 70)
        print(f"Input: {text}")

        # Extract keywords
        keywords = self.extract_emotional_keywords(text)
        print(f"📍 Emotional Keywords Found: {keywords}")

        # Find matching glyphs
        matching_glyphs = self.find_matching_glyphs(keywords, max_results=50)
        print(f"✅ Matching Glyphs: {len(matching_glyphs)} found")

        # Analyze gate coverage
        coverage = self.analyze_gate_coverage(matching_glyphs)
        print(f"🗺️  Gate Coverage: {coverage['coverage_percentage']:.1f}% ({len(coverage['gates'])}/12 gates)")

        # Display matched glyphs
        if matching_glyphs:
            print(f"\n📜 Top Glyphs:")
            for i, g in enumerate(matching_glyphs[:5], 1):
                gate_str = g.get('gate', 'Unknown')
                print(f"   {i}. {g.get('glyph_name', 'Unknown')} ({gate_str})")

        # Evaluate success
        success = True
        if expected_gates:
            found_gates = set(coverage['gates'].keys())
            expected = set(expected_gates)
            if not found_gates.intersection(expected):
                success = False
                print(f"\n⚠️  Warning: Expected gates {expected}, found {found_gates}")

        result = {
            'scenario': scenario_name,
            'keywords': keywords,
            'matches': len(matching_glyphs),
            'gates_covered': len(coverage['gates']),
            'coverage': coverage['coverage_percentage'],
            'expected_gates': expected_gates,
            'found_gates': list(coverage['gates'].keys()),
            'success': success
        }

        self.scenario_results.append(result)
        return result

    def run_test_suite(self):
        """Run full test suite of diverse scenarios."""
        print("\n" + "=" * 70)
        print("🌟 EMOTIONAL OS SCENARIO TESTING SUITE")
        print("Testing 7,096-Glyph Balanced Database")
        print("=" * 70)

        scenarios = [
            # Grief & Loss scenarios
            (
                "Grief Processing",
                "I feel stuck and recursive, like I'm going in circles with this grief. It's about losing someone close to me. The ache feels sacred somehow.",
                [3, 7, 11, 12]  # Deep emotion territories
            ),
            (
                "Loss & Transformation",
                "My grief is transforming. I'm learning to hold both the sadness and the gratitude for what we shared.",
                [2, 3, 5, 8]  # Paradox, transformation, creativity, devotion
            ),

            # Joy & Connection scenarios
            (
                "Celebration of Connection",
                "I've never felt more connected to my community. This joy is overflowing and I want to share it with everyone.",
                [5, 8, 9, 10]  # Creativity, abundance, community, consciousness
            ),
            (
                "Authentic Self Expression",
                "I'm finally expressing my true self creatively. It feels like I'm becoming who I've always wanted to be.",
                [1, 5, 6, 9]  # Initiation, creativity, vitality, selfhood
            ),

            # Fear & Vulnerability scenarios
            (
                "Facing Fear",
                "I'm terrified of the unknown, but I'm leaning into the uncertainty. It's teaching me to surrender.",
                [2, 10, 11]  # Paradox, consciousness, synchronicity
            ),
            (
                "Vulnerability as Strength",
                "My vulnerability is my power. I'm learning to be open and present with my own helplessness.",
                [4, 6, 8, 9]  # Foundation, vitality, devotion, self
            ),

            # Transformation & Growth scenarios
            (
                "Creative Emergence",
                "Something new is emerging from within me. I feel the creative impulse awakening.",
                [1, 3, 5]  # Initiation, transformation, creativity
            ),
            (
                "Spiritual Awakening",
                "I'm experiencing a profound awakening of consciousness. I feel transcendent and connected to something infinite.",
                [10, 11, 12]  # Consciousness, synchronicity, transcendence
            ),

            # Paradox & Balance scenarios
            (
                "Living Both/And",
                "I can hold both my strength and my fragility. I'm learning to live in the paradox of being human.",
                [2, 4, 9]  # Duality, foundation, selfhood
            ),
            (
                "Finding Center",
                "In the chaos of my life, I'm finding a center point. Everything is balanced on the edge of something new.",
                [4, 11]  # Foundation, synchronicity
            ),

            # Community & Belonging scenarios
            (
                "Tribal Connection",
                "I've found my tribe. There's a sense of belonging and shared purpose that feels deeply nourishing.",
                [8, 9]  # Abundance, community
            ),
            (
                "Individual & Collective",
                "I'm honoring my unique gifts while serving my community. It's about being myself within the collective.",
                [5, 9, 10]  # Creativity, selfhood, consciousness
            ),

            # Surrender & Acceptance scenarios
            (
                "Letting Go",
                "I'm learning to surrender and let go of control. There's a peace in accepting what I cannot change.",
                [8, 10, 11, 12]  # Devotion, consciousness, synchronicity, transcendence
            ),
            (
                "Sacred Acceptance",
                "I accept this situation as it is, sacred and whole. I'm flowing with the natural rhythm of life.",
                [11, 12]  # Synchronicity, transcendence
            ),

            # Sexual & Vital Energy scenarios
            (
                "Embodied Presence",
                "I feel alive in my body. My sexuality is sacred and my vitality is flowing.",
                [6, 8]  # Vitality, abundance
            ),
            (
                "Sensual Awakening",
                "I'm awakening to the sensuality and magnetism of embodied presence. It's creative life force.",
                [5, 6]  # Creativity, vitality
            ),

            # Complex multi-emotional scenarios
            (
                "Spiritual Crisis",
                "I'm losing my faith, my identity, my sense of self. Yet somehow in this dissolution, something sacred is emerging.",
                [3, 9, 10, 12]  # Transformation, selfhood, consciousness, transcendence
            ),
            (
                "Wholeness in Fragmentation",
                "I feel fragmented, paradoxical, impossible. And yet I'm more whole than ever. I contain multitudes.",
                [2, 4, 10]  # Paradox, foundation, consciousness
            ),
        ]

        for scenario_name, text, expected_gates in scenarios:
            self.test_scenario(scenario_name, text, expected_gates)

        # Print summary
        self._print_summary()

    def _print_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)

        total = len(self.scenario_results)
        successful = sum(1 for r in self.scenario_results if r['success'])
        total_matches = sum(r['matches'] for r in self.scenario_results)
        avg_coverage = sum(r['coverage'] for r in self.scenario_results) / total if total > 0 else 0

        print(f"\n✅ Scenarios Tested: {total}")
        print(f"✅ Successful: {successful}/{total} ({100*successful/total:.1f}%)")
        print(f"✅ Total Glyph Matches: {total_matches}")
        print(f"✅ Average Gate Coverage: {avg_coverage:.1f}%")

        # Gate coverage analysis
        all_gates = Counter()
        for result in self.scenario_results:
            all_gates.update(result['found_gates'])

        print(f"\n🗺️  GATE COVERAGE ACROSS ALL SCENARIOS:")
        gate_names = {
            1: "Initiation & Emergence",
            2: "Duality & Paradox",
            3: "Dissolution & Transformation",
            4: "Foundation & Structure",
            5: "Creativity & Expression",
            6: "Sexuality & Vitality",
            7: "Depth & Mystery",
            8: "Abundance & Devotion",
            9: "Selfhood & Community",
            10: "Consciousness & Surrender",
            11: "Synchronicity & Flow",
            12: "Transcendence & Return",
        }

        for gate in range(1, 13):
            count = all_gates.get(gate, 0)
            status = "✅" if count > 0 else "⚠️"
            print(f"   Gate {gate:2d}: {status} {count:3d} matches - {gate_names[gate]}")

        gates_covered = len(all_gates)
        print(f"\n   Total Gates Accessed: {gates_covered}/12 ({100*gates_covered/12:.1f}%)")

        # Ritual analysis
        print(f"\n🔄 RITUAL SEQUENCE COVERAGE:")
        rituals = {
            'Ascending (1→12)': list(range(1, 13)),
            'Grounding (12→1)': list(range(12, 0, -1)),
            'Inner Circle (4→9)': [4, 5, 6, 7, 8, 9],
            'Outer Cosmic': [1, 2, 3, 10, 11, 12],
            'Shadow Work (7→11)': [7, 8, 9, 10, 11],
            'Light Work (1→6)': [1, 2, 3, 4, 5, 6],
        }

        for ritual_name, ritual_gates in rituals.items():
            accessed = sum(1 for g in ritual_gates if all_gates.get(g, 0) > 0)
            percentage = 100 * accessed / len(ritual_gates)
            status = "✅" if accessed == len(ritual_gates) else "⚠️"
            print(f"   {ritual_name:25s}: {status} {accessed}/{len(ritual_gates)} gates ({percentage:.0f}%)")

        print("\n" + "=" * 70)
        print("✨ SCENARIO TESTING COMPLETE")
        print("=" * 70)


def main():
    """Run scenario test suite."""
    tester = ScenarioTester()
    tester.run_test_suite()


if __name__ == "__main__":
    main()
