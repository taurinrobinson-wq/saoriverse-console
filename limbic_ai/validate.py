#!/usr/bin/env python3
"""
Quick validation script to test core LimbicAI modules work correctly.
Run this to verify the system is functioning properly.
"""

def test_core_modules():
    """Test that core modules can be imported and used."""
    print("🧠 LimbicAI Core Module Test\n")
    print("=" * 60)
    
    # Test 1: Models
    print("\n1. Testing models...")
    try:
        from limbic_ai.models import EmotionalFeatures, LimbicState
        
        features = EmotionalFeatures(
            social_rejection=0.5,
            self_blame=0.3,
            empathy_for_other=0.7
        )
        print(f"   ✓ Created EmotionalFeatures")
        print(f"     - Social rejection: {features.social_rejection}")
        print(f"     - Self blame: {features.self_blame}")
        print(f"     - Empathy: {features.empathy_for_other}")
        
        state = LimbicState(amygdala=0.6, insula=0.4)
        print(f"   ✓ Created LimbicState")
        print(f"     - Amygdala: {state.amygdala}")
        print(f"     - Insula: {state.insula}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: NLP Parser
    print("\n2. Testing NLP Parser...")
    try:
        from limbic_ai.nlp_parser import EmotionalFeatureExtractor
        
        extractor = EmotionalFeatureExtractor()
        
        test_text = """
        I got fired from my job and it's all my fault. I should have known 
        better. My manager was right to let me go. I'm just not good enough.
        """
        
        features = extractor.extract_features(test_text)
        print(f"   ✓ Extracted features from text")
        print(f"     - Self blame: {features.self_blame:.2f}")
        print(f"     - Loss of reward: {features.loss_of_reward:.2f}")
        
        themes = extractor.get_detected_themes(test_text)
        print(f"   ✓ Detected themes:")
        for theme, keywords in themes.items():
            if keywords:
                print(f"     - {theme}: {', '.join(keywords[:2])}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 3: Mapping
    print("\n3. Testing Mapping...")
    try:
        from limbic_ai.mapping import map_features_to_limbic
        
        features = EmotionalFeatures(
            social_rejection=0.8,
            threat_to_identity=0.6,
            empathy_for_other=0.2
        )
        
        limbic = map_features_to_limbic(features)
        print(f"   ✓ Mapped features to limbic state")
        print(f"     - Amygdala: {limbic.amygdala:.2f}")
        print(f"     - Insula: {limbic.insula:.2f}")
        print(f"     - dlPFC: {limbic.dlPFC:.2f}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 4: Analyzer
    print("\n4. Testing Analyzer...")
    try:
        from limbic_ai.analyzer import LimbicAnalyzer
        
        analyzer = LimbicAnalyzer()
        
        scenario = """
        My girlfriend broke up with me because I didn't listen to her 
        emotionally. But I feel like she's just too dramatic about everything.
        She lost her job and I don't understand why that's such a big deal.
        Everyone loses their job sometimes.
        """
        
        analysis = analyzer.analyze(scenario)
        print(f"   ✓ Analyzed scenario")
        print(f"     - Scenario length: {len(scenario.split())} words")
        print(f"     - Top feature: rationalization = {analysis.emotional_features.rationalization:.2f}")
        
        summary = analyzer.get_summary(analysis)
        print(f"   ✓ Generated summary ({len(summary)} chars)")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 5: Visualization
    print("\n5. Testing Visualization...")
    try:
        from limbic_ai.visualization import generate_limbic_visualization_data, generate_svg_limbic_map
        
        limbic = LimbicState(
            amygdala=0.7,
            acc=0.6,
            insula=0.3,
            dlPFC=0.8
        )
        
        data = generate_limbic_visualization_data(limbic)
        print(f"   ✓ Generated visualization data")
        print(f"     - Nodes: {len(data['nodes'])}")
        
        svg = generate_svg_limbic_map(limbic)
        print(f"   ✓ Generated SVG map ({len(svg)} bytes)")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("\n✅ All core modules working correctly!")
    print("\nNext steps:")
    print("  1. Install Flask: pip install -r requirements.txt")
    print("  2. Run web app:    python app.py")
    print("  3. Try examples:   python examples.py")
    return True


if __name__ == "__main__":
    import sys
    import os
    
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    success = test_core_modules()
    sys.exit(0 if success else 1)
