using UnityEngine;
#pragma warning disable CS0618  // Suppress Input Manager deprecation warning (still functional)

namespace Velinor.Core
{
    /// <summary>
    /// SimpleCharacterMovement - Basic WASD + Mouse Look for physics-based characters
    /// Applies forces to Rigidbody instead of using CharacterController
    /// </summary>
    public class SimpleCharacterMovement : MonoBehaviour
    {
        [Header("Movement")]
        [SerializeField] private float moveSpeed = 5f;
        [SerializeField] private float groundDrag = 5f;
        public bool isMovementLocked = false;

        [Header("Ground Check")]
        [SerializeField] private float groundCheckDistance = 1.5f;

        [Header("Camera")]
        public Camera mainCamera;
        [SerializeField] private float mouseSensitivity = 2f;

        [Header("Camera Zoom / First Person")]
        [SerializeField] private float minZoomDistance = 0f; // 0 = First Person Mode
        [SerializeField] private float maxZoomDistance = 5f;
        [SerializeField] private float currentZoomDistance = 0f; // Default to 0f (First Person) as requested!
        [SerializeField] private float zoomSensitivity = 2f;
        [SerializeField] private SkinnedMeshRenderer playerMesh;

        private Rigidbody rb;
        private bool isGrounded;
        private float yRotation = 0f;
        private Animator animator;
        
        // Debug tracking
        private RaycastHit lastGroundHit;
        private float debugLogTimer = 0f;
        private const float DEBUG_LOG_INTERVAL = 0.5f; // Log every 0.5 seconds

        private void Start()
        {
            rb = GetComponent<Rigidbody>();
            if (rb == null)
            {
                Debug.LogWarning("SimpleCharacterMovement: No Rigidbody found");
                return;
            }

            animator = GetComponent<Animator>();
            if (animator == null)
            {
                Debug.LogWarning("SimpleCharacterMovement: No Animator found - animations disabled");
            }

            if (mainCamera == null)
            {
                mainCamera = Camera.main;
            }

            // Find player skinned mesh renderer in children if unassigned
            if (playerMesh == null)
            {
                playerMesh = GetComponentInChildren<SkinnedMeshRenderer>();
            }

            // Apply initial zoom state
            ApplyZoom();

            // Start with unlocked, visible cursor
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
            
            Debug.Log("SimpleCharacterMovement: Ready (WASD to move, Right-Click + Drag Mouse to look, Scroll Wheel to Zoom)");
        }

        private void Update()
        {
            if (rb == null) return;

            // Ground check using raycast with LAYER MASK (only hit Foreground layer)
            // Raycast originates from character root position, pointing down
            // Character is at eye level (Y=0.9), collider bottom is at Y=0
            // So we raycast from Y=0.9 down 1.5 units, which reaches Y=-0.6 (well below ground at Y=0)
            int foregroundMask = LayerMask.GetMask("Foreground");
            isGrounded = Physics.Raycast(transform.position, Vector3.down, out lastGroundHit, groundCheckDistance, foregroundMask);

            // Handle input
            HandleMovement();
            HandleCamera();
            HandleCursorToggle();
            
            // Debug logging
            DebugGroundState();
        }
        
        private void DebugGroundState()
        {
            debugLogTimer += Time.deltaTime;
            if (debugLogTimer >= DEBUG_LOG_INTERVAL)
            {
                debugLogTimer = 0f;
                
                string groundInfo = isGrounded 
                    ? $"✅ GROUNDED - Object: '{lastGroundHit.collider.gameObject.name}' | Position: {transform.position:F2} | Hit: {lastGroundHit.point:F2}"
                    : $"❌ FREEFALL - Position: {transform.position:F2} | Velocity: {rb.linearVelocity:F2}";
                
                Debug.Log($"[PLAYER STATE] {groundInfo}");
            }
        }

        private void HandleMovement()
        {
            if (isMovementLocked)
            {
                rb.linearVelocity = new Vector3(0f, rb.linearVelocity.y, 0f);
                rb.linearDamping = groundDrag;
                if (animator != null)
                {
                    animator.SetFloat("Speed", 0f);
                    animator.SetFloat("MotionSpeed", 0f);
                    animator.SetBool("Grounded", isGrounded);
                }
                return;
            }

            float horizontal = Input.GetAxis("Horizontal");
            float vertical = Input.GetAxis("Vertical");

            // Calculate movement direction
            Vector3 moveDirection = transform.forward * vertical + transform.right * horizontal;
            moveDirection.y = 0; // Don't move up/down with WASD
            moveDirection = moveDirection.normalized;

            // Apply movement with drag
            rb.linearVelocity = new Vector3(
                moveDirection.x * moveSpeed,
                rb.linearVelocity.y, // Preserve vertical velocity (gravity)
                moveDirection.z * moveSpeed
            );

            // Apply drag
            rb.linearDamping = isGrounded ? groundDrag : 1f;
            
            // Update animator parameters for animations
            if (animator != null)
            {
                // Speed for walk/run blend tree (0=idle, 1=walk, 2=run)
                float horizontalSpeed = new Vector3(rb.linearVelocity.x, 0, rb.linearVelocity.z).magnitude;
                animator.SetFloat("Speed", horizontalSpeed / moveSpeed); // Normalize to 0-1 range
                animator.SetFloat("MotionSpeed", horizontalSpeed);
                animator.SetBool("Grounded", isGrounded);
                
                if (!isGrounded)
                {
                    animator.SetBool("FreeFall", true);
                }
                else if (isGrounded && animator.GetBool("FreeFall"))
                {
                    animator.SetBool("FreeFall", false);
                }
            }
            
            // Handle jumping
            if (Input.GetKeyDown(KeyCode.Space) && isGrounded)
            {
                rb.linearVelocity = new Vector3(rb.linearVelocity.x, 5f, rb.linearVelocity.z);
                
                if (animator != null)
                {
                    animator.SetBool("Jump", true);
                }
                
                Debug.Log("Jump!");
            }
            else if (isGrounded && animator != null && animator.GetBool("Jump"))
            {
                animator.SetBool("Jump", false);
            }
        }

