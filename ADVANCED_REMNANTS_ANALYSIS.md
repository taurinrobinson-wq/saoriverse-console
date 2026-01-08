# Advanced REMNANTS Analysis: Ripple Matrices, Trait Stability & Tool Resonance

Based on the AI feedback, I've implemented three advanced analysis tools to understand the REMNANTS
system's emergent behavior:

## 1. **Ripple Matrix Analysis** 🌊
Shows how one NPC's trait changes cascade through the influence network.

### Key Findings:

**Aggressive Playstyle Cascades:**
- Ravi's resolve jumps → spreads skepticism (+0.70) to others
- Kaelen's authority spike (+0.55) → reduces nuance across network
- Nima's authority (+0.50) conflicts with natural skepticism → nuance drops (-0.55)

**Cautious Playstyle Cascades:**
- Ravi's memory spike (+0.30) flows to Tovren, Dalen
- Nima maintains high nuance even under wisdom influence
- Dalen acts as cascade amplifier (resolve +0.10, nuance +0.20)

**Empathetic Playstyle Cascades:**
- Kaelen's empathy surge (+0.60) is most dramatic NPC response
- Tovren's need jumps highest (+0.70) when shown compassion
- Trust ripples outward from multiple sources simultaneously

## 2. **Trait Stability Matrix** 📊
Measures which traits resist change (RIGID) vs. which shift easily (FLUID).

### Stability Rankings by Playstyle:

**Aggressive Play:**
- **RIGID:** Empathy (100%), Need (100%)
- **STABLE:** Memory (75%)
- **FLUID:** Authority (1.4%) ← Most affected
- **Insight:** Aggressive play hits authority hardest; empathy/need untouched

**Cautious Play:**
- **RIGID:** Resolve (75%), Empathy (75%), Need (75%)
- **STABLE:** Trust (31%)
- **FLUID:** Nuance (19%) ← Most affected
- **Insight:** Wisdom/observation overwhelmingly shifts nuance; core resolve stable

**Empathetic Play:**
- **FLUID:** Trust (31%), Skepticism (36%), Authority (1-5%)
- **Insight:** Empathy dissolves barriers; authority collapses under compassion

### Game Design Implication:
- **Aggressive routes** lock in core traits (empathy unchanging = ≠ redemption arc)
- **Cautious routes** preserve resolve (wisdom respects conviction)
- **Empathetic routes** shatter everything (true redemption possible)

## 3. **Tool Resonance Tracking** 🎁
Tools gifted to NPCs can amplify related traits and ripple to their allies.

### Example Tool Resonances:

| Tool | Primary Effect | Secondary Ripple | NPC Archetype |
|------|---|---|---|
| **Compass** | Observation +0.20, Nuance +0.15 | Strengthens Ravi, Nima, Kaelen | For navigators (Tovren) |
| **Journal** | Memory +0.20, Nuance +0.10 | Deepens observation network | For chroniclers (Nima) |
| **Mirror of Selfhood** | Empathy +0.20, Trust +0.15 | Opens hearts across network | For healers (Sera) |
| **Scales of Balance** | Wisdom +0.20, Nuance +0.15 | Sharpens judgment network | For judges |
| **Bell of Truth** | Trust +0.20, Authority -0.10 | Destabilizes authority | For truth-seekers |

**Tool Strategy Pattern:**
- Compass → Give to Tovren → ripples to merchant network → observation boost spreads
- Mirror → Give to Sera → ripples to healers → empathy becomes contagious
- Journal → Give to Nima → ripples to skeptics → skepticism becomes thoughtful

## 4. **Emergent System Behavior** 🧠

### Discovery 1: Playstyle "Lock-In"
Different playstyles create different baseline NPC configurations:
- **Aggressive** → Resolute but rigid (authority-driven)
- **Cautious** → Thoughtful but resistant (memory-driven)
- **Empathetic** → Fluid and open (trust-driven)

Changing playstyles mid-story requires OVERWRITING existing locked-in traits.

### Discovery 2: The "Conflict Zone"
When incompatible traits clash, NPCs show internal conflict:
- Ravi under Cautious play: Skepticism +0.70 but Nuance -0.55 = "Suspicious yet confused"
- Dalen under Mixed play: Resolve drops 0.80→0.55 = "Torn between strategies"
- Kaelen under Empathetic play: Extreme empathy despite thief background = "Conflicted redemption"

**Mechanic Possibility:** Internal conflict could trigger special dialogue lines.

