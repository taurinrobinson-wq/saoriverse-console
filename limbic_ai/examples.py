"""
Example scenarios demonstrating LimbicAI capabilities.
"""

EXAMPLE_SCENARIOS = {
    "breakup_rationalization": """
My girlfriend broke up with me. She said I couldn't hear her and didn't know 
how to support her emotionally, but I always felt like she was too dramatic 
and overblown. I mean she got fired from her job, it happens, I don't get 
why that's such a big deal. We had a good relationship otherwise. 
I don't know what she wanted from me.
""",
    
    "job_loss_self_blame": """
I got fired from my job today. It's all my fault. I should have known 
better. I made careless mistakes and didn't double-check my work. My 
manager gave me a chance and I blew it. Everyone says it wasn't my fault, 
that the company is poorly run, but I know the truth. I'm just not good 
enough. I don't know how I'll tell my family. They're going to be so 
disappointed in me.
""",
    
    "empathetic_response": """
My best friend is going through a really hard time. Their parent just 
passed away unexpectedly. I can feel how much pain they're in, and it 
hurts to see them suffer. We spent hours talking, and I was there 
listening to their memories and feelings. I want to support them through 
this. I can see how much they mean to me and how important it is to be 
present for them right now.
""",
    
    "identity_threat": """
I was told that I'm not as smart as I thought I was. Someone at work 
pointed out a flaw in my reasoning in front of everyone. This really 
shook me because I've always seen myself as someone who is intelligent 
and capable. Now I'm questioning everything about myself. Who am I if 
I'm not actually that smart? This feels like a fundamental challenge 
to how I understand myself.
""",
    
    "loss_aversion": """
I had the opportunity to take a big promotion with a 30% raise, but 
I turned it down because it would require moving to a new city. I know 
it would have been good for my career, but I can't stop thinking about 
what I'm losing by staying here - the opportunity, the money, the growth. 
Others are telling me I'm lucky to be in this position, but all I can 
think about is what I gave up.
""",
}


def run_example(scenario_key: str) -> None:
    """Run an example scenario through the analyzer.
    
    Args:
        scenario_key: Key from EXAMPLE_SCENARIOS
    """
    from limbic_ai.analyzer import LimbicAnalyzer
    
    if scenario_key not in EXAMPLE_SCENARIOS:
        print(f"Unknown scenario: {scenario_key}")
        print(f"Available: {', '.join(EXAMPLE_SCENARIOS.keys())}")
        return
    
    scenario = EXAMPLE_SCENARIOS[scenario_key]
    analyzer = LimbicAnalyzer()
    
    print(f"\n{'='*70}")
    print(f"SCENARIO: {scenario_key.upper()}")
    print(f"{'='*70}\n")
    
    print("INPUT TEXT:")
    print("-" * 70)
    print(scenario.strip())
    print("-" * 70)
    
    # Analyze
    analysis = analyzer.analyze(scenario)
    
    print("\nEXTRACTED FEATURES:")
    print("-" * 70)
    features = analysis.emotional_features
    print(f"Social Rejection:     {features.social_rejection:.1%}")
    print(f"Self Blame:           {features.self_blame:.1%}")
    print(f"Other Blame:          {features.other_blame:.1%}")
    print(f"Empathy for Other:    {features.empathy_for_other:.1%}")
    print(f"Rationalization:      {features.rationalization:.1%}")
    print(f"Threat to Identity:   {features.threat_to_identity:.1%}")
    print(f"Loss of Reward:       {features.loss_of_reward:.1%}")
    
    print("\nLIMBIC ACTIVATIONS:")
    print("-" * 70)
    state = analysis.limbic_state
    limbic_dict = state.as_dict()
    for region, activation in sorted(limbic_dict.items(), key=lambda x: x[1], reverse=True):
        bar_length = int(activation * 40)
        bar = "█" * bar_length + "░" * (40 - bar_length)
        print(f"{region:20s} {activation:5.1%} [{bar}]")
    
    print("\nSUMMARY:")
    print("-" * 70)
    print(analyzer.get_summary(analysis))


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        scenario_key = sys.argv[1]
    else:
        print("Available scenarios:")
        for i, key in enumerate(EXAMPLE_SCENARIOS.keys(), 1):
            print(f"  {i}. {key}")
        
        choice = input("\nSelect scenario (number or key): ").strip()
        
        if choice.isdigit():
            scenario_key = list(EXAMPLE_SCENARIOS.keys())[int(choice) - 1]
        else:
            scenario_key = choice
    
    run_example(scenario_key)
