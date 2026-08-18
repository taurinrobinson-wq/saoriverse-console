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
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Attach to a trigger collider to create a proximity-based scene transition.
/// Player automatically transitions when entering (or press E if requireKeyPress = true).
/// </summary>
public class ProximityTransitionZone : MonoBehaviour
{
    [Header("Transition Settings")]
#if UNITY_EDITOR
    [SerializeField] private UnityEditor.SceneAsset targetSceneAsset;
#endif
    [SerializeField] private string targetScene;
    [SerializeField] private bool requireKeyPress = false;
    [SerializeField] private KeyCode interactKey = KeyCode.E;
    [SerializeField] private string spawnIDForNextScene = "";
    [SerializeField] private float spawnGracePeriod = 0.5f;

    private bool playerInside = false;
    private bool transitionTriggered = false;
    private Collider cachedCollider;
    private Collider2D cachedCollider2D;

    private void Awake()
    {
        cachedCollider = GetComponent<Collider>();
        cachedCollider2D = GetComponent<Collider2D>();
    }

#if UNITY_EDITOR
private void OnValidate()
    {
        if (targetSceneAsset != null)
        {
            targetScene = targetSceneAsset.name;
        }
        else if (!string.IsNullOrEmpty(targetScene))
        {
            string[] guids = UnityEditor.AssetDatabase.FindAssets(targetScene + " t:Scene");
            if (guids != null && guids.Length > 0)
            {
                string path = UnityEditor.AssetDatabase.GUIDToAssetPath(guids[0]);
                targetSceneAsset = UnityEditor.AssetDatabase.LoadAssetAtPath<UnityEditor.SceneAsset>(path);
            }
        }
    }
#endif

    private void OnTriggerEnter2D(Collider2D other)
    {
        HandleTriggerEnter(other.gameObject);
    }

    private void OnTriggerEnter(Collider other)
    {
        HandleTriggerEnter(other.gameObject);
    }

    private void HandleTriggerEnter(GameObject other)
    {
        if (other.CompareTag("Player"))
        {
            playerInside = true;
            CheckAutoTrigger(other);
        }
    }

    private void CheckAutoTrigger(GameObject player)
    {
        if (transitionTriggered || requireKeyPress) return;

        // Use pivot position to check if player is actually "at" the trigger
        if (!IsPlayerPivotInside(player)) return;

        if (Time.timeSinceLevelLoad < spawnGracePeriod) return;

        TriggerTransition();
    }

    private bool IsPlayerPivotInside(GameObject player)
    {
        if (cachedCollider != null) return cachedCollider.bounds.Contains(player.transform.position);
        if (cachedCollider2D != null) return cachedCollider2D.OverlapPoint(player.transform.position);
        return false;
    }

    private void OnTriggerExit2D(Collider2D other)
    {
        HandleTriggerExit(other.gameObject);
    }

    private void OnTriggerExit(Collider other)
    {
        HandleTriggerExit(other.gameObject);
    }

    private void HandleTriggerExit(GameObject other)
    {
        if (other.CompareTag("Player"))
            playerInside = false;
    }

    private void Update()
    {
        if (!playerInside || transitionTriggered) return;

        GameObject player = GameObject.FindWithTag("Player");
        if (player == null) return;

        if (!requireKeyPress)
        {
            CheckAutoTrigger(player);
            return;
        }

        // Key press logic: Player must be at trigger
        if (!IsPlayerPivotInside(player)) return;

        bool isPressed = false;
#if ENABLE_INPUT_SYSTEM
        var keyboard = Keyboard.current;
        if (keyboard != null)
        {
            if (interactKey == KeyCode.E && keyboard.eKey.wasPressedThisFrame) isPressed = true;
            else if (interactKey == KeyCode.Space && keyboard.spaceKey.wasPressedThisFrame) isPressed = true;
            else if (interactKey == KeyCode.Return && keyboard.enterKey.wasPressedThisFrame) isPressed = true;
        }
#else
        if (Input.GetKeyDown(interactKey)) isPressed = true;
#endif

        if (isPressed)
        {
            TriggerTransition();
        }
    }

    private void TriggerTransition()
    {
        if (transitionTriggered) return;

        if (string.IsNullOrEmpty(targetScene))
        {
            Debug.LogError("[ProximityTransitionZone] targetScene is not set!");
            return;
        }

        transitionTriggered = true;
        Debug.Log($"[ProximityTransitionZone] Triggering transition to {targetScene}...");

        // Set spawn point for next scene
        if (!string.IsNullOrEmpty(spawnIDForNextScene))
            SceneSpawnManager.nextSpawnID = spawnIDForNextScene;

        SceneTransitionManager.Instance.TransitionToScene(targetScene);
    }
}
