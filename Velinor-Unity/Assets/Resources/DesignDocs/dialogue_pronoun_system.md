# Dialogue Pronoun System Architecture

## Overview

The **Dialogue Pronoun System** enables dynamic pronoun and name swapping throughout the game based on the player's character selection. This document outlines the technical architecture and implementation strategy.

---

## System Goals

1. **Seamless pronoun swapping** in all dialogue without requiring separate dialogue trees
2. **Natural language** that feels written (not templated)
3. **Contextual variation** where appropriate (formal vs. intimate, institutional vs. spiritual)
4. **NPC-specific behavior** (some NPCs always use player's chosen name; others may vary)
5. **Mechanical transparency** (player can see what pronouns are currently active)

---

## Core Architecture

### Layer 1: Pronoun Tokens

All dialogue that references the player uses **pronoun tokens** instead of hard-coded pronouns.

#### Token List

| Token | Replaces | Example |
|-------|----------|---------|
| `{player_name}` | Character's name | "Lior", "Lioren", or "Lior(en)" |
| `{player_subj}` | Subject pronoun | "you" (always "you" in 2nd person dialogue) |
| `{player_obj}` | Object pronoun | "you" (always "you" in 2nd person dialogue) |
| `{player_poss}` | Possessive | "your" (always "your") |
| `{player_refl}` | Reflexive | "yourself" (always "yourself") |
| `{player_gender}` | Gender reference | "man/woman/person" |
| `{player_he_she}` | Subject (3rd person) | "he", "she", "they" |
| `{player_him_her}` | Object (3rd person) | "him", "her", "them" |
| `{player_his_her}` | Possessive (3rd person) | "his", "her", "their" |
| `{player_himself_herself}` | Reflexive (3rd person) | "himself", "herself", "themself" |

#### Notes

- **2nd person dialogue** (NPC speaking to player) uses "you/your" consistently—no token needed
- **3rd person dialogue** (NPC speaking about player to someone else) uses gender-specific tokens
- **Variant names** only affect `{player_name}` token; pronouns are determined separately

---

### Layer 2: Dialogue Data Structure

Each line of dialogue is stored with embedded tokens:

#### Standard Format

```json
{
  "dialogue_id": "malrik_001_greeting",
  "speaker": "malrik",
  "scene": "archive_study",
  "content": "Welcome, {player_name}. You work competently.",
  "requires_stats": { "coherence": null },
  "npc_knows_pronouns": true
}
```

#### 3rd Person Reference Format

```json
{
  "dialogue_id": "velinor_012_to_malrik",
  "speaker": "velinor",
  "addressee": "malrik",
  "about": "player",
  "content": "I've been observing {player_name}. {player_he_she} shows potential, though {player_his_her} coherence is fractured.",
  "requires_stats": { "coherence": null }
}
```

---

### Layer 3: Token Replacement Engine

The **token replacement system** substitutes tokens at runtime.

#### Replacement Logic

```python
def replace_pronouns(dialogue: str, player_profile: dict) -> str:
    """
    Replace pronoun tokens with player-specific pronouns.
    
    Args:
        dialogue: Raw dialogue string with tokens
        player_profile: Player's character selection data
    
    Returns:
        Dialogue with all tokens replaced
    """
    
    replacements = {
        "{player_name}": player_profile["chosen_name"],
        "{player_gender}": get_gender_reference(player_profile["pronouns"]),
        "{player_he_she}": get_pronoun_subject(player_profile["pronouns"]),
        "{player_him_her}": get_pronoun_object(player_profile["pronouns"]),
        "{player_his_her}": get_pronoun_possessive(player_profile["pronouns"]),
        "{player_himself_herself}": get_pronoun_reflexive(player_profile["pronouns"]),
    }
    
    for token, replacement in replacements.items():
        dialogue = dialogue.replace(token, replacement)
    
    return dialogue


def get_gender_reference(pronouns: str) -> str:
    """Map pronouns to gender reference noun."""
    mapping = {
        "he/him": "man",
        "she/her": "woman",
        "they/them": "person",
    }
    return mapping.get(pronouns, "person")


def get_pronoun_subject(pronouns: str) -> str:
    """Get subject pronoun (3rd person)."""
    mapping = {
        "he/him": "he",
        "she/her": "she",
        "they/them": "they",
    }
    return mapping.get(pronouns, "they")


def get_pronoun_object(pronouns: str) -> str:
    """Get object pronoun (3rd person)."""
    mapping = {
        "he/him": "him",
        "she/her": "her",
        "they/them": "them",
    }
    return mapping.get(pronouns, "them")


def get_pronoun_possessive(pronouns: str) -> str:
    """Get possessive pronoun (3rd person)."""
    mapping = {
        "he/him": "his",
        "she/her": "her",
        "they/them": "their",
    }
    return mapping.get(pronouns, "their")


def get_pronoun_reflexive(pronouns: str) -> str:
    """Get reflexive pronoun (3rd person)."""
    mapping = {
        "he/him": "himself",
        "she/her": "herself",
        "they/them": "themself",
    }
    return mapping.get(pronouns, "themself")
```

---

### Layer 4: Contextual Variation

Some dialogue should vary based on **which NPC is speaking** or **what context we're in**.

#### Rule 1: Institutional vs. Spiritual Language

**Malrik (Institutional)** uses formal pronouns and may use academic gender references:

```json
{
  "dialogue_id": "malrik_015_observation",
  "speaker": "malrik",
  "content": "The archives show that {player_gender.capitalize()} of {player_his_her} temperament rarely integrates well with systematic knowledge.",
  "tone": "institutional"
}
```

Output:
- Lior: "The archives show that a man of his temperament rarely integrates well with systematic knowledge."
- Lioren: "The archives show that a woman of her temperament rarely integrates well with systematic knowledge."
- Lior(en): "The archives show that a person of their temperament rarely integrates well with systematic knowledge."

**Elenya (Spiritual)** uses inclusive pronouns and nature metaphors:

```json
{
  "dialogue_id": "elenya_022_ritual",
  "speaker": "elenya",
  "content": "I see {player_name}. The glyphs see {player_him_her}. You are known.",
  "tone": "spiritual"
}
```

Output (all variants): "I see [name]. The glyphs see [them]. You are known."

---

#### Rule 2: NPC Familiarity with Pronouns

Some NPCs know the player's pronouns early; others learn gradually.

```python
NPC_PRONOUN_AWARENESS = {
    "malrik": {
        "aware_from_start": True,
        "formal_or_informal": "formal",
    },
    "elenya": {
        "aware_from_start": True,
        "formal_or_informal": "intimate",
    },
    "velinor": {
        "aware_from_start": True,
        "formal_or_informal": "formal",
    },
    "ravi": {
        "aware_from_start": False,
        "learns_at": "chapter_2",
        "formal_or_informal": "casual",
    },
}
```

---

#### Rule 3: Name Variation by NPC

Most NPCs use the player's chosen name consistently. Some may vary:

**Malrik:** Always uses formal name ("Lior", "Lioren", or "Lior(en)")

**Elenya:** May refer to player as "seeker" in spiritual contexts; uses name in intimate moments

**Velinor:** Always uses formal name; may use title ("the unintegrated")

**Ravi:** Uses casual nickname based on familiarity; learns full name over time

---

### Layer 5: Pronoun Markers (Optional UI Feature)

In dialogue, players can optionally see pronoun markers:

```
MALRIK:
"Welcome, Lior. You work competently."
[Pronouns: he/him]
```

This transparency helps players track that the system is working and what pronouns are active.

---

## Implementation Strategy

### Phase 1: Core System Setup

1. Create pronoun token registry in game data
2. Implement token replacement engine
3. Add pronoun profiles to all dialogue files
4. Test token replacement with sample dialogues

### Phase 2: NPC Integration

1. Update all existing NPC dialogue with tokens
2. Create NPC-specific tone guidelines
3. Test contextual variation
4. Verify character voice consistency

### Phase 3: Advanced Features

1. Add pronoun awareness system (NPC learns pronouns over time)
2. Implement nickname system (for close NPCs)
3. Add gender-specific glyph responses
4. Test romance options with pronoun variations

---

## Example Dialogues

### Example 1: Malrik's Greeting (All Variants)

**Raw dialogue (with tokens):**
```
malrik_005_welcome:
"Welcome to the Archive, {player_name}. I'm Malrik, Archivist of this place. 
{player_you}'ll be sorting records in the lower annex. The work is 
precise—if {player_you} can't commit to accuracy, I need to know now."
```

**Rendered (Lior):**
```
MALRIK:
"Welcome to the Archive, Lior. I'm Malrik, Archivist of this place. 
You'll be sorting records in the lower annex. The work is 
precise—if you can't commit to accuracy, I need to know now."
```

(Note: "You" and "your" are always used in direct address—no token substitution needed)

---

### Example 2: Velinor Speaking to Malrik About Player

**Raw dialogue (with tokens):**
```
velinor_042_to_malrik:
"What do you make of {player_name}? {player_he_she.capitalize()} carries something. 
A presence without integration. I wonder if {player_he_she} realizes {player_his_her} own potential."
```

**Rendered (Lior):**
```
VELINOR (to Malrik):
"What do you make of Lior? He carries something. 
A presence without integration. I wonder if he realizes his own potential."
```

**Rendered (Lioren):**
```
VELINOR (to Malrik):
"What do you make of Lioren? She carries something. 
A presence without integration. I wonder if she realizes her own potential."
```

**Rendered (Lior(en)):**
```
VELINOR (to Malrik):
"What do you make of Lior(en)? They carry something. 
A presence without integration. I wonder if they realize their own potential."
```

---

### Example 3: Elenya's Ritual (All Variants - Same)

**Raw dialogue:**
```
elenya_018_ritual:
"I see {player_name}. The glyphs see {player_him_her}. 
The memory system recognizes {player_you}. 
You are known, {player_name}. You are home."
```

**Rendered (all variants):**
```
ELENYA:
"I see [Lior/Lioren/Lior(en)]. The glyphs see them. 
The memory system recognizes you. 
You are known, [Lior/Lioren/Lior(en)]. You are home."
```

(Note: Elenya uses inclusive language regardless of pronouns)

---

## Edge Cases & Considerations

### 1. Names with Parentheses

The nonbinary name "Lior(en)" may need special handling:

- **In formal contexts:** May display as "Lior(en)" or "Lioren (integrated)"
- **In casual contexts:** May display as "Lior" or "Lior-en"
- **In speech:** Spoken as "Lior-en" (with hyphen pronunciation)

### 2. Pronoun Agreement

**Nonbinary pronouns ("they/them") require singular verb conjugation:**

- ✓ "They are talented" (not "They is talented")
- ✓ "They have potential" (not "They has potential")
- ✓ "Their work matters" (not "Their work matter")

All dialogue with "they/them" must use singular verb conjugation.

### 3. Reflexive Pronouns

- "He": "himself"
- "She": "herself"
- "They": "themself" (singular) or "themselves" (plural—avoid in 3rd person singular)

### 4. Possessive vs. Pronoun

- Possessive adjective: "their work" (always works)
- Possessive pronoun: "that work is theirs" (use with caution in narrative)

---

## Dialogue File Format

All dialogue files should use this structure:

```json
{
  "scene_id": "archive_study_01",
  "scene_name": "Archive Study - First Meeting",
  "dialogues": [
    {
      "dialogue_id": "malrik_001_welcome",
      "speaker": "malrik",
      "content": "Welcome to the Archive, {player_name}.",
      "pronouns_used": ["name"],
      "notes": "Simple greeting; no gender-specific references"
    },
    {
      "dialogue_id": "malrik_002_work_assignment",
      "speaker": "malrik",
      "content": "The work requires precision. Can you commit to that, {player_name}?",
      "pronouns_used": ["name"],
      "notes": "Uses 'you/your' in direct address; no token substitution"
    },
    {
      "dialogue_id": "velinor_015_observation",
      "speaker": "velinor",
      "addressee": "malrik",
      "about": "player",
      "content": "{player_he_she.capitalize()} shows potential. I wonder if {player_he_she} knows it.",
      "pronouns_used": ["subject", "subject_again"],
      "notes": "Speaking about player to someone else; requires 3rd person pronouns"
    }
  ]
}
```

---

## Implementation Checklist

- [ ] Create pronoun token registry
- [ ] Build token replacement engine
- [ ] Update character selection screen to store pronouns
- [ ] Add pronoun field to game state
- [ ] Convert all existing dialogue to use tokens
- [ ] Test replacement across all variants
- [ ] Verify NPC-specific tone consistency
- [ ] Add pronoun display UI feature (optional)
- [ ] Test romance dialogue with all variants
- [ ] Test glyph-specific dialogue variations
- [ ] Document all edge cases for writers

---

This system ensures that every player experiences **Velinor as written for them**—with natural language that respects their pronouns while maintaining the game's literary quality.
