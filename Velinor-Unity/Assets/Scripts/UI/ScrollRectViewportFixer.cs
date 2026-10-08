using UnityEngine;
using UnityEngine.UI;

namespace Velinor.UI
{
    /// <summary>
    /// Fixes the ScrollRect structure in MindLogSecondaryContainer.
    /// Creates a proper Viewport child if missing.
    /// </summary>
    public class ScrollRectViewportFixer : MonoBehaviour
    {
        private void Awake()
        {
            FixScrollRectViewport();
        }

        private void FixScrollRectViewport()
        {
            ScrollRect scrollRect = GetComponent<ScrollRect>();
            if (scrollRect == null)
            {
                return; // No ScrollRect on this object
            }

            // Check if Viewport is set and valid
            RectTransform viewport = scrollRect.viewport;
            if (viewport != null && viewport.parent == transform)
            {
                // Viewport already exists and is a child of this container
                Debug.Log($"[ScrollRectViewportFixer] ScrollRect on {gameObject.name} already has valid Viewport");
                return;
            }

            // Need to create or fix the viewport structure
            Debug.LogWarning($"[ScrollRectViewportFixer] ScrollRect on {gameObject.name} has invalid Viewport. Fixing...");

            // Try to find existing Viewport child
            Transform existingViewport = transform.Find("Viewport");
            if (existingViewport == null)
            {
                // Create a new Viewport GameObject
                GameObject viewportGO = new GameObject("Viewport");
                viewportGO.transform.SetParent(transform, false);
                existingViewport = viewportGO.transform;

                RectTransform viewportRect = viewportGO.AddComponent<RectTransform>();
                viewportRect.anchorMin = Vector2.zero;
                viewportRect.anchorMax = Vector2.one;
                viewportRect.offsetMin = Vector2.zero;
                viewportRect.offsetMax = Vector2.zero;

                // Add Image for background
                Image viewportImage = viewportGO.AddComponent<Image>();
                viewportImage.color = Color.white;

                // Add Mask for clipping
                Mask viewportMask = viewportGO.AddComponent<Mask>();
                viewportMask.showMaskGraphic = false;

                Debug.Log($"[ScrollRectViewportFixer] Created new Viewport child for {gameObject.name}");
            }

            // Move the content into the viewport if it's not already there
            RectTransform contentRect = scrollRect.content;
            if (contentRect != null && contentRect.parent != existingViewport)
            {
                contentRect.SetParent(existingViewport, false);
                Debug.Log($"[ScrollRectViewportFixer] Moved content into Viewport");
            }

            // Set the viewport in the ScrollRect
            scrollRect.viewport = existingViewport.GetComponent<RectTransform>();
            if (scrollRect.viewport == null)
            {
                scrollRect.viewport = existingViewport.gameObject.AddComponent<RectTransform>();
            }

            Debug.Log($"[ScrollRectViewportFixer] Fixed ScrollRect viewport structure on {gameObject.name}");
        }
    }
}
