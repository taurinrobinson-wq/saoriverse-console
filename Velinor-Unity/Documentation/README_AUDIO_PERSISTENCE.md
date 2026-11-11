# 🎵 Audio Persistence System - Complete Guide

## Quick Answer to Your Question

**Q: Is there a way to make it so when the player transitions the sound from the prior scene continues to play, except when it's overridden by a different sound file?**

**A: YES! ✅** Your AudioManager now does exactly this using `DontDestroyOnLoad()` and a singleton pattern.

---

## What Changed

Your `AudioManager.cs` has been enhanced with:

### 1. **Singleton Pattern** 
Ensures only one AudioManager exists across all scenes
```csharp
private static AudioManager instance;

if (instance == null)
{
    instance = this;
    DontDestroyOnLoad(gameObject);  // ← Music survives scene unloads
}
```

### 2. **New Inspector Option**
- **Persist Across Scenes** (enabled by default)
- Toggle ON = Music continues across scenes
- Toggle OFF = Old behavior (music stops)

### 3. **New Public Methods**
```csharp
AudioManager.Instance                  // Access from anywhere
AudioManager.Instance.IsMusicContinuing()  // Check if continuing from previous scene
AudioManager.Instance.ResumeMusic()        // Resume if paused
```

---

## How It Works: Visual Guide

### Before (Old Behavior)
```
Market Scene           Shop Scene
┌──────────────┐      ┌──────────────┐
│ Music: ON    │      │ Music: OFF   │ ❌
│ Volume: 0.7  │  →   │ Silence      │
│ "Glass Horiz"│      │              │
└──────────────┘      └──────────────┘
```

### After (New Behavior)
```
Market Scene           Shop Scene (Default)
┌──────────────┐      ┌──────────────┐
│ Music: ON    │      │ Music: ON    │ ✅
│ Volume: 0.7  │  →   │ Volume: 0.7  │
│ "Glass Horiz"│      │ "Glass Horiz"│ (CONTINUES)
└──────────────┘      └──────────────┘

OR with Override:
Shop Scene (Custom Music)
┌──────────────┐
│ Music: ON    │ ✅
│ Volume: 0.7  │
│ "Shop Ambiance"│ (CROSSFADED)
└──────────────┘

OR with Silence:
Boss Arena Scene
┌──────────────┐
│ Music: OFF   │ ✅
│ (Fading out) │
│ Silence      │
└──────────────┘
```

---

## Implementation by Use Case

### Use Case 1: Continue Music (Most Scenes)
```csharp
public class ShopScene : MonoBehaviour
{
    private void Start()
    {
        // Do nothing! Music continues automatically from previous scene
        Debug.Log("🎵 Music from market continues here");
    }
}
```

### Use Case 2: Override with New Music
```csharp
public class BossArenaScene : MonoBehaviour
{
    [SerializeField] private AudioClip bossMusic;

    private void Start()
    {
        // Crossfade to boss music smoothly
        AudioManager.Instance.CrossfadeToTrack(bossMusic, "Boss Battle");
    }
}
```

### Use Case 3: Silence for Dramatic Effect
```csharp
public class CutsceneScene : MonoBehaviour
{
    private void Start()
    {
        // Fade out music over 1.5 seconds
        AudioManager.Instance.StopMusic(fadeOutDuration: 1.5f);
    }
}
```

### Use Case 4: Check Before Deciding
```csharp
public class AdaptiveScene : MonoBehaviour
{
    [SerializeField] private AudioClip sceneMusic;

    private void Start()
    {
        // If music is already playing from previous scene, keep it
        if (AudioManager.Instance.IsMusicContinuing())
        {
            Debug.Log("🎵 Continuing music from previous scene");
            return;
        }

        // Otherwise, play this scene's music
        if (sceneMusic != null)
        {
            AudioManager.Instance.CrossfadeToTrack(sceneMusic, "Scene Ambiance");
        }
    }
}
```

---

## Public API Reference

### Query Methods
| Method | Returns | Purpose |
|--------|---------|---------|
| `AudioManager.Instance` | AudioManager | Get the singleton instance |
| `.IsPlaying()` | bool | Is music currently playing? |
| `.IsMusicContinuing()` | bool | Is music from previous scene playing? |
| `.GetCurrentTrack()` | AudioClip | Which track is playing? |
| `.GetMusicVolume()` | float | Current volume (0-1) |

