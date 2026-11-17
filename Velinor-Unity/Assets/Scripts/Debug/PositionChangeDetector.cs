using UnityEngine;

/// <summary>
/// Debug script: Detects and logs any changes to this GameObject's position.
/// Attach to any object that's mysteriously moving.
/// </summary>
public class PositionChangeDetector : MonoBehaviour
{
    private Vector3 lastPosition;
    private Vector3 lastLocalPosition;
    private bool initialized = false;

    private void Start()
    {
        lastPosition = transform.position;
        lastLocalPosition = transform.localPosition;
        initialized = true;
        Debug.Log($"[PositionChangeDetector] {gameObject.name} initialized at world position {lastPosition}, local {lastLocalPosition}");
    }

    private void Update()
    {
        if (!initialized) return;

        // Check world position
        if (transform.position != lastPosition)
        {
            Debug.LogWarning($"[PositionChangeDetector] {gameObject.name} WORLD POSITION CHANGED!");
            Debug.LogWarning($"  Old: {lastPosition}");
            Debug.LogWarning($"  New: {transform.position}");
            Debug.LogWarning($"  Delta: {transform.position - lastPosition}");
            Debug.LogWarning(System.Environment.StackTrace);
            lastPosition = transform.position;
        }

        // Check local position
        if (transform.localPosition != lastLocalPosition)
        {
            Debug.LogWarning($"[PositionChangeDetector] {gameObject.name} LOCAL POSITION CHANGED!");
            Debug.LogWarning($"  Old: {lastLocalPosition}");
            Debug.LogWarning($"  New: {transform.localPosition}");
            Debug.LogWarning($"  Delta: {transform.localPosition - lastLocalPosition}");
            Debug.LogWarning(System.Environment.StackTrace);
            lastLocalPosition = transform.localPosition;
        }
    }
}
