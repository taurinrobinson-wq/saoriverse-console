using UnityEngine;

namespace Velinor.Utils
{
    /// <summary>
    /// Decouples an object from its parent at runtime to prevent inheriting scale/rotation,
    /// but continues to follow the target's position. 
    /// Essential for lighting setups that must not scale with the character.
    /// </summary>
    public class FollowTransformFixed : MonoBehaviour
    {
        [SerializeField] private Transform target;
        [SerializeField] private Vector3 fixedWorldRotation = Vector3.zero;
        [SerializeField] private Vector3 localOffset = Vector3.zero;

        private void Start()
        {
            // If no target assigned, assume the current parent was intended
            if (target == null && transform.parent != null)
            {
                target = transform.parent;
                localOffset = transform.localPosition;
            }

            // Unparent to avoid inheriting parent scale (the cause of the light-bulb effect)
            transform.SetParent(null);
        }

        private void LateUpdate()
        {
            if (target == null) return;

            // Follow position but ignore parent scale
            transform.position = target.position + localOffset;
            
            // Maintain fixed world rotation for consistent light direction
            transform.rotation = Quaternion.Euler(fixedWorldRotation);
        }

        public void SetTarget(Transform newTarget)
        {
            target = newTarget;
            if (target != null) localOffset = transform.position - target.position;
        }

        public void SetRotation(Vector3 rotation)
        {
            fixedWorldRotation = rotation;
        }
    }
}
