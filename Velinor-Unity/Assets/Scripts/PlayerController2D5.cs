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
/// 2.5D player controller for side-scrolling cave traversal.
/// Moves with WASD controls and scales based on Y position to simulate depth.
/// Y-axis (vertical) = depth perception (smaller up, larger down).
/// X-axis (horizontal) = left/right movement.
/// </summary>
public class PlayerController2D5 : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField] private float moveSpeed = 3f;
    [SerializeField] private float minX = -6f;
    [SerializeField] private float maxX = 6f;
    [SerializeField] private float minY = -2.5f;
    [SerializeField] private float maxY = 2.5f;

    [Header("Depth Scaling")]
    [SerializeField] private float minScale = 0.5f; // Smallest when at top (farthest)
    [SerializeField] private float maxScale = 1.5f; // Largest when at bottom (closest)
    [SerializeField] private float scaleSmoothing = 5f; // How quickly scale updates

    [Header("Visuals")]
    [SerializeField] private SpriteRenderer spriteRenderer;

    private Vector3 currentPosition;
    private float currentScale = 1f;
    private SpriteRenderer cachedSpriteRenderer;

    private void Start()
    {
        cachedSpriteRenderer = spriteRenderer != null ? spriteRenderer : GetComponent<SpriteRenderer>();
        currentPosition = transform.position;
        currentScale = transform.localScale.x;
    }

    private void Update()
    {
        HandleMovement();
        UpdateDepthScaling();
        ApplyTransform();
    }

    private void HandleMovement()
    {
        Vector3 movement = Vector3.zero;

        // Left/Right movement (X axis only)
        if (Input.GetKey(KeyCode.D))
            movement.x += moveSpeed * Time.deltaTime;
        if (Input.GetKey(KeyCode.A))
            movement.x -= moveSpeed * Time.deltaTime;

        // Forward/Backward movement (Y axis only) - W goes up/forward (away), S goes down/backward (toward)
        if (Input.GetKey(KeyCode.W))
            movement.y += moveSpeed * Time.deltaTime;
        if (Input.GetKey(KeyCode.S))
            movement.y -= moveSpeed * Time.deltaTime;

        // Apply movement with bounds
        currentPosition += movement;
        currentPosition.x = Mathf.Clamp(currentPosition.x, minX, maxX);
        currentPosition.y = Mathf.Clamp(currentPosition.y, minY, maxY);
    }

    private void UpdateDepthScaling()
    {
        // Calculate scale based on Y position
        // Y ranges from minY to maxY
        // Scale ranges from maxScale (at minY) to minScale (at maxY)
        float yRange = maxY - minY;
        float yNormalized = (currentPosition.y - minY) / yRange; // 0 to 1, where 0 is bottom (close), 1 is top (far)

        float targetScale = Mathf.Lerp(maxScale, minScale, yNormalized);
        currentScale = Mathf.Lerp(currentScale, targetScale, scaleSmoothing * Time.deltaTime);
    }

    private void ApplyTransform()
    {
        transform.position = currentPosition;
        transform.localScale = new Vector3(currentScale, currentScale, 1f);
    }

    public Vector3 GetPlayerPosition() => currentPosition;
    public float GetPlayerYNormalized()
    {
        float yRange = maxY - minY;
        return (currentPosition.y - minY) / yRange; // 0 = bottom (close), 1 = top (far)
    }
}
