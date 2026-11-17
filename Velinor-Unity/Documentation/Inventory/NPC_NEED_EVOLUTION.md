# NPC Need Evolution – From What to Why to Story

## The Three Layers of Understanding

As Lioren interacts with NPCs across the game, her understanding deepens:

```
Layer 1: WHAT
├─ "Willy buys electrical salvage"
├─ "Tala trades for food ingredients"
└─ "Hunter wants copper wire"

Layer 2: WHY (Circumstance)
├─ "Willy is a scrapper—it's his trade"
├─ "Tala is rebuilding community through food"
└─ "Hunter is trying to survive"

Layer 3: STORY (History & Meaning)
├─ "Willy's mother was an engineer. He honors her through salvage."
├─ "Tala lost her family in the collapse. Food is how she rebuilds."
└─ "Hunter's wife died. He's trying to repair her music box."
```

Each layer unlocks through dialogue, time, gifts, and asking the right questions.

---

## Example NPC Arc: The Electrician

### Scene 1: First Meeting (Layer 1 - What)
```
Lioren: (exploring ruins)
Electrician: "Do you have any wire? Copper or aluminum?"
Lioren: "Why?"
Electrician: "My heating system is broken. Without it, I won't survive winter."

NPC Profile Revealed:
├─ Name: Elena
├─ Wants: Copper or aluminum wire
├─ Pays: 4 bits per wire (or will pay it back as labor)
└─ Immediate Need: Urgent (heating)
```

**Player learns:** This person needs wire for a practical reason.

**Player choice:**
- Trade wire for bits (neutral)
- Give wire freely (generous)
- Refuse (cold, but survive-focused)

### Scene 2: Follow-up (Layer 2 - Why)
```
After player gives or refuses:

If Given:
  Elena: "You saved my life. Thank you. In this cold, that means everything."
  
  Later dialogue option:
  Lioren: "Why is heating so important to you?"
  Elena: "I'm old. My body can't handle the cold anymore. 
          Without heat, I'd die in a week when winter comes."
  
  Revelation: Elena's circumstance is survival, not comfort.

If Refused:
  Elena: "I understand. You have to survive too."
  
  Later: She's shivering, less talkative. 
         The weight of her need is visible.
```

**Player learns:** Why this matters to her. Her circumstances.

### Scene 3: Relationship (Layer 3 - Story)
```
Weeks later (game time), after multiple interactions:

Lioren visits Elena regularly. Maybe brought her food once.

Lioren: "You mentioned the heating was broken. How did it break?"
Elena: "It's not really broken. It's... old. My late husband built it, 
        twenty-three years ago. After he died, I kept it running.
        But I'm not an engineer. I'm just trying to keep what he made alive."

New dialogue unlocks:
- "What was he like?"
- "Have you tried rebuilding it?"
- "Do you want help fixing it?"
```

**Player learns:** Elena's need isn't about comfort. It's about preserving memory.

### Possible Outcomes

#### Outcome A: Lioren Helps Repair It
```
Lioren and Elena fix the heating system together.

Elena: "It works. It actually works. I can hear my husband in this thing."

Flags set:
├─ elena_heating_repaired = true
├─ elena_relationship_tag = "friend"
└─ elena_future_help_available = true

Later: When Lioren faces the cold in the mountains,
       Elena gives her heavy coats and survival supplies.
```

#### Outcome B: Lioren Gives Her Wire (No Repair)
```
Elena uses the wire to get someone else to fix it.

Elena: "I got it working again. Barely. I had to trade almost everything,
        but it's warm again."

Flags set:
├─ elena_heating_working = true (but barely)
├─ elena_relationship_tag = "grateful"
├─ elena_debt_to_lioren = true
└─ elena_future_help_limited = true

Later: Elena can't help as much (she's stretched thin),
       but she remembers. Tells others about Lioren.
```

#### Outcome C: Lioren Refuses
```
Winter comes.

Elena: (shivering, ill, weaker)
"I understand. You're surviving too. I shouldn't have asked."

Flags set:
├─ elena_heating_status = "none"
├─ elena_health_deteriorating = true
└─ elena_relationship_tag = "distant"

Story continues anyway:
- Maybe Elena finds another source (less reliable)
- Maybe she doesn't survive winter (dark but real)
- Maybe she survives and later helps Lioren for a different reason
  (showing that refusing generosity doesn't earn punishment)
```

---

## NPC Preference Complexity Over Time

### Early Game: Simple Exchange
```
Willy Profile (First Encounter):
├─ Wants: Electrical salvage
├─ Pays: 1.5x multiplier
└─ Dialogue: "I'm a scrapper. You got any good salvage?"
```

### Mid Game: Circumstance Revealed
```
Willy Profile (After several trades):
├─ Wants: Electrical salvage
├─ Pays: 1.5x multiplier (but less negotiable now—he's struggling)
├─ New Info: Business is slow. Council isn't buying much salvage.
└─ New Option: Lioren can offer to help him find specific items
               (shifts from trader to ally)
```

