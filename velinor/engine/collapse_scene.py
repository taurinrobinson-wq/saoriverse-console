"""
Building Collapse Scene for Velinor - Phase 3
Implements the collapse event, immediate aftermath, and pathway divergence
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from .event_timeline import AftermathPath


class CollapseTriggerPhase(Enum):
    """Phases within the collapse event itself"""
    INITIAL_RUMBLE = "initial_rumble"
    STRUCTURAL_FAILURE = "structural_failure"
    NPC_REACTIONS = "npc_reactions"
    FACTIONAL_CONFLICT = "factional_conflict"
    PLAYER_CHOICE_POINT = "player_choice_point"


class AftermathPhase(Enum):
    """Phases of immediate aftermath"""
    FACTION_SEPARATION = "faction_separation"
    COREN_MEDIATION_ATTEMPT = "coren_mediation_attempt"
    PLAYER_INTERVENTION = "player_intervention"
    PATH_DIVERGENCE = "path_divergence"


class CollapseTriggerScene:
    """The actual collapse event sequence"""
    
    def __init__(self):
        self.phase = CollapseTriggerPhase.INITIAL_RUMBLE
        self.player_witnessed = False
        self.npc_reactions_recorded = {}
    
    def get_initial_rumble_narration(self) -> str:
        """Opening moment of collapse"""
        return """
        [A deep creaking sound. Not dramatic—intimate.]
        
        The ground beneath your feet shifts. Dust motes suspended in the 
        afternoon light start to dance.
        
        For a moment, nothing else happens.
        
        Then—
        
        A sound like a scream. Not a person screaming. A building screaming.
        """
    
    def get_structural_failure_narration(self) -> str:
        """Main collapse sequence"""
        return """
        The eastern wall of the archive building develops a visible crack 
        that spreads like lightning frozen in concrete. A beam shudders and 
        splits down its length. The roof over the storage wing sags, then 
        buckles inward.
        
        Dust explodes outward in a choking cloud.
        
        [This is not a explosion. It's a slow failure. The building doesn't 
        fall—it breaks.]
        
        Pieces of masonry rain down into the courtyard. A support column 
        tilts at an angle that shouldn't be possible. The eastern half of 
        the building becomes visibly unstable, tilted at forty-five degrees.
        
        Then—silence.
        
        Dust settles like ghosts being laid to rest.
        """
    
    def get_malrik_reaction(self) -> str:
        """Malrik's immediate response"""
        return """
        Malrik emerges from the building, covered in dust, face pale.
        
        He stands frozen, staring at the damage, unable to process what 
        he's seeing.
        
        "No. No, no, no... The archive. Years of work. Everything we 
        preserved..."
        
        His voice cracks. His hands shake.
        """
    
    def get_elenya_reaction(self) -> str:
        """Elenya's immediate response"""
        return """
        Elenya runs toward the building, screaming.
        
        "Where's Soren? Where's Soren? Is anyone hurt?"
        
        Her face is wild with fear—not for the building, but for the 
        people. She looks from person to person in the gathering crowd, 
        desperately searching.
        
        A younger mystic appears, alive and relatively unharmed.
        
        "Elenya, I'm here. Everyone got out. Everyone."
        
        She collapses to her knees, sobbing.
        """
    
    def get_coren_reaction(self) -> str:
        """Coren's response"""
        return """
        Coren is standing in the courtyard, helping evacuate people. His 
        face is streaked with dust and sweat. When the building finally 
        stops moving, he looks at the ruins with an expression you can't 
        quite read.
        
        Part of him looks like he's been waiting for this moment.
        Part of him looks like his heart just broke.
        """
    
    def get_post_collapse_dialogue(self) -> str:
        """Dialogue exchange after immediate danger passes"""
        return """
        [Malrik stares at the damage]
        
        MALRIK: "No. No, no, no... The archive. Years of work. Everything 
        we preserved..."
        
        [Elenya, standing nearby, face wet with tears, voice shaking]
        
        ELENYA: "You knew. You KNEW the roof was weakening. You said you 
        wanted to 'consolidate' operations. If we'd just reinforced the 
        structure together instead of trying to accommodate both—"
        
        MALRIK: [Looking at her, eyes wide]
        "That's not... Elenya, I didn't—"
        
        ELENYA: [Voice rising, years of frustration pouring out]
        "Yes you did. You knew and you did nothing because admitting the 
        building wasn't perfect meant admitting your system doesn't work. 
        You'd rather watch it fail than actually collaborate."
        
        MALRIK: "That's not what—"
        
        ELENYA: "Yes it is. And now look at us. The building is destroyed, 
        and you're STILL finding a way to blame me."
        
        [She turns away from him and walks toward her followers. Malrik 
        stands frozen, staring at the ruins.]
        
        [Coren approaches you. His face is streaked with dust.]
        
        COREN: "This is where they decide. Rebuild or walk away. The 
        building was the only thing holding their worlds together. Now 
        they have to figure out if they will."
        """
    
    def get_scene_assets(self) -> Dict[str, str]:
        """Asset references for visual/audio rendering"""
        return {
            "background": "archive_building_collapse",
            "audio_ambient": "dust_settling_aftermath",
            "audio_tension": "building_structural_failure",
            "lighting": "dusty_afternoon",
            "npcs_present": ["malrik", "elenya", "coren"]
        }