        private void HandleCamera()
        {
            if (mainCamera == null) return;

            // Handle Zoom Input via Scroll Wheel
            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) > 0.005f)
            {
                currentZoomDistance -= scroll * zoomSensitivity;
                currentZoomDistance = Mathf.Clamp(currentZoomDistance, minZoomDistance, maxZoomDistance);
            }

            ApplyZoom();

            // Only rotate camera when Right-Click (Mouse Button 1) is held down, and movement is not locked (e.g. not in dialogue)
            if (Input.GetMouseButton(1) && !isMovementLocked)
            {
                // Lock and hide the cursor during camera control
                Cursor.lockState = CursorLockMode.Locked;
                Cursor.visible = false;

                float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
                float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;

                // Rotate character left/right
                transform.Rotate(0, mouseX, 0);

                // Rotate camera up/down
                yRotation -= mouseY;
                yRotation = Mathf.Clamp(yRotation, -90f, 90f);
                mainCamera.transform.localRotation = Quaternion.Euler(yRotation, 0, 0);
            }
            else
            {
                // Release lock and show cursor when not right-clicking or when movement is locked
                if (!Input.GetMouseButton(1) || isMovementLocked)
                {
                    Cursor.lockState = CursorLockMode.None;
                    Cursor.visible = true;
                }
            }
        }

        private void ApplyZoom()
        {
            if (mainCamera == null) return;

            if (currentZoomDistance <= 0.1f)
            {
                // First Person Mode
                mainCamera.transform.localPosition = new Vector3(0f, 1.60f, 0f);
                if (playerMesh != null)
                {
                    playerMesh.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.ShadowsOnly;
                }
            }
            else
            {
                // Third Person Mode
                Vector3 headLocalPos = new Vector3(0f, 1.60f, 0f);
                Vector3 targetLocalPos = headLocalPos - Vector3.forward * currentZoomDistance;

                Vector3 worldHeadPos = transform.TransformPoint(headLocalPos);
                Vector3 worldTargetPos = transform.TransformPoint(targetLocalPos);
                Vector3 direction = worldTargetPos - worldHeadPos;

                RaycastHit hit;
                int cameraClipMask = LayerMask.GetMask("Foreground", "Midground", "Default");
                if (Physics.Raycast(worldHeadPos, direction.normalized, out hit, direction.magnitude, cameraClipMask))
                {
                    Vector3 worldHitPos = hit.point + hit.normal * 0.2f;
                    mainCamera.transform.position = worldHitPos;
                }
                else
                {
                    mainCamera.transform.localPosition = targetLocalPos;
                }

                if (playerMesh != null)
                {
                    playerMesh.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.On;
                }
            }
        }

        private void HandleCursorToggle()
        {
            // Escape remains as a robust escape hatch to free the cursor if needed
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                Cursor.lockState = CursorLockMode.None;
                Cursor.visible = true;
            }
        }

        /// <summary>
        /// Called by animation event when character lands after jump
        /// Triggered by the JumpLand animation's AnimationEvent
        /// </summary>
        public void OnLand()
        {
            // Character landed - animation event callback
            // Can add landing effects here (dust, sound, etc.)
            Debug.Log("Character landed!");
        }

        /// <summary>
        /// Called by animation event when footstep occurs during walk/run
        /// Single event for both left and right feet
        /// </summary>
        public void OnFootstep()
        {
            // Footstep animation event
            // Can add footstep sound or particle effect here
            Debug.Log("Footstep!");
        }

        /// <summary>
        /// Called by animation event for left foot landing (if using separate events)
        /// </summary>
        public void FootstepL()
        {
            // Left footstep event
            Debug.Log("Left footstep!");
        }

        /// <summary>
        /// Called by animation event for right foot landing (if using separate events)
        /// </summary>
        public void FootstepR()
        {
            // Right footstep event
            Debug.Log("Right footstep!");
        }

        /// <summary>
        /// Called by animation event when jump animation starts
        /// </summary>
        public void OnJump()
        {
            // Jump animation started
            Debug.Log("Jump animation triggered!");
        }

        public bool IsGrounded => isGrounded;
        
        /// <summary>
        /// Visual debug: Draw raycast line in scene view
        /// </summary>
        private void OnDrawGizmos()
        {
            if (!Application.isPlaying) return;
            
            // Draw ground detection raycast
            Vector3 rayStart = transform.position;
            Vector3 rayEnd = rayStart + Vector3.down * groundCheckDistance;
            
            // Green line if grounded, red if in freefall
            Gizmos.color = isGrounded ? Color.green : Color.red;
            Gizmos.DrawLine(rayStart, rayEnd);
            
            // Mark the raycast endpoint
            Gizmos.color = isGrounded ? Color.green : Color.red;
            Gizmos.DrawWireSphere(rayEnd, 0.1f);
        }
    }
}
#pragma warning restore CS0618
