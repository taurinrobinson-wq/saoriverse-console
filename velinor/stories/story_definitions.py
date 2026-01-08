"""
Velinor Story Definitions
========================

This is where you define the story structure. Edit this file directly.
You can write it like prose, organized by acts and scenes.

To regenerate JSON:
    python build_story.py

To validate:
    python validate_story.py
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import velinor
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from velinor.engine.twine_adapter import StoryBuilder


def build_velinor_story():
    """Build Velinor: Remnants of the Tone story from structured Python."""
    
    story = StoryBuilder("Velinor: Remnants of the Tone")
    
    # ========================================
    # ACT 1: MARKETPLACE AWAKENING
    # ========================================
    
    # Scene: Market Arrival
    story.add_passage(
        name="market_arrival",
        text="""*They're staring at me. What should I do?*""",
        background="market_ruins",
        npcs=["Ravi", "Nima"],
        is_start=True,
        tags=["marketplace", "act1"]
    )
    
    # First choice node - sets initial TONE baseline
    story.add_choice(
        from_passage_name="market_arrival",
        choice_text="Step toward the figures",
        to_passage_name="meet_ravi_nima",
        tone_effects={"courage": 0.2, "narrative_presence": 0.15},
        npc_resonance={"Ravi": 0.1, "Nima": -0.1}
    )
    story.add_choice(
        from_passage_name="market_arrival",
        choice_text="Retreat toward the underpass (safer)",
        to_passage_name="meet_ravi_nima",
        tone_effects={"wisdom": 0.2, "courage": -0.1},
        npc_resonance={"Ravi": -0.1, "Nima": 0.15}
    )
    story.add_choice(
        from_passage_name="market_arrival",
        choice_text="Call out to them",
        to_passage_name="meet_ravi_nima",
        tone_effects={"empathy": 0.15, "narrative_presence": 0.1},
        npc_resonance={"Ravi": 0.15, "Nima": 0.05}
    )
    story.add_choice(
        from_passage_name="market_arrival",
        choice_text="Stay still and observe",
        to_passage_name="meet_ravi_nima",
        tone_effects={"observation": 0.2, "wisdom": 0.1},
        npc_resonance={"Ravi": 0.05, "Nima": 0.15}
    )
    
    # Scene: Meet Ravi & Nima
    story.add_passage(
        name="meet_ravi_nima",
        text="""The dust clears. Two figures emerge:

Ravi - tall, warm-eyed, with earth-toned robes and the bearing of someone who once led.
Nima - sharp-gazed, braided hair, layers of practical cloth. She watches you carefully.

"You carry something," Nima says, her voice like wind through ruins. "A resonance. We felt it."

Ravi steps forward, less cautious. "Welcome. The Market District doesn't often receive travelers anymore. What brings you here?\"""",
        background="market_ruins",
        npcs=["Ravi", "Nima"],
        tags=["marketplace", "act1", "npc_encounter"]
    )
    
    # Second choice node - relationship building
    story.add_choice(
        from_passage_name="meet_ravi_nima",
        choice_text="Step toward them openly",
        to_passage_name="ravi_dialogue",
        tone_effects={"courage": 0.15, "narrative_presence": 0.1},
        npc_resonance={"Ravi": 0.2, "Nima": -0.05}
    )
    story.add_choice(
        from_passage_name="meet_ravi_nima",
        choice_text="Keep distance and ask questions first",
        to_passage_name="nima_dialogue",
        tone_effects={"wisdom": 0.15, "observation": 0.1},
        npc_resonance={"Ravi": -0.05, "Nima": 0.2}
    )
    story.add_choice(
        from_passage_name="meet_ravi_nima",
        choice_text="Ask what they mean by 'resonance'",
        to_passage_name="ravi_nima_resonance",
        tone_effects={"empathy": 0.15, "observation": 0.15},
        npc_resonance={"Ravi": 0.1, "Nima": 0.1}
    )
    
    # Ravi path
    story.add_passage(
        name="ravi_dialogue",
        text="""You move toward Ravi. His expression softens.

"I've learned to recognize it," he says. "People who listen. People who feel the Tone beneath the silence."

He extends a weathered hand. "I'm Ravi. That's Nima—she's more careful than I am, but she's rarely wrong about people."

Nima nods slightly, a small gesture of acknowledgment.

"What's your name, traveler?\"""",
        background="market_ruins",
        npcs=["Ravi", "Nima"],
        tags=["marketplace", "act1", "ravi_relationship"]
    )
    
    story.add_choice(
        from_passage_name="ravi_dialogue",
        choice_text="Tell them your name",
        to_passage_name="established_in_market",
        tone_effects={"empathy": 0.1},
        npc_resonance={"Ravi": 0.15, "Nima": 0.1}
    )
    story.add_choice(
        from_passage_name="ravi_dialogue",
        choice_text="Ask them first who they were before the collapse",
        to_passage_name="ravi_backstory",
        tone_effects={"empathy": 0.2, "observation": 0.1},
        npc_resonance={"Ravi": 0.25, "Nima": 0.05}
    )
    
    # Nima path
    story.add_passage(
        name="nima_dialogue",
        text="""You take a step back, measuring them both. Nima notices. She respects caution.

"Wise," she says quietly. "Not everyone is."

She crosses her arms, not defensively—more like she's settled in for a real conversation.

"I'm Nima. We've been here longer than we should have been. Looking for something, though we're not always sure what."

Ravi adds, "The Market District used to be the heart of Velhara. Now it's just... ruins and waiting.\"""",
        background="market_ruins",
        npcs=["Ravi", "Nima"],
        tags=["marketplace", "act1", "nima_relationship"]
    )
    
    story.add_choice(
        from_passage_name="nima_dialogue",
        choice_text="Ask what they're looking for",
        to_passage_name="nima_quest_reveal",
        tone_effects={"empathy": 0.15},
        npc_resonance={"Ravi": 0.05, "Nima": 0.2}
    )
    story.add_choice(
        from_passage_name="nima_dialogue",
        choice_text="Ask about the resonance they mentioned",
        to_passage_name="ravi_nima_resonance",
        tone_effects={"observation": 0.15, "wisdom": 0.1},
        npc_resonance={"Ravi": 0.1, "Nima": 0.15}
    )
    
    # Shared resonance explanation
    story.add_passage(
        name="ravi_nima_resonance",
        text="""Ravi and Nima exchange a glance. Some unspoken agreement passes between them.

"The Tone," Ravi begins. "It was the name we gave to the emotional frequency that held the city together. Our collective voice, resonating across the Corelink system."

Nima continues, "Most people can't feel it anymore. The system broke. But some people... they carry an echo of it. You do."

"It means you can hear what others can't," Ravi says. "You can gather the glyphs. You might even understand what happened."

Nima adds, more cautiously: "It also means the city will know you're here. That brings attention.\"""",
        background="market_ruins",
        npcs=["Ravi", "Nima"],
        tags=["marketplace", "act1", "lore"]
    )
    
    story.add_choice(
        from_passage_name="ravi_nima_resonance",
        choice_text="Ask to learn more",
        to_passage_name="established_in_market",
        tone_effects={"observation": 0.1, "wisdom": 0.1},
        npc_resonance={"Ravi": 0.1, "Nima": 0.1}
    )
    story.add_choice(
        from_passage_name="ravi_nima_resonance",
        choice_text="Ask what kind of attention",
        to_passage_name="nima_warning",
        tone_effects={"wisdom": 0.15, "observation": 0.15},
        npc_resonance={"Ravi": 0.05, "Nima": 0.2}
    )
    
    # Warning path
    story.add_passage(
        name="nima_warning",
        text="""Nima's jaw tightens slightly.

"There are others who hear the Tone. Most have... different ideas about what should happen next. Some want to restore the system. Others want to destroy what's left of it. And some..." she pauses, "...some want to use it."

Ravi adds quietly, "Kaelen is one of them. A thief, or so they call him. He's been taking things from people—tools, fragments, things that might be glyphs."

"He won't touch you if you can prove you're useful to him," Nima says. "But he's watching everyone new.\"""",
        background="market_ruins",
        npcs=["Ravi", "Nima"],
        tags=["marketplace", "act1", "threat"]
    )
    
    story.add_choice(
        from_passage_name="nima_warning",
        choice_text="Ask where you can find Kaelen",
        to_passage_name="kaelen_location",
        tone_effects={"courage": 0.1, "narrative_presence": 0.15},
        npc_resonance={"Ravi": -0.1, "Nima": -0.05}
    )
    story.add_choice(
        from_passage_name="nima_warning",
        choice_text="Ask if Ravi and Nima can help you",
        to_passage_name="established_in_market",
        tone_effects={"empathy": 0.15},
        npc_resonance={"Ravi": 0.15, "Nima": 0.15}
    )
    
    # Kaelen location
    story.add_passage(
        name="kaelen_location",
        text="""Nima says, "The Thieves' Cache. An old underground market. We can show you the way, but you should know: going there is a choice. Once Kaelen knows you're interested, you become part of his game."

Ravi nods slowly. "We can guide you if you want. Or we can help you prepare first."

The choice hangs in the market air between you.""",
        background="market_ruins",
        npcs=["Ravi", "Nima"],
        tags=["marketplace", "act1", "quest_fork"]
    )
    
    story.add_choice(
        from_passage_name="kaelen_location",
        choice_text="Go to the Thieves' Cache now",
        to_passage_name="thieves_cache_entrance",
        tone_effects={"courage": 0.2, "narrative_presence": 0.15},
        npc_resonance={"Ravi": -0.15, "Nima": -0.1}
    )
    story.add_choice(
        from_passage_name="kaelen_location",
        choice_text="Ask Ravi and Nima to help you prepare",
        to_passage_name="market_preparation",
        tone_effects={"wisdom": 0.2},
        npc_resonance={"Ravi": 0.2, "Nima": 0.2}
    )
    
    # Established in market (neutral path)
    story.add_passage(
        name="established_in_market",
        text="""Whether you told them your name or shared stories, something shifts. You're no longer just a stranger.

Ravi says, "The Market District isn't safe to explore alone. But if you travel with us, or if we can vouch for you, others will be more welcoming."

"There are shrines deeper in," Nima adds. "Places where people gather. And there are chambers—old Corelink hubs that have been sealed. We think there are glyphs there."

"For now," Ravi concludes, "you should rest. There's a shelter we know. Tomorrow, you can decide which path to take."

The day is ending. The bioluminescent fungi grow brighter as the sun sets beyond the ruins.""",
        background="market_ruins",
        npcs=["Ravi", "Nima"],
        tags=["marketplace", "act1", "rest"]
    )
    
    story.add_choice(
        from_passage_name="established_in_market",
        choice_text="Go to the shelter and rest",
        to_passage_name="marketplace_shelter",
        tone_effects={"empathy": 0.05},
        npc_resonance={"Ravi": 0.1, "Nima": 0.1}
    )
    story.add_choice(
        from_passage_name="established_in_market",
        choice_text="Ask to visit the shrines before nightfall",
        to_passage_name="shrine_visit_evening",
        tone_effects={"courage": 0.15, "observation": 0.1},
        npc_resonance={"Ravi": 0.15, "Nima": 0.1}
    )
    
    # Placeholder endings (to be expanded)
    story.add_passage(
        name="marketplace_shelter",
        text="""You rest in a sheltered corner of the Market District—an old merchant's vault, fortified and safe. Ravi and Nima leave you with water and dried fruit.

"Tomorrow," Ravi says, "we'll show you what comes next."

You rest, and in your dreams, you hear the faint echo of thousands of voices, layered and distant.

The Tone.

[END OF PROTOTYPE - Act 2 to follow]""",
        background="shelter_interior",
        npcs=["Ravi", "Nima"],
        tags=["marketplace", "act1", "ending"]
    )
    
    # More placeholder passages
    story.add_passage(
        name="shrine_visit_evening",
        text="""Ravi nods. "If you want to move before nightfall, we should go now."

The shrines await, deeper in the city...

[PLACEHOLDER: Shrine encounter - Saori appears if resonance is high enough]""",
        background="shrine_ruins",
        npcs=["Ravi"],
        tags=["marketplace", "act1", "shrine"]
    )
    
    story.add_passage(
        name="thieves_cache_entrance",
        text="""The path to the Thieves' Cache descends into older tunnels...

[PLACEHOLDER: Thieves' Cache - Kaelen encounter]""",
        background="thieves_cache",
        npcs=["Kaelen"],
        tags=["marketplace", "act1", "kaelen"]
    )
    
    story.add_passage(
        name="market_preparation",
        text="""Ravi and Nima lead you through the Market District, showing you the lay of the land...

[PLACEHOLDER: Market preparation - Learning from Ravi & Nima]""",
        background="market_ruins",
        npcs=["Ravi", "Nima"],
        tags=["marketplace", "act1", "prep"]
    )
    
    story.add_passage(
        name="nima_quest_reveal",
        text="""Nima's eyes distant.

"We're looking for the Corelink's heart. The system that connected everyone..." 

[PLACEHOLDER: Nima's quest - What they've been searching for]""",
        background="market_ruins",
        npcs=["Nima"],
        tags=["marketplace", "act1", "quest"]
    )
    
    story.add_passage(
        name="ravi_backstory",
        text="""Ravi settles, as if preparing for a long story.

"Before the collapse, I was a teacher in the Archive..." 

[PLACEHOLDER: Ravi's backstory - Before the collapse]""",
        background="market_ruins",
        npcs=["Ravi"],
        tags=["marketplace", "act1", "backstory"]
    )
    
    return story


if __name__ == "__main__":
    # Build and export
    velinor_story = build_velinor_story()
    velinor_story.export_json("velinor/stories/sample_story.json")
    print("[OK] Story exported to sample_story.json")
    
    # Export NPC REMNANTS state if REMNANTS is enabled
    if velinor_story.enable_remnants and velinor_story.npc_manager:
        # Simulate story choices to track NPC evolution
        simulation = velinor_story.simulate_npc_evolution()
        print(f"[OK] NPC evolution simulated: {simulation['total_choices']} choices, {simulation['npc_count']} NPCs")
        
        # Export NPC state
        velinor_story.export_npc_state("velinor/stories/npc_state.json")
        print("[OK] NPC state exported to npc_state.json")
