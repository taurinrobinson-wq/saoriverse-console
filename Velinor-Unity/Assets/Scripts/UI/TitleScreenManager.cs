using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using System.Collections;

public class TitleScreenManager : MonoBehaviour
{
    [Header("--- DRAG AND DROP TARGET SCENE BELOW ---")]
    [Space(10)]
#if UNITY_EDITOR
    [Tooltip("Drag the Scene asset you want to load when Start is pressed into this slot.")]
    [SerializeField] private UnityEditor.SceneAsset openingSceneAsset;
#endif
    [SerializeField] private string targetScene = "MachinesCave_01";

    [Header("--- EYE ANIMATION ---")]
    [Tooltip("The Image component that covers the character's face.")]
    public UnityEngine.UI.Image characterOverlayImage;
    [Tooltip("The sprite to show when eyes are closed (initial state).")]
    public Sprite eyesClosedSprite;
    [Tooltip("The sprite to show when eyes are partially open.")]
    public Sprite eyesPartOpenSprite;
    [Tooltip("The sprite to show when eyes are fully open.")]
    public Sprite eyesOpenSprite;
    [Tooltip("Duration to show the partially open eyes.")]
    public float eyesPartOpenDuration = 0.15f;
    [Tooltip("Duration to show the fully open eyes.")]
    public float eyesOpenDuration = 0.2f;

    [Header("--- AUDIO ---")]
    [SerializeField] private AudioClip startButtonSound;
    private AudioSource audioSource;

    private CanvasGroup canvasGroup;
    private bool transitioning = false;

    [Header("--- UI PANELS ---")]
    [SerializeField] private GameObject mainMenuPanel;
    [SerializeField] private GameObject overlayRoot;
    [SerializeField] private GameObject settingsPanel;
    [SerializeField] private GameObject profilePanel;
    [SerializeField] private GameObject profileEntryPanel;
    [SerializeField] private GameObject overwriteWarningPanel;
    [SerializeField] private GameObject deleteProfileWarningPanel;
    [SerializeField] private GameObject displayConfirmationPanel;
    [SerializeField] private GameObject extrasPanel;

    [Header("--- MAIN MENU BUTTONS ---")]
    [SerializeField] private Button newGameButton;
    [SerializeField] private Button continueButton;

    private int selectedSlotIndex = -1;

    private void Start()
    {
        canvasGroup = GetComponent<CanvasGroup>();
        if (canvasGroup == null)
        {
            canvasGroup = gameObject.AddComponent<CanvasGroup>();
        }

        audioSource = GetComponent<AudioSource>();
        if (audioSource == null)
        {
            audioSource = gameObject.AddComponent<AudioSource>();
            audioSource.playOnAwake = false;
        }

        if (characterOverlayImage != null && eyesClosedSprite != null)
        {
            characterOverlayImage.sprite = eyesClosedSprite;
        }

        // Initialize Persistence
        if (Velinor.Persistence.SettingsManager.Instance != null)
        {
            Velinor.Persistence.SettingsManager.Instance.LoadSettings();
        }

        if (Velinor.Persistence.ProfileManager.Instance != null)
        {
            Velinor.Persistence.ProfileManager.Instance.ClearActiveProfile();
        }

        RefreshMenuState();

        if (mainMenuPanel != null) mainMenuPanel.SetActive(true);
        if (overlayRoot != null) overlayRoot.SetActive(false);
        
        HideAllOverlays();
    }

    public void RefreshMenuState()
    {
        var pm = Velinor.Persistence.ProfileManager.Instance;
        if (pm == null) return;

        bool hasActiveContinue = pm.ActiveProfile != null && pm.ActiveProfile.hasValidContinuePoint;

        if (continueButton != null) continueButton.gameObject.SetActive(hasActiveContinue);
        if (newGameButton != null) newGameButton.gameObject.SetActive(!hasActiveContinue);
    }

    public void StartGame()
    {
        if (transitioning) return;

        var pm = Velinor.Persistence.ProfileManager.Instance;
        if (pm == null) return;

        if (pm.ActiveProfile == null)
        {
            int firstEmpty = -1;
            for (int i = 0; i < 3; i++)
            {
                if (pm.GetSlot(i) == null) { firstEmpty = i; break; }
            }

            if (firstEmpty != -1) OpenProfileEntry(firstEmpty);
            else OpenProfile();
            return;
        }

        if (pm.ActiveProfile.hasValidContinuePoint) HandleContinue();
        else HandleNewGame();
    }

    private void HandleContinue()
    {
        if (audioSource != null && startButtonSound != null) audioSource.PlayOneShot(startButtonSound);
        Velinor.Persistence.SaveCoordinator.Instance.RestoreFromSnapshot();
        StartCoroutine(GlitchTransition(Velinor.Persistence.ProfileManager.Instance.ActiveProfile.lastSavedScene));
    }

    private void HandleNewGame()
    {
        var pm = Velinor.Persistence.ProfileManager.Instance;
        if (pm.ActiveProfile != null && pm.ActiveProfile.gameStarted)
        {
            ShowOverlay(overwriteWarningPanel);
            return;
        }

        if (audioSource != null && startButtonSound != null) audioSource.PlayOneShot(startButtonSound);
        if (mainMenuPanel != null) mainMenuPanel.SetActive(false);
        StartCoroutine(NewGameSequence());
    }

    public void ConfirmOverwrite()
    {
        if (overlayRoot != null) overlayRoot.SetActive(false);
        StartCoroutine(NewGameSequence());
    }

    public void CancelOverwrite() => OpenProfile();

