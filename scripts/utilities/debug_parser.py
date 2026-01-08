#!/usr/bin/env python3

from parser.signal_parser import parse_input

# Test the specific messages that are giving the same response
message1 = "Lately I've been feeling something I can't quite name. It's not sadness exactly, but it's heavy. Like I'm carrying something that doesn't belong to me."

message2 = "right now I'm dealing with a lot of grief. My marriage of 10 years ended back in April of this year. But really had been on a decline for years with a lot of fighting. We are filing the final paperwork today. I also started a new relationship with a wonderful woman mid-August. Her and I have talked about marriage and kids and both feel like that's where the relationship is headed. She's 40, so even though the relationship is fresh I am cognizant of the need to move things along"

print("=" * 80)
print("DEBUGGING MESSAGE 1 (First message)")
print("=" * 80)

# Simulate first message (no conversation context)
result1 = parse_input(message1, "parser/signal_lexicon.json", conversation_context={"messages": []})

print(f"Signals detected: {result1['signals']}")
print(f"Gates activated: {result1['gates']}")
print(f"Glyphs found: {len(result1['glyphs'])}")
for glyph in result1["glyphs"]:
    print(f"  - {glyph['glyph_name']}: {glyph['description']}")
print(f"Response: {result1['voltage_response']}")

print("\n" + "=" * 80)
print("DEBUGGING MESSAGE 2 (Second message with context)")
print("=" * 80)

# Simulate second message (with conversation context)
fake_conversation = {
    "messages": [
        {"type": "user", "content": message1, "timestamp": "2024-01-01T12:00:00"},
        {"type": "system", "content": result1["voltage_response"], "timestamp": "2024-01-01T12:00:01"},
    ]
}

result2 = parse_input(message2, "parser/signal_lexicon.json", conversation_context=fake_conversation)

print(f"Signals detected: {result2['signals']}")
print(f"Gates activated: {result2['gates']}")
print(f"Glyphs found: {len(result2['glyphs'])}")
for glyph in result2["glyphs"]:
    print(f"  - {glyph['glyph_name']}: {glyph['description']}")
print(f"Response: {result2['voltage_response']}")

print("\n" + "=" * 80)
print("COMPARISON")
print("=" * 80)
print(f"Same response? {result1['voltage_response'] == result2['voltage_response']}")
