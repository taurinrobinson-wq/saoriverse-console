# Glass Horizon Integration - Market Scene Audio Setup

## Overview

**Glass Horizon** is now your market soundscape—looping continuously as the atmospheric backdrop while players explore the market and interact with Malrik/Elenya.

The audio system is designed to:
- Play Glass Horizon on loop in the market
- Crossfade to other tracks for dialogue moments (e.g., Simple.ogg for love revelation)
- Return to market ambience afterward
- Manage volume and fading smoothly

---

## Quick Setup (In Unity Editor)

### Step 1: Add AudioManager to Scene

1. Open **Marketplace.unity** scene
2. Right-click in Hierarchy → Create Empty
3. Rename to: `AudioManager`
4. Add Component: **AudioManager** (drag script onto it)
5. In Inspector, keep defaults (they auto-load your Music files)

### Step 2: Add MarketSceneAudioSetup

1. Right-click in Hierarchy → Create Empty
2. Rename to: `MarketAudioSetup`
3. Add Component: **MarketSceneAudioSetup**
4. Leave references empty (it finds AudioManager automatically)

### Step 3: Play Scene

1. Press Play ▶
2. You should hear Glass Horizon begin playing on loop
3. Watch console: `🎵 Market soundscape started: Glass Horizon (looping)`

---

## Architecture

### AudioManager (Core Audio Handler)

```
AudioManager
├── PlayMarketSoundscape()           → Plays Glass Horizon
├── PlayMusicTrack(clip)             → Play any audio clip
├── CrossfadeToTrack(clip)           → Smooth transition between tracks
├── StopMusic(fadeOutDuration)       → Stop with optional fade
└── SetMusicVolume(volume)           → Control loudness
```

**Key Settings in Inspector:**
- `Music Volume`: 0.7 (70% - good default)
- `Auto Loop Music`: ✓ enabled (Glass Horizon loops continuously)
- `Crossfade Duration`: 2 seconds (time to fade between tracks)

### MarketSceneAudioSetup (Scene Integration)

Automatically starts Glass Horizon on scene load and provides helpers:

```csharp
// Called automatically on Start()
StartMarketSoundscape();            // Begin Glass Horizon

// When dialogue occurs
TransitionToDialogueMusic("malrik_elenya");  // Switch to Simple.ogg

// After dialogue
ReturnToMarketSoundscape();         // Back to Glass Horizon
```

---

## Hookup Example: Using with DialogueManager

When Malrik & Elenya's love revelation begins, you can trigger audio transition:

```csharp
// In your DialogueManager or dialogue trigger
public class MalrikElenyaDialogue : MonoBehaviour
{
    private MarketSceneAudioSetup audioSetup;

    private void Start()
    {
        audioSetup = FindObjectOfType<MarketSceneAudioSetup>();
    }

    public void BeginLoveRevealDialogue()
    {
        // Switch to Simple.ogg (charming, lo-fi) for this moment
        audioSetup.TransitionToDialogueMusic("malrik_elenya");
        
        // Start dialogue sequence...
        // StartDialogueSequence();
    }

    public void EndLoveRevealDialogue()
    {
        // Return to ambient market soundscape
        audioSetup.ReturnToMarketSoundscape();
    }
}
```

---

## Audio Tracks & Their Uses

Your 8 OGG files mapped to their narrative moments:

| Track | Mood | Use Case | Loop Fade |
|-------|------|----------|-----------|
| **Glass-Horizon.ogg** | Contemplative, ambient | Market exploration, default soundscape | ✓ Faded |
| **Simple.ogg** | Charming, lo-fi, plinky | Malrik & Elenya love revelation | ✓ Faded |
| **Into-the-codex.ogg** | Mysterious, introspective | Discovery of ancient knowledge | ✓ Faded |
| **Traveling-along.ogg** | Adventurous, journey | Movement between locations | ✓ Faded |
| **Sorrow-walks.ogg** | Melancholic, emotional | Sad/reflective moments | ✓ Faded |
| **A-strange-serenity-_fade_.ogg** | Ethereal, dreamy | Supernatural/magical moments | ✓ Faded |
| **Some-ambience-.ogg** | Atmospheric, textured | General ambience layer | ✓ Faded |
| **Velinor-fades-_effect_.ogg** | Fade/transition effect | Scene transitions, effects | ✓ Faded |