### Late Game: Story Emerges
```
Willy Profile (After helping or deep dialogue):
├─ Wants: Specific items tied to past (Old Velharan tech)
├─ Pays: Variable (doesn't need bits anymore, needs connections)
├─ Story: His mother was an Old Velharan engineer who died in collapse
├─ New Options:
│  ├─ Help him find her research (no payment, but deep trust)
│  ├─ Trade salvage and ask about her (learning his story)
│  └─ Give him something of hers you find (emotional, not transactional)
└─ Relationship Shift: From "vendor" to "person with a past"
```

---

## Designing NPC Need Progression

### Template: NPCNeedProfile

```csharp
[CreateAssetMenu(menuName = "Velinor/NPCs/NPC Need Profile")]
public class NPCNeedProfile : ScriptableObject
{
    [SerializeField] private string npcId;
    
    [Header("LAYER 1: What Do They Want?")]
    [SerializeField] private NeedTier currentTier;
    [SerializeField] private List<string> desiredItemIds;
    [SerializeField] private ItemCategory desiredCategory;
    
    [Header("LAYER 2: Why Do They Need It?")]
    [Tooltip("Revealed after N interactions or specific dialogue")]
    [SerializeField] private CircumstanceReveal circumstance;
    [SerializeField] private int dialogueBeatsBeforeReveal;
    [SerializeField] private bool revealsAfterFirstGift;
    
    [Header("LAYER 3: What Story Does This Tell?")]
    [Tooltip("The deeper truth about this person")]
    [SerializeField] private BackstoryLayerReveal backstory;
    [SerializeField] private string backstoryTriggerCondition;
    [SerializeField] private List<BackstoryDialogueBeat> backstoryBeats;
    
    [Header("Outcomes Based on Player Choice")]
    [SerializeField] private NPCOutcome ifGiftReceived;
    [SerializeField] private NPCOutcome ifTradedWith;
    [SerializeField] private NPCOutcome ifRefused;
    [SerializeField] private NPCOutcome ifIgnored; // Over time
}

[System.Serializable]
public class CircumstanceReveal
{
    [TextArea] public string explanation;
    public string urgencyLevel; // "critical", "important", "moderate"
    public string emotionalContext; // "desperate", "hopeful", "resigned"
}

[System.Serializable]
public class BackstoryLayerReveal
{
    [TextArea] public string story;
    public List<string> triggerConditions; // "visited_their_home", "asking_about_past"
    public string revelationType; // "dialogue_prompt", "observed_action", "direct_conversation"
}

[System.Serializable]
public class NPCOutcome
{
    [TextArea] public string immediateResponse;
    public List<string> relationshipTagsGranted;
    public List<string> futureDialogueBranchesUnlocked;
    public List<string> futureInteractionsAvailable;
    public float chanceToHelpLaterUnexpectedly;
}
```

---

## Mechanic: NPC Circumstances Change

Over game time or based on player actions, NPC circumstances evolve:

```csharp
public class NPCCircumstanceSystem : MonoBehaviour
{
    // Change NPC's needs based on what happened
    
    public void UpdateNPCAfterGift(string npcId, string itemId)
    {
        // Elena got wire
        if (npcId == "elena" && itemId == "copper_wire")
        {
            // Her immediate need is satisfied
            GameFlags.Set("elena_needs_wire", false);
            GameFlags.Set("elena_heating_status", "repaired");
            
            // New need emerges: helping others
            // Or: deeper gratitude becomes available
            // Or: she's now more willing to help Lioren
            
            // Time-based: does she still need help?
            // Over days: does new problem emerge?
        }
    }
    
    public void UpdateNPCOverTime(string npcId)
    {
        // Simulate passage of time
        // Elena without heat → deteriorates
        // Willy without sales → gets desperate
        // Hunter without supplies → becomes more withdrawn
        
        // This makes Lioren's choices have visible consequences
    }
}
```

---

## Design Principle: Needs Feel Real

### ❌ What NOT to Do
```
NPC: "I need 5 copper wire."
     (Dialogue has no urgency, no story)
Player: Give wire
NPC: "Thanks! Here's your reward." (Quest complete)
```

### ✅ What TO Do
```
NPC: "I'm freezing. Without heat, I won't live through winter."
     (Urgent, specific, real consequence)
     (Dialogue reveals: she's old, alone, keeping deceased husband's work alive)
Player: Gives wire
NPC: (Visible relief) "You saved my life."
     (Later scene: shows her using the heat, surviving)
     (Much later: helps Lioren in an unexpected way—remembering)
```

---

## Preventing Transactional Relationships

### The Risk: Optimization
```
Player realizes: "Every NPC who helps me = give them something small"
                 "I've memorized who wants what and how much"
                 "This is just a resource matrix"
```

