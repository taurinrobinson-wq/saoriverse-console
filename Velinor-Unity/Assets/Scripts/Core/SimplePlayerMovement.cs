using UnityEngine;
using UnityEngine.EventSystems;

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
    private bool wasGroundedLastFrame = false;  // Track grounded state
    private bool isMovementLocked = false;  // Lock movement during dialogue
    
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
        mainCam.transform.localRotation = Quaternion.identity;  // Start with no rotation
        
        // Initialize camera pitch to look slightly forward/up (not down at floor)
        camPitch = 15f;  // Look slightly upward by default
        mainCam.transform.localRotation = Quaternion.Euler(camPitch, 0, 0);

        // Lock cursor to game
        Cursor.lockState = CursorLockMode.Locked;
        Debug.Log("✅ Third-person controller active!");
        Debug.Log("WASD = Move | Right Mouse = Look Around | Shift = Sprint | Space = Jump | ESC = Unlock cursor");
    }

    void Update()
    {
        if (cc == null) return;

        // If movement is locked (dialogue open), skip input processing
        if (isMovementLocked)
        {
            // Still apply gravity to keep grounded check accurate
            if (!cc.isGrounded)
                velocityY -= gravity * Time.deltaTime;
            else
                velocityY = -0.1f;

            cc.Move(Vector3.up * velocityY * Time.deltaTime);
            wasGroundedLastFrame = cc.isGrounded;
            return;
        }

        // Get movement input
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");

        // Check if sprinting
        bool isSprinting = Input.GetKey(KeyCode.LeftShift);
        float currentSpeed = isSprinting ? sprintSpeed : moveSpeed;

        // Calculate movement direction relative to player's forward/right
        Vector3 moveDirection = (transform.forward * vertical + transform.right * horizontal).normalized;

        // ===== JUMP FIRST =====
        if (Input.GetKeyDown(KeyCode.Space) && cc.isGrounded)
        {
            velocityY = 5f;
            Debug.Log($"🎯 JUMP!");
        }

        // Apply gravity and grounding logic
        if (!cc.isGrounded)
        {
            velocityY -= gravity * Time.deltaTime;
        }
        else
        {
            // Only reset velocity to -0.1 if we JUST landed (weren't grounded last frame)
            if (!wasGroundedLastFrame)
            {
                velocityY = -0.1f;
            }
        }

        // Move player
        Vector3 velocity = moveDirection * currentSpeed + Vector3.up * velocityY;
        cc.Move(velocity * Time.deltaTime);

        // Mouse look (only when RIGHT MOUSE BUTTON is held down)
        if (Input.GetMouseButton(1))
        {
            float mouseX = Input.GetAxis("Mouse X");
            float mouseY = Input.GetAxis("Mouse Y");

            // Rotate player body horizontally (yaw)
            transform.Rotate(0, mouseX * mouseSensitivity, 0);

            // Rotate camera vertically (pitch)
            camPitch -= mouseY * mouseSensitivity;
            camPitch = Mathf.Clamp(camPitch, -90f, 90f);
            mainCam.transform.localRotation = Quaternion.Euler(camPitch, 0, 0);
        }

        // Mouse wheel zoom
        float scrollDelta = Input.GetAxis("Mouse ScrollWheel");
        if (scrollDelta != 0)
        {
            cameraDistance -= scrollDelta * zoomSpeed;
            cameraDistance = Mathf.Clamp(cameraDistance, minZoom, maxZoom);
            mainCam.transform.localPosition = new Vector3(0, 1.2f, -cameraDistance);
        }

        // Auto-manage cursor lock based on dialogue state
        bool isDialogueOpen = false;
        GameObject dialoguePanel = GameObject.Find("DialoguePanel");  // Search entire scene
        if (dialoguePanel != null)
            isDialogueOpen = dialoguePanel.activeSelf;

        // Debug: Log cursor state and dialogue panel status every frame
        if (Input.GetKeyDown(KeyCode.D))  // Press D to debug
        {
            Debug.Log($"🐛 DEBUG - Dialogue Panel found: {dialoguePanel != null}");
            Debug.Log($"🐛 DEBUG - Dialogue Panel active: {isDialogueOpen}");
            Debug.Log($"🐛 DEBUG - Cursor locked: {Cursor.lockState}");
            Debug.Log($"🐛 DEBUG - Cursor position: {Input.mousePosition}");
        }

        // Unlock cursor when dialogue is open (so user can click buttons)
        if (isDialogueOpen)
        {
            Cursor.lockState = CursorLockMode.Confined;  // Visible but confined to window
        }
        else
        {
            Cursor.lockState = CursorLockMode.Locked;  // Hidden during gameplay
        }

        // Allow escape to manually toggle if needed
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            Cursor.lockState = Cursor.lockState == CursorLockMode.Locked
                ? CursorLockMode.Confined
                : CursorLockMode.Locked;
        }

        // Update grounded state for next frame
        wasGroundedLastFrame = cc.isGrounded;
    }

    /// <summary>
    /// Called by NPCInteraction to lock/unlock player movement during dialogue
    /// </summary>
    public void LockMovement(bool locked)
    {
        isMovementLocked = locked;
        if (locked)
            Debug.Log("🔒 PLAYER MOVEMENT LOCKED (Dialogue open)");
        else
            Debug.Log("🔓 PLAYER MOVEMENT UNLOCKED (Dialogue closed)");
    }
}
