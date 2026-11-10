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
    [SerializeField] private UnityEngine.UI.Image characterOverlayImage;
    [SerializeField] private Sprite eyesPartOpenSprite;
    [SerializeField] private Sprite eyesOpenSprite;

    [Header("--- AUDIO ---")]
    [SerializeField] private AudioClip startButtonSound;
    private AudioSource audioSource;

    private CanvasGroup canvasGroup;
    private bool transitioning = false;

    [Header("--- UI PANELS ---")]
    [SerializeField] private GameObject mainMenuPanel;
    [SerializeField] private GameObject settingsPanel;

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

        if (mainMenuPanel != null) mainMenuPanel.SetActive(true);
        if (settingsPanel != null) settingsPanel.SetActive(false);
    }

    public void StartGame()
    {
        if (transitioning) return;
        
        if (audioSource != null && startButtonSound != null)
        {
            audioSource.PlayOneShot(startButtonSound);
        }

        Debug.Log($"[TitleScreenManager] StartGame button pressed. Transitioning to {targetScene}...");
        StartCoroutine(GlitchTransition());
    }

    private IEnumerator GlitchTransition()
    {
        transitioning = true;
        
        // Start loading the scene in the background as soon as we press start
        AsyncOperation asyncLoad = SceneManager.LoadSceneAsync(targetScene);
        asyncLoad.allowSceneActivation = false;

        // --- EYE SEQUENCE START ---
        if (characterOverlayImage != null)
        {
            if (eyesPartOpenSprite != null)
            {
                characterOverlayImage.sprite = eyesPartOpenSprite;
                yield return new WaitForSeconds(0.15f);
            }
            
            if (eyesOpenSprite != null)
            {
                characterOverlayImage.sprite = eyesOpenSprite;
                yield return new WaitForSeconds(0.2f);
            }
        }
        // --- EYE SEQUENCE END ---

        float glitchDuration = 0.5f;
        float elapsed = 0f;

        // Glitch effect - random color flashes and scale
        while (elapsed < glitchDuration)
        {
            elapsed += Time.deltaTime;
            
            // Random color flashes
            if (canvasGroup != null) canvasGroup.alpha = Random.Range(0.3f, 1f);
            
            // Random rotation/scale for glitch
            transform.localScale = Vector3.one * Random.Range(0.98f, 1.02f);
            
            yield return new WaitForEndOfFrame();
        }

        // Reset state
        if (canvasGroup != null) canvasGroup.alpha = 1f;
        transform.localScale = Vector3.one;

        // If we have a SceneTransitionManager, we can use its fade out before activating the scene
        if (SceneTransitionManager.Instance != null)
        {
            // Trigger a quick fade out to black
            yield return StartCoroutine(FadeToBlack(0.3f));
            
            // The scene should be almost loaded by now
            while (asyncLoad.progress < 0.9f)
            {
                yield return null;
            }
            
            asyncLoad.allowSceneActivation = true;
        }
        else
        {
            // Fallback: just wait for load and activate
            while (asyncLoad.progress < 0.9f)
            {
                yield return null;
            }
            asyncLoad.allowSceneActivation = true;
        }
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

    public void OpenSettings()
{
        if (mainMenuPanel != null) mainMenuPanel.SetActive(false);
        if (settingsPanel != null) settingsPanel.SetActive(true);
    }

    public void CloseSettings()
    {
        if (mainMenuPanel != null) mainMenuPanel.SetActive(true);
        if (settingsPanel != null) settingsPanel.SetActive(false);
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
