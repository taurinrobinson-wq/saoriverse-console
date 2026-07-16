# Velinor: Playable Demo Roadmap
## From Shell to First Playable Story Beat

**Vision:** A complete, emotionally resonant first act playable in 2-4 weeks  
**Scope:** Saori intro → Marketplace → First glyph collection → Closure moment  
**Target:** Story-driven, dialogue-heavy, minimal combat (boss encounter only)

---

## 🎬 Demo Structure: 5 Sequential Scenes

### Scene 1: Saori's Chamber (5-10 min)
**Narrative:** Player awakens in a quiet space, meets Saori (the guide). Emotional setup.
**Mechanics:** Walking, listening, establishing tone
**Assets Needed:**
- ✅ Character controller (ready)
- ✅ Dialogue system (ready)
- ⚠️ Interior space (use MarioParadiso or create simple room)
- ⚠️ Saori 3D model/sprite (from your character images)
- ⚠️ Saori animation/idle state

**Blocking:** 15 min setup, dialogue writing already done
**Parallel Work:** Character model prep while dialogue is finalized

---

### Scene 2: Marketplace Meeting (10-15 min)
**Narrative:** Player encounters Ravi and Nima. Learn about Ophina's disappearance. First emotional beat.
**Mechanics:** NPC interaction (E-key), multi-character dialogue, branch detection
**Assets Needed:**
- ⚠️ Marketplace environment (BillemotdonggulLavaTubePack or ALP_Assets)
- ⚠️ Ravi model/sprite
- ⚠️ Nima model/sprite
- ✅ Dialogue system (supports multiple NPCs)
- ✅ Interaction zones

**Blocking:** 30 min environment setup, 2-3 hours dialogue scripting
**Parallel Work:** Character models while environment is being built

---

### Scene 3: Suspicion Encounter with Kaelen (5-10 min)
**Narrative:** Player meets the suspected thief. Dialogue suggests Kaelen may know something.
**Mechanics:** NPC interaction, dialogue trees, establishing mystery
**Assets Needed:**
- ⚠️ Interior/alley space (any asset pack)
- ⚠️ Kaelen model/sprite
- ✅ Dialogue system
- ✅ Interaction zones

**Blocking:** 20 min environment, 1-2 hours dialogue writing
**Parallel Work:** Character model creation

---

### Scene 4: Glyph Collection Sequence (15-20 min)
**Narrative:** Player discovers three glyphs: Sorrow, Remembrance, Legacy
- Sub-scene 4a: Finding Glyph of Sorrow (outdoor, emotional discovery)
- Sub-scene 4b: Finding Glyph of Remembrance (dialogue-triggered memory)
- Sub-scene 4c: Finding Glyph of Legacy (puzzle moment with Nima)

**Mechanics:**
- ✅ Item pickup system (extend InteractionZone)
- ✅ Inventory tracking (CodexManager.emotionalTags can track glyphs)
- ✅ Glyph UI display
- ⚠️ Simple environmental puzzles
- ⚠️ Emotional state changes (adding glyph → emotional response)

**Assets Needed:**
- ⚠️ Three distinct outdoor environments
- ⚠️ 3D glyph models (simple geometric, glowing)
- ✅ Dialogue system (for emotional reactions)
- ⚠️ Nima model for sub-scene 4c

**Blocking:** 1-2 hours per environment, 2 hours puzzle logic, 2 hours glyph logic
**Parallel Work:** Environment and glyph model creation

---

### Scene 5: Triglyph Door & Boss Chamber (15-20 min)
**Narrative:** Player reaches cave entrance, uses three glyphs on door panel, enters chamber. Boss encounter.
**Mechanics:**
- ⚠️ Glyph door puzzle (place glyphs in sequence)
- ⚠️ Boss encounter (health system, basic combat)
- ✅ Dialogue system (pre/post combat dialogue)

**Assets Needed:**
- ⚠️ Cave environment (BillemotdonggulLavaTubePack—perfect for this)
- ⚠️ Door panel UI/model
- ⚠️ Boss creature model
- ⚠️ Combat system (HP, attack, player damage)
- ✅ Dialogue for boss encounter

**Blocking:** 1 hour environment, 2 hours puzzle/door logic, 3-4 hours boss combat
**Parallel Work:** Boss creature model, combat logic while cave is being built

---

### Scene 6: Resolution (10-15 min)
**Narrative:** Boss defeated. Player receives Transcendance Glyph. Returns to Ravi/Nima. Emotional closure. Player confronts own loss.
**Mechanics:**
- ✅ Item acquisition
- ✅ Dialogue with emotional payoff
- ✅ Emotional tagging system (grief, closure, empathy)

