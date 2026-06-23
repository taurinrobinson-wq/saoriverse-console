using UnityEngine;

public class SimplePlayerMovement : MonoBehaviour
{
    private CharacterController cc;
    private Camera mainCam;
    private float moveSpeed = 5f;
    private float sprintSpeed = 10f;
    private float gravity = 9.81f;
    private float velocityY = 0f;
    private float mouseSensitivity = 4f;
    private float camPitch = 0f;
    
    // Camera zoom
    private float cameraDistance = 2.5f;
    private float minZoom = 0.5f;
    private float maxZoom = 5f;
    private float zoomSpeed = 1f;

    void Start()
    {
        cc = GetComponent<CharacterController>();
        if (cc == null)
        {
            Debug.LogError("NO CHARACTER CONTROLLER!");
            return;
        }

        mainCam = Camera.main;
        if (mainCam == null)
        {
            Debug.LogError("NO MAIN CAMERA!");
            return;
        }

        // Position camera behind and above player for third-person view
        mainCam.transform.SetParent(transform);
        mainCam.transform.localPosition = new Vector3(0, 1.2f, -2.5f);

        // Lock cursor to game
        Cursor.lockState = CursorLockMode.Locked;
        Debug.Log("✅ Third-person controller active!");
        Debug.Log("WASD = Move | Mouse = Free look | Shift = Sprint | Space = Jump | ESC = Unlock cursor");
    }

    void Update()
    {
        if (cc == null) return;

        // Get movement input
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");

        // Check if sprinting
        bool isSprinting = Input.GetKey(KeyCode.LeftShift);
        float currentSpeed = isSprinting ? sprintSpeed : moveSpeed;

        // Calculate movement direction relative to player's forward/right
        Vector3 moveDirection = (transform.forward * vertical + transform.right * horizontal).normalized;

        // Apply gravity - only when falling
        if (!cc.isGrounded)
        {
            velocityY -= gravity * Time.deltaTime;
        }
        else
        {
            velocityY = -0.1f; // Small negative to keep grounded
        }

        // Move player
        Vector3 velocity = moveDirection * currentSpeed + Vector3.up * velocityY;
        cc.Move(velocity * Time.deltaTime);

        // Jump
        if (Input.GetKeyDown(KeyCode.Space) && cc.isGrounded)
        {
            velocityY = 5f;
            Debug.Log($"JUMP! IsGrounded: {cc.isGrounded}");
        }
        else if (Input.GetKeyDown(KeyCode.Space))
        {
            Debug.Log($"Space pressed but NOT grounded: {cc.isGrounded}");
        }

        // Mouse look
        float mouseX = Input.GetAxis("Mouse X");
        float mouseY = Input.GetAxis("Mouse Y");

        // Rotate player body horizontally (yaw)
        transform.Rotate(0, mouseX * mouseSensitivity, 0);

        // Rotate camera vertically (pitch)
        camPitch -= mouseY * mouseSensitivity;
        camPitch = Mathf.Clamp(camPitch, -90f, 90f);
        mainCam.transform.localRotation = Quaternion.Euler(camPitch, 0, 0);

        // Mouse wheel zoom
        float scrollDelta = Input.GetAxis("Mouse ScrollWheel");
        if (scrollDelta != 0)
        {
            cameraDistance -= scrollDelta * zoomSpeed;
            cameraDistance = Mathf.Clamp(cameraDistance, minZoom, maxZoom);
            mainCam.transform.localPosition = new Vector3(0, 1.2f, -cameraDistance);
        }

        // Unlock cursor
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            Cursor.lockState = Cursor.lockState == CursorLockMode.Locked
                ? CursorLockMode.Confined
                : CursorLockMode.Locked;
        }
    }
}
