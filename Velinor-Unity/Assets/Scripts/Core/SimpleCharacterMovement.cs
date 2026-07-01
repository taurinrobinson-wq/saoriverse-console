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

        [Header("Ground Check")]
        [SerializeField] private float groundCheckDistance = 0.1f;

        [Header("Camera")]
        public Camera mainCamera;
        [SerializeField] private float mouseSensitivity = 2f;

        private Rigidbody rb;
        private bool isGrounded;
        private float yRotation = 0f;
        private Animator animator;

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

            // Lock cursor
            Cursor.lockState = CursorLockMode.Locked;
            
            Debug.Log("SimpleCharacterMovement: Ready (WASD to move, Mouse to look, ESC to unlock cursor)");
        }

        private void Update()
        {
            if (rb == null) return;

            // Ground check using raycast
            isGrounded = Physics.Raycast(transform.position, Vector3.down, groundCheckDistance);

            // Handle input
            HandleMovement();
            HandleCamera();
            HandleCursorToggle();
        }

        private void HandleMovement()
        {
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

            float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
            float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;

            // Rotate character left/right
            transform.Rotate(0, mouseX, 0);

            // Rotate camera up/down
            yRotation -= mouseY;
            yRotation = Mathf.Clamp(yRotation, -90f, 90f);
            mainCamera.transform.localRotation = Quaternion.Euler(yRotation, 0, 0);
        }

        private void HandleCursorToggle()
        {
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                Cursor.lockState = Cursor.lockState == CursorLockMode.Locked ? 
                    CursorLockMode.None : CursorLockMode.Locked;
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
    }
}
#pragma warning restore CS0618
