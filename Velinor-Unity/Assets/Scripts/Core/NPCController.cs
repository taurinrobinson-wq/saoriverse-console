using UnityEngine;
using System.Collections;

namespace Velinor.Core
{
    /// <summary>
    /// NPCController: Basic movement and animation driver for NPC characters.
    /// No input handling - all movement is programmatic via method calls.
    /// Uses 3D CharacterController for NPCs in hybrid 2D/3D environments.
    /// Requires: CharacterController, Animator
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class NPCController : MonoBehaviour
    {
        [Header("Movement")]
        [SerializeField] private float moveSpeed = 2.0f;
        [SerializeField] private float speedChangeRate = 10.0f;
        [SerializeField] private float rotationSpeed = 5.0f;

        [Header("Physics")]
        [SerializeField] private float gravity = -15.0f;
        [SerializeField] private float terminalVelocity = 53.0f;

        private CharacterController characterController;
        private Animator animator;
        private float currentSpeed = 0.0f;
        private float verticalVelocity = 0.0f;

        // Animator hashes for performance
        private int animIDSpeed;
        private int animIDMotionSpeed;

        private Coroutine currentMovementCoroutine;

        private void Awake()
        {
            characterController = GetComponent<CharacterController>();
            animator = GetComponent<Animator>();

            if (characterController == null)
            {
                Debug.LogError($"[NPCController] {gameObject.name}: CharacterController component required!");
            }

            if (animator != null)
            {
                // Cache animator hashes
                animIDSpeed = Animator.StringToHash("Speed");
                animIDMotionSpeed = Animator.StringToHash("MotionSpeed");
            }

            Debug.Log($"[NPCController] {gameObject.name}: Initialized");
        }

        private void Update()
        {
            ApplyGravity();
        }

        private void ApplyGravity()
        {
            if (characterController == null) return;

            verticalVelocity += gravity * Time.deltaTime;

            if (verticalVelocity < -terminalVelocity)
            {
                verticalVelocity = -terminalVelocity;
            }

            if (characterController.isGrounded) 
            {
                verticalVelocity = -2.0f;
            }
        }

        /// <summary>
        /// Smoothly move NPC towards target position.
        /// Handles animation blending and rotation.
        /// </summary>
        public void MoveTo(Vector3 targetPosition, float speed)
        {
            if (currentMovementCoroutine != null)
            {
                StopCoroutine(currentMovementCoroutine);
            }

            currentMovementCoroutine = StartCoroutine(MoveToCoroutine(targetPosition, speed));
        }

        private IEnumerator MoveToCoroutine(Vector3 targetPosition, float speed)
        {
            // Flatten Y to ignore height differences
            Vector3 flatTarget = new Vector3(targetPosition.x, transform.position.y, targetPosition.z);

            while (Vector3.Distance(transform.position, flatTarget) > 0.1f)
            {
                if (characterController == null) break;

                Vector3 direction = (flatTarget - transform.position).normalized;

                // Move character
                Vector3 movement = direction * speed * Time.deltaTime;
                movement.y = verticalVelocity * Time.deltaTime;
                characterController.Move(movement);

                // Rotate towards direction of movement
                if (direction.sqrMagnitude > 0.001f)
                {
                    Quaternion targetRotation = Quaternion.LookRotation(direction);
                    transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, rotationSpeed * Time.deltaTime);
                }

                // Update animation
                UpdateAnimatorSpeed(speed);

                yield return null;
            }

            // Stop movement
            UpdateAnimatorSpeed(0.0f);
        }

        /// <summary>
        /// Smoothly rotate NPC to look at target.
        /// </summary>
        public void LookAt(Transform target)
        {
            if (target == null) return;
            StopAllCoroutines();
            StartCoroutine(LookAtCoroutine(target));
        }

        private IEnumerator LookAtCoroutine(Transform target)
        {
            while (target != null)
            {
                Vector3 direction = (target.position - transform.position);
                direction.y = 0f; // Keep upright

                if (direction.sqrMagnitude > 0.001f)
                {
                    Quaternion targetRotation = Quaternion.LookRotation(direction);
                    transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, rotationSpeed * Time.deltaTime);
                }

                yield return null;
            }
        }

        /// <summary>
        /// Stop all movement immediately.
        /// </summary>
        public void StopMovement()
        {
            if (currentMovementCoroutine != null)
            {
                StopCoroutine(currentMovementCoroutine);
                currentMovementCoroutine = null;
            }
            UpdateAnimatorSpeed(0.0f);
        }

        /// <summary>
        /// Play animation on this NPC.
        /// </summary>
        public void PlayAnimation(string triggerName)
        {
            if (animator != null)
            {
                animator.SetTrigger(triggerName);
            }
        }

        /// <summary>
        /// Set boolean animation parameter.
        /// </summary>
        public void SetAnimationBool(string parameterName, bool value)
        {
            if (animator != null)
            {
                animator.SetBool(parameterName, value);
            }
        }

        private void UpdateAnimatorSpeed(float speed)
        {
            if (animator == null) return;

            // Smooth speed blending
            currentSpeed = Mathf.Lerp(currentSpeed, speed, Time.deltaTime * speedChangeRate);

            float motionSpeed = currentSpeed > 0 ? 1.0f : 0.0f;
            animator.SetFloat(animIDSpeed, currentSpeed);
            animator.SetFloat(animIDMotionSpeed, motionSpeed);
        }
    }
}
