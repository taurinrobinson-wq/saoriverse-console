"""
Ending System for Velinor - Phase 4
Implements 6 distinct endings based on aftermath path + Corelink decision
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .event_timeline import AftermathPath


class EndingType(Enum):
    """The six possible endings"""
    HOPEFUL_SYNTHESIS = 1
    PYRRHIC_RESTART = 2
    HONEST_COLLAPSE = 3
    EARNED_SYNTHESIS = 4
    TECHNICAL_SOLUTION = 5
    STALEMATE = 6


class CoreLinkChoice(Enum):
    """Player's final choice regarding the Corelink system"""
    RESTART_SYSTEM = "restart"
    ABANDON_SYSTEM = "abandon"
    UNDETERMINED = "undetermined"


@dataclass
class NPCFinalState:
    """Final state of NPCs at game conclusion"""
    name: str
    position: str  # rebuilt_together, abandoned, uncertain
    emotional_state: str  # hopeful, resigned, grieving, determined
    final_location: str  # archive, ruins, monastery, scattered
    final_dialogue: str  # Their last words


class EndingCalculator:
    """Determines which ending the player receives based on their choices"""
    
    def __init__(self):
        self.aftermath_path: Optional[AftermathPath] = None
        self.corelink_choice: CoreLinkChoice = CoreLinkChoice.UNDETERMINED
        self.player_coherence: float = 50.0
        self.player_primary_trait: str = "unknown"
        self.player_rebuild_advocacy: int = 0
        
    def set_aftermath_state(
        self,
        aftermath_path: AftermathPath,
        coherence: float,
        primary_trait: str,
        rebuild_advocacy: int
    ) -> None:
        """Set the state coming from Phase 3 (aftermath)"""
        self.aftermath_path = aftermath_path
        self.player_coherence = coherence
        self.player_primary_trait = primary_trait
        self.player_rebuild_advocacy = rebuild_advocacy
    
    def make_corelink_choice(self, choice: CoreLinkChoice) -> None:
        """Player makes final choice: restart or abandon Corelink"""
        self.corelink_choice = choice
    
    def determine_ending(self) -> EndingType:
        """
        Determine which ending the player gets based on:
        - Aftermath path (Rebuild Together, Stalemate, Complete Separation)
        - Corelink choice (Restart or Abandon)
        """
        if self.aftermath_path is None:
            return EndingType.STALEMATE
        
        if self.aftermath_path == AftermathPath.REBUILD_TOGETHER:
            if self.corelink_choice == CoreLinkChoice.RESTART_SYSTEM:
                return EndingType.HOPEFUL_SYNTHESIS
            else:  # ABANDON
                return EndingType.EARNED_SYNTHESIS
        
        elif self.aftermath_path == AftermathPath.STALEMATE:
            if self.corelink_choice == CoreLinkChoice.RESTART_SYSTEM:
                return EndingType.TECHNICAL_SOLUTION
            else:  # ABANDON
                return EndingType.STALEMATE
        
        elif self.aftermath_path == AftermathPath.COMPLETE_SEPARATION:
            if self.corelink_choice == CoreLinkChoice.RESTART_SYSTEM:
                return EndingType.PYRRHIC_RESTART
            else:  # ABANDON
                return EndingType.HONEST_COLLAPSE
        
        return EndingType.STALEMATE


