using UnityEngine;
using System;
using System.Collections.Generic;
using System.Linq;

public enum ToneType { Trust, Observation, NarrativePresence, Empathy }
public enum RemnantType { Resolve, Empathy, Memory, Nuance, Authority, Need, Trust, Skepticism }

[Serializable]
public class Remnants
{
    public float resolve = 0.5f, empathy = 0.5f, memory = 0.5f, nuance = 0.5f;
    public float authority = 0.5f, need = 0.5f, trust = 0.5f, skepticism = 0.5f;

    public float Get(RemnantType t) => t switch {
        RemnantType.Resolve => resolve, RemnantType.Empathy => empathy, RemnantType.Memory => memory,
        RemnantType.Nuance => nuance, RemnantType.Authority => authority, RemnantType.Need => need,
        RemnantType.Trust => trust, RemnantType.Skepticism => skepticism, _ => 0f
    };

    public void Set(RemnantType t, float v) {
        float val = Mathf.Clamp(v, 0.1f, 0.9f);
        switch (t) {
            case RemnantType.Resolve: resolve = val; break;
            case RemnantType.Empathy: empathy = val; break;
            case RemnantType.Memory: memory = val; break;
            case RemnantType.Nuance: nuance = val; break;
            case RemnantType.Authority: authority = val; break;
            case RemnantType.Need: need = val; break;
            case RemnantType.Trust: trust = val; break;
            case RemnantType.Skepticism: skepticism = val; break;
        }
    }
    public Remnants Clone() => (Remnants)this.MemberwiseClone();
}

[Serializable]
public class NpcProfile 
{ 
    public string name; 
    public int npcTier = 2;  // 1=Tier1 (0.03), 2=Tier2 (0.02), 3=Tier3 (0.01)
    public Remnants remnants; 
}

public class StatManager : MonoBehaviour
{
    public static StatManager Instance { get; private set; }

    // Player TONE properties synced with the playerTone dictionary
    public float toneTrust { get => playerTone[ToneType.Trust]; set => playerTone[ToneType.Trust] = value; }
    public float toneObservation { get => playerTone[ToneType.Observation]; set => playerTone[ToneType.Observation] = value; }
    public float toneNarrativePresence { get => playerTone[ToneType.NarrativePresence]; set => playerTone[ToneType.NarrativePresence] = value; }
    public float toneEmpathy { get => playerTone[ToneType.Empathy]; set => playerTone[ToneType.Empathy] = value; }

    // Saori REMNANTS properties synced with npcRemnants dictionary
    public float saoriTrust { get => GetSaoriRemnant(RemnantType.Trust); set => SetSaoriRemnant(RemnantType.Trust, value); }
    public float saoriResolve { get => GetSaoriRemnant(RemnantType.Resolve); set => SetSaoriRemnant(RemnantType.Resolve, value); }
    public float saoriSkepticism { get => GetSaoriRemnant(RemnantType.Skepticism); set => SetSaoriRemnant(RemnantType.Skepticism, value); }
    public float saoriNuance { get => GetSaoriRemnant(RemnantType.Nuance); set => SetSaoriRemnant(RemnantType.Nuance, value); }
    public float saoriMemory { get => GetSaoriRemnant(RemnantType.Memory); set => SetSaoriRemnant(RemnantType.Memory, value); }
    public float saoriAuthority { get => GetSaoriRemnant(RemnantType.Authority); set => SetSaoriRemnant(RemnantType.Authority, value); }
    public float saoriEmpathy { get => GetSaoriRemnant(RemnantType.Empathy); set => SetSaoriRemnant(RemnantType.Empathy, value); }
    public float saoriNeed { get => GetSaoriRemnant(RemnantType.Need); set => SetSaoriRemnant(RemnantType.Need, value); }

    private float GetSaoriRemnant(RemnantType t)
    {
        if (npcRemnants.TryGetValue("Saori", out var r)) return r.Get(t);
        return 0.5f;
    }

    private void SetSaoriRemnant(RemnantType t, float val)
    {
        if (!npcRemnants.TryGetValue("Saori", out var r))
        {
            r = new Remnants();
            npcRemnants["Saori"] = r;
        }
        r.Set(t, val);
    }

    private Dictionary<ToneType, float> playerTone = new Dictionary<ToneType, float> {
        { ToneType.Trust, 0.5f }, { ToneType.Observation, 0.5f },
        { ToneType.NarrativePresence, 0.5f }, { ToneType.Empathy, 0.5f }
    };
    private Dictionary<string, Remnants> npcRemnants = new Dictionary<string, Remnants>();
    private Dictionary<string, int> npcTiers = new Dictionary<string, int>();  // NPC tier for drift magnitude
    private Dictionary<string, Dictionary<string, float>> influenceMap = new Dictionary<string, Dictionary<string, float>>();
    private Dictionary<string, Dictionary<string, float>> cascadingRelationships = new Dictionary<string, Dictionary<string, float>>();

