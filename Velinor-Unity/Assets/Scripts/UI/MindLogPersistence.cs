using UnityEngine;

/// <summary>
/// Protects the MindLogPrimaryContainer and MindLogSecondaryContainer from being deactivated or destroyed.
/// This component ensures they persist and remain active when needed.
/// </summary>
public class MindLogPersistence : MonoBehaviour
{
    [SerializeField] private GameObject mindLogPrimaryContainer;
    [SerializeField] private GameObject mindLogSecondaryContainer;
    
    private bool isPrimaryActive = false;
    private bool isSecondaryActive = false;

    private void OnEnable()
    {
        // Find containers if not assigned
        if (mindLogPrimaryContainer == null)
            mindLogPrimaryContainer = GameObject.Find("MindLogPrimaryContainer");
        if (mindLogSecondaryContainer == null)
            mindLogSecondaryContainer = GameObject.Find("MindLogSecondaryContainer");

        // Mark as DontDestroyOnLoad
        if (mindLogPrimaryContainer != null)
            DontDestroyOnLoad(mindLogPrimaryContainer.transform.root.gameObject);
        if (mindLogSecondaryContainer != null)
            DontDestroyOnLoad(mindLogSecondaryContainer.transform.root.gameObject);
    }

    private void Update()
    {
        // Re-find containers if they become null
        if (mindLogPrimaryContainer == null)
            mindLogPrimaryContainer = GameObject.Find("MindLogPrimaryContainer");
        if (mindLogSecondaryContainer == null)
            mindLogSecondaryContainer = GameObject.Find("MindLogSecondaryContainer");

        // Protect primary container
        if (mindLogPrimaryContainer != null && isPrimaryActive)
        {
            if (!mindLogPrimaryContainer.activeSelf)
            {
                Debug.LogWarning("[MindLogPersistence] MindLogPrimaryContainer was deactivated! Re-activating...");
                mindLogPrimaryContainer.SetActive(true);
            }
        }

        // Protect secondary container
        if (mindLogSecondaryContainer != null && isSecondaryActive)
        {
            if (!mindLogSecondaryContainer.activeSelf)
            {
                Debug.LogWarning("[MindLogPersistence] MindLogSecondaryContainer was deactivated! Re-activating...");
                mindLogSecondaryContainer.SetActive(true);
            }
        }
    }

    /// <summary>
    /// Called by CodexViewController to mark the primary container as protected.
    /// </summary>
    public void ProtectPrimaryContainer()
    {
        isPrimaryActive = true;
        if (mindLogPrimaryContainer == null)
            mindLogPrimaryContainer = GameObject.Find("MindLogPrimaryContainer");
        if (mindLogPrimaryContainer != null)
            mindLogPrimaryContainer.SetActive(true);
        Debug.Log("[MindLogPersistence] Primary container protected");
    }

    /// <summary>
    /// Called by CodexViewController to unprotect the primary container.
    /// </summary>
    public void UnprotectPrimaryContainer()
    {
        isPrimaryActive = false;
        Debug.Log("[MindLogPersistence] Primary container unprotected");
    }

    /// <summary>
    /// Called by CodexViewController to mark the secondary container as protected.
    /// </summary>
    public void ProtectSecondaryContainer()
    {
        isSecondaryActive = true;
        if (mindLogSecondaryContainer == null)
            mindLogSecondaryContainer = GameObject.Find("MindLogSecondaryContainer");
        if (mindLogSecondaryContainer != null)
            mindLogSecondaryContainer.SetActive(true);
        Debug.Log("[MindLogPersistence] Secondary container protected");
    }

    /// <summary>
    /// Called by CodexViewController to unprotect the secondary container.
    /// </summary>
    public void UnprotectSecondaryContainer()
    {
        isSecondaryActive = false;
        Debug.Log("[MindLogPersistence] Secondary container unprotected");
    }
}
