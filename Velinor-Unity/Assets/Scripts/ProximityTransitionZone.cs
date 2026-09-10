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
    private bool playerHasExitedOnce = false;
    private Collider cachedCollider;
    private Collider2D cachedCollider2D;

    private void Awake()
    {
        cachedCollider = GetComponent<Collider>();
        cachedCollider2D = GetComponent<Collider2D>();
    }

    private void Start()
    {
        // Ensure there's a Rigidbody to own this trigger collider
        // Trigger colliders without a Rigidbody don't always register collisions
        Rigidbody rb = GetComponent<Rigidbody>();
        if (rb == null)
        {
            rb = gameObject.AddComponent<Rigidbody>();
            rb.isKinematic = true;
            rb.constraints = RigidbodyConstraints.FreezeAll;
            Debug.Log("[ProximityTransitionZone] Added missing Rigidbody to trigger collider");
        }

        // Force physics engine to recognize the collider by toggling it
        if (cachedCollider != null)
        {
            cachedCollider.enabled = false;
            cachedCollider.enabled = true;
        }
        if (cachedCollider2D != null)
        {
            cachedCollider2D.enabled = false;
            cachedCollider2D.enabled = true;
        }
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
        Debug.Log($"[ProximityTransitionZone] OnTriggerEnter called with: {other.gameObject.name} (tag: {other.tag}) at Time.timeSinceLevelLoad={Time.timeSinceLevelLoad:F4}");
        HandleTriggerEnter(other.gameObject);
    }

    private void HandleTriggerEnter(GameObject other)
    {
        Debug.Log($"[ProximityTransitionZone] HandleTriggerEnter - other.tag={other.tag}, Player tag check: {other.CompareTag("Player")}");
        if (other.CompareTag("Player"))
        {
            Debug.Log($"[ProximityTransitionZone] Player detected! Setting playerInside=true. playerHasExitedOnce={playerHasExitedOnce}");
            playerInside = true;
            CheckAutoTrigger(other);
        }
    }

    private void CheckAutoTrigger(GameObject player)
    {
        Debug.Log($"[ProximityTransitionZone] CheckAutoTrigger called. transitionTriggered={transitionTriggered}, requireKeyPress={requireKeyPress}");
        if (transitionTriggered || requireKeyPress) 
        {
            Debug.Log("[ProximityTransitionZone] CheckAutoTrigger blocked: transitionTriggered or requireKeyPress");
            return;
        }

        // Grace period only applies to first entry on scene load
        // If player has exited and re-entered, skip grace period
        float timeSinceLoad = Time.timeSinceLevelLoad;
        bool withinGracePeriod = timeSinceLoad < spawnGracePeriod && !playerHasExitedOnce;
        Debug.Log($"[ProximityTransitionZone] Time.timeSinceLevelLoad={timeSinceLoad:F3}, spawnGracePeriod={spawnGracePeriod}, playerHasExitedOnce={playerHasExitedOnce}, withinGracePeriod={withinGracePeriod}");
        if (withinGracePeriod) 
        {
            Debug.Log("[ProximityTransitionZone] CheckAutoTrigger blocked: within grace period");
            return;
        }

        Debug.Log("[ProximityTransitionZone] All checks passed! Triggering transition...");
        TriggerTransition();
    }

    private bool IsPlayerPivotInside(GameObject player)
    {
        if (cachedCollider != null) 
        {
            bool contains = cachedCollider.bounds.Contains(player.transform.position);
            Debug.Log($"[ProximityTransitionZone] IsPlayerPivotInside (3D): Player pos={player.transform.position}, Collider bounds={cachedCollider.bounds}, Contains={contains}");
            return contains;
        }
        if (cachedCollider2D != null) 
        {
            bool overlaps = cachedCollider2D.OverlapPoint(player.transform.position);
            Debug.Log($"[ProximityTransitionZone] IsPlayerPivotInside (2D): Player pos={player.transform.position}, OverlapPoint={overlaps}");
            return overlaps;
        }
        Debug.Log("[ProximityTransitionZone] IsPlayerPivotInside: No collider cached!");
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
        {
            playerInside = false;
            playerHasExitedOnce = true;
        }
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
