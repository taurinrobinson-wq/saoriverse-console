using UnityEngine;
using UnityEngine.SceneManagement;
using System.Collections;

/// <summary>
/// Handles the fade to black and scene transition to the next cave scene.
/// Triggered when player enters the cave entrance collider after door opens.
/// </summary>
public class SceneTransitionController : MonoBehaviour
{
    [SerializeField] private CanvasGroup fadeOverlay;
    [SerializeField] private string nextSceneName = "MachinesCave_01";
    [SerializeField] private float fadeDuration = 2.0f;

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            BeginTransition();
        }
    }

    public void BeginTransition()
    {
        StartCoroutine(FadeAndLoad());
    }

    private IEnumerator FadeAndLoad()
    {
        if (fadeOverlay == null)
        {
            Debug.LogWarning("FadeOverlay not assigned! Loading scene directly.");
            SceneManager.LoadScene(nextSceneName);
            yield break;
        }

        // Fade to black
        float elapsedTime = 0f;
        while (elapsedTime < fadeDuration)
        {
            elapsedTime += Time.deltaTime;
            fadeOverlay.alpha = Mathf.Clamp01(elapsedTime / fadeDuration);
            yield return null;
        }

        fadeOverlay.alpha = 1f;

        // Load next scene
        SceneManager.LoadScene(nextSceneName);
    }
}
