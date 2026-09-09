using System;
using UnityEngine;

/// <summary>
/// A single dialogue beat (passage in JSON).
/// This structure maps directly to the JSON format without transformation.
/// </summary>
[Serializable]
public class BeatData
{
    [SerializeField] public string pid;                    // "desert_intro"
    [SerializeField] public string name;                   // "Older Woman in the Desert"
    [SerializeField] public string conversationId;         // "saori_encounter_01"
    [SerializeField] public string text;                   // NPC's line
    [SerializeField] public BeatChoice[] choices;          // player choices
    [SerializeField] public string[] required_flags;       // flags needed to see this beat

    // Inferred at load time
    [NonSerialized] public DialogueMode mode;              // computed based on content
}

/// <summary>
/// A single choice in a beat. Maps directly to JSON choice structure.
/// </summary>
[Serializable]
public class BeatChoice
{
    [SerializeField] public string text;                   // "(T) Yeah. I'm looking for work..."
    [SerializeField] public string target;                 // "saori_first_react"
    [SerializeField] public string shared_beat;            // NPC's response to this choice
    [SerializeField] public string data_hook;              // "met_older_woman=true"
    [SerializeField] public string system_trigger;         // "give_device" (optional)
    [SerializeField] public EffectWrapper tone_effects;    // TONE effects
    [SerializeField] public EffectWrapper npc_resonance;   // NPC affinity (optional)
    [SerializeField] public string tone_str;               // "Trust", "Observation", etc.
    [SerializeField] public string playerLine;             // without tone prefix

    // Derived at load time
    [NonSerialized] public string tone;                    // "T", "O", "N", "E"
}

/// <summary>
/// Wrapper for the effects { "entries": [...] } structure in JSON.
/// </summary>
[Serializable]
public class EffectEntry
{
    [SerializeField] public string key;
    [SerializeField] public float value;
}

[Serializable]
public class EffectWrapper
{
    [SerializeField] public EffectEntry[] entries;
}

/// <summary>
/// Root structure matching JSON exactly.
/// </summary>
[Serializable]
public class DialogueJson
{
    [SerializeField] public string name;
    [SerializeField] public string startnode;
    [SerializeField] public BeatData[] passages;
}
