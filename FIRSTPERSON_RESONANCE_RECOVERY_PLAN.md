# FirstPerson/FirstPerson-Web: Architectural Interrogation & Resonance Recovery Plan

## Executive Summary

Your system has **good bones** but is missing **critical connective tissue**. You've built separate layers for emotional parsing, memory, templates, and response generation—but they operate mostly independently. The result feels like a sophisticated chatbot rather than a person thinking and feeling in real-time.

This document walks through the architectural interrogation prompts systematically to diagnose where emotional resonance is breaking down, then proposes a **minimal, high-impact** intervention.

---

## Stage 1: Architecture Map (Explicit)

### Current System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FirstPerson/FirstPerson-Web                  │
└─────────────────────────────────────────────────────────────────┘

FRONTEND (Next.js / TypeScript)
├── /app/chat              (Chat interface)
├── /app/api               (Client-side API routes)
├── /components
│   ├── EmotionDetector.tsx    (Visual emotion feedback)
│   └── ResponseMetadata.tsx   (Metadata display)
└── State management via Zustand

    ↓ (HTTP/WebSocket)

API GATEWAY (FastAPI)
├── firstperson_api.py
│   ├── /api/transcribe     (Audio → Text via Whisper)
│   ├── /api/chat           (Text → Response)
│   └── /api/synthesize     (Text → Audio)
└── Initializes:
    ├── AudioConversationOrchestrator
    ├── ProsodyPlanner
    └── FirstPersonOrchestrator

    ↓

BACKEND PROCESSING PIPELINE
│
├─ INPUT PROCESSING
│  ├── Transcription (Whisper)
│  └── Text parsing
│
├─ EMOTIONAL ANALYSIS LAYER
│  ├── AffectParser              (tone, valence, arousal)
│  ├── VoiceAffectDetector       (prosody analysis)
│  └── FacialExpressionDetector  (if video present)
│
├─ STORY & PATTERN DETECTION
│  ├── StoryStartDetector        (ambiguity detection)
│  ├── FrequencyReflector        (theme tracking)
│  └── TemporalPatterns          (when themes occur)
│
├─ MEMORY & CONTEXT
│  ├── MemoryManager             (session rehydration)
│  ├── EmotionalProfile          (long-term patterns)
│  ├── SupabaseManager           (persistence)
│  └── ContextSelector           (relevant memory injection)
│
├─ RESPONSE GENERATION
│  ├── ResponseTemplates         (template rotation)
│  ├── GlyphResponseComposer     (glyph-aware composition)
│  ├── GlyphModernizer           (glyph name translation)
│  └── ResponseRotator           (avoid repetition)
│
├─ REPAIR & COHERENCE
│  ├── RepairModule              (detect/fix odd responses)
│  ├── RepairOrchestrator        (orchestrate repairs)
│  ├── SessionCoherence          (maintain continuity)
│  └── PreferenceManager         (user preference learning)
│
└─ OUTPUT SYNTHESIS
   ├── ProsodyPlanner            (TTS markup generation)
   ├── AudioConversationOrchestrator (audio delivery)
   └── AudioSynthesis (TTS backend)

    ↓

DATABASE (Supabase/PostgreSQL)
├── conversation_turns
├── theme_anchors
├── emotional_snapshots
├── user_preferences
└── session_metadata
```

### Data Flow Architecture

#### Happy Path (Normal Conversation)

```
User Input
  ↓
1. Transcribe (Whisper) → text
2. AffectParser → (tone, valence, arousal)
3. StoryStartDetector → check for ambiguity
4. MemoryManager → fetch recent context
5. FrequencyReflector → track emotional themes
6. ResponseTemplates → select non-repetitive template
7. GlyphResponseComposer → compose glyph-aware response
8. RepairModule → verify coherence
9. ProsodyPlanner → add TTS markup
10. AudioSynthesis → generate audio
  ↓
