"""
Sample Velinor Story - Clean Implementation
=============================================

This module demonstrates how to build a Velinor story using the StoryBuilder API.

Features:
- Passages with separate fields (id, text, background, npc)
- Choices with tone effects, NPC resonance, and dice checks
- Proper Velinor JSON export (no Twine markup)
- Integration with Emotional OS (tone_effects, npc_resonance)

Stories are exported as Velinor-native JSON format, compatible with StorySession.
"""

from velinor.story.story_builder import StoryBuilder


def build_velinor_sample_story():
    """Build a sample story scaffold for Velinor using clean API."""
    
    story = StoryBuilder(
        "Velinor: Remnants of the Tone - Sample",
        author="Saoriverse Team",
        region="Marketplace"
    )
    
    # ========== OPENING SCENE ==========
    story.add_passage(
        passage_id="market_entry",
        text="You emerge from the collapsed underpass into the Market District of Saonyx. "
             "Crumbling vendor stalls line the plaza. Vines creep up shattered windows. "
             "Bioluminescent fungi cast a faint glow.\n\n"
             "A figure approaches from the shadows—an older person with weathered skin and "
             "eyes that seem to recognize something in you.\n\n"
             "'Welcome to the Remnants,' they say. 'I am the Keeper. You carry the weight "
             "of choice. The Tone pulses here still, waiting for those who listen.'",
        background="market_ruins",
        npc="Keeper",
        tags=["intro", "market"],
        is_start=True
    )
    
    story.add_choice(
        from_passage_id="market_entry",
        text="Approach and ask about the Tone",
        target_id="keeper_dialogue_1",
        tone_effects={"courage": 0.1},
        npc_resonance={"Keeper": 0.2}
    )
    
    story.add_choice(
        from_passage_id="market_entry",
        text="Explore the Market first",
        target_id="market_exploration",
        tone_effects={"wisdom": 0.1}
    )
    
    story.add_choice(
        from_passage_id="market_entry",
        text="Keep your distance and observe",
        target_id="keeper_wary",
        dice_check={"stat": "wisdom", "dc": 11}
    )
    
    # ========== KEEPER DIALOGUE PATH ==========
    story.add_passage(
        passage_id="keeper_dialogue_1",
        text="The Keeper's eyes soften. 'I've been waiting for someone like you. The city "
             "remembers things we've forgotten. The Tone—our collective voice—still echoes "
             "through these ruins.\n\n"
             "They gesture to nearby monuments, half-buried in moss.\n\n"
             "'Those markers hold fragments of what we were. If you're brave enough to "
             "seek them, you might understand what was lost... and what can be recovered.'",
        background="market_ruins",
        npc="Keeper",
        tags=["dialogue", "lore"]
    )
    
    story.add_choice(
        from_passage_id="keeper_dialogue_1",
        text="Ask to be guided",
        target_id="keeper_guide",
        tone_effects={"courage": 0.05},
        npc_resonance={"Keeper": 0.1}
    )
    
    story.add_choice(
        from_passage_id="keeper_dialogue_1",
        text="Ask about the glyphs",
        target_id="keeper_glyphs",
        tone_effects={"wisdom": 0.1}
    )
    
    story.add_choice(
        from_passage_id="keeper_dialogue_1",
        text="Explore alone",
        target_id="market_alone",
        tone_effects={"courage": 0.05}
    )
    
    # ========== KEEPER GUIDE PATH ==========
    story.add_passage(
        passage_id="keeper_guide",
        text="The Keeper leads you deeper into the Market District. The monuments draw "
             "closer—ancient pillars inscribed with symbols that shift in the light.\n\n"
             "'These were gathering places. The Tone was strongest here. Listen carefully.'\n\n"
             "You hear it—a faint resonance, like thousands of voices speaking in unison, "
             "now fractured and distant.\n\n"
             "'Choose one monument to approach. It will test you.'",
        background="monuments",
        npc="Keeper",
        tags=["monuments"],
        glyph_rewards=["Courage", "Wisdom"]
    )
    
    story.add_choice(
        from_passage_id="keeper_guide",
        text="Test Courage",
        target_id="courage_monument",
        dice_check={"stat": "courage", "dc": 12},
        tone_effects={"courage": 0.15},
        mark_story_beat="monument_courage"
    )
    
    story.add_choice(
        from_passage_id="keeper_guide",
        text="Test Wisdom",
        target_id="wisdom_monument",
        dice_check={"stat": "wisdom", "dc": 12},
        tone_effects={"wisdom": 0.15}
    )
    
    story.add_choice(
        from_passage_id="keeper_guide",
        text="Test Empathy",
        target_id="empathy_monument",
        dice_check={"stat": "empathy", "dc": 11},
        tone_effects={"empathy": 0.15}
    )
    
    # ========== MONUMENTS ==========
    story.add_passage(
        passage_id="courage_monument",
        text="You approach the monument carved with fire and forward motion. The "
             "bioluminescent glow intensifies. You feel a sudden weight—accumulated fear.\n\n"
             "[Courage check DC 12]\n\n"
             "SUCCESS: The weight passes through you. You stand firm. The monument glows "
             "brightly. You gain a Glyph of Courage.\n\n"
             "FAILURE: The weight overwhelms you. You stumble back. Something valuable "
             "slips away.",
        background="monuments",
        tags=["monument"],
        glyph_rewards=["Courage"],
        tone_effects_on_enter={"courage": 0.05}
    )
    
    story.add_choice(
        from_passage_id="courage_monument",
        text="Return to Keeper",
        target_id="keeper_aftermath",
        tone_effects={"resolve": 0.1}
    )
    
    story.add_choice(
        from_passage_id="courage_monument",
        text="Continue exploring",
        target_id="market_alone"
    )
    
    story.add_passage(
        passage_id="wisdom_monument",
        text="You approach the monument carved with scrolls and stars. Its light is softer.\n\n"
             "[Wisdom check DC 12]\n\n"
             "SUCCESS: Clarity washes over you. Symbols suddenly make sense. You gain a "
             "Glyph of Wisdom.\n\n"
             "FAILURE: The symbols remain cryptic. You sense something important you're "
             "missing.",
        background="monuments",
        tags=["monument"],
        glyph_rewards=["Wisdom"],
        tone_effects_on_enter={"wisdom": 0.05}
    )
    
    story.add_choice(
        from_passage_id="wisdom_monument",
        text="Return to Keeper",
        target_id="keeper_aftermath",
        tone_effects={"resolve": 0.1}
    )
    
    story.add_choice(
        from_passage_id="wisdom_monument",
        text="Continue exploring",
        target_id="market_alone"
    )
    
    story.add_passage(
        passage_id="empathy_monument",
        text="You approach the monument with intertwined figures. Its light pulses like "
             "a heartbeat.\n\n"
             "[Empathy check DC 11]\n\n"
             "SUCCESS: You feel connections between all things. The monument glows warmly. "
             "You gain a Glyph of Empathy.\n\n"
             "FAILURE: The pulse feels overwhelming. You step back.",
        background="monuments",
        tags=["monument"],
        glyph_rewards=["Empathy"],
        tone_effects_on_enter={"empathy": 0.05}
    )
    
    story.add_choice(
        from_passage_id="empathy_monument",
        text="Return to Keeper",
        target_id="keeper_aftermath",
        tone_effects={"resolve": 0.1}
    )
    
    story.add_choice(
        from_passage_id="empathy_monument",
        text="Continue exploring",
        target_id="market_alone"
    )
    
    # ========== KEEPER GLYPHS ==========
    story.add_passage(
        passage_id="keeper_glyphs",
        text="The Keeper leans in, voice becoming reverent.\n\n"
             "'Glyphs are echoes of truth. When our civilization was whole, we encoded "
             "our deepest values—Courage, Wisdom, Empathy, Resolve—into symbols we could "
             "touch and internalize. They were compasses for the soul.\n\n"
             "When everything collapsed, the glyphs remained, scattered, waiting.\n\n"
             "Each glyph strengthens you—not in body, but in resonance. You'll hear the "
             "Tone more clearly.'\n\n"
             "'But be warned: gathering glyphs requires vulnerability. You must face the "
             "memories they hold.'",
        background="market_ruins",
        npc="Keeper",
        tags=["lore"]
    )
    
    story.add_choice(
        from_passage_id="keeper_glyphs",
        text="Ask if Keeper has glyphs",
        target_id="keeper_has_glyphs",
        tone_effects={"wisdom": 0.1},
        npc_resonance={"Keeper": 0.15}
    )
    
    story.add_choice(
        from_passage_id="keeper_glyphs",
        text="Express determination",
        target_id="market_alone",
        tone_effects={"courage": 0.15},
        npc_resonance={"Keeper": 0.25}
    )
    
    # ========== KEEPER HAS GLYPHS ==========
    story.add_passage(
        passage_id="keeper_has_glyphs",
        text="The Keeper nods. 'I was wondering when you'd ask.'\n\n"
             "They lead you to a hidden chamber beneath a market stall. Inside, dozens of "
             "glyphs glow on shelves carved from stone.\n\n"
             "'I've preserved these for decades. They were never meant to be hoarded. They "
             "need to be carried into the living world. Spread across Saonyx by someone "
             "with strength to understand them.'\n\n"
             "The Keeper selects four—Courage, Wisdom, Empathy, Resolve.\n\n"
             "'Start with these. Prove yourself, and others will reveal themselves.'",
        background="keeper_sanctuary",
        npc="Keeper",
        tags=["gift"],
        glyph_rewards=["Courage", "Wisdom", "Empathy", "Resolve"]
    )
    
    story.add_choice(
        from_passage_id="keeper_has_glyphs",
        text="Accept and ask for guidance",
        target_id="keeper_guidance",
        tone_effects={"wisdom": 0.1},
        npc_resonance={"Keeper": 0.3},
        mark_story_beat="received_glyphs"
    )
    
    # ========== EXPLORATION ==========
    story.add_passage(
        passage_id="market_exploration",
        text="You explore the Market District on your own, mapping the ruins.\n\n"
             "You notice several paths:\n"
             "- A collapsed building with flickering lights (Archive?)\n"
             "- Stairs descending into darkness (Underground?)\n"
             "- A bridge spanning a ravine (Bridge?)\n\n"
             "The Keeper's voice: 'Be careful. Not all memories are kind.'",
        background="market_ruins",
        tags=["exploration"]
    )
    
    story.add_choice(
        from_passage_id="market_exploration",
        text="Archive",
        target_id="archive_entrance",
        tone_effects={"wisdom": 0.1}
    )
    
    story.add_choice(
        from_passage_id="market_exploration",
        text="Underground",
        target_id="underground_entrance",
        tone_effects={"courage": 0.05}
    )
    
    story.add_choice(
        from_passage_id="market_exploration",
        text="Bridge",
        target_id="bridge_crossing",
        tone_effects={"resolve": 0.1}
    )
    
    story.add_choice(
        from_passage_id="market_exploration",
        text="Back to Keeper",
        target_id="keeper_dialogue_1"
    )
    
    # ========== MARKET ALONE ==========
    story.add_passage(
        passage_id="market_alone",
        text="You venture deeper, determined to forge your own path. The ruins spread like "
             "a skeleton of what was—vendor stalls hinting at commerce and culture.",
        background="market_ruins",
        tags=["exploration"]
    )
    
    story.add_choice(
        from_passage_id="market_alone",
        text="Archive",
        target_id="archive_entrance",
        tone_effects={"wisdom": 0.1}
    )
    
    story.add_choice(
        from_passage_id="market_alone",
        text="Underground",
        target_id="underground_entrance",
        tone_effects={"courage": 0.05}
    )
    
    story.add_choice(
        from_passage_id="market_alone",
        text="Bridge",
        target_id="bridge_crossing",
        tone_effects={"resolve": 0.1}
    )
    
    # ========== LOCATIONS ==========
    story.add_passage(
        passage_id="archive_entrance",
        text="You approach a collapsed building. A younger figure emerges—ink-stained "
             "fingers, hungry eyes.\n\n"
             "'The Archive. Or what's left. Welcome. You're here to remember, yes?'\n\n"
             "[Continuation: Archivist questline...]",
        background="archive_ruins",
        npc="Archivist",
        tags=["ending"]
    )
    
    story.add_passage(
        passage_id="underground_entrance",
        text="Stairs descend into darkness. Your footsteps echo. The fungi glow brighter "
             "here.\n\n"
             "You emerge into a sprawling underground city—tunnels, plazas, infrastructure "
             "that kept the surface alive.\n\n"
             "[Continuation: Underground questline...]",
        background="underground_ruins",
        tags=["ending"]
    )
    
    story.add_passage(
        passage_id="bridge_crossing",
        text="A bridge stretches across a ravine filled with mist and glowing plants. A "
             "figure stands at the midpoint—a sentinel.\n\n"
             "'The bridge doesn't let just anyone pass. Who are you? What brings you to "
             "the other side?'\n\n"
             "[Continuation: Bridge questline...]",
        background="bridge_ravine",
        npc="Bridge Sentinel",
        tags=["ending"]
    )
    
    # ========== KEEPER AFTERMATH ==========
    story.add_passage(
        passage_id="keeper_aftermath",
        text="You return to the Keeper, changed.\n\n"
             "'You've taken your first true step. The Tone recognizes you now. That will "
             "open doors... and create enemies. But that is the path.'",
        background="market_ruins",
        npc="Keeper",
        tags=["checkpoint"]
    )
    
    story.add_choice(
        from_passage_id="keeper_aftermath",
        text="Ask about other locations",
        target_id="keeper_locations"
    )
    
    story.add_choice(
        from_passage_id="keeper_aftermath",
        text="Continue exploring",
        target_id="market_alone"
    )
    
    # ========== CONTINUATIONS ==========
    story.add_passage(
        passage_id="keeper_wary",
        text="You stand at distance, studying carefully. The Keeper glances nervously at "
             "a doorway, tension in their shoulders.\n\n"
             "After a moment, the Keeper turns to you. 'Careful ones often last longer in "
             "the Remnants. Come—let's talk.'",
        background="market_ruins",
        npc="Keeper",
        tags=["dialogue"]
    )
    
    story.add_choice(
        from_passage_id="keeper_wary",
        text="Approach now",
        target_id="keeper_dialogue_1",
        tone_effects={"courage": 0.05},
        npc_resonance={"Keeper": 0.25}
    )
    
    story.add_passage(
        passage_id="keeper_guidance",
        text="'My role is different now. I watch, preserve, guide. But you must carry the "
             "glyphs forward, spread the Tone across Saonyx. That means traveling, meeting "
             "others, facing challenges. Use that power wisely.'",
        background="keeper_sanctuary",
        npc="Keeper",
        tags=["guidance"]
    )
    
    story.add_choice(
        from_passage_id="keeper_guidance",
        text="Set out into the world",
        target_id="market_alone",
        tone_effects={"courage": 0.1},
        mark_story_beat="began_quest"
    )
    
    story.add_passage(
        passage_id="keeper_locations",
        text="'The Archive to the north holds records. The Underground was hidden—we think "
             "the administration retreated there. The Bridge to the east leads to territories "
             "we've lost contact with.\n\n"
             "Each has dangers and opportunities. Each will teach you what we were... and "
             "what we might become.'",
        background="market_ruins",
        npc="Keeper",
        tags=["guidance"]
    )
    
    story.add_choice(
        from_passage_id="keeper_locations",
        text="Archive",
        target_id="archive_entrance",
        tone_effects={"wisdom": 0.1}
    )
    
    story.add_choice(
        from_passage_id="keeper_locations",
        text="Underground",
        target_id="underground_entrance",
        tone_effects={"courage": 0.05}
    )
    
    story.add_choice(
        from_passage_id="keeper_locations",
        text="Bridge",
        target_id="bridge_crossing",
        tone_effects={"resolve": 0.1}
    )
    
    # ========== EXPORT ==========
    export_path = "d:/saoriverse-console/velinor/stories/sample_story.json"
    story.export_json(export_path)
    
    print(f"Sample story created at: {export_path}")
    
    # Validate
    errors = story.validate()
    if errors:
        print("Validation warnings:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Story validated successfully!")
    
    return story


