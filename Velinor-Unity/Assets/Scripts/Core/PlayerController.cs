using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// PlayerController - First-person and third-person character movement
    /// 
    /// Controls:
    /// - WASD: Move forward/backward/strafe left/right
    /// - Mouse: Look around (first-person) or rotate camera (third-person)
    /// - Space: Jump
    /// - Shift: Sprint (2x speed)
    /// - ESC: Toggle cursor lock
    /// - E: Interact
    /// </summary>
    public class PlayerController : MonoBehaviour
    {
        [Header("Movement")]
        [SerializeField] private float moveSpeed = 5f;
        [SerializeField] private float sprintSpeed = 10f;
        [SerializeField] private float jumpForce = 5f;
        [SerializeField] private float groundDrag = 5f;
        [SerializeField] private float airDrag = 2f;

        [Header("Ground Check")]
        [SerializeField] private LayerMask groundLayer;
        [SerializeField] private float groundCheckDistance = 0.2f;

        [Header("Camera")]
        [SerializeField] private Camera mainCamera;
        [SerializeField] private float mouseSensitivity = 2f;
        [SerializeField] private float maxLookAngle = 90f;

        private Rigidbody rb;
        private bool isGrounded;
        private float yRotation = 0f;

        private void Start()
        {
            rb = GetComponent<Rigidbody>();
            
            if (rb == null)
            {
                rb = gameObject.AddComponent<Rigidbody>();
                rb.mass = 1;
                rb.drag = groundDrag;
                rb.angularDrag = 0.05f;
                rb.useGravity = true;
                rb.constraints = RigidbodyConstraints.FreezeRotation;
            }

            if (mainCamera == null)
            {
                mainCamera = Camera.main;
            }

            // Set ground layer to all layers if not configured
            if (groundLayer == 0)
            {
                groundLayer = -1;
            }

            // Lock and hide cursor
            Cursor.lockState = CursorLockMode.Locked;
        }

        private void Update()
        {
            // Check if grounded using raycast
            isGrounded = Physics.Raycast(transform.position, Vector3.down, groundCheckDistance + rb.velocity.y * Time.deltaTime, groundLayer);

            // Apply drag based on ground state
            rb.drag = isGrounded ? groundDrag : airDrag;

            // Handle input
            HandleMovement();
            HandleJump();
            HandleCamera();
            HandleCursorToggle();
            HandleInteraction();
        }

        private void HandleMovement()
        {
            // Get input
            float horizontal = Input.GetAxis("Horizontal");
            float vertical = Input.GetAxis("Vertical");

            // Determine speed
            float currentSpeed = Input.GetKey(KeyCode.LeftShift) ? sprintSpeed : moveSpeed;

            // Calculate movement direction relative to player facing direction
            Vector3 moveDirection = transform.forward * vertical + transform.right * horizontal;
            moveDirection.y = 0; // Don't move up/down with WASD
            moveDirection = moveDirection.normalized;

            // Apply velocity
            rb.velocity = new Vector3(
                moveDirection.x * currentSpeed,
                rb.velocity.y, // Preserve vertical velocity (gravity, jump)
                moveDirection.z * currentSpeed
            );
        }

        private void HandleJump()
        {
            if (Input.GetKeyDown(KeyCode.Space) && isGrounded)
            {
                rb.velocity = new Vector3(rb.velocity.x, 0, rb.velocity.z); // Reset vertical
                rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
            }
        }

        private void HandleCamera()
        {
            if (mainCamera == null) return;

            // Get mouse input
            float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
            float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;

            // Rotate player left/right (Y rotation)
            transform.Rotate(0, mouseX, 0);

            // Rotate camera up/down (X rotation, clamped)
            yRotation -= mouseY;
            yRotation = Mathf.Clamp(yRotation, -maxLookAngle, maxLookAngle);
            mainCamera.transform.localRotation = Quaternion.Euler(yRotation, 0, 0);
        }

        private void HandleCursorToggle()
        {
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                if (Cursor.lockState == CursorLockMode.Locked)
                {
                    Cursor.lockState = CursorLockMode.None;
                }
                else
                {
                    Cursor.lockState = CursorLockMode.Locked;
                }
            }
        }

        private void HandleInteraction()
        {
            if (Input.GetKeyDown(KeyCode.E))
            {
                RaycastHit hit;
                if (Physics.Raycast(mainCamera.transform.position, mainCamera.transform.forward, out hit, 2f))
                {
                    var interactable = hit.collider.GetComponent<IInteractable>();
                    if (interactable != null)
                    {
                        interactable.Interact(gameObject);
                    }
                }
            }
        }

        public bool IsGrounded => isGrounded;
    }


    /// <summary>
    /// Interface for interactable objects in the world.
    /// </summary>
    public interface IInteractable
    {
        void Interact(GameObject player);
    }
}
