"""
Corelink Chamber Scene - Player's Final Choice
Where the player makes the decision that determines their ending
"""

from typing import Dict, Any, Optional
from enum import Enum


class CoreLinkScene:
    """The Corelink chamber where the player makes their final choice"""
    
    def __init__(self):
        self.player_entered_chamber = False
        self.player_choice_made = False
        self.choice: Optional[str] = None
    
    def get_chamber_entrance_narration(self) -> str:
        """Narration when player enters the Corelink chamber"""
        return """
[THE CORELINK CHAMBER]

You ascend the final spiral. The chamber is exactly as you left it—the massive console that 
once kept Velinor in an iron grip, now dark and waiting.

Saori stands by the main control panel, her hand resting gently on the activation sequence. 
Velinor pulses softly beside her, no longer the urgent urgent force that once dominated this space, 
but something more like a presence. A companion.

The city spreads below you, visible through the chamber's translucent walls. You can see the 
building that houses Malrik and Elenya's archive, now being rebuilt. You can see the marketplace 
where Coren still stands, still reaching out to the scattered factions.

Everything has led to this moment.

"What do you want to do?" Saori asks quietly. "The Corelink is ready. You can restart it. Or 
you can let it rest."

She's not deciding for you this time. Neither is Velinor. Neither is the system.

This choice is yours alone.
"""
    
    def get_setup_monologue(self) -> str:
        """A moment of reflection before the choice"""
        return """
[THE WEIGHT OF CHOICE]

You stand at the console, letting your hands hover over the activation sequence. The Corelink 
has shaped everything about Velinor. It unified the factions. It managed the city's resources. 
It also controlled the people. It never asked permission. It never admitted doubt. It simply 
decided.

And now, in this moment, you have to decide what it will be.

Do you want to restart the Corelink? Do you want to give the system another chance, trusting 
that this time it will be different? That it will support the integration that the people 
are building instead of imposing false unity?

Or do you want to let it rest? To trust that the people, finally forced to face each other 
honestly, can build something without the system's guidance?

Either choice honors what's happened. Either choice acknowledges what the people have begun 
to create. The difference is what role you believe the system should play in that creation.

The choice is yours.
"""
    
    def get_choice_prompt(self) -> Dict[str, str]:
        """The choices presented to the player"""
        return {
            "restart": {
                "label": "RESTART THE CORELINK SYSTEM",
                "description": "The system will wake up, supporting the integration happening below. It will no longer impose—only mirror and amplify what the people choose.",
                "consequence_preview": "The machine's power will serve synthesis instead of hierarchy."
            },
            "abandon": {
                "label": "LET THE CORELINK REST",
                "description": "The system will remain dormant. The people will build their future without artificial guidance or support.",
                "consequence_preview": "The people will be free to determine their own path—harder, but entirely their own."
            }
        }
    
    def get_choice_confirmation(self, choice: str) -> Dict[str, Any]:
        """Narration when player confirms their choice"""
        if choice == "restart":
            return {
                "choice": "restart",
                "confirmation_narration": self._get_restart_confirmation(),
                "next_phase": "ending"
            }
        elif choice == "abandon":
            return {
                "choice": "abandon",
                "confirmation_narration": self._get_abandon_confirmation(),
                "next_phase": "ending"
            }
        else:
            return {"error": "Invalid choice"}
    
    @staticmethod
    def _get_restart_confirmation() -> str:
        """Narration for restarting the system"""
        return """
You place your hands on the activation sequence.

"We're restarting it," you say quietly. "But different this time. It will listen before it 
decides."

Saori nods. There's trust in that nod—trust in you, trust in the system, trust that maybe, 
just maybe, things can be different.

Velinor brightens. The console begins to glow.

As the Corelink powers up, you feel something shift. The system coming online, but not as a 
ruler. As a partner. As a mirror to reflect back the integration that the people have chosen 
for themselves.

The city below lights up. The marketplace glows. The archive glows. And in that glow, you see 
what the future might hold.

The choice has been made. The system will wake. And now, everything depends on whether it 
can learn to serve instead of command.
"""
    
    @staticmethod
    def _get_abandon_confirmation() -> str:
        """Narration for letting the system rest"""
        return """
You pull your hands back from the console.

"Let it rest," you say. "They can figure this out on their own."

Saori's expression is complicated—it's not approval or disapproval, just recognition of what 
you're choosing. A commitment to trust the people completely. No safety net. No system guidance.

The console remains dark. Velinor settles into quietness.

As the chamber stays dark, you feel something shift. The system powering down, releasing its 
grip on the city, trusting the people to carry forward what they've begun.

The city below continues its work. The archive glows with candle-light and determination. The 
marketplace bustles with people making their own choices. Coren moves between communities.

No system. No guidance. No artificial manager.

Just the people, learning to live together without the machine to mediate.

The choice has been made. The system will rest. And now, everything depends on whether the 
people can do what the system never could—love each other into coherence.
"""
    
    def get_after_choice_reflection(self, choice: str) -> str:
        """A moment of reflection after the choice is made"""
        if choice == "restart":
            return """
As the Corelink powers up, Saori places her hand on your shoulder.

"Thank you," she says. "For believing this could work differently."

Below, the city begins to respond to the system coming online. But it's not an intrusion this 
time. It's a conversation. The system asking the city what it needs. The city telling the 
system what it's building.

Velinor pulses with warm light.

For the first time, maybe things can be different.
"""
        else:  # abandon
            return """
As the chamber falls dark, Saori steps closer to you.

"I'm scared," she admits. "But maybe fear is what we need. To force us to be brave enough to 
face each other without the system between us."

Below, the city continues its work by whatever light they can create. Archive. Marketplace. 
Community. All of it built by human hands now, without system support.

Velinor fades into the background.

The real work is just beginning.
"""
