using UnityEngine;

/// <summary>
/// Manages 3D character movement on an invisible ground plane with depth-based scaling.
/// Constrains movement to a ground plane and scales character based on Z-depth for 2.5D effect.
/// Part of the 3D/2D hybrid rendering system.
/// 
/// © 2026 Saoriverse Console. All rights reserved.
/// This code is proprietary and confidential. Unauthorized copying, modification, or distribution
/// is strictly prohibited. See LICENSE_COMMERCIAL.md and NDA_TEMPLATE.md for licensing information.
/// </summary>
public class CharacterGroundMovement : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float groundPlaneY = 0f;  // Y-value of the ground plane

    [Header("Depth Scaling")]
    [SerializeField] private float minZ = -5f;   // Farthest depth (smallest scale)
    [SerializeField] private float maxZ = 5f;    // Closest depth (largest scale)
    [SerializeField] private float minScale = 0.6f;
    [SerializeField] private float maxScale = 1.5f;
    [SerializeField] private float scaleSmoothing = 5f;

    [Header("Bounds")]
    [SerializeField] private float minX = -10f;
    [SerializeField] private float maxX = 10f;

    private CharacterController characterController;
    private Transform modelTransform;  // The visual model (child of this object)
    private Vector3 movementVelocity;
    private float currentScale = 1f;

    private void Start()
    {
        // Find the CharacterController on this character (UMA avatar)
        characterController = GetComponent<CharacterController>();

        // Find the visual model transform (usually first child)
        if (transform.childCount > 0)
        {
            modelTransform = transform.GetChild(0);
        }
        else
        {
            modelTransform = transform;
        }

        currentScale = transform.localScale.x;
    }

    private void Update()
    {
        HandleMovement();
        UpdateDepthScale();
        ConstrainToBounds();
    }

    private void HandleMovement()
    {
        // Get input (WASD or arrow keys)
        float moveX = Input.GetAxis("Horizontal");  // A/D or Left/Right
        float moveZ = Input.GetAxis("Vertical");    // W/S or Up/Down

        // Create movement direction (X and Z axes only - stays on ground plane)
        Vector3 movement = new Vector3(moveX, 0, moveZ).normalized * moveSpeed;

        // Apply gravity to keep on ground
        movement.y = -9.81f * Time.deltaTime;

        // Use CharacterController if available, otherwise direct transform
        if (characterController != null)
        {
            characterController.Move(movement * Time.deltaTime);
        }
        else
        {
            transform.Translate(movement * Time.deltaTime, Space.World);
        }
    }

    private void UpdateDepthScale()
    {
        // Get Z-position (depth)
        float currentZ = transform.position.z;

        // Normalize Z to 0-1 range
        float zNormalized = Mathf.InverseLerp(minZ, maxZ, currentZ);
        zNormalized = Mathf.Clamp01(zNormalized);

        // Calculate target scale (closer = bigger, farther = smaller)
        float targetScale = Mathf.Lerp(minScale, maxScale, zNormalized);

        // Smooth scale transition
        currentScale = Mathf.Lerp(currentScale, targetScale, scaleSmoothing * Time.deltaTime);

        // Apply scale to character
        transform.localScale = new Vector3(currentScale, currentScale, currentScale);
    }

    private void ConstrainToBounds()
    {
        // Keep character within bounds
        Vector3 pos = transform.position;
        pos.x = Mathf.Clamp(pos.x, minX, maxX);
        pos.y = groundPlaneY;  // Snap to ground
        transform.position = pos;
    }

    // Optional: Set specific position on ground plane
    public void SetPositionOnGround(float x, float z)
    {
        Vector3 newPos = transform.position;
        newPos.x = Mathf.Clamp(x, minX, maxX);
        newPos.z = Mathf.Clamp(z, minZ, maxZ);
        newPos.y = groundPlaneY;
        transform.position = newPos;
    }
}