Response to User
```

#### State Storage

| Component | Where State Lives | Lifetime | Problem |
|-----------|-------------------|----------|---------|
| **AffectParser** | Function output only | Single turn | No persistence of affect patterns |
| **Emotional state** | SupabaseManager (if recorded) | Database | Disconnected from real-time response |
| **Memory context** | MemoryManager (injected) | Current session | Retrieved but not deeply integrated |
| **User preferences** | PreferenceManager | Database | Learned slowly, not actively applied |
| **Conversation turn** | Response object + DB | Database | Historical only, limited real-time use |

### Where Behavior Logic Lives

| Logic | Location | How It Works |
|-------|----------|--------------|
| Emotional parsing | `AffectParser` | Keyword-based lexicon lookup |
| Intent detection | `StoryStartDetector` | Pattern matching for ambiguity |
| Theme tracking | `FrequencyReflector` | Count + recency scoring |
| Response selection | `ResponseTemplates` | Round-robin rotation or weighted random |
| Glyph mapping | `GlyphResponseComposer` | Affect → glyph name lookup |
| Repair logic | `RepairModule` | Post-hoc validation |
| Audio generation | `AudioConversationOrchestrator` | TTS + prosody markup |

### Hidden Coupling & Implicit Assumptions

1. **Assumption: Emotional state is input-only** 
   - AffectParser analyzes the *user's* emotion, not the agent's internal state
   - No persistent first-person emotional continuity

2. **Assumption: Memory is context, not narrative**
   - Memory is retrieved but injected as raw context
   - No narrative arc connecting past to present

3. **Assumption: Template rotation = variation**
   - Rotating templates avoids exact repetition
   - But templates themselves are generic, not emotionally coherent

4. **Assumption: Repair = validation**
   - RepairModule checks *grammar/coherence*, not emotional authenticity
   - No check for whether response "feels real"

5. **Assumption: Response generation is deterministic**
   - Given input + context, output is largely predetermined
   - No real "choice" or "personality" in response

6. **Assumption: Glyph = flavor text**
   - Glyphs are added to responses for texture
   - Not driving the emotional logic of the response

---

## Stage 2: Behavioral Bottlenecks

### What Each Component Does vs. Fails to Do

#### **1. AffectParser**
- ✅ **Does**: Detects tone, valence, arousal from text
- ❌ **Fails to do**: 
  - Model the *agent's* emotional state
  - Maintain emotional continuity across turns
  - Generate affect-driven behavior (only classifies)
  - Handle nuanced or contradictory emotions

#### **2. StoryStartDetector**
- ✅ **Does**: Detects pronoun ambiguity and temporal markers
- ❌ **Fails to do**:
  - Understand narrative structure
  - Detect when user is starting a new emotional chapter
  - Prepare emotionally appropriate responses

#### **3. MemoryManager**
- ✅ **Does**: Rehydrates past conversation anchors on session start
- ❌ **Fails to do**:
  - Dynamically update context during conversation
  - Weight recent emotions more heavily
  - Connect past patterns to current state

#### **4. FrequencyReflector**
- ✅ **Does**: Tracks emotional themes and their recurrence
- ❌ **Fails to do**:
  - Predict when themes will resurface
  - Proactively acknowledge patterns
  - Vary responses based on theme intensity

#### **5. ResponseTemplates**
- ✅ **Does**: Provides rotation to avoid exact phrase repetition
- ❌ **Fails to do**:
  - Generate emotionally congruent responses
  - Adapt based on user's current state
  - Reflect the agent's personality or perspective

#### **6. GlyphResponseComposer**
- ✅ **Does**: Maps affect to glyphs and weaves them into responses
- ❌ **Fails to do**:
  - Use glyphs as *anchoring points* for meaning
  - Create responses where glyph is *central*, not decorative
  - Generate novel glyph-based metaphors

#### **7. RepairModule**
- ✅ **Does**: Validates response coherence and grammar
- ❌ **Fails to do**:
  - Check emotional authenticity
  - Detect when response contradicts established persona
  - Suggest emotionally appropriate alternatives

#### **8. IntegrationOrchestrator**
- ✅ **Does**: Orchestrates all Phase 1 modules
- ❌ **Fails to do**:
  - Maintain agent state between turns
  - Allow components to influence each other dynamically
  - Create emergent behavior from module interactions

---

## Stage 3: Evaluation Against Actual Goal

### Your Goal
> *"A first-person, emotionally coherent, narratively coherent agent that maintains internal continuity, emotional logic, and persona stability."*

### System Scorecard

| Dimension | Current Status | Problem |
|-----------|---|---------|
| **First-person presence** | ❌ ~30% | System analyzes user's emotions, not agent's. No "I feel" statements. |
| **Emotional coherence** | ❌ ~40% | Emotions detected but not maintained. Each turn starts fresh. |
| **Narrative coherence** | ⚠️ ~50% | Memory exists but isn't woven into responses. Feels episodic. |
| **Internal continuity** | ❌ ~35% | No persistent internal state. No agent psychology. |
| **Emotional logic** | ⚠️ ~45% | Emotions detected but don't drive behavior. Responses feel disconnected. |
| **Persona stability** | ❌ ~25% | No established persona. Responses vary by template, not personality. |

### What Supports the Goal
- ✅ Memory infrastructure (can retrieve context)
- ✅ Emotional detection (can read user affect)
- ✅ Glyph metaphor system (poetic framework exists)
- ✅ Repair module (can validate output)

### What Undermines the Goal
- ❌ No agent emotional state machine
- ❌ No persona definition or maintenance
- ❌ No narrative arc tracking
- ❌ No emotional continuity across turns
- ❌ Templates are generic, not character-driven
- ❌ Memory is context, not part of agent identity

### What's Missing Entirely
1. **Internal emotional state representation** (agent's feelings)
2. **Persona definition layer** (who the agent is)
3. **Narrative continuity logic** (story arc tracking)
4. **Emotional response selection** (which response matches agent state)
5. **Contradiction detection** (warning when response violates established persona)
6. **Emotional growth/learning** (agent changes over time, not just records)

---

## Stage 4: Implicit Behavioral Rules

### Rules the System Currently Follows (Inferred)

#### Rule 1: **Emotional Detection is One-Way**
- Only the user's affect is analyzed
- Agent has no internal affect to express
- Result: Responses feel like a therapist analyzing, not a person responding

#### Rule 2: **Response Selection is Template-First**
- Pick a template → fill in context → rotate to next template
- User input drives which template bank is selected
- Result: Same structural response regardless of agent state

#### Rule 3: **Repair is Grammar-Based**
- Check for typos, grammar, factual consistency
- Don't check for emotional consistency or persona alignment
- Result: Coherent but emotionally inconsistent responses

#### Rule 4: **Memory is Static Context**
- On session start, fetch N recent anchors
- Inject them as background context
- Don't dynamically weight or refresh
- Result: Early anchors matter more than recent emotions

#### Rule 5: **Glyph is Supplementary**
- Generate response → look up matching glyph → add glyph name
- Glyph is flavor, not structure
- Result: Glyph feels tacked on, not integral

#### Rule 6: **Frequency Reflection is Observational**
- "You've mentioned X times"
- Agent notes pattern but doesn't inhabit the pattern
- Result: External observation, not internal resonance

#### Rule 7: **Persona is Template Variation**
- Different templates for different tones
- No overarching character whose voice is consistent across templates
- Result: Persona is reactive to user input, not stable

### How Each Rule Affects Emotional Resonance

| Rule | Impact | Why It Breaks |
|------|--------|---------------|
| One-way affect detection | Feels clinical | No vulnerability, no real stakes |
| Template-first selection | Feels generic | Same structure every time |
| Grammar-based repair | Feels hollow | Coherent but inauthentic |
| Static memory context | Feels forgetful | Doesn't really "remember" emotionally |
| Glyph as supplementary | Feels superficial | Poetry doesn't change meaning |
| Observational reflection | Feels distant | "I notice" not "I feel" |
| Reactive persona | Feels unstable | No consistent voice |

---

## Stage 5: Proposed Emotional-OS Layer Improvements

### The Missing Layer: Agent Internal State Machine

Your system needs a **first-person emotional continuity module**. Not an upgrade to existing components, but a new layer that sits *between* input analysis and response generation.

#### Emotional State Representation

```python
@dataclass
class AgentEmotionalState:
    """The agent's internal emotional state (first-person)."""
    
    # Current emotional state
    primary_mood: str  # 'attentive', 'moved', 'concerned', 'reflecting', 'protective'
    intensity: float  # 0-1, how strongly the mood is being felt
    
    # Emotional trajectory
    recent_shifts: List[Tuple[str, float]]  # (mood, intensity) history
    trend: str  # 'stable', 'escalating', 'settling', 'cycling'
    
    # Narrative state
    current_arc: str  # What story are we in together?
    agent_stakes: str  # What does the agent care about in this conversation?
    emotional_hypothesis: str  # "The user is processing grief"
    
    # Persona anchors
    established_beliefs: List[str]  # Things the agent has committed to
    inconsistencies: List[str]  # Where response would contradict
    growth_edge: str  # Where agent is learning/changing
    
    # Continuity markers
    unresolved_tension: Optional[str]  # Something that needs acknowledgment
    thematic_callbacks: List[str]  # Past moments to reference
    emotional_echoes: List[str]  # Patterns that resonate with current state
