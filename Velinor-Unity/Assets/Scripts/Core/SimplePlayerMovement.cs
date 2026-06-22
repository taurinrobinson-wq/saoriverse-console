using UnityEngine;

public class SimplePlayerMovement : MonoBehaviour
{
    private CharacterController cc;
    private Camera mainCam;
    private float moveSpeed = 5f;
    private float sprintSpeed = 10f;
    private float gravity = -9.81f;
    private float velocityY = 0f;
    private float mouseSensitivity = 4f;  // Increased for snappier response
    private float camPitch = 0f;

    void Start()
    {
        cc = GetComponent<CharacterController>();
        if (cc == null)
        {
            cc = gameObject.AddComponent<CharacterController>();
            cc.height = 2f;
            cc.radius = 0.5f;
        }

        mainCam = GetComponentInChildren<Camera>();
        if (mainCam == null)
        {
            Debug.LogError("No Camera found in Player or children!");
        }
        else
        {
            // Position camera behind and above player for third-person view
            mainCam.transform.localPosition = new Vector3(0, 1.2f, -2.5f);
        }

        // Lock cursor to game
        Cursor.lockState = CursorLockMode.Locked;
        Debug.Log("✅ Third-person controller active!");
        Debug.Log("WASD = Move | Mouse = Free look | Shift = Sprint | Space = Jump | ESC = Unlock cursor");
    }

    void Update()
    {
        // Get movement input
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");

        // Check if sprinting
        bool isSprinting = Input.GetKey(KeyCode.LeftShift);
        float currentSpeed = isSprinting ? sprintSpeed : moveSpeed;

        // Calculate movement direction relative to player's forward/right
        Vector3 moveDirection = (transform.forward * vertical + transform.right * horizontal).normalized;

        // Apply gravity
        velocityY += gravity * Time.deltaTime;

        // Move player
        Vector3 velocity = moveDirection * currentSpeed + Vector3.up * velocityY;
        cc.Move(velocity * Time.deltaTime);

        // Check if grounded
        if (cc.isGrounded)
        {
            velocityY = 0f;
        }

        // Jump
        if (Input.GetKeyDown(KeyCode.Space) && cc.isGrounded)
        {
            velocityY = 5f;
        }

        // Mouse look
        float mouseX = Input.GetAxis("Mouse X");
        float mouseY = Input.GetAxis("Mouse Y");

        // Rotate player body (yaw) - camera follows since it's a child
        if (mouseX != 0)
        {
            transform.Rotate(0, mouseX * mouseSensitivity, 0);
        }

        // Rotate camera up/down (pitch only)
        if (mainCam != null && mouseY != 0)
        {
            camPitch -= mouseY * mouseSensitivity;
            camPitch = Mathf.Clamp(camPitch, -90f, 90f);
            mainCam.transform.localRotation = Quaternion.Euler(camPitch, 0, 0);
        }

        // Unlock cursor on ESC
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            Cursor.lockState = CursorLockMode.None;
        }
    }
}