### Discovery 3: NPC Vulnerability Windows
Certain trait combinations create "tool unlock" moments:
- Kaelen with empathy >0.6 and trust >0.4 = READY for redemption tool
- Nima with skepticism >0.8 and memory >0.8 = READY for truth tool
- Dalen with authority >0.7 and resolve >0.8 = READY for leadership tool

**UI Possibility:** Show which tools are "unlocking" based on current NPC state.

## 5. **Usage in Story Design** 📝

### Unlock Gating Example:

```python
def check_tool_unlock(npc, tool_name):
    """Check if NPC is ready for a specific tool."""
    if tool_name == "Mirror of Selfhood":
        # Empathy must be high, trust must exist
        if npc.remnants["empathy"] > 0.7 and npc.remnants["trust"] > 0.4:
            return True  # Unlock available
        elif npc.remnants["empathy"] > 0.6 and npc.remnants["trust"] > 0.6:
            return True  # Alternative unlock (both very high)

    elif tool_name == "Scales of Balance":
        # Nuance must be developed
        if npc.remnants["nuance"] > 0.7 and npc.remnants["wisdom"] > 0.6:
            return True

    return False
```


### Dialogue Branching Example:

```python
if player_playstyle == "aggressive":
    # Authority-focused NPCs respond well
    if npc.remnants["authority"] > 0.8:
        dialogue = "I respect your decisiveness. Lead the way."
    elif npc.remnants["resolve"] > 0.8:
        dialogue = "You have conviction. I can work with that."
else:
    # Different dialogue for non-aggressive
    dialogue = get_dialogue_for_playstyle(npc, player_playstyle)
```


### Ripple Event Trigger:

```python
def apply_tool_gift(npc_name, tool):
    """Give tool to NPC and trigger ripple."""
    npc = manager.get_npc(npc_name)
    npc.receive_tool(tool)  # Boosts relevant traits

    # Ripple to allies
    allies = influence_map.get(npc_name, {})
    for ally_name in allies:
        ally = manager.get_npc(ally_name)
        ally.hear_about_tool(tool)  # Secondary trait boost
```


## 6. **Running the Advanced Tests** 🧪

### Full Advanced Analysis:

```bash
python velinor/stories/test_remnants_advanced.py
```


**Output includes:**
1. Ripple matrices for Aggressive & Cautious playstyles 2. Trait stability analysis showing which
traits are rigid/fluid 3. Tool resonance mapping (example: Compass → Observation ripples) 4.
Playstyle comparison (System stability by strategy) 5. Kaelen cascade demonstration (redemption arc
example)

### Customize Analysis:
Edit `test_remnants_advanced.py` to:
- Add new playstyles (Mix courage + observation for unique profiles)
- Define custom tool resonances
- Test specific NPC redemption paths
- Model future story branches

## 7. **Next Level Ideas** 🚀

### Idea 1: "Stability Decay"
Traits under a certain stability threshold (FLUID) could drift toward neutral over time:

```python
def apply_stability_decay(npc, playstyle_matrix):
    """Highly volatile traits drift if not reinforced."""
    for trait, (avg_change, stability) in playstyle_matrix.items():
        if stability < 0.3:  # FLUID trait
            # Drift toward middle
            current = npc.remnants[trait]
            npc.remnants[trait] += (0.5 - current) * 0.02  # 2% drift/turn
```


### Idea 2: "Contradiction Events"
When internal conflicts reach critical mass, trigger special scenes:

```python
conflicts = [
    ("Kaelen", "empathy", 0.6, "skepticism", 0.8),  # Compassionate thief
    ("Ravi", "authority", 0.8, "skepticism", 0.2),  # Confident leader
]
if npc.has_contradiction(conflicts):
    trigger_internal_conflict_scene(npc)
```


### Idea 3: "Tool Synergy"
Multiple tools can amplify each other on same NPC:

```python
if "Mirror of Selfhood" in npc.tools and "Scales of Balance" in npc.tools:
    # Both empathy AND wisdom tools = unlock "wise healer" dialogue tree
    npc.unlock_synergy_tree("wise_healer")
```

## 

**Test Files:**
- [test_remnants_simulation.py](velinor/stories/test_remnants_simulation.py) - Basic 4 playstyle tests
- [test_remnants_advanced.py](velinor/stories/test_remnants_advanced.py) - Ripple, stability, tool analysis
- [REMNANTS_TEST_ANALYSIS.md](REMNANTS_TEST_ANALYSIS.md) - Basic test documentation

**System Core:**
- [npc_manager.py](velinor/engine/npc_manager.py) - REMNANTS engine (405 lines)
- [REMNANTS_SYSTEM_GUIDE.md](REMNANTS_SYSTEM_GUIDE.md) - Full documentation
