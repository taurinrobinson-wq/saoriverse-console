"""
Sample Velinor Story Scaffold
==============================

This module demonstrates how to build a Velinor story using the StoryBuilder,
with passages, choices, NPC interactions, and dice roll mechanics.

This can be exported to JSON and imported into Twine for visual editing,
or used directly as a programmatic story.
"""

from .twine_adapter import StoryBuilder


def build_velinor_sample_story():
    """Build a sample story scaffold for Velinor."""
    
    story = StoryBuilder("Velinor: Remnants of the Tone - Sample")
    
    # ========== OPENING SCENE ==========
    # Market District - First encounter
    market_opening = story.add_passage(
        name="market_entry",
        text="""
{background: market_ruins}
{npc: Keeper}

You emerge from the collapsed underpass into what was once the Market District 
of Saonyx. The air is thick with silence—not the silence of absence, but of 
waiting. Crumbling vendor stalls line the plaza, their surfaces worn by time 
and weather. Vines creep up shattered display windows, and bioluminescent fungi 
cast a faint glow on the stone.

A figure approaches from the shadows. It's an older person with weathered skin 
and eyes that seem to recognize something in you.

"Welcome to the Remnants," they say. "I am called the Keeper. You carry the 
weight of choice in you—I can feel it. The Tone pulses faintly here still, 
waiting for those who listen."

What do you do?
""",
        is_start=True
    )
    
    # Choice 1: Approach the Keeper directly
    story.add_choice(
        "market_entry",
        "Approach the Keeper and ask about the Tone",
        "keeper_dialogue_1"
    )
    
    # Choice 2: Explore the market first
    story.add_choice(
        "market_entry",
        "Explore the Market District before speaking to anyone",
        "market_exploration"
    )
    
    # Choice 3: Stay cautious
    story.add_choice(
        "market_entry",
        "Keep your distance and observe (Wisdom, DC 11)",
        "keeper_wary"
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

[[Ask the Keeper to guide you to the monuments->keeper_guide]]
[[Ask the Keeper about the glyphs they mentioned->keeper_glyphs]]
[[Thank them but insist on exploring alone->market_alone]]
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

[[Approach the Courage monument (Courage check, DC 12)->courage_monument]]
[[Approach the Wisdom monument (Wisdom check, DC 12)->wisdom_monument]]
[[Approach the Empathy monument (Empathy check, DC 12)->empathy_monument]]
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

[[Return to the Keeper->keeper_aftermath]]
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

[[Ask if the Keeper has glyphs->keeper_has_glyphs]]
[[Express your determination->market_alone]]
[[Ask about the danger->keeper_danger]]
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

[[Accept the glyphs and ask for guidance->keeper_guidance]]
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

[[Investigate the collapsed archive building->archive_entrance]]
[[Descend the stairs->underground_entrance]]
[[Cross the bridge->bridge_crossing]]
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

[[Continue->market_alone]]
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

[[Continue->market_alone]]
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

[[Continue->market_alone]]
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

[[Ask about the enemies->keeper_enemies]]
[[Ask about other locations in Saonyx->saonyx_map]]
[[Rest before continuing->rest_area]]
"""
    )
    
    # Export to JSON
    story.export_json('/Volumes/My Passport for Mac/saoriverse-console/velinor/stories/sample_story.json')
    
    print("Sample story scaffold created at: velinor/stories/sample_story.json")
    return story


if __name__ == "__main__":
    build_velinor_sample_story()
