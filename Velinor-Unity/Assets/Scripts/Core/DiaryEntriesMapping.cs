using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Maps diary entry keys to their content text.
/// Used by DialogueManager when system_triggers call "diary_append" events.
/// Example: "market_discovery_daughter_hint" → "Ravi mentioned an unstable building... and a daughter."
/// </summary>
public static class DiaryEntriesMapping
{
    private static Dictionary<string, string> entries = new Dictionary<string, string>
    {
        // Market Discovery Encounter
        {
            "market_discovery_daughter_hint",
            "Ravi mentioned an unstable building. And... a daughter. There's grief in how he said it, the kind that never fully settles. Nima wouldn't look at him when he spoke. Whatever happened here, it bound them together in a way I don't yet understand."
        },

        // Nima Encounter Entries
        {
            "nima_market_anniversary",
            "Today marks one year since Nima lost someone here. A collapse. The ground itself became a tomb. She returns to this spot despite the pain—or perhaps because of it. Some places refuse to let us forget."
        },

        {
            "nima_guard_relationship",
            "Nima is guarded. Observant. She watches threats the way a hawk watches wind currents. Every word from her carries weight; she doesn't waste breath on pleasantries. But there's more to her than caution—there's a protective fiber running through her, even when she's grieving."
        },

        {
            "nima_grief_marker",
            "The ground took her. Those were Nima's words. Whatever happened here left deep scars—not just physical, but emotional. This place is a marker of what can be lost in seconds."
        },

        // Kaelen Confession Entries
        {
            "kaelen_witnessed_collapse",
            "Kaelen was there when it happened. They froze. And now, that moment of inaction sits with them like a stone in the chest. Guilt isn't something they're hiding—it's something they're drowning in."
        },

        {
            "kaelen_wall_failure",
            "A wall groaned. A brace snapped. These small mechanical failures can cascade into catastrophe. Kaelen saw it happen but couldn't move fast enough to stop it. Now they live in the gap between 'I could have' and 'I didn't.'"
        },

        // Ravi-Specific Entries
        {
            "ravi_instability_warning",
            "The buildings in Velhara are unstable. Walls fail. People vanish. This isn't new construction settling—something is actively destabilizing the infrastructure. And Ravi seems to think it's connected to the collapsed building where his daughter was lost."
        },

        {
            "ravi_irreparable_loss",
            "Ravi said: 'Some things stay broken.' There's finality in that statement, but also a kind of hollow acceptance. He's living in the aftermath of a loss he can't repair or reverse. Just... endure."
        },

        // Glyph/Codex Entries
        {
            "obtained_codex",
            "She gave me this device without explanation. Her name is Saori. She appeared and vanished like a ghost, leaving only her words: 'Use it wisely.' The Codex hums in my hands—warm, waiting, patient. Whatever it is meant to do, I'm only beginning to understand."
        },

        // Willy Encounter Entries
        {
            "willy_concourse_glyph",
            "I found it. The Glyph of Sorrow, buried under the Concourse ruins. It took Willy—a scrapper who knows these piles like a surgeon knows flesh—to clear the way. When my hand touched its surface, the world became heavy. Everything I carry now feels weighted, as if the glyph itself passed something to me. Sorrow is not abstract anymore. It's a thing I hold."
        },

        {
            "glyph_codex_observation",
            "The Codex I carry resonates with something in this place. Ravi noticed it immediately. There's a connection between these collapsed structures and whatever this artifact is—or what it's trying to tell me."
        },

        // Generic Reflection Entries
        {
            "place_weight",
            "This marketplace carries weight. Not just history, but active trauma. People have died here. People are still grieving. The air itself feels different around loss."
        },

        {
            "npc_pattern_recognition",
            "I'm beginning to see patterns in the NPCs I meet: they're all connected to loss, to the collapse, to something that's fundamentally broken in this place. And each of them carries a piece of understanding I need."
        }
    };

    /// <summary>
    /// Get diary entry text by key.
    /// Returns the entry text if found, or a warning message if not.
    /// </summary>
    public static string GetEntry(string key)
    {
        if (entries.TryGetValue(key, out var text))
        {
            return text;
        }

        Debug.LogWarning($"[DiaryEntriesMapping] Entry key not found: {key}");
        return $"[Diary Entry: {key}]";  // Fallback placeholder
    }

    /// <summary>
    /// Check if a diary entry key exists.
    /// </summary>
    public static bool HasEntry(string key)
    {
        return entries.ContainsKey(key);
    }

    /// <summary>
    /// Manually add or override a diary entry (for runtime or testing).
    /// </summary>
    public static void SetEntry(string key, string text)
    {
        entries[key] = text;
        Debug.Log($"[DiaryEntriesMapping] Set entry: {key}");
    }
}