    [Serializable]
    private class NpcStateJson
    {
        public Dictionary<string, NpcProfile> npc_profiles;
        public Dictionary<string, Dictionary<string, float>> influence_map;
    }

    private void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        if (Application.isPlaying) DontDestroyOnLoad(gameObject);
        LoadInitialState();
    }

    private void LoadInitialState()
    {
        npcRemnants["Saori"] = new Remnants();
        npcRemnants["Ravi"] = new Remnants();
        npcRemnants["Nima"] = new Remnants();
        
        // Default to Tier 2
        npcTiers["Saori"] = 1;
        npcTiers["Ravi"] = 1;
        npcTiers["Nima"] = 1;

        TextAsset stateAsset = Resources.Load<TextAsset>("velinor/data/npc_state");
        if (stateAsset != null)
        {
            try
            {
                var root = Newtonsoft.Json.JsonConvert.DeserializeObject<NpcStateJson>(stateAsset.text);
                if (root != null)
                {
                    if (root.npc_profiles != null)
                    {
                        foreach (var kvp in root.npc_profiles)
                        {
                            if (kvp.Value != null && kvp.Value.remnants != null)
                            {
                                npcRemnants[kvp.Key] = kvp.Value.remnants;
                                npcTiers[kvp.Key] = kvp.Value.npcTier;
                            }
                        }
                    }
                    if (root.influence_map != null)
                    {
                        influenceMap = root.influence_map;
                    }
                    Debug.Log($"[StatManager] Successfully loaded {npcRemnants.Count} NPC profiles and {influenceMap.Count} influence map nodes.");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[StatManager] Failed to deserialize npc_state: {e.Message}");
            }
        }
        else
        {
            Debug.LogError("[StatManager] npc_state.json not found in Resources/velinor/data/npc_state");
        }
        
        LoadCascadingRelationships();
    }

    public void ApplyTone(ToneType tone)
    {
        AdjustPlayerTone(tone, 0.01f, "Saori");
    }

    public void AdjustPlayerTone(ToneType tone, float amount, string activeNpcId)
    {
        playerTone[tone] = Mathf.Clamp01(playerTone[tone] + amount);
        foreach (var npc in npcRemnants.Keys) {
            // Use tier-based drift magnitude
            float driftMagnitude = GetDriftMagnitudeForNpc(npc) * amount;
            var r = npcRemnants[npc];
            switch (tone) {
                case ToneType.Trust:
                    r.Set(RemnantType.Trust, r.trust + driftMagnitude);
                    r.Set(RemnantType.Resolve, r.resolve + driftMagnitude);
                    r.Set(RemnantType.Skepticism, r.skepticism - driftMagnitude);
                    break;
                case ToneType.Observation:
                    r.Set(RemnantType.Nuance, r.nuance + driftMagnitude);
                    r.Set(RemnantType.Memory, r.memory + driftMagnitude);
                    r.Set(RemnantType.Authority, r.authority - driftMagnitude);
                    break;
                case ToneType.NarrativePresence:
                    r.Set(RemnantType.Authority, r.authority + driftMagnitude);
                    r.Set(RemnantType.Resolve, r.resolve + driftMagnitude);
                    r.Set(RemnantType.Nuance, r.nuance - driftMagnitude);
                    break;
                case ToneType.Empathy:
                    r.Set(RemnantType.Empathy, r.empathy + driftMagnitude);
                    r.Set(RemnantType.Need, r.need + driftMagnitude);
                    r.Set(RemnantType.Resolve, r.resolve - driftMagnitude);
                    break;
            }
        }
        
        // After drift, apply cascading influence to connected NPCs
        if (!string.IsNullOrEmpty(activeNpcId))
        {
            ApplyCascadingDrift(activeNpcId);
            CheckThresholds(activeNpcId);
        }
    }

    public void ApplyNpcResonance(string npcId, Dictionary<string, float> resonance)
    {
        foreach (var kvp in resonance) {
            string targetNpc = kvp.Key;
            float amount = kvp.Value;
            if (npcRemnants.TryGetValue(targetNpc, out var r)) {
                r.Set(RemnantType.Trust, r.trust + amount);
                if (influenceMap.TryGetValue(targetNpc, out var connections)) {
                    foreach (var conn in connections) {
                        string connectedNpc = conn.Key;
                        float multiplier = conn.Value;
                        if (npcRemnants.TryGetValue(connectedNpc, out var connRemnants)) {
                            float cascadedAmount = amount * multiplier;
                            connRemnants.Set(RemnantType.Trust, connRemnants.trust + cascadedAmount);
                            Debug.Log($"[StatManager] Cascaded resonance shift from {targetNpc} to {connectedNpc}: {cascadedAmount:F4} (multiplier: {multiplier})");
                        }
                    }
                }
            }
        }
    }

    public float GetPlayerTone(ToneType tone) => playerTone[tone];
    public Remnants GetNpcRemnants(string npcId) => npcRemnants.TryGetValue(npcId, out var r) ? r : null;
    
    private float GetDriftMagnitudeForNpc(string npcId)
    {
        if (!npcTiers.TryGetValue(npcId, out int tier)) tier = 2;
        return tier switch {
            1 => 0.03f,
            2 => 0.02f,
            3 => 0.01f,
            _ => 0.01f
        };
    }
    
    private void LoadCascadingRelationships()
    {
        TextAsset cascadeAsset = Resources.Load<TextAsset>("velinor/data/cascading_relationships");
        if (cascadeAsset != null)
        {
            try
            {
                cascadingRelationships = Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<string, Dictionary<string, float>>>(cascadeAsset.text);
                Debug.Log($"[StatManager] Loaded cascading relationships for {cascadingRelationships.Count} NPCs.");
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[StatManager] Failed to load cascading relationships: {e.Message}");
                cascadingRelationships = new Dictionary<string, Dictionary<string, float>>();
            }
        }
    }
    
    private void ApplyCascadingDrift(string interactedNpcName)
    {
        // Micro-drift: ±0.001f to connected NPCs
        if (!cascadingRelationships.TryGetValue(interactedNpcName, out var connections)) return;
        
        foreach (var conn in connections)
        {
            string connectedNpc = conn.Key;
            float amount = conn.Value * 0.001f;  // Cascading magnitude is always ±0.001
            
            if (npcRemnants.TryGetValue(connectedNpc, out var r))
            {
                r.Set(RemnantType.Trust, r.trust + amount);
                Debug.Log($"[StatManager] Cascading drift: {interactedNpcName} influenced {connectedNpc} by {amount:F4}");
            }
        }
    }
    
    private void CheckThresholds(string npcId)
    {
        if (npcId != "Nima") return;  // Only Nima has phase thresholds for now
        
        if (!npcRemnants.TryGetValue("Nima", out var nima)) return;
        
        // Phase 1: Guarded Grief (softening border)
        if (!GameFlags.Get("nima_phase1_soften") && 
            nima.skepticism <= 0.60f && nima.authority <= 0.60f && nima.nuance >= 0.67f)
        {
            GameFlags.Set("nima_phase1_soften", true);
            Debug.Log("[StatManager] THRESHOLD: Nima Phase 1 - Guarded Grief (softening)");
        }
        
        // Phase 2: Revelation (Ophina photo reveal)
        if (!GameFlags.Get("nima_phase2_photo") && 
            nima.skepticism <= 0.50f && nima.authority <= 0.40f && 
            nima.memory >= 0.65f && nima.need >= 0.87f)
        {
            GameFlags.Set("nima_phase2_photo", true);
            Debug.Log("[StatManager] THRESHOLD: Nima Phase 2 - Revelation (photo)");
        }
        
        // Phase 3: Release (able to leave marketplace)
        if (!GameFlags.Get("nima_phase3_release") && 
            nima.resolve >= 0.85f && nima.trust >= 0.60f && 
            nima.memory >= 0.70f && nima.skepticism <= 0.40f)
        {
            GameFlags.Set("nima_phase3_release", true);
            Debug.Log("[StatManager] THRESHOLD: Nima Phase 3 - Release (marketplace exit)");
        }
    }

    // History and logging placeholder
    public void LogEncounter(Dictionary<string, float> effects) {}
}

// LEGACY STUBS
public class PlayerStats : MonoBehaviour { public static PlayerStats Get() => null; public float GetRemnant(string s) => 0f; }
public class NPCStats : MonoBehaviour { public float Resolve, Empathy, Memory, Nuance, Authority, Need, Trust, Skepticism; public float GetRemnant(string s) => 0f; }
public class DialogueSegment { public string segmentId; public string npcLine; public bool completedByPlayer; public List<DialogueChoice> playerChoices; }
public class DialogueGateEvaluator : MonoBehaviour { public void MarkSegmentComplete(string s) {} }
public class MalrikDialogueSequence : MonoBehaviour { public void CompleteSegment(string s) {} }
public class ElenyaDialogueSequence : MonoBehaviour { public void CompleteSegment(string s) {} }
namespace VelinorGame.Core { public class ElenyaDialogueSequence : MonoBehaviour { public void CompleteSegment(string s) {} } }
