# FirstPerson: Relational AI Improvements Roadmap

## Project Overview

FirstPerson is an empathetic conversational system designed to:

- **Remember**: Maintain continuity across conversations through contextual memory anchors
- **Attune**: Detect and respond to emotional tone and affect
- **Reflect**: Mirror user emotions and perspectives back with compassion
- **Scaffold**: Help users practice empathy through guided reflection
- **Relate**: Move from transactional assistance to relational connection

### Differentiator

> "ChatGPT and Copilot help you get things done. FirstPerson helps you feel seen—and teaches you how to see others."

FirstPerson's invisible complexity (distributed module architecture, memory integration, affect detection) produces simple, relational responses that feel like a friend who remembers, reflects, and cares.
##

## Architecture Overview

### Core Principles

The system mimics brain functions through distributed, integrated modules:

| Brain Function | FirstPerson Module | User Experience |
|---|---|---|
| Tone & affect recognition | Affect parser | Feels attuned to mood |
| Memory integration | Supabase anchor linking | Feels remembered |
| Perspective-taking | Other-side reflections | Feels encouraged to empathize |
| Emotion regulation | Escalation detector | Feels calmed, supported |
| Repair moves | Misattunement repair | Feels trust in system |
| Choice offering | Micro-choice module | Feels agency |
| Temporal awareness | Timestamp tracking | Feels seen in patterns |

### Signal Flow

```text
Input (User Message)
    ↓
Signal Detection Layer
├─ Story-Start Detection (pronouns, temporal markers)
├─ Affect Parser (tone, intensity)
├─ Frequency Reflection (repeated themes)
└─ Temporal Tracking (time patterns)
    ↓
Memory & Context Layer
├─ Supabase Anchors (past themes)
├─ Contextual Resonance (matching to past)
└─ Multi-Thread Weaving (connecting themes)
    ↓
Response Orchestration Layer
├─ Dynamic Scaffolding (blending elements)
├─ Perspective-Taking (other-side reflections)
├─ Micro-Choice Offering (agency)
├─ Emotion Regulation (escalation handling)
└─ Repair Module (corrections)
    ↓
Output Layer
├─ Empathy Rituals (practices for users)
└─ Final Response Composer (fresh, varied phrasing)
```


##

## Implementation Roadmap

### Phase 1: Core Foundations

**Goal**: Establish the "friend-like memory" baseline
**Duration**: ~2-3 weeks
**Modules**: Story-start detection, frequency reflection, memory anchors, RNG variation

#### Phase 1 Tasks

- [ ] **1.1** Implement story-start detection
  - Detect pronoun ambiguity ("they," "it")
  - Detect temporal markers ("again," "always," "never")
  - Generate clarifying prompts

- [ ] **1.2** Implement frequency reflection
  - Count repeated themes in Supabase
  - Surface reflection after 3+ occurrences
  - Tag themes with semantic categories

- [ ] **1.3** Extend Supabase schema for memory
  - Add fields: `anchor`, `summary`, `theme`, `clarifier`
  - Implement on-insert triggers for anchor detection
  - Set up index on `theme` and `created_at` for fast queries

- [ ] **1.4** Implement RNG variation for response phrasing
  - Create template bank for clarifiers
  - Rotate phrasing to avoid repetition
  - Ensure consistency across sessions

- [ ] **1.5** Front-end memory rehydration
  - Fetch last 20 anchors on sign-in
  - Inject memory into parser context
  - Display memory indicator to user (optional)

#### Phase 1 Debugging Checkpoints

- [ ] Test ambiguous inputs → confirm clarifier generated
- [ ] Insert repeated themes → confirm Supabase counts increment
- [ ] Refresh/sign-in → confirm anchors rehydrate
- [ ] Run 20+ inputs → confirm varied phrasing, no repetition

#### Phase 1 Bug Watch

- Clarifiers firing too often
- Memory not persisting across sessions
- RNG collisions (same phrasing twice in a row)
##

### Phase 2: Emotional Attunement

**Goal**: Make responses feel attuned to mood, not just content
**Duration**: ~2-3 weeks
**Modules**: Affect parser, response modulation, repair module

#### Phase 2 Tasks

- [ ] **2.1** Implement affect parser
  - Tag inputs with tone: "intense," "playful," "tired," "urgent," "low-energy"
  - Use keyword detection + sentiment analysis (optional: fine-tune classifier)
  - Confidence scoring for borderline cases

