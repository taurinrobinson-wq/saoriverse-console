using UnityEngine;
using System.Collections.Generic;
using System.Linq;
using TMPro;

/// <summary>
/// MalrikDialogueSequence: Loads and manages Malrik's complete story arc from JSON.
/// Supports multi-act progression with gate-based dialogue unlocking.
/// 
/// Story Structure:
/// - Act 1-3: Pre-collapse (discovered through dialogue)
/// - Act 4: The cataclysm (narrated)
/// - Act 5-8: Post-collapse reunion (playable)
/// 
/// Gates:
/// - TONE-based (empathy, observation, trust, narrative presence)
/// - Story gates (prior segments completed)
/// - Coherence gates (emotional integration)
/// - Influence gates (relationship with Malrik)
/// </summary>
[System.Serializable]
public class MalrikStoryData
{
    public string npc;
    public string npcFullName;
    public string storyTitle;
    public List<MalrikAct> acts = new List<MalrikAct>();
}

[System.Serializable]
public class MalrikAct
{
    public int actNumber;
    public string actTitle;
    public string timeframe;
    public string emotionalTheme;
    public List<MalrikSegment> segments = new List<MalrikSegment>();
}

[System.Serializable]
public class MalrikSegment
{
    public string segmentId;
    public int act;
    public string title;
    public string npcLine;
    public List<DialogueGate> requiredGates = new List<DialogueGate>();
    public List<DialogueChoice> choices = new List<DialogueChoice>();
    public string emotionalTheme;
    public bool completedByPlayer = false;
}

public class MalrikDialogueSequence : MonoBehaviour
{
    private static MalrikStoryData storyData;
    private DialogueGateEvaluator gateEvaluator;
    private int currentActIndex = 0;
    private int currentSegmentIndex = 0;
    private Dictionary<string, MalrikSegment> segmentMap = new Dictionary<string, MalrikSegment>();

    void Awake()
    {
        LoadStoryData();
        gateEvaluator = GetComponent<DialogueGateEvaluator>() ?? gameObject.AddComponent<DialogueGateEvaluator>();
    }

    private void LoadStoryData()
    {
        // Load JSON from Resources/Dialogue/MalrikStoryGates.json
        TextAsset jsonFile = Resources.Load<TextAsset>("Dialogue/MalrikStoryGates");
        if (jsonFile != null)
        {
            storyData = JsonUtility.FromJson<MalrikStoryData>(jsonFile.text);
            Debug.Log($"✅ Loaded Malrik story: {storyData.storyTitle} with {storyData.acts.Count} acts");
            
            // Build segment map for quick lookup
            foreach (var act in storyData.acts)
            {
                foreach (var segment in act.segments)
                {
                    segmentMap[segment.segmentId] = segment;
                }
            }
        }
        else
        {
            Debug.LogError("❌ Failed to load MalrikStoryGates.json from Resources/Dialogue/");
        }
    }

    /// <summary>
    /// Get available dialogue segments for current state
    /// </summary>
    public List<MalrikSegment> GetAvailableSegments(PlayerStats playerStats, NPCInteraction npc, string npcName = "Malrik")
    {
        var available = new List<MalrikSegment>();

        if (storyData == null)
        {
            Debug.LogWarning("⚠️ Story data not loaded");
            return available;
        }

        // Find all segments where gates are open
        foreach (var act in storyData.acts)
        {
            foreach (var segment in act.segments)
            {
                if (gateEvaluator.CanAccessDialogue(segment, playerStats, npc, npcName))
                {
                    available.Add(segment);
                }
            }
        }

        return available;
    }

    /// <summary>
    /// Get a specific segment by ID
    /// </summary>
    public MalrikSegment GetSegment(string segmentId)
    {
        return segmentMap.ContainsKey(segmentId) ? segmentMap[segmentId] : null;
    }

    /// <summary>
    /// Get next available segment after current one
    /// </summary>
    public MalrikSegment GetNextSegment(string currentSegmentId, PlayerStats playerStats, NPCInteraction npc)
    {
        var available = GetAvailableSegments(playerStats, npc);

        if (available.Count == 0)
            return null;

        // Find current segment in available list
        var currentIdx = available.FindIndex(s => s.segmentId == currentSegmentId);

        // Return next available if exists
        if (currentIdx >= 0 && currentIdx < available.Count - 1)
        {
            return available[currentIdx + 1];
        }

        // Or first available if starting fresh
        return available.Count > 0 ? available[0] : null;
    }

    /// <summary>
    /// Get all segments in a specific act
    /// </summary>
    public List<MalrikSegment> GetActSegments(int actNumber)
    {
        var segments = new List<MalrikSegment>();

        if (storyData == null) return segments;

        var act = storyData.acts.FirstOrDefault(a => a.actNumber == actNumber);
        if (act != null)
        {
            segments.AddRange(act.segments);
        }

        return segments;
    }

    /// <summary>
    /// Mark a segment as completed
    /// </summary>
    public void CompleteSegment(string segmentId)
    {
        if (segmentMap.ContainsKey(segmentId))
        {
            segmentMap[segmentId].completedByPlayer = true;
            gateEvaluator.MarkSegmentComplete(segmentId);
            Debug.Log($"✨ Completed: {segmentId}");
        }
    }

    /// <summary>
    /// Get story progress percentage
    /// </summary>
    public float GetProgressPercentage()
    {
        if (storyData == null) return 0f;

        int totalSegments = storyData.acts.Sum(a => a.segments.Count);
        int completedSegments = storyData.acts.Sum(a => a.segments.Count(s => s.completedByPlayer));

        return totalSegments > 0 ? (completedSegments / (float)totalSegments) : 0f;
    }

    /// <summary>
    /// Get story summary
    /// </summary>
    public string GetStorySummary()
    {
        return storyData != null ? $"{storyData.npcFullName}: {storyData.storyTitle}" : "Story not loaded";
    }

    public static MalrikStoryData GetStoryData()
    {
        return storyData;
    }
}
