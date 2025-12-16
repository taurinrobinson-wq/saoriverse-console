# Velinor — Improvements & Implementation Checklist

This is a cleaned, human-readable summary and implementation checklist distilled from `Velinor_improvements.md`.
##

## Summary (what's in the file)

- Character notes and portrait prompts for: Nima, Ravi, Tovren, Dalen, Mariel, Sera, Korrin and more.
- A choice/consequences system (`story.add_choice`) with `tone_effects` and `npc_resonance` payloads.
- A proposal for two complementary systems:
  - `TONE` — the player stat system (Trust, Observation, Narrative Presence, Empathy).
  - `REMNANTS` — the NPC trait system (Resolve, Empathy, Memory, Nuance, Authority, Need, Trust, Skepticism).
- Mapping and pseudo‑code showing how TONE → REMNANTS correlations work, a multi‑NPC manager, and a simulation loop.
- Several example REMNANTS profiles and game integration notes.
- Many inline AI image prompt placeholders and several generator-error lines that need cleanup.
##

## Issues found (needs work)

1. Image placeholders and generator responses
   - Multiple `[imageX]` placeholders exist; some are repeated and several generator error lines like "I'm sorry, I'm having trouble responding to requests right now" appear interleaved. These should either be replaced with working asset file links (e.g., `assets/characters/nima.png`) or removed.

2. Formatting problems
   - Several code blocks are inline or malformed (e.g., `python  text` or escaped underscores). Convert these to fenced code blocks (```python ...```).
   - Excess backslash escapes (e.g., `\_`) in normal prose must be unescaped for Markdown.
   - Some headings are run together and need proper spacing and consistent heading levels.

3. Missing formal artifacts
   - NPC profiles (JSON or `npc_profiles.py`) are described but not present as actual files. Create `velinor/npc_profiles.json` or `velinor/npc_profiles.py`.
   - Influence map (`influence_map.json`) missing.
   - Choice helper functions (e.g., `apply_tone_to_all_npcs`, `apply_tone_to_remnants`) need real implementations in the codebase (suggest `velinor/engine/resonance.py`).

4. Integration gaps
   - `story.add_choice()` examples reference `story_definitions.py` and `story` API—verify these APIs exist and document required function signatures.
   - Tool unlock conditions (e.g., *Chalk of Paths*, *Thread of Memory*, *Trial Token*) should be encoded in a `tools.json` or integrated into the engine.

5. Testing / Simulation
   - Provide a small simulation harness (`velinor/tools/simulate_resonance.py`) that runs sample encounters and outputs a CSV/JSON timeline for trait changes.

6. Documentation polish
   - Add cross‑links to `CHOICE_CONSEQUENCES_GUIDE.md`, `SCENE_COMPOSITION_GUIDE.md`, etc. Confirm those files are present (or create stubs).
##

## Suggested Implementation Plan (short)

1. Create canonical NPC profiles file: `velinor/data/npc_profiles.json` with entries for Ravi, Nima, Tovren, Dalen, Mariel, Sera, Korrin.
2. Create `velinor/data/influence_map.json` containing the ripple values per NPC.
3. Implement `velinor/engine/resonance.py` containing:
   - `apply_tone_to_remnants(npc_profile, tone_effects, correlation_map)`
   - `apply_tone_to_all_npcs(npc_profiles, tone_effects, influence_map)`
   - `simulate_encounters(npc_profiles, influence_map, encounters)`
4. Clean `Velinor_improvements.md` (or replace with this cleaned file) and remove generator noise.
5. Add small unit tests in `velinor/tests/test_resonance.py` exercising the example runs.
6. Wire tool unlock conditions into `velinor/engine/tools.py` or a `velinor/data/tools.json`.
7. Replace image placeholders with actual files in `velinor/assets/characters/` and update the markdown to reference them.
##

## Quick cleaned examples (copyable)

### Example NPC profile (JSON)

```json
{
  "Ravi": {
    "sphere": ["Merchants"],
    "trait": "Trust",
    "remnants": {
      "resolve": 0.6,
      "empathy": 0.5,
      "memory": 0.4,
      "nuance": 0.3,
      "authority": 0.3,
      "need": 0.5,
      "trust": 0.7,
      "skepticism": 0.2
    },
    "influence": "Offers map tools if trust is high",
    "ripple": {"Nima": -0.1}
  }
```text
```



### Example resonance application (Python stub)

```python
def apply_tone_to_remnants(npc_profile: dict, tone_effects: dict, correlation: dict) -> dict:
    for tone_stat, delta in tone_effects.items():
        if tone_stat in correlation:
            for trait in correlation[tone_stat]['raise']:
                npc_profile[trait] = npc_profile.get(trait, 0) + delta
            for trait in correlation[tone_stat]['lower']:
                npc_profile[trait] = npc_profile.get(trait, 0) - delta
    return npc_profile
```


##

## What I can do next (pick any, I can run all)

- Create `velinor/data/npc_profiles.json` and `velinor/data/influence_map.json` from the profiles in the file.
- Implement `velinor/engine/resonance.py` and add tests.
- Replace the noisy original `Velinor_improvements.md` with a cleaned version (this file) or update both in-place.
- Generate the simulation harness and produce a sample output for your review.

Tell me which of the next steps you want me to take and I will proceed (I can start with creating the canonical JSON and the resonance implementation).