**Assets Needed:**
- ⚠️ Return location (marketplace or neutral space)
- ⚠️ Transcendance Glyph model
- ✅ Dialogue system
- ✅ Emotional state tracking

**Blocking:** 30 min environment, 2-3 hours dialogue writing and emotional scripting

---

## 📊 Implementation Timeline (2-4 Week Sprint)

### Week 1: Foundation & Scene 1-2
**Days 1-2:**
- [ ] Establish character model workflow (see Character Pipeline below)
- [ ] Create Saori character (model/sprite)
- [ ] Import marketplace environment (ALP_Assets or similar)

**Days 3-5:**
- [ ] Build Saori's Chamber scene (simple interior)
- [ ] Test Saori dialogue with emotional tags
- [ ] Create Marketplace scene layout
- [ ] Create Ravi & Nima character models

**Deliverable:** Playable Scenes 1-2 with placeholder characters

---

### Week 2: Middle Acts & Characters
**Days 6-8:**
- [ ] Create Kaelen character model
- [ ] Build alley/meeting space for Scene 3
- [ ] Implement glyph item system (pickup/inventory)
- [ ] Create glyph visual models (glowing geometric shapes)

**Days 9-10:**
- [ ] Build 3 environment spaces for glyph collection (outdoor spaces)
- [ ] Implement glyph door puzzle logic
- [ ] Create puzzle UI

**Deliverable:** Playable Scenes 1-4 with full glyph collection loop

---

### Week 3: Boss & Combat
**Days 11-13:**
- [ ] Import cave environment (BillemotdonggulLavaTubePack)
- [ ] Create boss creature model
- [ ] Build combat system (basic health/damage)

**Days 14-15:**
- [ ] Implement boss encounter logic
- [ ] Test player→boss→player damage flow
- [ ] Create Transcendance Glyph model

**Deliverable:** Full playable Scenes 1-5, boss encounter works

---

### Week 4: Polish & Resolution
**Days 16-18:**
- [ ] Write all dialogue (Saori, Ravi, Nima, Kaelen, Boss)
- [ ] Emotional tag scripting (grief, trust, empathy)
- [ ] Build resolution scene

**Days 19-20:**
- [ ] Test full flow (all 6 scenes sequentially)
- [ ] Debug interactions, dialogue sequencing
- [ ] Polish UI (glyph display, inventory, door panel)
- [ ] Add ambient audio placeholders

**Deliverable:** Fully playable demo, end-to-end story

---

## ✅ What's Ready (No Time Cost)
- ✅ Character controller & movement
- ✅ Dialogue system with typewriter effect
- ✅ NPC interaction framework
- ✅ Emotional tagging system (CodexManager)
- ✅ Scene management
- ✅ Asset collection (25+ packages locally)

---

## ⚠️ What Needs Building (Main Time Cost)

| Task | Est. Time | Blocker? | Parallel? |
|------|-----------|----------|-----------|
| Character model prep (4 NPCs) | 8-10 hrs | YES | YES - can happen anytime |
| Environments (5 scenes) | 8-10 hrs | YES | YES - each scene independent |
| Glyph system (pickup/inventory) | 4-5 hrs | YES | YES - after characterization |
| Door puzzle logic | 2-3 hrs | NO | YES - after glyph system |
| Boss combat system | 4-6 hrs | YES | YES - parallel to scene building |
| Dialogue writing & scripting | 8-10 hrs | NO | YES - parallel to all work |
| Testing & polish | 4-5 hrs | NO | NO - final phase |

**Critical Path:** Character models → Environments → Boss system (can work in parallel)

---

## 🎨 Character Pipeline: 2D to 3D
### Your Images → Game-Ready Models

You have **excellent animation frames** from your ezgif-split folder (turntable rotations). Here's how to bring them into 3D:

### Option A: Sprite-Based Characters (FASTEST - Recommended for Demo)
**Approach:** Use your character images as textured quad billboards in 3D space

**Workflow:**
```
1. Export sprite sheet from GIF frames
   - Use your GIF → sprite sheet tool
   - Grid: 5 columns × N rows (5 rotation angles)
   - Size: 1024x1024 or 512x512 per frame

2. Create simple quad/cylinder mesh in Unity
   - UV-mapped to sprite sheet
   - Uses correct frame based on camera angle to character
   - Single-sided mesh (camera always facing)

3. Animate with sprite sheet coordinates
   - Idle: frame 1-5 loop (all rotations)
   - Walk: frames 6-10 (next rotation angle)
   - Talk: frames vary by angle

4. Add glow/outline shader for "3D feel"
   - Makes 2D art feel more game-like
   - URP has outline shaders in asset store
```

