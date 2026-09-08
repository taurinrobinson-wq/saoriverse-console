using UnityEngine;
using Velinor.Core;

namespace Velinor.Core
{
    /// <summary>
    /// Simple wrapper to allow OnClick listeners to trigger NPC dialogue.
    /// Just add this to your NPC Canvas and set the fields in Inspector.
    /// </summary>
    public class NPCDialogueTrigger : MonoBehaviour
    {
        [SerializeField]
        [Tooltip("The NPC ID (e.g., 'Saori', 'Ravi', 'Nima')")]
        private string npcId = "Saori";

        [SerializeField]
        [Tooltip("The starting passage ID in the story JSON")]
        private string startPassageId = "market_entry";

        [SerializeField]
        [Tooltip("Path to story JSON file (leave empty for default)")]
        private string storyPath = "";

        /// <summary>
        /// Call this from OnClick listener - no parameters needed!
        /// </summary>
        public void TriggerDialogue()
        {
            if (DialogueManager.Instance == null)
            {
                Debug.LogError("[NPCDialogueTrigger] DialogueManager not found in scene!");
                return;
            }

            if (string.IsNullOrEmpty(storyPath))
            {
                DialogueManager.Instance.StartDialogue(npcId, startPassageId);
            }
            else
            {
                DialogueManager.Instance.StartDialogue(npcId, startPassageId, storyPath);
            }

            Debug.Log($"[NPCDialogueTrigger] Started dialogue with {npcId}, passage: {startPassageId}");
        }
    }
}