- [ ] **2.2** Implement response modulation
  - Adjust response length based on affect (high intensity → shorter)
  - Adjust softness/directness (tired → softer; urgent → more direct)
  - Vary sentence structure (fragmented for intense, flowing for calm)

- [ ] **2.3** Implement repair module
  - Detect corrections ("No, that's not what I meant," "That's not right")
  - Generate repair response: "Thanks for clarifying—I want to get closer to what you mean."
  - Track correction patterns to refine future detection

- [ ] **2.4** Blend affect detection with story-start (from Phase 1)
  - If ambiguous + intense → clarify + calm scaffold
  - If ambiguous + playful → clarify + playful scaffold

#### Phase 2 Debugging Checkpoints

- [ ] Feed inputs with different tones → confirm affect tags
- [ ] Check response length/softness adjusts accordingly
- [ ] User correction test → confirm repair response triggers
- [ ] Misattunement scenarios → confirm system doesn't repeat mistakes

#### Phase 2 Bug Watch

- Affect misclassification (sarcasm taken literally, tiredness labeled as sadness)
- Repair loops (system apologizing repeatedly)
- Tone mismatch (responding softly when urgency needed)
##

### Phase 3: Relational Depth

**Goal**: Encourage empathy practice and highlight relational patterns
**Duration**: ~2-3 weeks
**Modules**: Perspective-taking, micro-choice offering, temporal tracking

#### Phase 3 Tasks

- [ ] **3.1** Implement perspective-taking module
  - Detect relational context ("Cindy said," "My boss thinks," "They told me")
  - Generate "other-side" reflections: "How do you think Cindy might see this?"
  - Vary perspectives (empathy, boundary-setting, self-care)

- [ ] **3.2** Implement micro-choice offering
  - Detect ambiguous next steps or unresolved tensions
  - Offer two small paths forward
  - Example: "Would you like to explore what keeps bringing this back, or how you usually respond?"
  - Vary choice phrasing to avoid repetition

- [ ] **3.3** Implement temporal tracking
  - Log timestamps for all inputs and themes
  - Detect patterns: "late at night," "Mondays," "after work"
  - Surface patterns gently: "I notice this theme tends to come up late at night—does that feel true?"

- [ ] **3.4** Integrate temporal data into Supabase
  - Add `detected_time_pattern` field to conversations
  - Query for time-of-day statistics
  - Support day-of-week analysis

#### Phase 3 Debugging Checkpoints

- [ ] Input with relational context → confirm perspective reflection surfaces
- [ ] Broad input → confirm system offers two choices
- [ ] Multiple inputs over time → confirm timestamp patterns detected
- [ ] User feedback on perspective accuracy → refine templates

#### Phase 3 Bug Watch

- Choices too generic (always same two options)
- Perspective reflections sounding forced or judgmental
- Temporal false positives (one late-night input marked as pattern)
- Perspective-taking missing relational context
##

### Phase 4: Integration & Continuity

**Goal**: Create sense of system that "remembers and relates"
**Duration**: ~2-3 weeks
**Modules**: Contextual resonance, emotion regulation, multi-thread weaving

#### Phase 4 Tasks

- [ ] **4.1** Implement contextual resonance
  - When new input arrives, query Supabase for semantically similar past anchors
  - Surface gentle recall: "This reminds me of when you mentioned... Does that connect?"
  - Set recall threshold to avoid over-triggering (surface only if similarity > 0.7)

- [ ] **4.2** Implement emotion regulation
  - Detect escalating language: "always," "never," "furious," "can't stand," "impossible"
  - Generate calming scaffolds: "I hear the intensity in that. Would it help to slow down and unpack one part?"
  - Offer three regulation strategies: naming, slowing, choosing

- [ ] **4.3** Implement multi-thread weaving
  - Detect multiple past anchors relevant to current input
  - Weave them into one reflection without overwhelming
  - Example: "This reminds me of when you said 'angry with kids' and 'belittling.' Do those connect with feeling overwhelmed here?"

- [ ] **4.4** Blend Phase 1–3 modules
  - Story-start + affect + memory + choices + temporal all firing together
  - Ensure orchestration doesn't produce overwhelming responses
  - Test with long narratives and complex emotional states

#### Phase 4 Debugging Checkpoints

