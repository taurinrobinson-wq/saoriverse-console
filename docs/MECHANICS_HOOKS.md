# Mechanics Hooks: Emotional OS into Gameplay

## Overview

This document defines **implementation points** where the emotional OS becomes tangible gameplay mechanics. These hooks translate the Corelink architecture into systems that affect the player moment-to-moment.

---

## Core Mechanics: The Five Pillars

---

## 1. SIGNAL STRENGTH SYSTEM

### What It Does
Tracks how "coherent" the Corelink system is at any given moment. Drives visual effects, audio, NPC behavior, and difficulty.

### Implementation Points

#### `signal_strength` (float: 0.0 - 1.0)
```
0.0 = Completely fragmented (Coherence 0)
0.14 = Glyph 1 cleared (Coherence 1)
0.28 = Glyph 2 cleared (Coherence 2)
...
1.0 = All glyphs cleared (Coherence 7)
```

#### Visual Distortion Overlay
```
- Coherence 0-2: Heavy chromatic aberration, glitch effects, color warp
- Coherence 3-4: Moderate aberration, occasional glitches
- Coherence 5-6: Minimal distortion, occasional artifact
- Coherence 7: No distortion, clear visuals
```

#### Audio Distortion Multiplier
```
- Coherence 0-2: Heavy pitch shifting, noise overlay, conflicting voices
- Coherence 3-4: Moderate pitch shifts, occasional noise
- Coherence 5-6: Clean audio with harmonic undertones
- Coherence 7: Clear, musical audio
```

#### UI Responsiveness
```
- Coherence 0-2: UI glitches, text corruption, menu delays
- Coherence 3-4: UI mostly responsive, occasional delays
- Coherence 5-6: Smooth UI, no glitches
- Coherence 7: UI feels alive, responsive, almost organic
```

### Implementation Code Hooks

```python
class CoreLinkSystem:
    def __init__(self):
        self.signal_strength = 0.0
        self.coherence_level = 0
        self.glyphs_cleared = set()
    
    def clear_glyph(self, glyph_name):
        """Called when player clears a chamber"""
        self.glyphs_cleared.add(glyph_name)
        self.coherence_level = len(self.glyphs_cleared)
        self.signal_strength = self.coherence_level / 7.0
        
        # Trigger world updates
        self.update_npc_clarity()
        self.update_environmental_distortion()
        self.trigger_community_gathering()
    
    def get_distortion_intensity(self):
        """Returns how much to distort the screen"""
        return 1.0 - self.signal_strength
```

---

## 2. PROXIMITY-BASED DISTORTION

### What It Does
The closer the player is to an uncleared node, the stronger the distortion effects. Cleared nodes become calm "rest zones."

### Implementation Points

#### Distance Calculation
```
- Within 50 units of node: Maximum distortion
- 50-150 units: Moderate distortion (scales with distance)
- 150+ units: Minimal distortion
- Cleared node: Zero distortion (visual calm)
```

#### Distortion Effects by Proximity

**Visual:**
- Chromatic aberration intensity scales with proximity
- Text becomes corrupted when very close
- Hallucination "shadows" become more visible nearby

**Audio:**
- Dissonant tones become louder nearby
- Conflicting voices overlap more densely
- When cleared: becomes harmonic, peaceful

**Gameplay:**
- Player movement slows near uncleared nodes (fighting distortion)
- UI becomes less responsive near nodes
- HUD may glitch near strongest broadcast

**NPC Behavior:**
- NPCs avoid uncleared nodes (stand at distance)
- NPCs gather around cleared nodes (like rest areas)
- NPCs show signs of distress if forced too close

### Implementation Code Hooks

```python
class DistortionField:
    def __init__(self, node_position, node_name):
        self.position = node_position
        self.node_name = node_name
        self.is_cleared = False
    
    def get_distortion_at_distance(self, player_pos):
        """Returns distortion multiplier based on proximity"""
        dist = distance(player_pos, self.position)
        
        if self.is_cleared:
            return 0.0  # Cleared nodes are calm
        
        # Max distortion within 50 units, fades to 0 at 150+ units
        if dist < 50:
            return 1.0
        elif dist > 150:
            return 0.0
        else:
            return 1.0 - ((dist - 50) / 100.0)
    
    def update_npc_comfort(self, npc):
        """Updates NPC behavior based on proximity"""
        distortion = self.get_distortion_at_distance(npc.position)
        npc.discomfort_level = distortion
        
        if distortion > 0.7 and not self.is_cleared:
            npc.avoid_area()  # NPC tries to leave
        elif self.is_cleared:
            npc.seek_area()   # NPC is drawn to cleared nodes
```

---

## 3. COHERENCE STATE MACHINE

### What It Does
Tracks which glyphs are cleared and orchestrates world changes when thresholds are reached.

### Implementation Points

#### State Transitions