### Playback Control
| Method | Purpose |
|--------|---------|
| `.PlayMusicTrack(clip, name)` | Play track immediately |
| `.CrossfadeToTrack(clip, name)` | Smooth transition to new track (2-3 seconds) |
| `.StopMusic(duration)` | Fade out and stop (duration in seconds) |
| `.ResumeMusic()` | Resume if paused |
| `.SetMusicVolume(0-1)` | Adjust volume |

---

## Step-by-Step Setup

### Step 1: Verify Inspector Settings
1. Open your scene with AudioManager
2. Select the AudioManager GameObject
3. In Inspector, find the **AudioManager** component
4. Check: **Persist Across Scenes** = ☑️ ON
5. Verify: **Music Volume** is set (default 0.7)
6. Verify: **Crossfade Duration** is 2-3 seconds

### Step 2: Test a Scene Transition
1. Load Scene A (has music)
2. Transition to Scene B (no audio code)
3. Result: Music should continue automatically ✅

### Step 3: Update Scenes (As Needed)
- **Most scenes:** No code needed (music continues)
- **Boss/Special:** Add code to override music or silence
- **Unique:** Attach `SceneAudioController` template

### Step 4: Debug (If Needed)
Check Console for messages starting with 🎵:
- `🎵 AudioManager: Set to persist across scenes`
- `🎵 Now playing: [Track Name]`
- `🎵 Crossfading to: [Track Name]`

---

## Common Questions

**Q: Will music continue in ALL scenes?**
A: Yes! By default, music continues. Each scene can override this if needed.

**Q: How do I stop music?**
A: Call `AudioManager.Instance.StopMusic(1.5f)` to fade out over 1.5 seconds.

**Q: Can I have different music per scene?**
A: Yes! Use `CrossfadeToTrack()` to smoothly transition to new music.

**Q: What if I want music to pause and resume?**
A: Use `ResumeMusic()` to continue from where it left off.

**Q: What if there are multiple AudioManagers?**
A: The singleton pattern prevents duplicates. Extras are destroyed automatically.

**Q: Can I have multiple songs playing at once?**
A: This implementation uses a single AudioSource. For layered music, extend the AudioManager.

---

## Documentation Files

| File | Purpose | Read Time |
|------|---------|-----------|
| [AUDIO_PERSISTENCE_QUICK_REFERENCE.md](AUDIO_PERSISTENCE_QUICK_REFERENCE.md) | Quick lookup & examples | 5 min |
| [AUDIO_SCENE_PERSISTENCE_GUIDE.md](AUDIO_SCENE_PERSISTENCE_GUIDE.md) | Complete technical guide | 15 min |
| [AUDIO_PERSISTENCE_EXAMPLES.md](AUDIO_PERSISTENCE_EXAMPLES.md) | 7 real-world scenarios | 20 min |
| [AUDIO_PERSISTENCE_SETUP_CHECKLIST.md](AUDIO_PERSISTENCE_SETUP_CHECKLIST.md) | Step-by-step implementation | 30 min |

---

## Code Files Created

### AudioManager.cs (Updated)
Enhanced with singleton pattern and persistence
- Location: `Assets/Scripts/Core/AudioManager.cs`
- Changes: +Singleton, +DontDestroyOnLoad(), +New methods

### SceneAudioController.cs (New Template)
Ready-to-use scene audio controller template
- Location: `Assets/Scripts/Core/SceneAudioController.cs`
- Attach to any scene for easy audio control
- Configurable in Inspector

---

## Before & After Comparison

### BEFORE
```csharp
// No way to continue music across scenes
// Music stops every scene transition
// Each scene needs its own AudioManager
// No unified audio control
```

### AFTER
```csharp
// Music continues automatically
// Scenes can override when needed
// Single AudioManager handles everything
// Full control via AudioManager.Instance
// Smooth crossfades
// Query state with IsMusicContinuing()
```

---

## Pro Tips

### ✅ Best Practices

