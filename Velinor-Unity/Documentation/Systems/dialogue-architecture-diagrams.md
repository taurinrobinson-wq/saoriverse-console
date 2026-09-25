# Dialogue System Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     DIALOGUE SYSTEM                          │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   JSON File      │
│  (Beats Array)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────────┐
│         DialogueManager.LoadBeatsFromJson()          │
│  Parses JSON into Dictionary<pid, BeatData>          │
│  Infers DialogueMode for each beat automatically     │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   BeatData Dict     │
         │  beat_1 → BeatData  │
         │  beat_2 → BeatData  │
         │  beat_3 → BeatData  │
         │  ...                │
         └─────────────────────┘
```

## Dialogue Flow - State Machine

```
START
  │
  ▼
┌─────────────────────────────────┐
│ DialogueManager.StartDialogue() │
│  Initialize with npcId, beat_id │
└────────────┬────────────────────┘
             │
             ▼
      ┌──────────────────┐
      │ DisplayBeat()    │
      │ Infer Mode       │
      └────────┬─────────┘
               │
        ┌──────┴──────────────────────────────┐
        │                                     │
        ▼                                     ▼
    NPCToNPC                           NPCToPlayer
    │                                  │
    ├─ Show Speaker                    ├─ Show Speaker
    ├─ Show Text                       ├─ Show Text
    └─ Auto-Advance                    └─ Show Choices
       OR [Continue]                      ▼
                                  Player Selects Choice
                                  │
                                  ▼
                           ┌──────────────────────┐
                           │ ResolveChoice()      │
                           │ Apply TONE effects   │
                           │ Apply REMNANTS eff.  │
                           │ Show result_text     │
                           │ Show Npc_response    │
                           │ Advance to target    │
                           └──────────┬───────────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │ Next Beat or  │
                              │ DIALOGUE_END  │
                              └───────┬───────┘
                                      │
        ┌─────────────────────────────┘
        │
        ▼
    [Loop Back to DisplayBeat]
    OR
    END DIALOGUE

PlayerInnerThought          PlayerActionChoice
    │                             │
    ├─ Hide Speaker              ├─ Show Speaker
    ├─ Show Text                 ├─ Show Action Prompt
    └─ Auto-Advance             └─ Show Choices
       OR [Continue]               ▼
                           Player Selects Action
                                  │
                                  ▼
                           Show result_text
                           Apply TONE/REMNANTS
                           Optional: Show NPC Response
                           Advance to target
```

## Dialogue Mode Decision Tree

```
                    ┌─────────────┐
                    │  BeatData   │
                    └──────┬──────┘
                           │
                ┌──────────┴──────────┐
                │                     │
           beat_type=?           active_speaker=?
                │                     │
        ┌───────┼───────┐             │
        │       │       │             │
    "npc_    "player_ "npc_      "Player"?
    shared"  posture" turn"        │
      │         │       │        ┌──┴──┐
      │         │       │        │     │
      ▼         ▼       ▼       Yes   No
      │    has choices?  │       │      │
      │      │      │     │       │      │
      │     Yes    No     │       ▼      ▼
      │      │      │     │      │      │
      │      ▼      ▼     ▼      │    NPCToNPC
      │    Player Player   │      │    (fallback)
      │    Action Inner    │      │
      │    Choice Thought  │      │
      │                    │      │
      │                    ▼      ▼
      │                 NPCToPlayer
      │
      └──────────────────────────────► NPCToNPC
         (always this mode)

RESULT:
  NPCToNPC → Auto-advance, no choices
  NPCToPlayer → Show choices, show NPC response
  PlayerInnerThought → Auto-advance, no speaker
  PlayerActionChoice → Show choices, optional NPC response
```

## Choice Resolution Flow

```
Player Selects Choice
        │
        ▼
┌─────────────────────────────┐
│ ResolveChoiceCoroutine()    │
└────────────┬────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ Show result_text?  │
    └───────┬────────────┘
            │
       ┌────┴────┐
       │ Yes     No
       │  │      │
       │  ▼      └─────────┐
       │ Display result    │
       │ Wait for render   │
       │                   │
       ▼                   ▼
    ┌──────────────────────────────┐
    │ Apply TONE Effects           │
    │ (Trust/Observation/etc.)     │
    │ via StatManager.Adjust()     │
    └──────────┬───────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │ Apply REMNANTS Effects       │
    │ (Resolve/Memory/etc.)        │
    │ Modify NPC Remnants object   │
    └──────────┬───────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │ Show NPC Response?           │
    │ (if NPCToPlayer or           │
    │  PlayerActionChoice)         │
    └─────────┬────────────────────┘
              │
         ┌────┴────┐
         │ Yes     No
         │  │      │
         │  ▼      │
         │ Display │
         │ response│
         │  & wait │
         │         │
         ▼         ▼
    ┌─────────────────────────┐
    │ Check target            │
    └────────┬────────────────┘
             │
        ┌────┴─────┐
        │           │
    "DIALOGUE_END" Other
        │           │
        ▼           ▼
    ┌────────┐   ┌──────────────┐
    │ Call   │   │ DisplayBeat()│
    │ End()  │   │ (Next Beat)  │
    └────────┘   └──────────────┘
```

## Effect Application System

```
TONE EFFECTS (Player Stats)
┌──────────────────────────────────┐
│ "tone": "T"                      │
│ "tone_effects": [                │
│   {"stat": "trust", "delta": 0.02}
│ ]                                │
└────────────┬─────────────────────┘
             │
             ▼
    ParseTone("trust") → ToneType.Trust
             │
             ▼
    StatManager.AdjustPlayerTone(
      ToneType.Trust,
      0.02,
      "activeNpcId"
    )
             │
             ▼
    Updates player's Trust tone with this NPC


