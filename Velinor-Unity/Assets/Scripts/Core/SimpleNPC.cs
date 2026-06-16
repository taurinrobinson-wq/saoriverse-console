using UnityEngine;
using Velinor.Core;

public class SimpleNPC : MonoBehaviour, IInteractable
{
    public string npcName = "Tala";

    public void Interact(GameObject player)
    {
        Debug.Log($"Interacting with {npcName}");
        
        // Hardcoded test dialogue
        var sequence = new DialogueSequence
        {
            sequenceId = "test_dialogue",
            npcName = npcName,
            lines = new System.Collections.Generic.List<DialogueLine>
            {
                new DialogueLine 
                { 
                    speakerId = npcName, 
                    text = "Hello, stranger. I am Tala.",
                    emotionalTags = new System.Collections.Generic.List<string> { "Trust" }
                },
                new DialogueLine 
                { 
                    speakerId = npcName, 
                    text = "My daughter was lost in the Collapse.",
                    emotionalTags = new System.Collections.Generic.List<string> { "Grief" }
                },
                new DialogueLine 
                { 
                    speakerId = npcName, 
                    text = "Do you remember what it was like before?",
                    emotionalTags = new System.Collections.Generic.List<string>()
                }
            }
        };

        DialogueManager.Instance.StartDialogue(sequence);
    }
}
