using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// NPCRoaming - Simple physics-based roaming behavior for NPCs
    /// Moves Rigidbody towards waypoints and updates Animator parameters
    /// </summary>
    public class NPCRoaming : MonoBehaviour
    {
        [Header("Movement")]
        [SerializeField] private float walkSpeed = 2f;
        [SerializeField] private float rotationSpeed = 5f;

        [Header("Roaming Bounds")]
        [SerializeField] private Vector3 boundsMin = new Vector3(-5f, 0.30f, -2f);
        [SerializeField] private Vector3 boundsMax = new Vector3(5f, 0.30f, 14f);
        [SerializeField] private float waypointTolerance = 0.5f;
        [SerializeField] private float minWaitTime = 2f;
        [SerializeField] private float maxWaitTime = 6f;

        [Header("Obstacle Avoidance")]
        [SerializeField] private float obstacleDetectionDistance = 2.2f;
        [SerializeField] private LayerMask obstacleMask;

        private Rigidbody rb;
        private Animator animator;
        private Vector3 targetWaypoint;
        private bool isWaiting = false;
        private float waitTimer = 0f;
        private bool isGrounded = true;

        private void Start()
        {
            rb = GetComponent<Rigidbody>();
            if (rb == null)
            {
                rb = gameObject.AddComponent<Rigidbody>();
            }
            rb.isKinematic = true; // Make kinematic so player cannot push them!
            rb.constraints = RigidbodyConstraints.FreezeRotation;

            animator = GetComponent<Animator>();

            // Find a random start waypoint
            SetRandomWaypoint();
        }

        private void Update()
        {
            if (isWaiting)
            {
                waitTimer -= Time.deltaTime;
                if (waitTimer <= 0f)
                {
                    isWaiting = false;
                    SetRandomWaypoint();
                }
            }

            // Ground check (NPCs are static on ground normally, but we keep them grounded)
            int foregroundMask = LayerMask.GetMask("Foreground");
            isGrounded = Physics.Raycast(transform.position, Vector3.down, 1.5f, foregroundMask);

            // Update animator
            UpdateAnimator();
        }

        private void FixedUpdate()
        {
            if (isWaiting)
            {
                return;
            }

            MoveTowardsWaypoint();
        }

        private void SetRandomWaypoint()
        {
            float randomX = Random.Range(boundsMin.x, boundsMax.x);
            float randomZ = Random.Range(boundsMin.z, boundsMax.z);
            targetWaypoint = new Vector3(randomX, transform.position.y, randomZ);
        }

        private void MoveTowardsWaypoint()
        {
            Vector3 direction = targetWaypoint - transform.position;
            direction.y = 0f; // Stay horizontal

            float distance = direction.magnitude;

            if (distance < waypointTolerance)
            {
                StartWaiting();
                return;
            }

            // Obstacle Avoidance: Raycast forward starting outside own collider (radius 0.4)
            RaycastHit hit;
            Vector3 rayStart = transform.position + Vector3.up * 0.9f + transform.forward * 0.5f; 
            if (Physics.Raycast(rayStart, transform.forward, out hit, obstacleDetectionDistance, obstacleMask))
            {
                // Blocked! Wait and choose a new waypoint
                StartWaiting();
                return;
            }

            // Rotate towards target
            Vector3 targetDirection = direction.normalized;
            if (targetDirection != Vector3.zero)
            {
                Quaternion targetRotation = Quaternion.LookRotation(targetDirection);
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, rotationSpeed * Time.fixedDeltaTime);
            }

            // Move kinematic position smoothly
            Vector3 nextPos = transform.position + transform.forward * walkSpeed * Time.fixedDeltaTime;
            nextPos.y = 0.30f; // Stay on the walkway level
            rb.MovePosition(nextPos);
        }

        private void StartWaiting()
        {
            isWaiting = true;
            waitTimer = Random.Range(minWaitTime, maxWaitTime);
        }

        private void UpdateAnimator()
        {
            if (animator == null) return;

            float horizontalSpeed = isWaiting ? 0f : walkSpeed;
            
            // Speed factor for BlendTree (0=idle, 1=walk)
            animator.SetFloat("Speed", horizontalSpeed / walkSpeed);
            animator.SetFloat("MotionSpeed", horizontalSpeed);
            animator.SetBool("Grounded", isGrounded);
        }

        #region Animation Event Receivers
        /// <summary>
        /// Suppress warning: 'OnFootstep' has no receiver
        /// </summary>
        public void OnFootstep()
        {
            // Optional: add footstep audio/effects here
        }

        /// <summary>
        /// Suppress warning: 'FootstepL' has no receiver
        /// </summary>
        public void FootstepL()
        {
        }

        /// <summary>
        /// Suppress warning: 'FootstepR' has no receiver
        /// </summary>
        public void FootstepR()
        {
        }

        /// <summary>
        /// Suppress warning: 'OnLand' has no receiver
        /// </summary>
        public void OnLand()
        {
        }

        /// <summary>
        /// Suppress warning: 'OnJump' has no receiver
        /// </summary>
        public void OnJump()
        {
        }
        #endregion

        // Draw debug visuals in Editor
        private void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(targetWaypoint, 0.3f);
            
            // Draw forward avoidance ray
            Gizmos.color = Color.cyan;
            Gizmos.DrawLine(transform.position + Vector3.up * 0.9f, transform.position + Vector3.up * 0.9f + transform.forward * obstacleDetectionDistance);
        }
    }
}
