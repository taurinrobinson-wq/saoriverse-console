# Audio Persistence - Setup & Implementation Checklist

## ✅ What Was Done

Your AudioManager has been updated with **persistent audio across scene transitions**. Here's what changed:

### Changes Made:

1. **Updated `AudioManager.cs`**
   - Added singleton pattern (`private static AudioManager instance`)
   - Implemented `DontDestroyOnLoad()` to survive scene unloads
   - Added new methods:
     - `AudioManager.Instance` - Singleton accessor
     - `IsMusicContinuing()` - Check if music from previous scene is playing
     - `ResumeMusic()` - Resume paused music
   - New Inspector option: `Persist Across Scenes` (default: ON)

2. **Created `SceneAudioController.cs`**
   - Template for scene-specific audio behavior
   - Configurable music override, fade options
   - Ready to attach to any scene

3. **Created 3 Documentation Files**
   - `AUDIO_SCENE_PERSISTENCE_GUIDE.md` - Complete technical guide
   - `AUDIO_PERSISTENCE_QUICK_REFERENCE.md` - Quick lookup reference
   - `AUDIO_PERSISTENCE_EXAMPLES.md` - Real-world code examples

---

## 🎯 Step-by-Step Implementation

### Step 1: Verify AudioManager Setup ✅
- [x] `AudioManager.cs` has been updated
- [ ] Open the scene with your AudioManager GameObject
- [ ] In Inspector, verify: **Persist Across Scenes = ON**
- [ ] Confirm only **one** AudioManager exists in your startup scene

### Step 2: Audit Your Scenes ⚠️
- [ ] List all scenes in your project
- [ ] For each scene, determine: Does it need custom music or silence?
  
  **Categorize:**
  - **Scenes A-Z:** Can use music from previous scene
  - **Scenes X-Y:** Need specific music (boss fight, shop, etc.)
  - **Scenes M-N:** Need silence

### Step 3: Update Scene Scripts
For each scene, choose one pattern:

**Pattern A: Continue Previous Music**
```csharp
// Do nothing! Music continues automatically
```

**Pattern B: Specific Music Required**
```csharp
using Velinor.Core;

public class MyScene : MonoBehaviour
{
    [SerializeField] private AudioClip sceneMusic;

    private void Start()
    {
        if (sceneMusic != null)
            AudioManager.Instance.CrossfadeToTrack(sceneMusic, "Scene Name");
    }
}
```

**Pattern C: Silence Required**
```csharp
using Velinor.Core;

public class SilentScene : MonoBehaviour
{
    private void Start()
    {
        AudioManager.Instance.StopMusic(fadeOutDuration: 1.5f);
    }
}
```

### Step 4: (Optional) Use SceneAudioController
Instead of writing custom scripts, attach the template:

1. Copy `SceneAudioController.cs` code
2. Add to a new script in your Assets folder
3. In each scene, add to any GameObject:
   ```
   Add Component → SceneAudioController
   ```
4. Configure in Inspector:
   - Scene Ambient Music (clip)
   - Force Music Change (boolean)
   - Stop Music On Entry (boolean)

### Step 5: Test Each Transition ✅

For each scene pair that transitions:

1. **Load Scene A**
   - [ ] Verify music plays
   - [ ] Check console for 🎵 debug message

2. **Transition to Scene B**
   - [ ] If B should continue A's music: Verify it does
   - [ ] If B should change music: Verify it crossfades
   - [ ] If B should be silent: Verify music fades out

3. **Return to Scene A**
   - [ ] Verify previous state is maintained (or restart)

### Step 6: Debug Issues (If Any)

**Problem: No music plays**
- [ ] Check AudioManager is enabled in Inspector
- [ ] Verify audio clips are assigned
- [ ] Check for errors in Console (🎵 prefix)
- [ ] Ensure AudioListener exists in scene

**Problem: Music stops on transition**
- [ ] Verify `Persist Across Scenes = ON`
- [ ] Check only one AudioManager in startup scene
- [ ] Ensure AudioManager isn't in multiple scenes
- [ ] Check Time.timeScale isn't 0

**Problem: Duplicate audio/cacophony**
- [ ] Multiple AudioManagers exist → Remove duplicates
- [ ] Multiple AudioSources playing → Use singleton only
- [ ] Dialog + background music clashing → Reduce background volume

---

## 📋 Complete Setup Checklist

### Pre-Implementation
- [ ] Backed up current `AudioManager.cs`
- [ ] Reviewed current scene structure
- [ ] Identified which scenes need which music

### Implementation
- [ ] Updated `AudioManager.cs` with singleton pattern
- [ ] Created `SceneAudioController.cs` template
- [ ] Created documentation files
- [ ] Each scene has audio handling code (or uses template)
- [ ] All scenes are tested

### Verification
- [ ] Scene A → Scene B: Music continues ✅
- [ ] Scene B → Scene C (different music): Crossfades smoothly ✅
- [ ] Scene D (silence): Music stops ✅
- [ ] Return transitions work ✅
- [ ] Console shows 🎵 debug messages ✅
- [ ] No duplicate AudioManagers ✅