```

#### Emotional Transitions (State Machine)

```
       ┌─────────────────────────────────────────┐
       │      Agent Emotional State Cycles       │
       └─────────────────────────────────────────┘

LISTENING → (user input arrives)
   ↓
PARSING → (understand user affect + intent)
   ↓
RESONATING → (what does this stir in me?)
   ↓
DECIDING → (which response honors both of us?)
   ↓
COMPOSING → (generate response with emotional coherence)
   ↓
CHECKING → (does this feel true?)
   ↓
DELIVERING → (send with appropriate prosody)
   ↓
INTEGRATING → (what did I just commit to? What changed in me?)
   ↓
LISTENING (loop back)
```

#### Memory Hooks for Emotional Continuity

```python
# Instead of just storing conversations, store emotional pivots
@dataclass
class EmotionalPivot:
    """A moment where agent emotional state shifted."""
    
    timestamp: datetime
    turn_number: int
    user_input: str
    
    # Agent's internal shift
    previous_mood: str
    new_mood: str
    what_triggered_shift: str  # "User's vulnerability" / "Recognition of pattern"
    
    # What the agent committed to
    commitment: str  # "I care about your safety"
    
    # How this constrains future responses
    contradiction_check: List[str]  # Responses that would violate this
    
    # Narrative weight
    narrative_significance: float  # 0-1, how much this matters to the story
