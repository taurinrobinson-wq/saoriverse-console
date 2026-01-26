# Engine Integration — Driving the Motif at Runtime

This doc gives concise patterns for wiring the `Velinor` fracture-tone and `Saori` dyads into a game audio engine. Choose one: sample layers (recommended) or procedural MIDI.

Design principles
- Treat `pressure` as the primary control value (0.0..1.0) mapped to a discrete state index (0..4 in `music_states.json`).
- Drive audio by: layered samples + gain/filters, or parametric synth (MIDI/oscillator) where velocity/duration emulate pressure.

1) Minimal Python trigger API (local testing)

Example: load `music_states.json`, set `pressure` then trigger sample or MIDI render.

Pseudo-Python:

```py
from json import load
states = load(open('velinor/music_prototypes/music_states.json'))['states']

def pressure_to_state(pressure):
    idx = int(pressure * (len(states)-1))
    return states[idx]

# call when game updates
state = pressure_to_state(game.REMNANTS_normalized)
# then trigger sample or synth with state['velocity'] and state['duration_ms']
```

2) Unity + FMOD (recommended for polished results)
- Build 5 stacked audio layers for Velinor recorded at increasing 'pressure'.
- Expose a single parameter `pressure` in FMOD (0..1) and map it to layer gain crossfades.
- Tie game variable `REMNANTS` to FMOD `pressure` via `EventInstance.setParameterByName("pressure", value)`.

Pseudo-C# (Unity):

```csharp
// binding game variable to FMOD event parameter
EventInstance inst = FMODUnity.RuntimeManager.CreateInstance("event:/velinor/motif");
inst.setParameterByName("pressure", pressureValue);
inst.start();
```

3) WebAudio / HTML5 (fast prototype)
- Use pre-rendered WAV layers (one per state). Crossfade with `GainNode` and simple lowpass for `mute_factor`.
- To morph continuously, crossfade neighbor layers and adjust `BiquadFilter.frequency` according to `mute_factor`.

Pseudo-JS:

```js
// load audio buffers for states[0..4]
// crossfade according to pressure = t
let i = Math.floor(t * (n-1));
let frac = (t*(n-1)) - i;
gain[i].gain.value = 1-frac;
gain[i+1].gain.value = frac;
filter.frequency.value = lerp(2000, 12000, 1 - states[i].mute_factor);
```

4) MIDI / Procedural synth
- Use the `generate_motifs.py` approach for rapid iteration, but for runtime you need a synth host (FluidSynth, WebAudioSynth, or platform synth).
- Map `velocity` -> note velocity, `duration_ms` -> gate time, and `mute_factor` -> a lowpass cutoff.

Notes and next steps
- For best expressive control, record 5 acoustic layers (Velinor half-muted->full) and implement crossfading.
- If you want I can generate reference WAVs from the MIDI (needs a synth or sample library) or create FMOD event JSON scaffolding next.
