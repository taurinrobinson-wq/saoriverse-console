# Audio Persistence - Practical Examples

## Scene Transition Scenarios

### Scenario 1: Continue Market Music into Shop

**Market Scene:**
```csharp
public class MarketScene : MonoBehaviour
{
    private void Start()
    {
        // Only play if no music is already playing
        if (!AudioManager.Instance.IsPlaying())
        {
            AudioManager.Instance.PlayMusicTrack(marketAmbiance, "Market Ambiance");
        }
    }
}
```

**Player enters shop → Scene transition**

**Shop Scene:**
```csharp
public class ShopScene : MonoBehaviour
{
    private void Start()
    {
        // Music from market continues automatically!
        // No code needed unless you want to change it
    }
}
```

**Result:** 🎵 Market music continues playing smoothly in the shop

---

### Scenario 2: Switch Music on Specific Scene

**Market Scene:** Glass Horizon playing

**Transition to Dark Cavern**

**CavernScene.cs:**
```csharp
public class CavernScene : MonoBehaviour
{
    [SerializeField] private AudioClip cavernMusic; // Spooky track

    private void Start()
    {
        // Always use cavern music here, don't continue market music
        AudioManager.Instance.CrossfadeToTrack(cavernMusic, "Cavern - Deep Darkness");
    }
}
```

**Result:** 🎵 Smooth crossfade from market music → cavern music

---

### Scenario 3: Boss Encounter (Silence)

**Forest Scene:** Traveling Along playing

**Player encounters boss → Scene transition**

**BossArenaScene.cs:**
```csharp
public class BossArenaScene : MonoBehaviour
{
    private void Start()
    {
        // Boss fights in silence!
        AudioManager.Instance.StopMusic(fadeOutDuration: 2f);
    }

    public void OnBossDefeated()
    {
        // Resume music after victory
        AudioManager.Instance.ResumeMusic();
    }
}
```

**Result:** 🎵 Music fades out → Boss arena is silent → Music resumes when boss defeated

---

### Scenario 4: Layered Audio (Dialogue on Top)

**Town Square:** Simple background music

**NPC Dialogue starts:**
```csharp
public class DialogueController : MonoBehaviour
{
    private void PlayNPCDialogue(AudioClip voiceover)
    {
        // Background music keeps playing at reduced volume
        AudioManager.Instance.SetMusicVolume(0.3f);
        
        // Play voiceover on a separate AudioSource
        AudioSource voiceSource = gameObject.AddComponent<AudioSource>();
        voiceSource.PlayOneShot(voiceover);
    }

    private void OnDialogueEnd()
    {
        // Restore music volume
        AudioManager.Instance.SetMusicVolume(0.7f);
    }
}
```

**Result:** 🎵 Background music + dialogue simultaneously

---

### Scenario 5: Conditional Music Based on Inventory

**Tavern Scene:**
```csharp
public class TavernScene : MonoBehaviour
{
    private AudioClip cheerfulMusic;
    private AudioClip melancholyMusic;

    private void Start()
    {
        // Choose music based on game state
        bool hasCompletedMainQuest = GameState.HasCompletedQuestLine("main");
        
        AudioClip music = hasCompletedMainQuest ? cheerfulMusic : melancholyMusic;
        
        AudioManager.Instance.CrossfadeToTrack(music, "Tavern Ambiance");
    }
}
```

**Result:** 🎵 Different music based on player progress

---

### Scenario 6: Dynamic Music Layers

**Combat System:**
```csharp
public class CombatManager : MonoBehaviour
{
    private AudioClip baseMusic;
    private AudioClip intensityLayer;
    private AudioSource layerSource;

    private void Start()
    {
        // Main music continues (or starts)
        if (!AudioManager.Instance.IsPlaying())
        {
            AudioManager.Instance.PlayMusicTrack(baseMusic, "Combat Base");
        }

        // Add intensity layer
        layerSource = gameObject.AddComponent<AudioSource>();
    }

    public void OnEnemySpotted()
    {
        // Fade in intensity layer
        layerSource.clip = intensityLayer;
        layerSource.Play();
        StartCoroutine(FadeInLayer());
    }

    private IEnumerator FadeInLayer()
    {
        float elapsed = 0;
        while (elapsed < 1f)
        {
            elapsed += Time.deltaTime;
            layerSource.volume = Mathf.Lerp(0, 0.5f, elapsed);
            yield return null;
        }
    }
}
```

**Result:** 🎵 Base music + dynamic intensity layer

---

### Scenario 7: Crossfade on Environmental Change

