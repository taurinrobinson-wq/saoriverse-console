"""
Simple mechanics implementation for Velinor characters and tone system.
This module loads the JSON export and provides small classes to apply mini-game choices
and update player tone stats and NPC correlations.
"""
from dataclasses import dataclass, field
from typing import Dict, List
import json
import os


ROOT = os.path.dirname(__file__)  # velinor/game_mechanics
DATA_PATH = os.path.join(os.path.dirname(ROOT), 'markdowngameinstructions', 'malrik_elenya_coren.json')


def load_data(path: str = DATA_PATH) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


@dataclass
class ToneState:
    trust: float = 0.5
    observation: float = 0.5
    narrative: float = 0.5
    empathy: float = 0.5

    def clamp(self):
        for k in ('trust', 'observation', 'narrative', 'empathy'):
            v = getattr(self, k)
            setattr(self, k, max(0.0, min(1.0, v)))

    def as_dict(self) -> Dict[str, float]:
        return {k: getattr(self, k) for k in ('trust', 'observation', 'narrative', 'empathy')}


@dataclass
class GameMechanics:
    data: Dict = field(default_factory=load_data)
    tone: ToneState = field(default_factory=ToneState)
    attunement: float = 0.0

    def apply_choice(self, orientation: str, choice_index: int):
        scene = self.data['miniGames']['observationalScene']
        order = scene['toneOrder']
        shifts = scene['toneShifts'][orientation][choice_index]
        # shifts array corresponds to order [trust, observation, narrative, empathy]
        for key, delta in zip(order, shifts):
            setattr(self.tone, key, getattr(self.tone, key) + delta)
        self.tone.clamp()
        # update attunement: empathy-weighted increment (simplified)
        self.attunement += shifts[3] * 0.5
        self.attunement = max(0.0, self.attunement)

    def malrik_elenya_correlation(self) -> float:
        # Determine correlation state based on attunement thresholds
        thresholds = self.data['systems']['attunement']['thresholds']
        if self.attunement <= thresholds[0]:
            return self.data['systems']['npcCorrelation']['malrik_elenya']['default']
        if self.attunement <= thresholds[1]:
            return self.data['systems']['npcCorrelation']['malrik_elenya']['neutral']
        return self.data['systems']['npcCorrelation']['malrik_elenya']['positive']


if __name__ == '__main__':
    gm = GameMechanics()
    print('Initial tone:', gm.tone.as_dict())
    print('Initial attunement:', gm.attunement)
    # Example: player with empathy orientation picks choice 0 (strong empathy)
    gm.apply_choice('empathy', 0)
    print('After empathy choice:', gm.tone.as_dict())
    print('Attunement:', gm.attunement)
    print('Malrik/Elenya correlation:', gm.malrik_elenya_correlation())