if __name__ == "__main__":
    build_velinor_sample_story()
"""
Sample Velinor Story - Clean Implementation
=============================================

This module demonstrates how to build a Velinor story using the StoryBuilder API.

Features:
- Passages with separate fields (id, text, background, npc)
- Choices with tone effects, NPC resonance, and dice checks
- Proper Velinor JSON export (no Twine markup)
- Integration with Emotional OS (tone_effects, npc_resonance)

Stories are exported as Velinor-native JSON format, compatible with StorySession.
"""

from velinor.story.story_builder import StoryBuilder


def build_velinor_sample_story():
    """Build a sample story scaffold for Velinor using clean API."""
    
    story = StoryBuilder(
        "Velinor: Remnants of the Tone - Sample",
        author="Saoriverse Team",
        region="Marketplace"
    )
    
    # ========== OPENING SCENE ==========
    # Market District - First encounter
    story.add_passage(
        passage_id="market_entry",
        text="You emerge from the collapsed underpass into what was once the Market "
             "District of Saonyx. Crumbling vendor stalls line the plaza, worn by time "
             "and weather. Vines creep up shattered windows, and bioluminescent fungi "
             "cast a faint glow on the stone.\n\n"
             "A figure approaches from the shadows—an older person with weathered skin "
             "and eyes that seem to recognize something in you.\n\n"
             "'Welcome to the Remnants,' they say. 'I am called the Keeper. You carry "
             "the weight of choice in you. The Tone pulses faintly here still, waiting "
             "for those who listen.'",
        background="market_ruins",
        npc="Keeper",
        tags=["intro", "market", "opening"],
        is_start=True
    )
    
    # Choice 1: Approach directly (increases courage)
    story.add_choice(
        from_passage_id="market_entry",
        text="Approach the Keeper and ask about the Tone",
        target_id="keeper_dialogue_1",
        tone_effects={"courage": 0.1},
        npc_resonance={"Keeper": 0.2}
    )
    
    # Choice 2: Explore first (increases wisdom)
    story.add_choice(
        from_passage_id="market_entry",
        text="Explore the Market District before speaking",
        target_id="market_exploration",
        tone_effects={"wisdom": 0.1}
    )
    
    # Choice 3: Stay cautious (requires wisdom check)
    story.add_choice(
        from_passage_id="market_entry",
        text="Keep your distance and observe",
        target_id="keeper_wary",
        dice_check={"stat": "wisdom", "dc": 11},
        tone_effects={"resolve": 0.05}
    )
    
    # ========== KEEPER DIALOGUE PATH ==========
    story.add_passage(
        passage_id="keeper_dialogue_1",
        text="The Keeper's eyes soften as you approach.\n\n"
             "'I've been waiting for someone like you,' they say. 'The city remembers "
             "things we've forgotten. The Tone—our collective voice, our shared "
             "resonance—it still echoes through these ruins. Most who come here don't "
             "know how to listen. But you... you carry glyphs within you.'\n\n"
             "They gesture to nearby stone monuments, half-buried in moss and soil.\n\n"
             "'Those markers hold fragments of what we were. If you're brave enough to "
             "seek them out, you might begin to understand what was lost... and what "
             "can be recovered.'",
        background="market_ruins",
        npc="Keeper",
        tags=["dialogue", "lore"]
    )
    
    story.add_choice(
        from_passage_id="keeper_dialogue_1",
        text="Ask the Keeper to guide you",
        target_id="keeper_guide",
        tone_effects={"courage": 0.05},
        npc_resonance={"Keeper": 0.1}
    )
    
    story.add_choice(
        from_passage_id="keeper_dialogue_1",
        text="Ask about the glyphs",
        target_id="keeper_glyphs",
        tone_effects={"wisdom": 0.1}
    )
    
    story.add_choice(
        from_passage_id="keeper_dialogue_1",
        text="Explore alone",
        target_id="market_alone",
        tone_effects={"courage": 0.05, "empathy": -0.05},
        npc_resonance={"Keeper": -0.1}
    )
    
    # ========== KEEPER GUIDE PATH ==========
    story.add_passage(
        passage_id="keeper_guide",
        text="The Keeper leads you deeper into the Market District, their footsteps "
             "echoing softly on cracked stone. The monuments draw closer—ancient pillars "
             "inscribed with symbols that seem to shift in the bioluminescent light.\n\n"
             "'These were gathering places,' the Keeper explains. 'Where citizens came "
             "to speak, to share their burdens and joys. The Tone was strongest here. "
             "Listen carefully...'\n\n"
             "You hear it—a faint resonance, like thousands of voices speaking in unison, "
             "now fractured and distant.\n\n"
             "'The first monument holds Courage. The second, Wisdom. The third, Empathy. "
             "And the fourth... something I've never understood. Not all emotions have "
             "names. Choose one to approach. It will test you.'",
        background="monuments",
        npc="Keeper",
        tags=["monuments", "challenge"],
        glyph_rewards=["Courage", "Wisdom"]
    )
    
    story.add_choice(
        from_passage_id="keeper_guide",
        text="Test Courage",
        target_id="courage_monument",
        dice_check={"stat": "courage", "dc": 12},
        tone_effects={"courage": 0.15},
        mark_story_beat="monument_courage"
    )
    
    story.add_choice(
        from_passage_id="keeper_guide",
        text="Test Wisdom",
        target_id="wisdom_monument",
        dice_check={"stat": "wisdom", "dc": 12},
        tone_effects={"wisdom": 0.15},
        mark_story_beat="monument_wisdom"
    )
    
    story.add_choice(
        from_passage_id="keeper_guide",
        text="Test Empathy",
        target_id="empathy_monument",
        dice_check={"stat": "empathy", "dc": 11},
        tone_effects={"empathy": 0.15},
        mark_story_beat="monument_empathy"
    )
    
    story.add_choice(
        from_passage_id="keeper_guide",
        text="Test the unknown",
        target_id="unknown_monument",
        dice_check={"stat": "resolve", "dc": 13},
        tone_effects={"resolve": 0.2},
        mark_story_beat="monument_unknown"
    )
    
    # ========== MONUMENT: COURAGE ==========
    story.add_passage(
        passage_id="courage_monument",
        text="You step toward the monument carved with symbols of fire and forward motion. "
             "As you approach, the bioluminescent glow intensifies, and you feel a sudden "
             "weight—the accumulated fear of a civilization that lost its way.\n\n"
             "[Wisdom check DC 12]\n\n"
             "SUCCESS: The weight passes through you. You stand firm. The monument glows "
             "brightly, and a fragment of memory floods your mind: scenes of a city where "
             "people moved forward with purpose, unafraid.\n\n"
             "You gain a Glyph of Courage and understand a piece of what the city was.\n\n"
             "FAILURE: The weight overwhelms you. You stumble back, gasping. The monument's "
             "light dims. You feel something valuable slip away.",
        background="monuments",
        tags=["monument", "challenge"],
        glyph_rewards=["Courage"],
        tone_effects_on_enter={"courage": 0.05}
    )
    
    story.add_choice(
        from_passage_id="courage_monument",
        text="Return to the Keeper",
        target_id="keeper_aftermath",
        tone_effects={"resolve": 0.1}
    )
    
    story.add_choice(
        from_passage_id="courage_monument",
        text="Continue exploring",
        target_id="market_alone"
    )
    
    # ========== MONUMENT: WISDOM ==========
    story.add_passage(
        passage_id="wisdom_monument",
        text="You step toward the monument carved with scrolls and stars. Its light is "
             "softer than the others, more inviting.\n\n"
             "[Wisdom check DC 12]\n\n"
             "SUCCESS: As you approach, clarity washes over you. The monument's light "
             "reveals symbols that suddenly make sense—a language of memory and meaning. "
             "You gain a Glyph of Wisdom and feel your understanding deepen.\n\n"
             "FAILURE: The symbols remain cryptic. You sense you're missing something "
             "important, but can't grasp what.",
        background="monuments",
        tags=["monument", "challenge"],
        glyph_rewards=["Wisdom"],
        tone_effects_on_enter={"wisdom": 0.05}
    )
    
    story.add_choice(
        from_passage_id="wisdom_monument",
        text="Return to the Keeper",
        target_id="keeper_aftermath",
        tone_effects={"resolve": 0.1}
    )
    
    story.add_choice(
        from_passage_id="wisdom_monument",
        text="Continue exploring",
        target_id="market_alone"
    )
    
    # ========== MONUMENT: EMPATHY ==========
    story.add_passage(
        passage_id="empathy_monument",
        text="You step toward the monument carved with intertwined figures and circles. "
             "Its light pulses like a heartbeat.\n\n"
             "[Empathy check DC 11]\n\n"
             "SUCCESS: As you approach, you feel the connections between all things—not "
             "as abstract knowledge, but as lived experience. The monument glows warmly, "
             "and you gain a Glyph of Empathy.\n\n"
             "FAILURE: The pulse feels overwhelming, and you have to step back. You sense "
             "something profound, but can't quite reach it.",
        background="monuments",
        tags=["monument", "challenge"],
        glyph_rewards=["Empathy"],
        tone_effects_on_enter={"empathy": 0.05}
    )
    
    story.add_choice(
        from_passage_id="empathy_monument",
        text="Return to the Keeper",
        target_id="keeper_aftermath",
        tone_effects={"resolve": 0.1}
    )
    
    story.add_choice(
        from_passage_id="empathy_monument",
        text="Continue exploring",
        target_id="market_alone"
    )
    
    # ========== MONUMENT: UNKNOWN ==========
    story.add_passage(
        passage_id="unknown_monument",
        text="The fourth monument has no clear symbols—just abstract forms that seem to "
             "shift when you look directly at them.\n\n"
             "[Resolve check DC 13]\n\n"
             "SUCCESS: You stand before it without flinching, and the forms coalesce into "
             "meaning—not one emotion, but the space between them. The glyph you receive is "
             "unlike the others, seeming to contain multitudes.\n\n"
             "FAILURE: The monument resists you. Its shifting forms feel threatening, and "
             "you pull back before understanding what it means.",
        background="monuments",
        tags=["monument", "challenge", "mysterious"],
        glyph_rewards=["Resolve"],
        tone_effects_on_enter={"resolve": -0.1}
    )
    
    story.add_choice(
        from_passage_id="unknown_monument",
        text="Return to the Keeper",
        target_id="keeper_aftermath",
        tone_effects={"resolve": 0.15}
    )
    
    story.add_choice(
        from_passage_id="unknown_monument",
        text="Continue exploring",
        target_id="market_alone"
    )
    
    # ========== KEEPER GLYPHS INFO ==========
    story.add_passage(
        passage_id="keeper_glyphs",
        text="The Keeper leans in, their voice becoming almost reverent.\n\n"
             "'Glyphs are echoes of truth,' they say. 'When our civilization was whole, "
             "we encoded our deepest values—Courage, Wisdom, Empathy, Resolve—into "
             "symbols that we could touch, feel, internalize. They were like compasses "
             "for the soul.\n\n"
             "When everything collapsed, the glyphs remained. Scattered. Waiting for "
             "someone like you to gather them again.\n\n"
             "Each glyph you collect will strengthen you—not in body, but in resonance. "
             "You'll hear the Tone more clearly. You'll understand what needs to be healed.'\n\n"
             "The Keeper steps toward you. 'But be warned: gathering glyphs requires "
             "vulnerability. You must face the memories they hold. Not everyone can "
             "bear that.'",
        background="market_ruins",
        npc="Keeper",
        tags=["lore", "glyphs"]
    )
    
    story.add_choice(
        from_passage_id="keeper_glyphs",
        text="Ask if the Keeper has glyphs",
        target_id="keeper_has_glyphs",
        tone_effects={"wisdom": 0.1},
        npc_resonance={"Keeper": 0.15}
    )
    
    story.add_choice(
        from_passage_id="keeper_glyphs",
        text="Ask about the danger",
        target_id="keeper_danger",
        tone_effects={"courage": -0.05, "wisdom": 0.1}
    )
    
    story.add_choice(
        from_passage_id="keeper_glyphs",
        text="Express your determination",
        target_id="market_alone",
        tone_effects={"courage": 0.15},
        npc_resonance={"Keeper": 0.25}
    )
    
    # ========== KEEPER HAS GLYPHS ==========
    story.add_passage(
        passage_id="keeper_has_glyphs",
        text="The Keeper nods slowly. 'I was wondering when you'd ask.'\n\n"
             "They lead you to a small, hidden chamber beneath an old market stall. Inside, "
             "carefully arranged on shelves carved from stone, are dozens of glyphs—each "
             "glowing with faint luminescence.\n\n"
             "'I've been collecting these for decades,' the Keeper says. 'Preserving them. "
             "But they were never meant to be hoarded. They need to be carried, integrated "
             "into the living world again. Spread across Saonyx by someone with the strength "
             "to understand them.'\n\n"
             "The Keeper selects four from the shelves—one each of Courage, Wisdom, Empathy, "
             "and Resolve.\n\n"
             "'Start with these. Prove yourself, and the others will reveal themselves.'",
        background="keeper_sanctuary",
        npc="Keeper",
        tags=["gift", "glyphs"],
        glyph_rewards=["Courage", "Wisdom", "Empathy", "Resolve"]
    )
    
    story.add_choice(
        from_passage_id="keeper_has_glyphs",
        text="Accept and ask for guidance",
        target_id="keeper_guidance",
        tone_effects={"wisdom": 0.1},
        npc_resonance={"Keeper": 0.3},
        mark_story_beat="received_first_glyphs"
    )
    
    story.add_choice(
        from_passage_id="keeper_has_glyphs",
        text="Ask about the cost of carrying them",
        target_id="glyph_cost",
        tone_effects={"wisdom": 0.05}
    )
    
    # ========== MARKET EXPLORATION ==========
    story.add_passage(
        passage_id="market_exploration",
        text="You decide to explore the Market District on your own, mapping the ruins "
             "and looking for clues about what Saonyx once was.\n\n"
             "As you wander, you notice several paths:\n"
             "- A collapsed building with flickering lights inside (Archive?)\n"
             "- Stairs descending into darkness (Underground?)\n"
             "- A bridge spanning a ravine (Bridge District?)\n\n"
             "The Keeper's voice calls after you: 'Be careful. Not all memories are kind.'",
        background="market_ruins",
        tags=["exploration", "choice"]
    )
    
    story.add_choice(
        from_passage_id="market_exploration",
        text="Investigate the Archive",
        target_id="archive_entrance",
        tone_effects={"wisdom": 0.1}
    )
    
    story.add_choice(
        from_passage_id="market_exploration",
        text="Descend into the Underground",
        target_id="underground_entrance",
        tone_effects={"courage": 0.05}
    )
    
    story.add_choice(
        from_passage_id="market_exploration",
        text="Cross the Bridge",
        target_id="bridge_crossing",
        tone_effects={"resolve": 0.1}
    )
    
    story.add_choice(
        from_passage_id="market_exploration",
        text="Return to the Keeper",
        target_id="keeper_dialogue_1",
        tone_effects={"wisdom": 0.05}
    )
    
    # ========== MARKET ALONE ==========
    story.add_passage(
        passage_id="market_alone",
        text="You venture deeper into the Market District, determined to forge your own path. "
             "The ruins spread before you like a skeleton of what once was—vendor stalls "
             "hinting at the commerce, culture, and connection that once flowed here.\n\n"
             "The weight of the city's silence settles on your shoulders as you walk.",
        background="market_ruins",
        tags=["exploration"]
    )
    
    story.add_choice(
        from_passage_id="market_alone",
        text="Search for the Archive",
        target_id="archive_entrance",
        tone_effects={"wisdom": 0.1}
    )
    
    story.add_choice(
        from_passage_id="market_alone",
        text="Find the Underground entrance",
        target_id="underground_entrance",
        tone_effects={"courage": 0.05}
    )
    
    story.add_choice(
        from_passage_id="market_alone",
        text="Head toward the Bridge",
        target_id="bridge_crossing",
        tone_effects={"resolve": 0.1}
    )
    
    # ========== PLACEHOLDER ENDINGS ==========
    story.add_passage(
        passage_id="archive_entrance",
        text="You approach the collapsed building. A figure emerges from the shadows—younger "
             "than the Keeper, with ink-stained fingers and eyes that gleam with intellectual "
             "hunger.\n\n"
             "'The Archive,' they say, introducing themselves as the Archivist. 'Or what's "
             "left of it. Welcome. I suspect you're here for the same reason we all are: "
             "to remember.'\n\n"
             "[Story continues with Archivist questline...]",
        background="archive_ruins",
        npc="Archivist",
        tags=["archive", "ending"]
    )
    
    story.add_choice(
        from_passage_id="archive_entrance",
        text="Speak with the Archivist",
        target_id="archivist_dialogue"
    )
    
    # ========== UNDERGROUND ==========
    story.add_passage(
        passage_id="underground_entrance",
        text="The stairs descend into darkness. Your footsteps echo off tile and stone, "
             "suggesting vast, empty chambers below. The bioluminescent fungi glow brighter "
             "here—as if thriving in the absence of direct sunlight.\n\n"
             "You emerge into a sprawling underground city—tunnels, plazas, infrastructure "
             "that kept the surface city alive.\n\n"
             "[Story continues with Underground questline...]",
        background="underground_ruins",
        tags=["underground", "ending"]
    )
    
    story.add_choice(
        from_passage_id="underground_entrance",
        text="Explore the tunnels",
        target_id="underground_exploration"
    )
    
    # ========== BRIDGE ==========
    story.add_passage(
        passage_id="bridge_crossing",
        text="The bridge stretches across a ravine filled with mist and bioluminescent plants. "
             "It's built from stone and ancient metal, surprisingly sturdy despite neglect.\n\n"
             "A figure stands at the midpoint—a sentinel of some kind, neither approaching "
             "nor fleeing.\n\n"
             "'I've been waiting for a crosser,' they say. 'The bridge doesn't let just "
             "anyone pass. Who are you, and what brings you to the other side?'\n\n"
             "[Story continues with Bridge questline...]",
        background="bridge_ravine",
        npc="Bridge Sentinel",
        tags=["bridge", "ending"]
    )
    
    story.add_choice(
        from_passage_id="bridge_crossing",
        text="Speak with the Sentinel",
        target_id="sentinel_dialogue"
    )
    
    # ========== KEEPER AFTERMATH ==========
    story.add_passage(
        passage_id="keeper_aftermath",
        text="You return to the Keeper, changed by your encounter with the monuments.\n\n"
             "'You've taken your first true step,' they say, studying you carefully. 'The Tone "
             "recognizes you now. That will open doors... and create enemies. But that is the "
             "path of one who gathers glyphs.'\n\n"
             "The Keeper smiles. 'What comes next is up to you.'",
        background="market_ruins",
        npc="Keeper",
        tags=["checkpoint", "reflection"]
    )
    
    story.add_choice(
        from_passage_id="keeper_aftermath",
        text="Ask about other locations",
        target_id="keeper_locations"
    )
    
    story.add_choice(
        from_passage_id="keeper_aftermath",
        text="Continue exploring on your own",
        target_id="market_alone"
    )
    
    # ========== PLACEHOLDER CONTINUATIONS ==========
    story.add_passage(
        passage_id="keeper_wary",
        text="You stand at a careful distance, studying the Keeper before approaching. "
             "From your vantage point, you notice details: the Keeper glancing nervously "
             "at a doorway, a slight tension in their shoulders.\n\n"
             "After a moment, the Keeper turns directly toward you. 'Careful ones often "
             "last longer in the Remnants. Come—let's talk.' They seem relieved that you "
             "approached on your own terms.",
        background="market_ruins",
        npc="Keeper",
        tags=["dialogue"]
    )
    
    story.add_choice(
        from_passage_id="keeper_wary",
        text="Approach now",
        target_id="keeper_dialogue_1",
        tone_effects={"courage": 0.05},
        npc_resonance={"Keeper": 0.25}
    )
    
    story.add_passage(
        passage_id="keeper_guidance",
        text="The Keeper gestures toward the Market District. 'My role is different now. "
             "I watch, preserve, and guide those who arrive. But you—you must be the one "
             "to carry the glyphs forward, to spread the Tone across Saonyx.\n\n"
             "'That means traveling, meeting others, facing challenges. The glyphs will "
             "change you and those around you. Use that power wisely.'",
        background="keeper_sanctuary",
        npc="Keeper",
        tags=["guidance", "checkpoint"]
    )
    
    story.add_choice(
        from_passage_id="keeper_guidance",
        text="Set out into the world",
        target_id="market_alone",
        tone_effects={"courage": 0.1},
        mark_story_beat="began_glyph_quest"
    )
    
    story.add_passage(
        passage_id="keeper_danger",
        text="The Keeper's expression grows serious. 'There are those who fear the glyphs. "
             "In the city's final days, not everyone agreed on what the Tone should be. "
             "Some wanted power, others wanted connection. That conflict... it led to "
             "the Fall.\n\n"
             "'Those same factions might still exist in the Remnants. If they learn you "
             "carry glyphs, you could become a target. Or an ally. Either way, you won't "
             "remain unknown.'",
        background="market_ruins",
        npc="Keeper",
        tags=["lore", "warning"]
    )
    
    story.add_choice(
        from_passage_id="keeper_danger",
        text="Accept the risk",
        target_id="market_alone",
        tone_effects={"courage": 0.15},
        npc_resonance={"Keeper": 0.15}
    )
    
    story.add_passage(
        passage_id="glyph_cost",
        text="The Keeper hands you the glyphs, and their weight is immediate—not physical, "
             "but spiritual. You feel them humming in your hands, resonating with something "
             "deep inside you.\n\n"
             "'The cost,' the Keeper says quietly, 'is that you'll start to hear the Tone. "
             "Always. It will become part of you. Some find that beautiful. Others find it "
             "unbearable. There's no going back once you've accepted them.'",
        background="keeper_sanctuary",
        npc="Keeper",
        tags=["ritual"]
    )
    
    story.add_choice(
        from_passage_id="glyph_cost",
        text="Accept the glyphs despite the cost",
        target_id="keeper_guidance",
        tone_effects={"resolve": 0.2},
        npc_resonance={"Keeper": 0.2},
        mark_story_beat="accepted_glyphs"
    )
    
    story.add_passage(
        passage_id="keeper_locations",
        text="The Keeper nods. 'Saonyx is vast, and most of it remains unexplored. "
             "The Archive to the north holds the city's records. The Underground was always "
             "hidden—we think the surviving administration retreated there. And the Bridge "
             "to the east leads to territories we've lost contact with entirely.\n\n"
             "'Each has its own dangers and opportunities. Each will teach you something "
             "different about what we were... and what we might become.'",
        background="market_ruins",
        npc="Keeper",
        tags=["guidance"]
    )
    
    story.add_choice(
        from_passage_id="keeper_locations",
        text="Head to the Archive",
        target_id="archive_entrance",
        tone_effects={"wisdom": 0.1}
    )
    
    story.add_choice(
        from_passage_id="keeper_locations",
        text="Explore the Underground",
        target_id="underground_entrance",
        tone_effects={"courage": 0.05}
    )
    
    story.add_choice(
        from_passage_id="keeper_locations",
        text="Cross the Bridge",
        target_id="bridge_crossing",
        tone_effects={"resolve": 0.1}
    )
    
    story.add_passage(
        passage_id="archivist_dialogue",
        text="The Archivist's eyes widen as they study you. 'You carry glyphs. The old ones. "
             "Where did you find them?'\n\n"
             "'The Keeper,' you say.\n\n"
             "'Ah. Then you're trusted. Good. We need people who carry memory forward. "
             "Come—let me show you what we've preserved.'",
        background="archive_ruins",
        npc="Archivist",
        tags=["dialogue", "continuation"]
    )
    
    story.add_passage(
        passage_id="underground_exploration",
        text="You venture deeper into the Underground, exploring the vast chamber system. "
             "What you find is surprising: signs of habitation. Structures maintained. Water "
             "flowing. Evidence that life continues in the dark.\n\n"
             "A voice calls out from the shadows: 'Who enters the Deep City?'",
        background="underground_ruins",
        tags=["exploration", "continuation"]
    )
    
    story.add_passage(
        passage_id="sentinel_dialogue",
        text="The Sentinel studies you with ancient eyes. 'A glyph-bearer. I haven't seen "
             "one in decades. The Tone has chosen you—or the glyphs have chosen you. Either "
             "way, you may pass.\n\n"
             "'Beyond the bridge lies what remains of the Eastern Territories. Different "
             "cultures. Different memories. Different interpretations of the Tone. They will "
             "test you.'",
        background="bridge_ravine",
        npc="Bridge Sentinel",
        tags=["dialogue", "continuation"]
    )
    
    # ========== EXPORT TO JSON ==========
    # Export to the proper location
    export_path = "d:/saoriverse-console/velinor/stories/sample_story.json"
    story.export_json(export_path)
    
    print(f"Sample story created at: {export_path}")
    
    # Validate the story
    errors = story.validate()
    if errors:
        print("Validation warnings:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Story validated successfully!")
    
    return story