REMNANTS EFFECTS (NPC Stats)
┌──────────────────────────────────┐
│ "remnants_effects": [            │
│   {                              │
│     "target": "activeNpcId",     │
│     "stat": "resolve",           │
│     "delta": 0.01                │
│   }                              │
│ ]                                │
└────────────┬─────────────────────┘
             │
             ▼
    target == "activeNpcId" ? → "Nima"
             │
             ▼
    ParseRemnantType("resolve") → RemnantType.Resolve
             │
             ▼
    StatManager.GetNpcRemnants("Nima")
             │
             ▼
    remnants.Set(RemnantType.Resolve, newValue)
             │
             ▼
    Nima's Resolve stat updated
```

## JSON to Runtime Object Mapping

```
JSON                          C# Object
──────────────────────────────────────────────

{
  "name": "...",            DialogueJson
  "startnode": "beat_1",    │
  "passages": [             │
    {                       ├─► BeatData[] passages
      "pid": "beat_1",      │   │
      "beat_type": "...",   │   ├─► string pid
      "active_speaker": "...",│   ├─► string beat_type
      "text": "...",        │   ├─► string active_speaker
      "choices": [          │   ├─► string text
        {                   │   ├─► BeatChoice[] choices
          "tone": "T",      │   │   │
          "label": "...",   │   │   ├─► string tone
          "playerLine": "...",│  │   ├─► string label
          "npc_response": "...",│ │   ├─► string npc_response
          "result_text": "...", │ │   ├─► string result_text
          "target": "beat_2",  │ │   ├─► string target
          "tone_effects": [...],│ │   ├─► BeatEffect[] tone_effects
          "remnants_effects": [...]│ ├─► RemnantsEffect[]
        }
      ]
    }
  ]
}
```

## UI Component Hierarchy

```
┌────────────────────────────────────────┐
│         DialoguePanel                  │
│  (CanvasGroup)                         │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ NPCNameText (TextMeshProUGUI)    │ │
│  │ "Nima"                           │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ DialogueText (TextMeshProUGUI)   │ │
│  │ Main dialogue content            │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │     Tone Choices (Buttons)       │ │
│  │  ┌──┐  ┌──┐  ┌──┐  ┌──┐         │ │
│  │  │T │  │O │  │N │  │E │         │ │
│  │  └──┘  └──┘  └──┘  └──┘         │ │
│  │ Trust  Obs.  Narr. Empa.        │ │
│  └──────────────────────────────────┘ │
│                                        │
└────────────────────────────────────────┘

T = Trust
O = Observation
N = Narrative Presence
E = Empathy
```

## System Integration Points

```
┌────────────────────┐
│  DialogueManager   │
└────────┬───────────┘
         │
    ┌────┴─────────────────────┐
    │                           │
    ▼                           ▼
┌─────────────────┐    ┌──────────────────┐
│  StatManager    │    │ DialogueUI       │
│                 │    │ Controller       │
│  • TONE stats   │    │                  │
│  • REMNANTS     │    │  • ShowSpeaker() │
│  • Thresholds   │    │  • ShowChoices() │
│  • Cascading    │    │  • ShowText()    │
│    Drift        │    │  • WaitFor...()  │
└─────────────────┘    └──────────────────┘
    │
    ├─ ToneType enum
    ├─ RemnantType enum
    └─ Remnants class

    Other Systems (to add):
    • CodexController (diary)
    • NPCStateManager (appearance)
    • FlagManager (conditions)
    • AudioManager (future)
```

## Dialogue Mode Decision Logic (Pseudocode)

```python
def infer_mode(beat):
    has_choices = len(beat.choices) > 0
    
    if beat.beat_type == "npc_shared":
        return DialogueMode.NPCToNPC
    
    if beat.active_speaker == "Player" and \
       beat.beat_type == "player_posture" and \
       not has_choices:
        return DialogueMode.PlayerInnerThought
    
    if beat.beat_type == "npc_turn" and has_choices:
        return DialogueMode.NPCToPlayer
    
    if beat.beat_type == "player_posture" and has_choices:
        return DialogueMode.PlayerActionChoice
    
    return DialogueMode.NPCToNPC  # fallback
```

## Performance Characteristics

```
Loading Phase:
  JSON Parse         → O(n) where n = # beats
  Mode Inference     → O(n)
  Dictionary Build   → O(n)
  Total Load Time    → < 10ms for typical dialogue file

Display Phase:
  ShowBeat()         → O(1) dictionary lookup + UI update
  Wait for Render    → Async coroutine (non-blocking)
  Choice Selection   → O(1) array access + effect apply

Effect Application:
  Tone Effects       → O(m) where m = # tone_effects in choice
  Remnants Effects   → O(k) where k = # remnants_effects in choice
  Typical: m,k < 5, so very fast

Memory:
  Typical Dialogue File: ~10-50 KB JSON
  Runtime Dictionary: ~100-500 KB (all beats loaded)
  Per-Beat Object: ~2-5 KB
  Per-Choice Object: ~1-2 KB
```

---

This architecture is designed to be:
- **Efficient** - O(1) lookups, no redundant parsing
- **Clear** - State machine with explicit modes
- **Extensible** - Easy to add new modes, effects, systems
- **Debuggable** - Console logs at every step
- **Unity-Native** - Uses coroutines, not passage graphs
