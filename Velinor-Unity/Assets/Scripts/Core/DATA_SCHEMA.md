# Velinor Unity — Core Systems Data Schema

## 1. CodexState (Player Emotional State)

```json
{
  "activeTags": ["Grief", "Empathy", "Resolve"],
  "lastTriggeredPedestalId": "pedestal_001",
  "resolvedGlyphIds": ["glyph_001", "glyph_042"],
  "resonanceLevel": 0.45
}
```

### Fields:
- `activeTags` (array of strings): Emotional tags currently active in the player's Codex
- `lastTriggeredPedestalId` (string): The most recent pedestal activation
- `resolvedGlyphIds` (array of strings): Glyphs the player has already experienced
- `resonanceLevel` (float 0-1): Overall emotional attunement (derived from tags + glyphs)

---

## 2. Pedestal Definition (World Object)

```json
{
  "pedestalId": "pedestal_market_001",
  "linkedGlyphId": "glyph_sorrow_001",
  "requiredTags": ["Grief", "Empathy"],
  "location": "Market Ruins",
  "scene": "MarketRuins",
  "position": { "x": 12.5, "y": 0, "z": 8.3 },
  "activationRadius": 5.0,
  "description": "A stone pedestal half-buried in market dust. Faint tech hum emanates from its base.",
  "flavorText": "This place remembers loss.",
  "linkedNPCId": "npc_tala"
}
```

### Fields:
- `pedestalId`: Unique identifier
- `linkedGlyphId`: Which glyph chamber opens when activated
- `requiredTags`: Emotional tags needed to awaken this pedestal
- `location`: Scene and coordinates
- `activationRadius`: How close player must be to feel resonance
- `description`: Environmental text
- `linkedNPCId`: Optional NPC associated with this pedestal (for dialogue triggers)

---

## 3. Glyph Definition

```json
{
  "glyphId": "glyph_sorrow_001",
  "name": "Sorrow",
  "domain": "Ache",
  "layer0": "Poetic fragment about loss",
  "layer1": "NPC perspective on grief",
  "layer2": "Plaintext understanding of the emotional truth",
  "emotionalThemes": ["Loss", "Memory", "Acceptance"],
  "emitsTags": ["Sorrow", "Remembrance"],
  "chamberScene": "GlyphChamber_glyph_sorrow_001",
  "chamberDuration": 3.5,
  "imageAssetPath": "Assets/Graphics/Glyphs/full-color_glyphs/sorrow.png"
}
```

### Fields:
- `glyphId`: Unique identifier
- `name`: Display name
- `domain`: Category (Ache, Presence, Joy, etc.)
- `layer0/1/2`: The three-tier cipher structure
- `emotionalThemes`: Keywords for emotional tone
- `emitsTags`: Tags added to Codex when glyph is resolved
- `chamberScene`: Scene to load for the glyph chamber
- `imageAssetPath`: Where the visual glyph asset lives

---

## 4. NPC Definition

```json
{
  "npcId": "npc_tala",
  "name": "Tala",
  "role": "Market Cook",
  "location": "Market Ruins",
  "description": "A weathered woman tending to a cold hearth.",
  "remnants": {
    "resolve": 0.6,
    "empathy": 0.8,
    "memory": 0.7,
    "nuance": 0.8,
    "authority": 0.3,
    "need": 0.8,
    "trust": 0.4,
    "skepticism": 0.7
  },
  "dialogueSequenceId": "dialogue_tala_market_001",
  "linkedGlyphIds": ["glyph_sorrow_001", "glyph_shared_feast_001"],
  "emotionalArcs": {
    "start": "Closed, suspicious",
    "mid": "Warming, shares memory",
    "end": "Open, collaborative"
  }
}
```

### Fields:
- `npcId`: Unique identifier
- `name`, `role`: Display information
- `remnants`: 8-trait personality profile (drives response behavior)
- `dialogueSequenceId`: Reference to the dialogue JSON file
- `linkedGlyphIds`: Glyphs associated with this NPC
- `emotionalArcs`: How the NPC's emotional state evolves through the game

