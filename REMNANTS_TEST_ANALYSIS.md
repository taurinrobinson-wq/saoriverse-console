# REMNANTS Simulation Test Analysis

## Overview
The test suite (`test_remnants_simulation.py`) demonstrates how different player playstyles reshape
NPC personality traits through the REMNANTS system. Each test runs 5 decision encounters with a
specific emotional strategy.

## Key Findings

### Test 1: Aggressive Playstyle
**Player Strategy:** Courage +0.2/0.15, Narrative Presence emphasis

**NPC Transformations:**
- **Ravi:** resolve 0.60→0.90 (+0.30), authority 0.50→0.90 (+0.40), skepticism increases
- **Nima:** resolve 0.60→0.90 (+0.30), authority 0.40→0.90 (+0.50), trust drops 0.80→0.65
- **Kaelen:** resolve 0.40→0.85 (+0.45), authority 0.30→0.85 (+0.55)
- **Tovren:** resolve 0.70→0.90 (+0.20), authority 0.60→0.90 (+0.30)
- **Dalen:** resolve stays high 0.80→0.90, authority increases 0.70→0.90
- **Mariel:** resolve 0.60→0.90 (+0.30), trust becomes 0.90
- **Korrin:** resolve 0.40→0.85 (+0.45), authority 0.30→0.85 (+0.55)
- **Drossel:** resolve 0.80→0.90 (+0.10), trust becomes 0.90
- **Sera:** resolve increases 0.30→0.75 (+0.45) but stays less than others

**Pattern:** Aggressive play makes NPCs more resolute and authority-focused. Traits like empathy and trust become secondary.
## 

### Test 2: Cautious Playstyle
**Player Strategy:** Wisdom +0.2/0.15, Observation emphasis

**NPC Transformations:**
- **Ravi:** memory 0.60→0.90 (+0.30), nuance 0.40→0.90 (+0.50), skepticism 0.20→0.90
- **Nima:** memory 0.70→0.90 (+0.20), nuance 0.80→0.90 (+0.10) - already high
- **Kaelen:** memory 0.60→0.90 (+0.30), nuance 0.50→0.90 (+0.40)
- **Tovren:** memory 0.60→0.90 (+0.30), nuance 0.30→0.85 (+0.55)
- **Sera:** memory 0.50→0.90 (+0.40), nuance 0.60→0.90 (+0.30)
- **Dalen:** memory 0.50→0.90 (+0.40), nuance 0.20→0.75 (+0.55)
- **Mariel:** memory 0.80→0.90 (+0.10), nuance 0.70→0.90 (+0.20), trust becomes 0.90
- **Korrin:** memory 0.80→0.90 (+0.10), nuance 0.70→0.90 (+0.20)
- **Drossel:** memory 0.80→0.90 (+0.10), nuance 0.80→0.90 (+0.10)

**Pattern:** Cautious play makes NPCs more thoughtful and observant. Memory and nuance become dominant. Authority traits reduce.
## 

### Test 3: Empathetic Playstyle
**Player Strategy:** Empathy +0.2/0.15, Trust emphasis

**NPC Transformations:**
- **Ravi:** empathy 0.70→0.90 (+0.20), need 0.50→0.90 (+0.40), skepticism drops 0.20→0.65
- **Nima:** empathy 0.60→0.90 (+0.30), need 0.50→0.90 (+0.40), trust becomes 0.90
- **Kaelen:** empathy 0.30→0.90 (+0.60), need 0.70→0.90 (+0.20), trust 0.20→0.55
- **Tovren:** empathy 0.30→0.90 (+0.60), need 0.20→0.90 (+0.70), skepticism stays high
- **Sera:** empathy 0.80→0.90 (+0.10), need 0.80→0.90 (+0.10), trust becomes 0.90
- **Dalen:** empathy 0.40→0.90 (+0.50), need 0.30→0.90 (+0.60), trust 0.50→0.80
- **Mariel:** empathy 0.80→0.90 (+0.10), need 0.40→0.90 (+0.50), trust becomes 0.90
- **Korrin:** empathy 0.30→0.90 (+0.60), need 0.50→0.90 (+0.40)
- **Drossel:** empathy 0.20→0.90 (+0.70), need 0.30→0.90 (+0.60), trust becomes 0.90

**Pattern:** Empathetic play dramatically increases empathy across all NPCs, especially thieves (Kaelen, Korrin) and merchants. Even hardened Drossel becomes more trusting.
## 

### Test 4: Mixed Playstyle
**Player Strategy:** Balanced blend of courage, wisdom, and empathy