### The Solution: Variability
```
NPC Responses aren't 100% predictable:

1. Some gifts are deeply appreciated, others shrugged off
   (Different things matter to different people)

2. Help doesn't always create allies
   (Some people are broken by circumstance, can't reciprocate)

3. Some responses come later (weeks of game time)
   (Player forgets, then surprised by remembrance)

4. Some help is declined
   (NPC: "I appreciate it, but I can't accept charity.")

5. Some outcomes are bittersweet
   (You helped, it mattered, they're still struggling)
```

---

## Dialogue Integration: Asking About Needs

### New Dialogue Mechanic: Probe Questions

```
After meeting NPC:

Lioren: "Why do you need that?"

Options:
A) "That's personal."    → NPC deflects (reveal later)
B) (Listen)              → NPC explains (reveal now, one layer)
C) "I might help."       → NPC hopes (becomes more open)
D) (Say nothing)         → NPC assumes refusal (closes off)

This shouldn't be a quest marker. It's just... talking to someone.
```

### Progressive Dialogue: Story Through Conversation

```
First conversation:
- NPC: "I need wire."
- Lioren: "Why?"
- NPC: "For work."

Third conversation (after some trade):
- Lioren: "You've been asking for a lot of wire."
- NPC: "Yeah... I'm trying to rebuild something."

Fifth conversation (after helping):
- Lioren: "What are you rebuilding?"
- NPC: "My wife was an engineer. She designed heating systems.
        After she died, I kept hers running. It's breaking down.
        Every time I find wire, I try to keep it alive."

The story emerges slowly, through natural conversation.
```

---

## Outcomes: Making Choices Matter

### Type 1: Immediate (Visible)
```
You: Give wire to Elena
Result: She immediately repairs her heating
        Next scene: Her place is warm, she's visibly healthier
        Future: She mentions this saved her life
```

### Type 2: Delayed (Forgotten, Then Surprise)
```
You: Help Hunter find materials (weeks ago)
Result: Nothing happened, seemed pointless
Later: Different situation, you're in trouble
       Hunter appears: "You helped me once. My turn."
       Player surprise: "Oh! Right, that person!"
```

### Type 3: Complicated (Not What You Expected)
```
You: Give money to struggling person
Result: They're grateful, but also ashamed
        Relationship is complex, not purely positive
        They might later refuse help because of pride
```

### Type 4: Failure (Life is Hard)
```
You: Try to help someone
Result: Helps briefly, but their situation is too severe
        They're still struggling despite your effort
        Not a failure on your part—just the reality of scarcity
        But you tried, and they remember
```

---

## Architecture Summary

```
NPCStoryProfile
├─ Basic Info (name, ID)
├─ Current Tier (what they need now)
│  ├─ Items/categories wanted
│  ├─ Payment offered
│  └─ Urgency level
├─ Circumstance Layer (why they need it)
│  ├─ Explanation
│  ├─ Unlock conditions (dialogue, gifts, time)
│  └─ Emotional weight
├─ Backstory Layer (who they are)
│  ├─ The real story
│  ├─ Trigger conditions
│  └─ Multiple dialogue branches
└─ Outcomes (what happens based on choices)
   ├─ If gifted
   ├─ If traded
   ├─ If refused
   └─ If ignored

All layers drive:
- Relationship tags (ally, friend, grateful, distant)
- Future dialogue availability
- Unexpected help probability
- Circumstance changes over time
```

---

## Making It Feel Alive

### Rule 1: Needs Evolve
Nobody wants the same thing forever. As circumstances change, needs change.

### Rule 2: Stories Surprise
Don't telegraph backstory. Let players discover it through conversation.

### Rule 3: Gratitude Varies
Some people are moved by small gifts. Others need ongoing help. Some refuse help entirely.

### Rule 4: Help Isn't Always Enough
You can help someone and they still struggle. That's realistic.

### Rule 5: Memory Lasts
NPCs remember what you did. Sometimes it comes back. Sometimes it doesn't. But they don't forget.

---

## Implementation Phases

### Phase 1: Foundation
- ✓ Inventory system (exists)
- ✓ Trading system (just built)
- [ ] Giving/gift system (new)
- [ ] NPC circumstance tracking (new)

### Phase 2: Storytelling
- [ ] Circumstance reveals (dialogue integration)
- [ ] Backstory layers (long conversation chains)
- [ ] Time-based NPC updates (NPCs change over time)

### Phase 3: Relationship Depth
- [ ] Relationship tags (ally, friend, grateful)
- [ ] Future dialogue branches (based on tags)
- [ ] Unexpected help system (remember and return)

### Phase 4: Polish
- [ ] Visual feedback (gifts vs trades)
- [ ] Dialogue variety (not all NPCs respond identically)
- [ ] Consequence visibility (see how NPC's life changed)

---

## The Beauty of This Approach

One NPC need profile can drive:
- **Economy** (What they'll trade for)
- **Progression** (Unlocking their backstory)
- **Relationship** (Building trust)
- **Storytelling** (Understanding Velinor's collapse through their eyes)
- **Empathy** (Helping someone become real to the player)

All from asking: "What does this person need? And why?"
