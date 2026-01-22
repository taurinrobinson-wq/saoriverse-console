# Velinor Glyph Animation Specifications

## Overview
Pre-baked animations for glyph discoveries using Stable Diffusion-generated frames composited with WebGL particle effects.

---

## Animation 1: Glyph of Sparks Lost — Sand Emergence

### Visual Narrative
A broken lantern with incomplete halo emerges from sand. As it rises, sand particles cascade downward with realistic gravity. The glyph glows softly—not triumphant, but discovered. The lantern symbol is faint, as if surfacing from deep memory.

### Technical Specs

**Frame Generation** (Stable Diffusion/Automatic1111):
- **Total frames**: 60 frames at 24fps = 2.5 seconds
- **Resolution**: 1920x1080 (will composite into scene at variable scale)
- **Format**: PNG with alpha channel (transparency)
- **Aspect ratio**: 16:9 (match viewport)

**Prompt Structure** (for Stable Diffusion):
Base prompt should emphasize:
- Broken/incomplete lantern symbol
- Sand texture, realistic particle behavior
- Faint glow (warm amber/gold)
- Upward motion/emergence
- Minimalist aesthetic (consistent with Velinor's visual language)
- Depth of field (foreground clear, background soft)

**Frame Breakdown**:
1. **Frames 0-15** (0.0-0.625s): Lantern barely visible beneath sand, sand beginning to move upward
2. **Frames 16-35** (0.625s-1.458s): Lantern emerges, sand cascades more heavily
3. **Frames 36-50** (1.458s-2.083s): Lantern fully visible, sand settling, glow intensifies slightly
4. **Frames 51-60** (2.083s-2.5s): Final settle, glyph appears in steady state

**Visual Elements**:
- Lantern symbol: Small, centered, appears to be carved/etched
- Incomplete halo: Crescent/arc shape around upper edge
- Sand: Realistic particle flow (not perfectly smooth)
- Color palette: Warm earth tones (browns, golds, ochres)
- Lighting: Single warm light source, creates shadow beneath lantern

### WebGL Implementation

**Particle Effects Layer** (Three.js):
- Sand grain particles (500-1000 particles)
- Physics simulation: gravity, wind resistance, collision with ground
- Particle lifespan: fade out as they settle
- Emission point: above the lantern, throughout emergence sequence
- Particle size: 1-3mm (screen-relative)

**Composition**:
1. Stable Diffusion frames play as sprite animation (backbone)
2. Particle effects render on top in real-time
3. Glyph symbol overlay: Static vector glyph (can be SVG or texture) that phases in during frames 40-45

**Code Structure**:
```javascript
// Pseudo-structure for animation sequencing
class GlyphEmergenceAnimation {
  constructor(scene, audioContext) {
    this.frames = loadSequence('assets/glyphs/sparks-lost-emergence/frame-*.png');
    this.particleSystem = new SandParticleSystem(scene, {
      emissionCount: 800,
      lifetime: 2.5,
      gravity: -9.8
    });
    this.audioContext = audioContext;
  }
  
  play(onComplete) {
    // 1. Start sprite animation (frames)
    this.playFrameSequence(this.frames, 24);
    
    // 2. Start particle system
    this.particleSystem.emit(duration: 2.5);
    
    // 3. Fade in glyph symbol at frame 40
    this.glyphSymbol.fadeIn(startFrame: 40, duration: 500);
    
    // 4. Optional audio: subtle whoosh, settling sand
    this.playAudio('sfx/glyph-emergence-wind.mp3', volume: 0.3);
    this.playAudio('sfx/sand-settling.mp3', volume: 0.2, delay: 1.5);
    
    // 5. Call completion callback
    setTimeout(onComplete, 2500);
  }
}
```

**Asset Organization**:
```
assets/
  glyphs/
    sparks-lost-emergence/
      frames/
        frame-000.png
        frame-001.png
        ...
        frame-059.png
      metadata.json (frame timing, dimensions, etc.)
      glyph-symbol.svg
      sfx/
        emergence-wind.mp3
        sand-settling.mp3
```

### Metadata File Format

**`metadata.json`**:
```json
{
  "animation": "sparks-lost-emergence",
  "glyph": "Glyph of Sparks Lost",
  "frameCount": 60,
  "fps": 24,
  "totalDuration": 2.5,
  "frameSize": {
    "width": 1920,
    "height": 1080
  },
  "particles": {
    "type": "sand",
    "emissionStart": 0,
    "emissionEnd": 1.5,
    "particleCount": 800,
    "gravity": -9.8,
    "windForce": 0.1
  },
  "glyphSymbol": {
    "type": "svg",
    "file": "glyph-symbol.svg",
    "fadeInStart": 1.667,
    "fadeInDuration": 0.5
  },
  "audio": [
    {
      "type": "sfx",
      "file": "emergence-wind.mp3",
      "volume": 0.3,
      "delay": 0,
      "fadeIn": 0.2
    },
    {
      "type": "sfx",
      "file": "sand-settling.mp3",
      "volume": 0.2,
      "delay": 1.5,
      "fadeIn": 0.3
    }
  ],
  "triggers": {
    "onFrameComplete": {
      "frame": 59,
      "action": "revealGlyph"
    }
  }
}
```

---

## Animation 2: Standard Glyph Discovery

### Visual Narrative
Glyph symbol appears centered on screen. Soft glow pulse. Optional sparkle/light particles. No gravity physics—this is meant to feel magical/instantaneous, not physical.

### Technical Specs

**Frame Generation** (Stable Diffusion):
- **Total frames**: 30 frames at 24fps = 1.25 seconds
- **Resolution**: 512x512 (will scale up in viewport)
- **Format**: PNG with alpha
- **Focus**: Glyph symbol only, centered, with aura/glow effect

**Particle Effects**:
- Light particles (100-200): float upward, fade out
- Glow pulse: radial gradient that expands from center
- No gravity physics
- Ambient sparkle

**Duration**: 1.25 seconds

---

## Animation 3: Glyph Console Emergence (Future)

### Visual Narrative
Console platform rises from sand. Panels slide into place. Sand cascades more dramatically than Sparks Lost. Mechanical/architectural feel (solid surfaces).

### Technical Specs

**Frame Generation**:
- **Total frames**: 90 frames at 30fps = 3.0 seconds
- **Resolution**: 1920x1080
- **Format**: PNG with alpha

**Particle Effects**:
- Heavier sand particles (1500+ particles)
- Stronger gravity
- Wind effects (sand blown sideways)
- Dust cloud effect

**Duration**: 3.0 seconds

---

## Implementation Pipeline

### Step 1: Generate Frames with Stable Diffusion

Using Automatic1111 WebUI:
1. Set up batch generation with negative prompts (avoid: "blurry", "low quality", "cartoon")
2. Use consistent seed for frame-to-frame coherence (or vary slightly for natural motion)
3. Generate full frame sequence
4. Export as PNG with transparency

### Step 2: Sequence Assembly

1. Verify frame count matches spec
2. Organize into directory structure
3. Generate metadata.json with timing/particle/audio specs
4. Test frame playback at correct FPS

### Step 3: WebGL Integration

1. Load frame sequence into Three.js
2. Create particle system with matching physics params
3. Wire audio triggers
4. Test full animation loop

### Step 4: UI/Game Integration

1. Trigger animation on glyph discovery
2. Pause game state during animation (or allow non-blocking overlay)
3. Add skip option (for accessibility)
4. Log glyph acquisition to player state

---

## Design Guidelines

**Color Palette**:
- Warm earth tones for sand/emergence animations
- Cool tones for magical discovery animations
- Consistent with existing Velinor visual language

**Pacing**:
- Emergence animations: 2-3 seconds (slow, contemplative)
- Discovery animations: 1-1.5 seconds (quick, satisfying)
- Avoid: Fast cuts, jarring transitions

**Accessibility**:
- All animations should be skippable
- Provide alternative text/description
- Audio should not be required for understanding
- Particle density should be adjustable (performance)

---

## Asset Checklist

- [ ] Glyph of Sparks Lost — 60 frames (1920x1080, 24fps)
- [ ] Sparks Lost glyph symbol (SVG)
- [ ] Emergence wind SFX (2-3 seconds, loopable)
- [ ] Sand settling SFX (3-4 seconds, fade-out)
- [ ] metadata.json with all timing/physics specs
- [ ] Test particle system implementation
- [ ] Test full animation in WebGL context
- [ ] Test audio sync with frame sequence
- [ ] Performance profile (GPU/CPU load)

---

## Future Expansions

This pipeline can be extended for:
- NPC discovery animations
- Environmental reveals
- Transition sequences
- Tutorial/onboarding animations
- Ending variations (different glyph discovery styles based on player choices)

Each animation follows same pattern: **Stable Diffusion frames + WebGL particle effects + audio triggers**.