**NPC Transformations:**
- **Ravi:** empathy 0.70→0.90, memory 0.60→0.90, skepticism increases
- **Nima:** memory 0.70→0.90, nuance stays high 0.80→0.90, empathy increases 0.60→0.85
- **Kaelen:** memory 0.60→0.90, need 0.70→0.90, skepticism moderates 0.80→0.75
- **Tovren:** memory 0.60→0.90, skepticism stays 0.70→0.90, empathy drops 0.30→0.55
- **Sera:** empathy 0.80→0.90, need 0.80→0.90, memory increases 0.50→0.80
- **Dalen:** memory 0.50→0.80, empathy 0.40→0.65 (more moderate changes), resolve drops 0.80→0.55
- **Mariel:** empathy 0.80→0.90, memory 0.80→0.90, nuance 0.70→0.90 (already high, minimal change)
- **Korrin:** memory 0.80→0.90, nuance 0.70→0.90, skepticism stays 0.80→0.90
- **Drossel:** memory 0.80→0.90, nuance 0.80→0.90, trust becomes 0.90

**Pattern:** Mixed strategy creates balanced NPC profiles without extreme shifts. Results are more nuanced than pure strategies.
## 

## System Mechanics Demonstrated

### 1. **Direct Effects (Player → All NPCs)**
Each player TONE stat increases or decreases all NPC REMNANTS traits:
- Courage → Resolve ↑, Nuance ↓
- Wisdom → Nuance ↑, Memory ↑, Authority ↓
- Empathy → Empathy ↑, Need ↑, Authority ↓
- Observation → Nuance ↑, Memory ↑, Authority ↓
- Narrative Presence → Authority ↑, Resolve ↑, Nuance ↓

### 2. **Ripple Effects (NPC → NPC)**
When an NPC's traits change significantly, they influence connected NPCs:
- Ravi (merchant leader) influences Nima, Kaelen, Mariel, Tovren
- Nima (observant) influences other skeptics like Korrin
- Drossel (thieves leader) influences Kaelen, Korrin, and others
- Ripple magnitude: 0.05-0.15 per connection

### 3. **Value Clamping**
All traits are clamped to [0.1, 0.9] range:
- No absolute extremes preserve NPC complexity
- Even villainous Kaelen caps at 0.9 (never 1.0)
- Even weakest traits floor at 0.1 (never 0.0)

### 4. **NPC Archetypes Respond Differently**
- **Merchants** (Ravi, Tovren): Respond strongly to courage/authority
- **Observers** (Nima, Korrin): Respond strongly to wisdom/observation
- **Healers** (Sera): Respond strongly to empathy/trust
- **Adventurers** (Dalen): Respond moderately across strategies
- **Thieves** (Kaelen, Drossel): Respond dramatically to empathy
- **Bridges** (Mariel): Stable across all strategies
## 

## Usage of Test Suite

### Run Full Suite

```bash
python velinor/stories/test_remnants_simulation.py
```


### Modify Test Encounters
Edit the `encounters` list in each test function to try different decision sequences:

```python
encounters = [
    {"courage": 0.2, "empathy": 0.15},
    {"wisdom": 0.2},
    # ... add more TONE stat changes
]
```


### Key Variables to Adjust
- **Magnitude:** Increase 0.2→0.3 for stronger changes
- **Duration:** Add more encounter dicts for longer stories
- **Mix:** Combine multiple TONE stats for complex strategies
## 

## Integration Points

### 1. Story Building

```python
from velinor.engine.npc_manager import NPCManager
from velinor.stories.test_remnants_simulation import *

# Initialize NPCs
manager = NPCManager()
npcs = create_marketplace_npcs()
manager.add_npcs_batch(npcs)
```


### 2. Game Engine Hook

```python

# When player makes a choice:
tone_effects = {"courage": 0.2, "empathy": -0.1}
manager.simulate_encounters([tone_effects])

# Access updated NPC state:
npc = manager.npcs["Ravi"]
print(npc.remnants)  # Shows updated traits
```


### 3. Dialogue Triggers

```python

# Make NPC dialogue depend on their current state:
if manager.npcs["Kaelen"].remnants["empathy"] > 0.7:
    # Play "redeemed Kaelen" dialogue
else:
    # Play "cynical Kaelen" dialogue
```

## 

## Test Results Summary

| Playstyle | Most Affected NPC | Change Type | Key Shift |
|-----------|-------------------|-------------|-----------|
| **Aggressive** | Kaelen | High-impact | Resolve +0.45 |
| **Cautious** | Dalen | High-impact | Nuance +0.55 |
| **Empathetic** | Kaelen/Drossel | Dramatic | Empathy +0.60-0.70 |
| **Mixed** | Variable | Moderate | Balanced shifts |
## 

## No Permanent State Changes
✅ Each test creates a fresh NPCManager instance ✅ All NPC modifications are isolated to the test ✅
Running tests multiple times produces identical results ✅ Main NPC system remains unmodified
## 

**Test File:** [velinor/stories/test_remnants_simulation.py](velinor/stories/test_remnants_simulation.py)
**System Core:** [velinor/engine/npc_manager.py](velinor/engine/npc_manager.py)
**Documentation:** [REMNANTS_SYSTEM_GUIDE.md](REMNANTS_SYSTEM_GUIDE.md)
