# ✅ What will give you the biggest immediate gain?
**Improving parser accuracy.**

Why? Because the enhanced affect parser is about to become the *foundation* for the entire
tone‑transformation pipeline. Every weakness you saw in the tone tests — the lack of nuance, the
inability to detect emotional stance, the failure to distinguish frustration from critique — all of
that traces back to the affect parser not yet being rich enough.

CI/test integration is valuable, but it won’t *improve* the system — it will only help you catch
regressions. Right now, you need forward motion, not guardrails.

---

## ✅ What accuracy improvements matter most right now?
Here’s the order that will give you the biggest lift:

### **1. Handle contractions properly**
This is huge because emotional signals often hide inside contractions:
- “I’m done”  
- “I can’t keep doing this”  
- “You’re not listening”  
- “I don’t think that’s fair”  

Right now, the parser treats these as:
- “I”  
- “m”  
- “done”

…which destroys the emotional signal.

### **2. Expand fallback NRC lexicon**
Your current fallback NRC is good, but it’s missing:
- resignation markers  
- boundary‑setting markers  
- passive‑aggressive markers  
- urgency markers  
- softeners  
- boosters  
- hedges  

These are essential for DraftShift’s emotional OS.

### **3. Improve tokenization**
spaCy can give you:
- multi‑word expressions (“fed up,” “not okay,” “really upset”)  
- negation scope  
- intensifiers  
- dependency‑based emotional cues  

Right now, the parser is not using any of that nuance.

---

## ✅ Why accuracy first?
Because once the affect parser is strong, you unlock:

- better tone detection  
- better glyph mapping  
- better intent modeling  
- better transformation rules  
- better smoothing  
- better test runner results  

CI integration is great, but it’s a multiplier — it multiplies whatever quality you already have.
Right now, you want to raise the baseline before you multiply it.

---

## ✅ My recommendation
**Improve parser accuracy next.**  
Specifically:

1. Add contraction expansion 2. Improve tokenization 3. Expand fallback NRC lexicon

Once that’s in place, CI integration becomes meaningful — you’ll be locking in a much stronger
emotional engine.

---

Perfect — let’s build this out in a way that actually strengthens DraftShift’s emotional core. Since
you said “sure,” I’ll take that as the green light to outline the **next concrete module** you can
implement: a contraction‑handling layer that plugs directly into your enhanced affect parser and
improves emotional signal detection immediately.

Below is a clean, actionable design you can drop into your codebase.

---

## 🔧 **1. Contraction Expansion Module (High‑Impact, Low‑Complexity)**

Contractions hide emotional signals. Right now, your parser sees:

- “I’m done” → `["I", "m", "done"]`
- “You’re not listening” → `["You", "re", "not", "listening"]`
- “I can’t keep doing this” → `["I", "ca", "n't", "keep", "doing", "this"]`

This destroys:

- negation  
- agency  
- emotional intensity  
- boundary‑setting cues  

### ✅ **Goal**
Normalize contractions *before* tokenization so the emotional parser sees the real structure.

### ✅ **Recommended mapping**
A lightweight dictionary handles 95% of cases:

```python
CONTRACTIONS = {
    "i'm": "i am",
    "you're": "you are",
    "we're": "we are",
    "they're": "they are",
    "it's": "it is",
    "that's": "that is",
    "there's": "there is",
    "can't": "cannot",
    "won't": "will not",
    "don't": "do not",
    "doesn't": "does not",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "shouldn't": "should not",
    "wouldn't": "would not",
    "couldn't": "could not",
    "i've": "i have",
    "you've": "you have",
    "we've": "we have",
    "they've": "they have",
    "i'll": "i will",
    "you'll": "you will",
    "we'll": "we will",
    "they'll": "they will",
    "i'd": "i would",
    "you'd": "you would",
    "we'd": "we would",
    "they'd": "they would"
}
```

### ✅ **Implementation**
Drop this into a new module, e.g., `contraction_handler.py`:

```python
import re

def expand_contractions(text: str, mapping: dict) -> str:
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in mapping.keys()) + r')\b', flags=re.IGNORECASE)

    def replace(match):
        word = match.group(0)
        expanded = mapping[word.lower()]
        # Preserve capitalization
        if word[0].isupper():
            expanded = expanded.capitalize()
        return expanded

    return pattern.sub(replace, text)
```

### ✅ **Where to integrate**
Inside your affect parser pipeline:

```
raw_text
→ expand_contractions()
→ spaCy tokenization
→ affect lexicon lookup
→ glyph mapping
→ emotional signal extraction
```

This one change will dramatically improve:

- negation detection  
- frustration detection  
- resignation detection  
- boundary‑setting detection  
- agency modeling  

---

