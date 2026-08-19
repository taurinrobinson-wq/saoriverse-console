using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// InputManager: Global input state manager for controlling when player can move.
    /// Used to disable movement keys when panels (Codex, Dialogue, Diary, Triglyph) are open.
    /// </summary>
    public class InputManager : MonoBehaviour
    {
        private static InputManager instance;
        private static bool movementEnabled = true;

        private void Awake()
        {
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }
            instance = this;
        }

        /// <summary>
        /// Check if player movement is currently allowed.
        /// </summary>
        public static bool IsMovementEnabled() => movementEnabled;

        /// <summary>
        /// Disable player movement (called when panels open).
        /// </summary>
        public static void DisableMovement()
        {
            movementEnabled = false;
            Debug.Log("[InputManager] Movement disabled");
        }

        /// <summary>
        /// Enable player movement (called when panels close).
        /// </summary>
        public static void EnableMovement()
        {
            movementEnabled = true;
            Debug.Log("[InputManager] Movement enabled");
        }
    }
}
