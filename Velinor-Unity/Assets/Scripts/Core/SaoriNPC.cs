using UnityEngine;
using TMPro;
using Velinor.Core;

namespace Velinor.Core
{
    public class SaoriNPC : MonoBehaviour, IInteractable
    {
        public string npcName = "Saori";
        public string dialogueText = "Welcome to the ruins. Be careful out there.";

        private GameObject dialogueCanvas;
        private TextMeshProUGUI nameText;
        private TextMeshProUGUI bodyText;
        private GameObject dialoguePanel;

        private void Start()
        {
            dialogueCanvas = GameObject.Find("DialogueCanvas");
            if (dialogueCanvas != null)
            {
                var panel = dialogueCanvas.transform.Find("DialoguePanel");
                if (panel != null)
                {
                    dialoguePanel = panel.gameObject;
                    nameText = panel.Find("NPCNameText")?.GetComponent<TextMeshProUGUI>();
                    bodyText = panel.Find("DialogueBodyText")?.GetComponent<TextMeshProUGUI>();
                }
            }
        }

        private void Update()
        {
            // Billboard effect - face the camera
            if (Camera.main != null)
            {
                transform.LookAt(Camera.main.transform);
                transform.rotation = Quaternion.Euler(0, transform.rotation.eulerAngles.y + 180, 0);
            }
        }

        public void Interact(GameObject player)
        {
            if (dialoguePanel != null)
            {
                dialoguePanel.SetActive(true);
                if (nameText != null) nameText.text = npcName;
                if (bodyText != null) bodyText.text = dialogueText;
                
                // For testing, hide it after 3 seconds
                CancelInvoke("HideDialogue");
                Invoke("HideDialogue", 3f);
            }
        }

        private void HideDialogue()
        {
            if (dialoguePanel != null)
                dialoguePanel.SetActive(false);
        }
    }
}
