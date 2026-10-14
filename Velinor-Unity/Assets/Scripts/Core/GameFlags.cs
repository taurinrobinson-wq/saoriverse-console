using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Global game flags that persist across scenes.
/// Used for tracking dialogue completion, NPC state, and other game-wide state.
/// 
/// Examples:
///   GameFlags.Set("ravi_nima_market_discovery_complete", true);
///   if (GameFlags.Get("ravi_nima_market_discovery_complete")) { ... }
/// 
/// Flags set via dialogue system_triggers automatically use this to persist state.
/// </summary>
public static class GameFlags
{
    private static readonly Dictionary<string, bool> flags = new Dictionary<string, bool>();

    public static void Set(string key, bool value)
    {
        if (string.IsNullOrWhiteSpace(key))
            return;

        flags[key] = value;
        Debug.Log($"[GameFlags] {key} = {value}");
        // In future: could add PlayerPrefs.SetInt(key, value ? 1 : 0) for save persistence
    }

    public static bool Get(string key, bool defaultValue = false)
    {
        if (string.IsNullOrWhiteSpace(key))
            return defaultValue;

        return flags.TryGetValue(key, out var value) ? value : defaultValue;
    }

    public static bool HasFlag(string key)
    {
        return !string.IsNullOrWhiteSpace(key) && flags.ContainsKey(key);
    }

    public static void Clear()
    {
        flags.Clear();
        Debug.Log("[GameFlags] Cleared all flags");
    }

    public static int GetFlagCount()
    {
        return flags.Count;
    }

    /// <summary>
    /// Get all active flags for debugging
    /// </summary>
    public static IEnumerable<KeyValuePair<string, bool>> GetAllFlags()
    {
        return flags;
    }
}