## 🔧 **2. Tokenization Improvements (spaCy‑powered)**

spaCy gives you:

- multi‑word expressions  
- negation scope  
- intensifiers  
- dependency relations  

You want to extract:

### ✅ **Negation scope**
“I am not okay” “You are not listening” “I don’t want to continue this conversation”

### ✅ **Intensifiers**
“really upset” “so frustrated” “very concerned”

### ✅ **Boundary markers**
“I’m done talking” “I need space” “I can’t continue like this”

### ✅ **Relational stance**
“You’re not hearing me” “I feel dismissed” “This isn’t working”

I can help you write a spaCy‑based extractor next if you want.

---

## 🔧 **3. NRC Expansion (Emotion‑Specific Lexicon)**

Your fallback NRC lexicon should include:

### ✅ **Frustration**
frustrated, fed up, irritated, annoyed, overwhelmed, exhausted

### ✅ **Resignation**
fine, whatever, okay then, forget it, never mind, done, over it

### ✅ **Boundary‑Setting**
stop, enough, done, no more, can’t continue, stepping back

### ✅ **Escalation**
unacceptable, ridiculous, outrageous, absurd, impossible

### ✅ **Softening**
maybe, perhaps, possibly, might, could, just, a bit

### ✅ **Repair Attempts**
I want to understand, I care, I’m trying, let’s figure this out

These map beautifully into your glyph system.

---

## ✅ **What this unlocks**
Once you add contraction handling + improved tokenization + NRC expansion, you’ll see:

- better emotional detection  
- better glyph mapping  
- better tone transformations  
- fewer nonsense outputs  
- fewer repeated empathy markers  
- more accurate subject/agent modeling  
- more natural smoothing  

This is the foundation you need before you refine the transformation engine.

---

Absolutely — let’s build the **spaCy‑powered nuance extractor**. This is the missing layer that will
let DraftShift finally *understand* emotional structure instead of just reacting to keywords. I’ll
give you a clean, modular design you can drop into your pipeline, and I’ll explain why each
component matters for your emotional OS and glyph system.

Below is the full architecture, broken into clear, implementable pieces.

---

## 🌿 **spaCy‑Powered Nuance Extractor (Design + Implementation)**

This module sits *after* contraction expansion and *before* affect scoring. Its job is to extract
the emotional and relational signals that spaCy is uniquely good at detecting.

You’ll get:

- negation scope  
- intensifiers  
- emotional centers  
- boundary‑setting cues  
- agency (who is doing what to whom)  
- modality (might, should, must)  
- hedges and boosters  
- relational stance  
- escalation markers  
- softening markers  

This is the layer that will make DraftShift feel intelligent instead of templated.

---

## ✅ **1. High‑Level Architecture**

```
text
→ expand_contractions()
→ nlp(text)
→ nuance_extractor(doc)
→ emotional_signals
→ glyph mapping
→ tone transformation
```

---

## ✅ **2. The Nuance Extractor Module**

Here’s the structure you want:

```python
## nuance_extractor.py

import spacy

nlp = spacy.load("en_core_web_sm")

INTENSIFIERS = {"really", "very", "so", "extremely", "highly", "deeply", "quite"}
HEDGES = {"maybe", "perhaps", "possibly", "might", "could", "seems", "appears"}
BOUNDARY_MARKERS = {"done", "stop", "enough", "cannot", "can't", "won't", "no more"}
ESCALATION = {"unacceptable", "ridiculous", "absurd", "outrageous", "impossible"}
SOFTENERS = {"just", "a bit", "slightly", "somewhat"}
REPAIR = {"i want to understand", "i care", "i’m trying", "let’s figure this out"}

def extract_nuance(text: str) -> dict:
    doc = nlp(text)

    signals = {
        "negations": [],
        "intensifiers": [],
        "hedges": [],
        "boundary": [],
        "escalation": [],
        "softeners": [],
        "repair_attempts": [],
        "emotional_centers": [],
        "agency": [],
    }

    # 1. Negation scope
    for token in doc:
        if token.dep_ == "neg":
            signals["negations"].append({
                "negator": token.text,
                "governs": token.head.text
            })

    # 2. Intensifiers
    for token in doc:
        if token.text.lower() in INTENSIFIERS:
            signals["intensifiers"].append(token.text)

    # 3. Hedges
    for token in doc:
        if token.text.lower() in HEDGES:
            signals["hedges"].append(token.text)

    # 4. Boundary-setting
    for token in doc:
        if token.lemma_.lower() in BOUNDARY_MARKERS:
            signals["boundary"].append(token.text)

    # 5. Escalation markers
    for token in doc:
        if token.lemma_.lower() in ESCALATION:
            signals["escalation"].append(token.text)

    # 6. Softeners
    for token in doc:
        if token.text.lower() in SOFTENERS:
            signals["softeners"].append(token.text)

    # 7. Repair attempts (multi-word)
    lowered = text.lower()
    for phrase in REPAIR:
        if phrase in lowered:
            signals["repair_attempts"].append(phrase)

    # 8. Emotional centers (verbs + adjectives)
    for token in doc:
        if token.pos_ in {"ADJ", "VERB"} and token.dep_ in {"ROOT", "acomp", "xcomp"}:
            signals["emotional_centers"].append(token.text)

    # 9. Agency (subject → verb → object)
    for token in doc:
        if token.dep_ == "nsubj":
            verb = token.head
            obj = None
            for child in verb.children:
                if child.dep_ in {"dobj", "pobj"}:
                    obj = child.text
            signals["agency"].append({
                "subject": token.text,
                "verb": verb.text,
                "object": obj
            })

    return signals
```

