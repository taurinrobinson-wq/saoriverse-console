using UnityEngine;

/// <summary>
/// Ensures UI_Canvas persists across scene changes.
/// Prevents the UI from being destroyed when scenes transition.
/// </summary>
public class UIPersistenceManager : MonoBehaviour
{
    private static UIPersistenceManager _instance;

    public bool EnsureOwnership()
    {
        if (_instance == null)
        {
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }
        return _instance == this;
    }

    private void Awake()
    {
        if (EnsureOwnership())
        {
            Debug.Log("[UI] UI_Canvas marked as persistent across scenes");
        }
        else
        {
            // Prevent child OnEnable handlers running on a doomed duplicate.
            gameObject.SetActive(false);
            Debug.Log("[UI] Duplicate UI_Canvas detected - destroying");
            Destroy(gameObject);
        }
    }

    private void OnDestroy()
    {
        if (_instance == this) _instance = null;
    }
}
