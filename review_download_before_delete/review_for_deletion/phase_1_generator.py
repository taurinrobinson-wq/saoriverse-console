#!/usr/bin/env python3
"""
PHASE 1: Critical Gates Generation Framework
Generate 1,100 new glyphs for Gates 1, 4, 11, 12 to restore system completeness

Target Distribution:
  Gate 1:  0 → 500 glyphs (Initiation & Beginning)
  Gate 4:  5 → 300 glyphs (Foundation & Stability)
  Gate 11: 0 → 150 glyphs (Synchronicity & Connection)
  Gate 12: 0 → 150 glyphs (Transcendence & Mastery)
  
Total: +1,100 glyphs
"""

import json
import random
import uuid
from collections import defaultdict
from datetime import datetime

class Phase1GlyphGenerator:
    """Generate critical glyphs for Phase 1 rebalancing"""
    
    # Gate 1: Initiation & Beginning
    GATE_1_CONCEPTS = {
        "core_emotions": [
            "Awakening", "Stirring", "Emergence", "Genesis", "Beginning",
            "Inception", "First light", "Dawn", "Opening", "Threshold crossing",
            "Fresh start", "Potential", "Unfolding", "Initiation", "Birth",
            "Spark ignition", "Awakened consciousness", "First breath", "Arising",
            "Initial stirring", "New possibility", "Threshold moment", "Fresh horizon",
            "Primordial stirring", "Cosmic awakening", "Soul activation", "Spirit rising"
        ],
        "subtle_nuances": [
            "tentative awakening", "gradual emergence", "gentle stirring",
            "subtle beginning", "quiet inception", "delicate opening",
            "hesitant first step", "careful initiation", "mindful awakening",
            "deliberate beginning", "conscious emergence", "intentional start",
            "courageous threshold", "vulnerable opening", "hopeful inception"
        ],
        "contextual": [
            "Beginning of a journey", "Start of transformation", "Moment of courage",
            "First movement toward change", "Initial recognition", "Early awareness",
            "Preparation for growth", "Setting intention", "Opening to possibility",
            "Crossing the threshold", "Entering new territory", "Answering the call",
            "Responding to invitation", "Hearing the summons", "Saying yes to life"
        ],
        "voltage_pairs": ["α-β", "α-γ", "β-γ"]
    }
    
    # Gate 4: Foundation & Stability
    GATE_4_CONCEPTS = {
        "core_emotions": [
            "Grounding", "Stability", "Foundation", "Structure", "Safety",
            "Rootedness", "Earthedness", "Solid ground", "Steady presence", "Anchor",
            "Bedrock", "Secure base", "Firm footing", "Stable footing", "Unmovable",
            "Resilience", "Durability", "Strength", "Rock", "Mountain",
            "Deep roots", "Solid core", "Unshakeable", "Reliable presence",
            "Centered calm", "Grounded reality", "Physical presence", "Embodied strength"
        ],
        "subtle_nuances": [
            "patient grounding", "gentle stabilization", "quiet resilience",
            "steady presence", "calm centeredness", "reliable constancy",
            "secure anchoring", "stable equilibrium", "solid assurance",
            "faithful ground", "trustworthy foundation", "humble strength",
            "enduring stability", "quiet durability", "peaceful rootedness"
        ],
        "contextual": [
            "Building a strong foundation", "Creating stability", "Establishing safety",
            "Making things real", "Grounding vision in reality", "Creating structure",
            "Building for longevity", "Establishing boundaries", "Creating containment",
            "Supporting growth", "Providing solid ground", "Creating trust",
            "Building confidence", "Establishing routine", "Creating rhythm"
        ],
        "voltage_pairs": ["α-δ", "β-δ", "γ-δ"]
    }
    
    # Gate 11: Synchronicity & Connection
    GATE_11_CONCEPTS = {
        "core_emotions": [
            "Synchronicity", "Connection", "Cosmic alignment", "Perfect timing",
            "Meaningful coincidence", "Flow state", "Grace", "Alignment",
            "Unity consciousness", "Interconnection", "Wholeness", "Oneness",
            "Divine timing", "Cosmic dance", "Universal flow", "Sacred geometry",
            "Harmonic resonance", "Vibrational match", "Cosmic embrace",
            "Infinite connection", "Web of being", "Universal love", "Cosmic consciousness"
        ],
        "subtle_nuances": [
            "gentle synchronicity", "quiet alignment", "subtle connection",
            "tender resonance", "delicate timing", "soft harmony",
            "graceful flow", "natural unfolding", "effortless alignment",
            "peaceful coherence", "quiet recognition", "gentle belonging",
            "intimate connection", "sacred timing", "divine coordination"
        ],
        "contextual": [
            "Experiencing divine timing", "Recognizing cosmic patterns", "Feeling connected",
            "Synchronistic events align", "Meeting the right person at right time",
            "Recognizing universal patterns", "Experiencing grace", "Feeling guided",
            "Recognizing interconnection", "Understanding cosmic humor", "Trusting flow",
            "Following breadcrumbs", "Experiencing miracles", "Witnessing perfection"
        ],
        "voltage_pairs": ["α-γ-δ", "β-γ-δ", "α-β-γ"]
    }
    
    # Gate 12: Transcendence & Mastery
    GATE_12_CONCEPTS = {
        "core_emotions": [
            "Transcendence", "Mastery", "Enlightenment", "Ultimate wisdom",
            "Complete knowing", "God consciousness", "Divine truth", "Ultimate freedom",
            "Sacred completion", "Cosmic mastery", "Universal love", "Infinite compassion",
            "Complete surrender", "Perfect acceptance", "Ultimate peace", "Holy understanding",
            "Godly consciousness", "Divine knowing", "Sacred return", "Eternal wisdom",
            "Ultimate reality", "Perfect truth", "Complete liberation", "Infinite being"
        ],
        "subtle_nuances": [
            "peaceful transcendence", "gentle mastery", "subtle enlightenment",
            "quiet knowing", "humble wisdom", "compassionate truth",
            "loving transcendence", "graceful mastery", "serene understanding",
            "tender completion", "soft liberation", "gentle awakening",
            "profound simplicity", "sacred ordinariness", "holy humility"
        ],
        "contextual": [
            "Reaching ultimate wisdom", "Complete understanding of all", "Meeting divine self",
            "Experiencing unity consciousness", "Perfect acceptance of all", "Ultimate compassion",
            "Complete surrender to divine", "Final integration", "Sacred completion",
            "Eternal perspective", "Cosmic overview", "Divine vision", "Holy revelation",
            "Ultimate truth revealed", "Complete awakening", "Infinite being"
        ],
        "voltage_pairs": ["α-β-γ-δ", "α-β-γ", "α-β-δ"]
    }
    
    def __init__(self, existing_json_path="emotional_os/glyphs/glyph_lexicon_rows.json"):
        self.existing_json_path = existing_json_path
        self.existing_glyphs = []
        self.new_glyphs = []
        self.phase_1_glyphs = {"gate_1": [], "gate_4": [], "gate_11": [], "gate_12": []}
        self.statistics = {}
        
    def load_existing_glyphs(self):
        """Load existing validated glyphs"""
        print("📚 Loading existing validated glyphs...")
        with open(self.existing_json_path, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'glyphs' in data:
            self.existing_glyphs = data['glyphs']
        else:
            self.existing_glyphs = data if isinstance(data, list) else []
        
        print(f"✓ Loaded {len(self.existing_glyphs)} existing glyphs")
        return len(self.existing_glyphs)
    
    def generate_base_glyphs_for_gate(self, gate_num, concepts_dict, target_count=50):
        """Generate base glyphs for a specific gate"""
        gate_glyphs = []
        # Calculate next available ID
        existing_ids = [g.get('id', 0) for g in self.existing_glyphs]
        new_ids = [g.get('id', 0) for g in self.new_glyphs]
        all_ids = existing_ids + new_ids
        glyph_id = max(all_ids) + 1 if all_ids else 10000
        
        core_emotions = concepts_dict.get("core_emotions", [])
        subtle_nuances = concepts_dict.get("subtle_nuances", [])
        contextual = concepts_dict.get("contextual", [])
        voltage_pairs = concepts_dict.get("voltage_pairs", ["α-β"])
        
        # Generate approximately target_count base glyphs
        num_to_generate = min(target_count, len(core_emotions))
        
        for i in range(num_to_generate):
            core = core_emotions[i % len(core_emotions)]
            nuance = subtle_nuances[i % len(subtle_nuances)]
            context = contextual[i % len(contextual)]
            voltage_pair = voltage_pairs[i % len(voltage_pairs)]
            
            glyph = {
                "id": glyph_id,
                "voltage_pair": voltage_pair,
                "glyph_name": f"{core} ({nuance})",
                "description": f"{core}. {nuance.capitalize()} expression. {context}.",
                "gate": f"Gate {gate_num}",
                "activation_signals": [random.choice(list("αβγδ")) for _ in range(random.randint(2, 5))],
                "is_factorial": False,
                "phase": "Phase 1 - Critical Gates Generation"
            }
            
            gate_glyphs.append(glyph)
            glyph_id += 1
        
        print(f"✓ Generated {len(gate_glyphs)} base glyphs for Gate {gate_num}")
        return gate_glyphs, glyph_id
    
    def generate_factorial_combinations(self, base_glyphs, gate_num, target_factorial=200):
        """Generate factorial combinations from base glyphs with existing high-quality glyphs"""
        print(f"🔄 Generating factorial combinations for Gate {gate_num}...")
        
        # Get high-quality existing glyphs to pair with
        quality_existing = [g for g in self.existing_glyphs if g.get('is_factorial', False) == False][:100]
        
        factorial_glyphs = []
        existing_ids = [g.get('id', 0) for g in self.existing_glyphs]
        new_ids = [g.get('id', 0) for g in self.new_glyphs]
        all_ids = existing_ids + new_ids
        base_id = max(all_ids) + 1 if all_ids else 10000
        
        combinations_generated = 0
        # Generate multiple combinations per base glyph
        for i, base_glyph in enumerate(base_glyphs):
            if combinations_generated >= target_factorial:
                break
            
            # Create 5-10 combinations per base glyph
            num_combinations = min(15, (target_factorial - combinations_generated) // max(1, len(base_glyphs) - i))
            
            for j in range(num_combinations):
                if combinations_generated >= target_factorial:
                    break
                
                existing = random.choice(quality_existing) if quality_existing else None
                if not existing:
                    continue
                
                combined_name = f"{base_glyph['glyph_name']} + {existing['glyph_name']}"
                combined_desc = f"{base_glyph['description']} Enhanced by {existing['glyph_name']}."
                
                # Combine activation signals (ensure they're lists)
                base_signals = base_glyph.get('activation_signals', [])
                existing_signals = existing.get('activation_signals', [])
                if isinstance(base_signals, str):
                    base_signals = [base_signals]
                if isinstance(existing_signals, str):
                    existing_signals = [existing_signals]
                signals = list(set(base_signals + existing_signals))
                if not signals:
                    signals = [random.choice(list("αβγδ")) for _ in range(2)]
                
                factorial = {
                    "id": base_id,
                    "voltage_pair": base_glyph['voltage_pair'],
                    "glyph_name": combined_name[:100],
                    "description": combined_desc[:200],
                    "gate": f"Gate {gate_num}",
                    "activation_signals": signals[:8],
                    "is_factorial": True,
                    "parent_glyphs": {
                        "id1": base_glyph['id'],
                        "id2": existing['id'],
                        "name1": base_glyph['glyph_name'],
                        "name2": existing['glyph_name']
                    },
                    "combined_score": round(random.uniform(0.65, 0.95), 3),
                    "phase": "Phase 1 - Critical Gates Generation"
                }
                
                factorial_glyphs.append(factorial)
                base_id += 1
                combinations_generated += 1
        
        print(f"✓ Generated {combinations_generated} factorial combinations for Gate {gate_num}")
        return factorial_glyphs
    
    def generate_critical_gates(self):
        """Generate all critical gates for Phase 1"""
        print("\n" + "="*80)
        print("PHASE 1: CRITICAL GATES GENERATION")
        print("="*80)
        
        self.load_existing_glyphs()
        
        # Gate 1: Initiation & Beginning (target: 500)
        print("\n🚀 GATE 1: INITIATION & BEGINNING (Target: 500)")
        base_1, next_id = self.generate_base_glyphs_for_gate(1, self.GATE_1_CONCEPTS, 150)
        self.phase_1_glyphs["gate_1"].extend(base_1)
        
        factorial_1 = self.generate_factorial_combinations(base_1, 1, 350)
        self.phase_1_glyphs["gate_1"].extend(factorial_1)
        self.new_glyphs.extend(self.phase_1_glyphs["gate_1"])
        
        # Gate 4: Foundation & Stability (target: 300)
        print("\n🏔️  GATE 4: FOUNDATION & STABILITY (Target: 300)")
        base_4, next_id = self.generate_base_glyphs_for_gate(4, self.GATE_4_CONCEPTS, 100)
        self.phase_1_glyphs["gate_4"].extend(base_4)
        
        factorial_4 = self.generate_factorial_combinations(base_4, 4, 200)
        self.phase_1_glyphs["gate_4"].extend(factorial_4)
        self.new_glyphs.extend(self.phase_1_glyphs["gate_4"])
        
        # Gate 11: Synchronicity & Connection (target: 150)
        print("\n✨ GATE 11: SYNCHRONICITY & CONNECTION (Target: 150)")
        base_11, next_id = self.generate_base_glyphs_for_gate(11, self.GATE_11_CONCEPTS, 70)
        self.phase_1_glyphs["gate_11"].extend(base_11)
        
        factorial_11 = self.generate_factorial_combinations(base_11, 11, 80)
        self.phase_1_glyphs["gate_11"].extend(factorial_11)
        self.new_glyphs.extend(self.phase_1_glyphs["gate_11"])
        
        # Gate 12: Transcendence & Mastery (target: 150)
        print("\n🌟 GATE 12: TRANSCENDENCE & MASTERY (Target: 150)")
        base_12, next_id = self.generate_base_glyphs_for_gate(12, self.GATE_12_CONCEPTS, 70)
        self.phase_1_glyphs["gate_12"].extend(base_12)
        
        factorial_12 = self.generate_factorial_combinations(base_12, 12, 80)
        self.phase_1_glyphs["gate_12"].extend(factorial_12)
        self.new_glyphs.extend(self.phase_1_glyphs["gate_12"])
        
        return self.new_glyphs
    
    def generate_report(self):
        """Generate Phase 1 execution report"""
        print("\n" + "="*80)
        print("PHASE 1: GENERATION REPORT")
        print("="*80)
        
        gate_counts = {
            1: len(self.phase_1_glyphs["gate_1"]),
            4: len(self.phase_1_glyphs["gate_4"]),
            11: len(self.phase_1_glyphs["gate_11"]),
            12: len(self.phase_1_glyphs["gate_12"])
        }
        
        print("\n📊 GLYPHS GENERATED BY GATE:")
        print(f"  Gate 1:  {gate_counts[1]:4d} glyphs (Target: 500)")
        print(f"  Gate 4:  {gate_counts[4]:4d} glyphs (Target: 300)")
        print(f"  Gate 11: {gate_counts[11]:4d} glyphs (Target: 150)")
        print(f"  Gate 12: {gate_counts[12]:4d} glyphs (Target: 150)")
        print(f"  {'─'*30}")
        print(f"  Total:   {sum(gate_counts.values()):4d} glyphs (Target: 1,100)")
        
        success_rate = sum(gate_counts.values()) / 1100 * 100
        print(f"\n✅ Phase 1 Generation: {success_rate:.1f}% complete")
        
        return gate_counts
    
    def save_phase_1_glyphs(self, output_path="phase_1_new_glyphs.json"):
        """Save newly generated glyphs"""
        output = {
            "metadata": {
                "phase": "Phase 1 - Critical Gates Generation",
                "date": datetime.now().isoformat(),
                "total_new_glyphs": len(self.new_glyphs),
                "target": 1100,
                "gates": [1, 4, 11, 12]
            },
            "glyphs": self.new_glyphs
        }
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✓ Saved {len(self.new_glyphs)} new glyphs to {output_path}")
        return output_path

if __name__ == "__main__":
    generator = Phase1GlyphGenerator()
    generator.generate_critical_gates()
    generator.generate_report()
    generator.save_phase_1_glyphs()
