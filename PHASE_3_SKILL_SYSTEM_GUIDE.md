# Phase 3: Skill System & Dynamic Dialogue Architecture

## 🎯 Delivery Summary

Two foundational files created to enable the vocational apprenticeship system:

### 1. **Glyph_Organizer_Skills.csv** (23 columns)
- All 73 glyphs with complete metadata
- **NEW:** `skill_taught` column - What skill this glyph teaches
- **NEW:** `skill_required` column - What prerequisite skill is needed
- Ready for dialogue router and quest gatekeeper integration

### 2. **Skill_Registry.json** (62 core skills across 7 categories)
- Complete skill system definition
- Skill prerequisites and dependency chains
- REMNANTS effects for each skill
- Emotional impacts mapped to skill categories
- Taught-by relationships linking skills to glyphs

---

## 📊 Skill System Overview

### 7 Skill Categories (62 Skills Total)

| Category | Skills | Core Theme |
|----------|--------|-----------|
| **Collapse Discernment** | 7 | Clarity through understanding what breaks |
| **Legacy & Continuity** | 6 | Connection across time |
| **Sovereignty & Boundaries** | 7 | Agency through intention |
| **Presence & Witnessing** | 9 | Healing through witnessed presence |
| **Trust & Interdependence** | 10 | Survival through reliable bonds |
| **Joy & Creativity** | 10 | Resilience through joy and creation |
| **Ache & Grief** | 13 | Wisdom through witnessed loss |

---

## 🎓 How the System Works

### Example 1: Malrik's Apprenticeship Path

```
Player encounters Malrik → No skills yet
  ↓
Malrik says (Dialogue Bank A): "You're raw, but I see potential. Let's start simple."
  ↓
Player attempts: Glyph of Mirage Echo
  → Teaches: illusion_discernment
  ↓
Player returns with illusion_discernment
  ↓
Malrik says (Dialogue Bank B): "You're seeing clearly now. Ready for something deeper?"
  ↓
Player attempts: Glyph of Shattered Corridor
  → Requires: illusion_discernment (NOW MET)
  → Teaches: collapse_navigation
  ↓
Player now has: [illusion_discernment, collapse_navigation]
  ↓
Malrik says (Dialogue Bank C): "You understand how systems fracture. Come, the archives go deeper."
```

### Example 2: Player Coming from Different Path

```
Player trained with Tala FIRST
  → Learned: communal_celebration, exchange_appreciation
  ↓
Malrik says (Dialogue Bank B variant): "You're used to markets breathing. Archives are different.
They require patience. But your people-reading is sharp. Useful."
  ↓
Malrik adjusts quest difficulty/approach to match player's existing skills
```

---

## 📋 Skill Registry Structure

Each skill in the JSON has:

```json
{
  "skill_id": "illusion_discernment",
  "skill_name": "Illusion Discernment",
  "category": "collapse_discernment",
  "description": "Seeing through self-deception and false patterns",
  "taught_by_glyphs": ["Glyph of Mirage Echo"],
  "prerequisite_skill": "",
  "emotional_impact": "Clarity through understanding collapse",
  "remnants_effects": "memory:+0.1,presence:+0.1"
}
```

### Key Properties

- **skill_id** - Machine-readable identifier for dialogue routers
- **taught_by_glyphs** - Which glyphs teach this skill
- **prerequisite_skill** - Must acquire this skill first
- **emotional_impact** - Narrative resonance (for dialogue context)
- **remnants_effects** - REMNANTS traits modified when skill acquired

---

## 🔗 Skill Dependency Chains

### Example: The Witnessing Path
```
silent_witnessing (entry point)
  ↓
  ├→ connection_holding (requires: silent_witnessing)
  ├→ emotional_anchoring (requires: silent_witnessing)
  ├→ receptive_presence (requires: silent_witnessing)
  ├→ healing_presence (requires: silent_witnessing)
  └→ All other presence skills require silent_witnessing first
```

### Example: The Sovereignty Path
```
measured_movement (entry point)
  ↓
  ├→ boundary_setting (requires: measured_movement)
  │   └→ enforced_boundaries (requires: boundary_setting)
  ├→ impulse_regulation (requires: measured_movement)
  └→ (co_witnessing available without prerequisite)
```

---

## 🎮 How NPCs Use This System

### Malrik (Archivist)
**Teaches:** illusion_discernment, distortion_recognition, measured_movement, boundary_setting, lineage_interpretation

**Dialogue Bank Selection Logic:**
```
IF player_has_skill("illusion_discernment") AND NOT player_has_skill("collapse_navigation"):
    → Dialogue Bank B: "You see through illusions. Shall we go deeper?"
    
ELIF player_has_skill("collapse_navigation"):
    → Dialogue Bank C: "You're ready for the archives."
    
ELSE:
    → Dialogue Bank A: "You're untrained, but there's time."
```

