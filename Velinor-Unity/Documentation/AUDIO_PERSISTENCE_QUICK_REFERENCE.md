# Audio Persistence - Quick Reference

## TL;DR

✅ **Music now continues across scene transitions automatically**

- Your AudioManager uses `DontDestroyOnLoad()` to persist
- Only one instance exists (singleton pattern)
- Scenes can override music or let it play

## Setup Checklist

- [ ] Updated `AudioManager.cs` with singleton pattern
- [ ] `persistAcrossScenes` option enabled in Inspector (default: ON)
- [ ] Only **one** AudioManager in your first scene
- [ ] All other scenes should **NOT** have an AudioManager instance

## Common Tasks

### "Music continues from previous scene"
```csharp
// No code needed! It just works.
// If you want to check:
if (AudioManager.Instance.IsMusicContinuing())
{
    Debug.Log("Music is continuing");
}
```

### "Switch to different music"
```csharp
AudioManager.Instance.CrossfadeToTrack(newClip, "Scene Name");
```

### "Stop all music"
```csharp
AudioManager.Instance.StopMusic(fadeOutDuration: 1.5f);
```

### "Check if music is playing"
```csharp
if (AudioManager.Instance.IsPlaying())
{
    Debug.Log("Music is playing");
}
```

### "Get current track"
```csharp
AudioClip current = AudioManager.Instance.GetCurrentTrack();
```

### "Change volume"
```csharp
AudioManager.Instance.SetMusicVolume(0.5f); // 0-1 range
```

## New Methods

| Method | Purpose |
|--------|---------|
| `AudioManager.Instance` | Singleton instance |
| `IsMusicContinuing()` | Check if music from previous scene is playing |
| `ResumeMusic()` | Resume if paused |
| `PlayMusicTrack(clip)` | Play immediately |
| `CrossfadeToTrack(clip)` | Smooth transition |
| `StopMusic(duration)` | Fade out and stop |
| `IsPlaying()` | Check if playing |
| `GetCurrentTrack()` | Get current clip |

## Scene Script Template

```csharp
using Velinor.Core;
using UnityEngine;

public class MyScene : MonoBehaviour
{
    [SerializeField] private AudioClip sceneMusic;

    private void Start()
    {
        // If music is continuing from previous scene, keep it
        if (AudioManager.Instance.IsMusicContinuing())
            return;

        // Otherwise start this scene's music
        if (sceneMusic != null)
            AudioManager.Instance.CrossfadeToTrack(sceneMusic, "Scene Music");
    }
}
```

## Inspector Settings

In the AudioManager component:
- **Persist Across Scenes** = ✅ ON (recommended)
- **Crossfade Duration** = 2 seconds (adjust as needed)
- **Music Volume** = 0.7 (adjust to taste)

## Avoid

❌ Don't create AudioManager in every scene  
❌ Don't call `DontDestroyOnLoad()` manually  
❌ Don't access `musicSource` directly  
❌ Don't expect audio if AudioManager is disabled  

## Debug

Check the console for messages like:
- 🎵 AudioManager: Set to persist across scenes
- 🎵 Now playing: [Track Name]
- 🎵 Crossfading to: [Track Name]

## FAQ

**Q: Will music continue if I disable the AudioManager?**  
A: No. Keep it enabled. It will automatically survive scene unloads.

**Q: Can I have multiple AudioManagers?**  
A: No. The singleton pattern prevents duplicates. Extra instances are destroyed automatically.

**Q: What if I want silence?**  
A: Call `AudioManager.Instance.StopMusic()` explicitly in the scene that needs silence.

**Q: Does this work with multiple AudioSources?**  
A: This implementation uses a single AudioSource. For multi-track audio (e.g., layered music), extend the AudioManager with additional AudioSources.

## Next Steps

1. Open your first scene that has AudioManager
2. Verify `persistAcrossScenes` is enabled
3. Test transitions between scenes
4. Update scene scripts to use `AudioManager.Instance.IsMusicContinuing()`
5. Enjoy seamless audio! 🎵

---

**Full guide:** See `AUDIO_SCENE_PERSISTENCE_GUIDE.md`
