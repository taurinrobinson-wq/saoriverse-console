using UnityEngine;
using UnityEngine.UI;
using System.Collections;

public class SaoriIntro : MonoBehaviour
{
    [SerializeField] private float interactionDistance = 5f;
    
    private GameObject player;
    private bool hasTriggered = false;
    private bool dialogueActive = false;
    private Canvas dialogueCanvas;

    private void Start()
    {
        player = GameObject.FindGameObjectWithTag("Player");
        CreateDialogueCanvas();
    }

    private void Update()
    {
        if (player == null || hasTriggered) return;

        float distance = Vector3.Distance(transform.position, player.transform.position);
        
        if (distance < interactionDistance && !dialogueActive)
        {
            StartCoroutine(PlayIntroDialogue());
        }
    }

    private IEnumerator PlayIntroDialogue()
    {
        dialogueActive = true;
        hasTriggered = true;

        // Show Saori dialogue
        ShowDialogue("Saori: You look lost. This is yours now.", 2f);
        yield return new WaitForSeconds(2.5f);

        // Hand over codex device
        ShowDialogue("Saori: Use it wisely.", 1.5f);
        yield return new WaitForSeconds(2f);

        // Saori walks away
        StartCoroutine(WalkAway());
        
        yield return new WaitForSeconds(1f);

        // Show prompt for device
        ShowDialogue("Press 'G' to use the Codex Device", 3f);
        yield return new WaitForSeconds(3f);

        // Clean up dialogue
        HideDialogue();
        dialogueActive = false;
    }

    private IEnumerator WalkAway()
    {
        float duration = 3f;
        float elapsed = 0f;
        Vector3 startPos = transform.position;
        Vector3 endPos = startPos + Vector3.forward * 10f;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            transform.position = Vector3.Lerp(startPos, endPos, elapsed / duration);
            yield return null;
        }

        // Destroy Saori after walking away
        yield return new WaitForSeconds(1f);
        Destroy(gameObject);
    }

    private void CreateDialogueCanvas()
    {
        GameObject canvasObj = new GameObject("DialogueCanvas");
        dialogueCanvas = canvasObj.AddComponent<Canvas>();
        dialogueCanvas.renderMode = RenderMode.ScreenSpaceOverlay;

        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);

        // Create dialogue text
        GameObject textObj = new GameObject("DialogueText");
        textObj.transform.SetParent(canvasObj.transform, false);
        
        Text text = textObj.AddComponent<Text>();
        text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        text.fontSize = 36;
        text.alignment = TextAnchor.MiddleCenter;
        text.color = Color.white;

        RectTransform textRect = textObj.GetComponent<RectTransform>();
        textRect.anchorMin = Vector2.zero;
        textRect.anchorMax = Vector2.one;
        textRect.offsetMin = Vector2.zero;
        textRect.offsetMax = Vector2.zero;

        // Add outline/shadow for readability
        Shadow shadow = textObj.AddComponent<Shadow>();
        shadow.effectColor = Color.black;
        shadow.effectDistance = new Vector2(2, -2);

        // Store reference
        textObj.name = "DialogueText";
    }

    private void ShowDialogue(string message, float duration)
    {
        Canvas canvas = FindAnyObjectByType<Canvas>();
        if (canvas == null) return;

        Text dialogueText = canvas.GetComponentInChildren<Text>();
        if (dialogueText != null)
        {
            dialogueText.text = message;
            dialogueText.enabled = true;
        }
    }

    private void HideDialogue()
    {
        Canvas canvas = FindAnyObjectByType<Canvas>();
        if (canvas == null) return;

        Text dialogueText = canvas.GetComponentInChildren<Text>();
        if (dialogueText != null)
        {
            dialogueText.enabled = false;
        }
    }
}