**Quest Gating:**
```
IF NOT player_has_skill(glyph.skill_required):
    → Don't offer quest yet
    → Say: "Come back when you understand X"
```

### Tala (Market Cook/Merchant)
**Teaches:** communal_celebration, beauty_creation, exchange_appreciation, joy_witnessing

**Dialogue Shift Example:**
```
Player comes with measured_movement (from Malrik):
    → "You're careful. Markets need quick thinking. 
       But that discipline? It'll help you read people."
       → Adjust quest: Slower pace, more observation

Player comes with impulse_regulation (from Dakrin):
    → "You know how to hold back. In markets, that's power.
       Let's teach you when to let loose."
```

---

## 📈 Player Resume Structure

When the player acquires a skill, it's recorded:

```json
{
  "player_name": "...",
  "skills_acquired": [
    {
      "skill_id": "illusion_discernment",
      "skill_name": "Illusion Discernment",
      "learned_from": "Malrik",
      "date_acquired": "game_session_3",
      "via_glyph": "Glyph of Mirage Echo"
    },
    {
      "skill_id": "boundary_setting",
      "skill_name": "Boundary Setting",
      "learned_from": "Malrik",
      "date_acquired": "game_session_5",
      "via_glyph": "Glyph of Boundary Stone"
    }
  ],
  "npc_relationships": {
    "Malrik": {
      "status": "mentor",
      "dialogue_bank": "C",
      "first_encounter": "game_session_1",
      "times_returned": 4
    },
    "Tala": {
      "status": "unmet",
      "dialogue_bank": null
    }
  }
}
```

---

## 🔧 Implementation Roadmap

### Step 1: Load Skill Registry (Python)
```python
import json

with open('Skill_Registry.json', 'r') as f:
    skill_registry = json.load(f)

# Access skill data
skill = skill_registry['skills']['illusion_discernment']
print(skill['description'])  # "Seeing through self-deception..."
```

### Step 2: Create Dialogue Router
```python
class DialogueRouter:
    def select_bank(self, npc, player_resume, glyph):
        required_skill = glyph.get('skill_required')
        taught_skill = glyph.get('skill_taught')
        
        # Check if player has required skill
        if required_skill and required_skill not in player_resume['skills']:
            return npc.dialogue_bank_a  # "Not ready yet"
        
        # Check if player has adjacent skills
        if self.has_adjacent_skills(player_resume, glyph):
            return npc.dialogue_bank_b  # "Potential here"
        
        # Player is ready
        return npc.dialogue_bank_c  # "Full quest"
```

### Step 3: Create Quest Gatekeeper
```python
class QuestGatekeeper:
    def can_attempt_glyph(self, player_resume, glyph):
        required = glyph['skill_required']
        if required and required not in player_resume['skills']:
            return False
        return True
    
    def offer_quest(self, npc, player, glyph):
        if not self.can_attempt_glyph(player.resume, glyph):
            npc.say(f"Come back when you understand {glyph['skill_required']}")
            return
        
        npc.start_glyph_trial(glyph)
```

### Step 4: Create Skill Tracker
```python
class SkillTracker:
    def acquire_skill(self, player, skill_id, learned_from_npc):
        skill = self.skill_registry['skills'][skill_id]
        
        player.resume['skills_acquired'].append({
            'skill_id': skill_id,
            'skill_name': skill['skill_name'],
            'learned_from': learned_from_npc,
            'date_acquired': current_game_session()
        })
        
        # Apply REMNANTS effects
        self.apply_remnants_effects(player, skill['remnants_effects'])
        
        # Update NPC relationship
        self.update_npc_relationship(player, learned_from_npc)
```

---

## 📝 Dialogue Bank Template

Each NPC now has 4 dialogue banks per glyph:

```json
{
  "npc": "Malrik",
  "glyph": "Glyph of Mirage Echo",
  "dialogue_banks": {
    "bank_a_untrained": {
      "intro": "You're new to the desert. The mirages here... they'll confuse you.",
      "offer": "But before I can teach you, you need to understand the basics.",
      "redirect": "Come back when you've proven yourself elsewhere.",
      "returns_not_ready": "Not yet. You're still believing in false things."
    },
    "bank_b_partial": {
      "intro": "I see you've learned something of how the world breaks.",
      "offer": "That will help here. The mirages aren't random—they're echoes.",
      "adjustment": "You have some foundation. Let's build on it.",
      "returns": "You're seeing more clearly. Ready for the next layer?"
    },
    "bank_c_ready": {
      "intro": "You're ready for this. I can see it.",
      "offer": "The Mirage Echo teaches you to question reality itself.",
      "quest_setup": "Navigate the desert. When you see a mirage, choose to dismiss it.",
      "returns": "You understand now. The illusions were inside all along."
    },
    "bank_d_overqualified": {
      "intro": "You've learned so much. More than I expected.",
      "offer": "There's still something here for you—something about self-deception.",
      "adjusted_quest": "Let's go deeper. This time, look for the illusions inside yourself.",
      "returns": "You've seen through your own lies. That's rare."
    }
  }
}
```

