using UnityEngine;
using System.Collections;

/// <summary>
/// Applies camera shake/rumble effects.
/// Used for machine activation, overload, glyph resonance, and chamber power surges.
/// Singleton pattern for easy access from any script.
/// </summary>
public class CameraShake : MonoBehaviour
{
    public static CameraShake Instance;

    [Header("Shake Settings")]
    [SerializeField] private float defaultDuration = 0.4f;
    [SerializeField] private float defaultMagnitude = 0.2f;

    private Vector3 originalPos;
    private Coroutine activeShake;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
        }
        else
        {
            Destroy(gameObject);
            return;
        }

        originalPos = transform.localPosition;
    }

    /// <summary>
    /// Trigger a camera shake with optional duration and magnitude.
    /// </summary>
    public void Shake(float duration = -1f, float magnitude = -1f)
    {
        if (duration < 0) duration = defaultDuration;
        if (magnitude < 0) magnitude = defaultMagnitude;

        // Stop existing shake
        if (activeShake != null)
            StopCoroutine(activeShake);

        activeShake = StartCoroutine(ShakeRoutine(duration, magnitude));
    }

    private IEnumerator ShakeRoutine(float duration, float magnitude)
    {
        float time = 0f;

        while (time < duration)
        {
            float x = Random.Range(-1f, 1f) * magnitude;
            float y = Random.Range(-1f, 1f) * magnitude;

            transform.localPosition = originalPos + new Vector3(x, y, 0f);

            time += Time.deltaTime;
            yield return null;
        }

        transform.localPosition = originalPos;
    }
}