1. **Always use CrossfadeToTrack() for changes**
   ```csharp
   // ✅ Good: Smooth transition
   AudioManager.Instance.CrossfadeToTrack(newClip);
   
   // ❌ Avoid: Jarring cut-off
   AudioManager.Instance.PlayMusicTrack(newClip);
   ```

2. **Check before playing**
   ```csharp
   // ✅ Good: Avoid redundant playback
   if (!AudioManager.Instance.IsMusicContinuing())
   {
       AudioManager.Instance.PlayMusicTrack(clip);
   }
   ```

3. **Fade to silence, don't cut**
   ```csharp
   // ✅ Good: Graceful fade
   AudioManager.Instance.StopMusic(1.5f);
   
   // ❌ Avoid: Abrupt silence
   AudioManager.Instance.StopMusic(0);
   ```

4. **Use the Instance singleton**
   ```csharp
   // ✅ Correct: Works everywhere
   AudioManager.Instance.PlayMusicTrack(clip);
   
   // ❌ Wrong: May fail in other scenes
   GetComponent<AudioManager>().PlayMusicTrack(clip);
   ```

---

## Troubleshooting

### Problem: Music Stops on Transition
**Solution:** 
1. Check "Persist Across Scenes" is ☑️ ON
2. Verify only one AudioManager in startup scene
3. Ensure AudioManager GameObject is enabled

### Problem: Duplicate Audio Playing
**Solution:**
1. Singleton prevents duplicates automatically
2. If you see duplicates, remove AudioManager from non-startup scenes
3. Check console for "Another instance exists. Destroying this one."

### Problem: No Sound
**Solution:**
1. Verify AudioListener exists in scene
2. Check audio volume > 0
3. Ensure audio files are in Resources folder
4. Check Time.timeScale != 0

### Problem: Crackling During Crossfade
**Solution:**
1. Increase crossfadeDuration to 3-4 seconds (Inspector)
2. Check audio files aren't corrupted
3. Verify sufficient memory available

---

## Architecture Diagram

```
                    PERSISTENT LAYER
                   (DontDestroyOnLoad)
                    ┌─────────────────┐
                    │ AudioManager    │
                    │  - Instance     │
                    │  - musicSource  │
                    │  - currentTrack │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
       Scene A            Scene B            Scene C
       ┌──────┐         ┌──────┐          ┌──────┐
       │Music │         │ Can: │          │ Can: │
       │Start │  →      │  1.Continue    │  1.Continue
       └──────┘         │  2.Change      │  2.Change
                        │  3.Silence     │  3.Silence
                        └──────┘          └──────┘
```

---

## Next Actions

1. **Right Now:** 
   - Open Inspector, verify "Persist Across Scenes" = ON
   - Test one scene transition

2. **This Session:**
   - Read AUDIO_PERSISTENCE_QUICK_REFERENCE.md
   - Update 2-3 scene scripts as examples

3. **This Week:**
   - Update all scenes with appropriate audio behavior
   - Test all scene transitions
   - Adjust crossfade duration and volumes to taste

4. **Future:**
   - Implement volume ducking for dialogue
   - Add dynamic music layers for combat
   - Implement conditional music based on game state

---

## Summary

✨ **Your AudioManager now supports seamless audio persistence across scene transitions!**

- 🎵 Music continues automatically when scenes change
- 🔄 Scenes can override with new tracks (smooth crossfades)
- 🔇 Scenes can request silence (graceful fade-out)
- 🎚️ Full control via public API
- 🏗️ Singleton pattern (clean architecture)
- 📝 Comprehensive documentation and examples

**Start using it today!** Most scenes need zero code changes—music just works. ✨

---

For detailed information, see:
- Quick Start: [AUDIO_PERSISTENCE_QUICK_REFERENCE.md](AUDIO_PERSISTENCE_QUICK_REFERENCE.md)
- Complete Guide: [AUDIO_SCENE_PERSISTENCE_GUIDE.md](AUDIO_SCENE_PERSISTENCE_GUIDE.md)
- Examples: [AUDIO_PERSISTENCE_EXAMPLES.md](AUDIO_PERSISTENCE_EXAMPLES.md)
- Setup Steps: [AUDIO_PERSISTENCE_SETUP_CHECKLIST.md](AUDIO_PERSISTENCE_SETUP_CHECKLIST.md)