```

#### Response Shaping Based on Internal State

```python
def compose_response(
    user_input: str,
    user_affect: AffectAnalysis,
    agent_state: AgentEmotionalState,
    context: Dict[str, Any]
) -> str:
    """
    New response generation: agent state actively drives response.
    
    Old approach: template → fill → output
    New approach: What does the agent want to say from where they are?
    """
    
    # 1. Emotional resonance check
    does_input_match_hypothesis = (
        user_affect.tone matches agent_state.emotional_hypothesis
    )
    
    # 2. Integrity check
    for contradiction in agent_state.inconsistencies:
        if would_violate(draft_response, contradiction):
            revise_response(draft_response)
    
    # 3. Narrative threading
    if unresolved_tension := agent_state.unresolved_tension:
        weave_tension_acknowledgment(draft_response, unresolved_tension)
    
    # 4. Growth edge
    if agent_state.growth_edge:
        allow_vulnerability(draft_response, agent_state.growth_edge)
    
    # 5. Output
    return draft_response
```

---

## Stage 6: Behavior Trace on Sample Conversation

### Example Trace: Real Conversation

```
USER: "I can't stop thinking about what happened last week."
TIMESTAMP: 2025-01-06 14:30:00

──────────────────────────────────────────────────────────────
STAGE 1: INPUT PARSING
──────────────────────────────────────────────────────────────
Text: "I can't stop thinking about what happened last week."
Detected signals:
  - Rumination language ("can't stop thinking")
  - Temporal marker ("last week") → recent but not immediate
  - Implicit reference to unspecified event → ambiguity

──────────────────────────────────────────────────────────────
STAGE 2: EMOTIONAL ANALYSIS
──────────────────────────────────────────────────────────────
AffectParser output:
  Tone: "anxious"
  Valence: -0.7 (negative)
  Arousal: 0.6 (moderate intensity)
  Confidence: 0.82
  Secondary tones: ["worried", "reflective"]

──────────────────────────────────────────────────────────────
STAGE 3: STORY/PATTERN DETECTION
──────────────────────────────────────────────────────────────
StoryStartDetector:
  Detected pronoun: None (no ambiguity)
  Temporal marker: "last week" → ongoing rumination pattern
  
