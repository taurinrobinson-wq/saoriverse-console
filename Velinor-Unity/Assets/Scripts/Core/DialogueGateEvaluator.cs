using UnityEngine;
using System.Collections.Generic;
using System.Linq;

/// <summary>
/// DialogueGateEvaluator: Evaluates whether a dialogue segment is accessible
/// based on player TONE stats, NPC influence, emotional gates, and story progression.
/// 
/// Gate Types:
/// - "tone_stat": Requires minimum TONE value (e.g., empathy >= 0.7)
/// - "influence": Requires minimum NPC relationship (e.g., malrik_influence >= 0.5)
/// - "story_gate": Requires prior dialogue segment completion (e.g., "met_at_lighthouse")
/// - "coherence": Requires emotional alignment (e.g., coherence >= 0.6)
/// - "signal_present": Requires emotional signal from player (advanced)
/// </summary>
[System.Serializable]
public class DialogueGate
{
    public string gateId;
    public string gateType;  // "tone_stat", "influence", "story_gate", "coherence", etc.
    public string requirement;  // e.g., "empathy", "malrik_influence", "completed_act1"
    public float threshold;  // Minimum value (0-1 scale)
    public string description;  // Human readable: "Player must have high empathy"
}

[System.Serializable]
public class DialogueSegment
{
    public string segmentId;
    public int act;
    public string title;
    public string npcLine;
    public List<DialogueGate> requiredGates = new List<DialogueGate>();
    public List<DialogueChoice> choices = new List<DialogueChoice>();
    public string emotionalTheme;  // "connection", "grief", "recognition", etc.
    public bool completedByPlayer = false;
}

public class DialogueGateEvaluator : MonoBehaviour
{
    private Dictionary<string, bool> completedSegments = new Dictionary<string, bool>();
    
    public bool CanAccessDialogue(DialogueSegment segment, PlayerStats playerStats, NPCInteraction npc, string npcName)
    {
        // Check all required gates
        foreach (var gate in segment.requiredGates)
        {
            if (!EvaluateGate(gate, playerStats, npc, npcName))
            {
                Debug.Log($"🚪 Gate locked: {gate.description}");
                return false;
            }
        }
        
        Debug.Log($"✅ All gates open for: {segment.title}");
        return true;
    }

    private bool EvaluateGate(DialogueGate gate, PlayerStats playerStats, NPCInteraction npc, string npcName)
    {
        switch (gate.gateType.ToLower())
        {
            case "tone_stat":
                return EvaluateToneStat(gate, playerStats);
                
            case "influence":
                return EvaluateInfluence(gate, npc, npcName);
                
            case "story_gate":
                return EvaluateStoryGate(gate);
                
            case "coherence":
                return EvaluateCoherence(gate, playerStats);
                
            default:
                return true;  // Unknown gate types pass by default
        }
    }

    private bool EvaluateToneStat(DialogueGate gate, PlayerStats playerStats)
    {
        float statValue = 0f;
        
        // Map stat names to player values
        switch (gate.requirement.ToLower())
        {
            case "empathy":
            case "empathytone":
                statValue = playerStats.EmpathyTone;
                break;
            case "trust":
            case "trusttone":
                statValue = playerStats.TrustTone;
                break;
            case "observation":
            case "observationtone":
                statValue = playerStats.ObservationTone;
                break;
            case "narrativepresence":
            case "narrativetone":
                statValue = playerStats.NarrativeTone;
                break;
        }
        
        bool passed = statValue >= gate.threshold;
        Debug.Log($"📊 Tone gate '{gate.requirement}': {statValue:F2} >= {gate.threshold} ? {passed}");
        return passed;
    }

    private bool EvaluateInfluence(DialogueGate gate, NPCInteraction npc, string npcName)
    {
        // This would pull from an Influence system tracking NPC relationships
        // For now, simplified: all NPCs start at 0.5
        float influence = 0.5f;  // TODO: Connect to actual influence tracking
        
        bool passed = influence >= gate.threshold;
        Debug.Log($"❤️ Influence gate with {npcName}: {influence:F2} >= {gate.threshold} ? {passed}");
        return passed;
    }

    private bool EvaluateStoryGate(DialogueGate gate)
    {
        // Check if prior dialogue segment was completed
        bool completed = completedSegments.ContainsKey(gate.requirement) && completedSegments[gate.requirement];
        Debug.Log($"📖 Story gate '{gate.requirement}' completed? {completed}");
        return completed;
    }

    private bool EvaluateCoherence(DialogueGate gate, PlayerStats playerStats)
    {
        // Coherence = how aligned TONE stats are (0-1 scale)
        float coherence = CalculateCoherence(playerStats);
        bool passed = coherence >= gate.threshold;
        Debug.Log($"⚖️ Coherence gate: {coherence:F2} >= {gate.threshold} ? {passed}");
        return passed;
    }

    private float CalculateCoherence(PlayerStats playerStats)
    {
        // Simple version: 1.0 when all TONE stats are equal
        // Lower when they diverge
        float empathy = playerStats.EmpathyTone;
        float trust = playerStats.TrustTone;
        float observation = playerStats.ObservationTone;
        float narrative = playerStats.NarrativeTone;
        
        float avg = (empathy + trust + observation + narrative) / 4f;
        float deviation = Mathf.Abs(empathy - avg) + Mathf.Abs(trust - avg) + Mathf.Abs(observation - avg) + Mathf.Abs(narrative - avg);
        float coherence = Mathf.Max(0f, 1f - (deviation / 4f));  // 0-1 range
        
        return coherence;
    }

    public void MarkSegmentComplete(string segmentId)
    {
        completedSegments[segmentId] = true;
        Debug.Log($"✨ Marked complete: {segmentId}");
    }

    public bool IsSegmentComplete(string segmentId)
    {
        return completedSegments.ContainsKey(segmentId) && completedSegments[segmentId];
    }
}
