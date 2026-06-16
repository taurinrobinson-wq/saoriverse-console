using System;
using System.Collections.Generic;
using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// Represents a single dialogue line with optional emotional effects.
    /// </summary>
    [System.Serializable]
    public class DialogueLine
    {
        public string speakerId; // NPC or "Player"
        public string text;
        public List<string> emotionalTags = new List<string>(); // Tags to add after this line
        public bool isChoice = false; // If true, player must choose a response
    }

    /// <summary>
    /// A dialogue choice that the player can select.
    /// </summary>
    [System.Serializable]
    public class DialogueChoice
    {
        public string choiceText;
        public List<string> emotionalTags = new List<string>(); // Tags added if player chooses this
        public int nextLineIndex; // Where to jump after this choice
    }

    /// <summary>
    /// A complete conversation sequence.
    /// Can be used for NPC interactions, environmental lore, etc.
    /// </summary>
    [System.Serializable]
    public class DialogueSequence
    {
        public string sequenceId;
        public string npcName;
        public List<DialogueLine> lines = new List<DialogueLine>();
        public List<DialogueChoice> choices = new List<DialogueChoice>();
    }

    /// <summary>
    /// Manages dialogue playback and emotional tag integration.
    /// </summary>
    public class DialogueManager : MonoBehaviour
    {
        public GameObject dialogueUIPanel;
        public TMPro.TextMeshProUGUI speakerNameText;
        public TMPro.TextMeshProUGUI dialogueText;
        public Transform choicesContainer;
        [SerializeField] private GameObject choiceButtonPrefab;

        private DialogueSequence currentSequence;
        private int currentLineIndex = 0;
        private bool isDisplayingDialogue = false;
        private float textRevealSpeed = 0.05f;

        public static DialogueManager Instance { get; private set; }

        // Events
        public event Action<DialogueSequence> OnDialogueStarted;
        public event Action<string> OnEmotionalTagTriggered;
        public event Action OnDialogueEnded;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            dialogueUIPanel.SetActive(false);
        }

        /// <summary>
        /// Starts a dialogue sequence.
        /// </summary>
        public void StartDialogue(DialogueSequence sequence)
        {
            if (isDisplayingDialogue)
                return;

            currentSequence = sequence;
            currentLineIndex = 0;
            isDisplayingDialogue = true;

            dialogueUIPanel.SetActive(true);
            OnDialogueStarted?.Invoke(sequence);

            DisplayCurrentLine();
        }

        /// <summary>
        /// Displays the current line in the sequence.
        /// </summary>
        private void DisplayCurrentLine()
        {
            if (currentLineIndex >= currentSequence.lines.Count)
            {
                EndDialogue();
                return;
            }

            DialogueLine currentLine = currentSequence.lines[currentLineIndex];
            speakerNameText.text = currentLine.speakerId;

            // Add emotional tags to Codex
            foreach (string tag in currentLine.emotionalTags)
            {
                CodexManager.Instance.AddEmotionalTag(tag);
                OnEmotionalTagTriggered?.Invoke(tag);
            }

            // Start revealing text
            StartCoroutine(RevealText(currentLine.text));
        }

        /// <summary>
        /// Reveals text character-by-character (typewriter effect).
        /// </summary>
        private System.Collections.IEnumerator RevealText(string fullText)
        {
            dialogueText.text = "";
            foreach (char c in fullText)
            {
                dialogueText.text += c;
                yield return new WaitForSeconds(textRevealSpeed);
            }

            // Wait before allowing next line or auto-advance
            yield return new WaitForSeconds(2f);
            
            if (Input.GetKeyDown(KeyCode.Space) || Input.GetMouseButtonDown(0))
            {
                NextLine();
            }
        }

        /// <summary>
        /// Displays choices if the current line has them.
        /// </summary>
        private void DisplayChoices()
        {
            DialogueLine currentLine = currentSequence.lines[currentLineIndex];
            if (!currentLine.isChoice || currentSequence.choices.Count == 0)
            {
                NextLine();
                return;
            }

            // Clear previous buttons
            foreach (Transform child in choicesContainer)
            {
                Destroy(child.gameObject);
            }

            // Create buttons for each choice
            foreach (DialogueChoice choice in currentSequence.choices)
            {
                GameObject buttonObj = Instantiate(choiceButtonPrefab, choicesContainer);
                var button = buttonObj.GetComponent<UnityEngine.UI.Button>();
                var buttonText = buttonObj.GetComponentInChildren<TMPro.TextMeshProUGUI>();

                buttonText.text = choice.choiceText;
                button.onClick.AddListener(() => SelectChoice(choice));
            }
        }

        /// <summary>
        /// Called when player selects a choice.
        /// </summary>
        private void SelectChoice(DialogueChoice choice)
        {
            // Add choice's emotional tags
            foreach (string tag in choice.emotionalTags)
            {
                CodexManager.Instance.AddEmotionalTag(tag);
                OnEmotionalTagTriggered?.Invoke(tag);
            }

            // Jump to next line
            currentLineIndex = choice.nextLineIndex;
            DisplayCurrentLine();
        }

        /// <summary>
        /// Advances to the next line.
        /// </summary>
        private void NextLine()
        {
            currentLineIndex++;
            if (currentLineIndex >= currentSequence.lines.Count)
            {
                EndDialogue();
            }
            else
            {
                DisplayCurrentLine();
            }
        }

        /// <summary>
        /// Ends the dialogue sequence.
        /// </summary>
        private void EndDialogue()
        {
            isDisplayingDialogue = false;
            dialogueUIPanel.SetActive(false);
            OnDialogueEnded?.Invoke();
        }

        /// <summary>
        /// Loads a dialogue sequence from JSON.
        /// </summary>
        public DialogueSequence LoadDialogueFromJSON(string json)
        {
            return UnityEngine.JsonUtility.FromJson<DialogueSequence>(json);
        }
    }
}
