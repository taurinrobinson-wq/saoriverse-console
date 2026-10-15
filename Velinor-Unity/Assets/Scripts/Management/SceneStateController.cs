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

using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Per-scene state controller.
/// Attaches to scene root and applies state changes based on GameFlags.
/// 
/// Usage:
/// 1. Add this script to the scene root GameObject
/// 2. In inspector, create state actions:
///    - If flag "willy_dialogue_complete" is true → hide Willy NPC
///    - If flag "sorrow_glyph_collected" is true → disable glyph collider
/// 3. Script runs at Start() and applies all actions
/// 
/// This ensures consistent state when entering a scene, regardless of prior state.
/// </summary>
public class SceneStateController : MonoBehaviour
{
    [System.Serializable]
    public class StateAction
    {
        [Tooltip("Flag that must be true for this action to apply")]
        public string requiredFlag;
        
        [Tooltip("GameObject to act on")]
        public GameObject target;
        
        [Tooltip("Fallback name to find GameObject by if target reference is broken")]
        public string targetName;
        
        [Tooltip("Set target active/inactive")]
        public bool setActive = false;
        
        [Tooltip("Optional: Disable specific Collider instead of the whole GameObject")]
        public Collider targetCollider;

        public void Apply()
        {
            if (string.IsNullOrEmpty(requiredFlag))
            {
                Debug.LogWarning("[SceneStateController] StateAction has no requiredFlag!");
                return;
            }

            // Try to get target - use direct reference if available, fall back to Find()
            GameObject actualTarget = target;
            if (actualTarget == null && !string.IsNullOrEmpty(targetName))
            {
                actualTarget = GameObject.Find(targetName);
                if (actualTarget != null)
                {
                    Debug.Log($"[SceneStateController] Found target by name: {targetName}");
                }
            }

            if (actualTarget == null)
            {
                Debug.LogWarning($"[SceneStateController] StateAction has no target! (direct ref null, targetName: {targetName ?? "empty"})");
                return;
            }

            if (!GameFlags.Get(requiredFlag))
            {
                // Flag not set, don't apply this action
                return;
            }

            if (targetCollider != null)
            {
                // Disable specific collider
                targetCollider.enabled = setActive;
                Debug.Log($"[SceneStateController] {actualTarget.name}: Collider {(setActive ? "enabled" : "disabled")}");
            }
            else
            {
                // Toggle entire GameObject
                actualTarget.SetActive(setActive);
                Debug.Log($"[SceneStateController] {actualTarget.name}: {(setActive ? "Enabled" : "Disabled")} (flag: {requiredFlag})");
            }
        }
    }

    [SerializeField] private List<StateAction> actions = new List<StateAction>();

    private void Start()
    {
        Debug.Log($"[SceneStateController] Applying {actions.Count} state actions...");
        
        foreach (var action in actions)
        {
            action.Apply();
        }
    }

    /// <summary>
    /// Public method to reapply all state actions (useful for testing or manual state refresh)
    /// </summary>
    public void RefreshState()
    {
        Debug.Log("[SceneStateController] Refreshing state...");
        foreach (var action in actions)
        {
            action.Apply();
        }
    }
}
