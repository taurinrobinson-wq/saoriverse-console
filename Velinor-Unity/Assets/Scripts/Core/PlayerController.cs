using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// Third-person character controller with simple movement.
    /// Supports: walk, turn, crouch, squeeze through gaps.
    /// No jump, sprint, or stamina.
    /// </summary>
    public class PlayerController : MonoBehaviour
    {
        [SerializeField] private float walkSpeed = 3f;
        [SerializeField] private float turnSpeed = 5f;
        [SerializeField] private float groundDrag = 5f;
        [SerializeField] private float groundAcceleration = 10f;

        [SerializeField] private CharacterController characterController;
        [SerializeField] private Transform cameraFollowTarget; // Where camera aims

        private Vector3 velocity;
        private Animator animator;

        private void Start()
        {
            animator = GetComponent<Animator>();
            if (characterController == null)
                characterController = GetComponent<CharacterController>();
        }

        private void Update()
        {
            HandleInput();
            ApplyGravity();
            Move();
        }

        /// <summary>
        /// Handles player input for movement and actions.
        /// </summary>
        private void HandleInput()
        {
            // Movement input (WASD or analog stick)
            float horizontal = Input.GetAxis("Horizontal");
            float vertical = Input.GetAxis("Vertical");

            // Construct movement direction relative to camera forward
            Vector3 moveDirection = GetMovementDirection(horizontal, vertical);

            // Apply movement
            ApplyMovement(moveDirection);

            // Rotation
            if (moveDirection.magnitude > 0.1f)
            {
                RotateTowards(moveDirection);
            }

            // Crouch (optional)
            if (Input.GetKey(KeyCode.C))
            {
                animator.SetBool("IsCrouching", true);
            }
            else
            {
                animator.SetBool("IsCrouching", false);
            }

            // Interaction
            if (Input.GetKeyDown(KeyCode.E))
            {
                HandleInteraction();
            }
        }

        /// <summary>
        /// Calculates movement direction relative to camera forward.
        /// </summary>
        private Vector3 GetMovementDirection(float horizontal, float vertical)
        {
            Transform cameraTransform = Camera.main.transform;

            Vector3 forward = cameraTransform.forward;
            Vector3 right = cameraTransform.right;

            // Remove Y component so movement is always grounded
            forward.y = 0;
            right.y = 0;

            forward.Normalize();
            right.Normalize();

            return (forward * vertical + right * horizontal).normalized;
        }

        /// <summary>
        /// Applies movement to velocity.
        /// </summary>
        private void ApplyMovement(Vector3 moveDirection)
        {
            if (moveDirection.magnitude > 0.1f)
            {
                Vector3 targetVelocity = moveDirection * walkSpeed;
                velocity.x = Mathf.Lerp(velocity.x, targetVelocity.x, groundAcceleration * Time.deltaTime);
                velocity.z = Mathf.Lerp(velocity.z, targetVelocity.z, groundAcceleration * Time.deltaTime);

                animator.SetFloat("Speed", walkSpeed);
            }
            else
            {
                velocity.x = Mathf.Lerp(velocity.x, 0, groundDrag * Time.deltaTime);
                velocity.z = Mathf.Lerp(velocity.z, 0, groundDrag * Time.deltaTime);

                animator.SetFloat("Speed", 0);
            }
        }

        /// <summary>
        /// Rotates character to face movement direction.
        /// </summary>
        private void RotateTowards(Vector3 direction)
        {
            Quaternion targetRotation = Quaternion.LookRotation(direction);
            transform.rotation = Quaternion.Lerp(transform.rotation, targetRotation, turnSpeed * Time.deltaTime);
        }

        /// <summary>
        /// Applies gravity (simple downward force).
        /// </summary>
        private void ApplyGravity()
        {
            if (characterController.isGrounded)
            {
                velocity.y = -2f; // Small negative value to keep grounded
            }
            else
            {
                velocity.y -= 9.81f * Time.deltaTime;
            }
        }

        /// <summary>
        /// Moves the character using CharacterController.
        /// </summary>
        private void Move()
        {
            characterController.Move(velocity * Time.deltaTime);
        }

        /// <summary>
        /// Handles interaction with nearby objects.
        /// </summary>
        private void HandleInteraction()
        {
            // Raycast forward to find interactable objects
            RaycastHit hit;
            if (Physics.Raycast(transform.position + Vector3.up, transform.forward, out hit, 2f))
            {
                var interactable = hit.collider.GetComponent<IInteractable>();
                if (interactable != null)
                {
                    interactable.Interact(gameObject);
                }
            }
        }

        /// <summary>
        /// Allows squeeze-through animations (low-poly movement).
        /// </summary>
        public void SqueezeThrough(Vector3 targetPosition)
        {
            // Transition character to squeeze animation and move to target
            StartCoroutine(SqueezeThroughCoroutine(targetPosition));
        }

        private System.Collections.IEnumerator SqueezeThroughCoroutine(Vector3 targetPosition)
        {
            animator.SetTrigger("Squeeze");
            float duration = 1f;
            float elapsed = 0f;

            Vector3 startPos = transform.position;
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                transform.position = Vector3.Lerp(startPos, targetPosition, elapsed / duration);
                yield return null;
            }

            transform.position = targetPosition;
        }
    }

    /// <summary>
    /// Interface for interactable objects in the world.
    /// </summary>
    public interface IInteractable
    {
        void Interact(GameObject player);
    }
}
