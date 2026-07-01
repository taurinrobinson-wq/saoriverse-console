using UnityEngine;

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
        [SerializeField] private Camera mainCamera;
        [SerializeField] private float mouseSensitivity = 2f;

        private Rigidbody rb;
        private bool isGrounded;
        private float yRotation = 0f;

        private void Start()
        {
            rb = GetComponent<Rigidbody>();
            if (rb == null)
            {
                Debug.LogWarning("SimpleCharacterMovement: No Rigidbody found");
                return;
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

        public bool IsGrounded => isGrounded;
    }
}
