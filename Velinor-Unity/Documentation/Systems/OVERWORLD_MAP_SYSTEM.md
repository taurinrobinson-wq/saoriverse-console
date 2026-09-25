# Velinor Overworld Map System - Implementation Guide

## Overview

This system transforms the Velhara overworld map into an interactive fast-travel UI element. The implementation consists of:

1. **Labeled Map Image** - Programmatically generated with region names
2. **Configuration Files** - Fast-travel routes and UI parameters
3. **C# UI System** - Unity integration for player interaction

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    OVERWORLD MAP SYSTEM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  label_overworld_map.py                                        │
│  └── Generates: OverworldMap_Labeled.png                       │
│      • Adds region names with serif font                       │
│      • Dark brown text on cream outline                        │
│      • Centered positioning for each region                    │
│                                                                 │
│  generate_fast_travel_config.py                                │
│  ├── Generates: fast_travel_config.json                        │
│  │   • 8 regions with full descriptions                        │
│  │   • Travel routes and times between regions                 │
│  │   • NPCs and cultural descriptions                          │
│  │                                                              │
│  └── Generates: overworld_map_ui_prefab.json                   │
│      • UI button positions and sizes                           │
│      • Hover/click interactions                                │
│      • Color schemes for different states                      │
│                                                                 │
│  OverworldMapUI.cs                                             │
│  ├── Main UI controller                                        │
│  ├── Region button management                                  │
│  ├── Fast-travel logic and transitions                         │
│  └── Map open/close functionality                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## File Locations

```
Velinor-Unity/
├── Assets/
│   ├── Resources/
│   │   ├── DesignDocs/
│   │   │   ├── OverworldMap.png (original clean line art)
│   │   │   └── OverworldMap_Labeled.png (generated with labels)
│   │   │
│   │   └── Config/
│   │       ├── fast_travel_config.json
│   │       └── overworld_map_ui_prefab.json
│   │
│   └── Scripts/
│       └── UI/
│           └── OverworldMapUI.cs
│
├── label_overworld_map.py
└── generate_fast_travel_config.py
```

## Regions Defined

### 1. **Archive District** (East)
- **Map Position**: 1100, 180
- **Climate**: Dry, dusty winds sweep through broken architecture
- **Culture**: Knowledge keepers preserving fragments of the old world
- **Primary NPC**: Archivist Malrik
- **Description**: Ruins of past Velhara - towering structures crumble with age

### 2. **Shrine Ridge** (North)
- **Map Position**: 550, 120
- **Climate**: Cool, thin air - whispers carry far
- **Culture**: Spiritual seekers and memory guardians
- **Primary NPC**: High Seer Elenya
- **Description**: Ancient temples cling to northern cliffs - sacred and haunted

### 3. **Market Basin** (Central Hub)
- **Map Position**: 480, 380
- **Climate**: Variable, sheltered by surrounding structures
- **Culture**: Pragmatic merchants and organized community
- **Primary NPC**: Ravi & Nima
- **Description**: The living heart of Velhara - bustling with survivors and traders

### 4. **Desert & Mountain Expanse** (West)
- **Map Position**: 280, 380
- **Climate**: Scorching heat by day, frigid nights
- **Culture**: Nomadic scavengers and solitary travelers
- **Primary NPC**: Saori (starting location)
- **Description**: Vast emptiness where the player begins - sandy dunes meet rocky peaks

### 5. **Harbor Air Lowlands** (Southeast)
- **Map Position**: 1050, 500
- **Climate**: Humid, salt-laden breezes - oppressive heat
- **Culture**: Fishers and maritime traders
- **Primary NPC**: Captain Dalen
- **Description**: Flooded coastal areas with makeshift watercraft

### 6. **Swamid Swamps & Lowlands** (South)
- **Map Position**: 650, 600
- **Climate**: Damp, murky - mist clings to everything
- **Culture**: Herbalists and hidden communities
- **Primary NPC**: Keeper
- **Description**: Wetlands thick with vegetation and strange sounds

### 7. **Buried Tomb Archives** (Southwest)
- **Map Position**: 200, 550
- **Climate**: Cool, stable - untouched by surface weather
- **Culture**: Archaeologists and tomb keepers
- **Primary NPC**: Tovren
- **Description**: Underground chambers holding secrets of the before-time

### 8. **Concourse Ruins** (East-Central)
- **Map Position**: 950, 320
- **Climate**: Variable with wind patterns from multiple directions
- **Culture**: Crossroads merchants and opportunity seekers
- **Primary NPC**: Kaelen
- **Description**: Central hub where multiple paths converge

## Game Design Integration

### Player Journey

1. **Start**: Desert & Mountain Expanse (west)
   - Player encounters Saori
   - Receives Glyph Codex device
   - Enters Market Basin