---

## 🎯 Key Integration Points

### With Phase 1 (Semantic + REMNANTS)
- Skill acquisition triggers REMNANTS trait changes
- Skills modify player's emotional posture (semantic_tags)
- Dialogue selection uses skill context + emotional state

### With Phase 2 (Glyph Metadata)
- Each glyph now tied to specific skill (`skill_taught`)
- Prerequisites enforced before quest offer (`skill_required`)
- Skill acquisition recorded in player resume

### New Phase 3 Systems
- **Dialogue Router:** Selects correct dialogue bank based on player resume
- **Quest Gatekeeper:** Blocks/allows glyphs based on skill requirements
- **Skill Tracker:** Records acquisitions and applies effects
- **Resume Manager:** Tracks player's vocational biography

---

## 🌳 Sample Skill Tree Visualization

```
COLLAPSE DISCERNMENT
├── illusion_discernment (Glyph of Mirage Echo) [no prereq]
├── distortion_recognition (Glyph of Fractured Memory) [no prereq]
├── trauma_recognition (Glyph of Fractured Oath) [no prereq]
├── collapse_navigation (Glyph of Shattered Corridor) [requires: illusion_discernment]
├── truth_discernment (Glyph of Fractured Rumor) [requires: illusion_discernment]
├── false_covenant_recognition (Glyph of Hollow Pact) [no prereq]
└── deception_detection (Glyph of Cloaked Fracture) [requires: illusion_discernment]

LEGACY & CONTINUITY
├── lineage_interpretation (Glyph of Ancestral Record) [no prereq]
├── emotional_data_processing (Glyph of Sand Memories) [requires: lineage_interpretation]
├── ritual_participation (Glyph of Emotional Inheritance) [requires: emotional_data_processing]
├── ancestral_communion (Glyph of Echoed Breath) [requires: emotional_data_processing]
├── generational_voice (Glyph of Returning Song) [requires: ritual_participation]
└── legacy_persistence (Glyph of Hopeful Transmission) [requires: emotional_data_processing]

SOVEREIGNTY & BOUNDARIES
├── measured_movement (Glyph of Measured Step) [no prereq]
├── risk_acceptance (Glyph of Reckless Trial) [no prereq]
├── co_witnessing (Glyph of Held Ache) [no prereq]
├── boundary_setting (Glyph of Boundary Stone) [requires: measured_movement]
├── enforced_boundaries (Glyph of Iron Boundary) [requires: boundary_setting]
├── impulse_regulation (Glyph of Interruptive Restraint) [requires: measured_movement]
└── discernment_in_betrayal (Glyph of Venomous Choice) [requires: deception_detection]

[... and 4 more categories ...]
```

---

## 📊 Statistics

- **Total Skills:** 62
- **Entry-Level Skills (no prerequisite):** 28
- **Advanced Skills (require prerequisite):** 34
- **Max Skill Chain Depth:** 3 levels
- **Glyphs Teaching Skills:** 63 of 73 (86%)
- **Average Skills per Category:** 8.9

---

## 🚀 What's Next

1. **Create NPC Dialogue Banks** - Write 4 dialogue variants per NPC per glyph
2. **Build Dialogue Router Logic** - Python class to select correct bank
3. **Implement Quest Gatekeeper** - Block/allow quests based on prerequisites
4. **Create Skill Display UI** - Show player their resume/skills
5. **Wire to Game Loop** - Integrate skill tracking into main game state

---

## 📁 Files Created

**Location:** `d:\saoriverse-console\velinor\markdowngameinstructions\`

1. **Glyph_Organizer_Skills.csv** (59.6 KB + skill columns)
   - Use this instead of Glyph_Organizer_Expanded.csv
   - Contains all original data + new skill metadata

2. **Skill_Registry.json** (15 KB)
   - Master skill definition file
   - Load once at startup
   - Reference for all skill queries

---

## 💡 Design Philosophy

This system doesn't ask "What resources did you spend?"

It asks **"Who did you learn from? In what order? What does that say about who you're becoming?"**

Every skill acquired tells part of the player's story.

Every NPC encounter changes based on that story.

Every dialogue feels personally calibrated to the player's journey.

That's what makes it alive.

---

**Status:** ✅ Phase 3a Complete - Core skill system infrastructure ready
**Next:** Phase 3b - Dialogue bank creation and routing implementation