class ImmediateAftermathScene:
    """Days 1-3 after collapse: Faction separation and player intervention"""
    
    def __init__(self):
        self.player_interventions: List[str] = []
        self.player_position = "neutral"  # neutral, pro_malrik, pro_elenya
    
    def get_separation_narration(self) -> str:
        """Day 1: Factions separate"""
        return """
        Both Malrik and Elenya withdraw into their respective factions.
        
        Malrik closes himself off in an auxiliary archival space, working 
        obsessively to salvage records. Other archivists report he won't 
        sleep, won't eat. It's like he's punishing himself.
        
        Elenya moves away from the marketplace, taking her group to a 
        temporary meditation chamber. Mystics report she's been alone 
        constantly, crying, not herself.
        
        Coren tries to bridge the gap, but both of them refuse to see him.
        """
    
    def get_malrik_isolation_dialogue(self) -> str:
        """Malrik's isolated state"""
        return """
        You find Malrik in a basement storage room, surrounded by salvaged 
        records. His eyes are hollow.
        
        "I should have maintained the structure better. I should have 
        listened to her when she said we needed to address the 
        deterioration."
        
        He doesn't look at you.
        
        "A good archivist protects what's entrusted to him. I failed."
        """
    
    def get_elenya_isolation_dialogue(self) -> str:
        """Elenya's isolated state"""
        return """
        You find Elenya in a candlelit chamber, her face marked by tears 
        that still haven't fully dried.
        
        "I said things... cruel things. I was scared, and I hurt him instead 
        of helping him."
        
        She looks at you, searching.
        
        "He hasn't come to see me. Maybe that's answer enough about what he 
        thinks of me."
        """
    
    def get_coren_exhaustion_dialogue(self) -> str:
        """Coren's attempted mediation"""
        return """
        Coren finds you and collapses onto a nearby seat.
        
        "I've been trying to tell them... Malrik that she didn't mean what 
        she said. Elenya that he's blaming himself entirely. But they won't 
        listen. They won't even see each other."
        
        He looks at you with desperate hope.
        
        "You're not bound up in this like I am. Maybe they'll listen to you."
        """
    
    def get_malrik_response_to_intervention(self, intervention_type: str) -> str:
        """Malrik's response based on intervention type"""
        responses = {
            "not_your_fault": """
            Malrik pauses, considering your words.
            
            "Wasn't it? If I'd managed better..."
            
            But there's something in his eyes now. A small opening.
            """,
            
            "how_rebuild": """
            Malrik looks up at you, surprised.
            
            "Why would she want to rebuild with me after everything that's 
            happened?"
            
            He stands, looking at the salvaged records, then at you.
            
            "I... I should ask her. Shouldn't I?"
            """,
            
            "she_is_grieving": """
            Malrik's face crumples.
            
            "Then I should be with her. Not here. With her."
            
            He stands, as if ready to move, then hesitates.
            
            "What if she doesn't want to see me?"
            """,
            
            "default": """
            Malrik nods slowly, but his expression remains distant. He 
            returns his attention to the salvaged records, the moment of 
            connection passing.
            """
        }
        return responses.get(intervention_type, responses["default"])
    
    def get_elenya_response_to_intervention(self, intervention_type: str) -> str:
        """Elenya's response based on intervention type"""
        responses = {
            "he_is_suffering": """
            Elenya's eyes widen.
            
            "He is? I thought... I didn't know. I've been so focused on my 
            own pain, I didn't consider that he might be..."
            
            She trails off, tears starting again.
            """,
            
            "collapse_as_change": """
            Elenya looks thoughtful, pain and possibility mixing in her 
            expression.
            
            "Maybe you're right. Maybe this is the only way we could have 
            broken through. If the building hadn't forced this..."
            
            She doesn't finish the thought.
            """,
            
            "he_wants_rebuild": """
            Elenya stands up, surprise flooding her face.
            
            "Really? Even after...?"
            
            She looks toward where Malrik is, as if she can see through walls.
            
            "Maybe... if he were willing to actually listen."
            """,
            
            "default": """
            Elenya nods sadly, accepting the situation.
            
            "There's too much hurt, isn't there? Maybe we're just not meant 
            to work together."
            """
        }
        return responses.get(intervention_type, responses["default"])


