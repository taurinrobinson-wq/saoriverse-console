using UnityEngine;

public class SimplePlayerController : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 3f;
    [SerializeField] private float mouseSensitivity = 100f;
    
    private CharacterController characterController;
    private Camera mainCamera;
    private float verticalVelocity = 0f;
    private float xRotation = 0f;
    private bool isGrounded = false;

    void Start()
    {
        characterController = GetComponent<CharacterController>();
        mainCamera = GetComponentInChildren<Camera>();
    }

    void Update()
    {
        HandleMovement();
        HandleMouseLook();
    }

    void HandleMovement()
    {
        // Ground check
        isGrounded = characterController.isGrounded;

        // Get input
        float horizontalInput = Input.GetAxis("Horizontal");
        float verticalInput = Input.GetAxis("Vertical");

        // Calculate move direction relative to where player is looking
        Vector3 moveDirection = transform.forward * verticalInput + transform.right * horizontalInput;
        
        // Apply speed
        Vector3 moveVelocity = moveDirection * moveSpeed;

        // Handle gravity and jumping
        if (isGrounded)
        {
            verticalVelocity = -1f;  // Small negative to keep grounded
            
            if (Input.GetKeyDown(KeyCode.Space))
            {
                verticalVelocity = jumpForce;
            }
        }
        else
        {
            verticalVelocity -= 9.81f * Time.deltaTime;
        }

        moveVelocity.y = verticalVelocity;
        
        // Apply movement
        characterController.Move(moveVelocity * Time.deltaTime);
    }

    void HandleMouseLook()
    {
        // Only look when right-clicking
        if (!Input.GetMouseButton(1)) return;  // Right mouse button

        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity * Time.deltaTime;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity * Time.deltaTime;

        // Rotate player left/right
        transform.Rotate(Vector3.up * mouseX);

        // Rotate camera up/down (clamp to prevent flipping)
        xRotation -= mouseY;
        xRotation = Mathf.Clamp(xRotation, -90f, 90f);

        mainCamera.transform.localRotation = Quaternion.Euler(xRotation, 0f, 0f);
    }
}