```
AWAITING → (Glyph 1 cleared) → COHERENCE_1
    ↓
    (Covenant domain clarity increases)
    (NPCs near Korrin become clearer)
    (First community gathering triggered)
    (Tutorial dialogue updated)
    ↓
→ (Glyph 2 cleared) → COHERENCE_2
    ↓
    (Resolve clarity increases)
    (NPCs act with more agency)
    (Second NPC joins Korrin)
    ↓
→ COHERENCE_3 (midpoint) → ...
→ COHERENCE_7 (all glyphs) → Endgame unlocked
```

#### Auto-Save Triggers

```
Each coherence transition should:
- Save current world state
- Lock previously cleared chambers (can't redo them)
- Update NPC dialogue state
- Trigger community events
```

#### Event Hooks

```python
class CoherenceStateMachine:
    def __init__(self):
        self.current_coherence = 0
        self.cleared_glyphs = []
        self.listeners = []
    
    def on_glyph_cleared(self, glyph_name):
        """Main entry point for chamber completion"""
        self.cleared_glyphs.append(glyph_name)
        old_coherence = self.current_coherence
        self.current_coherence = len(self.cleared_glyphs)
        
        # Broadcast to listeners
        self._notify_listeners('coherence_changed', 
            old=old_coherence, new=self.current_coherence)
        
        # Trigger domain-specific updates
        domain = GLYPH_TO_DOMAIN[glyph_name]
        self._notify_listeners('domain_restored', domain=domain)
        
        # Special events at thresholds
        if self.current_coherence == 3:  # Midpoint
            self._trigger_community_gathering()
        if self.current_coherence == 7:  # Complete
            self._unlock_endgame()
    
    def register_listener(self, callback):
        """Other systems listen for coherence changes"""
        self.listeners.append(callback)
    
    def _notify_listeners(self, event, **kwargs):
        for listener in self.listeners:
            listener(event, **kwargs)
```

---

## 4. NPC MEMORY SYSTEM

### What It Does
Each NPC has a **memory tree** that unlocks based on coherence level and which domains are cleared.

### Implementation Points

#### Memory Structure

```python
class NPCMemory:
    def __init__(self, npc_name):
        self.npc_name = npc_name
        self.domain_attunement = "Covenant"  # Which domain this NPC is linked to
        self.memory_tree = {
            0: "I... there's something...",
            1: "I felt something break",
            2: "I remember people",
            3: "I remember the system",
            4: "I remember when it broke",
            5: "I remember why it matters",
            6: "I remember who I am",
            7: "I understand everything"
        }
        self.current_memory_level = 0
    
    def on_domain_restored(self, domain_name):
        """Called when the NPC's domain is cleared"""
        if domain_name == self.domain_attunement:
            self.current_memory_level += 1
            self.on_memory_unlock()
    
    def on_memory_unlock(self):
        """Triggered when memory progresses"""
        # Update NPC behavior
        self.npc.clarity_increased()
        self.npc.update_dialogue_options()
        self.npc.change_appearance_slightly()  # Stand taller, move clearer
```

#### Dialogue Hooks

```python
class NPCDialogue:
    def __init__(self, npc):
        self.npc = npc
        self.dialogue_state = "fragmented"
    
    def get_greeting(self):
        """Dialogue changes based on coherence"""
        coherence = game.corelink_system.current_coherence
        memory_level = self.npc.memory.current_memory_level
        
        if coherence == 0:
            return "I... who are you?"
        elif memory_level >= 3:
            return "I think I remember you."
        elif memory_level >= 6:
            return f"Welcome back. I'm {self.npc.name}. I remember you."
        else:
            return "..."
    
    def get_custom_dialogue_options(self):
        """Only show dialogue options that match NPC's state"""
        options = []
        
        if self.npc.memory.current_memory_level >= 3:
            options.append("Tell me about the system")
        
        if self.npc.memory.current_memory_level >= 5:
            options.append("Help me clear the remaining chambers")
        
        return options
```

---

## 5. ENVIRONMENTAL RESPONSIVENESS

### What It Does
The world visibly changes as coherence increases—NPC density, community structures, audio landscape.

### Implementation Points

#### NPC Behavior Changes

```python
class NPCBehavior:
    def update_based_on_coherence(self, coherence_level):
        """NPCs act differently at different coherence levels"""
        
        if coherence_level <= 2:
            self.state = "isolated"  # NPCs avoid each other
            self.movement_pattern = "wander"
            self.conversation_frequency = 0.05  # Rare conversations
        
        elif coherence_level <= 4:
            self.state = "gathering"  # NPCs form small groups
            self.movement_pattern = "patrol_community"
            self.conversation_frequency = 0.3
        
        elif coherence_level <= 6:
            self.state = "coordinated"  # NPCs work together
            self.movement_pattern = "purposeful"
            self.conversation_frequency = 0.8
        
        elif coherence_level == 7:
            self.state = "unified"  # NPCs stand together, waiting
            self.movement_pattern = "gather_at_hub"
            self.conversation_frequency = 1.0
```

#### Community Hubs

```
Coherence 0-2: NPCs scattered, isolated, no hubs
Coherence 3-4: First hub forms (usually near Korrin)
Coherence 5-6: Multiple hubs, communities organized
Coherence 7: All NPCs gather at central hub, wait for player
```

