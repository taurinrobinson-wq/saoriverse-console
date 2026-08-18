using UnityEngine;

/// <summary>
/// Ensures UI_Canvas persists across scene changes.
/// Prevents the UI from being destroyed when scenes transition.
/// </summary>
public class UIPersistenceManager : MonoBehaviour
{
    private static UIPersistenceManager _instance;

    private void Awake()
    {
        // If this is the first instance, keep it and mark it as persistent
        if (_instance == null)
        {
            _instance = this;
            DontDestroyOnLoad(gameObject);
            Debug.Log("[UI] UI_Canvas marked as persistent across scenes");
        }
        else
        {
            // If a persistent UI_Canvas already exists, destroy this duplicate
            Debug.Log("[UI] Duplicate UI_Canvas detected - destroying");
            Destroy(gameObject);
        }
    }
}