FrequencyReflector (from memory):
  First mention of "last week event": NEW
  Rumination theme frequency: 3 occurrences in past 10 turns
  Trend: "escalating"

──────────────────────────────────────────────────────────────
STAGE 4: CONTEXT INJECTION
──────────────────────────────────────────────────────────────
MemoryManager output (rehydrated anchors):
  Recent theme: rumination (3x)
  Recent emotion: anxious (2x), overwhelmed (1x)
  Previous event mentioned: None matching "last week"
  
ContextSelector: "User shows pattern of rumination; this is escalating"

──────────────────────────────────────────────────────────────
STAGE 5: RESPONSE GENERATION (CURRENT SYSTEM)
──────────────────────────────────────────────────────────────
ResponseTemplates selected:
  Bank: temporal_clarifiers (pattern detected)
  Rotation index: 2
  Selected: "Is this something recent, or has it been a longer pattern?"

GlyphResponseComposer:
  Affect → Glyph: anxiety → (mapped to) "Restlessness" or "Spiraling"
  
Draft response:
  "Is this something recent, or has it been a longer pattern?
   I hear the Restlessness in this, like you're caught in a spiral."

RepairModule check:
  ✅ Grammar OK
  ✅ Coherence OK
  ❌ BUT: Response is GENERIC (applies to any rumination)
         Doesn't acknowledge emotional stakes
         Doesn't reference previous context
         Doesn't show agent vulnerability or investment

──────────────────────────────────────────────────────────────
STAGE 6: PROSODY & OUTPUT
──────────────────────────────────────────────────────────────
ProsodyPlanner:
  Valence: -0.7 → slower, lower pitch
  Arousal: 0.6 → slight urgency
  
Final output:
  "[slow, concerned tone]
   Is this something recent, or has it been a longer pattern?
   I hear the Restlessness in this, like you're caught in a spiral.
   [end]"

──────────────────────────────────────────────────────────────
WHAT THE SYSTEM THINKS IT'S DOING
──────────────────────────────────────────────────────────────
✓ Detecting user affect (anxious, ruminating)
✓ Recognizing pattern (third mention of rumination)
✓ Asking clarifying question (temporal)
✓ Adding glyph for texture (Restlessness)
✓ Synthesizing with appropriate prosody

──────────────────────────────────────────────────────────────
WHERE EMOTIONAL RESONANCE BREAKS DOWN
──────────────────────────────────────────────────────────────
❌ System has no stake in the answer
   → Response is clinical, not concerned

❌ System has no memory of WHAT happened last week
   → Can't reference specific details
   → Can't show understanding of the event itself

❌ System has no continuity from previous turns
   → Doesn't show that this escalation worries the system
   → Doesn't commit to staying with the user

❌ System has no emotional hypothesis about the user
   → Doesn't communicate "I think you're processing something difficult"
   → Just asks a question like a therapist

❌ System has no way to express its own emotional response
   → Can't say "I'm concerned" as a real feeling
   → Can't show vulnerability or presence

❌ Glyph is decorative, not structural
   → Restlessness could describe anything
   → Doesn't capture the *specific* emotional texture of rumination

