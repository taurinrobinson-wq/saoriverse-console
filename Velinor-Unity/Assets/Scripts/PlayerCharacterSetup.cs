using UnityEngine;

/// <summary>
/// Complete player character setup for Velinor 3D/2D hybrid system.
/// Handles UMA character initialization, ground plane integration, scene spawning,
/// and depth-based scaling. Drop this on your player character GameObject.
/// 
/// Setup:
/// 1. Create empty GameObject named "Player" with tag "Player"
/// 2. Add CharacterController component
/// 3. Add this script
/// 4. Create UMA character as child, disable initially
/// 5. Create invisible ground plane in scene (see SYSTEMS_INTEGRATION_GUIDE.md)
/// 6. Script will auto-initialize on scene load
/// 
/// © 2026 Saoriverse Console. All rights reserved.
/// This code is proprietary and confidential. Unauthorized copying, modification, or distribution
/// is strictly prohibited. See LICENSE_COMMERCIAL.md and NDA_TEMPLATE.md for licensing information.
/// </summary>
public class PlayerCharacterSetup : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private CharacterController characterController;
    [SerializeField] private Transform umaCharacterTransform;  // Child UMA avatar
    [SerializeField] private Collider groundPlaneCollider;     // Ground plane collider

    [Header("Movement")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float groundDrag = 0.1f;

    [Header("Depth Scaling (3D/2D Hybrid)")]
    [SerializeField] private float minZ = -5f;
    [SerializeField] private float maxZ = 5f;
    [SerializeField] private float minScale = 0.6f;
    [SerializeField] private float maxScale = 1.5f;
    [SerializeField] private float scaleSmoothing = 5f;

    [Header("Bounds")]
    [SerializeField] private float minX = -10f;
    [SerializeField] private float maxX = 10f;
    [SerializeField] private float groundPlaneY = 0f;  // Y position of ground

    [Header("Spawning")]
    [SerializeField] private bool autoPositionOnSpawn = true;
    [SerializeField] private Vector3 defaultSpawnOffset = new Vector3(0, 0.5f, 0);  // Above ground

    private Vector3 movementVelocity;
    private float currentScale = 1f;
    private CharacterController cc;
    private bool isInitialized = false;

    private void Awake()
    {
        // Ensure CharacterController exists
        cc = GetComponent<CharacterController>();
        if (cc == null)
        {
            cc = gameObject.AddComponent<CharacterController>();
        }

        // Auto-find UMA character if not assigned
        if (umaCharacterTransform == null && transform.childCount > 0)
        {
            umaCharacterTransform = transform.GetChild(0);
        }

        // Auto-find ground plane collider in scene
        if (groundPlaneCollider == null)
        {
            Collider[] allColliders = FindObjectsByType<Collider>(FindObjectsInactive.Exclude, FindObjectsSortMode.None);
            foreach (var col in allColliders)
            {
                if (col.name.ToLower().Contains("ground") || col.name.ToLower().Contains("plane"))
                {
                    groundPlaneCollider = col;
                    break;
                }
            }
        }

        // Get ground Y from plane if found
        if (groundPlaneCollider != null)
        {
            groundPlaneY = groundPlaneCollider.bounds.center.y;
        }

        currentScale = transform.localScale.x;
        isInitialized = true;
    }

    private void Start()
    {
        // Position on spawn point or default location
        if (autoPositionOnSpawn)
        {
            PositionOnSpawnPoint();
        }
    }

    private void Update()
    {
        if (!isInitialized) return;

        HandleMovement();
        UpdateDepthScale();
        ConstrainToBounds();
    }

    /// <summary>
    /// Handles WASD movement on the ground plane (X and Z axes only).
    /// </summary>
    private void HandleMovement()
    {
        // Get input
        float moveX = Input.GetAxis("Horizontal");
        float moveZ = Input.GetAxis("Vertical");

        // Movement vector (X and Z only, no Y)
        Vector3 movement = new Vector3(moveX, 0, moveZ).normalized * moveSpeed;

        // Apply gravity to keep on ground
        movement.y = -9.81f * Time.deltaTime;

        // Move via CharacterController
        cc.Move(movement * Time.deltaTime);
    }

    /// <summary>
    /// Updates character scale based on Z-depth for depth-of-field effect.
    /// Closer characters (lower Z) appear larger; farther characters (higher Z) appear smaller.
    /// </summary>
    private void UpdateDepthScale()
    {
        // Get current Z position
        float currentZ = transform.position.z;

        // Normalize Z to 0-1 range (0 = farther/minZ, 1 = closer/maxZ)
        float zNormalized = Mathf.InverseLerp(minZ, maxZ, currentZ);
        zNormalized = Mathf.Clamp01(zNormalized);

        // Calculate target scale
        float targetScale = Mathf.Lerp(minScale, maxScale, zNormalized);

        // Smooth scale transition
        currentScale = Mathf.Lerp(currentScale, targetScale, scaleSmoothing * Time.deltaTime);

        // Apply scale
        transform.localScale = new Vector3(currentScale, currentScale, currentScale);
    }

    /// <summary>
    /// Keeps character within defined bounds and locked to ground Y-position.
    /// </summary>
    private void ConstrainToBounds()
    {
        Vector3 pos = transform.position;

        // Constrain X
        pos.x = Mathf.Clamp(pos.x, minX, maxX);

        // Lock to ground Y
        pos.y = groundPlaneY + defaultSpawnOffset.y;

        // Constrain Z (optional - remove if you want infinite depth)
        // pos.z = Mathf.Clamp(pos.z, minZ, maxZ);

        transform.position = pos;
    }

    /// <summary>
    /// Positions player on spawn point from SceneSpawnManager.
    /// Called at Start() if autoPositionOnSpawn is enabled.
    /// </summary>
    private void PositionOnSpawnPoint()
    {
        // Try to find a SpawnPoint in the scene
        SpawnPoint[] spawnPoints = FindObjectsByType<SpawnPoint>(FindObjectsInactive.Exclude, FindObjectsSortMode.None);

        if (spawnPoints.Length == 0)
        {
            // No spawn points - use default position
            SetPositionOnGround(0, 0);
            return;
        }

        // Find matching spawn point (by ID from SceneSpawnManager)
        string targetSpawnID = SceneSpawnManager.nextSpawnID;

        foreach (var spawnPoint in spawnPoints)
        {
            if (spawnPoint.SpawnID == targetSpawnID || string.IsNullOrEmpty(targetSpawnID))
            {
                // Found spawn point - position there
                Vector3 spawnPos = spawnPoint.transform.position;
                SetPositionOnGround(spawnPos.x, spawnPos.z);
                return;
            }
        }

        // No matching spawn point - use first one or default
        if (spawnPoints.Length > 0)
        {
            Vector3 spawnPos = spawnPoints[0].transform.position;
            SetPositionOnGround(spawnPos.x, spawnPos.z);
        }
        else
        {
            SetPositionOnGround(0, 0);
        }
    }

    /// <summary>
    /// Manually set character position on ground plane.
    /// </summary>
    public void SetPositionOnGround(float x, float z)
    {
        Vector3 newPos = new Vector3(
            Mathf.Clamp(x, minX, maxX),
            groundPlaneY + defaultSpawnOffset.y,
            z
        );
        transform.position = newPos;
    }

    /// <summary>
    /// Get current ground plane Y value.
    /// </summary>
    public float GetGroundY() => groundPlaneY;

    /// <summary>
    /// Update ground plane reference (call if ground plane moves or changes).
    /// </summary>
    public void UpdateGroundPlaneReference(Collider newGroundPlane)
    {
        groundPlaneCollider = newGroundPlane;
        if (groundPlaneCollider != null)
        {
            groundPlaneY = groundPlaneCollider.bounds.center.y;
        }
    }

    /// <summary>
    /// Get current scale for external systems (VFX, animations, etc).
    /// </summary>
    public float GetCurrentScale() => currentScale;

#if UNITY_EDITOR
    private void OnDrawGizmosSelected()
    {
        // Draw bounds in editor
        Gizmos.color = Color.green;
        
        // Draw X bounds
        Vector3 leftBound = new Vector3(minX, groundPlaneY, 0);
        Vector3 rightBound = new Vector3(maxX, groundPlaneY, 0);
        Gizmos.DrawLine(leftBound, rightBound);
        
        // Draw Z bounds
        Vector3 farBound = new Vector3(0, groundPlaneY, minZ);
        Vector3 nearBound = new Vector3(0, groundPlaneY, maxZ);
        Gizmos.DrawLine(farBound, nearBound);
        
        // Draw depth scale range
        Gizmos.color = Color.cyan;
        Gizmos.DrawWireSphere(new Vector3(0, groundPlaneY, minZ), 0.5f);  // Far (small)
        Gizmos.DrawWireSphere(new Vector3(0, groundPlaneY, maxZ), 1.0f);  // Near (large)
    }
#endif
}