---

## Scripting Examples

### Example 1: Manual Music Playback

```csharp
AudioManager audioMgr = GetComponent<AudioManager>();

// Play a specific clip
audioMgr.PlayMusicTrack(
    Resources.Load<AudioClip>("Music/Into-the-codex"),
    "Into the Codex"
);

// Crossfade smoothly
audioMgr.CrossfadeToTrack(
    Resources.Load<AudioClip>("Music/Simple"),
    "Simple - Dialogue"
);

// Check what's playing
if (audioMgr.IsPlaying())
    Debug.Log("Current track: " + audioMgr.GetCurrentTrack().name);

// Adjust volume
audioMgr.SetMusicVolume(0.5f);  // 50%
```

### Example 2: Scene-Based Transitions

```csharp
// In your NPC interaction script
public class VendorInteraction : MonoBehaviour
{
    private MarketSceneAudioSetup audioSetup;

    private void Start()
    {
        audioSetup = FindObjectOfType<MarketSceneAudioSetup>();
    }

    public void OnVendorTalk()
    {
        // Fade to travelling music during vendor journey story
        audioSetup.TransitionToDialogueMusic("travel");
    }

    public void OnVendorDone()
    {
        // Return to market ambient
        audioSetup.ReturnToMarketSoundscape();
    }
}
```

### Example 3: Add New Music Transition

```csharp
// Extend MarketSceneAudioSetup with new dialogue types
public void TransitionToDialogueMusic(string dialogueType = "malrik_elenya")
{
    switch (dialogueType)
    {
        case "ancient_temple":
            audioManager.CrossfadeToTrack(
                Resources.Load<AudioClip>("Music/Into-the-codex"),
                "Into the Codex - Temple Discovery"
            );
            break;
        
        // Add more cases as needed...
    }
}
```

---

## Setup Checklist

- [ ] Created AudioManager GameObject in Marketplace scene
- [ ] Attached AudioManager script component
- [ ] Created MarketSceneAudioSetup GameObject
- [ ] Attached MarketSceneAudioSetup script component
- [ ] Played scene and heard Glass Horizon start
- [ ] Console shows: "🎵 Market soundscape started: Glass Horizon (looping)"
- [ ] Music files visible in Resources/Music folder (Inspector)

---

## Troubleshooting

### Problem: No sound when playing scene
- **Check:** AudioManager component is in scene (Inspector → find it)
- **Check:** Scene has Main Camera (required for audio)
- **Check:** Music volume slider in AudioManager is not at 0
- **Action:** Set AudioManager's `musicVolume` to 0.7 in Inspector

### Problem: Music cuts off abruptly
- **Check:** Glass Horizon clip has fade applied (you did this ✓)
- **Check:** `Auto Loop Music` is enabled in AudioManager
- **Action:** If not looping, enable this checkbox

### Problem: Can't hear transition between tracks
- **Check:** `Crossfade Duration` is not 0 (should be ~2 seconds)
- **Action:** Increase from current value (makes fade slower, more noticeable)

### Problem: Music doesn't load from Resources
- **Check:** Music files are in `Assets/Music/` folder
- **Problem:** Script tries to load from Resources, which needs special folder
- **Solution:** Either:
  1. Keep in `Assets/Music/`, drag clips directly into Inspector fields, OR
  2. Create `Assets/Resources/Music/` folder and move files there

---

## Performance Note

AudioManager uses a single AudioSource for all music playback. This is efficient and standard practice:
- One source playing one track at a time
- Clean transitions with crossfading
- Minimal CPU/GPU overhead

If you later add sound effects (vendor chatter, wind, etc.), you can add secondary AudioSources for those separately.

---

## Next Steps

1. **Set up scene** - Follow the Quick Setup section above
2. **Test playback** - Play scene and confirm Glass Horizon loops
3. **Connect dialogue** - When you build dialogue scenes, use `TransitionToDialogueMusic()` to switch tracks
4. **Iterate on mood** - Adjust volume, crossfade duration, etc. based on feel

Your dusk market scene + Glass Horizon = atmospheric foundation for Malrik & Elenya's story. Perfect for introspective dialogue moments with that charming lo-fi soundtrack layered underneath.