---

## 5. Dialogue Sequence

```json
{
  "sequenceId": "dialogue_tala_market_001",
  "npcId": "npc_tala",
  "npcName": "Tala",
  "lines": [
    {
      "lineIndex": 0,
      "speakerId": "Tala",
      "text": "You're new to the Ruins. I can tell by the way you look around—like you're trying to understand what broke.",
      "emotionalTags": [],
      "isChoice": false
    },
    {
      "lineIndex": 1,
      "speakerId": "Player",
      "text": "(Listen carefully)",
      "emotionalTags": ["Observation", "Empathy"],
      "isChoice": false
    },
    {
      "lineIndex": 2,
      "speakerId": "Tala",
      "text": "My daughter used to buy bread here. Before the Collapse.",
      "emotionalTags": ["Grief"],
      "isChoice": false
    },
    {
      "lineIndex": 3,
      "speakerId": "Player",
      "text": "(Player choice)",
      "emotionalTags": [],
      "isChoice": true,
      "choices": [
        {
          "choiceIndex": 0,
          "choiceText": "I'm sorry for your loss.",
          "emotionalTags": ["Empathy"],
          "nextLineIndex": 4
        },
        {
          "choiceIndex": 1,
          "choiceText": "What happened to her?",
          "emotionalTags": ["Observation"],
          "nextLineIndex": 5
        }
      ]
    },
    {
      "lineIndex": 4,
      "speakerId": "Tala",
      "text": "(She pauses, then nods) Thank you. Few people... remember to say that.",
      "emotionalTags": ["Trust"],
      "isChoice": false
    }
  ]
}
```

### Fields:
- `sequenceId`: Unique identifier
- `npcId`: Which NPC is speaking
- `lines`: Array of dialogue lines
- Each line has:
  - `speakerId`: Who is speaking
  - `text`: Dialogue text
  - `emotionalTags`: Tags added when this line plays
  - `isChoice`: If true, player must select from options
  - `choices`: Array of possible player responses (if isChoice=true)

---

## 6. Scene State (Per-Scene Flags)

```json
{
  "sceneName": "MarketRuins",
  "pedestalsState": {
    "pedestal_market_001": {
      "state": "Spent",
      "hasBeenActivated": true
    },
    "pedestal_market_002": {
      "state": "Dormant",
      "hasBeenActivated": false
    }
  },
  "doorsUnlocked": ["door_market_interior_001"],
  "environmentChanges": {
    "marketLighting": "warm",
    "fogDensity": 0.3
  },
  "npcStates": {
    "npc_tala": {
      "dialogueCompleted": true,
      "emotionalState": "Warm",
      "hasLeft": false
    }
  }
}
```

---

## 7. Global Save State

```json
{
  "saveSlotId": "slot_001",
  "playerName": "Lior",
  "timestamp": "2026-06-15T14:30:00Z",
  "currentScene": "MarketRuins",
  "playTime": 1800,
  "codexState": {
    "activeTags": ["Grief", "Empathy", "Resolve"],
    "lastTriggeredPedestalId": "pedestal_001",
    "resolvedGlyphIds": ["glyph_001"],
    "resonanceLevel": 0.45
  },
  "sceneStates": [
    { "sceneName": "MarketRuins", "...": "..." },
    { "sceneName": "TransitHub", "...": "..." }
  ],
  "globalFlags": {
    "hasMetTala": true,
    "hasEnteredGlyphChamber": true,
    "currentEmotionalArc": "Mid",
    "endingPath": "Fragments Freed"
  }
}
```

---

## 8. File Structure (Unity Project)

