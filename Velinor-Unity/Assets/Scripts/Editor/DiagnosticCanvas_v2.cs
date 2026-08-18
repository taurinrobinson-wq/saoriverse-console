using UnityEngine;
using UnityEngine.UI;

public class DiagnosticCanvas_v2 : MonoBehaviour
{
    void Awake()
    {
        Debug.Log("[DIAGNOSTIC] DiagnosticCanvas_v2.Awake() called!");
    }

    void Start()
    {
        Debug.Log("[DIAGNOSTIC] DiagnosticCanvas_v2.Start() called!");
        
        // Find main canvas
        Canvas mainCanvas = Object.FindAnyObjectByType<Canvas>();
        
        if (mainCanvas == null)
        {
            Debug.LogError("[DIAGNOSTIC] NO CANVAS FOUND IN SCENE!");
            return;
        }

        Debug.Log($"[DIAGNOSTIC] Canvas found: {mainCanvas.gameObject.name}");
        Debug.Log($"[DIAGNOSTIC] Canvas enabled: {mainCanvas.enabled}");
        Debug.Log($"[DIAGNOSTIC] Canvas GameObject active: {mainCanvas.gameObject.activeSelf}");
        Debug.Log($"[DIAGNOSTIC] Canvas Render Mode: {mainCanvas.renderMode}");
        Debug.Log($"[DIAGNOSTIC] Canvas Sorting Order: {mainCanvas.sortingOrder}");
        
        RectTransform canvasRT = mainCanvas.GetComponent<RectTransform>();
        if (canvasRT != null)
        {
            Debug.Log($"[DIAGNOSTIC] Canvas Rect: {canvasRT.rect}");
            Debug.Log($"[DIAGNOSTIC] Canvas World Size: {canvasRT.lossyScale}");
        }
        
        GraphicRaycaster gr = mainCanvas.GetComponent<GraphicRaycaster>();
        Debug.Log($"[DIAGNOSTIC] GraphicRaycaster exists: {(gr != null ? "YES" : "NO")}");
        
        // Also check for a Camera if in camera render mode
        if (mainCanvas.renderMode == RenderMode.ScreenSpaceCamera)
        {
            Debug.Log($"[DIAGNOSTIC] Canvas uses Camera render mode");
            Debug.Log($"[DIAGNOSTIC] Canvas.worldCamera: {mainCanvas.worldCamera}");
        }

        // Check all child panels
        Debug.Log($"[DIAGNOSTIC] Canvas has {mainCanvas.transform.childCount} children");
        
        foreach (Transform child in mainCanvas.transform)
        {
            CanvasGroup cg = child.GetComponent<CanvasGroup>();
            Image img = child.GetComponent<Image>();
            RectTransform rt = child.GetComponent<RectTransform>();
            
            Debug.Log($"\n[DIAGNOSTIC] Panel: {child.name}");
            Debug.Log($"  - Active: {child.gameObject.activeSelf}");
            Debug.Log($"  - CanvasGroup: {(cg != null ? "YES" : "NO")}");
            if (cg != null)
            {
                Debug.Log($"    - Alpha: {cg.alpha}");
                Debug.Log($"    - Interactable: {cg.interactable}");
                Debug.Log($"    - BlocksRaycasts: {cg.blocksRaycasts}");
            }
            Debug.Log($"  - Image: {(img != null ? "YES" : "NO")}");
            if (img != null)
            {
                Debug.Log($"    - Color: {img.color}");
                Debug.Log($"    - Enabled: {img.enabled}");
            }
            if (rt != null)
            {
                Debug.Log($"  - Size: {rt.sizeDelta}");
                Debug.Log($"  - Position: {rt.anchoredPosition}");
            }
        }
    }
}