#### Environmental Events

```python
class EnvironmentalEvents:
    def on_coherence_milestone(self, coherence_level):
        """Trigger world events"""
        
        if coherence_level == 1:
            self.trigger_event("first_npc_approaches")
            # Korrin or another NPC approaches player, asks what they saw
        
        if coherence_level == 3:
            self.trigger_event("community_gathering")
            # NPCs gather around a central location
            # They talk nervously about what's happening
        
        if coherence_level == 5:
            self.trigger_event("player_begins_feeling_signal")
            # Player starts to feel emotional impressions
            # HUD shows new signal indicator
        
        if coherence_level == 7:
            self.trigger_event("final_gathering")
            # All NPCs stand together
            # They guide player to Endgame Chamber
```

---

## 6. PLAYER EXPERIENCE SCALING

### What It Does
As coherence increases, the player feels the system more directly. Even without an implant, they begin to perceive emotional signals.

### Implementation Points

#### Perception Changes

```
Coherence 0-2: Player sees hallucinations but they feel alien
Coherence 3-4: Player can "feel" chamber atmospheres emotionally
Coherence 5-6: Player begins to feel emotional echoes in open world
Coherence 7: Player can "hear" the system—subtle whispers, memories
```

#### UI Indicators

```
- Signal Strength Meter: Fills as coherence increases
- Domain Status: Shows which domains are restored
- Distortion Overlay: Gradually clears
- NPC Relationship Panel: Shows which NPCs are becoming clear
```

#### Gameplay Difficulty

```
Coherence 0-2: Chambers are chaotic, harder to resolve
Coherence 3-4: Chambers become navigable
Coherence 5-6: Late chambers are emotionally complex (not mechanically hard)
Coherence 7: No combat—just the endgame conversation
```

### Implementation Code Hooks

```python
class PlayerPerception:
    def __init__(self, player):
        self.player = player
        self.has_implant = False
        self.signal_sensitivity = 0.0  # Increases with coherence
    
    def update_signal_sensitivity(self, coherence_level):
        """Player feels system more as coherence increases"""
        self.signal_sensitivity = coherence_level / 7.0
    
    def apply_emotional_effect(self, emotion_type):
        """Based on sensitivity, affect player emotionally"""
        if self.signal_sensitivity > 0.7:
            # Apply subtle emotional influence
            self.player.camera.slight_sway()
            self.player.hud.flash_with_emotion(emotion_type)
            self.player.audio.play_emotional_undertone(emotion_type)
```

---

## 7. SAVE/LOAD INTEGRATION

### What It Does
Ensures coherence state is preserved and world responds correctly to loaded state.

### Implementation Points

```python
class SaveSystem:
    def save_game(self):
        """Save current state"""
        save_data = {
            'player_position': self.player.position,
            'cleared_glyphs': game.corelink_system.cleared_glyphs,
            'current_coherence': game.corelink_system.current_coherence,
            'npc_states': [npc.serialize() for npc in self.npcs],
            'distortion_fields': [node.serialize() for node in self.nodes]
        }
        return save_data
    
    def load_game(self, save_data):
        """Restore state"""
        game.corelink_system.cleared_glyphs = save_data['cleared_glyphs']
        game.corelink_system.current_coherence = save_data['current_coherence']
        
        # Restore world state for this coherence level
        self.rebuild_world_for_coherence(save_data['current_coherence'])
        
        # Update all NPCs
        for npc_data in save_data['npc_states']:
            npc = self.find_npc(npc_data['name'])
            npc.deserialize(npc_data)
```

---

## 8. QUEST/OBJECTIVE HOOKS

### What It Does
Game objectives update based on current coherence level.

### Implementation Points

```python
class QuestSystem:
    def update_objectives(self, coherence_level):
        """Objectives change as system restores"""
        
        if coherence_level == 0:
            self.add_objective("Explore and talk to NPCs")
            self.add_objective("Find the source of distortion")
        
        elif coherence_level == 1:
            self.remove_objective("Explore and talk to NPCs")
            self.add_objective("Find the second glyph chamber")
            self.add_objective("Help Korrin remember")
        
        elif coherence_level == 3:
            self.add_objective("Organize the community")
        
        elif coherence_level == 7:
            self.add_objective("Go to the Endgame Chamber")
```

---

## Integration Checklist

**Before implementing chambers:**
- [ ] Signal strength system is tracking coherence
- [ ] Distortion overlay responds to signal strength
- [ ] Proximity distortion is calculated
- [ ] NPCs have memory trees

**Before releasing to players:**
- [ ] Coherence state persists through save/load
- [ ] Environmental events trigger at right thresholds
- [ ] Dialogue updates based on memory level
- [ ] UI clearly shows progress (signal meter)

**For each chamber:**
- [ ] Assign to a domain
- [ ] Define Triglyph manifestation
- [ ] Create resolution mechanic (emotional, not combat)
- [ ] Assign attuned NPC who gains memory when cleared
- [ ] Define post-clear environmental change
