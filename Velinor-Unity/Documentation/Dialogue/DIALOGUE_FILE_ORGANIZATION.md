# Dialogue File Organization

## Folder Structure

The `/Assets/Resources/Dialogue/` folder is organized by **primary NPC** to manage the growing narrative complexity. All 24 NPCs from the Glyph_Organizer have dedicated folders:

```
Dialogue/
├── Cal/                 (empty)      - Cal, the Mediator
├── Drossel/             (empty)      - Drossel, Black-Market Salvage Broker
├── Elenya/              (19 files)   - Elenya, Spiritual Leader (Acts 1-8)
├── Elka/                (empty)      - Elka, Ruins Cartographer
├── Helia/               (empty)      - Helia, Triage Chemist & Distiller
├── Inodora/             (empty)      - Inodora, Storyteller & Folk Chronicler
├── Juria_Korinth/       (empty)      - Juria & Korinth, Coastal Traders (joint)
├── Kaelen/              (1 file)     - Kaelen, Petty Thief / Swamp Guide
├── Kiv/                 (empty)      - Kiv, Stonemason & Monument Carver
├── Korrin/              (empty)      - Korrin, Information Broker
├── Lark/                (empty)      - Lark, Canopy Scout & Overgrowth Tracker
├── Lioren/              (empty)      - Lioren, Player Character (inner dialogue/narration)
├── Lira/                (empty)      - Lira, Skiff Builder
├── Malrik/              (1 file)     - Malrik, Lighthouse Keeper (story gates)
├── Malrik_Elenya/       (2 files)    - Shared Malrik & Elenya scenes (lighthouse pt1 & pt2)
├── Nima/                (2 files)    - Nima, Young Woman (encounter)
├── Ravi/                (1 file)     - Ravi (encounter)
├── Ravi_Nima/           (1 file)     - Shared Ravi & Nima scene (market discovery)
├── Saori/               (1 file)     - Saori (encounter)
├── Search/              (1 file)     - Search/remembrance narrative
├── Seyla/               (empty)      - Seyla, Field Technician
├── Sybil/               (empty)      - Sybil, Forest Loner
├── Tala/                (3 files)    - Tala, Market Cook
├── Tessa/               (empty)      - Tessa, Desert Survivor
├── Thalma/              (empty)      - Thalma, Handyperson
├── Thoran/              (empty)      - Thoran, Apparatus Tinker & Salvage Smith (Mask-Maker)
├── Tovren/              (empty)      - Tovren, Mechanic
├── Veynar/              (empty)      - Veynar, Unofficial Perimeter Guard
└── Willy/               (2 files)    - Willy (encounter)
```

**Total: 32 dialogue files across 29 NPC folders**

### NPC Key

| Folder | NPC Name | Role | Glyph Theme |
|--------|----------|------|-------------|
| Cal | Cal | Mediator | Sovereignty/Collapse |
| Drossel | Drossel | Black-Market Salvage Broker | Antagonist (Sovereignty/Collapse/Presence) |
| Elenya | Elenya | Spiritual Leader | Multiple (Trust/Joy/Presence) |
| Elka | Elka | Ruins Cartographer | Presence/Legacy/Ache |
| Helia | Helia | Triage Chemist & Distiller | Presence |
| Inodora | Inodora | Storyteller & Folk Chronicler | Legacy/Presence |
| Juria_Korinth | Juria & Korinth | Coastal Traders | Joy |
| Kaelen | Kaelen | Petty Thief / Swamp Guide | Presence/Sovereignty/Collapse/Trust |
| Kiv | Kiv | Stonemason & Monument Carver | Ache |
| Korrin | Korrin | Information Broker | Presence/Trust/Collapse |
| Lark | Lark | Canopy Scout & Overgrowth Tracker | Legacy |
| Lioren | Lioren | Player Character | Optional inner dialogue |
| Lira | Lira | Skiff Builder | Joy |
| Malrik | Malrik | Lighthouse Keeper | Story arc |
| Nima | Nima | Young Woman | Encounter |
| Ravi | Ravi | (encounter) | Encounter |
| Saori | Saori | (encounter) | Encounter |
| Search | Search Character | Remembrance narrative | Narrative |
| Seyla | Seyla | Field Technician | Ache |
| Sybil | Sybil | Forest Loner | Joy |
| Tala | Tala | Market Cook | Story arc (Legacy) |
| Tessa | Tessa | Desert Survivor | Ache |
| Thalma | Thalma | Handyperson | Presence |
| Thoran | Thoran | Apparatus Tinker & Salvage Smith / Mask-Maker | Ache |
| Tovren | Tovren | Mechanic | Trust |
| Veynar | Veynar | Unofficial Perimeter Guard | Sovereignty/Collapse/Trust |
| Willy | Willy | (encounter) | Encounter |