    private IEnumerator NewGameSequence()
    {
        yield return new WaitForSeconds(0.5f);
        
        // Eye Opening
        if (characterOverlayImage != null)
        {
            if (eyesPartOpenSprite != null)
            {
                characterOverlayImage.sprite = eyesPartOpenSprite;
                yield return new WaitForSeconds(eyesPartOpenDuration);
            }
            
            if (eyesOpenSprite != null)
            {
                characterOverlayImage.sprite = eyesOpenSprite;
                yield return new WaitForSeconds(eyesOpenDuration);
            }
        }

        StartCoroutine(GlitchTransition(targetScene));
    }

    private IEnumerator GlitchTransition(string sceneToLoad)
    {
        transitioning = true;
        
        // Start loading the scene in the background
        AsyncOperation asyncLoad = SceneManager.LoadSceneAsync(sceneToLoad);
        asyncLoad.allowSceneActivation = false;

        float glitchDuration = 0.5f;
        float elapsed = 0f;

        while (elapsed < glitchDuration)
        {
            elapsed += Time.deltaTime;
            if (canvasGroup != null) canvasGroup.alpha = Random.Range(0.3f, 1f);
            transform.localScale = Vector3.one * Random.Range(0.98f, 1.02f);
            yield return new WaitForEndOfFrame();
        }

        if (canvasGroup != null) canvasGroup.alpha = 1f;
        transform.localScale = Vector3.one;

        if (SceneTransitionManager.Instance != null)
        {
            yield return StartCoroutine(FadeToBlack(0.3f));
            while (asyncLoad.progress < 0.9f) yield return null;
            asyncLoad.allowSceneActivation = true;
        }
        else
        {
            while (asyncLoad.progress < 0.9f) yield return null;
            asyncLoad.allowSceneActivation = true;
        }
    }

    private void HideAllOverlays()
    {
        if (settingsPanel != null) settingsPanel.SetActive(false);
        if (profilePanel != null) profilePanel.SetActive(false);
        if (profileEntryPanel != null) profileEntryPanel.SetActive(false);
        if (overwriteWarningPanel != null) overwriteWarningPanel.SetActive(false);
        if (deleteProfileWarningPanel != null) deleteProfileWarningPanel.SetActive(false);
        if (displayConfirmationPanel != null) displayConfirmationPanel.SetActive(false);
        if (extrasPanel != null) extrasPanel.SetActive(false);
    }

    private void ShowOverlay(GameObject panel)
    {
        if (overlayRoot != null)
        {
            overlayRoot.SetActive(true);
            overlayRoot.transform.SetAsLastSibling();
            
            var canvas = overlayRoot.GetComponent<Canvas>();
            if (canvas != null)
            {
                canvas.overrideSorting = true;
                canvas.sortingOrder = 999;
            }

            var rootImg = overlayRoot.GetComponent<UnityEngine.UI.Image>();
            if (rootImg != null)
            {
                rootImg.color = new Color(0, 0, 0, 0.9f);
                rootImg.raycastTarget = true;
            }
        }
        HideAllOverlays();
        if (panel != null) panel.SetActive(true);
    }

    private void CloseCurrentOverlay()
    {
        HideAllOverlays();
        if (overlayRoot != null) overlayRoot.SetActive(false);
        if (mainMenuPanel != null) mainMenuPanel.SetActive(true);
        RefreshMenuState();
    }

    public void OpenSettings() => ShowOverlay(settingsPanel);
    public void CloseSettings() => CloseCurrentOverlay();

    public void OpenProfile() => ShowOverlay(profilePanel);
    public void CloseProfile() => CloseCurrentOverlay();

    public void OpenExtras() => ShowOverlay(extrasPanel);
    public void CloseExtras() => CloseCurrentOverlay();

    public void OpenDeleteWarning() => ShowOverlay(deleteProfileWarningPanel);
    public void CloseDeleteWarning() => ShowOverlay(profilePanel);

    public void OpenDisplayConfirmation() => ShowOverlay(displayConfirmationPanel);
    public void CloseDisplayConfirmation() => ShowOverlay(settingsPanel);

    private void OpenProfileEntry(int slotIndex)
    {
        selectedSlotIndex = slotIndex;
        ShowOverlay(profileEntryPanel);
    }

    public void ConfirmProfileCreation()
    {
        if (selectedSlotIndex == -1) return;

        var input = profileEntryPanel.GetComponentInChildren<TMPro.TMP_InputField>();
        string profileName = (input != null && !string.IsNullOrEmpty(input.text)) ? input.text : "Explorer";

        Velinor.Persistence.ProfileManager.Instance.CreateProfile(selectedSlotIndex, profileName);
        Velinor.Persistence.ProfileManager.Instance.SetActiveProfile(selectedSlotIndex);

        if (profileEntryPanel != null) profileEntryPanel.SetActive(false);
        if (overlayRoot != null) overlayRoot.SetActive(false);
        HandleNewGame();
    }

    public void CancelProfileCreation()
    {
        if (profileEntryPanel != null) profileEntryPanel.SetActive(false);
        if (overlayRoot != null) overlayRoot.SetActive(false);
        if (mainMenuPanel != null) mainMenuPanel.SetActive(true);
        selectedSlotIndex = -1;
    }

    private IEnumerator FadeToBlack(float duration)
    {
        float elapsed = 0f;
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            if (canvasGroup != null) canvasGroup.alpha = Mathf.Lerp(1f, 0f, elapsed / duration);
            yield return null;
        }
        if (canvasGroup != null) canvasGroup.alpha = 0f;
    }

    public void QuitGame()
    {
        Debug.Log("[TitleScreenManager] Quitting game...");
#if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
#else
        Application.Quit();
#endif
    }
}
