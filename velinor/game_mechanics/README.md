# Velinor Game Mechanics — Frontend Wiring

This folder contains minimal mechanics code and a small TypeScript API to wire the mechanics into frontend code.

Usage (TypeScript):

1. Import the factory:

```ts
import { createToneSnapshot } from 'velinor/game_mechanics/frontend_api';

const snap = createToneSnapshot();
console.log(snap.tone, snap.attunement);

// apply a choice (orientation: 'empathy'|'trust'|'observation'|'narrative')
const after = snap.applyChoice('empathy', 0);
console.log(after.tone, after.attunement, after.correlation);
```

Notes:
- This wiring is intentionally minimal and framework-agnostic.
- Your build/tooling may require `resolveJsonModule` or similar TS config to import JSON files.
