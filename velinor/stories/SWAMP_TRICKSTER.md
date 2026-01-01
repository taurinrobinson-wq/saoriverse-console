# Swamp Trickster (Design & Integration)

Brief: A duplicitous swamp informant that functions as a TONE mirror and gatekeeper to the thieves' hideout (Drossel). The encounter rewards players for emotional alignment, observation, and narrative presence while punishing blind trust or authoritarian alignment.

Files added:
- `swamp_trickster_scene.json` — Structured passages, choices, TONE effects, REMNANTS profile, and tone gates.

Design highlights:
- Every player choice carries an immediate TONE delta (`T`, `O`, `N`, `E`). Use these to update the player's hidden stats.
- Certain outcomes use `tone_checks` (min thresholds) to route to `true_breadcrumb`, `false_breadcrumb`, or intermediary branches (`partial_truth`, `challenge_branch`).
- A visible clue (lantern/moss) is triggered by an `O >= 2` check; honoring it leads to the true path.
- The false breadcrumb intentionally creates a swamp maze side-quest that can be converted into a small reward (minor glyph) to soften punishment.

Integration instructions:
1. If using `StoryBuilder` in `story_definitions.py`, import and parse `swamp_trickster_scene.json` and iterate passages:
   - `story.add_passage(name=..., text=..., npcs=[...], background=...)`
   - For each `choices` entry: `story.add_choice(from_passage_name=..., choice_text=..., to_passage_name=..., tone_effects=..., ...)`
2. Implement tone application logic in your engine if not present: when a player selects a choice, add each numeric delta to hidden TONE stats and persist to session state.
3. Implement `tone_checks` evaluation immediately after choice resolution; if a check matches, redirect to the gate outcome instead of the default `to` target.
4. Wire REMNANTS influence lines in your NPC manager so the trickster's influence on Kaelen/Drossel/Veynar changes downstream behaviors.

Suggested UX cues:
- When `O` reveals the lantern/moss clue, show a subtle UI hint: "Something about his lantern looks off." (no explicit reveal required)
- When a `true_breadcrumb` unlocks, show an ephemeral confirmation: "You feel a thread of truth in his words." (reinforces progress)
- When misled, reinforce with atmosphere (fog buries the path, longer travel timer) and add a small reward if they persisted (minor glyph).

Next options I can implement for you:
- Expand the JSON into `story_definitions.py` passages directly (ready to export with `build_story.py`).
- Produce a Twine-compatible JSON export from this scene.
- Flesh out `maze_sidequest` with 3 nodes and a minor glyph puzzle.
- Create a small unit-test simulating TONE profiles against the scene (useful for validation).

Tell me which next step you want and Ill proceed.