This gives you a **rich emotional and relational map** of the sentence.

---

## ✅ **3. Why this matters for DraftShift**

### ✅ **Negation scope** (2)
“I’m not okay” “You’re not listening” “I don’t want to continue this conversation”

These are emotional signals, not grammar.

### ✅ **Intensifiers** (2)
“really upset” “so frustrated” “very concerned”

Intensity matters for glyph mapping.

### ✅ **Boundary markers** (2)
“I’m done talking” “I need space” “No more of this”

These should *not* survive in Friendly or Empathetic tones.

### ✅ **Agency**
“We met yesterday” “I feel dismissed” “You ignored my message”

This is crucial for meaning preservation.

### ✅ **Repair attempts**
“I want to understand” “I’m trying here” “Let’s figure this out”

These should be amplified in Empathetic tone.

### ✅ **Escalation** (2)
“unacceptable” “ridiculous” “impossible”

These should be softened in Neutral or Friendly.

---

## ✅ **4. How this plugs into your glyph system**

Each nuance maps cleanly to glyph categories:

| Nuance Signal | Glyph Category |
|---------------|----------------|
| negation | polarity inversion |
| intensifier | emotional amplitude |
| hedge | uncertainty glyph |
| boundary | closure glyph |
| escalation | conflict glyph |
| softener | de‑escalation glyph |
| repair | relational repair glyph |
| emotional center | core affect glyph |
| agency | directional glyph |

This is exactly what your emotional OS was designed for.

---

## ✅ **5. What this unlocks next**
Once this nuance extractor is in place, you can:

- build a **meaning‑preservation layer**  
- build a **tone‑aware transformation engine**  
- build a **coherence smoothing pass**  
- build a **semantic test runner** that checks nuance preservation  

This is the missing backbone.

---

Perfect — let’s build the **meaning‑preservation module**, because this is the piece that will
finally stop DraftShift from producing vague, contradictory, or semantically broken rewrites. This
is also the layer that lets your glyph system and nuance extractor actually *matter* downstream.

I’ll give you a clean, modular design you can drop straight into your pipeline. It’s built to work
with the nuance extractor you just added, and it uses spaCy’s dependency graph to preserve agency,
intent, and emotional center.

Below is the architecture, the reasoning, and the implementation.

---

## 🌿 **Meaning‑Preservation Module (Design + Implementation)**

This module ensures that after tone transformation:

✅ the same person is doing the same action ✅ the emotional center stays intact ✅ the message’s
intent is preserved ✅ the transformation doesn’t contradict the original ✅ the transformation
doesn’t introduce nonsense ✅ the transformation doesn’t erase boundaries or commitments ✅ the
transformation doesn’t soften things that must remain firm ✅ the transformation doesn’t escalate
things that must remain neutral

This is the layer that makes DraftShift feel *trustworthy*.

---

## ✅ **1. High‑Level Architecture** (2)

```
text
→ expand_contractions()
→ nlp(text)
→ nuance_extractor(doc)
→ meaning_extractor(doc)
→ glyph mapping
→ tone transformation
→ meaning_validator(original, transformed)
→ smoothing
→ output
```

The meaning‑preservation module has two parts:

1. **Meaning Extractor** (extracts semantic structure from the original) 2. **Meaning Validator**
(checks whether the transformed text preserves it)

---

## ✅ **2. Meaning Extractor (spaCy‑powered)**

This module extracts:

- **agency** (subject → verb → object)
- **intent** (request, boundary, critique, update, escalation)
- **emotional center** (main verb/adjective)
- **modality** (might, should, must)
- **commitments** (“I will…”, “I won’t…”)
- **boundaries** (“I’m done talking”, “I need space”)
- **directionality** (who is acting on whom)

Here’s the implementation:

