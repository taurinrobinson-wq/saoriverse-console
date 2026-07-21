using UnityEngine;
using UnityEngine.SceneManagement;
using System.Collections;

/// <summary>
/// Central scene transition controller with fade support.
/// Handles async loading + smooth fade in/out.
/// Persists across scenes (DontDestroyOnLoad).
/// </summary>
public class SceneTransitionManager : MonoBehaviour
{
    public static SceneTransitionManager Instance;

    [Header("Fade Settings")]
    [SerializeField] private CanvasGroup fadeCanvas;
    [SerializeField] private float fadeDuration = 0.5f;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    public void TransitionToScene(string sceneName)
    {
        StartCoroutine(LoadSceneRoutine(sceneName));
    }

    private IEnumerator LoadSceneRoutine(string sceneName)
    {
        // Fade out (black screen)
        yield return StartCoroutine(Fade(1f));

        // Load scene async
        AsyncOperation asyncLoad = SceneManager.LoadSceneAsync(sceneName);
        asyncLoad.allowSceneActivation = false;

        while (!asyncLoad.isDone)
        {
            if (asyncLoad.progress >= 0.9f)
            {
                asyncLoad.allowSceneActivation = true;
            }
            yield return null;
        }

        // Fade in (show new scene)
        yield return StartCoroutine(Fade(0f));
    }

    private IEnumerator Fade(float targetAlpha)
    {
        if (fadeCanvas == null)
        {
            Debug.LogError("[SceneTransitionManager] fadeCanvas not assigned!");
            yield break;
        }

        float startAlpha = fadeCanvas.alpha;
        float time = 0f;

        while (time < fadeDuration)
        {
            fadeCanvas.alpha = Mathf.Lerp(startAlpha, targetAlpha, time / fadeDuration);
            time += Time.deltaTime;
            yield return null;
        }

        fadeCanvas.alpha = targetAlpha;
    }
}
