using UnityEngine;

namespace Velinor.UI.Codex
{
    /// <summary>
    /// Tracks changes to a RectTransform to diagnose position drift issues.
    /// </summary>
    public class RectTransformTracker : MonoBehaviour
    {
        private RectTransform rect;
        private Vector2 lastPosition;
        private Vector2 lastAnchorMin;
        private Vector2 lastAnchorMax;
        private Vector2 lastOffsetMin;
        private Vector2 lastOffsetMax;
        private int changeCount = 0;

        private void OnEnable()
        {
            rect = GetComponent<RectTransform>();
            if (rect != null)
            {
                CaptureState("OnEnable");
            }
        }

        private void LateUpdate()
        {
            if (rect == null) return;

            Vector2 currentPos = rect.anchoredPosition;
            Vector2 currentAnchorMin = rect.anchorMin;
            Vector2 currentAnchorMax = rect.anchorMax;
            Vector2 currentOffsetMin = rect.offsetMin;
            Vector2 currentOffsetMax = rect.offsetMax;

            bool changed = false;

            if (currentPos != lastPosition)
            {
                Debug.LogWarning($"[RectTransformTracker] {gameObject.name} POSITION CHANGED: {lastPosition} → {currentPos}");
                changed = true;
            }

            if (currentAnchorMin != lastAnchorMin)
            {
                Debug.LogWarning($"[RectTransformTracker] {gameObject.name} ANCHOR MIN CHANGED: {lastAnchorMin} → {currentAnchorMin}");
                changed = true;
            }

            if (currentAnchorMax != lastAnchorMax)
            {
                Debug.LogWarning($"[RectTransformTracker] {gameObject.name} ANCHOR MAX CHANGED: {lastAnchorMax} → {currentAnchorMax}");
                changed = true;
            }

            if (currentOffsetMin != lastOffsetMin)
            {
                Debug.LogWarning($"[RectTransformTracker] {gameObject.name} OFFSET MIN CHANGED: {lastOffsetMin} → {currentOffsetMin}");
                changed = true;
            }

            if (currentOffsetMax != lastOffsetMax)
            {
                Debug.LogWarning($"[RectTransformTracker] {gameObject.name} OFFSET MAX CHANGED: {lastOffsetMax} → {currentOffsetMax}");
                changed = true;
            }

            if (changed)
            {
                changeCount++;
                if (changeCount <= 5) // Log first 5 changes only to avoid spam
                {
                    Debug.Log($"[RectTransformTracker] Change #{changeCount} - Stack trace:\n{StackTraceUtility.ExtractStackTrace()}");
                }
                CaptureState("After change");
            }
        }

        private void CaptureState(string context)
        {
            if (rect == null) return;
            lastPosition = rect.anchoredPosition;
            lastAnchorMin = rect.anchorMin;
            lastAnchorMax = rect.anchorMax;
            lastOffsetMin = rect.offsetMin;
            lastOffsetMax = rect.offsetMax;
            Debug.Log($"[RectTransformTracker] {gameObject.name} state captured ({context}): pos={lastPosition}, anchorMin={lastAnchorMin}, anchorMax={lastAnchorMax}, offsetMin={lastOffsetMin}, offsetMax={lastOffsetMax}");
        }
    }
}
