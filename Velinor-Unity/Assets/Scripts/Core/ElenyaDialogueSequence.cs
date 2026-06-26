using UnityEngine;
using System.Collections.Generic;
using UnityEngine.Networking;
using System.Collections;

namespace VelinorGame.Core
{
    /// <summary>
    /// Manages Elenya's complete 8-act story arc with gate-based progression.
    /// Loads story data from ElenyaStoryGates.json and tracks dialogue segment completion.
    /// </summary>
    public class ElenyaDialogueSequence : MonoBehaviour
    {
        [System.Serializable]
        public class ElenyaStoryData
        {
            public string npc;
            public string npcFullName;
            public string storyTitle;
            public string storylineType;
            public string description;
            public List<ElenyaAct> acts;
            public List<ElenyaEpilogueMoment> epilogueMoments;
        }

        [System.Serializable]
        public class ElenyaAct
        {
            public int actNumber;
            public string actTitle;
            public string timeframe;
            public string emotionalTheme;
            public string description;
            public List<ElenyaSegment> segments;
        }

        [System.Serializable]
        public class ElenyaSegment
        {
            public string segmentId;
            public string title;
            public string dialogueContext;
            public string npcLine;
            public List<DialogueGate> requiredGates;
            public List<string> emotionalSignals;
            public string elenyaTone;
            public List<ElenyaChoice> playerChoices;
        }

        [System.Serializable]
        public class ElenyaChoice
        {
            public string toneId;
            public char toneType;
            public string toneName;
            public string playerLine;
            public string elenyaResponse;
            public Dictionary<string, float> statEffects;
            public List<string> unlocksGates;
        }

        [System.Serializable]
        public class ElenyaEpilogueMoment
        {
            public string momentId;
            public string description;
            public string trigger;
            public List<string> emotionalSignals;
            public string elenyaLine;
        }

        [SerializeField] private string storyJsonPath = "Dialogue/ElenyaStoryGates";
        private ElenyaStoryData storyData;
        private Dictionary<string, bool> completedSegments = new Dictionary<string, bool>();
        private Dictionary<string, ElenyaSegment> segmentMap = new Dictionary<string, ElenyaSegment>();

        private void Start()
        {
            LoadStoryData();
        }

        /// <summary>
        /// Load story data from JSON resource file.
        /// </summary>
        public void LoadStoryData()
        {
            TextAsset jsonAsset = Resources.Load<TextAsset>(storyJsonPath);
            if (jsonAsset == null)
            {
                Debug.LogError($"Failed to load story JSON at {storyJsonPath}");
                return;
            }

            try
            {
                storyData = JsonUtility.FromJson<ElenyaStoryData>(jsonAsset.text);
                BuildSegmentMap();
                Debug.Log($"✅ Loaded {storyData.npc} story: {storyData.storyTitle}");
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"Failed to parse Elenya story JSON: {ex.Message}");
            }
        }

        /// <summary>
        /// Build map of all segments by ID for quick lookup.
        /// </summary>
        private void BuildSegmentMap()
        {
            if (storyData?.acts == null)
                return;

            foreach (var act in storyData.acts)
            {
                if (act.segments != null)
                {
                    foreach (var segment in act.segments)
                    {
                        segmentMap[segment.segmentId] = segment;
                        completedSegments[segment.segmentId] = false;
                    }
                }
            }
        }

        /// <summary>
        /// Get all dialogue segments available to player given current game state.
        /// </summary>
        public List<ElenyaSegment> GetAvailableSegments(PlayerStats playerStats, NPCInteraction npc, string npcName)
        {
            var available = new List<ElenyaSegment>();
            if (storyData?.acts == null)
                return available;

            var gateEvaluator = GetComponent<DialogueGateEvaluator>();
            if (gateEvaluator == null)
                gateEvaluator = gameObject.AddComponent<DialogueGateEvaluator>();

            foreach (var act in storyData.acts)
            {
                if (act.segments != null)
                {
                    foreach (var segment in act.segments)
                    {
                        if (gateEvaluator.CanAccessDialogue(segment, playerStats, npc, npcName))
                        {
                            available.Add(segment);
                        }
                    }
                }
            }

            return available;
        }

        /// <summary>
        /// Get specific segment by ID.
        /// </summary>
        public ElenyaSegment GetSegment(string segmentId)
        {
            if (segmentMap.ContainsKey(segmentId))
                return segmentMap[segmentId];

            Debug.LogWarning($"Segment not found: {segmentId}");
            return null;
        }

        /// <summary>
        /// Get next available segment after current one.
        /// </summary>
        public ElenyaSegment GetNextSegment(string currentSegmentId, PlayerStats playerStats, NPCInteraction npc)
        {
            var available = GetAvailableSegments(playerStats, npc, storyData.npc);
            
            if (available.Count == 0)
                return null;

            // Return first available segment not yet shown
            foreach (var segment in available)
            {
                if (!completedSegments[segment.segmentId])
                    return segment;
            }

            return null;
        }

        /// <summary>
        /// Get all segments in a specific act.
        /// </summary>
        public List<ElenyaSegment> GetActSegments(int actNumber)
        {
            var actSegments = new List<ElenyaSegment>();
            if (storyData?.acts == null)
                return actSegments;

            foreach (var act in storyData.acts)
            {
                if (act.actNumber == actNumber && act.segments != null)
                {
                    actSegments.AddRange(act.segments);
                    break;
                }
            }

            return actSegments;
        }

        /// <summary>
        /// Mark a segment as completed, unlocking future gates.
        /// </summary>
        public void CompleteSegment(string segmentId)
        {
            if (completedSegments.ContainsKey(segmentId))
            {
                completedSegments[segmentId] = true;
                
                var gateEvaluator = GetComponent<DialogueGateEvaluator>();
                if (gateEvaluator != null)
                {
                    gateEvaluator.MarkSegmentComplete(segmentId);
                }

                Debug.Log($"📖 Elenya segment completed: {segmentId}");
            }
        }

        /// <summary>
        /// Check if segment is marked as completed.
        /// </summary>
        public bool IsSegmentComplete(string segmentId)
        {
            if (completedSegments.ContainsKey(segmentId))
                return completedSegments[segmentId];

            return false;
        }

        /// <summary>
        /// Get overall story progress percentage.
        /// </summary>
        public float GetProgressPercentage()
        {
            if (completedSegments.Count == 0)
                return 0f;

            int completed = 0;
            foreach (var kvp in completedSegments)
            {
                if (kvp.Value)
                    completed++;
            }

            return (float)completed / completedSegments.Count;
        }

        /// <summary>
        /// Get human-readable story summary.
        /// </summary>
        public string GetStorySummary()
        {
            if (storyData == null)
                return "Story not loaded";

            return $"{storyData.npcFullName}: {storyData.storyTitle} ({GetProgressPercentage():P0} complete)";
        }

        /// <summary>
        /// Static accessor for story data.
        /// </summary>
        public ElenyaStoryData GetStoryData()
        {
            return storyData;
        }
    }
}