### Optimization (Optional)
- [ ] Adjust `crossfadeDuration` for smooth transitions (2-3 sec recommended)
- [ ] Set `musicVolume` to desired level (0.7 default)
- [ ] Add volume ducking for dialogue scenes
- [ ] Implement dynamic music layers for combat

---

## 🎵 Quick Reference

| Need | Method | Code |
|------|--------|------|
| Check if music is playing | `IsPlaying()` | `AudioManager.Instance.IsPlaying()` |
| Check if continuing from previous scene | `IsMusicContinuing()` | `AudioManager.Instance.IsMusicContinuing()` |
| Play music immediately | `PlayMusicTrack()` | `AudioManager.Instance.PlayMusicTrack(clip)` |
| Smooth transition | `CrossfadeToTrack()` | `AudioManager.Instance.CrossfadeToTrack(clip)` |
| Stop with fade | `StopMusic()` | `AudioManager.Instance.StopMusic(1.5f)` |
| Stop immediately | `StopMusic(0)` | `AudioManager.Instance.StopMusic(0)` |
| Change volume | `SetMusicVolume()` | `AudioManager.Instance.SetMusicVolume(0.5f)` |
| Get current track | `GetCurrentTrack()` | `AudioManager.Instance.GetCurrentTrack()` |
| Resume if paused | `ResumeMusic()` | `AudioManager.Instance.ResumeMusic()` |

---

## 📚 Documentation Overview

Three guides have been created:

### 1. **AUDIO_SCENE_PERSISTENCE_GUIDE.md** (Complete)
- Technical overview
- Singleton pattern explanation
- Full API reference
- Best practices
- Troubleshooting
- 8+ code examples

### 2. **AUDIO_PERSISTENCE_QUICK_REFERENCE.md** (Quick)
- TL;DR summary
- Quick task lookup
- Common methods table
- Scene script template
- FAQ

### 3. **AUDIO_PERSISTENCE_EXAMPLES.md** (Practical)
- 7 real-world scenarios
- Scene transition walkthroughs
- 4 code templates
- Testing procedures
- Performance considerations

---

## 🚀 Next Steps

### Immediate (Today)
1. [ ] Review the updated `AudioManager.cs`
2. [ ] Check "Persist Across Scenes" is ON in Inspector
3. [ ] Test one scene transition to verify it works
4. [ ] Read the Quick Reference guide

### Short Term (This Week)
1. [ ] Update each scene with appropriate audio code
2. [ ] Test all scene transitions
3. [ ] Debug any audio issues
4. [ ] Adjust crossfade duration to taste

### Medium Term (This Month)
1. [ ] Implement volume ducking for dialogue
2. [ ] Add conditional music based on game state
3. [ ] Optimize audio performance if needed
4. [ ] Polish audio transitions

---

## ⚠️ Important Notes

### What NOT To Do
- ❌ Don't create AudioManager in every scene
- ❌ Don't call `DontDestroyOnLoad()` manually in your scripts
- ❌ Don't access `musicSource` directly from other classes
- ❌ Don't disable the AudioManager GameObject

### What TO Do
- ✅ Use `AudioManager.Instance` to access from anywhere
- ✅ Use `IsMusicContinuing()` to check before playing new music
- ✅ Use `CrossfadeToTrack()` for smooth transitions
- ✅ Keep AudioManager enabled at all times

---

## 💡 Pro Tips

1. **Always check before playing new music**
   ```csharp
   if (!AudioManager.Instance.IsMusicContinuing())
   {
       AudioManager.Instance.PlayMusicTrack(newClip);
   }
   ```

2. **Use Crossfade for professional feel**
   ```csharp
   // ✅ Good: Smooth transition
   AudioManager.Instance.CrossfadeToTrack(newClip, "Scene Name");
   
   // ❌ Avoid: Jarring cut-off
   AudioManager.Instance.PlayMusicTrack(newClip);
   ```

3. **Fade out before silence**
   ```csharp
   // ✅ Good: Graceful fade
   AudioManager.Instance.StopMusic(fadeOutDuration: 1.5f);
   
   // ❌ Avoid: Abrupt silence
   AudioManager.Instance.StopMusic(0);
   ```

4. **Use the Instance singleton**
   ```csharp
   // ✅ Correct: Cross-scene access
   AudioManager.Instance.PlayMusicTrack(clip);
   
   // ❌ Wrong: May fail in other scenes
   GetComponent<AudioManager>().PlayMusicTrack(clip);
   ```

---

## 📞 Support

If audio isn't working:
1. Check the console for 🎵 debug messages
2. Verify AudioManager is in your startup scene
3. Confirm `Persist Across Scenes` is ON
4. Read the complete guide: `AUDIO_SCENE_PERSISTENCE_GUIDE.md`
5. Try the troubleshooting section

---

## Summary

Your game now has **seamless, persistent audio** across scene transitions!

✨ **Music continues automatically** when scenes change  
🎚️ **Scenes can override** with new tracks when needed  
🔇 **Silence is an option** when scenes require it  
🎵 **Smooth crossfades** prevent jarring audio cuts  

Enjoy! 🎉
