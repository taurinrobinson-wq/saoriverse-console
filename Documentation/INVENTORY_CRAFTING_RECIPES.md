# Inventory Crafting System

**Design Principle:** Keep the system compact with 18 reusable material categories, 3 permanent tools, and 9 single-use crafted items. Ordinary recipes use only two or three ingredient types, so the player can understand them at a glance.

---

## Materials

### Salvage Materials

Collected from derelict structures, machinery, and debris.

1. **Scrap Metal**
   - Brackets, housings, blades, braces, and structural pieces.

2. **Wire**
   - Electrical connections, bindings, and simple repairs.

3. **Polymer**
   - Handles, insulation, seals, and flexible components.

4. **Glass**
   - Lenses, protective covers, and optical pieces.

5. **Fabric**
   - Bandages, padding, straps, and filtration.

6. **Electronic Parts**
   - Circuit boards, switches, sensors, and controls.

7. **Power Cell**
   - Stored electrical energy for portable devices.

8. **Mechanical Parts**
   - Gears, bearings, hinges, springs, and actuators.

9. **Sealant**
   - Joining, waterproofing, patching, and insulation.

### Medicinal Materials

Taught by **Sera** through dialogue interactions.

1. **Medicinal Herbs**
   - General restorative plants used in salves.

2. **Antiseptic Herbs**
   - Plants used to clean and dress wounds.

3. **Soothing Herbs**
   - Plants used for burns, irritation, and inflammation.

4. **Plant Oil**
   - A base for ointments and burn treatments.

### Food Materials

Taught by **Tala** through dialogue interactions.

1. **Roots**
   - Edible roots and tubers.

2. **Greens**
   - Edible leaves and tender shoots.

3. **Vegetables**
   - General savory produce.

4. **Fruit**
   - Fresh or preserved edible fruit.

5. **Culinary Herbs**
   - Flavorful plants Tala knows how to identify and prepare.

---

## Permanent Tools

These remain available after construction and unlock contextual interactions throughout the game world.

### Portable Light

**Recipe:**
- Electronic Parts ×1
- Power Cell ×1
- Wire ×1

**Uses:** Illuminates dark service corridors, tunnels, sealed rooms, and machinery interiors.

### Pry Tool

**Recipe:**
- Scrap Metal ×2
- Mechanical Parts ×1
- Polymer ×1

**Uses:** Opens jammed doors, access panels, crates, floor grates, and maintenance hatches.

### Cutting Tool

**Recipe:**
- Scrap Metal ×2
- Polymer ×1

**Uses:** Cuts intrusive vegetation, tangled rope, fabric barriers, netting, and obstructing raft lines.

---

## Single-Use Utility Items

### Repair Kit

**Recipe:**
- Scrap Metal ×1
- Wire ×1
- Sealant ×1

**Uses:** Repairs one damaged mechanism, broken connection, leaking structure, or disabled piece of equipment.

---

## First-Aid Items

Taught by **Sera** through dialogue interactions. Each provides situational healing without creating a persistent hunger or health meter.

### Bandage

**Recipe:**
- Fabric ×1
- Antiseptic Herbs ×1

**Use:** Treats a minor wound or can be given to an injured character.

### Medicinal Salve

**Recipe:**
- Medicinal Herbs ×2
- Plant Oil ×1

**Use:** Restores Lioren after illness, strain, or lingering physical discomfort; may also be given to another character.

### Burn Cream

**Recipe:**
- Soothing Herbs ×2
- Plant Oil ×1

**Use:** Treats burns, heat exposure, and skin irritation.

### Splint

**Recipe:**
- Scrap Metal ×1
- Fabric ×2

**Use:** Stabilizes an injured limb or helps an injured character safely move.

---

## Food Items

Taught by **Tala** through dialogue interactions. Food provides modest situational restoration without creating a hunger meter.

### Mixed Greens

**Recipe:**
- Greens ×2
- Culinary Herbs ×1

**Use:** Provides light nourishment or can be given to another character.

### Fruit Salad

**Recipe:**
- Fruit ×2
- Culinary Herbs ×1

**Use:** Provides light nourishment and helps with fatigue.

### Vegetable Soup

**Recipe:**
- Vegetables ×2
- Roots ×1
- Culinary Herbs ×1

**Use:** Provides stronger nourishment and helps Lioren recover from exhaustion or illness.

### Root Stew

**Recipe:**
- Roots ×2
- Vegetables ×1
- Culinary Herbs ×1

**Use:** A substantial meal intended primarily for giving to someone who needs food or prolonged recovery.

---

## Crafting System Overview

### Tab Structure

- **Materials & Schematics Tab** (Default view)
  - Display available materials in a list
  - Show available schematics based on material availability
  - Display Assemble button when recipe requirements are met

- **Tools & Items Tab** (Secondary view)
  - Display crafted tools (permanent inventory items)
  - Display single-use items and consumables
  - Provide Equip/Use buttons for items

### Tab Switching

Tab buttons toggle visibility by controlling **CanvasGroup alpha**:
- **Alpha = 1:** Tab is fully visible and interactive
- **Alpha = 0:** Tab is hidden but remains in the scene

Both tabs remain enabled in the editor; visibility is controlled purely by alpha value and CanvasGroup blocking.

### Gameplay Flow

1. **Player opens inventory** (default: Materials & Schematics tab visible)
2. **Player selects materials** via single-click
3. **Valid combinations activate schematics** (Assemble button appears)
4. **Player clicks Assemble** to craft
5. **Materials decrease** by recipe amount
6. **Item appears in Tools & Items tab**
7. **Player switches tabs** to access crafted item
8. **Player clicks Equip (tools) or Use (consumables)**

---

## Implementation Notes

- **Material Categories:** Keep at 18 to maintain cognitive load balance
- **Recipe Complexity:** Limit to 2-3 ingredient types per recipe for clarity
- **Dialog Teaching:** Sera teaches medicinal/first-aid; Tala teaches food crafting
- **Item Distribution:** Salvage materials (9) + Medicinal (4) + Food (5) = 18 total
- **Tool Permanence:** Portable Light, Pry Tool, Cutting Tool remain after crafting
- **Consumables:** All food and first-aid items are single-use
