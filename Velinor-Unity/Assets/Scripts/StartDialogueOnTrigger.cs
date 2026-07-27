using UnityEngine;
using StarterAssets;

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

        if (lockPlayerMovement)
        {
            var playerController = other.GetComponentInParent<VelinorPlayerController>();
            if (playerController != null)
            {
                playerController.enabled = false;
            }
        }

        if (DialogueManager.Instance != null)
        {
            DialogueManager.Instance.OnDialogueEnded -= HandleDialogueEnded;
            DialogueManager.Instance.OnDialogueEnded += HandleDialogueEnded;
            DialogueManager.Instance.StartDialogue(npcId, startingPassageId, storyResourcePath);
        }
    }

    private void HandleDialogueEnded()
    {
        if (lockPlayerMovement)
        {
            var player = GameObject.FindGameObjectWithTag("Player");
            if (player != null)
            {
                var playerController = player.GetComponentInChildren<VelinorPlayerController>();
                if (playerController != null)
                {
                    playerController.enabled = true;
                }
            }
        }

        if (DialogueManager.Instance != null)
        {
            DialogueManager.Instance.OnDialogueEnded -= HandleDialogueEnded;
        }
    }
}
