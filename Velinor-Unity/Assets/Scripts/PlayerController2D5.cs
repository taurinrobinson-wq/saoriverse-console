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
using Velinor.Core;

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
    [SerializeField] private float minX = -10f;
    [SerializeField] private float maxX = 10f;
    [SerializeField] private float minY = -5f;
    [SerializeField] private float maxY = 5f;

    [Header("Depth Scaling")]
    [SerializeField] private float minScale = 0.5f; // Smallest when at top (farthest)
    [SerializeField] private float maxScale = 1.5f; // Largest when at bottom (closest)
    [SerializeField] private float scaleSmoothing = 10f; // Increased for faster visual feedback

    [Header("Visuals")]
    [SerializeField] private SpriteRenderer spriteRenderer;

    private Vector3 currentPosition;
    private float currentScale = 1f;
    private SpriteRenderer cachedSpriteRenderer;
    private Animator animator;
    private CharacterController characterController;

    // Animation parameter hashes
    private int animIDSpeed;
    private int animIDGrounded;
    private int animIDMotionSpeed;

    private void Start()
    {
        cachedSpriteRenderer = spriteRenderer != null ? spriteRenderer : GetComponent<SpriteRenderer>();
        animator = GetComponent<Animator>();
        characterController = GetComponent<CharacterController>();

        // ENSURE skinWidth is optimized for small colliders
        if (characterController != null)
        {
            characterController.skinWidth = 0.03f;
            characterController.minMoveDistance = 0f;
        }

        // Ensure player has a collider for collision detection
        if (GetComponent<Collider>() == null && characterController == null)
        {
            SphereCollider sphere = gameObject.AddComponent<SphereCollider>();
            sphere.radius = 0.3f;
            sphere.center = Vector3.zero;
            Debug.Log("[PlayerController2D5] SphereCollider created with radius=0.3 at base");
        }

        // Optimize CharacterController for 2.5D (depth is Y, not height)
        if (characterController != null)
        {
            characterController.height = 0.2f;
            characterController.center = Vector3.zero;
            characterController.radius = 0.3f;
        }

        currentPosition = transform.position;

        // Immediate scale calculation for first frame
        UpdateDepthScaling(true);
        ApplyTransform();

        if (animator != null)
        {
            animIDSpeed = Animator.StringToHash("Speed");
            animIDGrounded = Animator.StringToHash("Grounded");
            animIDMotionSpeed = Animator.StringToHash("MotionSpeed");

            animator.SetBool(animIDGrounded, true);
            animator.SetFloat(animIDMotionSpeed, 1f);
        }
    }

    private void Update()
    {
        // If position was changed externally (e.g., by spawn manager), sync currentPosition and update scale immediately
        if (Vector3.Distance(transform.position, currentPosition) > 0.01f)
        {
            currentPosition = transform.position;
            UpdateDepthScaling(true); // Force immediate scale to prevent lerp popping/shrinking
            ApplyTransform();
        }

        HandleMovement();
        HandleInteraction();
        UpdateDepthScaling(false);
        ApplyTransform();
    }

    /// <summary>
    /// Teleports the player to a new position and updates scale immediately.
    /// Use this for scene spawns and transitions.
    /// </summary>
    public void Teleport(Vector3 newPosition)
    {
        currentPosition = newPosition;
        transform.position = newPosition;
        UpdateDepthScaling(true);
        ApplyTransform();
    }

    private void HandleMovement()
    {
        Vector2 input = Vector2.zero;

        // Force currentPosition to stay on the Z=0 plane to prevent drift
        currentPosition.z = 0;
        if (transform.position.z != 0)
        {
            Vector3 pos = transform.position;
            pos.z = 0;
            transform.position = pos;
        }

        // Get raw input
#if ENABLE_INPUT_SYSTEM
        var keyboard = Keyboard.current;
        if (keyboard != null)
        {
            if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed) input.x += 1f;
            if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed) input.x -= 1f;
            if (keyboard.wKey.isPressed || keyboard.upArrowKey.isPressed) input.y += 1f;
            if (keyboard.sKey.isPressed || keyboard.downArrowKey.isPressed) input.y -= 1f;
        }
