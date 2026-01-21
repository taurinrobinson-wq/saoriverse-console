# Title Screen Component - 4-Layer Architecture

## Overview

Implemented a professional title screen for Velinor with a sophisticated 4-layer composition system. The screen uses actual game art to create an immersive first impression while maintaining performance through optimized asset loading.

## 4-Layer Architecture

### Layer 1: Background (Z-Index: 1)
**File:** `Velhara_background_title(blur).png`
- Full-screen environment backdrop
- Subtle blur effect for depth
- Contains the ruins of Velhara environment
- Establishes the game world visual identity

**CSS:**
```
position: absolute; top: 0; left: 0; right: 0; bottom: 0;
width: 100%; height: 100%;
objectFit: cover;
filter: blur(2px);
```

### Layer 2: Character Overlay - Velinor (Z-Index: 2)
**File:** `velinor_eyesclosed2.png`
- The main character, Velinor, with eyes closed
- Positioned center-screen
- Scales responsively to viewport
- Opacity set to 0.95 for subtle transparency
- Represents the player's connection to the protagonist

**CSS:**
```
position: absolute; top: 50%; left: 50%;
transform: translate(-50%, -50%);
width: 100%; height: 100%;
maxWidth: 1200px; maxHeight: 800px;
objectFit: contain;
opacity: 0.95;
```

### Layer 3: Title Overlay (Z-Index: 3)
**File:** `velinor_title_transparent2.png`
- Transparent title graphic with game logo/name
- Positioned as full-screen overlay
- Contains decorative elements and branding
- Non-interactive (pointer-events: none)
- Adds visual polish and game branding

**CSS:**
```
position: absolute; top: 0; left: 0; right: 0; bottom: 0;
width: 100%; height: 100%;
objectFit: contain;
pointerEvents: none;
```

### Layer 4: Interactive Button - "Play New Game" (Z-Index: 10)
**File:** Generated dynamically with CSS/gradient
- Floating action button
- Positioned 120px from bottom
- Gradient background: `#2e3f2f` to `#1a2219` (earthy greens)
- Golden border: `#a88f5c` with 2px width
- Matches the Velhara color palette
- Advanced hover/press states with animations

**Color Palette (from game assets):**
- Primary: `#2e3f2f` (dark sage green)
- Secondary: `#1a2219` (deep forest)
- Accent: `#a88f5c` (aged gold)
- Text: `#e6d8b4` (cream/parchment)

**Button States:**

1. **Default:**
   - Background: Linear gradient (dark sage to forest)
   - Border: 2px solid aged gold
   - Shadow: Subtle glow (0 4px 12px)
   - Transform: Base position

2. **Hover:**
   - Background: Lighter gradient
   - Shadow: Enhanced glow
   - Transform: translateY(-3px) - lifts button
   - Cursor: pointer

3. **Active/Press:**
   - Background: Darker gradient
   - Shadow: Reduced glow
   - Transform: No lift (pressed state)

4. **Focus:**
   - Maintains hover state for accessibility

**Typography:**
- Font: Georgia, serif (matches game narrative style)
- Size: 1.1rem
- Weight: bold
- Letter-spacing: 1px (elevated typography)
- Text-transform: uppercase
- Text-shadow: 2px 4px rgba(0,0,0,0.8) (depth)

## Player Name Input Modal

### Structure
- Backdrop: Semi-transparent dark overlay with blur
- Modal: Gradient semi-transparent container
- Border: Gold accent matching button
- Animation: Slide-up transition on appearance

### Features
- Character limit: 30 characters
- Real-time validation
- Enter key support for quick submission
- Cancel button for dismissing
- Error message display
- Loading state management
- Character counter display

### Styling
- Background: Gradient dark with transparency
- Border: Gold matching button palette
- Text: Cream on dark (high contrast)
- Input: Dark semi-transparent background
- Buttons: Confirm (green) and Cancel (red)

## Component API

### Props
```typescript
interface TitleScreenProps {
  onGameStart?: (playerName: string) => void;
}
```

### Usage
```tsx
import TitleScreen from '@/components/TitleScreen';

export default function Home() {
  const handleGameStart = (playerName: string) => {
    router.push(`/game/velhara_market?player=${encodeURIComponent(playerName)}`);
  };

  return <TitleScreen onGameStart={handleGameStart} />;
}
```

