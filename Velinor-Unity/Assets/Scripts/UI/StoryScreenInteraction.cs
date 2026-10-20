using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Story Screen Interaction System
/// 
/// Handles the "Press E to activate" interaction for story sequence screens in caves.
/// Mirrors the Triglyph Puzzle system but opens Codex to Mind Logs page + story screen image.
/// 
/// Usage:
/// 1. Attach to a collider in the scene (the interactive screen area)
/// 2. Assign the storyScreenImage in the Inspector
/// 3. Assign the dialogueJsonFileName (e.g., "story_1_sequence")
/// 4. When player presses E, Codex opens + screen image appears
/// </summary>
public class StoryScreenInteraction : MonoBehaviour
{
    [Header("UI Elements")]
    [SerializeField] private Image storyScreenImage; // The panel/image that displays the story screen
    [SerializeField] private CanvasGroup storyScreenCanvasGroup; // For fade effects
    [SerializeField] private float fadeInDuration = 0.5f;
    
    [Header("Audio")]
    [SerializeField] private AudioClip activationSound; // Optional: sound when screen activates
    
    [Header("Dialogue")]
    [SerializeField] private string dialogueJsonFileName; // e.g., "story_1_sequence"
    
    [Header("Codex")]
    [SerializeField] private bool openCodexOnActivation = true;
    [SerializeField] private CodexController codexController; // Reference to Codex system
    
    private bool isActivated = false;
    private bool playerInRange = false;
    private AudioSource audioSource;
    private DialogueManager dialogueManager;

    private void Start()
    {
        audioSource = GetComponent<AudioSource>();
        dialogueManager = FindObjectOfType<DialogueManager>();
        
        // Ensure screen is hidden initially
        if (storyScreenCanvasGroup)
        {
            storyScreenCanvasGroup.alpha = 0f;
        }
        else if (storyScreenImage)
        {
            storyScreenImage.gameObject.SetActive(false);
        }
    }

    private void Update()
    {
        if (playerInRange && Input.GetKeyDown(KeyCode.E) && !isActivated)
        {
            ActivateStoryScreen();
        }
    }

    private void OnTriggerEnter2D(Collider2D collision)
    {
        if (collision.CompareTag("Player"))
        {
            playerInRange = true;
            ShowActivationPrompt();
        }
    }

    private void OnTriggerExit2D(Collider2D collision)
    {
        if (collision.CompareTag("Player"))
        {
            playerInRange = false;
            HideActivationPrompt();
        }
    }

    /// <summary>
    /// Activates the story screen interaction.
    /// Opens Codex to Mind Logs page and displays the story screen image.
    /// </summary>
    public void ActivateStoryScreen()
    {
        if (isActivated) return;
        
        isActivated = true;
        Debug.Log($"Story screen activated: {dialogueJsonFileName}");
        
        // Play activation sound
        if (activationSound && audioSource)
        {
            audioSource.PlayOneShot(activationSound);
        }
        
        // Open Codex to Mind Logs page
        if (openCodexOnActivation)
        {
            OpenCodexToMindLogs();
        }
        
        // Show story screen image
        ShowStoryScreenImage();
        
        // Start dialogue sequence
        if (dialogueManager && !string.IsNullOrEmpty(dialogueJsonFileName))
        {
            dialogueManager.LoadAndStartDialogue(dialogueJsonFileName);
        }
    }

    /// <summary>
    /// Opens the Codex UI and navigates to Mind Logs page.
    /// </summary>
    private void OpenCodexToMindLogs()
    {
        if (codexController == null)
        {
            codexController = FindObjectOfType<CodexController>();
        }
        
        if (codexController)
        {
            codexController.OpenCodex();
            codexController.NavigateToPage("MindLogs"); // Adjust method name if needed
            Debug.Log("Codex opened to Mind Logs page.");
        }
        else
        {
            Debug.LogWarning("CodexController not found in scene!");
        }
    }

    /// <summary>
    /// Displays the story screen image with fade-in effect.
    /// </summary>
    private void ShowStoryScreenImage()
    {
        if (!storyScreenImage) return;
        
        if (storyScreenCanvasGroup)
        {
            storyScreenImage.gameObject.SetActive(true);
            StartCoroutine(FadeInImage(storyScreenCanvasGroup, fadeInDuration));
        }
        else
        {
            storyScreenImage.gameObject.SetActive(true);
        }
        
        Debug.Log("Story screen image displayed.");
    }

    /// <summary>
    /// Hides the story screen image (called when dialogue ends or cancelled).
    /// </summary>
    public void HideStoryScreenImage()
    {
        if (!storyScreenImage) return;
        
        if (storyScreenCanvasGroup)
        {
            StartCoroutine(FadeOutImage(storyScreenCanvasGroup, fadeInDuration));
        }
        else
        {
            storyScreenImage.gameObject.SetActive(false);
        }
        
        Debug.Log("Story screen image hidden.");
    }

    /// <summary>
    /// Shows the "Press E to activate" prompt.
    /// (Hook this into your UI notification system)
    /// </summary>
    private void ShowActivationPrompt()
    {
        // TODO: Display "Press E to activate" notification
        // Example: UIManager.ShowNotification("Press E to activate story screen");
        Debug.Log("[Notification] Press E to activate story screen");
    }

    /// <summary>
    /// Hides the activation prompt.
    /// </summary>
    private void HideActivationPrompt()
    {
        // TODO: Hide notification
        Debug.Log("[Notification Hidden]");
    }

    private System.Collections.IEnumerator FadeInImage(CanvasGroup canvasGroup, float duration)
    {
        canvasGroup.alpha = 0f;
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            canvasGroup.alpha = Mathf.Lerp(0f, 1f, elapsed / duration);
            yield return null;
        }
        
        canvasGroup.alpha = 1f;
    }

    private System.Collections.IEnumerator FadeOutImage(CanvasGroup canvasGroup, float duration)
    {
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            canvasGroup.alpha = Mathf.Lerp(1f, 0f, elapsed / duration);
            yield return null;
        }
        
        canvasGroup.alpha = 0f;
        storyScreenImage.gameObject.SetActive(false);
    }

    /// <summary>
    /// Called when dialogue sequence completes.
    /// Triggers scene transition (if needed).
    /// </summary>
    public void OnStorySequenceComplete(int storyNumber)
    {
        HideStoryScreenImage();
        
        // TODO: Trigger scene load via CaveStateManager
        // CaveStateManager.OnStorySequenceComplete(storyNumber);
        
        Debug.Log($"Story {storyNumber} sequence complete.");
    }
}