**Time:** 2-3 hours per character (frame export + quad setup + shader)  
**Quality:** Looks pseudo-3D, perfect for story-driven game  
**Advantage:** Uses your existing art perfectly

---

### Option B: Simple 3D Models with Your Art as Texture (MEDIUM QUALITY)
**Approach:** Create low-poly 3D shapes, use turntable images as texture maps

**Workflow:**
```
1. Use Adobe Illustrator turntables
   - Already have 5-8 rotation angles per character
   - Export as individual PNG files

2. Create simple 3D form in Blender (free)
   - Basic capsule shape for body
   - Cube for head
   - Simple cylinder limbs
   - Total: 8-12 vertices per character

3. UV unwrap to use turntable images
   - Blend images for smooth rotation effect
   - Or swap images based on camera angle

4. Rig with simple bones
   - Use Blender's armature
   - Basic idle/walk/talk poses
   - Export as FBX

5. Import into Unity
   - Add Animator controller
   - Set up state machine (idle/walk/talk)
```

**Time:** 4-6 hours per character (Blender modeling, rigging, export, Unity setup)  
**Quality:** Looks more 3D, proper character controllers  
**Advantage:** Full 3D compatibility, better for game feel

---

### Option C: AI-Assisted 3D Generation (EXPERIMENTAL)
**Tools to explore:**
- **Blockade Labs** - Convert 2D images to 3D scenes/characters
- **Nomad Sculpt** (iPad) - Sculpt 3D from 2D reference
- **Meshmixer** - Combine/modify 3D forms
- **Stable Diffusion + Depth** - Generate 3D from 2D

**Workflow:** Generate rough 3D → Polish in Blender → Import to Unity

**Time:** 2-4 hours per character (depending on tool quality)  
**Quality:** Variable, requires cleanup  
**Advantage:** Fastest if tools work well

---

## 🎯 Recommended Character Pipeline for Your Demo

**Step 1 (Fast Path):** Use **Option A (Sprite Billboards)** for Scenes 1-4
- Takes 8-12 hours total for 4 characters
- Looks great for dialogue-heavy scenes
- No rigging complexity

**Step 2 (Polish):** If time allows, upgrade Scene 5 (Boss) to **Option B** for more dramatic 3D effect
- Boss feels more "real" in combat
- Takes additional 4-6 hours
- Creates visual distinction for climax

**Step 3 (If extra time):** Upgrade remaining characters gradually

---

## 📋 Specific Next Steps

### Immediate (Today/Tomorrow):
1. Export your character GIF animations as sprite sheets
   - Frame size: recommend 512x512 or 1024x1024
   - Grid layout: 5 columns (rotation angles) × rows (animation frames)
   - Format: PNG with transparency

2. Create character documentation:
   - Saori: Which GIF frame range = idle/talk?
   - Ravi: Animation frames?
   - Nima: Animation frames?
   - Kaelen: Animation frames?
   - Boss: Do you have creature art?

3. Identify 2-3 scene environments from asset packs you already have

### This Week:
1. Build Scene 1 (Saori's Chamber) with sprite billboard character
2. Set up Marketplace scene environment
3. Write complete Scene 1 dialogue

### What I Can Help With:
- [ ] Creating the sprite billboard shader/prefab system
- [ ] Writing scene layout/scripting
- [ ] Building dialogue sequences
- [ ] Glyph system implementation
- [ ] Boss combat logic
- [ ] Audio cue system
- [ ] UI for glyph display/inventory

---

## 🎬 Success Metrics for Week 1
- [ ] At least one complete scene playable end-to-end
- [ ] Two character models in-game (even as simple sprites)
- [ ] Dialogue flowing naturally with emotional tags
- [ ] Player can walk, interact with NPC, trigger dialogue
- [ ] One glyph collectible and visible in UI

---

## Questions Before Starting

1. **Boss creature:** Do you have artwork for the tri-glyph boss? (Or should I create conceptual design first?)
2. **Saori design:** Is Saori in the character image set, or separate character?
3. **Scene preferences:** Any specific mood/setting for Saori's chamber? (Mystical? Minimalist? Ornate?)
4. **Voice/Audio:** Planning voice acting, or text-only dialogue?
5. **Ending:** Does closure scene happen in same location as marketplace, or new space?

---

**Status:** Ready to execute. All systems in place. Waiting on:
- Character model pipeline confirmation
- Dialogue finalization
- Environment selection from asset packs

This is achievable. Let's build your demo. 🎮
