# Audio Persistence Across Scene Transitions

## Overview

Your `AudioManager` is now configured to **persist audio across scene transitions**. Music that's playing in one scene will automatically continue playing when the player moves to a new scene—unless explicitly overridden with a different track.

## How It Works

### Key Mechanism: `DontDestroyOnLoad()`

The AudioManager uses Unity's `DontDestroyOnLoad()` function to survive scene unloads:

```csharp
if (persistAcrossScenes)
{
    DontDestroyOnLoad(gameObject);
}
```

**This means:**
- The AudioManager GameObject persists when `SceneManager.LoadScene()` is called
- Music continues playing seamlessly
- Only one instance exists (singleton pattern prevents duplicates)

### Singleton Pattern

The AudioManager implements a singleton to ensure only one audio playback system exists:

```csharp
private static AudioManager instance;

if (instance == null)
{
    instance = this;
    DontDestroyOnLoad(gameObject);
}
else if (instance != this)
{
    Destroy(gameObject); // Destroy duplicate instances
}
```

## Usage in Your Scenes

### Scenario 1: Continue Music from Previous Scene

No code needed! If music is playing in Scene A and the player transitions to Scene B:
- The music keeps playing automatically
- Audio quality is uninterrupted
- No pop/click artifacts

### Scenario 2: Override with New Music

When a scene needs different music, explicitly call:

```csharp
AudioManager.Instance.PlayMusicTrack(newClip, "Scene-Specific Track");
// OR for smooth transitions:
AudioManager.Instance.CrossfadeToTrack(newClip, "Scene-Specific Track");
```

### Scenario 3: Stop Music for Silence

To stop music when entering a scene:

```csharp
AudioManager.Instance.StopMusic(fadeOutDuration: 1.5f);
// OR immediate stop:
AudioManager.Instance.StopMusic();
```

### Scenario 4: Resume Paused Music

If music was paused and you want to resume it:

```csharp
AudioManager.Instance.ResumeMusic();
```

## Implementation Pattern

In any scene script, follow this pattern:

```csharp
using Velinor.Core;
using UnityEngine;

public class MySceneSetup : MonoBehaviour
{
    private void Start()
    {
        // Check if music is already playing from previous scene
        if (AudioManager.Instance.IsMusicContinuing())
        {
            Debug.Log("🎵 Music continuing from previous scene");
            // Optionally fade in if needed
            return;
        }

        // No music playing, so start this scene's music
        AudioManager.Instance.PlayMusicTrack(mySceneTrack, "My Scene Ambient");
    }
}
```

## Configuration

In the Inspector, the AudioManager has a new option:

- **Persist Across Scenes** (checkbox)
  - ✅ ON = Music continues between scenes (recommended for most games)
  - ❌ OFF = Music stops when scenes unload (old behavior)

## Public API Reference

### Query Methods

```csharp
// Get singleton instance
AudioManager.Instance

// Check if music is currently playing
AudioManager.Instance.IsPlaying()

// Get the track currently playing
AudioManager.Instance.GetCurrentTrack()

// Check if music from previous scene is continuing
AudioManager.Instance.IsMusicContinuing()

// Get current volume (0-1)
AudioManager.Instance.GetMusicVolume()
```

### Playback Control

```csharp
// Play a track immediately
AudioManager.Instance.PlayMusicTrack(audioClip, "Track Name");

// Smoothly transition to new track
AudioManager.Instance.CrossfadeToTrack(audioClip, "New Track");

// Stop music with optional fade
AudioManager.Instance.StopMusic(fadeOutDuration: 2f);

// Resume if paused
AudioManager.Instance.ResumeMusic();

// Set volume (0-1)
AudioManager.Instance.SetMusicVolume(0.5f);
```

## Best Practices

### ✅ DO:

1. **Check before playing new music**
   ```csharp
   if (!AudioManager.Instance.IsMusicContinuing())
   {
       AudioManager.Instance.PlayMusicTrack(clip);
   }
   ```

2. **Use Crossfade for smooth transitions**
   ```csharp
   AudioManager.Instance.CrossfadeToTrack(newClip, "Market");
   ```

3. **Explicitly stop music when silence is needed**
   ```csharp
   if (isBossEncounter)
   {
       AudioManager.Instance.StopMusic(1.5f); // Fade out over 1.5 seconds
   }
   ```

4. **Access via the Instance singleton**
   ```csharp
   AudioManager.Instance.PlayMusicTrack(clip);
   // NOT: GetComponent<AudioManager>() - may fail!
   ```

### ❌ DON'T:

