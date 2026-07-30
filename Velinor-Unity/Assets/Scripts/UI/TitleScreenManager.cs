using UnityEngine;
using UnityEngine.SceneManagement;
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

    private CanvasGroup canvasGroup;
    private bool transitioning = false;

#if UNITY_EDITOR
    private void OnValidate()
    {
        if (openingSceneAsset != null)
        {
            targetScene = openingSceneAsset.name;
        }
        else if (!string.IsNullOrEmpty(targetScene))
        {
            string[] guids = UnityEditor.AssetDatabase.FindAssets(targetScene + " t:Scene");
            if (guids != null && guids.Length > 0)
            {
                string path = UnityEditor.AssetDatabase.GUIDToAssetPath(guids[0]);
                openingSceneAsset = UnityEditor.AssetDatabase.LoadAssetAtPath<UnityEditor.SceneAsset>(path);
            }
        }
    }
#endif

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
        
        Debug.Log($"[TitleScreenManager] StartGame button pressed. Transitioning to {targetScene}...");
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
            if (canvasGroup != null) canvasGroup.alpha = Random.Range(0.3f, 1f);
            
            // Random rotation/scale for glitch
            transform.localScale = Vector3.one * Random.Range(0.98f, 1.02f);
            
            yield return new WaitForEndOfFrame();
        }

        // Reset state
        if (canvasGroup != null) canvasGroup.alpha = 1f;
        transform.localScale = Vector3.one;

        // Transition to next scene
        if (SceneTransitionManager.Instance != null)
        {
            SceneTransitionManager.Instance.TransitionToScene(targetScene);
        }
        else
        {
            SceneManager.LoadScene(targetScene);
        }
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
