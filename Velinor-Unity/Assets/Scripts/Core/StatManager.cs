using UnityEngine;
using System;
using System.Collections.Generic;
using UnityEngine.Serialization;

/// <summary>
/// ToneType: Player TONE stats (emotional/narrative resonance qualities)
/// These represent the player's playstyle and choices throughout the narrative.
/// </summary>
public enum ToneType
{
    Courage,
    Empathy,
    Observation,
    Wisdom,
    NarrativePresence
}

/// <summary>
/// RemnantType: NPC REMNANTS stats (personality traits shaped by player choices)
/// These are what NPCs are "made of" - fragments reshaped by the player's resonance.
/// Range: 0.1 (recessive) to 0.9 (dominant), never at absolute extremes.
/// </summary>
public enum RemnantType
{
    Resolve,           // Firmness, conviction, backbone
    Empathy,           // Emotional openness, compassion
    Memory,            // Recall of past, context awareness
    Nuance,            // Subtlety, shades of gray, complexity
    Authority,         // Command presence, decisiveness
    Need,              // Vulnerability, dependence, connection desire
    Trust,             // Confidence in others
    Skepticism         // Doubt, caution, suspicion
}

/// <summary>
/// Remnants: Holds all 8 trait values for a single NPC.
/// Serializable for JSON deserialization.
/// </summary>
[System.Serializable]
public class Remnants
{
    public float resolve = 0.6f;
    public float empathy = 0.7f;
    public float memory = 0.6f;
    public float nuance = 0.4f;
    public float authority = 0.5f;
    public float need = 0.5f;
    public float trust = 0.7f;
    public float skepticism = 0.2f;

    public Remnants Clone()
    {
        return new Remnants
        {
            resolve = this.resolve,
            empathy = this.empathy,
            memory = this.memory,
            nuance = this.nuance,
            authority = this.authority,
            need = this.need,
            trust = this.trust,
            skepticism = this.skepticism
        };
    }

    public float Get(RemnantType type)
    {
        return type switch
        {
            RemnantType.Resolve => resolve,
            RemnantType.Empathy => empathy,
            RemnantType.Memory => memory,
            RemnantType.Nuance => nuance,
            RemnantType.Authority => authority,
            RemnantType.Need => need,
            RemnantType.Trust => trust,
            RemnantType.Skepticism => skepticism,
            _ => 0f
        };
    }

    public void Set(RemnantType type, float value)
    {
        switch (type)
        {
            case RemnantType.Resolve: resolve = value; break;
            case RemnantType.Empathy: empathy = value; break;
            case RemnantType.Memory: memory = value; break;
            case RemnantType.Nuance: nuance = value; break;
            case RemnantType.Authority: authority = value; break;
            case RemnantType.Need: need = value; break;
            case RemnantType.Trust: trust = value; break;
            case RemnantType.Skepticism: skepticism = value; break;
        }
    }
}

/// <summary>
/// NpcProfile: Mirrors the structure from npc_profiles.json.
/// Serializable for JSON deserialization.
/// </summary>
[System.Serializable]
public class NpcProfile
{
    public string name;
    public Remnants remnants;
}

/// <summary>
/// EncounterRecord: Tracks a single dialogue choice in history.
/// Mirrors the structure from npc_state.json history.
/// </summary>
[System.Serializable]
public class EncounterRecord
{
    public int encounter;
    public Dictionary<string, float> tone_effects;
    public Dictionary<string, NpcProfile> npc_profiles;
}

/// <summary>
/// NpcStateJson: Root structure for npc_state.json.
/// Mirrors exactly what is loaded from disk.
/// </summary>
[System.Serializable]
public class NpcStateJson
{
    public Dictionary<string, NpcProfile> npc_profiles;
    public Dictionary<string, Dictionary<string, float>> influence_map;
    public List<EncounterRecord> history;
}

