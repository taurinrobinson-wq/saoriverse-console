using System.Collections.Generic;
using UnityEngine;

public static class GameFlags
{
    private static readonly Dictionary<string, bool> flags = new Dictionary<string, bool>();

    public static void Set(string key, bool value)
    {
        if (string.IsNullOrWhiteSpace(key))
            return;

        flags[key] = value;
        Debug.Log($"[GameFlags] {key} = {value}");
    }

    public static bool Get(string key, bool defaultValue = false)
    {
        if (string.IsNullOrWhiteSpace(key))
            return defaultValue;

        return flags.TryGetValue(key, out var value) ? value : defaultValue;
    }

    public static void Clear()
    {
        flags.Clear();
    }
}