**Outdoor Scene:**
```csharp
public class WeatherSystem : MonoBehaviour
{
    private AudioClip sunnyMusic;
    private AudioClip rainyMusic;

    public void OnWeatherChanged(Weather newWeather)
    {
        switch (newWeather)
        {
            case Weather.Sunny:
                AudioManager.Instance.CrossfadeToTrack(sunnyMusic, "Sunny Day");
                break;
            
            case Weather.Rainy:
                AudioManager.Instance.CrossfadeToTrack(rainyMusic, "Rainy Day");
                break;
            
            case Weather.Stormy:
                AudioManager.Instance.StopMusic(fadeOutDuration: 1f);
                break;
        }
    }
}
```

**Result:** 🎵 Music changes based on weather in real-time

---

## Code Templates

### Template 1: Basic Scene Setup
```csharp
using Velinor.Core;
using UnityEngine;

public class MyScene : MonoBehaviour
{
    [SerializeField] private AudioClip sceneMusic;

    private void Start()
    {
        if (!AudioManager.Instance.IsMusicContinuing())
        {
            AudioManager.Instance.PlayMusicTrack(sceneMusic, "My Scene");
        }
    }
}
```

### Template 2: With Forced Music Change
```csharp
using Velinor.Core;
using UnityEngine;

public class BossScene : MonoBehaviour
{
    [SerializeField] private AudioClip bossMusic;

    private void Start()
    {
        // Always play boss music, override previous scene
        AudioManager.Instance.CrossfadeToTrack(bossMusic, "Boss Battle");
    }
}
```

### Template 3: With Conditional Logic
```csharp
using Velinor.Core;
using UnityEngine;

public class FlexibleScene : MonoBehaviour
{
    [SerializeField] private AudioClip sceneMusic;
    [SerializeField] private bool forceNewMusic = false;

    private void Start()
    {
        bool shouldPlayNewMusic = forceNewMusic || 
                                  !AudioManager.Instance.IsMusicContinuing();

        if (shouldPlayNewMusic && sceneMusic != null)
        {
            AudioManager.Instance.CrossfadeToTrack(sceneMusic, gameObject.scene.name);
        }
    }
}
```

### Template 4: Silence on Entry
```csharp
using Velinor.Core;
using UnityEngine;

public class SilentScene : MonoBehaviour
{
    [SerializeField] private float fadeOutDuration = 2f;

    private void Start()
    {
        AudioManager.Instance.StopMusic(fadeOutDuration);
    }
}
```

---

## Testing Your Setup

### Test 1: Verify Persistence
1. Load Scene A with music playing
2. Transition to Scene B (no audio code)
3. ✅ Music should continue uninterrupted

### Test 2: Verify Override
1. Load Scene A with music playing
2. Scene B calls `CrossfadeToTrack(newClip)`
3. ✅ Music should smoothly transition to new track

### Test 3: Verify Singleton
1. Add `SceneAudioController` to two different scenes
2. Load Scene A, then Scene B
3. ✅ Only one AudioManager instance should exist (check console)
4. ❌ Duplicate instances should be destroyed automatically

### Test 4: Verify Silence
1. Load Scene A with music playing
2. Scene B calls `StopMusic()`
3. ✅ Music should fade out and stop

---

## Performance Considerations

### Single AudioSource (Current Implementation)
- ✅ Lightweight
- ✅ Great for linear music changes
- ❌ Can't layer multiple tracks simultaneously

### Multi-Track Extension
If you need simultaneous music layers:

```csharp
public class AdvancedAudioManager : MonoBehaviour
{
    private AudioSource[] sources; // Multiple sources
    private float[] targetVolumes; // Track volumes

    public void PlayLayeredMusic(AudioClip base, AudioClip layer1, AudioClip layer2)
    {
        sources[0].clip = base;
        sources[1].clip = layer1;
        sources[2].clip = layer2;
        
        foreach (var source in sources)
            source.Play();
    }
}
```

---

## Common Patterns

| Use Case | Method | Code |
|----------|--------|------|
| Continue previous music | Do nothing | (no code) |
| Change music | Crossfade | `CrossfadeToTrack()` |
| Stop music | Stop | `StopMusic()` |
| Reduce volume | Set volume | `SetMusicVolume(0.3f)` |
| Pause & resume | Resume | `ResumeMusic()` |
| Check if playing | Query | `IsPlaying()` |

---

## Debug Checklist

When music isn't working:

- [ ] Is AudioManager in the first scene?
- [ ] Is `persistAcrossScenes` enabled?
- [ ] Is the AudioManager GameObject enabled?
- [ ] Are audio clips assigned in Inspector?
- [ ] Check console for 🎵 debug messages
- [ ] Is there an AudioListener in the scene?
- [ ] Are audio files in correct format (.mp3, .ogg, .wav)?
- [ ] Is the music volume > 0?

---

## Next Steps

1. Copy `SceneAudioController.cs` to your scene scripts
2. Attach it to a game object in each scene
3. Configure which music plays where
4. Test scene transitions
5. Iterate until audio behavior matches your vision

Enjoy seamless audio transitions! 🎵