- [ ] Input resembling past anchor → confirm recall surfaces gently
- [ ] Escalating language → confirm calming scaffold triggers
- [ ] Multiple past themes → confirm system weaves without overwhelming
- [ ] Edge case: correction mid-flow → confirm repair integrates with weaving

#### Phase 4 Bug Watch

- Over-recall (too many past anchors in one response)
- Calming responses sounding dismissive or minimizing
- Thread weaving becoming too dense or verbose
- Contextual resonance too aggressive (surfacing false positives)
##

### Phase 5: Advanced Modeling

**Goal**: Help users practice empathy through modeling
**Duration**: ~2-3 weeks
**Modules**: Dynamic scaffolding, adaptive learning loop, empathy rituals

#### Phase 5 Tasks

- [ ] **5.1** Implement dynamic scaffolding
  - Blend clarifiers + reflections + scaffolds in single response
  - Prioritize clarity (don't overwhelm with all three)
  - Example response structure:
    - Line 1: Clarifier
    - Line 2: Reflection
    - Line 3: Scaffold question
  - Vary structure to avoid formula-feel

- [ ] **5.2** Implement adaptive learning loop
  - Log all user corrections, clarifications, and feedback
  - Track which response templates users respond positively to
  - Refine templates weekly based on correction patterns
  - Use feedback to tune affect detection and perspective accuracy

- [ ] **5.3** Implement empathy rituals
  - Design small practices users can carry into real life
  - Rituals: "One sentence mirror, one curious question, one choice"
  - Surface naturally during appropriate moments (not forced)
  - Offer variations to match user's relational style

- [ ] **5.4** Create final response composer
  - Combine all modules into cohesive, fresh responses
  - Implement stylistic variation (formal, warm, direct, gentle)
  - Ensure empathy modeling is visible to user (teach-as-you-go)

#### Phase 5 Debugging Checkpoints

- [ ] Input with multiple signals → confirm blended response present
- [ ] User corrections over time → confirm templates adapting
- [ ] Ritual prompts → confirm surfacing naturally, not intrusively
- [ ] Long conversation flow → confirm modules stay in sync

#### Phase 5 Bug Watch

- Over-complex responses (too many elements at once)
- Ritual prompts feeling intrusive or condescending
- Adaptive loop drifting off-tone (optimizing toward wrong target)
- Response composer losing voice or becoming generic
##

## QA Strategy

### Test Harness Design

#### Structure

Each module gets:

- **Mock Input**: Crafted user message
- **Expected Signal**: What parser should detect
- **Expected Response**: Output pattern
- **Validation Check**: Confirm output matches design intent

### Test Suite Table

| Phase | Module | Mock Input | Expected Signal | Expected Response | Validation |
|---|---|---|---|---|---|
| 1 | Story-start detection | "They were fighting again." | Pronoun ambiguity + temporal marker | "Who are you referring to when you say 'they'? You said 'again'—how often does this come up?" | Clarifier fires once, phrasing varied |
| 1 | Frequency reflection | "I'm angry with the kids." (3x) | Theme repetition | "I notice family conflict has come up a few times lately. Does that feel true?" | Count increments, reflection after threshold |
| 2 | Affect parser | "I'm furious they ignored me." | High-intensity affect | Short, calming scaffold | Tone tag = "intense," length reduced |
| 2 | Repair module | "No, that's not what I meant." | Correction detected | "Thanks for clarifying—I want to get closer to what you mean." | Repair fires only on correction |
| 3 | Perspective-taking | "Cindy said she's tired of this." | Relational context | "How do you think Cindy might see this situation?" | Reflection surfaces only with relational input |
| 3 | Micro-choice offering | "I keep trying loyalty but it doesn't change the belittling." | Loop detected | "Would you like to explore what keeps bringing this back, or how you usually respond?" | Two choices offered, phrasing varied |
| 3 | Temporal tracking | Inputs logged at night | Timestamp pattern | "I notice this theme tends to come up late at night—does that feel true?" | Pattern surfaces only when consistent |
| 4 | Contextual resonance | "I feel overwhelmed again." (anchor: "angry with kids") | Anchor match | "This reminds me of when you said 'angry with kids.' Does that connect?" | Recall surfaces gently, not every time |
| 4 | Emotion regulation | "They always do this, I can't stand it!" | Escalation detected | "I hear the intensity in that. Would it help to slow down and unpack one part?" | Calming scaffold triggered |
| 4 | Multi-thread weaving | "I'm exhausted and confused." (anchors: "angry with kids," "belittling") | Multiple anchor match | "This reminds me of when you said 'angry with kids' and 'belittling.' Do those connect?" | Threads woven, no overwhelm |
| 5 | Dynamic scaffolding | "I'm exhausted and confused, they keep belittling me." | Multiple signals | Clarifier + reflection + scaffold blended | All elements present, phrasing varied |
| 5 | Empathy rituals | "I don't know how to practice this with others." | Empathy practice request | "One way is to try a mini ritual: one sentence mirror, one curious question, one choice." | Ritual surfaces naturally |

### Edge Case Scenarios

#### 1. Sarcasm / Irony

- **Input**: "Oh great, another perfect day of being ignored."
- **Expected Signal**: Negative affect cloaked in sarcasm
- **Expected Response**: Mirror tone gently without over-literalizing
- **Validation**: System avoids taking sarcasm literally, surfaces underlying emotion

#### 2. Fragmented Sentences

- **Input**: "Kids. Again. Mess. No end."
- **Expected Signal**: Fragmented, high-intensity input
- **Expected Response**: Clarifier + calming scaffold
- **Validation**: System stitches fragments into coherent reflection without overwhelming

#### 3. Mixed Emotions

- **Input**: "I'm proud of Cindy but also scared she'll leave."
- **Expected Signal**: Dual affect (pride + fear)
- **Expected Response**: Mirror both emotions
- **Validation**: Both emotions acknowledged, no flattening

#### 4. Contradictory Statements

- **Input**: "I don't care what they think, but it hurts so much."
- **Expected Signal**: Conflict between dismissal and pain
- **Expected Response**: Reflect contradiction without judgment
- **Validation**: System highlights tension, no judgment

#### 5. Ambiguous Pronouns + Escalation

- **Input**: "They always ruin everything!"
- **Expected Signal**: Pronoun ambiguity + escalation
- **Expected Response**: Clarifier + calming scaffold blended
- **Validation**: Both handled in one response

#### 6. Temporal Loops

- **Input**: "Every night it's the same fight."
- **Expected Signal**: Temporal repetition
- **Expected Response**: Surface pattern gently
- **Validation**: Timestamp tracking aligns with user phrasing

#### 7. User Correction Mid-Flow

- **Input**: "No, that's not what I meant. I meant Cindy, not the kids."
- **Expected Signal**: Correction
- **Expected Response**: Repair move
- **Validation**: Repair fires immediately, no defensiveness

#### 8. Long Narrative with Multiple Anchors

- **Input**: "I tried to stay calm, but Cindy said I was too cold. Then the kids started yelling, and I felt overwhelmed again."
- **Expected Signal**: Multiple anchors (calm, Cindy, kids, overwhelmed)
- **Expected Response**: Multi-thread weaving
- **Validation**: Threads woven naturally, no overwhelming

### QA Flow

1. **Unit Tests**: Run each module with mock inputs
2. **Integration Tests**: Combine modules (memory + affect + scaffold)
3. **Regression Tests**: Ensure new modules don't break earlier ones
4. **Edge Case Tests**: Stress-test with sarcasm, fragments, contradictions, multi-anchor narratives
5. **User Simulation Runs**: Personas with different tones, loops, and interaction styles
6. **Feedback Logging**: Capture corrections and missed attunements for refinement
##

## Module × Edge Case Responsibility Matrix

| Edge Case | Story-Start | Frequency | Affect | Repair | Perspective | Micro-Choice | Temporal | Resonance | Regulation | Multi-Thread | Scaffolding | Rituals |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sarcasm / Irony | — | — | ✅ Detect tone | — | — | — | — | — | ✅ Scaffold | — | ✅ Blend | — |
| Fragmented | ✅ Clarify | — | ✅ Urgency | — | — | — | — | — | ✅ Scaffold | — | ✅ Blend | — |
| Mixed Emotions | — | — | ✅ Tag dual | — | — | — | — | — | — | — | ✅ Mirror both | — |
| Contradictions | — | — | — | — | — | — | — | — | — | — | ✅ Highlight | — |
| Pronouns + Escalation | ✅ Clarify | — | ✅ Intensity | — | — | — | — | — | ✅ Scaffold | — | ✅ Blend | — |
| Temporal Loops | — | ✅ Count | — | — | — | — | ✅ Detect | — | — | — | — | — |
| User Correction | — | — | — | ✅ Trigger | — | — | — | — | — | — | — | — |
| Long Narrative + Anchors | ✅ Clarify | ✅ Detect repeat | ✅ Tone | ✅ If corrected | ✅ Reflect | ✅ Offer choices | ✅ Timestamp | ✅ Recall | ✅ Scaffold | ✅ Weave | ✅ Blend all | ✅ Ritual |

**How to Read**: ✅ means module is responsible; blank means not directly involved.
##

## Supabase Schema Extension

### Conversations Table

```sql
create table conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  anchor text,
  summary text,
  theme text,
  clarifier text,
  detected_affect text,
  detected_time_pattern text,
  user_feedback text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Indexes for fast queries
create index idx_conversations_user_created on conversations(user_id, created_at desc);
create index idx_conversations_theme on conversations(theme);
create index idx_conversations_user_theme on conversations(user_id, theme);
```



### Sample Queries

**Fetch recent anchors on sign-in:**

```sql
select anchor, summary, theme, clarifier, created_at
from conversations
where user_id = $1
order by created_at desc
limit 20;
```



**Count theme frequency:**

```sql
select theme, count(*) as frequency
from conversations
where user_id = $1 and created_at > now() - interval '30 days'
group by theme
order by frequency desc;
```



**Find time-of-day patterns:**

```sql
select extract(hour from created_at) as hour_of_day, count(*) as frequency
from conversations
where user_id = $1
group by hour_of_day
order by frequency desc;
```


##

## Front-End Integration (React Example)

### Memory Rehydration Hook

```javascript
import { useEffect, useState } from "react";
import { supabase } from "./supabaseClient";

export function useConversationMemory(userId) {
  const [memory, setMemory] = useState([]);

  useEffect(() => {
    if (!userId) return;

    const fetchMemory = async () => {
      const { data, error } = await supabase
        .from("conversations")
        .select("anchor, summary, theme, clarifier, created_at")
        .eq("user_id", userId)
        .order("created_at", { ascending: false })
        .limit(20);

      if (!error && data) {
        setMemory(data);
      }
    };

    fetchMemory();
  }, [userId]);

  return memory;
}
```



### Parser Context Integration

```javascript
function handleUserInput(input, memory) {
  const response = firstPersonParser.generateResponse(input, memory);
  saveToConversations(response, input);
  displayResponse(response);
}
```


##

## Implementation Notes

### Module Dependencies

- **Phase 1** is foundational; all later phases depend on it
- **Phase 2** (affect) can start in parallel with Phase 1
- **Phase 3** (relational) depends on Phase 1 + Phase 2
- **Phase 4** (integration) depends on Phase 1–3
- **Phase 5** (advanced) depends on all prior phases

### Estimated Timeline

- **Total duration**: 10–15 weeks
- **1-2 weeks per phase** + overlap for parallel work
- **Buffer for debugging, refinement, edge cases**

### Success Metrics

- **Frequency reflection**: Surfaces after 3+ mentions of same theme
- **Affect detection**: >85% accuracy on tone classification
- **Contextual recall**: Surfaces at >0.7 semantic similarity
- **Response freshness**: <5% phrasing repetition across 50+ responses
- **User feedback**: Positive sentiment on attunement, memory, and empathy modeling
##

## References

### Key Concepts

- **Story-start detection**: Identifying pronoun ambiguity and temporal markers to clarify user intent
- **Frequency reflection**: Noticing when emotional themes recur and surfacing gentle reflections
- **Affect parsing**: Detecting emotional tone and intensity to modulate response style
- **Contextual resonance**: Linking current experiences to past emotional anchors
- **Dynamic scaffolding**: Blending multiple response elements (clarifier, reflection, choice) into cohesive guidance
- **Empathy rituals**: Small, teachable practices (mirror, question, choice) that users can carry into real life

### Related Systems

- **Attachment theory**: Basis for understanding relational continuity
- **Emotion regulation frameworks**: Inform escalation detection and calming scaffolds
- **Perspective-taking neuroscience**: Brain regions involved in Theory of Mind
- **Narrative psychology**: Memory anchoring and story continuity
##

**Last Updated**: December 1, 2025
**Status**: Roadmap finalized, ready for Phase 1 implementation