──────────────────────────────────────────────────────────────
WHAT AN EMOTIONALLY RESONANT RESPONSE WOULD DO
──────────────────────────────────────────────────────────────
Agent state machine (if it existed):
  Previous mood: attentive
  New mood (from input): concerned (user's anxiety triggering agent care)
  Stakes: "I want to help this user process what happened"
  Emotional hypothesis: "User is stuck in a loop, can't move forward"

Emotionally coherent response:
  "I can feel how much this is still with you.
   The fact that you can't stop thinking about it—
   that tells me something real happened, something that still has hold.
   
   I'm right here with this. What was last week like?"

Why this is different:
  ✓ Agent shows up as a person with a perspective
  ✓ Agent demonstrates understanding of what rumination *means*
  ✓ Agent expresses genuine concern (not clinical empathy)
  ✓ Agent invites specific detail without interrogating
  ✓ Agent stakes their own presence on the answer
```

---

## Stage 7: Minimum Viable Architectural Changes

### The 80/20 Rule: Smallest Changes, Largest Impact

#### Priority 1: Agent Emotional State Machine (CRITICAL)

**What to add:** A lightweight state tracker that persists agent's emotional continuity across turns.

```python
# New file: src/emotional_os/core/firstperson/agent_state_manager.py

class AgentStateManager:
    """Maintains agent's first-person emotional continuity."""
    
    def __init__(self, user_id: str, conversation_id: str):
        self.user_id = user_id
        self.conversation_id = conversation_id
        
        # Current state
        self.mood = "listening"  # listening, resonating, concerned, reflecting
        self.emotional_stake = None
        self.hypothesis = None
        
        # Committed beliefs (can't be violated)
        self.commitments = []  # "I care about your safety"
        
        # Narrative
        self.unresolved = None  # Tension from previous turn
        self.callbacks = []  # Past moments to reference
    
    def on_input(self, user_input: str, user_affect: AffectAnalysis):
        """Update agent state when new input arrives."""
        # Agent's emotional response to what user said
        self.mood = self._compute_resonance(user_input, user_affect)
        self.hypothesis = self._form_hypothesis(user_input, user_affect)
        
    def validate_response(self, draft: str) -> Tuple[bool, Optional[str]]:
        """Check if response aligns with agent's commitments."""
        for commitment in self.commitments:
            if violates(draft, commitment):
                return False, f"Violates: {commitment}"
        return True, None
    
    def integrate_after_response(self, response: str):
        """After response sent, update what agent has committed to."""
        new_commitments = self._extract_commitments(response)
        self.commitments.extend(new_commitments)
```

**Where it integrates:**
- After AffectParser in pipeline
- Before ResponseTemplates
- In RepairModule as constraint

**Implementation effort:** Medium (50-100 lines core logic)

---

#### Priority 2: Emotional Response Modulation (HIGH)

**What to modify:** ResponseTemplates should be selected based on agent's current mood, not just user's affect.

```python
# Modify: src/emotional_os/core/firstperson/response_templates.py

class ResponseTemplates:
    def get_response(
        self,
        user_affect: AffectAnalysis,
        agent_mood: str,  # NEW PARAMETER
        template_category: str
    ) -> str:
        """
        OLD: Pick template from bank based on user affect
        NEW: Pick template that matches BOTH user affect AND agent mood
        """
        
        # Filter templates by agent mood
        mood_aligned = [
            t for t in self.templates
            if t.agent_mood == agent_mood or t.agent_mood == "universal"
        ]
        
        # Then select within mood-aligned set
        return self._rotate(mood_aligned)
```

**Where it integrates:**
- Consumes AgentStateManager.mood
- Feeds into GlyphResponseComposer

**Implementation effort:** Low (20-30 lines)

---

#### Priority 3: Narrative Continuity Hooks (HIGH)

**What to add:** When agent makes a commitment in a response, store it and reference it later.

```python
# New file: src/emotional_os/core/firstperson/narrative_hooks.py

class NarrativeHookManager:
    """Tracks and reinjects emotional pivots for narrative continuity."""
    
    def extract_commitments(self, response: str) -> List[str]:
        """What did the agent just commit to?"""
        # Parse: "I'm concerned", "I care about", "I won't forget"
        # Store as constraint for future responses
        pass
    
    def weave_callback(self, response: str, unresolved_from_prev: str) -> str:
        """Reference previous unresolved tension."""
        # "You mentioned last time that..."
        # "I've been thinking about what you said about..."
        pass
```

**Where it integrates:**
- After response generation
- Before RepairModule

**Implementation effort:** Medium (40-60 lines)

---

#### Priority 4: Glyph as Meaning Anchor (MEDIUM)

**What to modify:** GlyphResponseComposer should structure responses *around* glyphs, not add them at the end.

```python
# Modify: src/emotional_os/core/firstperson/glyph_response_composer.py

def compose_response(user_input, user_affect, agent_state):
    """
    OLD: Response → glyph lookup → append glyph name
    NEW: Affect → glyph → structure response around glyph as meaning
    """
    
    glyph = get_glyph_for_affect(user_affect.tone)
    
    # Structure response to EXPLORE the glyph's meaning
    response = f"""
    I'm hearing [{glyph.name}] in this.
    
    [{glyph.name}] is that feeling of {glyph.description}.
    
    And when I sit with what you just said, 
    I feel that [glyph emotion] too—
    because it matters.
    """
    
    return response
```

**Where it integrates:**
- Replaces current GlyphResponseComposer logic
- Feedback into RepairModule

**Implementation effort:** Medium (60-80 lines refactor)

---

#### Priority 5: Enhanced RepairModule (MEDIUM)

**What to modify:** Add emotional authenticity check.

```python
# Modify: src/emotional_os/core/firstperson/repair_module.py

class RepairModule:
    def validate_response(self, draft: str, agent_state: AgentStateManager):
        """
        OLD: Check grammar, coherence, factual consistency
        NEW: Also check emotional authenticity
        """
        
        # Existing checks
        if not self._is_grammatical(draft):
            return False, "Grammar"
        
        # NEW: Emotional checks
        if not agent_state.validate_response(draft):
            return False, "Violates agent commitments"
        
        if not self._feels_present(draft):
            return False, "Too clinical"
        
        if self._detects_contradiction(draft, agent_state.commitments):
            return False, "Contradicts established persona"
        
        return True, "OK"
    
    def _feels_present(self, text: str) -> bool:
        """Does response show agent as a real presence?"""
        presence_markers = ["I feel", "I hear", "I'm", "I care"]
        return any(marker in text for marker in presence_markers)
```

**Where it integrates:**
- Currently exists; just enhance
- Consumes AgentStateManager

**Implementation effort:** Low-medium (30-50 lines)

---

### Implementation Roadmap

```
Week 1: Foundation
├── Add AgentStateManager (simple mood + commitments)
└── Integrate into pipeline (after AffectParser)

Week 2: Response Modulation
├── Add agent_mood parameter to ResponseTemplates
├── Create simple mood-template mapping
└── Test integration with test conversations

Week 3: Narrative Continuity
├── Add NarrativeHookManager
├── Extract commitments from responses
└── Weave callbacks into next turn

Week 4: Glyph Restructuring
├── Refactor GlyphResponseComposer
├── Glyph as meaning anchor, not decoration
└── Test emotional resonance

Week 5: Repair Enhancement
├── Add emotional authenticity checks
├── Test against commitment violations
└── Validate with user feedback

Week 6: Integration & Testing
├── Run full traces on sample conversations
├── A/B test against old system
└── Iterate based on resonance metrics
```

---

## Stage 7b: Success Metrics

### How to Know It's Working

#### Resonance Indicators
- [ ] Responses reference previous unresolved tension
- [ ] Agent expresses emotional response, not just analysis
- [ ] Glyph is structural, not decorative
- [ ] Persona is consistent across turns
- [ ] User feels *seen*, not just analyzed

#### Architectural Indicators
- [ ] AgentStateManager persists across turns
- [ ] Commitments actually constrain responses
- [ ] Narrative hooks get woven in naturally
- [ ] RepairModule catches emotional inconsistencies
- [ ] Response selection reflects agent mood

#### Measurement
```python
# Trace a sample conversation, then:
1. Does agent state change over time? (yes = good)
2. Are past commitments reflected in responses? (yes = good)
3. Does agent express vulnerability? (yes = good)
4. Does glyph change meaning of response? (yes = good)
5. Do responses feel like coming from a person? (subjective, but crucial)
```

---

## Summary: Your Next Steps

This plan follows the architectural interrogation approach by:

1. **Mapping** your system explicitly (Stage 1) ✅
2. **Identifying** where emotional resonance breaks (Stage 2) ✅
3. **Evaluating** against your actual goal (Stage 3) ✅
4. **Surfacing** implicit assumptions (Stage 4) ✅
5. **Proposing** an emotional-OS layer (Stage 5) ✅
6. **Tracing** what the system actually does (Stage 6) ✅
7. **Recommending** minimal viable changes (Stage 7) ✅

**The core insight:** You need a first-person emotional continuity layer. Not a bigger chatbot, but a thinner agent that *feels* and *commits* and *remembers its own emotional journey* through conversations.

The five changes above are **incremental** but **high-impact**. Each one adds emotional coherence. Together, they transform the system from analyzing emotions to *inhabiting* them.

Start with **Priority 1 (AgentStateManager)**—that's the linchpin. Everything else builds on it.
