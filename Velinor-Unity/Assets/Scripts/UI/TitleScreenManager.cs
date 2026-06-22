using UnityEngine;
using UnityEngine.SceneManagement;
using System.Collections;

public class TitleScreenManager : MonoBehaviour
{
    private CanvasGroup canvasGroup;
    private bool transitioning = false;

    private void Start()
    {
        canvasGroup = GetComponent<CanvasGroup>();
        if (canvasGroup == null)
        {
            canvasGroup = gameObject.AddComponent<CanvasGroup>();
        }
    }

    public void StartGame()
    {
        if (transitioning) return;
        
        // Apply glitch effect on button press
        StartCoroutine(GlitchTransition());
    }

    private IEnumerator GlitchTransition()
    {
        transitioning = true;
        float glitchDuration = 0.5f;
        float elapsed = 0f;

        // Glitch effect - random color flashes and scale
        while (elapsed < glitchDuration)
        {
            elapsed += Time.deltaTime;
            
            // Random color flashes
            canvasGroup.alpha = Random.Range(0.3f, 1f);
            
            // Random rotation/scale for glitch
            Canvas canvas = GetComponent<Canvas>();
            if (canvas != null)
            {
                transform.localScale = Vector3.one * Random.Range(0.98f, 1.02f);
            }
            
            yield return new WaitForEndOfFrame();
        }

        // Reset state
        canvasGroup.alpha = 1f;
        transform.localScale = Vector3.one;

        // Fade out and load scene
        yield return StartCoroutine(FadeToBlack());
        
        SceneManager.LoadScene(1); // Load GamplayScene
    }

    private IEnumerator FadeToBlack()
    {
        float fadeDuration = 0.5f;
        float elapsed = 0f;

        while (elapsed < fadeDuration)
        {
            elapsed += Time.deltaTime;
            canvasGroup.alpha = Mathf.Lerp(1f, 0f, elapsed / fadeDuration);
            yield return null;
        }

        canvasGroup.alpha = 0f;
    }
}
