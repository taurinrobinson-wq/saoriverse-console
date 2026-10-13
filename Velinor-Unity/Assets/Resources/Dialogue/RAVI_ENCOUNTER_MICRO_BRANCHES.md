# Ravi Encounter - Micro-Branch Implementation

## Overview
Three micro-branch beats (1.21, 1.22, 1.23) have been added to `ravi_encounter_01.json` to handle Ravi's three question-ending NPC responses from Beat 1.

## Beat Structure

### Beat 1 (NPC Turn) → Routes to Micro-Branches

**Routing Logic:**
- **Trust (T)** response → Routes to **Beat 1.21**
  - "Oh… Anyone that I should be worried about?"
  
- **Observation (O)** response → Routes to **Beat 1.22**
  - "You would let me know if you saw or heard anything right?"
  
- **Narrative (N)** response → Routes to **Beat 1.23**
  - "Have you thought about what you might do for food and shelter and all that?"
  
- **Empathy (E)** response → Routes to **Beat 2** (skips micro-branches)
  - "Well… At least you seem genuine we need more people like that..."

---

## Micro-Branch Details

### Beat 1.21 - Trust Question
**Prompt:** "Anyone that I should be worried about?"

| Tone | Player Text | NPC Response |
|------|-------------|--------------|
| T | "No, not really." | *(blank - to be filled)* |
| O | "Not yet." | *(blank - to be filled)* |
| N | "Just a few colorful characters, nothing too concerning." | *(blank - to be filled)* |
| E | "If there were any concerning characters, I would let you know." | *(blank - to be filled)* |

**Routes to:** Beat 2

---

### Beat 1.22 - Observation Question
**Prompt:** "You would let me know if you saw or heard anything right?"

| Tone | Player Text | NPC Response |
|------|-------------|--------------|
| T | "Sure." | *(blank - to be filled)* |
| O | "I'm sure you mean saw or heard something sketchy. If that's the case then yes." | *(blank - to be filled)* |
| N | "If I feel like something is concerning, then I will let you know." | *(blank - to be filled)* |
| E | "I see you take your role seriously so yes of course I will do what I can to help." | *(blank - to be filled)* |

**Routes to:** Beat 2

---

### Beat 1.23 - Narrative Question
**Prompt:** "Have you thought about what you might do for food and shelter and all that?"

| Tone | Player Text | NPC Response |
|------|-------------|--------------|
| T | "I've thought about it. Daily. I just haven't really met anyone that seemed willing or able to provide those." | *(blank - to be filled)* |
| O | "Of course, I need to survive after all." | *(blank - to be filled)* |
| N | "That's the reason I even came to the marketplace... So far no luck though." | *(blank - to be filled)* |
| E | "It's definitely been on my mind. Hoping I can get established soon so I'm not digging around for scraps." | *(blank - to be filled)* |

**Routes to:** Beat 2

---

## Next Steps

**You need to fill in the NPC responses for beats 1.21, 1.22, and 1.23:**

For each micro-beat, provide Ravi's response to the player's answer. All responses should:
- Address the player's specific tone and answer
- Feel natural in the conversation flow
- Potentially use the `prompt_source` system to reference the player's answer

### Example Pattern
If you want each micro-beat's second NPC turn to reference what the player just said, use:
```json
"prompt_source": {
  "type": "previous_choice_response",
  "beat_id": <micro_beat_id>,
  "choice_field": "npc_response"
}
```

This would make the next beat show the player's answer before Ravi's follow-up question.

---

## File Changes Summary

- **Added Beats:** 1.21, 1.22, 1.23
- **Modified Beat:** 1 (updated routing logic for T, O, N choices)
- **Beat 1 Empathy Path:** Unchanged (still routes directly to Beat 2)
- **Total Dialogue Beats:** Now includes micro-branches for more granular player choice handling

---

## Testing Checklist

- [ ] Beat 1 → Select Trust → Should route to Beat 1.21
- [ ] Beat 1 → Select Observation → Should route to Beat 1.22
- [ ] Beat 1 → Select Narrative → Should route to Beat 1.23
- [ ] Beat 1 → Select Empathy → Should route to Beat 2 (skip micro-branches)
- [ ] All micro-beats → Should route to Beat 2
- [ ] NPC responses filled in for all micro-beat choices
- [ ] Dialogue flows naturally from Beat 1 → Micro-branches → Beat 2

---

## Integration with Dialogue Writer App

All changes have been made in the JSON file format. When opening this file in the Velinor Dialogue Writer app:
1. The Scene Library will show all beats including micro-branches
2. The beat navigation will properly show the decimal IDs (1.21, 1.22, 1.23)
3. All tone routing will be reflected in the UI

---

**Last Updated:** 2026-10-13
**Status:** Micro-branches created, NPC responses pending
