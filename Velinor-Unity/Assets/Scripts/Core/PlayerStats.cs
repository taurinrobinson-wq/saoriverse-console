using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// PlayerStats: Tracks player TONE/REMNANTS emotional dimensions.
/// 
/// TONE (Player Emotional Stances):
/// - Trust (T): Openness, sincerity, grounded honesty
/// - Observation (O): Perceptive, analytical, detail-oriented
/// - Narrative Presence (N): Intuitive interconnectedness, emotional attunement
/// - Empathy (E): Emotional openness, compassion
/// 
/// REMNANTS (NPC Emotional Dimensions):
/// - Resolve: Firmness, conviction, backbone
/// - Empathy: Emotional openness, compassion
/// - Memory: Recall of past, context awareness
/// - Nuance: Subtlety, complexity, shades of gray
/// - Authority: Command presence, decisiveness
/// - Need: Vulnerability, desire for connection
/// - Trust: Confidence in others
/// - Skepticism: Doubt, caution, suspicion
/// </summary>
public class PlayerStats : MonoBehaviour
{
    // TONE stats (0-1 scale)
    public float TrustTone = 0.5f;
    public float ObservationTone = 0.5f;
    public float NarrativeTone = 0.5f;
    public float EmpathyTone = 0.5f;

    // REMNANTS (affected by player choices)
    public float Resolve = 0.5f;
    public float Empathy = 0.5f;
    public float Memory = 0.5f;
    public float Nuance = 0.5f;
    public float Authority = 0.5f;
    public float Need = 0.5f;
    public float Trust = 0.5f;
    public float Skepticism = 0.5f;

    private static PlayerStats instance;

    void Awake()
    {
        if (instance == null)
        {
            instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    public static PlayerStats Get()
    {
        if (instance == null)
        {
            GameObject obj = new GameObject("PlayerStats");
            instance = obj.AddComponent<PlayerStats>();
        }
        return instance;
    }

    /// <summary>
    /// Apply TONE effects to player REMNANTS.
    /// Effects are normalized additions to prevent values going out of bounds.
    /// </summary>
    public void ApplyToneEffect(string toneName, Dictionary<string, float> effects)
    {
        foreach (var kvp in effects)
        {
            ApplyRemnantEffect(kvp.Key, kvp.Value);
        }
    }

    void ApplyRemnantEffect(string remnantName, float delta)
    {
        switch (remnantName)
        {
            case "Resolve": Resolve = Mathf.Clamp01(Resolve + delta * 0.1f); break;
            case "Empathy": Empathy = Mathf.Clamp01(Empathy + delta * 0.1f); break;
            case "Memory": Memory = Mathf.Clamp01(Memory + delta * 0.1f); break;
            case "Nuance": Nuance = Mathf.Clamp01(Nuance + delta * 0.1f); break;
            case "Authority": Authority = Mathf.Clamp01(Authority + delta * 0.1f); break;
            case "Need": Need = Mathf.Clamp01(Need + delta * 0.1f); break;
            case "Trust": Trust = Mathf.Clamp01(Trust + delta * 0.1f); break;
            case "Skepticism": Skepticism = Mathf.Clamp01(Skepticism + delta * 0.1f); break;
        }
    }

    public float GetRemnant(string remnantName)
    {
        return remnantName switch
        {
            "Resolve" => Resolve,
            "Empathy" => Empathy,
            "Memory" => Memory,
            "Nuance" => Nuance,
            "Authority" => Authority,
            "Need" => Need,
            "Trust" => Trust,
            "Skepticism" => Skepticism,
            _ => 0f
        };
    }
}
