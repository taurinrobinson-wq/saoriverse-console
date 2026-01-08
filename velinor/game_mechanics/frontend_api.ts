import data from '../markdowngameinstructions/malrik_elenya_coren.json';
import { GameMechanics } from './characters';

// Simple factory to create a GameMechanics instance preloaded with JSON data
export function createMechanics() {
    return new GameMechanics(data);
}

// Convenience helper to expose a minimal API for UI wiring
export function createToneSnapshot() {
    const gm = createMechanics();
    return {
        tone: gm.tone.asObject(),
        attunement: gm.attunement,
        correlation: gm.malrikElenyaCorrelation(),
        applyChoice: (orientation: string, index: number) => {
            gm.applyChoice(orientation, index);
            return { tone: gm.tone.asObject(), attunement: gm.attunement, correlation: gm.malrikElenyaCorrelation() };
        }
    };
}

export default { createMechanics, createToneSnapshot };
