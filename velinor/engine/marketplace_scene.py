"""
Marketplace Debate Scene - Phase 2 Implementation

This scene implements the first major branching dialogue from the narrative spine.
It demonstrates:
- Trait-based dialogue branching (empathy, skepticism, integration, awareness paths)
- Coherence-affected dialogue depth
- NPC personality compatibility
- Multiple valid player approaches
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Callable
from enum import Enum

from .trait_system import TraitType, TraitChoice
from .coherence_calculator import CoherenceCalculator
from .scene_manager import SceneModule, SceneState, DialogueOption, SceneAssets


class MarketplaceDebatePhase(Enum):
    """Phases of the marketplace debate scene"""
    INTRO = "intro"  # Player approaches/witnesses debate
    SETUP = "setup"  # NPCs explain positions
    BRANCHING = "branching"  # Player makes significant choice
    RESOLUTION = "resolution"  # Scene ends with consequence


@dataclass
class MarketplaceDebateScene:
    """
    Complete marketplace debate scene with branching dialogue.
    
    NPCs: Malrik (skeptical merchant), Elenya (empathetic mystic), Coren (integrator mediator)
    Player choices map to trait types and affect:
    - NPC perception
    - Coherence level
    - Path to building collapse
    """
    
    def __init__(self):
        self.current_phase = MarketplaceDebatePhase.INTRO
        self.player_choice_history: List[Dict] = []
        self.npc_state = {
            'malrik': {'perceived_player': None, 'openness': 0.5},
            'elenya': {'perceived_player': None, 'openness': 0.5},
            'coren': {'perceived_player': None, 'openness': 0.5},
        }
    
    def get_intro_narration(self) -> str:
        """Opening narration for the marketplace debate"""
        return """
        The marketplace square is crowded today. Merchants hawk their wares, 
        children chase each other between stalls. But near the archive building,
        a small crowd has formed, giving space to three figures locked in debate.
        
        Malrik stands rigid, arms crossed. His merchants respect him—they respect
        power, structure, things you can calculate. Elenya is across from him,
        her hands moving as she speaks. Her followers whisper between each other.
        And between them, Coren is trying to hold the line, though the cracks
        are starting to show.
        
        The debate has been going on for months. Everyone in Velhara knows about it.
        Some people laugh about it over drinks. Some people worry about what it means.
        
        You haven't chosen a side yet.
        """
    
    def get_entry_point_choices(self) -> List[Dict]:
        """
        Initial choices for how player approaches the scene.
        These establish the frame but don't yet commit to a trait.
        """
        return [
            {
                'text': 'Walk directly to Coren - you want to understand',
                'choice_id': 'entry_direct_coren',
                'npc_response': 'Coren looks relieved to see someone new. "Maybe you can help me make sense of this."',
                'next_phase': MarketplaceDebatePhase.SETUP,
                'trait_choice': None,  # Entry doesn't commit trait
            },
            {
                'text': 'Hang back and listen - observe their positions first',
                'choice_id': 'entry_observe',
                'npc_response': 'From a distance, you hear fragments. Malrik talks about "preservation." Elenya speaks of "meaning."',
                'next_phase': MarketplaceDebatePhase.SETUP,
                'trait_choice': TraitType.AWARENESS,  # Observing builds awareness
                'trait_weight': 0.2,
            },
            {
                'text': 'Ask a marketplace NPC what this is about - get context',
                'choice_id': 'entry_ask_context',
                'npc_response': 'A merchant laughs. "They\'ve been at it for months. Archive space. Malrik wants his records organized. Elenya wants mystical practice. Coren thinks they can share. I think they\'re wasting breath."',
                'next_phase': MarketplaceDebatePhase.SETUP,
                'trait_choice': TraitType.SKEPTICISM,  # Questioning builds skepticism
                'trait_weight': 0.15,
            },
        ]
    
    def get_setup_narration(self) -> str:
        """Scene description when debate is in progress"""
        return """
        As you approach, the debate intensifies. Malrik's voice rises slightly.
        
        "Records must be preserved. Organized. Catalogued. Stored with precision.
        The mystics' approach—leaving things scattered about, handling artifacts
        without proper documentation—this isn't spirituality, it's negligence."
        
        Elenya's hands grip the edge of her shawl.
        
        "And when do we preserve the memory of what those records mean? When do we
        teach people to feel the weight of history, not just read about it? Your
        archives are tombs—beautiful tombs, but tombs nonetheless."
        
        Coren looks between them, frustration building.
        
        "You're both right. We need preserved records AND people who understand their
        significance. What if we arranged time-sharing? Multiple wings—"
        
        "Time-sharing means compromise," Malrik says, not unkindly. "And compromise
        means neither approach works."
        
        They all turn to you. The debate pauses. Waiting.
        """
    
    def get_branching_choices(
        self,
        coherence_level: float,
        player_primary_trait: TraitType,
        npc_conflicts: Dict[str, str]
    ) -> List[Dict]:
        """
        Main player choices that determine the scene's outcome.
        Available choices vary based on coherence and trait pattern.
        
        Args:
            coherence_level: Player's current coherence (0-100)
            player_primary_trait: Player's dominant trait pattern
            npc_conflicts: Dict of NPC → conflict_level ("ally", "neutral", "opposed")
        """
        choices = []
        
        # ========== EMPATHY PATH ==========
        # Always available
        choices.append({
            'text': 'Support Coren\'s integration vision: "Why can\'t it be both?"',
            'choice_id': 'branch_empathy_synthesis',
            'primary_trait': TraitType.EMPATHY,
            'secondary_trait': TraitType.INTEGRATION,
            'trait_weight': 0.3,
            'secondary_weight': 0.2,
            'npc_name': 'Coren',
            'scene_name': 'marketplace_debate',
            'response': '"[To player] You understand. Thank you. But convincing them is another matter." [Malrik nods slightly. Elenya looks hopeful.]',
            'consequence': 'You\'ve positioned yourself as a bridge-builder. The factions will look to you.',
        })
        
        # ========== SKEPTICISM PATH ==========
        # Always available
        choices.append({
            'text': 'Challenge both sides: "This is a resource dispute, not philosophy."',
            'choice_id': 'branch_skepticism_practical',
            'primary_trait': TraitType.SKEPTICISM,
            'trait_weight': 0.3,
            'npc_name': 'Malrik',
            'scene_name': 'marketplace_debate',
            'response': '"[Malrik nods] Finally, someone who understands. [Elenya looks hurt.] This isn\'t about deeper truth—it\'s functional."',
            'consequence': 'Malrik respects your clarity. Elenya feels dismissed.',
        })
        
        # ========== INTEGRATION/AWARENESS PATH ==========
        # Requires coherence >= 60 (player needs to be somewhat consistent)
        if coherence_level >= 60:
            choices.append({
                'text': 'Name the underlying emotion: "You care about each other. That\'s why this hurts."',
                'choice_id': 'branch_synthesis_emotional',
                'primary_trait': TraitType.INTEGRATION,
                'secondary_trait': TraitType.AWARENESS,
                'trait_weight': 0.4,
                'secondary_weight': 0.3,
                'npc_name': 'Elenya',
                'scene_name': 'marketplace_debate',
                'response': '"[Silence. Elenya\'s eyes widen.] You... yes. That\'s... [Malrik\'s rigid posture softens.] [Coren quietly] You see it. Most people don\'t."',
                'consequence': 'You\'ve touched something deeper. Both factions recognize you understand them.',
                'coherence_locked': True,  # This response only works if player is being authentic
            })
        
        # ========== AWARENESS-FIRST PATH ==========
        # Requires coherence >= 70 (need clarity to see patterns)
        if coherence_level >= 70:
            choices.append({
                'text': 'Ask probing questions: "What\'s really at stake here?"',
                'choice_id': 'branch_awareness_questioning',
                'primary_trait': TraitType.AWARENESS,
                'secondary_trait': TraitType.SKEPTICISM,
                'trait_weight': 0.35,
                'secondary_weight': 0.2,
                'npc_name': 'Coren',
                'scene_name': 'marketplace_debate',
                'response': '"Power, resources, and the value of different ways of knowing. They\'re both right. They\'re both needed."',
                'consequence': 'You\'ve established yourself as someone who sees beneath surface conflicts.',
            })
        
        # ========== EMPATHY WITH MALRIK PATH ==========
        # If player is empathetic and Malrik sees them as ally
        if npc_conflicts.get('Malrik') == 'ally' or player_primary_trait == TraitType.EMPATHY:
            choices.append({
                'text': 'Support Malrik\'s concern: "Preservation matters. It\'s fragile."',
                'choice_id': 'branch_empathy_malrik',
                'primary_trait': TraitType.EMPATHY,
                'trait_weight': 0.25,
                'npc_name': 'Malrik',
                'scene_name': 'marketplace_debate',
                'response': '"You understand the burden of preservation. [Elenya steps back, hurt.] Someone needs to."',
                'consequence': 'Malrik trusts you. Elenya feels your betrayal.',
            })
        
        # ========== EMPATHY WITH ELENYA PATH ==========
        # If player is empathetic and Elenya sees them as ally
        if npc_conflicts.get('Elenya') == 'ally' or player_primary_trait == TraitType.EMPATHY:
            choices.append({
                'text': 'Support Elenya\'s concern: "Living tradition matters. So does connection."',
                'choice_id': 'branch_empathy_elenya',
                'primary_trait': TraitType.EMPATHY,
                'trait_weight': 0.25,
                'npc_name': 'Elenya',
                'scene_name': 'marketplace_debate',
                'response': '"[Elenya\'s eyes shine] You see it. Thank you. [Malrik\'s jaw tightens.] Someone needs to understand."',
                'consequence': 'Elenya trusts you. Malrik sees you as naive.',
            })
        
        return choices
    
    def get_resolution_narration(self, player_choice: Dict) -> str:
        """
        Scene resolution based on player's choice.
        Describes immediate consequences and sets up next scene.
        """
        choice_id = player_choice.get('choice_id')
        consequence = player_choice.get('consequence', '')
        
        if choice_id == 'branch_empathy_synthesis':
            return f"""
            {consequence}
            
            Over the next days, people start talking about you as someone who "understands both sides."
            
            Coren returns to you often, wanting to talk through the problem. Malrik watches you with
            calculation—is there value in knowing someone trusted by the mystics? Elenya seeks you out,
            hoping you might help Malrik see the spiritual dimension of preservation.
            
            But the archive building remains contested. And tensions continue to rise.
            
            Then, three days later, someone hears rumors of a crack in the building's foundation.
            """
        
        elif choice_id == 'branch_skepticism_practical':
            return f"""
            {consequence}
            
            Malrik appreciates your directness. He begins including you in merchant circle discussions,
            valuing your pragmatic thinking. But Elenya withdraws. She stops attending marketplace gatherings.
            
            You hear from mutual friends that she feels increasingly invisible, increasingly like the spiritual
            ways of Velhara simply don't matter.
            
            And then, one night, the spiritual quarter catches fire. Whether accident or intentional, no one
            can quite say. But Elenya is found collapsed near the burned archive annex, having tried to save
            sacred texts that weren't even there.
            """
        
        elif choice_id == 'branch_synthesis_emotional':
            return f"""
            {consequence}
            
            That night, Malrik and Elenya actually talk. Not about the archive building—about why they
            care so much. Malrik confesses his fear of losing everything. Elenya confesses her grief at
            feeling erased. It's not a resolution. But it's a beginning.
            
            They don't solve the archive problem. But they start understanding each other.
            
            Coren seems lighter than he has been in months.
            
            Then, the building shows signs of structural damage. And the factions must actually decide
            what to do together.
            """
        
        elif choice_id == 'branch_awareness_questioning':
            return f"""
            {consequence}
            
            By asking the right questions, you've positioned yourself as someone worth listening to.
            All three of them—Malrik, Elenya, and Coren—start seeking your input on decisions.
            
            You become something like a counselor to the factions. It's an unusual position for someone
            so new to Velhara. Some people resent it. Others appreciate it.
            
            Then, the building begins to fail. And they'll need all the wisdom you can gather.
            """
        
        else:
            return f"""
            {consequence}
            
            The debate continues. Malrik and Elenya are more entrenched than before.
            Coren looks increasingly tired.
            
            Then, the building shows signs of structural failure.
            """
    
    def get_exit_narration(self) -> str:
        """Final narration as scene ends"""
        return """
        The crowd around the debaters begins to disperse. People have work to do.
        Malrik walks away, still thinking. Elenya stands in the square a moment longer.
        Coren approaches you before leaving.
        
        "Whatever you did here, thank you. Or I'll thank you when this is all over."
        
        As the marketplace returns to normal commerce, you realize something has shifted.
        The factions know who you are now. And when the next crisis comes—and it will—
        they'll remember how you responded to this one.
        """
    
    def get_scene_assets(self) -> SceneAssets:
        """Asset references for visual rendering"""
        return SceneAssets(
            background_distant="backgrounds/marketplace_distant.jpg",
            background_close="backgrounds/marketplace_close.jpg",
            foreground_distant="npcs/debate_distant.jpg",
            foreground_close="npcs/debate_close.jpg",
            ambient_sound="audio/marketplace_ambience.mp3",
        )


def create_marketplace_debate_scene() -> Dict:
    """
    Factory function to create the marketplace debate scene.
    
    Returns scene config that can be used by orchestrator.
    """
    scene = MarketplaceDebateScene()
    
    return {
        'scene_id': 'marketplace_debate',
        'name': 'Marketplace Debate',
        'intro_narration': scene.get_intro_narration(),
        'intro_choices': scene.get_entry_point_choices(),
        'setup_narration': scene.get_setup_narration(),
        'get_branching_choices': scene.get_branching_choices,
        'get_resolution_narration': scene.get_resolution_narration,
        'exit_narration': scene.get_exit_narration(),
        'assets': scene.get_scene_assets(),
        'npcs': ['Malrik', 'Elenya', 'Coren'],
    }
