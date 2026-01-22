# Velinor Endgame Chamber Sequence

## Overview
The glyph insertion chamber finale: doors slide open to reveal a heavenly blue glowing void, then progressive reveal of the end image as player advances through the threshold.

---

## Sequence Flow

### Stage 1: Glyph Insertion (Player Action)
- Player places final glyph(s) into chamber slots
- Audio: Subtle resonance tone, slight vibration feedback
- Camera: Static, facing the chamber from ~2-3 meters back

### Stage 2: Door Opening Animation (2.5 seconds)

**Left Door**:
- Starts at: Closed position (x=0)
- Slides to: Just shy of fully open (x=-85% of door width)
- Speed: Easing function (ease-out-cubic) for natural deceleration
- Duration: 2.5 seconds
- Audio: Low mechanical hum, steady pitch rise

**Right Door**:
- Starts at: Closed position (x=0)
- Slides to: Just shy of fully open (x=+85% of door width)
- Speed: Easing function (ease-out-cubic, synchronized with left door)
- Duration: 2.5 seconds
- Audio: Same as left door (mirrored)

**Visual Cue**: As doors open, seams between doors and walls glow faintly (cyan/gold), suggesting pressure/energy release.

### Stage 3: Heavenly Void Reveal (Immediate upon door opening)

**Visual Setup**:
- Through the opening: Deep dark blue glowing space (like starfield or void)
- Color palette: #001a4d → #003d99 gradient (dark navy to medium blue)
- Glow intensity: Subtle, not blinding
- Particle effects (optional): Very sparse floating particles (embers/dust), slow drift
- No clear geometry visible yet—intentionally ambiguous and ethereal

**Lighting**:
- Hard cut: Chamber lighting (warm, architectural) → void lighting (cool, diffuse)
- Bloom effect on void glow for soft halo
- Player chamber becomes shadowed (backlit by void)

**Audio**:
- Door mechanical hum fades (2 seconds)
- Ambient drone enters: Low-frequency pad (like heavenly choir filtered through water)
- Volume: Soft, immersive, builds very gradually over 5 seconds

**Duration**: Player sees pure void for ~3-4 seconds before being prompted to advance

### Stage 4: Progressive Reveal (Player Movement Through Threshold)

**Trigger**: Player presses forward/move key after brief pause

**Camera/Player Movement**:
- Smooth camera dolly forward (auto-move if desired, or player-controlled)
- Speed: Slow, ~1.5 meters/second
- Duration: ~5-7 seconds to reach revelation point

**Reveal Mechanics**:
As player moves forward through the threshold:

**Distance Checkpoint 1** (50% through opening):
- Silhouette of end-image begins to emerge from void
- Very faint, almost imperceptible at first
- Player might think it's architecture or natural formation

**Distance Checkpoint 2** (75% through opening):
- End-image becomes more defined
- Recognition begins to set in
- Lighting shifts slightly warmer as void transitions

**Distance Checkpoint 3** (Fully through opening):
- Full revelation of Velinor_Saori_End_Reveal.png
- Image fills most/all of viewport
- Lighting fully transitions to end scene lighting
- Ambient audio swells (crescendo over 2 seconds)

**Visual Effects During Reveal**:
- Fade in: End-image opacity goes from 0% → 100% (over 5-7 second duration)
- Depth cue: End-image appears to be at infinite distance (no depth of field)
- Glow continuation: Faint blue/gold glow persists around edges of image (connects to door glow)
- Particle fade: Void particles fade out as image clarifies

