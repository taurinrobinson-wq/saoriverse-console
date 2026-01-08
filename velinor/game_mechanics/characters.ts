// TypeScript version of simple game mechanics for Velinor.
// Minimal, framework-agnostic classes for use in frontend code.

export type ToneKeys = 'trust' | 'observation' | 'narrative' | 'empathy';

export interface ToneState {
  trust: number;
  observation: number;
  narrative: number;
  empathy: number;
}

export class Tone implements ToneState {
  trust = 0.5;
  observation = 0.5;
  narrative = 0.5;
  empathy = 0.5;

  clamp() {
    (['trust', 'observation', 'narrative', 'empathy'] as ToneKeys[]).forEach(k => {
      // @ts-ignore
      this[k] = Math.max(0, Math.min(1, this[k]));
    });
  }

  asObject(): ToneState {
    return { trust: this.trust, observation: this.observation, narrative: this.narrative, empathy: this.empathy };
  }
}

export class GameMechanics {
  data: any;
  tone: Tone;
  attunement: number;

  constructor(data: any) {
    this.data = data;
    this.tone = new Tone();
    this.attunement = 0;
  }

  applyChoice(orientation: string, choiceIndex: number) {
    const scene = this.data.miniGames.observationalScene;
    const order: ToneKeys[] = scene.toneOrder;
    const shifts: number[] = scene.toneShifts[orientation][choiceIndex];
    order.forEach((k, i) => {
      // @ts-ignore
      this.tone[k] += shifts[i];
    });
    this.tone.clamp();
    this.attunement += shifts[3] * 0.5; // empathy-weighted increment
  }

  malrikElenyaCorrelation(): number {
    const thresholds = this.data.systems.attunement.thresholds;
    const cfg = this.data.systems.npcCorrelation.malrik_elenya;
    if (this.attunement <= thresholds[0]) return cfg.default;
    if (this.attunement <= thresholds[1]) return cfg.neutral;
    return cfg.positive;
  }
}

// Example usage (import JSON as data and create GameMechanics)
// import data from '../markdowngameinstructions/malrik_elenya_coren.json'
// const gm = new GameMechanics(data);
// gm.applyChoice('empathy', 0);
// console.log(gm.tone.asObject(), gm.attunement, gm.malrikElenyaCorrelation());