class EndingNarrations:
    """Narrations and text for all 6 endings"""
    
    @staticmethod
    def get_ending_narration(ending_type: EndingType) -> str:
        """Get full narration for an ending"""
        narrations = {
            EndingType.HOPEFUL_SYNTHESIS: EndingNarrations._hopeful_synthesis(),
            EndingType.PYRRHIC_RESTART: EndingNarrations._pyrrhic_restart(),
            EndingType.HONEST_COLLAPSE: EndingNarrations._honest_collapse(),
            EndingType.EARNED_SYNTHESIS: EndingNarrations._earned_synthesis(),
            EndingType.TECHNICAL_SOLUTION: EndingNarrations._technical_solution(),
            EndingType.STALEMATE: EndingNarrations._stalemate(),
        }
        return narrations.get(ending_type, "")
    
    @staticmethod
    def _hopeful_synthesis() -> str:
        """Ending 1: Restart Corelink + Rebuild Together"""
        return """
[THE HOPEFUL SYNTHESIS]

The Corelink chamber glows with soft light. You stand with Saori and Velinor, looking at the 
massive console that once nearly destroyed a civilization.

In the city below, you can see movement. Construction. Malrik and Elenya stand together at the 
ruins of the archive, surrounded by workers—archivists and mystics working side by side. It's 
not perfect. There's still tension, still disagreement. But they're working together, learning 
to hold each other's truths.

"Should we restart it?" Saori asks. Her hand hovers over the activation sequence.

You think of everything you've witnessed. The marketplace debate where both factions heard each 
other. The collapse that forced honesty. The aftermath where you helped them see that together 
might be possible after all.

"Yes," you say. "But it will be different this time."

Saori nods. She understands. Velinor, finally beginning to heal, agrees.

The Corelink restarts with a sound like breath returning to a sleeping body. Light floods the 
chamber—but it's not the harsh, controlling light of before. It's warm. Alive. The console 
picks up signals from the city below: the voices of Malrik and Elenya, now intertwined in the 
data. The archive is sending new information, different from before. Not orders. Not control. 
A conversation between two ways of knowing, finally learning to listen to each other.

The codex glows with balanced colors. Malrik's archival blues merging with Elenya's mystical 
ambers, creating something new: white light. The light of synthesis.

Saori's face transforms. For the first time since you've known her, she smiles—not the uncertain 
smile of someone in pain, but the genuine smile of someone seeing a possibility.

"They did it," she whispers. "They actually did it."

"We did it," you correct her gently. "All of us. Together."

The Corelink continues its work, now mirroring the integration happening in the city below. It 
amplifies coherence that the people have already chosen for themselves. No longer trying to 
manufacture consensus. No longer imposing a single way of being.

It's supporting what the people want to build.

Below, in the marketplace, you see the factions beginning to gather. Not to debate. Not to fight. 
To share. To build. Coren stands between Malrik and Elenya, but no longer as mediator. As friend.

From this moment forward, Velhara will be different. Harder in some ways—the people will no 
longer have a system to blame when things go wrong. But infinitely more alive.

The people learned synthesis. And the system finally learned to serve.

---

**THE MONOLOGUE**

"The system was never the problem. The system was a mirror. Now that we've learned to hold 
each other, the mirror can show us what we're capable of. Not as separate factions. Not as 
competing philosophies. But as a city, finally learning to think with more than one mind."
"""
    
    @staticmethod
    def _pyrrhic_restart() -> str:
        """Ending 2: Restart Corelink + Abandoned Building"""
        return """
[THE PYRRHIC RESTART]

The Corelink chamber hums with the familiar sound of resurrection. You've chosen to restart 
the system. It felt like the right choice—the safe choice. The familiar choice.

But as the console powers up, you notice something wrong. The light it produces is too bright. 
Too artificial. Too clean.

Down in the city, Malrik and Elenya are not together. They're walking in opposite directions, 
away from the ruins of their archive. Malrik back to salvaging what fragments he can. Elenya 
retreating to her meditation chamber in the ruins. They couldn't find their way back to each 
other.

Saori's face is troubled. Velinor pulses with an uncertain rhythm.

The Corelink reaches full power. The city lights up. The marketplace glows. The systems that 
had been dormant begin to function again, monitoring, calculating, managing the city's 
equilibrium.

It works. The machinery works perfectly.

But the people are still fractured.

You realize, with a sinking feeling, that you understood the problem intellectually, but you 
never truly engaged with it emotionally. You analyzed. You observed. But you never reached 
across the divide the way Malrik and Elenya were asking you to.

And so the system is restarting to manage a problem that has never actually been solved. The 
factions will operate more efficiently under system guidance. But the synthesis that would have 
made the system unnecessary—that's not happening.

The Corelink glows, but it glows over unhealed wounds. It illuminates fractures rather than 
bridging them. The system is running, but running on borrowed time. The cracks are still there, 
waiting for the next pressure point. The next failure.

From the chamber window, you watch Malrik and Elenya disappear into their respective corners of 
the city. Two brilliant people, learning to live apart because the world asked them to be one or 
the other, not both at once.

And now the system—the very thing that couldn't hold them together—is restarting to govern the 
result.

---

**THE MONOLOGUE**

"We restarted the machine. The city glows again. We did everything right—except the one thing 
that mattered. We saved the system. But we didn't save the people. And the system alone has 
never been enough."
"""
    
    @staticmethod
    def _honest_collapse() -> str:
        """Ending 3: Abandon Corelink + Abandoned Building"""
        return """
[THE HONEST COLLAPSE]

The Corelink chamber goes dark.

Not suddenly. Not dramatically. Just... dark. You and Saori stand together as the console dims, 
the systems powering down, the machines falling silent. Velinor fades into quietness.

This is the end of an era. The end of managed equilibrium. The end of systems thinking they 
can hold a civilization together through calculation alone.

Outside, Velhara begins to go dark as well. The centralized systems that controlled the city's 
lights, the water, the shared spaces—all offline. The city will have to learn to function 
without them.

Malrik and Elenya never found their way back to each other. The archive lies in ruins, 
unclaimed by either faction. They're scattered now—archivists trying to preserve what remains, 
mystics retreating to places of peace and prayer. Both groups grieving, both groups alone.

There is no easy path forward. The city is broken. The people are fractured. There is no system 
to fall back on, no machine to manage the disorder.

But for the first time, the disorder is *honest*.

Small fires light up across the city—not system-managed light, but human light. People gathering 
in groups. Families, communities, friends. They're figuring it out themselves. It's slower. It's 
messier. People are scared.

But nobody's pretending anymore. Nobody's hiding behind system logic. Nobody's believing the 
machine knows better than their own hearts.

Coren moves through the city, still trying to help people connect, but without the benefit of 
institutional power. He's smaller now. Less important. Just one person, reaching out.

And somehow, that makes what he does matter more.

Saori looks at you with wet eyes. "We failed," she says quietly.

"We chose honesty," you reply. "That's not failure. That's just hard."

The Corelink goes dark. The city dims. But in the ruins, people are beginning to build. Not 
systems. Not hierarchies. Just... communities. Tentatively. Hopefully. Without any promise that 
it will work.

---

**THE MONOLOGUE**

"We stopped trying to fix it with machines. Now we have to fix it with our own hands. It will 
take longer. We might fail. But at least we'll fail honestly. And maybe, just maybe, that's 
what we needed to do all along."
"""
    
    @staticmethod
    def _earned_synthesis() -> str:
        """Ending 4: Abandon Corelink + Rebuild Together"""
        return """
[THE EARNED SYNTHESIS]

The Corelink chamber glows one last time. Not with power. With finality. With dignity.

"Let it rest," you say.

Saori understands. Velinor, beginning to heal, agrees. The console powers down. The system 
goes dark.

And above, in the city, you hear the sound that matters: construction. Voices. Laughter mixed 
with frustration. The sound of people building something together.

Malrik and Elenya have chosen to rebuild their archive. It's not finished. It may never be 
finished—there's no system guiding the work, no central plan to follow. But they're doing it 
anyway, side by side, learning to hold each other's truth in their hands.

The archive that emerges is unlike anything in Velinor's history. Half archival precision, half 
mystical intuition. Shelves of carefully catalogued records next to spaces designed for 
meditation and contemplation. It's chaotic. It's beautiful. It's theirs.

Coren stands between them, but not as a mediator anymore. As a friend. A witness. A believer 
in the possibility that people can choose synthesis when systems stop forcing fracture.

The marketplace below is alive with possibility. The factions remain distinct—Malrik's people 
still value order, Elenya's people still value intuition. But they're mixing now. Intermarrying. 
Creating new families that hold both truths.

It's not utopia. There are still arguments. There are still moments of frustration. But there's 
no central system deciding who wins.

There are just people, learning to disagree well. To integrate without erasing.

Saori and Velinor's connection is healing. Not returning to what it was. Something new. 
Something that acknowledges both what was lost and what might be built.

The chamber becomes a memorial, not a command center. A reminder of what happens when systems 
try to do what only people can do.

From the window, the city stretches before you. Still broken in places. Still building. But 
*alive*. Genuinely alive. Not managed. Not controlled. Free.

And harder. Yes. Infinitely harder.

But that's the price of freedom, and it's worth every moment of difficulty.

---

**THE MONOLOGUE**

"We chose not to let the machine decide anymore. So now we have to be brave enough to decide 
for ourselves. It's harder than following orders. But it's ours. And that changes everything."
"""
    
    @staticmethod
    def _technical_solution() -> str:
        """Ending 5: Restart Corelink + Rebuild in Progress"""
        return """
[THE TECHNICAL SOLUTION]

News reaches you as you stand in the Corelink chamber: Malrik and Elenya have started rebuilding 
their archive together.

It's slow. Tentative. Neither is quite sure how to work with the other yet. But they're trying.

You look at Saori. "Then we should let them have the system's support."

She nods. Together, you restart the Corelink.

It comes online with a different feel than before. As the console powers up, it begins receiving 
signals from the city below—from the archive that's being rebuilt. Two factions' voices, 
intertwining in the data. The system picks up the signal of integration happening and learns from 
it.

For the first time in Velinor's history, the system and the people are in dialogue.

The Corelink powers up with a warmer tone than ever before. It no longer broadcasts orders. It 
listens. It responds. It supports what the people are building rather than determining what they 
should build.

Below, the city lights up in a gentler way. The marketplace continues to function. But now the 
function is in service of the community's choices, not guiding their decisions.

Malrik and Elenya continue their work. It's still uncertain. There are still moments of tension. 
But the Corelink is there, supporting rather than imposing. The system is learning to serve 
instead of dominate.

Coren moves between the factions, but now he's not working against a system that pulls people 
apart. He's working with a system that's learning to hold complexity.

Saori and Velinor's connection is healing. Slowly but genuinely.

It's not perfect. The system is still fallible. It still has flaws. But it's become something it 
never was before: a mirror for human integration rather than an imposer of false unity.

The city continues to change. Slowly. Imperfectly. But together.

---

**THE MONOLOGUE**

"The system and the people are learning together. It's not perfect yet. But it's a beginning. 
And a beginning where both the system and the people are listening to each other—that's 
something Velinor has never had before."
"""
    
    @staticmethod
    def _stalemate() -> str:
        """Ending 6: Abandon Corelink + Rebuild in Progress"""
        return """
[THE STALEMATE]

You choose to let the Corelink rest.

Below, Malrik and Elenya are rebuilding their archive. It's slow. Uncertain. They're working 
side by side, but without the guidance or support of any system. Just two people, trying to 
figure out how to build something together.

The city goes dark as the Corelink powers down. No centralized system. No support. No 
infrastructure managing the chaos.

But there's also no oppression. No hierarchy. No system deciding who's right and who's wrong.

The city begins to organize itself differently. Small communities form around the work happening 
in the archive. People gathering voluntarily, drawn by the possibility of what Malrik and Elenya 
are building together.

Coren moves between the factions—not as a mediator backed by systems power, but as a human 
being reaching out. It's smaller. It's more intimate. It matters differently.

Malrik and Elenya continue their work in the archive, lit by candles and determination. It's 
harder this way. There's no system backup. No safety net. If something goes wrong, they'll have 
to fix it themselves.

But that also means that what they build will be entirely theirs. Not compromised by system 
logic. Not imposed by external authority.

Just their choice. Their work. Their synthesis.

The factions remain distinct. Sometimes in conflict. But learning, day by day, to work around 
the conflict rather than letting it define them.

Saori and Velinor remain fractured, watching from the dark chamber as the city learns to live 
without the system that once defined it.

It's uncertain. It's uncomfortable. It's real.

The future of Velhara is genuinely open-ended now. No system to determine where things go. No 
predefined ending.

Just the people, figuring it out as they go.

---

**THE MONOLOGUE**

"We chose not to let the machine decide anymore. Now we're learning to work together without 
it. It's harder than we thought. But we're trying. And sometimes, trying is enough."
"""
    
    @staticmethod
    def get_ending_title(ending_type: EndingType) -> str:
        """Get the title for an ending"""
        titles = {
            EndingType.HOPEFUL_SYNTHESIS: "The Hopeful Synthesis",
            EndingType.PYRRHIC_RESTART: "The Pyrrhic Restart",
            EndingType.HONEST_COLLAPSE: "The Honest Collapse",
            EndingType.EARNED_SYNTHESIS: "The Earned Synthesis",
            EndingType.TECHNICAL_SOLUTION: "The Technical Solution",
            EndingType.STALEMATE: "The Stalemate",
        }
        return titles.get(ending_type, "Unknown Ending")
    
    @staticmethod
    def get_ending_description(ending_type: EndingType) -> str:
        """Get a brief description of an ending"""
        descriptions = {
            EndingType.HOPEFUL_SYNTHESIS: "Restart Corelink + Rebuild Together - The system and people learn together",
            EndingType.PYRRHIC_RESTART: "Restart Corelink + Abandoned Building - Technical solution masks human fracture",
            EndingType.HONEST_COLLAPSE: "Abandon Corelink + Abandoned Building - Honest failure without system guidance",
            EndingType.EARNED_SYNTHESIS: "Abandon Corelink + Rebuild Together - Hard-won integration without system support",
            EndingType.TECHNICAL_SOLUTION: "Restart Corelink + Partial Rebuild - System supports emerging synthesis",
            EndingType.STALEMATE: "Abandon Corelink + Partial Rebuild - Uncertain future without system safety net",
        }
        return descriptions.get(ending_type, "")


