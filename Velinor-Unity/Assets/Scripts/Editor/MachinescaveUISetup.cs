using UnityEngine;
using UnityEditor;
using TMPro;
using UnityEngine.UI;

/// <summary>
/// EditorScript to set up missing UI elements in MachinesCave_01 scene
/// Run this once to create and wire up Codex, Diary, and Notification panels
/// </summary>
public class MachinescaveUISetup : MonoBehaviour
{
    [MenuItem("Tools/Setup MachinesCave UI")]
    public static void SetupUI()
    {
        try
        {
            // Find or create Canvas
            Canvas mainCanvas = Object.FindAnyObjectByType<Canvas>();
            if (mainCanvas == null)
            {
                Debug.LogError("No Canvas found in scene!");
                return;
            }

            RectTransform canvasRect = mainCanvas.GetComponent<RectTransform>();
            
            // Create Codex Panel - FULL SCREEN overlay
            GameObject codexObj = new GameObject("CodexPanel");
            codexObj.transform.SetParent(mainCanvas.transform, false);
            RectTransform codexRect = codexObj.AddComponent<RectTransform>();
            codexRect.anchorMin = Vector2.zero;
            codexRect.anchorMax = Vector2.one;
            codexRect.anchoredPosition = Vector2.zero;
            codexRect.sizeDelta = Vector2.zero; // Stretch to fill canvas
            
            Image codexImage = codexObj.AddComponent<Image>();
            codexImage.color = new Color(0, 0, 0, 0.8f);
            Debug.Log($"[Setup] CodexPanel Image created: color={codexImage.color}, enabled={codexImage.enabled}");
            
            CanvasGroup codexGroup = codexObj.AddComponent<CanvasGroup>();
            codexGroup.alpha = 0;
            codexGroup.blocksRaycasts = false;
            codexGroup.interactable = false;

            // Create Diary Panel - Right side panel that animates on/off screen
            GameObject diaryObj = new GameObject("DiaryPanel");
            diaryObj.transform.SetParent(mainCanvas.transform, false);
            RectTransform diaryRect = diaryObj.AddComponent<RectTransform>();
            // DiaryController expects centered pivot and will animate from (0, -1200) to (0, 0)
            diaryRect.anchorMin = new Vector2(0.5f, 0.5f);
            diaryRect.anchorMax = new Vector2(0.5f, 0.5f);
            diaryRect.pivot = new Vector2(0.5f, 0.5f);
            diaryRect.anchoredPosition = new Vector2(0, -1200); // Start off-screen below
            diaryRect.sizeDelta = new Vector2(600, 800); // Large enough to be visible
            
            Image diaryImage = diaryObj.AddComponent<Image>();
            diaryImage.color = new Color(1, 1, 1, 0.95f);
            Debug.Log($"[Setup] DiaryPanel Image created: color={diaryImage.color}, enabled={diaryImage.enabled}");
            
            CanvasGroup diaryGroup = diaryObj.AddComponent<CanvasGroup>();
            diaryGroup.alpha = 0;
            diaryGroup.blocksRaycasts = false;
            diaryGroup.interactable = false;

            // Add DiaryController
            DiaryController diaryController = diaryObj.AddComponent<DiaryController>();

            // Create Notification Panel
            GameObject notifObj = new GameObject("NotificationPanel");
            notifObj.transform.SetParent(mainCanvas.transform, false);
            RectTransform notifRect = notifObj.AddComponent<RectTransform>();
            notifRect.anchorMin = new Vector2(0.5f, 1);
            notifRect.anchorMax = new Vector2(0.5f, 1);
            notifRect.anchoredPosition = new Vector2(0, -50);
            notifRect.sizeDelta = new Vector2(600, 80);
            notifRect.pivot = new Vector2(0.5f, 1);
            
            Image notifImage = notifObj.AddComponent<Image>();
            notifImage.color = new Color(0, 0, 0, 0.8f);
            
            CanvasGroup notifGroup = notifObj.AddComponent<CanvasGroup>();
            notifGroup.alpha = 0;
            notifGroup.blocksRaycasts = false;
            notifGroup.interactable = false;

            // Create Notification Text - position it inside the panel
            GameObject notifTextObj = new GameObject("NotificationText");
            notifTextObj.transform.SetParent(notifObj.transform, false);
            RectTransform notifTextRect = notifTextObj.AddComponent<RectTransform>();
            notifTextRect.anchorMin = Vector2.zero;
            notifTextRect.anchorMax = Vector2.one;
            notifTextRect.anchoredPosition = Vector2.zero;
            notifTextRect.sizeDelta = Vector2.zero; // Stretch to fill parent
            
            // Safely create TextMeshPro without assigning custom fonts
            TextMeshProUGUI notifText = notifTextObj.AddComponent<TextMeshProUGUI>();
            notifText.text = "Diary updated. Press [N] to access.";
            notifText.fontSize = 24;
            notifText.color = Color.white;
            notifText.alignment = TextAlignmentOptions.Center;

            // Find or create UIController GameObject
            GameObject uiControllerObj = GameObject.Find("UIController");
            if (uiControllerObj == null)
            {
                uiControllerObj = new GameObject("UIController");
            }

            DialogueUIController controller = uiControllerObj.GetComponent<DialogueUIController>();
            if (controller == null)
            {
                controller = uiControllerObj.AddComponent<DialogueUIController>();
            }

            // Add diagnostic component
            DiagnosticCanvas_v2 diagnostic = uiControllerObj.GetComponent<DiagnosticCanvas_v2>();
            if (diagnostic == null)
            {
                diagnostic = uiControllerObj.AddComponent<DiagnosticCanvas_v2>();
            }

            // Add verification component
            VerifyUISetup verify = uiControllerObj.GetComponent<VerifyUISetup>();
            if (verify == null)
            {
                verify = uiControllerObj.AddComponent<VerifyUISetup>();
            }

            // Note: No longer wiring panels to DialogueUIController
            // Controllers now auto-find their panels:
            // - DialogueUIController finds DialoguePanel in Awake()
            // - DiaryController finds DiarySystem in prefab
            // - CodexController finds CodexPanel in Awake()

            Debug.Log("✓ MachinesCave UI Setup Complete!");
            Debug.Log("  - Created CodexPanel");
            Debug.Log("  - Created DiaryPanel with DiaryController");
            Debug.Log("  - Created NotificationPanel");
            Debug.Log("  - Added DialogueUIController to UIController GameObject");
            Debug.Log("  - Controllers auto-wire themselves in Awake()");
            Debug.Log("  - Press N to toggle Diary, C to toggle Codex");
        }
        catch (System.Exception e)
        {
            Debug.LogError("Failed to setup UI: " + e.Message);
            Debug.LogException(e);
        }
    }

}
