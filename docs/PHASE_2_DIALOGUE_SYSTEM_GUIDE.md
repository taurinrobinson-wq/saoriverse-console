# Phase 2 Implementation Guide: Dialogue System Integration

## Overview

Phase 2 focuses on wiring the TONE stat system into actual dialogue choices. The core system is built; now we add the content that uses it.

## Implementation Checklist

### Step 1: Create Dialogue Data Structure

**File to create**: `velinor-web/src/lib/dialogueData.ts`

```typescript
// Example structure for dialogue options
interface DialogueChoice {
  id: string;
  text: string;
  toneChanges: Array<{
    stat: keyof ToneStats;
    delta: number;
    description: string;
  }>;
  requiresStats?: Record<keyof ToneStats, number>; // Gating requirements
  unlocksContent?: {
    glyph?: string;
    scene?: string;
  };
  nextDialogueId: string;
}

interface DialogueNode {
  id: string;
  npc: string;
  narration: string;
  backgroundImage: string;
  overlayImage?: string;
  choices: DialogueChoice[];
  conditions?: {
    requiresStats?: Record<string, number>;
    requiresGlyph?: string;
    requiresVisit?: string;
  };
}

// Dialogue database keyed by scene ID
export const dialogueDatabase: Record<string, DialogueNode> = {
  'ravi_first_meeting': {
    id: 'ravi_first_meeting',
    npc: 'Ravi',
    narration: 'A quiet scholar sits in the corner of the marketplace...',
    backgroundImage: '/assets/backgrounds/city_market.png',
    choices: [
      {
        id: 'ravi_listen',
        text: 'Listen carefully to her story',
        toneChanges: [
          { stat: 'empathy', delta: 5, description: 'Showed emotional understanding' },
          { stat: 'observation', delta: 3, description: 'Noticed subtle details' }
        ],
        nextDialogueId: 'ravi_story_deepens'
      },
      {
        id: 'ravi_question',
        text: 'Ask pointed questions',
        toneChanges: [
          { stat: 'observation', delta: 8, description: 'Keen insight' },
          { stat: 'trust', delta: -2, description: 'Seemed interrogative' }
        ],
        nextDialogueId: 'ravi_guarded'
      }
    ]
  },
  // More dialogue nodes...
```sql
```



### Step 2: Update GameScene Component

**File to modify**: `velinor-web/src/components/GameScene.tsx`

Add support for tracking which choice was made:

```typescript
interface GameSceneProps {
  // ... existing props
  onChoiceClick: (choiceId: string, choiceIndex: number) => void;
```text
```



### Step 3: Create Dialogue Handler Hook

**File to create**: `velinor-web/src/lib/useDialogue.ts`

```typescript
import { useGameStore } from './gameStore';
import { dialogueDatabase } from './dialogueData';

export function useDialogue() {
  const { toneStats, updateToneStats, setScene, unlockGlyph } = useGameStore();

  const handleDialogueChoice = (dialogueId: string, choiceIndex: number) => {
    const dialogue = dialogueDatabase[dialogueId];
    if (!dialogue) return;

    const choice = dialogue.choices[choiceIndex];
    if (!choice) return;

    // Check if player can select this choice
    if (choice.requiresStats) {
      const canSelect = Object.entries(choice.requiresStats).every(
        ([stat, required]) => toneStats[stat as keyof typeof toneStats] >= required
      );
      if (!canSelect) return; // Grey out or block this choice
    }

    // Apply TONE stat changes
    choice.toneChanges.forEach(action => {
      updateToneStats(action);
    });

    // Unlock content if applicable
    if (choice.unlocksContent?.glyph) {
      unlockGlyph(choice.unlocksContent.glyph);
    }

    // Move to next dialogue
    const nextDialogue = dialogueDatabase[choice.nextDialogueId];
    if (nextDialogue) {
      setScene(
        nextDialogue.id,
        nextDialogue.backgroundImage,
        nextDialogue.overlayImage
      );
    }
  };

  return { handleDialogueChoice, dialogueDatabase };
```text
```



### Step 4: Create Main Dialogue Component

**File to create**: `velinor-web/src/components/DialogueRenderer.tsx`

```typescript
import { useGameStore } from '@/lib/gameStore';
import { useDialogue } from '@/lib/useDialogue';
import GameScene from './GameScene';

export default function DialogueRenderer() {
  const { currentScene, currentBackground, currentOverlay, toneStats } = useGameStore();
  const { handleDialogueChoice, dialogueDatabase } = useDialogue();

  const dialogue = dialogueDatabase[currentScene];
  if (!dialogue) return <div>Scene not found</div>;

  // Filter choices based on TONE requirements
  const availableChoices = dialogue.choices.filter(choice => {
    if (!choice.requiresStats) return true;
    return Object.entries(choice.requiresStats).every(
      ([stat, required]) => toneStats[stat as keyof typeof toneStats] >= required
    );
  });

  return (
    <GameScene
      backgroundImage={currentBackground}
      overlay={currentOverlay}
      narration={dialogue.narration}
      npcName={dialogue.npc}
      choices={availableChoices.map(c => ({ text: c.text, id: c.id }))}
      onChoiceClick={(choiceIndex) => {
        const choice = availableChoices[choiceIndex];
        handleDialogueChoice(dialogue.id, dialogue.choices.indexOf(choice));
      }}
    />
  );
```sql
```



### Step 5: Update Main Game Page

**File to modify**: `velinor-web/src/app/game/[sessionId]/page.tsx`

Replace the hardcoded GameScene with DialogueRenderer:

```typescript
// Old:
<GameScene
  backgroundImage={gameState.background_image || '/assets/backgrounds/velhara_market.png'}
  narration={gameState.main_dialogue}
  npcName={gameState.npc_name || gameState.passage_name}
  choices={gameState.choices.map(c => ({ text: c.text, id: c.index.toString() }))}
  onChoiceClick={handleChoiceClick}
/>

// New:
```text
```



### Step 6: Add NPC Personality System

**File to create**: `velinor-web/src/lib/npcData.ts`

```typescript
interface NPC {
  id: string;
  name: string;
  role: string;
  description: string;
  initialTrustModifier?: number;
  toneAffinity?: {
    stat: keyof ToneStats;
    favorValue?: number; // How much they like this stat
  }[];
}

export const NPCDatabase: Record<string, NPC> = {
  ravi: {
    id: 'ravi',
    name: 'Ravi',
    role: 'Scholar',
    description: 'A thoughtful scholar who guards her vulnerabilities',
    toneAffinity: [
      { stat: 'empathy', favorValue: 2 },
      { stat: 'observation', favorValue: 1 }
    ]
  },
  // ... more NPCs
```text
```



## Content Creation Tasks

### Task 1: Write All Dialogue Trees

Create dialogue nodes for each NPC first encounter and key scenes. For reference, see:

- [NPC Sphere System](./velinor/markdowngameinstructions/NPC_SPHERE_SYSTEM.md)
- [Marketplace Roster](./velinor/markdowngameinstructions/MARKETPLACE_NPC_ROSTER.md)
- [Final Arc](./velinor/markdowngameinstructions/VELINOR_SAORI_FINAL_ARC.md)

### Task 2: Map Dialogue to TONE Consequences

For each choice, determine:

- How does this choice reflect the player's emotional intelligence?
- Which TONE stats change?
- By how much? (±1 to ±10)
- What description explains the change?

### Task 3: Implement Branching Logic

Decisions that unlock based on:

- **High Trust** (≥70): Vulnerable confessions
- **High Observation** (≥75): Notice subtle clues
- **High Narrative Presence** (≥70): Influence events
- **High Empathy** (≥80): Unlock emotional paths

### Task 4: Wire Glyphs to Dialogue

Each glyph should unlock from a meaningful dialogue moment:

- **glyph_joy**: Genuine connection moment
- **glyph_longing**: Understanding someone's deepest wish
- **glyph_chain**: Seeing how people are connected
- **glyph_hidden_truth**: Learning a profound secret

## Quick Implementation Order

**Days 1-2**: Create dialogue database for first 3 NPCs

1. Ravi (Scholar) - Trust/Empathy focused
2. Kaelen (Mystic) - Observation/Narrative Presence focused
3. Sera (Healer) - Empathy/Connection focused

**Days 2-3**: Implement dialogue system

1. Create useDialogue hook
2. Create DialogueRenderer component
3. Wire into game page
4. Test with NPC #1

**Days 3-4**: Complete remaining NPCs

1. Nima (Merchant) - Trust/Narrative Presence
2. Dalen (Warrior) - Observation/Trust
3. Mariel (Mystic Guide) - Narrative Presence/Empathy
4. Korrin (Wanderer) - Observation/Empathy
5. Tovren (Elder) - All stats balanced

**Day 4-5**: Saori & Velinor final scenes

- Final dialogue tree
- All 6 ending paths
- Closing scenes

## Code Structure After Phase 2

```
velinor-web/src/
├── lib/
│   ├── toneSystem.ts          (Existing)
│   ├── gameStore.ts           (Existing)
│   ├── dialogueData.ts        (NEW - Dialogue nodes)
│   ├── npcData.ts             (NEW - NPC definitions)
│   ├── useDialogue.ts         (NEW - Dialogue hook)
│   └── toneSystemDemo.ts      (Existing)
├── components/
│   ├── GameScene.tsx          (Updated - accept choiceId)
│   ├── DialogueRenderer.tsx   (NEW - Main dialogue handler)
│   └── ToneStatsDisplay.tsx   (Existing)
└── app/
    └── game/[sessionId]/
        └── page.tsx           (Updated - use DialogueRenderer)
```



## Success Criteria

✅ All 8 NPCs have first meeting dialogue
✅ All dialogue choices apply TONE stat changes
✅ TONE stat changes visible in dev console
✅ Dialogue options gate properly based on TONE stats
✅ All 4 glyphs unlock from meaningful moments
✅ Final arc is reachable with proper TONE stats
✅ All 6 endings are accessible via different TONE paths
✅ No hardcoded paths - all driven by TONE stats

## Current Status

- ✅ TONE System Core: Complete
- ✅ State Management: Complete
- ✅ Dev Console: Complete
- ⏳ Dialogue System: Ready to implement
- ⏳ NPC Dialogue Trees: In progress
- ⏳ Content Integration: Pending
- ⏳ Testing & Polish: Pending

**Next commit** will include Phase 2 - Dialogue System Integration