**Audio During Reveal**:
- Drone continues to build
- Subtle harmonic shifts (emotional resonance based on player's final TONE state)
- Optional: Very faint musical motif tied to player's journey themes
- Wind/air whoosh as final threshold is crossed (2-second build, then sustain)

---

## Technical Implementation (Three.js/WebGL)

### Door Animation

```javascript
class DoorAnimation {
  constructor(leftDoor, rightDoor) {
    this.leftDoor = leftDoor;
    this.rightDoor = rightDoor;
    this.duration = 2500; // ms
    this.easing = 'easeOutCubic';
  }
  
  play() {
    const timeline = new gsap.timeline();
    
    // Simultaneous door sliding
    timeline.to(this.leftDoor.position, {
      x: -this.leftDoor.userData.slideDistance * 0.85,
      duration: this.duration / 1000,
      ease: this.easing
    }, 0);
    
    timeline.to(this.rightDoor.position, {
      x: this.rightDoor.userData.slideDistance * 0.85,
      duration: this.duration / 1000,
      ease: this.easing
    }, 0); // Start at same time as left door
    
    // Door glow seam effect
    timeline.to(this.leftDoor.material, {
      emissiveIntensity: 0.3,
      duration: this.duration / 1000 * 0.3
    }, 0);
    
    timeline.to(this.rightDoor.material, {
      emissiveIntensity: 0.3,
      duration: this.duration / 1000 * 0.3
    }, 0);
  }
}
```

### Void Reveal & Progressive Image Fade

```javascript
class VoidRevealSequence {
  constructor(voidMesh, endImage, camera, player) {
    this.voidMesh = voidMesh; // Glowing void geometry
    this.endImage = endImage; // Plane/quad with Velinor_Saori_End_Reveal.png
    this.camera = camera;
    this.player = player;
    this.revealDistance = 10; // meters
  }
  
  startProgressiveReveal() {
    // Player advances through threshold
    const startPos = this.player.position.z;
    const endPos = startPos + this.revealDistance;
    
    const revealTimeline = new gsap.timeline();
    
    // Fade in end image as player moves
    revealTimeline.to(this.endImage.material, {
      opacity: 1,
      duration: 7, // Match movement duration
      ease: 'easeInOutQuad'
    }, 0);
    
    // Shift from void lighting to end-scene lighting
    revealTimeline.to(this.voidMesh.material, {
      emissiveIntensity: 0.2, // Fade void glow
      duration: 7,
      ease: 'easeInOutQuad'
    }, 0);
    
    // Audio swell
    revealTimeline.to(audioContext, {
      volume: 1,
      duration: 7,
      ease: 'easeInOutQuad'
    }, 0);
    
    // Player movement
    revealTimeline.to(this.player.position, {
      z: endPos,
      duration: 7,
      ease: 'easeInOutQuad'
    }, 0);
  }
}
```

### Particle System (Void Drift)

```javascript
// Optional sparse particles drifting in void
class VoidParticles {
  constructor(scene) {
    const geometry = new THREE.BufferGeometry();
    const positions = [];
    
    // Sparse particle cloud (50-100 particles)
    for (let i = 0; i < 75; i++) {
      positions.push(
        (Math.random() - 0.5) * 20,
        (Math.random() - 0.5) * 20,
        Math.random() * 30 - 5
      );
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(positions), 3));
    
    const material = new THREE.PointsMaterial({
      color: 0x00ffff,
      size: 0.05,
      sizeAttenuation: true,
      opacity: 0.2,
      transparent: true
    });
    
    this.particles = new THREE.Points(geometry, material);
    scene.add(this.particles);
  }
  
  animate() {
    this.particles.rotation.x += 0.0001;
    this.particles.rotation.y += 0.0002;
  }
  
  fadeOut(duration = 3) {
    gsap.to(this.particles.material, {
      opacity: 0,
      duration: duration,
      ease: 'easeInOutQuad'
    });
  }
}
```

---

## Visual Specifications

### Void Environment

**Color Scheme**:
- Primary: #001a4d (very dark navy)
- Secondary: #003d99 (medium dark blue)
- Accent glow: #00ffff (cyan) or #ffff00 (gold)

**Lighting**:
- Directional fill from void (soft, diffuse)
- Bloom enabled (strength: 0.3-0.5)
- No hard shadows (intentionally soft/ethereal)

**Mood**:
- Heavenly, transcendent
- Sense of infinity/vastness
- Peaceful, not menacing

### End Image Composition

**Velinor_Saori_End_Reveal.png**:
- Should fill majority of viewport
- Positioned behind player (at depth/distance)
- Framed by void glow/halo effect
- Color temperature: Match void blues OR shift warmer (depends on emotional tone desired)

**Progressive Fade Details**:
- Fade in starts at very low opacity (5%) 
- Peak opacity at 100% when fully revealed
- Easing: ease-in-out (smooth acceleration/deceleration)
- No sudden jumps in visibility

---

## Audio Design

### Door Opening (2.5 seconds)
- **Mechanical hum**: 50-100 Hz fundamental, rising pitch
- **Resonance tone**: Brief harmonic swell as doors stop
- **Volume**: -6dB (present but not dominant)
- **Fade**: Fade out over 1 second after doors stop

### Void Ambient (Fade in during reveal)
- **Pad**: Deep droning pad (like filtered choir or synth pad)
- **Frequency**: 60-120 Hz range (felt more than heard)
- **Volume**: -12dB → -3dB (gradual swell)
- **Duration**: Continuous loop, sustain through end reveal
- **Qualities**: Ethereal, timeless, slightly otherworldly

### Final Swell (Last 2 seconds of reveal)
- **Build**: Harmonic overtones added to pad
- **Crescendo**: Peak at final image reveal
- **Duration**: 2 seconds build + 3-5 second sustain
- **Optional**: Include player-theme leitmotif (faint, in background)

---

## Pacing Breakdown

| Stage | Duration | Action |
|-------|----------|--------|
| Void reveal | 0-2.5s | Doors slide open, void glows |
| Void contemplate | 2.5-5.5s | Player sees pure void, pauses (optional prompt) |
| Progressive reveal | 5.5-12.5s | Player moves forward, image fades in |
| Final image | 12.5s+ | Full revelation, player at rest |

---

## Accessibility & Variant Considerations

**Skip Option**: Allow players to skip to final image (for repeat playthroughs or accessibility)

**Difficulty Variants** (optional):
- **"Gentle" mode**: Slower reveal, more time to contemplate void
- **"Direct" mode**: Skip void stage, go straight to end image
- **"Extended" mode**: Longer void contemplation (meditative)

**Audio Variants** (optional):
- **Silent mode**: Remove audio cues, rely on visual progression
- **Narration variant**: Optional voiceover during final swell

---

## Post-Reveal Mechanics

After player reaches end image:
1. Fade to black (3-5 seconds)
2. Credits roll (if applicable)
3. Optional epilogue scenes (based on TONE state / ending branch)
4. Return to main menu or NG+ prompt

---

## Asset Checklist

- [ ] Left door asset (with slide-rail guides visible)
- [ ] Right door asset (mirrored)
- [ ] Door glow/seam textures
- [ ] Void environment (skybox or custom geometry)
- [ ] Velinor_Saori_End_Reveal.png (high resolution)
- [ ] Void particle sprites/textures
- [ ] Door mechanical hum SFX (1-2 seconds, loopable)
- [ ] Resonance tone SFX (0.5-1 second decay)
- [ ] Void ambient pad (loop, ~30 seconds minimum)
- [ ] Final swell audio (crescendo + sustain)
- [ ] Optional leitmotif track (10-15 seconds)

---

## Design Philosophy

This sequence prioritizes:
- **Emotional transcendence**: The void represents crossing a threshold from collapse to revelation
- **Player agency**: Movement is player-controlled (or smoothly auto-moved), maintaining presence
- **Progressive storytelling**: Image reveal mirrors player's own understanding/acceptance
- **Sensory immersion**: Audio, visuals, timing all work in concert
- **Contemplation**: Pacing allows moment of awe before final revelation
