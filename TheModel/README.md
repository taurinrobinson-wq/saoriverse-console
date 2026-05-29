# TheModel

TheModel is now a village simulator built from patterns already present in this repository. Each major subsystem is represented as a villager with its own role, mood, tasks, and daily responsibilities in service of one main mission.

The package still preserves your nine target components:

1. Persistent internal state
2. Self-model
3. Goal formation and persistence
4. Embodiment and environmental grounding
5. Competing internal subsystems
6. Internal reward signals
7. Narrative integration
8. Interaction interface
9. Learning and vocabulary expansion

## Structure

```
TheModel/
  core/           orchestration, state, villagers, scheduler, interpretation
  memory/         persistent session state and memory capsules
  embodiment/     simple action-consequence environment
  learning/       dictionary client, vocabulary learner, JSONL logs
  interface/      Flask UI, API, and village dialogue rendering
  data/           seed vocabulary
  runtime/        generated state, capsule, and learning files
  tests/          unit tests
```

## Reused Repo Patterns

- Persistent session-scoped mind loop from [limbic_ai/agent_core.py](d:/saoriverse-console/limbic_ai/agent_core.py)
- Memory capsule shape from [src/relational_memory.py](d:/saoriverse-console/src/relational_memory.py)
- Merriam-Webster client and rate limiting from [src/emotional_os/shared/mw_dictionary.py](d:/saoriverse-console/src/emotional_os/shared/mw_dictionary.py)
- JSONL learning logs from [tools/feedback_store.py](d:/saoriverse-console/tools/feedback_store.py)
- Session-oriented Flask interface from [limbic_ai/app.py](d:/saoriverse-console/limbic_ai/app.py)

## Village Layer

- Villagers live in [TheModel/core/villagers.py](d:/saoriverse-console/TheModel/core/villagers.py).
- The daily task engine lives in [TheModel/core/scheduler.py](d:/saoriverse-console/TheModel/core/scheduler.py).
- Dialogue rendering for the village metaphor lives in [TheModel/interface/dialogue.py](d:/saoriverse-console/TheModel/interface/dialogue.py).
- The main mission, health metrics, task backlog, villager states, and last run timestamp are persisted in [TheModel/core/models.py](d:/saoriverse-console/TheModel/core/models.py).

## Run

Install Flask if needed, then run:

```bash
cd D:\saoriverse-console
python -m TheModel.interface.api
```

The UI runs on http://localhost:5050.

To run one autonomous daily cycle from the command line:

```bash
cd D:\saoriverse-console
python -m TheModel.core.mind
```

That entrypoint is designed so you can wire it into OS scheduling tools.

## Merriam-Webster API

The learning layer checks these environment variables:

- `MW_DICTIONARY_API_KEY`
- `MERRIAM_WEBSTER_DICTIONARY_API_KEY`
- `MERIAM_WEBSTER_DICTIONARY_API_KEY`

Lookups are cached in-process and rate-limited per session to reduce load on the free non-commercial tier.

## Notes

This is a modular experimental architecture, not a claim of consciousness. Its value is that it now has continuity, stored state, unresolved questions, action-consequence updates, explicit vocabulary growth, a daily autonomous cycle, and a village-style dialogue layer for observing subsystem activity.