1. **Don't call DontDestroyOnLoad multiple times** - The singleton handles this
2. **Don't access the AudioSource directly** - Use the public API instead
3. **Don't expect music to survive if the AudioManager is disabled** - Keep it enabled
4. **Don't instantiate multiple AudioManagers** - The singleton pattern prevents this

## Scene Transition Workflow

### Example: Transitioning from Market Scene → Forest Scene

**Market Scene (playing Glass Horizon):**
```csharp
public class MarketSceneSetup : MonoBehaviour
{
    private void Start()
    {
        // Start music
        AudioManager.Instance.PlayMusicTrack(glassHorizonClip, "Market Ambient");
    }
}
```

**Player walks to Forest → Scene transitions**

**Forest Scene starts:**
```csharp
public class ForestSceneSetup : MonoBehaviour
{
    private void Start()
    {
        // Option A: Keep market music (no code needed!)
        // Glass Horizon continues playing

        // Option B: Switch to forest music
        AudioManager.Instance.CrossfadeToTrack(forestClip, "Forest Ambience");

        // Option C: Play in silence
        AudioManager.Instance.StopMusic(1.5f);
    }
}
```

## Technical Details

### Why `DontDestroyOnLoad()`?

When you load a new scene with `SceneManager.LoadScene()`:
- All GameObjects in the old scene are destroyed
- **EXCEPT** those marked with `DontDestroyOnLoad()`
- Audio stops unless the AudioSource GameObject survives

### Singleton Pattern Benefit

Without a singleton:
- Multiple scene loads could create duplicate AudioManagers
- Multiple AudioSources would play simultaneously (chaos!)
- With singleton: Only one instance ever exists

### Memory Efficiency

- Single AudioSource with pooled clips
- No duplication across scenes
- Audio clips are cached in memory (pre-loaded by AudioManager)

## Troubleshooting

### Problem: Music stops when scene transitions

**Solution:** Check that `Persist Across Scenes` is enabled in the Inspector

### Problem: Two instances of AudioManager exist

**Solution:** The singleton pattern prevents duplicates, but if you see duplicates:
1. Check you're not manually instantiating AudioManager in multiple scenes
2. Ensure there's only one AudioManager prefab in your first/startup scene
3. All subsequent scenes should NOT have an AudioManager

### Problem: Music crackles or pops during crossfade

**Solution:** Increase `crossfadeDuration` in the Inspector (try 2-3 seconds)

### Problem: Scene loads but no music plays

**Solution:** Call `AudioManager.Instance.ResumeMusic()` in the new scene's Start() method

## Example: Complete Scene Setup

Here's a complete example showing persistent audio:

```csharp
using Velinor.Core;
using UnityEngine;

public class CompleteSceneSetup : MonoBehaviour
{
    [SerializeField] private AudioClip sceneAmbiance;

    private void Start()
    {
        // Scenario 1: If music is already playing from previous scene, keep it
        if (AudioManager.Instance.IsMusicContinuing())
        {
            Debug.Log("🎵 Continuing music from previous scene");
            return;
        }

        // Scenario 2: Otherwise, start this scene's music
        if (sceneAmbiance != null)
        {
            AudioManager.Instance.CrossfadeToTrack(sceneAmbiance, gameObject.scene.name);
        }
    }

    private void OnDisable()
    {
        // NOTE: Don't stop music here! It persists to the next scene.
        // Only stop if you explicitly want silence.
    }
}
```

## Integration with Existing Code

If you have scene-specific audio setup scripts (like `MarketSceneAudioSetup`), update them:

**Before:**
```csharp
public class MarketSceneAudioSetup : MonoBehaviour
{
    private void Start()
    {
        audioManager.PlayMarketSoundscape();
    }
}
```

**After:**
```csharp
public class MarketSceneAudioSetup : MonoBehaviour
{
    private void Start()
    {
        // Music continues from previous scene OR starts here if new
        if (!AudioManager.Instance.IsMusicContinuing())
        {
            AudioManager.Instance.PlayMarketSoundscape();
        }
    }
}
```

## Summary

| Behavior | Action | Code |
|----------|--------|------|
| Continue existing music | Do nothing | (empty Start) |
| Switch to new track | Crossfade | `AudioManager.Instance.CrossfadeToTrack(clip)` |
| Stop music | Fade out | `AudioManager.Instance.StopMusic(duration)` |
| Pause & resume | Control | `ResumeMusic()` after pause |
| Check if playing | Query | `AudioManager.Instance.IsPlaying()` |

Your audio system now intelligently persists across scenes while allowing explicit control when needed!