## Naming Convention

Files follow the existing pattern with their NPC prefix:
- **Single NPC dialogues:** `npc_name_encounter_##.json` or `npc_name_act#_seg#_description.json`
- **Multi-NPC dialogues:** Stored in a folder named after both NPCs (e.g., `Ravi_Nima/`)

## Loading Dialogue Files in Code

When referencing dialogue files in your dialogue manager or scene loader, use the **subfolder path** in the resource load:

### Example Resource Paths

```csharp
// Single NPC dialogue
DialogueManager.LoadDialogue("Dialogue/Elenya/elenya_act1_seg0_intro");
DialogueManager.LoadDialogue("Dialogue/Tala/tala_barbed_kinship_01");

// Multi-NPC dialogue
DialogueManager.LoadDialogue("Dialogue/Malrik_Elenya/malrik_elenya_lighthouse_pt1");
DialogueManager.LoadDialogue("Dialogue/Ravi_Nima/ravi_nima_market_discovery");

// Willy's payment dialogue
DialogueManager.LoadDialogue("Dialogue/Willy/willy_concourse_ruins_payment");
```

### Unity `Resources.Load()` Compatibility

Unity's `Resources.Load()` works seamlessly with subfolders:

```csharp
TextAsset dialogueJson = Resources.Load<TextAsset>(
    "Dialogue/Elenya/elenya_act1_seg0_intro"
);
// No file extension (.json) needed in the path
```

## Adding New Dialogue Files

When creating new dialogue for an NPC:

1. **Check if their folder exists** — if not, create it
2. **Place the file in the appropriate folder**
3. **Update any dialogue manager logic** to reference the new path
4. **Test resource loading** to confirm the path works

### Example: Adding Elenya Act 9

```
Dialogue/Elenya/elenya_act9_seg1_<description>.json
Dialogue/Elenya/elenya_act9_seg2_<description>.json
```

Resource paths:
```csharp
"Dialogue/Elenya/elenya_act9_seg1_<description>"
```

## Multi-NPC Dialogue Guidelines

For conversations between multiple NPCs:

- **Two NPCs:** Use `NPC1_NPC2/` naming (alphabetically or by prominence)
- **Example:** `Ravi_Nima/` for Ravi & Nima shared dialogues

Consider the dominant relationship or chronological arc to pick folder placement:

| Dialogue | Folder | Reason |
|----------|--------|--------|
| `malrik_elenya_lighthouse_pt1.json` | `Malrik_Elenya/` | Shared intimate moment |
| `ravi_nima_market_discovery.json` | `Ravi_Nima/` | Dual-NPC scene |

## Why This Structure?

✅ **Scalability** — As you add 5+ acts per character, each NPC folder stays organized  
✅ **Discoverability** — Dialogue writers can quickly find all scenes for a character  
✅ **Git-friendly** — Easier to review changes by NPC arc  
✅ **Resource paths are clear** — No ambiguity about which file belongs where  
✅ **Unity-compatible** — `Resources.Load()` and scene loaders handle subfolders automatically  

## Maintenance

When adding significant dialogue content:

1. Check the character's folder for existing files
2. Follow the naming convention (`act#_seg#_description`)
3. Keep segment descriptions lowercase and hyphen-separated
4. Add an entry to your dialogue tracking sheet (if you maintain one)

This organization supports Velinor's narrative ambition without requiring a database refactor.
