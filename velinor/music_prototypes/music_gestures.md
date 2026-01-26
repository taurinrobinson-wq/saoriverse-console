# Music Gestures and Guitar Tabs — Velinor & Saori

Summary
- Velinor: fracture-tone motif built on a half-muted/wiry string that progressively rings into a full D octave.
- Saori: D minor pendulum — alternate `D` octaves and `F–A` dyads (ritual, contained).

Guitar tablature (simple)

Velinor (half-fretted -> pressure ramp)
- Target pitches: lower D (D3) and upper D (D4).
- Suggested frets:

Standard tuning strings (low -> high): 6:E2 5:A2 4:D3 3:G3 2:B3 1:E4

Velinor motif (repeat, gradually increase pressure):

e|----------------------|
B|--3-----3-----3-------|  (upper D = B string, fret 3)
G|----------------------|
D|--0--0--0--0--0--0----|  (lower D = D string open)
A|----------------------|
E|----------------------|

Articulation notes:
- Start with light finger touch on the B3 fret 3 (half-fret / muted), palm-mute the D string for a tinny sound.
- Gradually increase finger pressure on the B-string note across repeats until it rings.
- Vary pick attack: start soft and slightly behind the bridge for a metallic timbre, move toward center as motif resolves.
- Optionally add harmonic on upper D (touch at 12th or 7th fret) when reaching `near_presence`.

Saori motif (D minor dyads — pendulum)

e|-------------------------|
B|--3------3------3--------|  (upper D)
G|--2------2------2--------|  (A3 for the dyad)
D|--0------3------0--------|  (lower D then F3)
A|-------------------------|
E|-------------------------|

Pattern: D-octaves (D3+D4) -> F3+A3 dyad -> repeat. Keep attack precise and dry (minimal reverb).

Performance tips
- Saori: play with strict rhythmic spacing; leave silence between dyads to create the watchful pendulum.
- Velinor: treat pressure as the performance parameter — small per-iteration changes should be perceptible but subtle.

Notation legend
- Half-fret: press the string lightly (not intended to produce full fret contact) to create a flanged/wiry tone.
- Palm-mute: rest the edge of the picking hand lightly on the bridge to reduce sustain and add metallic timbre.
- Harmonic: touch lightly above the fret to elicit bell-like overtone when appropriate.

Link between gesture and in-game parameter
- Map the technique to the `mute_factor` and `velocity` in `music_states.json`.
- When game updates state, instruct performer or sample-layerer to change pressure/palm-mute intensity accordingly.
