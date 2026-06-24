using UnityEngine;

/// <summary>
/// SimplePlayerController: Basic WASD movement for testing scenes.
/// Works with CharacterController for physics-based movement.
/// 
/// Controls:
/// - WASD: Move
/// - Space: Jump (optional)
/// - E: Interact (handled by NPCInteraction proximity detection)
/// </summary>
public class SimplePlayerController : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float groundDrag = 5f;
    [SerializeField] private float jumpForce = 5f;
    [SerializeField] private float gravity = 9.8f;

    private CharacterController controller;
    private Vector3 velocity = Vector3.zero;
    private bool isGrounded = false;

    private void Start()
    {
        controller = GetComponent<CharacterController>();
    }

    private void Update()
    {
        // Ground check
        isGrounded = controller.isGrounded;

        // Get input
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");

        // Calculate movement direction
        Vector3 moveDirection = transform.forward * vertical + transform.right * horizontal;
        moveDirection.Normalize();

        // Apply gravity
        if (isGrounded && velocity.y < 0)
        {
            velocity.y = -2f; // Keep slightly grounded
        }
        else
        {
            velocity.y -= gravity * Time.deltaTime;
        }

        // Jump
        if (Input.GetKeyDown(KeyCode.Space) && isGrounded)
        {
            velocity.y = Mathf.Sqrt(jumpForce * 2f * gravity);
        }

        // Apply movement
        Vector3 finalVelocity = moveDirection * moveSpeed + new Vector3(0, velocity.y, 0);
        controller.Move(finalVelocity * Time.deltaTime);
    }
}
