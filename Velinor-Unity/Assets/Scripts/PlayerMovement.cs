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
/// 2.5D player movement with depth scaling.
/// Uses Rigidbody2D for collision safety.
/// Smooth 8-direction movement with normalized diagonal speed.
/// </summary>
public class PlayerMovement : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float moveSpeed = 5f;

    [Header("Depth Scaling")]
    [SerializeField] private float minScale = 0.6f;   // smallest size at top of screen
    [SerializeField] private float maxScale = 1.0f;   // largest size at bottom of screen
    [SerializeField] private float topY = 4f;         // adjust to match your scene
    [SerializeField] private float bottomY = -4f;     // adjust to match your scene

    private Rigidbody2D rb;
    private Vector2 movement;

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
        if (rb == null)
        {
            Debug.LogError("[PlayerMovement] Rigidbody2D not found on player!");
        }
    }

    private void Update()
    {
        // Raw input (no smoothing, immediate response)
        movement.x = Input.GetAxisRaw("Horizontal");
        movement.y = Input.GetAxisRaw("Vertical");

        // Normalize diagonal movement so diagonal speed = cardinal speed
        movement = movement.normalized;

        // Depth scaling based on Y position
        float t = Mathf.InverseLerp(topY, bottomY, transform.position.y);
        float scale = Mathf.Lerp(minScale, maxScale, t);
        transform.localScale = new Vector3(scale, scale, 1f);
    }

    private void FixedUpdate()
    {
        if (rb != null)
            rb.velocity = movement * moveSpeed;
    }
}
