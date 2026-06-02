# Source Map

This folder was assembled by copying and adapting patterns from the existing repo.

## Core state and narrative

- Source: [limbic_ai/agent_core.py](d:/saoriverse-console/limbic_ai/agent_core.py)
- Target: [TheVillage/core/mind.py](d:/saoriverse-console/TheVillage/core/mind.py), [TheVillage/core/models.py](d:/saoriverse-console/TheVillage/core/models.py)
- Use: persistent state, self-model, goals, subsystems, reward, narrative, daily-cycle persistence, mission, and health metrics

## Village abstractions

- Source inspiration: [limbic_ai/agent_core.py](d:/saoriverse-console/limbic_ai/agent_core.py)
- Target: [TheVillage/core/villagers.py](d:/saoriverse-console/TheVillage/core/villagers.py), [TheVillage/core/scheduler.py](d:/saoriverse-console/TheVillage/core/scheduler.py)
- Use: villager roles, task proposal, autonomous daily work, global health updates

## Memory capsules

- Source: [src/relational_memory.py](d:/saoriverse-console/src/relational_memory.py)
- Target: [TheVillage/memory/capsule.py](d:/saoriverse-console/TheVillage/memory/capsule.py)
- Use: structured episodic memory objects

## Dictionary client

- Source: [src/emotional_os/shared/mw_dictionary.py](d:/saoriverse-console/src/emotional_os/shared/mw_dictionary.py)
- Target: [TheVillage/learning/mw_dictionary.py](d:/saoriverse-console/TheVillage/learning/mw_dictionary.py)
- Use: cached Merriam-Webster lookup with rate limiting

## Logging

- Source: [tools/feedback_store.py](d:/saoriverse-console/tools/feedback_store.py)
- Target: [TheVillage/learning/logging.py](d:/saoriverse-console/TheVillage/learning/logging.py)
- Use: append-only JSONL logs for conversation, feedback, and vocabulary events

## Interface

- Source: [limbic_ai/app.py](d:/saoriverse-console/limbic_ai/app.py)
- Target: [TheVillage/interface/api.py](d:/saoriverse-console/TheVillage/interface/api.py)
- Use: session-oriented web UI, JSON API, village overview, and villager detail reporting

## Dialogue layer

- New local layer: [TheVillage/interface/dialogue.py](d:/saoriverse-console/TheVillage/interface/dialogue.py)
- Use: natural-language village summaries and villager speech instead of raw diagnostics

## Language seeds

- Source reference: [emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json](d:/saoriverse-console/emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json)
- Target seed: [TheVillage/data/seed_vocabulary.json](d:/saoriverse-console/TheVillage/data/seed_vocabulary.json)
- Use: initial local vocabulary bootstrap