/// <summary>
/// StatManager (Singleton)
/// 
/// Core narrative simulation engine that manages:
/// - Player TONE stats (player's playstyle)
/// - NPC REMNANTS stats (NPC personalities shaped by choices)
/// - Influence map (weighted social graph)
/// - History of encounters
/// 
/// When player makes choices:
/// 1. Tone effects update player TONE
/// 2. TONE→REMNANTS correlation automatically adjusts all NPCs
/// 3. NPC resonance applies direct changes to specific NPCs
/// 4. Changes cascade through influence_map to connected NPCs
/// 5. Encounter is logged to history
/// </summary>
public class StatManager : MonoBehaviour
{
    private static StatManager _instance;
    public static StatManager Instance
    {
        get
        {
            if (_instance == null)
            {
                _instance = FindAnyObjectByType<StatManager>(FindObjectsInactive.Exclude);
                if (_instance == null)
                {
                    GameObject go = new GameObject("StatManager");
                    _instance = go.AddComponent<StatManager>();
                }
            }
            return _instance;
        }
    }

    // Player TONE stats
    private Dictionary<ToneType, float> playerTone = new Dictionary<ToneType, float>
    {
        { ToneType.Courage, 0f },
        { ToneType.Empathy, 0f },
        { ToneType.Observation, 0f },
        { ToneType.Wisdom, 0f },
        { ToneType.NarrativePresence, 0f }
    };

    // NPC REMNANTS stats
    private Dictionary<string, Remnants> npcRemnants = new Dictionary<string, Remnants>();

    // Influence map: NPC → { otherNPC: multiplier }
    private Dictionary<string, Dictionary<string, float>> influenceMap = new Dictionary<string, Dictionary<string, float>>();

    // Encounter history
    private List<EncounterRecord> history = new List<EncounterRecord>();

    // Current encounter counter
    private int encounterCount = 0;

    private bool stateLoaded = false;

    private void Awake()
    {
        if (_instance != null && _instance != this)
        {
            Destroy(gameObject);
        }
        else
        {
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }
    }

    private void Start()
    {
        // Automatically load NPC state from Resources on startup
        if (!stateLoaded)
        {
            LoadStateFromResources();
        }
    }

