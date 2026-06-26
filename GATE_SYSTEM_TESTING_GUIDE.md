# GATE-BASED DIALOGUE SYSTEM — TESTING GUIDE

## 🎮 How to Test in Play Mode

### STEP 1: Generate the Test Scene

In Unity Editor:
1. Go to **Velinor** menu → **Create Malrik & Elenya Test Scene**
2. Wait for scene to generate (check console for ✅ confirmations)
3. You should see:
   - Ground plane (brown)
   - Player (blue capsule at center, looking up slightly)
   - Malrik (purple capsule, forward)
   - Elenya (cyan capsule, to the side)
   - UI elements ready

### STEP 2: Enter Play Mode

1. Press **Play** (or Ctrl+P)
2. You should see stat displays in corners:
   - **Top-left (cyan)**: Player TONE stats
   - **Top-right (magenta)**: Current NPC REMNANTS stats
3. Movement prompt at top of screen: "Press E to talk"

### STEP 3: Test Basic Movement

**Controls**:
- **WASD**: Move forward/back/strafe left/right
- **Space**: Jump
- **Right-mouse drag**: Look around
- **E**: Talk to nearby NPC

Try moving around the scene to verify physics work correctly.

---

## 🎭 Test Scenario 1: Malrik with HIGH EMPATHY

**Purpose**: Unlock emotional vulnerability dialogue in Malrik's story

