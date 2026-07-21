using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// Manages scene transitions for 2.5D traversal.
/// Preloads the next scene when player reaches 1/3 up the screen.
/// Transitions when player reaches 1/2 (halfway point).
/// </summary>
public class SceneTransitionManager : MonoBehaviour
{
    [Header("Transition Settings")]
    [SerializeField] private float preloadThreshold = 0.2f; // Preload at 20% (lower for testing)
    [SerializeField] private float transitionThreshold = 0.5f; // Transition at 50% (halfway)
    [SerializeField] private string nextSceneName = "";

    [Header("References")]
    [SerializeField] private PlayerController2D5 playerController;

    [Header("Debug")]
    [SerializeField] private bool showDebugInfo = true;

    private AsyncOperation asyncLoad;
    private bool isPreloading = false;
    private bool isReadyToTransition = false;

    private void Start()
    {
        if (playerController == null)
            playerController = FindAnyObjectByType<PlayerController2D5>();
    }

    private void Update()
    {
        if (playerController == null || string.IsNullOrEmpty(nextSceneName))
            return;

        float playerYNormalized = playerController.GetPlayerYNormalized();

        // Preload scene when player reaches 1/3 up
        if (playerYNormalized >= preloadThreshold && !isPreloading)
        {
            StartPreloadingScene();
        }

        // Mark ready to transition (at 90% progress, scene is loaded but waiting for activation)
        if (playerYNormalized >= transitionThreshold && asyncLoad != null && asyncLoad.progress >= 0.9f)
        {
            isReadyToTransition = true;
        }

        // Auto-transition when ready and player continues moving up
        if (isReadyToTransition && playerYNormalized >= transitionThreshold)
        {
            PerformTransition();
        }

        if (showDebugInfo)
        {
            DebugDisplay(playerYNormalized);
        }
    }

    private void StartPreloadingScene()
    {
        if (asyncLoad != null) return;

        // Validate nextSceneName
        if (string.IsNullOrEmpty(nextSceneName))
        {
            Debug.LogError("[Scene Transition] ERROR: nextSceneName is empty! Set it in the Inspector.");
            return;
        }

        isPreloading = true;
        asyncLoad = SceneManager.LoadSceneAsync(nextSceneName, LoadSceneMode.Single);

        if (asyncLoad == null)
        {
            Debug.LogError($"[Scene Transition] ERROR: Failed to load scene '{nextSceneName}'. Is it in Build Settings?");
            isPreloading = false;
            return;
        }

        asyncLoad.allowSceneActivation = false; // Don't activate yet
        Debug.Log($"[Scene Transition] Preloading scene: {nextSceneName}");
    }

    private void PerformTransition()
    {
        if (asyncLoad == null || asyncLoad.progress < 0.9f)
        {
            Debug.LogWarning("[Scene Transition] Scene not ready for transition yet");
            return;
        }

        asyncLoad.allowSceneActivation = true;
        isReadyToTransition = false;
        Debug.Log($"[Scene Transition] Transitioning to: {nextSceneName}");
    }

    private void DebugDisplay(float playerYNormalized)
    {
        string asyncStatus = "N/A";
        if (asyncLoad != null)
        {
            string readyStatus = asyncLoad.progress >= 0.9f ? "READY" : "Loading";
            asyncStatus = $"{readyStatus}, progress: {asyncLoad.progress:F2}";
        }

        Debug.Log($"[Scene Transition] Player Y: {playerYNormalized:F3} | Preload: {(playerYNormalized >= preloadThreshold ? "✓" : "✗")} | " +
                  $"Ready: {(isReadyToTransition ? "✓" : "✗")} | Preloading: {(isPreloading ? "In Progress" : "Idle")} | AsyncLoad: {asyncStatus}");
    }
}
