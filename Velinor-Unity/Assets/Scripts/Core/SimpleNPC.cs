using UnityEngine;
using Velinor.Core;

public class SimpleNPC : MonoBehaviour
{
    [Header("Dialogue")]
    [SerializeField] private TextAsset dialogueJson;  // Must be assigned in Inspector
    [SerializeField] private string npcId = "SimpleNPC";
    [SerializeField] private string startBeatId = "beat_1";

    public void Interact()
    {
        if (DialogueManager.Instance != null)
        {
            // Load dialogue JSON if assigned
            if (dialogueJson != null)
            {
                DialogueManager.Instance.LoadDialogue(dialogueJson);
            }
            else
            {
                Debug.LogError("[SimpleNPC] Dialogue JSON not assigned in Inspector!");
                return;
            }

            DialogueManager.Instance.StartDialogue(npcId, startBeatId);
        }
        else
        {
            Debug.LogError("[SimpleNPC] DialogueManager.Instance not found");
        }
    }
}
