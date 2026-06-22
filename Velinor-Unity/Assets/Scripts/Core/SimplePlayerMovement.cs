using UnityEngine;

public class SimplePlayerMovement : MonoBehaviour
{
    private CharacterController cc;
    private Camera mainCam;
    private float moveSpeed = 5f;
    private float gravity = -9.81f;
    private float velocityY = 0f;
    private float mouseSensitivity = 2f;
    private float camPitch = 0f;

    void Start()
    {
        cc = GetComponent<CharacterController>();
        if (cc == null)
        {
            cc = gameObject.AddComponent<CharacterController>();
            cc.height = 2f;
            cc.radius = 0.5f;
            Debug.Log("Added CharacterController to Player");
        }

        mainCam = Camera.main;
        if (mainCam == null)
        {
            Debug.LogError("No Main Camera found!");
        }

        Debug.Log("✅ SimplePlayerMovement active on " + gameObject.name);
        Debug.Log("🎮 WASD=Move, Mouse=Look, Space=Jump, Shift=Sprint");
    }

    void Update()
    {
        // Get input
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");

        // Movement
        Vector3 moveDirection = (transform.forward * vertical + transform.right * horizontal).normalized;
        velocityY += gravity * Time.deltaTime;

        Vector3 velocity = moveDirection * moveSpeed + Vector3.up * velocityY;
        cc.Move(velocity * Time.deltaTime);

        // Ground check
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

        // Rotate player body left/right
        if (mouseX != 0)
        {
            transform.Rotate(0, mouseX * mouseSensitivity, 0);
        }

        // Rotate camera up/down (pitch)
        if (mainCam != null && mouseY != 0)
        {
            camPitch -= mouseY * mouseSensitivity;
            camPitch = Mathf.Clamp(camPitch, -90f, 90f);
            mainCam.transform.localRotation = Quaternion.Euler(camPitch, 0, 0);
        }
    }
}
