from src.emotional_os.core.firstperson import create_orchestrator, create_affect_parser

print("Testing orchestrator creation...")
orch = create_orchestrator("test_user", "test_conv")
print(f"✓ Orchestrator created: {orch}")
print(f"  Agent state manager: {orch.agent_state_manager}")

print("\nTesting affect parser creation...")
parser = create_affect_parser()
print(f"✓ Affect parser created: {parser}")

print("\nTesting generate_response_with_glyph...")
test_glyph = {"glyph_name": "The Void", "description": "Emptiness and darkness"}
response = orch.generate_response_with_glyph("I feel so empty", test_glyph)
print(f"✓ Generated response: {response[:100]}")

print("\n✅ All tests passed!")