2. **First Hub**: Market Basin
   - Meet Ravi and Nima
   - Codex activates, leads to first glyph
   - Base camp for exploration

3. **Exploration**: All other regions
   - Each region has distinct visual style
   - Different NPCs with unique cultures
   - Glyphs scattered across world

4. **Fast-Travel**: Once Codex is activated
   - Players can reference map to see positions
   - Travel between discovered regions
   - Saves time on repeat visits

### 2.5D Implementation Notes

For your fixed-camera 2.5D style:

- **Background Depth**: Archive District visible from Market Basin (distant ruins)
- **Scaling**: Objects in foreground larger, distant regions scaled smaller
- **Lighting**: Each region has unique lighting mood:
  - Archive: Cool, blue-gray light through dust
  - Shrine Ridge: Golden hour, mystical glow
  - Market Basin: Varied, natural light patterns
  - Desert: Harsh, high-contrast shadows
  - Harbor: Refracted water light, cool blues
  - Swamp: Bioluminescent greens, murky shadows

## Using the System

### Step 1: Generate Labeled Map

```bash
cd Velinor-Unity
python label_overworld_map.py
```

**Output**: `Assets/Resources/DesignDocs/OverworldMap_Labeled.png`

### Step 2: Generate Configuration Files

```bash
python generate_fast_travel_config.py
```

**Outputs**:
- `Assets/Resources/Config/fast_travel_config.json`
- `Assets/Resources/Config/overworld_map_ui_prefab.json`

### Step 3: Setup in Unity

1. **Create Canvas**:
   - New UI Canvas (Screen Space - Overlay)
   - Name: "OverworldMapCanvas"

2. **Add OverworldMapUI Script**:
   - Create empty GameObject: "OverworldMapUI"
   - Add `OverworldMapUI.cs` script component
   - Drag labeled map image to `mapImage` field

3. **Create Map Container**:
   - Add Image component to hold the map
   - Set source to OverworldMap_Labeled sprite
   - Size: 800x800 (or appropriate for your UI)

4. **Add Close Button**:
   - Create Button UI element
   - Assign to `closeButton` field in script

5. **Add Info Panels**:
   - Region Name (Text)
   - Region Description (Text)
   - Travel Time (Text)

### Step 4: Wire Up Input

```csharp
// In your input manager or UI controller
if (Input.GetKeyDown(KeyCode.M))
{
    mapUI.ToggleMap();
}
```

## Configuration File Format

### fast_travel_config.json

```json
{
  "version": "1.0",
  "system": "VelharaFastTravel",
  "map_dimensions": {
    "width": 4320,
    "height": 4320
  },
  "regions": [
    {
      "id": "archive_district",
      "name": "Archive District",
      "description": "Ruins of past Velhara...",
      "map_position": {"x": 1100, "y": 180},
      "atmosphere": {
        "climate": "Dry, dusty winds...",
        "culture": "Knowledge keepers..."
      },
      "npc": "Archivist Malrik",
      "discovered": false,
      "accessible": true
    }
  ],
  "travel_system": {
    "enabled": true,
    "routes": [
      {
        "from": "desert_expanse",
        "to": "market_basin",
        "time_minutes": 15,
        "distance": "Medium"
      }
    ]
  }
}
```

## Customization

### Changing Map Labels

Edit `REGIONS` in `label_overworld_map.py`:

```python
REGIONS = [
    ("REGION NAME", x_position, y_position, font_size, rotation),
    # ...
]
```

### Adjusting Travel Times

Edit `TRAVEL_ROUTES` in `generate_fast_travel_config.py`:

```python
TRAVEL_ROUTES = [
    {"from": "region1", "to": "region2", "time_minutes": 20, "distance": "Far"},
    # ...
]
```

### Changing UI Colors

In `OverworldMapUI.cs`, modify region button colors:

```csharp
image.color = new Color(0.54f, 0.45f, 0.33f, 0.5f); // Brown
```

## Future Enhancements

- [ ] Load region data dynamically from JSON
- [ ] Animated transitions between regions
- [ ] Quest markers on map
- [ ] Discovered/undiscovered region states
- [ ] Minimap integration during gameplay
- [ ] Voice lines for region descriptions
- [ ] Photo mode anchors at each region
- [ ] Weather/seasonal changes per region

## Related Systems

- **Glyph System**: Glyphs are tied to regions, map helps players find them
- **NPC System**: Each region's primary NPC serves as a hub
- **Scene Management**: Fast-travel triggers scene transitions
- **Inventory System**: Codex device ties to map functionality
- **Save System**: Remember discovered regions

## Performance Notes

- Map image: 4320x4320 (high resolution for detail)
- Consider LOD for mobile platforms
- Pre-load map on game start or demand
- Cache region button positions
- Use object pooling for region buttons if needed

---

**Last Updated**: 2026-07-14  
**System Version**: 1.0  
**Status**: Ready for Integration
