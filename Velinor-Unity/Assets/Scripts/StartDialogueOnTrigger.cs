using UnityEngine;

public class StartDialogueOnTrigger : MonoBehaviour
{
    [Header("Dialogue")]
    [SerializeField] private string npcId = "Kaelen";
    [SerializeField] private string startingPassageId = "kaelen_beat_1";
    [SerializeField] private string storyResourcePath = "velinor/stories/kaelen_confession_01";
    [SerializeField] private string requiredFlag = "completed_willy";
    [SerializeField] private bool requireFlag = true;

    [Header("Movement")]
    [SerializeField] private bool lockPlayerMovement = true;

    private bool hasTriggered;

    private void OnTriggerEnter(Collider other)
    {
        if (hasTriggered) return;
        if (!other.CompareTag("Player")) return;

        if (requireFlag && !GameFlags.Get(requiredFlag))
            return;

        hasTriggered = true;

        if (DialogueManager.Instance != null)
        {
            DialogueManager.Instance.StartDialogue(npcId, startingPassageId, storyResourcePath);
        }
    }
}