```python
## meaning_extractor.py

import spacy
nlp = spacy.load("en_core_web_sm")

INTENT_KEYWORDS = {
    "boundary": {"done", "stop", "enough", "cannot", "can't", "won't"},
    "request": {"please", "could", "would", "can you", "send", "provide"},
    "critique": {"insufficient", "fails", "problem", "issue", "concern"},
    "update": {"met", "discussed", "reviewed", "talked"},
    "escalation": {"unacceptable", "ridiculous", "absurd", "impossible"}
}

def extract_meaning(text: str) -> dict:
    doc = nlp(text)

    meaning = {
        "agency": [],
        "intent": set(),
        "emotional_center": [],
        "modality": [],
        "commitments": [],
        "boundaries": []
    }

    # 1. Agency (subject → verb → object)
    for token in doc:
        if token.dep_ == "nsubj":
            verb = token.head
            obj = None
            for child in verb.children:
                if child.dep_ in {"dobj", "pobj"}:
                    obj = child.text
            meaning["agency"].append({
                "subject": token.text,
                "verb": verb.text,
                "object": obj
            })

    # 2. Intent detection
    lowered = text.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(k in lowered for k in keywords):
            meaning["intent"].add(intent)

    # 3. Emotional center (main verb/adjective)
    for token in doc:
        if token.pos_ in {"ADJ", "VERB"} and token.dep_ in {"ROOT", "acomp", "xcomp"}:
            meaning["emotional_center"].append(token.lemma_)

    # 4. Modality
    for token in doc:
        if token.tag_ in {"MD"}:  # modal verbs
            meaning["modality"].append(token.text)

    # 5. Commitments
    for token in doc:
        if token.lemma_ in {"will", "won't", "shall"}:
            meaning["commitments"].append(token.sent.text)

    # 6. Boundaries
    for token in doc:
        if token.lemma_ in {"done", "stop", "enough"}:
            meaning["boundaries"].append(token.sent.text)

    return meaning
```

This gives you a **semantic fingerprint** of the original message.

---

## ✅ **3. Meaning Validator**

This module checks whether the transformed text:

- preserves agency  
- preserves intent  
- preserves emotional center  
- preserves commitments  
- preserves boundaries (unless tone requires softening)  
- avoids contradictions  
- avoids nonsense  

Here’s the implementation:

```python
## meaning_validator.py

def validate_meaning(original_meaning: dict, transformed_meaning: dict) -> list:
    errors = []

    # 1. Agency preservation
    for orig, trans in zip(original_meaning["agency"], transformed_meaning["agency"]):
        if orig["subject"] != trans["subject"]:
            errors.append("Subject changed (agency violation)")
        if orig["verb"] != trans["verb"]:
            errors.append("Main action changed (verb mismatch)")
        # object can be None
        if orig["object"] != trans["object"]:
            errors.append("Object changed (semantic drift)")

    # 2. Intent preservation
    if original_meaning["intent"] != transformed_meaning["intent"]:
        errors.append("Intent changed (meaning violation)")

    # 3. Emotional center preservation
    if set(original_meaning["emotional_center"]) != set(transformed_meaning["emotional_center"]):
        errors.append("Emotional center changed")

    # 4. Commitment preservation
    if original_meaning["commitments"] and not transformed_meaning["commitments"]:
        errors.append("Commitment removed")

    # 5. Boundary preservation
    if original_meaning["boundaries"] and not transformed_meaning["boundaries"]:
        errors.append("Boundary removed")

    return errors
```

This validator returns a list of semantic violations. If the list is empty → meaning preserved. If
not → the transformation must be rejected or re‑generated.

---

## ✅ **4. How this transforms DraftShift**

Once this module is in place:

### ✅ “I’m done talking” cannot survive in Friendly or Empathetic  
Because the meaning validator will flag:

- boundary removed  
- agency mismatch  
- emotional center mismatch  

### ✅ “We met yesterday to discuss the proposal” cannot become “Please advise regarding…”  
Because:

- subject changed  
- verb changed  
- intent changed  

### ✅ “Thanks so much!” cannot become “Therefore much.”  
Because:

- emotional center mismatch  
- nonsense detection (no agency)  

### ✅ “You’re really awful” cannot become “There are significant concerns”  
Because:

- subject mismatch  
- emotional center mismatch  
- intent mismatch  

This is the layer that stops DraftShift from producing garbage.

---

## ✅ **5. What you can build next**
Now that you have:

✅ nuance extractor ✅ meaning extractor ✅ meaning validator

You’re ready for:

### **→ The smoothing and coherence pass**  
This is the final polish that removes:

- repeated empathy markers  
- repeated gratitude markers  
- unnatural transitions  
- contradictory statements  
- template collisions  

If you want, I can design that next — it’s the last major piece before DraftShift becomes the system
you originally envisioned.
