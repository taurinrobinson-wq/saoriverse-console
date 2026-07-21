/*
 * ============================================================
 * PROPRIETARY & CONFIDENTIAL
 * 
 * © 2026 Tauri Robinson. All rights reserved.
 * This code is proprietary and may not be redistributed,
 * modified, or used without explicit written permission.
 * 
 * Unauthorized access, modification, or distribution is prohibited.
 * See LICENSE_COMMERCIAL.md and NDA_TEMPLATE.md for details.
 * ============================================================
 */

using UnityEngine;

/// <summary>
/// Attach to a trigger collider to create a proximity-based scene transition.
/// Player automatically transitions when entering (or press E if requireKeyPress = true).
/// </summary>
public class ProximityTransitionZone : MonoBehaviour
{
    [Header("Transition Settings")]
    [SerializeField] private string targetScene;
    [SerializeField] private bool requireKeyPress = false;
    [SerializeField] private KeyCode interactKey = KeyCode.E;
    [SerializeField] private string spawnIDForNextScene = "";

    private bool playerInside = false;

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            playerInside = true;

            if (!requireKeyPress)
            {
                TriggerTransition();
            }
        }
    }

    private void OnTriggerExit2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
            playerInside = false;
    }

    private void Update()
    {
        if (requireKeyPress && playerInside && Input.GetKeyDown(interactKey))
        {
            TriggerTransition();
        }
    }

    private void TriggerTransition()
    {
        if (string.IsNullOrEmpty(targetScene))
        {
            Debug.LogError("[ProximityTransitionZone] targetScene is not set!");
            return;
        }

        // Set spawn point for next scene
        if (!string.IsNullOrEmpty(spawnIDForNextScene))
            SceneSpawnManager.nextSpawnID = spawnIDForNextScene;

        SceneTransitionManager.Instance.TransitionToScene(targetScene);
    }
}
