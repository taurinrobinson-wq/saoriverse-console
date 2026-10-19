using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Persistent singleton that survives all scene transitions.
/// Stores global game state: NPC visibility, dialogue completion, glyph collection, etc.
/// 
/// This replaces per-scene state management with a truly persistent world state.
/// Survives until Play mode stops.
/// </summary>
public class GameState : MonoBehaviour
{
    public static GameState Instance { get; private set; }

    // NPC visibility states (e.g., "Ravi" -> false means disabled, true means enabled)
    public Dictionary<string, bool> npcVisibility = new Dictionary<string, bool>();

    // Dialogue completion states (e.g., "ravi_nima_market_discovery_complete" -> true)
    public Dictionary<string, bool> dialogueFlags = new Dictionary<string, bool>();

    // Glyph collection states (e.g., "glyph_sorrow" -> true)
    public Dictionary<string, bool> glyphFlags = new Dictionary<string, bool>();

    // Quest/objective states
    public Dictionary<string, string> questStates = new Dictionary<string, string>();

    private void Awake()
    {
        // Singleton pattern: only one GameState can exist
        if (Instance != null && Instance != this)
        {
            Debug.LogWarning("[GameState] Another instance already exists, destroying this one");
            Destroy(gameObject);
            return;
        }

        Instance = this;
        
        // Make this GameObject persist across all scene transitions
        DontDestroyOnLoad(gameObject);

        Debug.Log("[GameState] Initialized as persistent singleton");

        // Initialize default NPC states (all NPCs visible by default)
        InitializeDefaults();
    }

    /// <summary>
    /// Set up default states for all known NPCs
    /// Only sets defaults if they don't already exist (preserves state on scene reload)
    /// </summary>
    private void InitializeDefaults()
    {
        // Market NPCs
        SetNPCVisibilityDefault("Ravi", true);
        SetNPCVisibilityDefault("Nima", true);
        SetNPCVisibilityDefault("Kaelen", true);
        SetNPCVisibilityDefault("Willy", true);
        
        // Add more NPCs as needed
        Debug.Log("[GameState] Default states initialized");
    }

    /// <summary>
    /// Set an NPC's visibility state, overwriting any previous state.
    /// Use this when a trigger (dialogue, collider, etc.) changes NPC visibility.
    /// </summary>
    public void SetNPCVisibility(string npcID, bool isVisible)
    {
        npcVisibility[npcID] = isVisible;
        Debug.Log($"[GameState] NPC visibility changed: {npcID} -> {(isVisible ? "VISIBLE" : "HIDDEN")}");
    }

    /// <summary>
    /// Get an NPC's current visibility state.
    /// Returns true if NPC should be visible, false if hidden.
    /// </summary>
    public bool GetNPCVisibility(string npcID)
    {
        if (npcVisibility.ContainsKey(npcID))
        {
            return npcVisibility[npcID];
        }
        
        // If no state exists, default to visible
        Debug.LogWarning($"[GameState] No visibility state for {npcID}, defaulting to visible");
        return true;
    }

    /// <summary>
    /// Internal: only sets default if key doesn't exist
    /// </summary>
    private void SetNPCVisibilityDefault(string npcID, bool isVisible)
    {
        if (!npcVisibility.ContainsKey(npcID))
        {
            npcVisibility[npcID] = isVisible;
        }
    }

    /// <summary>
    /// Set a dialogue flag (called by dialogue system when dialogue completes)
    /// </summary>
    public void SetDialogueFlag(string flagName, bool value)
    {
        dialogueFlags[flagName] = value;
        Debug.Log($"[GameState] Dialogue flag set: {flagName} = {value}");
    }

    /// <summary>
    /// Get a dialogue flag
    /// </summary>
    public bool GetDialogueFlag(string flagName)
    {
        if (dialogueFlags.ContainsKey(flagName))
        {
            return dialogueFlags[flagName];
        }
        return false;
    }

    /// <summary>
    /// Set a glyph collection flag
    /// </summary>
    public void SetGlyphFlag(string glyphID, bool isCollected)
    {
        glyphFlags[glyphID] = isCollected;
        Debug.Log($"[GameState] Glyph flag set: {glyphID} = {isCollected}");
    }

    /// <summary>
    /// Get a glyph collection flag
    /// </summary>
    public bool GetGlyphFlag(string glyphID)
    {
        if (glyphFlags.ContainsKey(glyphID))
        {
            return glyphFlags[glyphID];
        }
        return false;
    }

    /// <summary>
    /// Set a quest state (e.g., "quest_name" -> "in_progress", "completed", etc.)
    /// </summary>
    public void SetQuestState(string questID, string state)
    {
        questStates[questID] = state;
        Debug.Log($"[GameState] Quest state set: {questID} = {state}");
    }

    /// <summary>
    /// Get a quest state
    /// </summary>
    public string GetQuestState(string questID)
    {
        if (questStates.ContainsKey(questID))
        {
            return questStates[questID];
        }
        return "not_started";
    }

    /// <summary>
    /// Clear all state (useful for testing or new game)
    /// </summary>
    public void ResetAllState()
    {
        npcVisibility.Clear();
        dialogueFlags.Clear();
        glyphFlags.Clear();
        questStates.Clear();
        InitializeDefaults();
        Debug.Log("[GameState] All state has been reset to defaults");
    }

    /// <summary>
    /// Print all current state to console (for debugging)
    /// </summary>
    public void DebugPrintState()
    {
        Debug.Log("=== GAME STATE DEBUG ===");
        
        Debug.Log("--- NPC Visibility ---");
        foreach (var kvp in npcVisibility)
        {
            Debug.Log($"  {kvp.Key}: {kvp.Value}");
        }

        Debug.Log("--- Dialogue Flags ---");
        foreach (var kvp in dialogueFlags)
        {
            Debug.Log($"  {kvp.Key}: {kvp.Value}");
        }

        Debug.Log("--- Glyph Flags ---");
        foreach (var kvp in glyphFlags)
        {
            Debug.Log($"  {kvp.Key}: {kvp.Value}");
        }

        Debug.Log("--- Quest States ---");
        foreach (var kvp in questStates)
        {
            Debug.Log($"  {kvp.Key}: {kvp.Value}");
        }
    }
}