### Setup
1. In Play mode, look at the Player Stats (top-left cyan text)
2. **Modify TONE stats** (you'll need to add debug buttons OR manually edit in code):
   - Set **Empathy (E)** to 0.8+
   - Keep others at 0.5
3. Walk toward Malrik (forward from spawn)
4. When close enough, press **E**

### Expected Behavior
- Dialogue canvas appears (dark background with NPC name and dialogue)
- Malrik's available Act 1 segment should display
- Only choices requiring empathy appear
- Stat display updates show NPC stats (Malrik's default values)
- Player can select choices
- Stat effects apply (watch cyan empathy value change)

### What to Verify
- ✅ Dialogue appears
- ✅ Gate system evaluated (only empathy-gated segments available)
- ✅ Buttons show TONE labels (T/O/N/E)
- ✅ Choices have player lines
- ✅ Stat effects apply after selection
- ✅ Scene doesn't crash

---

## 🎭 Test Scenario 2: Elenya with HIGH NARRATIVE PRESENCE

**Purpose**: Unlock spiritual depth dialogue in Elenya's story

### Setup
1. Set Player TONE stats:
   - **Narrative Presence (N)** to 0.75+
   - Others at 0.5
2. Walk toward Elenya (to the left from spawn)
3. Press **E**

### Expected Behavior
- Elenya's dialogue appears
- Segments requiring narrative presence show
- Choices reflect spiritual themes
- Stat display shows Elenya's stats

### What to Verify
- ✅ Elenya initializes separately from Malrik
- ✅ Different story data loads
- ✅ Gate evaluation works for different NPC
- ✅ Stat effects apply to Elenya's stats separately

---

## 🎭 Test Scenario 3: LOW EMPATHY Playthrough

**Purpose**: Verify gate blocking works (doors close, not open)

### Setup
1. Set Player TONE stats:
   - **Empathy (E)** to 0.2 (LOW)
   - Others at 0.5
2. Try talking to Malrik
3. Watch console for gate evaluation messages

### Expected Behavior
- Dialogue appears (Act 1 seg 1 might still show - no empathy gate)
- Some dialogue options appear grayed out or unavailable
- Stat display shows blocked access
- Console shows gate evaluation messages

### What to Verify
- ✅ Gates actually prevent dialogue (not just cosmetic)
- ✅ Error handling doesn't crash if no segments available
- ✅ Console messages show gate checks happening

---

## 📊 Understanding Console Output

When testing, watch the console for these messages:

```
✅ Initialized Malrik (8-act gate-based dialogue)
✅ Initialized Elenya (8-act gate-based dialogue)
```
→ Scripts loaded successfully

```
🟣 Player detected near Malrik
Press E to talk to Malrik
```
→ Proximity detection working

```
🔮 Gate Check: tone_stat empathy >= 0.75
✅ Gate OPEN (empathy = 0.85)
```
→ Gate evaluation working

```
🟢 Setup button: (T) - "Player line text"
```
→ Choice button created

```
📊 statName +0.1: 0.75
```
→ Stat effect applied

```
📖 Malrik segment completed: malrik_act1_seg1
```
→ Progression tracked

---

## 🐛 Troubleshooting

### Issue: "DialogueCanvas not found"
**Solution**: Verify SetupMalrikElenyaTestScene created all UI elements. Check hierarchy for DialogueCanvas.

### Issue: No dialogue appears when pressing E
**Solution**: 
- Check if player is in range (console should show "Player detected")
- Verify NPC has NPCInteraction component with correct npcId ("Malrik" or "Elenya")
- Check console for gate evaluation errors

### Issue: Stat effects not applying
**Solution**:
- Verify stat effects defined in JSON have correct names (lowercase: "empathy", "observation", etc.)
- Check console for "ApplyGateBasedStatEffects" messages
- Verify PlayerStats.Get() returns valid instance

### Issue: Wrong NPC stats display
**Solution**:
- Check if correct NPC stat object being used (malrikStats vs elenyaStats)
- Verify stat display UI accessing correct component on NPC

---

## 🎯 Full Test Checklist

**Scene Generation**:
- [ ] Scene creates without errors
- [ ] All NPCs spawn in correct positions
- [ ] Ground, lighting, UI all visible
- [ ] Stat display shows player stats (top-left cyan)

**Movement & Proximity**:
- [ ] Player movement works (WASD)
- [ ] Looking around works (right-mouse)
- [ ] Proximity detection shows/hides prompt
- [ ] E key triggers dialogue

**Dialogue Flow - Malrik**:
- [ ] Dialogue canvas appears
- [ ] NPC name shows ("Malrik")
- [ ] Dialogue text displays
- [ ] 4 TONE buttons appear (labeled T/O/N/E)
- [ ] Buttons are clickable
- [ ] Choice text shows player line

**Dialogue Flow - Elenya**:
- [ ] Same as Malrik
- [ ] But with different story data
- [ ] Stats display Elenya values (top-right magenta)

**Stat System**:
- [ ] Stat display updates in real-time
- [ ] Choices modify player TONE values
- [ ] NPC stats visible in magenta
- [ ] Coherence calculated correctly (if implemented)

**Gate Evaluation**:
- [ ] Some segments available, some not
- [ ] Availability changes with different TONE stats
- [ ] Console shows gate checks
- [ ] Proper error handling if no segments available

**No Crashes**:
- [ ] Play mode runs smoothly
- [ ] Dialogue transitions smoothly
- [ ] Multiple dialogues don't cause issues
- [ ] Exit play mode without errors

---

## 📈 Advanced Testing

### Test Multiple TONE Combinations

Try these combinations:

| Combo | Stats | Expected Result |
|-------|-------|---|
| High Empathy | E=0.9, O/T/N=0.5 | Emotional dialogue unlocks |
| High Observation | O=0.9, E/T/N=0.5 | Subtle truth dialogue unlocks |
| Balanced | E/O/T/N all 0.7 | Wisdom/coherence dialogue unlocks |
| High Narrative | N=0.9, E/O/T=0.5 | Spiritual dialogue unlocks (Elenya) |

### Test Gate Progression

1. Start with low empathy (0.2)
2. Select choices that increase empathy
3. Close dialogue
4. Open dialogue again with Malrik
5. Verify new (empathy-gated) segments now available

### Test Segment Completion

1. Talk to Malrik, complete Act 1, Seg 1
2. Close dialogue
3. Open dialogue again
4. Verify Act 1, Seg 1 doesn't repeat
5. Verify Act 1, Seg 2 is now available (if gates open)

---

## 🎬 What Success Looks Like

**In Play Mode, you should be able to**:

1. Walk around scene freely with proper physics
2. Approach Malrik, see "Press E to talk to Malrik"
3. Press E and see:
   - Dark dialogue panel
   - "Malrik" or "???" as NPC name
   - His dialogue text
   - 4 buttons labeled (T), (O), (N), (E)
4. Select a choice
5. See stat effects apply (watch top-left cyan text change)
6. Close dialogue
7. See stat display update
8. Repeat with different TONE values
9. Notice different dialogue available based on stats
10. Walk to Elenya, repeat with her story

**Most importantly**: Each choice you make actually matters. Your TONE stats, the gates they unlock, the dialogue you access—it all flows together as a complete, functioning dialogue system.

---

## 🚀 Next Steps After Testing

**If tests pass**:
1. Celebrate! 🎉 You have a working gate-based dialogue system
2. Commit any bug fixes
3. Expand to second NPC (Nima)
4. Implement UI to show which gates are blocking
5. Add more NPCs using same pattern

**If bugs found**:
1. Note exact steps to reproduce
2. Check console messages
3. Verify JSON is valid
4. Check that C# classes match JSON structure
5. Use debug buttons to modify TONE stats dynamically

---

## 📖 Key Files for Testing

**Scene Generator**:
- `Assets/Scripts/Editor/SetupMalrikElenyaTestScene.cs`

**Integration**:
- `Assets/Scripts/Core/NPCInteraction.cs`

**Gate System**:
- `Assets/Scripts/Core/DialogueGateEvaluator.cs`

**Story Data**:
- `Assets/Resources/Dialogue/MalrikStoryGates.json`
- `Assets/Resources/Dialogue/ElenyaStoryGates.json`

**Sequence Loaders**:
- `Assets/Scripts/Core/MalrikDialogueSequence.cs`
- `Assets/Scripts/Core/ElenyaDialogueSequence.cs`

**Stat System**:
- `Assets/Scripts/Core/PlayerStats.cs`
- `Assets/Scripts/UI/StatDisplayUI.cs`

---

## 💡 Pro Tips

1. **Set breakpoints** in NPCInteraction.OnGateBasedChoiceSelected to step through stat application
2. **Add debug buttons** to quickly set TONE stats during testing (e.g., Button "Max Empathy")
3. **Use console filters** to see only "Malrik" or "Elenya" messages
4. **Save test runs** as scenes so you can reproduce bugs easily
5. **Modify JSON** to test with simpler gate requirements (lower thresholds) for faster testing

---

## 🎯 Success Criteria

You'll know the system works when:

✅ Game runs without crashing  
✅ Dialogue appears and is readable  
✅ Choices show TONE labels  
✅ Selecting choices modifies stats  
✅ Different TONE combinations unlock different dialogue  
✅ Gates actually prevent access to some dialogue  
✅ Segments don't repeat  
✅ Both Malrik and Elenya work independently  
✅ Stat display updates in real-time  
✅ Console shows appropriate gate evaluation messages  

**That's it. That's the whole system working.** 🎭
