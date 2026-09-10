using System;
using UnityEngine;

/// <summary>
/// A unified dialogue beat structure.
/// Empty fields are simply not displayed. Same system, different content.
/// </summary>
[Serializable]
public class BeatData
{
    [SerializeField] public float id;                       // 1, 2, 3, 3.1, etc. or use pid for passages
    [SerializeField] public string pid;                    // "desert_intro" (passages format) or null (beats)
    [SerializeField] public string type;                   // "player_posture", "npc_turn", "npc_shared"
    [SerializeField] public string active_speaker;         // "Player", "Nima", "Ravi", "Shared", etc.
    [SerializeField] public string setting_description;    // Scene context (optional)
    [SerializeField] public string prompt;                 // Main dialogue line (NPC speech or player thought)
    [SerializeField] public string shared_beat;            // Automatic NPC response (shown then auto-advances)
    [SerializeField] public BeatChoice[] tone_choices;     // Player choice options
    [SerializeField] public string[] required_flags;       // Flags needed to see this beat
    [SerializeField] public SystemTrigger[] system_triggers; // Actions to trigger
    [SerializeField] public float next_beat_id;            // Next beat ID (supports decimals like 3.1)

    // Backwards compat fields (for passages format)
    [SerializeField] public string name;                   // (passages only)
    [SerializeField] public string conversationId;         // (passages only)
    [SerializeField] public BeatChoice[] choices;          // (passages only - alias for tone_choices)

    [NonSerialized] public DialogueMode mode;
}

/// <summary>
/// A single player choice within a beat.
/// Empty fields (empty strings) are simply not displayed.
/// </summary>
[Serializable]
public class BeatChoice
{
    [SerializeField] public string tone;                   // "T", "O", "N", "E", "C"
    [SerializeField] public string label;                  // "Trust", "Observation", "NarrativePresence", "Empathy"
    [SerializeField] public string text;                   // Player's spoken line or choice text
    [SerializeField] public string result_text;            // Immediate feedback after choice (empty = skip)
    [SerializeField] public string npc_response;           // NPC's reply (empty = skip)
    [SerializeField] public BeatEffect[] tone_effects;     // TONE stat changes
    [SerializeField] public BeatEffect[] remnants_effects; // NPC REMNANTS changes
    [SerializeField] public float target;                  // Next beat ID (or 0 for end)
    [SerializeField] public string[] system_triggers;      // Array of system triggers to execute
    
    // Backwards compat
    [SerializeField] public string tone_str;               // (passages format: derives tone)
    [SerializeField] public string playerLine;             // (passages format)
    [SerializeField] public string shared_beat;            // (passages format)
    [SerializeField] public string data_hook;              // (passages format)
    [SerializeField] public string system_trigger;         // (passages format)
}

/// <summary>
/// A single TONE or REMNANTS effect.
/// </summary>
[Serializable]
public class BeatEffect
{
    [SerializeField] public string stat;
    [SerializeField] public float delta;
    [SerializeField] public string target;                 // For remnants: "Nima", "Ravi", "activeNpcId", etc.
}

/// <summary>
/// A system trigger (diary update, close dialogue, etc.)
/// </summary>
[Serializable]
public class SystemTrigger
{
    [SerializeField] public string type;                   // "diary_append", "close_dialogue", etc.
    [SerializeField] public string[] data;                 // Type-specific data
}

/// <summary>
/// Root structure for dialogue JSON files.
/// Supports both passages and beats formats.
/// </summary>
[Serializable]
public class DialogueJson
{
    [SerializeField] public string name;                   // (passages format)
    [SerializeField] public string startnode;              // (passages format)
    [SerializeField] public BeatData[] passages;           // (passages format)
    
    [SerializeField] public string scene_id;               // (beats format)
    [SerializeField] public string[] required_flags;       // (beats format)
    [SerializeField] public BeatData[] beats;              // (beats format)
}
