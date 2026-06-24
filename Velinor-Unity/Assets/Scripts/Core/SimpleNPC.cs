using UnityEngine;

public class SimpleNPC : MonoBehaviour
{
    [SerializeField] private string npcId = "SimpleNPC";
    [SerializeField] private string startingPassageId = "simple_npc_dialogue";

    public void Interact()
    {
        if (DialogueManager.Instance != null)
        {
            DialogueManager.Instance.StartDialogue(npcId, startingPassageId);
        }
        else
        {
            Debug.LogError("[SimpleNPC] DialogueManager.Instance not found");
        }
    }
}