## Asset Structure

All game assets are stored in the web's public folder for Next.js serving:

```
velinor-web/public/assets/
├── backgrounds/
│   ├── Velhara_background_title(blur).png      (Layer 1)
│   ├── Velhara_background_title.png            (Alternative)
│   └── velinor_title_eyes_closed.png           (Fallback)
├── npcs/
│   ├── velinor_eyesclosed2.png                 (Layer 2 - Primary)
│   ├── velinor_eyesclosed.png                  (Alternative)
│   └── velinor_eyesopen.png                    (Alternate state)
└── overlays/
    ├── velinor_title_transparent2.png          (Layer 3)
    └── velinor_title_transparent.png           (Fallback)
```

### Asset Syncing
Run sync script to update assets after modifying images in `velinor/`:

**PowerShell:**
```powershell
cd velinor-web
powershell -ExecutionPolicy Bypass -File sync-assets.ps1
```

**Bash:**
```bash
cd velinor-web
bash sync-assets.sh
```

## Color Palette Reference

| Color | Hex | Usage | RGB |
|-------|-----|-------|-----|
| Dark Sage | `#2e3f2f` | Button base | (46, 63, 47) |
| Deep Forest | `#1a2219` | Button pressed | (26, 34, 25) |
| Aged Gold | `#a88f5c` | Borders, accents | (168, 143, 92) |
| Cream | `#e6d8b4` | Text, highlights | (230, 216, 180) |
| Light Sage | `#3b4f3b` | Button hover | (59, 79, 59) |

## Responsive Design

- Full viewport coverage (100vw × 100vh)
- Fluid scaling for backgrounds and characters
- Maximum width constraints (1200px) for character layer
- Mobile-friendly modal positioning
- Touch-friendly button sizing (min 44px tap target)

## Performance Optimizations

1. **CSS-in-JS:** Inline styles with TypeScript types
2. **Lazy loading:** Images load naturally with native browser optimization
3. **No animations during load:** Animations only on user interaction
4. **Backdrop filter:** Hardware-accelerated blur
5. **Event delegation:** Efficient event handling for modal

## Accessibility Features

- Semantic HTML structure
- Keyboard support (Enter key to confirm)
- Focus states for all interactive elements
- High contrast text on backgrounds (WCAG AA compliant)
- ARIA-compliant modal with backdrop dismissal
- Disabled button state during loading

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Requires CSS Grid, Flexbox, and CSS Filters support

## Development Notes

### File Locations
- Component: `velinor-web/src/components/TitleScreen.tsx`
- Page: `velinor-web/src/app/page.tsx`
- Assets: `velinor-web/public/assets/{backgrounds,npcs,overlays}`
- Sync scripts: `velinor-web/sync-assets.{ps1,sh}`

### Future Enhancements

1. **Audio:** Add ambient music and button sound effects
2. **Transitions:** Screen transition animations when starting game
3. **Settings:** Add volume/graphics options button
4. **Language:** Multi-language support for UI text
5. **Achievements:** Display unlocked achievements on title screen
6. **Save Game:** Resume from save file option
7. **Credits:** In-game credits overlay
8. **Animations:** Subtle breathing animation for Velinor character

## Testing

Test in development:
```bash
cd velinor-web
npm run dev
# Visit http://localhost:3000
```

Verify all 4 layers render correctly:
1. ✓ Background (blur visible)
2. ✓ Character (centered, semi-transparent)
3. ✓ Title overlay (branding visible)
4. ✓ Button (interactive, animated)

Test interactions:
- ✓ Button hover animation
- ✓ Button click opens modal
- ✓ Enter key submits name
- ✓ Cancel button closes modal
- ✓ Name validation

## Git History

**Latest commits:**
- `TitleScreen.tsx` component created with 4-layer architecture
- `page.tsx` refactored to use TitleScreen component
- Asset sync scripts created for easy maintenance
- Game assets copied to web public folder

---

**Status:** ✅ Production Ready

The title screen is fully functional with professional aesthetics matching the Velinor game world. All assets are properly layered, the button palette matches the game's color scheme, and the modal provides smooth character name entry.
