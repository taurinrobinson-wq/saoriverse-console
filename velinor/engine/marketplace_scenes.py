"""Velinor Marketplace Scenes - Full Encounter Sequences

Implements the marketplace arrival sequence with trust-based NPC dynamics,
collapse mechanics, and first map appearance.
"""

from typing import List, Optional
from .scene_manager import SceneModule, SceneAssets, DialogueOption, SceneBuilder


class MarketplaceSceneSequence:
    """Container for all marketplace scenes and their progression."""
    
    @staticmethod
    def build_marketplace_intro() -> SceneModule:
        """Initial marketplace arrival - player is lost and encountering the city."""
        return SceneModule(
            scene_id="marketplace_intro_arrival",
            npc_name="Marketplace (Ambient)",
            npc_archetype="environment",
            
            narration_distant="""
You emerge from the fractured pathways into what was once a grand marketplace.
The air carries the smell of dust, rust, and smoke.
Around you, tents and makeshift stalls cluster together — survivors bartering
what little they've salvaged from the collapse.
            """.strip(),
            
            narration_close="""
You step deeper into the marketplace.
Eyes turn toward you — not aggressive, but cautious. You are clearly new here.
A few NPCs move away; others linger, assessing whether you're a threat or an opportunity.
            """.strip(),
            
            npc_dialogue="""
[The marketplace hums with quiet activity: haggling, footsteps, the clink of metal.]
[A wind shifts through broken structures, and you hear a distant chime.]
            """.strip(),
            
            assets=SceneAssets(
                background_distant="velinor/backgrounds/marketplace_intact_distant.png",
                background_close="velinor/backgrounds/marketplace_intact_close.png",
                foreground_distant=None,  # No specific NPC yet
                foreground_close=None,
            ),
            
            player_options=[],  # This is an intro scene, auto-advances
            
            glyph_distant=["Esḧ"],  # Sacred witness
            glyph_close=["Esḧ", "Querrä"],  # Sacred witness + inquiry
        )
    
    @staticmethod
    def build_npc_ravi_first_encounter() -> SceneModule:
        """First welcoming NPC - Ravi spots the player."""
        return SceneModule(
            scene_id="marketplace_ravi_discovery",
            npc_name="Ravi",
            npc_archetype="welcoming",
            
            narration_distant="""
You notice someone in the distance, partially obscured by a fabric stall.
He's arranging trade goods with care, checking each item twice.
When he looks up and sees you, something shifts in his expression.
            """.strip(),
            
            narration_close="""
He makes his way toward you with genuine warmth, though you notice
his gaze is careful, measuring. He sees the weight on you.
"Welcome to the marketplace. You're new here, I can tell."
            """.strip(),
            
            npc_dialogue="""
"I'd welcome you with open arms, but too many hands here have stolen lately."
"Still, I see something in you. You carry loss, but you're not here to take."
"My name is Ravi. What brings you to the city?"
            """.strip(),
            
            assets=SceneAssets(
                background_distant="velinor/backgrounds/marketplace_intact_distant.png",
                background_close="velinor/backgrounds/marketplace_intact_close.png",
                foreground_distant="velinor/backgrounds/ravi_distant.png",
                foreground_close="velinor/backgrounds/ravi_close.png",
            ),
            
            player_options=[
                DialogueOption(
                    text="I'm not here to steal. I'm here to listen.",
                    glyph_triggers=["Cinarä̈"],
                    npc_response="That's rare in these times. I think we can be friends. Come, I'll introduce you around.",
                    trust_modifier=0.25
                ),
                DialogueOption(
                    text="I lost someone. I had to leave my town.",
                    glyph_triggers=["Thalen̈"],
                    npc_response="Then you understand grief. Most of us here do. That common ground... it matters.",
                    trust_modifier=0.2
                ),
                DialogueOption(
                    text="Then let me earn your trust slowly.",
                    glyph_triggers=["Aelitḧ"],
                    npc_response="Patience. Wisdom. You might do well here after all.",
                    trust_modifier=0.15
                ),
            ],
            
            glyph_distant=["Esḧ"],
            glyph_close=["Cinarä̈", "Brethielï̈"],  # Invoked beloved, breath as guide
        )
    
    @staticmethod
    def build_npc_nima_first_encounter() -> SceneModule:
        """First mistrusting NPC - Nima the market guard."""
        return SceneModule(
            scene_id="marketplace_nima_discovery",
            npc_name="Nima",
            npc_archetype="mistrusting",
            
            narration_distant="""
You're studying the marketplace layout when a figure steps into your path.
She's smaller than you expected, but her posture communicates authority.
A worn dagger hangs at her hip. Her eyes narrow as she observes you.
            """.strip(),
            
            narration_close="""
"You. Stranger. I haven't seen you before."
Her voice is sharp, assessing. She's clearly someone important to the marketplace order.
She doesn't smile. She doesn't need to.
            """.strip(),
            
            npc_dialogue="""
"You're not from here. Outsiders are usually trouble."
"There's been theft, betrayal. The marketplace has been on edge."
"Give me a reason not to assume you're part of the problem."
            """.strip(),
            
            assets=SceneAssets(
                background_distant="velinor/backgrounds/marketplace_intact_distant.png",
                background_close="velinor/backgrounds/marketplace_intact_close.png",
                foreground_distant="velinor/backgrounds/nima_distant.png",
                foreground_close="velinor/backgrounds/nima_close.png",
            ),
            
            player_options=[
                DialogueOption(
                    text="I've lost too much to take more.",
                    glyph_triggers=["Thalen̈"],
                    npc_response="Loss. Yeah. I see that. Maybe you're not a thief. We'll see.",
                    trust_modifier=0.1
                ),
                DialogueOption(
                    text="I'll prove I can give back.",
                    glyph_triggers=["Querrä"],
                    npc_response="Words are cheap. Actions matter. Find something worth doing.",
                    trust_modifier=0.05
                ),
                DialogueOption(
                    text="Then don't trust me yet. Just watch.",
                    glyph_triggers=["Aelitḧ"],
                    npc_response="Respect for caution. That's something. We'll talk later.",
                    trust_modifier=0.15
                ),
            ],
            
            glyph_distant=["Querrä"],  # Inquiry
            glyph_close=["Querrä", "Ruuñ"],  # Inquiry + collapse (guardianship)
        )
    
    @staticmethod
    def build_collapse_event() -> SceneModule:
        """Major marketplace collapse event - dynamic environment change."""
        return SceneModule(
            scene_id="marketplace_collapse_event",
            npc_name="Marketplace (Collapse)",
            npc_archetype="environment",
            
            narration_distant="""
A deep rumble shakes the ground beneath your feet.
The sound is unlike anything you've heard since the cataclysm — 
a building in the distance begins to fall.
            """.strip(),
            
            narration_close="""
The collapse is sudden and terrifying.
Stone crashes into stone. Dust rises in clouds.
A path you could have walked closes forever.
            """.strip(),
            
            npc_dialogue="""
[The marketplace falls silent. Then, gradually, sounds return.]
[Some NPCs glance at the destruction. Most simply return to their bartering.]
[A red mark appears on the map in the sidebar where the collapse occurred.]
            """.strip(),
            
            assets=SceneAssets(
                background_distant="velinor/backgrounds/marketplace_intact_distant.png",
                background_close="velinor/backgrounds/marketplace_collapsed_close.png",  # Collapsed version
                foreground_distant=None,
                foreground_close=None,
            ),
            
            player_options=[
                DialogueOption(
                    text="What was that? Are you two okay!?",
                    glyph_triggers=["Thalen̈"],
                    npc_response="Looks like you really are new to the city. You get used to it. We barely notice it now.",
                    trust_modifier=0.0
                ),
                DialogueOption(
                    text="I'm surprised you didn't even flinch.",
                    glyph_triggers=["Querrä"],
                    npc_response="Another wall falls, another path closes. We've stopped counting.",
                    trust_modifier=0.05
                ),
                DialogueOption(
                    text="[Remain silent, observing]",
                    glyph_triggers=["Aelitḧ"],
                    npc_response="You're learning. The city teaches through silence.",
                    trust_modifier=0.1
                ),
            ],
            
            glyph_distant=["Ruuñ"],  # Collapse
            glyph_close=["Ruuñ", "Sha'rú"],  # Collapse + repair/adaptation
        )
    
    @staticmethod
    def build_map_introduction() -> SceneModule:
        """Scene where the map is first revealed to the player."""
        return SceneModule(
            scene_id="marketplace_map_reveal",
            npc_name="Ravi",
            npc_archetype="welcoming",
            
            narration_distant="""
After the collapse settles, Ravi approaches you with a worn cloth map.
The edges are tattered, marked with countless journey routes.
"You'll need to understand the layout if you're going to survive here."
            """.strip(),
            
            narration_close="""
He spreads the map on a nearby crate, pointing to various sectors.
"See here? The marketplace hub. The guard post. The shrine areas."
"And here," he marks a red X with his finger, "is where the collapse just happened."
            """.strip(),
            
            npc_dialogue="""
"The city changes constantly. What's open today might be blocked tomorrow."
"Keep track of your surroundings. The only constant here is change."
"This map will be your guide — mark it as you learn."
            """.strip(),
            
            assets=SceneAssets(
                background_distant="velinor/backgrounds/marketplace_collapsed_close.png",
                background_close="velinor/backgrounds/marketplace_collapsed_close.png",
                foreground_distant="velinor/backgrounds/ravi_close.png",
                foreground_close="velinor/backgrounds/ravi_close.png",
            ),
            
            player_options=[
                DialogueOption(
                    text="Thank you. I'll keep this close.",
                    glyph_triggers=["Cinarä̈"],
                    npc_response="Good. You'll understand the city better when you trust the map.",
                    trust_modifier=0.1
                ),
                DialogueOption(
                    text="How often does the map change?",
                    glyph_triggers=["Querrä"],
                    npc_response="Every few days, sometimes more. The collapses aren't always predictable.",
                    trust_modifier=0.05
                ),
                DialogueOption(
                    text="[Accept the map in silence]",
                    glyph_triggers=["Aelitḧ"],
                    npc_response="A person of few words. I respect that.",
                    trust_modifier=0.05
                ),
            ],
            
            glyph_distant=["Sha'rú"],  # Repair, new knowledge
            glyph_close=["Sha'rú", "Querrä"],  # Repair + inquiry
        )
    
    @staticmethod
    def get_sequence() -> List[SceneModule]:
        """Get the full marketplace sequence in order."""
        return [
            MarketplaceSceneSequence.build_marketplace_intro(),
            MarketplaceSceneSequence.build_npc_ravi_first_encounter(),
            MarketplaceSceneSequence.build_npc_nima_first_encounter(),
            MarketplaceSceneSequence.build_collapse_event(),
            MarketplaceSceneSequence.build_map_introduction(),
        ]