    /// <summary>
    /// Load complete NPC state from npc_state.json.
    /// Initializes REMNANTS, influence map, and history.
    /// </summary>
    public void LoadStateFromJson(string path)
    {
        try
        {
            string json = System.IO.File.ReadAllText(path);
            NpcStateJson stateJson = JsonUtility.FromJson<NpcStateJson>(json);

            // Load NPC REMNANTS
            npcRemnants.Clear();
            foreach (var kvp in stateJson.npc_profiles)
            {
                npcRemnants[kvp.Key] = kvp.Value.remnants.Clone();
            }

            // Load influence map
            influenceMap = stateJson.influence_map;

            // Load history
            history = stateJson.history ?? new List<EncounterRecord>();
            encounterCount = history.Count;

            Debug.Log($"[StatManager] Loaded state from {path}");
            Debug.Log($"[StatManager] Loaded {npcRemnants.Count} NPC profiles");
            Debug.Log($"[StatManager] Influence map has {influenceMap.Count} entries");
            Debug.Log($"[StatManager] History has {history.Count} encounters");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"[StatManager] Failed to load state from {path}: {ex.Message}");
        }
    }

    /// <summary>
    /// Load NPC state from Resources/velinor/data/npc_state.json.
    /// Called automatically on Start() if state not already loaded.
    /// </summary>
    private void LoadStateFromResources()
    {
        try
        {
            string jsonPath = "velinor/data/npc_state";
            TextAsset jsonAsset = Resources.Load<TextAsset>(jsonPath);

            if (jsonAsset == null)
            {
                Debug.LogWarning($"[StatManager] Could not load NPC state from Resources/{jsonPath}.json - file not found");
                Debug.Log("[StatManager] Proceeding with empty state. Call LoadStateFromJson() with full path to load manually.");
                stateLoaded = true;
                return;
            }

            string jsonText = jsonAsset.text;
            NpcStateJson stateJson = JsonUtility.FromJson<NpcStateJson>(jsonText);

            // Load NPC REMNANTS
            npcRemnants.Clear();
            foreach (var kvp in stateJson.npc_profiles)
            {
                npcRemnants[kvp.Key] = kvp.Value.remnants.Clone();
            }

            // Load influence map
            influenceMap = stateJson.influence_map;

            // Load history
            history = stateJson.history ?? new List<EncounterRecord>();
            encounterCount = history.Count;

            stateLoaded = true;

            Debug.Log($"[StatManager] Loaded NPC state from Resources/{jsonPath}");
            Debug.Log($"[StatManager] Loaded {npcRemnants.Count} NPC profiles");
            Debug.Log($"[StatManager] Influence map has {influenceMap.Count} entries");
            Debug.Log($"[StatManager] History has {history.Count} encounters");
        }
        catch (System.Exception ex)
        {
            stateLoaded = true;
            Debug.LogError($"[StatManager] Failed to load NPC state from Resources: {ex.Message}");
        }
    }

    /// <summary>
    /// Save current state to npc_state.json.
    /// Includes all NPC REMNANTS, influence map, and history.
    /// </summary>
    public void SaveStateToJson(string path)
    {
        try
        {
            // Build save structure
            var stateJson = new NpcStateJson
            {
                npc_profiles = new Dictionary<string, NpcProfile>(),
                influence_map = influenceMap,
                history = history
            };

            // Convert REMNANTS back to NpcProfile format
            foreach (var kvp in npcRemnants)
            {
                stateJson.npc_profiles[kvp.Key] = new NpcProfile
                {
                    name = kvp.Key,
                    remnants = kvp.Value.Clone()
                };
            }

            string json = JsonUtility.ToJson(stateJson, true);
            System.IO.File.WriteAllText(path, json);

            Debug.Log($"[StatManager] Saved state to {path}");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"[StatManager] Failed to save state to {path}: {ex.Message}");
        }
    }

    /// <summary>
    /// Adjust player TONE stat.
    /// Automatically applies TONE→REMNANTS correlation to all NPCs.
    /// 
    /// Correlation rules:
    /// - Narrative Presence ↑ → Resolve ↑, Authority ↑; Nuance ↓, Empathy ↓
    /// - Observation ↑ → Nuance ↑, Memory ↑; Authority ↓
    /// - Empathy ↑ → Empathy ↑, Need ↑; Resolve ↓
    /// - Courage ↑ → Resolve ↑, Authority ↑; Nuance ↓, Empathy ↓
    /// - Wisdom ↑ → Memory ↑, Nuance ↑; Skepticism ↓
    /// </summary>
    public void AdjustPlayerTone(ToneType tone, float amount, string activeNpcId)
    {
        if (amount == 0) return;

        // Update player TONE
        playerTone[tone] += amount;
        Debug.Log($"[StatManager] Player {tone} += {amount} (now {playerTone[tone]})");

        // Apply TONE→REMNANTS correlation to ALL NPCs
        ApplyToneToRemnantCorrelation(tone, amount);
    }

    /// <summary>
    /// Apply TONE stat change to all NPC REMNANTS via correlation mapping.
    /// This creates the "ripple effect" where player choices reshape all NPC personalities.
    /// </summary>
    private void ApplyToneToRemnantCorrelation(ToneType tone, float toneAmount)
    {
        foreach (var npcId in npcRemnants.Keys)
        {
            var changes = new Dictionary<RemnantType, float>();

            switch (tone)
            {
                case ToneType.NarrativePresence:
                    if (toneAmount > 0)
                    {
                        changes[RemnantType.Resolve] = toneAmount;
                        changes[RemnantType.Authority] = toneAmount * 0.75f;
                        changes[RemnantType.Nuance] = -toneAmount * 0.75f;
                        changes[RemnantType.Empathy] = -toneAmount * 0.5f;
                    }
                    else
                    {
                        changes[RemnantType.Resolve] = toneAmount;
                        changes[RemnantType.Authority] = toneAmount * 0.75f;
                        changes[RemnantType.Nuance] = -toneAmount * 0.75f;
                        changes[RemnantType.Empathy] = -toneAmount * 0.5f;
                    }
                    break;

                case ToneType.Observation:
                    if (toneAmount > 0)
                    {
                        changes[RemnantType.Nuance] = toneAmount;
                        changes[RemnantType.Memory] = toneAmount;
                        changes[RemnantType.Authority] = -toneAmount * 0.5f;
                    }
                    else
                    {
                        changes[RemnantType.Nuance] = toneAmount;
                        changes[RemnantType.Memory] = toneAmount;
                        changes[RemnantType.Authority] = -toneAmount * 0.5f;
                    }
                    break;

                case ToneType.Empathy:
                    if (toneAmount > 0)
                    {
                        changes[RemnantType.Empathy] = toneAmount;
                        changes[RemnantType.Need] = toneAmount * 0.75f;
                        changes[RemnantType.Resolve] = -toneAmount * 0.5f;
                    }
                    else
                    {
                        changes[RemnantType.Empathy] = toneAmount;
                        changes[RemnantType.Need] = toneAmount * 0.75f;
                        changes[RemnantType.Resolve] = -toneAmount * 0.5f;
                    }
                    break;

                case ToneType.Courage:
                    if (toneAmount > 0)
                    {
                        changes[RemnantType.Resolve] = toneAmount;
                        changes[RemnantType.Authority] = toneAmount * 0.75f;
                        changes[RemnantType.Nuance] = -toneAmount * 0.75f;
                        changes[RemnantType.Empathy] = -toneAmount * 0.5f;
                    }
                    else
                    {
                        changes[RemnantType.Resolve] = toneAmount;
                        changes[RemnantType.Authority] = toneAmount * 0.75f;
                        changes[RemnantType.Nuance] = -toneAmount * 0.75f;
                        changes[RemnantType.Empathy] = -toneAmount * 0.5f;
                    }
                    break;

                case ToneType.Wisdom:
                    if (toneAmount > 0)
                    {
                        changes[RemnantType.Memory] = toneAmount;
                        changes[RemnantType.Nuance] = toneAmount * 0.75f;
                        changes[RemnantType.Skepticism] = -toneAmount * 0.5f;
                    }
                    else
                    {
                        changes[RemnantType.Memory] = toneAmount;
                        changes[RemnantType.Nuance] = toneAmount * 0.75f;
                        changes[RemnantType.Skepticism] = -toneAmount * 0.5f;
                    }
                    break;
            }

            // Apply correlation changes without cascading (avoid double-cascade)
            if (changes.Count > 0)
            {
                ApplyRemnantChangesDirectly(npcId, changes);
            }
        }
    }

    /// <summary>
    /// Apply resonance changes to specific NPCs.
    /// Converts resonance dict into REMNANTS changes.
    /// Positive resonance increases Trust/Empathy.
    /// Negative resonance increases Skepticism/decreases Trust.
    /// Then cascades through influence_map.
    /// </summary>
    public void ApplyNpcResonance(string activeNpcId, Dictionary<string, float> resonanceDict)
    {
        foreach (var kvp in resonanceDict)
        {
            string targetNpcId = kvp.Key;
            float resonanceAmount = kvp.Value;

            if (resonanceAmount == 0) continue;

            // Convert resonance to REMNANTS changes
            var remnantChanges = new Dictionary<RemnantType, float>();

            if (resonanceAmount > 0)
            {
                // Positive resonance: trust and openness
                remnantChanges[RemnantType.Trust] = resonanceAmount;
                remnantChanges[RemnantType.Empathy] = resonanceAmount * 0.3f;
                remnantChanges[RemnantType.Skepticism] = -resonanceAmount * 0.2f;
            }
            else
            {
                // Negative resonance: distrust and caution
                remnantChanges[RemnantType.Trust] = resonanceAmount;
                remnantChanges[RemnantType.Skepticism] = -resonanceAmount * 0.3f;
                remnantChanges[RemnantType.Empathy] = resonanceAmount * 0.2f;
            }

            Debug.Log($"[StatManager] Applying resonance to {targetNpcId}: {resonanceAmount}");
            CascadeRemnantChanges(targetNpcId, remnantChanges);
        }
    }

    /// <summary>
    /// Cascade REMNANTS changes to target NPC and propagate through influence_map.
    /// 
    /// Flow:
    /// 1. Apply changes directly to target NPC (clamped 0.1-0.9)
    /// 2. For each NPC influenced by target, apply influence multiplier
    /// 3. Recursively cascade to secondary NPCs
    /// </summary>
    public void CascadeRemnantChanges(string npcId, Dictionary<RemnantType, float> changes)
    {
        if (changes.Count == 0) return;
        if (!npcRemnants.ContainsKey(npcId))
        {
            Debug.LogWarning($"[StatManager] NPC {npcId} not found in REMNANTS");
            return;
        }

        Remnants remnants = npcRemnants[npcId];

        // Apply direct changes to target NPC
        foreach (var kvp in changes)
        {
            RemnantType traitType = kvp.Key;
            float delta = kvp.Value;

            float oldValue = remnants.Get(traitType);
            float newValue = Mathf.Clamp(oldValue + delta, 0.1f, 0.9f);
            remnants.Set(traitType, newValue);

            Debug.Log($"[StatManager] {npcId}.{traitType}: {oldValue:F2} → {newValue:F2} (Δ {delta:F2})");
        }

        // Propagate to influenced NPCs through influence_map
        if (influenceMap.ContainsKey(npcId))
        {
            foreach (var influencedKvp in influenceMap[npcId])
            {
                string influencedNpcId = influencedKvp.Key;
                float multiplier = influencedKvp.Value;

                if (!npcRemnants.ContainsKey(influencedNpcId))
                    continue;

                // Apply influence changes to influenced NPC
                var influencedChanges = new Dictionary<RemnantType, float>();
                foreach (var changeKvp in changes)
                {
                    // Apply multiplier to each change
                    influencedChanges[changeKvp.Key] = changeKvp.Value * multiplier;
                }

                Debug.Log($"[StatManager] Cascading from {npcId} to {influencedNpcId} (multiplier {multiplier})");
                ApplyRemnantChangesDirectly(influencedNpcId, influencedChanges);
            }
        }
    }

    /// <summary>
    /// Apply REMNANTS changes directly without further cascading.
    /// Used by correlation and direct influence application.
    /// </summary>
    private void ApplyRemnantChangesDirectly(string npcId, Dictionary<RemnantType, float> changes)
    {
        if (!npcRemnants.ContainsKey(npcId))
            return;

        Remnants remnants = npcRemnants[npcId];

        foreach (var kvp in changes)
        {
            RemnantType traitType = kvp.Key;
            float delta = kvp.Value;

            float oldValue = remnants.Get(traitType);
            float newValue = Mathf.Clamp(oldValue + delta, 0.1f, 0.9f);
            remnants.Set(traitType, newValue);
        }
    }

    /// <summary>
    /// Log an encounter to history after a dialogue choice.
    /// Matches the structure in npc_state.json history.
    /// </summary>
    public void LogEncounter(Dictionary<string, float> toneEffects)
    {
        encounterCount++;

        // Snapshot current NPC profiles
        var npcSnapshot = new Dictionary<string, NpcProfile>();
        foreach (var kvp in npcRemnants)
        {
            npcSnapshot[kvp.Key] = new NpcProfile
            {
                name = kvp.Key,
                remnants = kvp.Value.Clone()
            };
        }

        var record = new EncounterRecord
        {
            encounter = encounterCount,
            tone_effects = toneEffects,
            npc_profiles = npcSnapshot
        };

        history.Add(record);
        Debug.Log($"[StatManager] Encounter #{encounterCount} logged with {toneEffects.Count} tone effects");
    }

    // ========== PUBLIC ACCESSORS ==========

    public Dictionary<ToneType, float> GetPlayerTone()
    {
        return new Dictionary<ToneType, float>(playerTone);
    }

    public float GetPlayerTone(ToneType tone)
    {
        return playerTone.ContainsKey(tone) ? playerTone[tone] : 0f;
    }

    public Dictionary<string, Remnants> GetNpcRemnants()
    {
        // Return deep copy to prevent external modification
        var copy = new Dictionary<string, Remnants>();
        foreach (var kvp in npcRemnants)
        {
            copy[kvp.Key] = kvp.Value.Clone();
        }
        return copy;
    }

    public Remnants GetNpcRemnants(string npcId)
    {
        return npcRemnants.ContainsKey(npcId) ? npcRemnants[npcId].Clone() : null;
    }

    public Dictionary<string, Dictionary<string, float>> GetInfluenceMap()
    {
        return new Dictionary<string, Dictionary<string, float>>(influenceMap);
    }

    public List<EncounterRecord> GetHistory()
    {
        return new List<EncounterRecord>(history);
    }

    public int GetEncounterCount()
    {
        return encounterCount;
    }
}