if __name__ == "__main__":
    build_velinor_sample_story()
"""
Sample Velinor Story - Clean Implementation
=============================================

This module demonstrates how to build a Velinor story using the StoryBuilder API.

Features:
- Passages with separate fields (id, text, background, npc)
- Choices with tone effects, NPC resonance, and dice checks
- Proper Velinor JSON export (no Twine markup)
- Integration with Emotional OS (tone_effects, npc_resonance)

Stories are exported as Velinor-native JSON format, compatible with StorySession.
"""

from velinor.story.story_builder import StoryBuilder


def build_velinor_sample_story():
    """Build a sample story scaffold for Velinor using clean API."""
    
    story = StoryBuilder(
        "Velinor: Remnants of the Tone - Sample",
        author="Saoriverse Team",
        region="Marketplace"
    )
    
    # ========== OPENING SCENE ==========
    # Market District - First encounter
    story.add_passage(
        passage_id="market_entry",
        text="You emerge from the collapsed underpass into what was once the Market "
             "District of Saonyx. Crumbling vendor stalls line the plaza, worn by time "
             "and weather. Vines creep up shattered windows, and bioluminescent fungi "
             "cast a faint glow on the stone.\n\n"
             "A figure approaches from the shadows—an older person with weathered skin "
             "and eyes that seem to recognize something in you.\n\n"
             "'Welcome to the Remnants,' they say. 'I am called the Keeper. You carry "
             "the weight of choice in you. The Tone pulses faintly here still, waiting "
             "for those who listen.'",
        background="market_ruins",
        npc="Keeper",
        tags=["intro", "market", "opening"],
        is_start=True
    )
    
    # Choice 1: Approach directly (increases courage)
    story.add_choice(
        from_passage_id="market_entry",
        text="Approach the Keeper and ask about the Tone",
        target_id="keeper_dialogue_1",
        tone_effects={"courage": 0.1},
        npc_resonance={"Keeper": 0.2}
    )
    
    # Choice 2: Explore first (increases wisdom)
    story.add_choice(
        from_passage_id="market_entry",
        text="Explore the Market District before speaking",
        target_id="market_exploration",
        tone_effects={"wisdom": 0.1}
    )
    
    # Choice 3: Stay cautious (requires wisdom check)
    story.add_choice(
        from_passage_id="market_entry",
        text="Keep your distance and observe",
        target_id="keeper_wary",
        dice_check={"stat": "wisdom", "dc": 11},
        tone_effects={"resolve": 0.05}
    )
    
    # ========== KEEPER DIALOGUE PATH ==========
    keeper_dialogue = story.add_passage(
        name="keeper_dialogue_1",
        text="""
{npc: Keeper}

The Keeper's eyes soften as you approach.

"I've been waiting for someone like you," they say. "The city remembers things 
we've forgotten. The Tone—our collective voice, our shared resonance—it still 
echoes through these ruins. Most who come here don't know how to listen. But 
you... you carry glyphs within you."

They gesture to a nearby plaza where several stone monuments stand, half-buried 
in moss and soil.

"Those markers hold fragments of what we were. If you're brave enough to seek 
them out, you might begin to understand what was lost... and what can be recovered."
[[Ask the Keeper about the glyphs they mentioned->keeper_glyphs]]
"""
    )
    
    story.add_choice("keeper_dialogue_1", "Ask the Keeper to guide you", "keeper_guide")
    story.add_choice("keeper_dialogue_1", "Ask about the glyphs", "keeper_glyphs")
    story.add_choice("keeper_dialogue_1", "Explore alone", "market_alone")
    
    # ========== KEEPER GUIDE PATH ==========
    keeper_guide = story.add_passage(
        name="keeper_guide",
        text="""
{npc: Keeper}
{background: monuments}

The Keeper leads you deeper into the Market District, their footsteps echoing 
softly on the cracked stone. The monuments draw closer—ancient pillars inscribed 
with symbols that seem to shift and breathe in the bioluminescent light.

"These were gathering places," the Keeper explains. "Where the citizens would 
come to speak, to share their burdens, their joys. The Tone was strongest here. 
Listen carefully..."

You hear it—a faint resonance, like the echo of thousands of voices speaking in 
unison, now fractured and distant.

"The first monument holds a memory of Courage," says the Keeper, pointing. 
"The second, Wisdom. The third, Empathy. And the fourth... that one holds 
something I've never understood. Not all emotions have names."

The Keeper steps back. "Choose one to approach. It will test you."
[[Approach the Wisdom monument (Wisdom check, DC 12)->wisdom_monument]]
[[Approach the unnamed fourth monument (Resolve check, DC 13)->unknown_monument]]
"""
    )
    
    story.add_choice("keeper_guide", "Test Courage", "courage_monument")
    story.add_choice("keeper_guide", "Test Wisdom", "wisdom_monument")
    story.add_choice("keeper_guide", "Test Empathy", "empathy_monument")
    story.add_choice("keeper_guide", "Test the unknown", "unknown_monument")
    
    # ========== MONUMENT PATHS (Skill Checks) ==========
    courage_monument = story.add_passage(
        name="courage_monument",
        text="""
{dice: d20+courage}

You step toward the monument carved with symbols of fire and forward motion. 
As you approach, the bioluminescent glow intensifies, and you feel a sudden 
weight—the accumulated fear of a civilization that lost its way.

[Rolling d20 + Courage modifier...]

**Success Path:**
The weight passes through you. You stand firm. The monument glows brightly, 
and a fragment of memory floods your mind: scenes of a city where people moved 
forward with purpose, unafraid.

You gain a Glyph of Courage: +5 to future Courage checks.

**Failure Path:**
The weight overwhelms you. You stumble back, gasping. The monument's light 
dims. You feel something valuable slip away—a moment lost.
"""
    )
    
    # ========== KEEPER GLYPHS INFO ==========
    keeper_glyphs = story.add_passage(
        name="keeper_glyphs",
        text="""
{npc: Keeper}

The Keeper leans in, their voice becoming almost reverent.

"Glyphs are echoes of truth," they say. "When our civilization was whole, 
we encoded our deepest values—Courage, Wisdom, Empathy, Resolve—into symbols 
that we could touch, feel, internalize. They were like compasses for the soul.

When everything collapsed, the glyphs remained. Scattered. Waiting for someone 
like you to gather them again.

Each glyph you collect will strengthen you—not in body, but in resonance. 
You'll hear the Tone more clearly. You'll understand what needs to be healed."

The Keeper steps toward you.

"But be warned: gathering glyphs requires vulnerability. You must face the 
memories they hold. Not everyone can bear that."
[[Express your determination->market_alone]]
"""
    )
    
    story.add_choice("keeper_glyphs", "Ask if the Keeper has glyphs", "keeper_has_glyphs")
    story.add_choice("keeper_glyphs", "Express determination", "market_alone")
    story.add_choice("keeper_glyphs", "Ask about danger", "keeper_danger")
    
    # ========== KEEPER HAS GLYPHS ==========
    keeper_has_glyphs = story.add_passage(
        name="keeper_has_glyphs",
        text="""
{npc: Keeper}
{background: keeper_sanctuary}

The Keeper nods slowly. "I was wondering when you'd ask."

They lead you to a small, hidden chamber beneath one of the older market stalls. 
Inside, carefully arranged on shelves carved from the old stone, are dozens of 
glyphs—each glowing with its own faint luminescence.

"I've been collecting these for decades," the Keeper says. "Preserving them. 
But they were never meant to be hoarded. They need to be carried, integrated 
into the living world again. Spread across Saonyx by someone with the strength 
to understand them."

The Keeper selects four from the shelves—one each of Courage, Wisdom, Empathy, 
and Resolve.

"Start with these. Prove yourself, and the others will reveal themselves."

You receive: Glyph of Courage, Glyph of Wisdom, Glyph of Empathy, Glyph of Resolve
[[Ask about the costs of carrying glyphs->glyph_cost]]
"""
    )
    
    story.add_choice("keeper_has_glyphs", "Accept and ask for guidance", "keeper_guidance")
    story.add_choice("keeper_has_glyphs", "Ask about the cost", "glyph_cost")
    
    # ========== MARKET ALONE PATH ==========
    market_alone = story.add_passage(
        name="market_alone",
        text="""
{background: market_ruins}

You thank the Keeper and turn toward the deeper Market District, determined 
to forge your own path through the ruins.

The Market District spreads before you like a skeleton of what it once was. 
Stalls of different sizes hint at the commerce that once flowed here—food, 
goods, stories traded between people.

You notice several paths ahead:
- A collapsed building with flickering lights inside (Archive?)
- Stairs descending into darkness (Underground?)
- A bridge spanning what looks like a ravine (Bridge District?)

The Keeper's voice calls after you: "Be careful. Not all memories are kind."

Which path calls to you?
[[Descend the stairs->underground_entrance]]
"""
    )
    
    story.add_choice("market_alone", "Archive", "archive_entrance")
    story.add_choice("market_alone", "Underground", "underground_entrance")
    story.add_choice("market_alone", "Bridge", "bridge_crossing")
    
    # ========== PLACEHOLDER ENDINGS ==========
    archive_entrance = story.add_passage(
        name="archive_entrance",
        text="""
{background: archive_ruins}
{npc: Archivist}

You approach the collapsed building. A figure emerges from the shadows—
younger than the Keeper, with ink-stained fingers and eyes that gleam with 
intellectual hunger.

"The Archive," they say, introducing themselves as the Archivist. "Or what's 
left of it. Welcome. I suspect you're here for the same reason we all are: 
to remember."

[Story continues with Archivist questline...]
"""
    )
    
    underground_entrance = story.add_passage(
        name="underground_entrance",
        text="""
{background: underground_ruins}
{npc: Tunnel}

The stairs descend into darkness. Your footsteps echo off tile and stone, 
suggesting vast, empty chambers below. The bioluminescent fungi here glow 
brighter—as if thriving in the absence of direct sunlight.

You emerge into a sprawling underground city—tunnels, plazas, infrastructure 
that kept the surface city alive.

[Story continues with Underground questline...]
"""
    )
    
    bridge_crossing = story.add_passage(
        name="bridge_crossing",
        text="""
{background: bridge_ravine}
{npc: Bridge Sentinel}

The bridge stretches across a ravine filled with mist and bioluminescent plants. 
It's built from stone and ancient metal, surprisingly sturdy despite years of 
neglect.

A figure stands at the midpoint—a sentinel of some kind, neither approaching 
nor fleeing.

"I've been waiting for a crosser," they say. "The bridge doesn't let just 
anyone pass. Who are you, and what brings you to the other side?"

[Story continues with Bridge questline...]
"""
    )
    
    # ========== AFTERMATH CHECKPOINT ==========
    keeper_aftermath = story.add_passage(
        name="keeper_aftermath",
        text="""
{npc: Keeper}
{background: market_ruins}

You return to the Keeper, changed by your encounter at the monument.

"You've taken your first true step," they say, studying you carefully. 
"The Tone recognizes you now. That will open doors... and create enemies."

What comes next?
[[Ask about other locations in Saonyx->saonyx_map]]
"""
    )
    
    # Export to JSON
    story.export_json('/Volumes/My Passport for Mac/saoriverse-console/velinor/stories/sample_story.json')
    
    print("Sample story scaffold created at: velinor/stories/sample_story.json")
    return story


if __name__ == "__main__":
    build_velinor_sample_story()