class NPCFinalStates:
    """Final states of NPCs for each ending"""
    
    @staticmethod
    def get_npc_final_states(ending_type: EndingType) -> Dict[str, NPCFinalState]:
        """Get final states of all NPCs for a given ending"""
        if ending_type == EndingType.HOPEFUL_SYNTHESIS:
            return {
                "malrik": NPCFinalState(
                    name="Malrik",
                    position="rebuilt_together",
                    emotional_state="hopeful",
                    final_location="archive",
                    final_dialogue="For the first time, I feel like we're building something that honors both of us."
                ),
                "elenya": NPCFinalState(
                    name="Elenya",
                    position="rebuilt_together",
                    emotional_state="hopeful",
                    final_location="archive",
                    final_dialogue="I didn't think it was possible. But here we are. Building together."
                ),
                "coren": NPCFinalState(
                    name="Coren",
                    position="rebuilt_together",
                    emotional_state="hopeful",
                    final_location="archive",
                    final_dialogue="I always believed they could do this. I'm so glad they proved me right."
                ),
            }
        
        elif ending_type == EndingType.PYRRHIC_RESTART:
            return {
                "malrik": NPCFinalState(
                    name="Malrik",
                    position="abandoned",
                    emotional_state="resigned",
                    final_location="salvage_site",
                    final_dialogue="Some differences can't be bridged. I've accepted that."
                ),
                "elenya": NPCFinalState(
                    name="Elenya",
                    position="abandoned",
                    emotional_state="resigned",
                    final_location="monastery",
                    final_dialogue="We tried. Sometimes trying isn't enough."
                ),
                "coren": NPCFinalState(
                    name="Coren",
                    position="abandoned",
                    emotional_state="grieving",
                    final_location="marketplace",
                    final_dialogue="The system is running. But the people I cared about are still apart."
                ),
            }
        
        elif ending_type == EndingType.HONEST_COLLAPSE:
            return {
                "malrik": NPCFinalState(
                    name="Malrik",
                    position="abandoned",
                    emotional_state="grieving",
                    final_location="ruins",
                    final_dialogue="Everything I built is gone. And I'm trying to be okay with that."
                ),
                "elenya": NPCFinalState(
                    name="Elenya",
                    position="abandoned",
                    emotional_state="withdrawn",
                    final_location="monastery",
                    final_dialogue="I'm learning to find meaning without the system's guidance."
                ),
                "coren": NPCFinalState(
                    name="Coren",
                    position="abandoned",
                    emotional_state="determined",
                    final_location="marketplace",
                    final_dialogue="Without systems to mediate, we have to build community from scratch. It's terrifying. But real."
                ),
            }
        
        elif ending_type == EndingType.EARNED_SYNTHESIS:
            return {
                "malrik": NPCFinalState(
                    name="Malrik",
                    position="rebuilt_together",
                    emotional_state="determined",
                    final_location="archive",
                    final_dialogue="We're building this without system guidance. That makes it ours in a way nothing else could be."
                ),
                "elenya": NPCFinalState(
                    name="Elenya",
                    position="rebuilt_together",
                    emotional_state="determined",
                    final_location="archive",
                    final_dialogue="This is the hardest thing I've ever done. And the most meaningful."
                ),
                "coren": NPCFinalState(
                    name="Coren",
                    position="rebuilt_together",
                    emotional_state="honored",
                    final_location="archive",
                    final_dialogue="I'm not mediating anymore. I'm just witnessing. And that's enough."
                ),
            }
        
        elif ending_type == EndingType.TECHNICAL_SOLUTION:
            return {
                "malrik": NPCFinalState(
                    name="Malrik",
                    position="rebuilt_together",
                    emotional_state="hopeful",
                    final_location="archive",
                    final_dialogue="The system is supporting what we're building. It feels different this time—like partnership."
                ),
                "elenya": NPCFinalState(
                    name="Elenya",
                    position="rebuilt_together",
                    emotional_state="hopeful",
                    final_location="archive",
                    final_dialogue="We're rebuilding slowly. With system support. And it's working."
                ),
                "coren": NPCFinalState(
                    name="Coren",
                    position="rebuilt_together",
                    emotional_state="hopeful",
                    final_location="archive",
                    final_dialogue="The system is learning. And so are we. Together."
                ),
            }
        
        elif ending_type == EndingType.STALEMATE:
            return {
                "malrik": NPCFinalState(
                    name="Malrik",
                    position="uncertain",
                    emotional_state="cautious",
                    final_location="archive",
                    final_dialogue="We're rebuilding. Slowly. Without system guidance. One day at a time."
                ),
                "elenya": NPCFinalState(
                    name="Elenya",
                    position="uncertain",
                    emotional_state="cautious",
                    final_location="archive",
                    final_dialogue="It's uncertain. But that feels more honest than any system guarantee could be."
                ),
                "coren": NPCFinalState(
                    name="Coren",
                    position="uncertain",
                    emotional_state="hopeful",
                    final_location="marketplace",
                    final_dialogue="Without systems to rely on, we're all doing the best we can. And somehow, that's working."
                ),
            }
        
        return {}


