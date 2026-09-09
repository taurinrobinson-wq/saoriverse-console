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
        [Tooltip("The dialogue JSON file to load")]
        private TextAsset dialogueJson;  // REQUIRED - must be assigned in Inspector

        [SerializeField]
        [Tooltip("The NPC ID (e.g., 'Saori', 'Ravi', 'Nima')")]
        private string npcId = "Saori";

        [SerializeField]
        [Tooltip("The starting beat ID in the story JSON (e.g., 'beat_1', 'desert_intro')")]
        private string startBeatId = "beat_1";

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

            if (dialogueJson == null)
            {
                Debug.LogError("[NPCDialogueTrigger] Dialogue JSON not assigned in Inspector!");
                return;
            }

            // Load the dialogue JSON
            DialogueManager.Instance.LoadDialogue(dialogueJson);
            
            // Start dialogue at the specified beat
            DialogueManager.Instance.StartDialogue(npcId, startBeatId);

            Debug.Log($"[NPCDialogueTrigger] Started dialogue with {npcId}, beat: {startBeatId}");
        }
    }
}
