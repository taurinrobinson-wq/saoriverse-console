using UnityEngine;

public class SimplePlayerMovement : MonoBehaviour
{
    private CharacterController cc;
    private float moveSpeed = 5f;
    private float gravity = -9.81f;
    private float velocityY = 0f;

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
        Debug.Log("✅ SimplePlayerMovement active on " + gameObject.name);
    }

    void Update()
    {
        // Get input
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");

        // Log input
        if (horizontal != 0 || vertical != 0)
        {
            Debug.Log($"Input: H={horizontal:F2}, V={vertical:F2}");
        }

        // Move direction (relative to player forward/right)
        Vector3 moveDirection = (transform.forward * vertical + transform.right * horizontal).normalized;

        // Apply gravity
        velocityY += gravity * Time.deltaTime;

        // Move player
        Vector3 velocity = moveDirection * moveSpeed + Vector3.up * velocityY;
        cc.Move(velocity * Time.deltaTime);

        // Reset Y velocity if grounded
        if (cc.isGrounded)
        {
            velocityY = 0f;
        }

        // Jump
        if (Input.GetKeyDown(KeyCode.Space) && cc.isGrounded)
        {
            velocityY = 5f;
            Debug.Log("JUMP!");
        }

        // Camera rotation with mouse
        float mouseX = Input.GetAxis("Mouse X");
        float mouseY = Input.GetAxis("Mouse Y");

        if (mouseX != 0 || mouseY != 0)
        {
            // Rotate player left/right
            transform.Rotate(0, mouseX * 2f, 0);

            // Log mouse input
            if (mouseX != 0 || mouseY != 0)
            {
                Debug.Log($"Mouse: X={mouseX:F2}, Y={mouseY:F2}");
            }
        }
    }
}