```
Assets/
├── Data/
│   ├── JSON/
│   │   ├── glyphs/
│   │   │   ├── glyph_sorrow_001.json
│   │   │   ├── glyph_shared_feast_001.json
│   │   │   └── ... (118 total)
│   │   ├── npcs/
│   │   │   ├── npc_tala.json
│   │   │   ├── npc_ravi.json
│   │   │   └── ... (21+ total)
│   │   ├── dialogue/
│   │   │   ├── dialogue_tala_market_001.json
│   │   │   └── ...
│   │   ├── pedestals/
│   │   │   ├── pedestals_market_ruins.json
│   │   │   └── ...
│   │   └── scenes/
│   │       ├── scene_market_ruins.json
│   │       └── ...
│   └── SaveGames/
│       ├── save_slot_001.json
│       ├── save_slot_002.json
│       └── save_slot_003.json
```

---

## 9. Codex UI Data (Runtime Display)

```json
{
  "glyphEntryId": "glyph_sorrow_001",
  "discovered": true,
  "displayName": "Sorrow",
  "imageAsset": "Assets/Graphics/Glyphs/full-color_glyphs/sorrow.png",
  "layers": {
    "0": {
      "title": "Fragment",
      "text": "Poetic fragment about loss",
      "unlocked": true
    },
    "1": {
      "title": "Echo",
      "text": "NPC perspective on grief",
      "unlocked": true
    },
    "2": {
      "title": "Truth",
      "text": "Plaintext understanding of the emotional truth",
      "unlocked": true
    }
  },
  "emotionalThemes": ["Loss", "Memory", "Acceptance"],
  "relatedNPCs": ["npc_tala", "npc_ravi"]
}
```

---

## Implementation Notes

### JSON Loading in Unity

```csharp
// Load glyph JSON
var glyphJson = Resources.Load<TextAsset>("Data/JSON/glyphs/glyph_sorrow_001");
var glyph = JsonUtility.FromJson<GlyphDefinition>(glyphJson.text);

// Load dialogue sequence
var dialogueJson = Resources.Load<TextAsset>("Data/JSON/dialogue/dialogue_tala_market_001");
var dialogue = JsonUtility.FromJson<DialogueSequence>(dialogueJson.text);

// Load pedestal data
var pedestalsJson = Resources.Load<TextAsset>("Data/JSON/pedestals/pedestals_market_ruins");
var pedestals = JsonUtility.FromJson<PedestalList>(pedestalsJson.text);
```

### Save/Load System

```csharp
// Save
var saveState = new GameSaveState { ... };
string json = JsonUtility.ToJson(saveState, prettyPrint: true);
System.IO.File.WriteAllText("Assets/Data/SaveGames/save_slot_001.json", json);

// Load
string json = System.IO.File.ReadAllText("Assets/Data/SaveGames/save_slot_001.json");
var saveState = JsonUtility.FromJson<GameSaveState>(json);
```

---

## C# Class Stubs

These classes are ready to implement based on the JSON schema above:

```csharp
[System.Serializable]
public class GlyphDefinition
{
    public string glyphId;
    public string name;
    public string domain;
    public string layer0, layer1, layer2;
    public List<string> emotionalThemes;
    public List<string> emitsTags;
    // ... etc
}

[System.Serializable]
public class NPCDefinition
{
    public string npcId;
    public string name;
    public string role;
    public RemnantTraits remnants;
    public List<string> linkedGlyphIds;
    // ... etc
}

[System.Serializable]
public class GameSaveState
{
    public string saveSlotId;
    public string playerName;
    public string currentScene;
    public CodexState codexState;
    public List<SceneState> sceneStates;
    // ... etc
}
```

---

## Next Steps

1. **Create JSON files** for the Market Ruins vertical slice (1 NPC, 2 pedestals, 1 glyph chamber, 1-2 dialogue sequences)
2. **Implement DataManager** to load and cache all JSON at startup
3. **Wire up Codex** to read NPC + Glyph data
4. **Test pedestal activation** with dialogue → emotional tags → resonance
5. **Build glyph chamber scene** for the first glyph