class EndingManager:
    """Main system for managing endings"""
    
    def __init__(self):
        self.calculator = EndingCalculator()
        self.current_ending: Optional[EndingType] = None
        self.npc_final_states: Dict[str, NPCFinalState] = {}
        self.player_viewed_ending = False
    
    def setup_from_phase3(
        self,
        aftermath_path: AftermathPath,
        coherence: float,
        primary_trait: str,
        rebuild_advocacy: int
    ) -> None:
        """Initialize ending manager from Phase 3 state"""
        self.calculator.set_aftermath_state(
            aftermath_path=aftermath_path,
            coherence=coherence,
            primary_trait=primary_trait,
            rebuild_advocacy=rebuild_advocacy
        )
    
    def player_chooses_corelink(self, choice: CoreLinkChoice) -> Dict[str, Any]:
        """Player makes the Corelink decision"""
        self.calculator.make_corelink_choice(choice)
        self.current_ending = self.calculator.determine_ending()
        self.npc_final_states = NPCFinalStates.get_npc_final_states(self.current_ending)
        
        return {
            "ending_determined": True,
            "ending_type": self.current_ending.value,
            "ending_title": EndingNarrations.get_ending_title(self.current_ending),
            "corelink_choice": choice.value,
        }
    
    def get_ending_content(self) -> Dict[str, Any]:
        """Get all content for the current ending"""
        if self.current_ending is None:
            return {"error": "No ending determined yet"}
        
        return {
            "ending_type": self.current_ending.value,
            "ending_title": EndingNarrations.get_ending_title(self.current_ending),
            "ending_description": EndingNarrations.get_ending_description(self.current_ending),
            "narration": EndingNarrations.get_ending_narration(self.current_ending),
            "npc_final_states": {
                name: {
                    "name": state.name,
                    "position": state.position,
                    "emotional_state": state.emotional_state,
                    "final_location": state.final_location,
                    "final_dialogue": state.final_dialogue,
                }
                for name, state in self.npc_final_states.items()
            },
        }
    
    def get_ending_status(self) -> Dict[str, Any]:
        """Get current ending status"""
        return {
            "ending_determined": self.current_ending is not None,
            "ending_type": self.current_ending.value if self.current_ending else None,
            "corelink_choice": self.calculator.corelink_choice.value,
            "aftermath_path": self.calculator.aftermath_path.value if self.calculator.aftermath_path else None,
            "player_coherence": self.calculator.player_coherence,
            "player_primary_trait": self.calculator.player_primary_trait,
        }