class AftermathPathDivergence:
    """Implementation of the 3 aftermath paths"""
    
    @staticmethod
    def get_rebuild_together_setup() -> str:
        """Path A: Setup for Rebuild Together"""
        return """
        [Day 4, near the ruined building at dusk]
        
        Malrik approaches Elenya slowly, carefully, like he's approaching 
        something that might shatter.
        
        "I don't know how to do this differently. Structure is the only 
        thing I understand."
        
        Elenya turns to face him. Her expression is guarded, but not hostile.
        
        "Then we'll have to learn something new. Together."
        
        Malrik: "What if we fail again?"
        
        Elenya: "Then at least we'll fail honestly."
        
        They stand looking at the ruins. Coren, nearby, exhales with relief.
        """
    
    @staticmethod
    def get_rebuild_together_progression() -> str:
        """Path A: Days 5-7 progression"""
        return """
        [Days 5-7: Planning Begins]
        
        Joint design sessions commence. Both Malrik and Elenya contribute 
        ideas. The tension remains, but it's productive—two perspectives 
        in genuine dialogue instead of opposition.
        
        Malrik proposes structural integrity frameworks.
        Elenya suggests spatial flow and spiritual resonance.
        
        Neither dismisses the other.
        
        They argue, but not to win. They argue to understand.
        
        Other NPCs notice:
        
        ARCHIVIST: "Malrik seems different. There's something... hopeful 
        in how he's talking about the reconstruction."
        
        MYSTIC: "Elenya's grief is still there, but there's something else 
        too. Purpose. Like she's found a reason to move forward."
        
        COREN: "I told you they could do this. I always believed."
        """
    
    @staticmethod
    def get_stalemate_setup() -> str:
        """Path B: Setup for Stalemate"""
        return """
        [Days 4-5: Independent Solutions Emerge]
        
        Instead of approaching each other, both Malrik and Elenya find 
        separate solutions.
        
        Malrik locates a smaller space to temporarily store the salvaged 
        records. It's not ideal, but it works. He throws himself into 
        organizing, into rebuilding what order he can.
        
        Elenya relocates her group to a meditation chamber in the ruins—
        one of the few sections not completely destroyed. It's cramped, 
        but it's sacred, and that's enough for now.
        
        They're functionally separated, but the city can still hold both 
        of them.
        
        Neither is happy. But neither is desperate.
        """
    
    @staticmethod
    def get_stalemate_resolution() -> str:
        """Path B: The stalemate decision"""
        return """
        [Day 6: Coren's Final Attempt]
        
        Coren brings them together one last time.
        
        COREN: "You could still rebuild together. The space is there. The 
        materials are there. What's missing is just you two being willing 
        to try."
        
        MALRIK: "We've found separate solutions. We're functioning."
        
        ELENYA: "It's working because we're not trying anymore."
        
        [Awkward silence. Both are exhausted. The collapse has taken more 
        than the building—it's taken their hope.]
        
        MALRIK: "Maybe that's enough for now."
        
        ELENYA: "Maybe."
        
        They don't look at each other.
        
        [Day 7: The Stalemate Settles]
        
        There are no immediate plans to rebuild. The broken building becomes 
        a scar on the city, a reminder of what was lost. Both factions are 
        functional but diminished. There's still love there—you can see it 
        in glances, in moments of hesitation—but it's dormant now.
        
        Waiting. Possibly forever.
        """
    
    @staticmethod
    def get_complete_separation_setup() -> str:
        """Path C: Setup for Complete Separation"""
        return """
        [Day 4: Both Factions Accept the Fracture]
        
        Neither Malrik nor Elenya reaches out. Days pass. The silence 
        becomes acceptance.
        
        Malrik becomes more rigid, more isolated in his archival work. He 
        works with mechanical precision, talking to no one, connecting with 
        nothing. His face hardens like the stone of his salvaged records.
        
        Elenya becomes more spiritual, more withdrawn. She spends hours in 
        meditation, seeking peace that won't come. Her mystics report she 
        speaks less, smiles less, seems present less.
        
        They're no longer in conflict because they're no longer in contact.
        """
    
    @staticmethod
    def get_complete_separation_aftermath() -> str:
        """Path C: The lasting separation"""
        return """
        [Days 5-7: The Building Remains a Ruin]
        
        No salvage efforts. No rebuilding. The archive becomes a cemetery 
        of what might have been.
        
        Other NPCs notice their absence and mourn in their own ways.
        
        COREN: [To player, privately, voice hollow]
        "I thought you might help them. But I suppose some things can't 
        be fixed. Some connections can't be rebuilt once they're broken."
        
        He looks smaller than before. Diminished.
        
        "I'm going to keep trying, though. Someone has to believe there's 
        a way back, even if there isn't."
        
        The city feels changed. Less vibrant. Like something essential has 
        been removed and the wound is still too fresh to close.
        """
    
    @staticmethod
    def get_aftermath_ending_connection(path: AftermathPath) -> Dict[str, str]:
        """Connect aftermath path to ending unlocks"""
        connections = {
            AftermathPath.REBUILD_TOGETHER: {
                "description": "Factions unified in shared reconstruction",
                "ending_paths_unlocked": ["ending_1_synthesis", "ending_4_new_vision"],
                "npc_state": "cooperative",
                "world_state": "lean_synthesis"
            },
            AftermathPath.STALEMATE: {
                "description": "Factions separated but stable",
                "ending_paths_unlocked": ["ending_5_ambiguity", "ending_6_resignation"],
                "npc_state": "dormant",
                "world_state": "neutral"
            },
            AftermathPath.COMPLETE_SEPARATION: {
                "description": "Factions fractured, little hope of reunion",
                "ending_paths_unlocked": ["ending_2_isolation", "ending_3_collapse"],
                "npc_state": "isolated",
                "world_state": "lean_fragmentation"
            }
        }
        return connections.get(path, {})
    
    @staticmethod
    def get_scene_assets() -> Dict[str, str]:
        """Asset references for aftermath scenes"""
        return {
            "background_ruined_building": "archive_ruins",
            "background_malrik_space": "archive_salvage_chamber",
            "background_elenya_space": "ruins_meditation_chamber",
            "background_marketplace": "marketplace_empty",
            "audio_ambient": "city_post_collapse",
            "audio_tension": "unresolved_conflict",
            "lighting": "gray_aftermath"
        }