#else
        if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) input.x += 1f;
        if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) input.x -= 1f;
        if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow)) input.y += 1f;
        if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow)) input.y -= 1f;
#endif

        // Calculate world movement
        Vector3 moveDir = new Vector3(input.x, input.y, 0).normalized;
        Vector3 movement = moveDir * moveSpeed * Time.deltaTime;

        // Clamp to bounds
        Vector3 newPosition = currentPosition + movement;
        newPosition.x = Mathf.Clamp(newPosition.x, minX, maxX);
        newPosition.y = Mathf.Clamp(newPosition.y, minY, maxY);

        // 2D & 3D Obstacle Collision Handling with independent X and Y axis sliding
        if (movement.sqrMagnitude > 0.000001f)
        {
            Vector2 colOffset = new Vector2(0f, 0.25f);
            float colRadius = 0.35f;

            // Test X movement independently
            Vector2 checkPosX = new Vector2(currentPosition.x + movement.x, currentPosition.y) + colOffset;
            bool blockedX = false;

            Collider2D[] hits2DX = Physics2D.OverlapCircleAll(checkPosX, colRadius);
            foreach (var h2d in hits2DX)
            {
                if (!h2d.isTrigger && h2d.gameObject != gameObject && !h2d.transform.IsChildOf(transform))
                {
                    blockedX = true;
                    break;
                }
            }

            if (!blockedX && Physics.CheckSphere(new Vector3(checkPosX.x, checkPosX.y, 0f), colRadius, ~0, QueryTriggerInteraction.Ignore))
            {
                Collider[] hits3D = Physics.OverlapSphere(new Vector3(checkPosX.x, checkPosX.y, 0f), colRadius, ~0, QueryTriggerInteraction.Ignore);
                foreach (var h in hits3D)
                {
                    if (h.gameObject != gameObject && !h.transform.IsChildOf(transform))
                    {
                        blockedX = true;
                        break;
                    }
                }
            }

            if (!blockedX)
            {
                currentPosition.x = Mathf.Clamp(currentPosition.x + movement.x, minX, maxX);
            }

            // Test Y movement independently
            Vector2 checkPosY = new Vector2(currentPosition.x, currentPosition.y + movement.y) + colOffset;
            bool blockedY = false;

            Collider2D[] hits2DY = Physics2D.OverlapCircleAll(checkPosY, colRadius);
            foreach (var h2d in hits2DY)
            {
                if (!h2d.isTrigger && h2d.gameObject != gameObject && !h2d.transform.IsChildOf(transform))
                {
                    blockedY = true;
                    break;
                }
            }

            if (!blockedY && Physics.CheckSphere(new Vector3(checkPosY.x, checkPosY.y, 0f), colRadius, ~0, QueryTriggerInteraction.Ignore))
            {
                Collider[] hits3D = Physics.OverlapSphere(new Vector3(checkPosY.x, checkPosY.y, 0f), colRadius, ~0, QueryTriggerInteraction.Ignore);
                foreach (var h in hits3D)
                {
                    if (h.gameObject != gameObject && !h.transform.IsChildOf(transform))
                    {
                        blockedY = true;
                        break;
                    }
                }
            }

            if (!blockedY)
            {
                currentPosition.y = Mathf.Clamp(currentPosition.y + movement.y, minY, maxY);
            }
        }

        // Use CharacterController for collision detection if present and enabled
        if (characterController != null && characterController.enabled)
        {
            characterController.Move(currentPosition - transform.position);
            currentPosition = transform.position;
        }

        // Update Animator
        if (animator != null)
        {
            // StarterAssets blend tree: 0=idle, 2=walk, 6=run
            float speedParam = input.sqrMagnitude > 0.01f ? 2.0f : 0f;
            animator.SetFloat(animIDSpeed, speedParam);
            animator.SetFloat(animIDMotionSpeed, 1f);
            animator.SetBool(animIDGrounded, true);
        }

        // Rotate player to face movement direction (8-way facing)
        if (input.sqrMagnitude > 0.01f)
        {
            float targetAngle = Mathf.Atan2(input.x, input.y) * Mathf.Rad2Deg;
            transform.rotation = Quaternion.Euler(0, targetAngle, 0);
        }
    }

    private void HandleInteraction()
    {
        bool dialogueKeyPressed = false;
#if ENABLE_INPUT_SYSTEM
        var keyboard = Keyboard.current;
        if (keyboard != null && keyboard.gKey.wasPressedThisFrame)
        {
            dialogueKeyPressed = true;
        }
#else
        if (Input.GetKeyDown(KeyCode.G))
        {
            dialogueKeyPressed = true;
        }
#endif

        if (dialogueKeyPressed)
        {
            // Check for IInteractable objects in proximity (3.0 unit radius)
            Collider[] colliders = Physics.OverlapSphere(transform.position, 3.0f);
            Debug.Log($"[PlayerController2D5] Player Position: {transform.position}, Radius: 3.0f, Found {colliders.Length} colliders in range");

            foreach (var col in colliders)
            {
                Debug.Log($"[PlayerController2D5]   - Checking collider: {col.gameObject.name}");
                IInteractable interactable = col.GetComponent<IInteractable>();
                if (interactable != null)
                {
                    Debug.Log($"[PlayerController2D5] ✓ Found IInteractable on {col.gameObject.name} - calling Interact()");
                    interactable.Interact(gameObject);
                    break; // Only interact with the first one found
                }
                else
                {
                    Debug.Log($"[PlayerController2D5]   - No IInteractable component on {col.gameObject.name}");
                }
            }
        }
    }

    private void UpdateDepthScaling(bool immediate)
    {
        // Calculate scale based on Y position (closer to camera/bottom = larger, farther/top = smaller)
        float yRange = maxY - minY;
        if (yRange <= 0.001f) yRange = 0.001f;
        float yNormalized = (currentPosition.y - minY) / yRange;
        yNormalized = Mathf.Clamp01(yNormalized);

        // Larger at minY (closest), smaller at maxY (farthest)
        // Since we want larger at bottom (minY), it should be Lerp(maxScale, minScale, yNormalized)
        float targetScale = Mathf.Lerp(maxScale, minScale, yNormalized);

        if (immediate)
            currentScale = targetScale;
        else
            currentScale = Mathf.Lerp(currentScale, targetScale, scaleSmoothing * Time.deltaTime);
    }

    private void ApplyTransform()
    {
        currentPosition.z = 0;
        
        if (characterController != null && characterController.enabled)
        {
            transform.position = currentPosition;
        }
        else
        {
            transform.position = currentPosition;
        }
        transform.localScale = new Vector3(currentScale, currentScale, currentScale);
    }

    public Vector3 GetPlayerPosition() => currentPosition;

    /// <summary>
    /// Set the player's movement speed (used by DialogueManager for dialogue effects).
    /// </summary>
    public void SetMoveSpeed(float newSpeed)
    {
        moveSpeed = newSpeed;
        Debug.Log($"[PlayerController2D5] Move speed changed to: {moveSpeed}");
    }

    // ============================================================
    // ANIMATION EVENT RECEIVERS
    // ============================================================

    /// <summary>
    /// Suppress warning: 'OnFootstep' has no receiver. 
    /// Matches StarterAssets AnimationEvent signature.
    /// </summary>
    public void OnFootstep(AnimationEvent animationEvent)
    {
        // Event receiver for walk/run animations
    }

    /// <summary>
    /// Suppress warning: 'OnLand' has no receiver
    /// </summary>
    public void OnLand(AnimationEvent animationEvent)
    {
        // Event receiver for landing animations
    }

    /// <summary>
    /// Suppress warning: 'OnJump' has no receiver
    /// </summary>
    public void OnJump(AnimationEvent animationEvent)
    {
        // Event receiver for jump start
    }

    public void FootstepL(AnimationEvent animationEvent) { }
    public void FootstepR(AnimationEvent animationEvent) { }
}
