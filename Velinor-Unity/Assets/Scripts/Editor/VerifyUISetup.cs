using UnityEngine;
using UnityEngine.UI;

public class VerifyUISetup : MonoBehaviour
{
    void Start()
    {
        Canvas[] allCanvases = Object.FindObjectsByType<Canvas>();
        Debug.Log($"[VERIFY] Found {allCanvases.Length} Canvas objects");
        
        foreach (Canvas canvas in allCanvases)
        {
            Debug.Log($"[VERIFY] Canvas: {canvas.gameObject.name}, Render Mode: {canvas.renderMode}, Enabled: {canvas.enabled}");
            
            // Find panels
            Transform codexPanelT = canvas.transform.Find("CodexPanel");
            Transform diaryPanelT = canvas.transform.Find("DiaryPanel");
            
            if (codexPanelT != null)
            {
                Image img = codexPanelT.GetComponent<Image>();
                CanvasGroup cg = codexPanelT.GetComponent<CanvasGroup>();
                RectTransform rt = codexPanelT.GetComponent<RectTransform>();
                
                Debug.Log($"[VERIFY] CodexPanel found!");
                Debug.Log($"  - Image: {(img != null ? "YES, Color=" + img.color : "NO")}");
                Debug.Log($"  - CanvasGroup: {(cg != null ? "YES, Alpha=" + cg.alpha : "NO")}");
                Debug.Log($"  - Size: {rt.sizeDelta}");
                Debug.Log($"  - Position: {rt.anchoredPosition}");
                Debug.Log($"  - Active: {codexPanelT.gameObject.activeSelf}");
            }
            else
            {
                Debug.LogWarning("[VERIFY] CodexPanel NOT FOUND as child of Canvas!");
            }
            
            if (diaryPanelT != null)
            {
                Image img = diaryPanelT.GetComponent<Image>();
                CanvasGroup cg = diaryPanelT.GetComponent<CanvasGroup>();
                RectTransform rt = diaryPanelT.GetComponent<RectTransform>();
                
                Debug.Log($"[VERIFY] DiaryPanel found!");
                Debug.Log($"  - Image: {(img != null ? "YES, Color=" + img.color : "NO")}");
                Debug.Log($"  - CanvasGroup: {(cg != null ? "YES, Alpha=" + cg.alpha : "NO")}");
                Debug.Log($"  - Size: {rt.sizeDelta}");
                Debug.Log($"  - Position: {rt.anchoredPosition}");
            }
        }
    }
}
