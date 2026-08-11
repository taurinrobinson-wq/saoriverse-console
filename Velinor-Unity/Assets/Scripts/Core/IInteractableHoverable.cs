using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// Optional interface for interactables that support hover feedback.
    /// Interactables can implement this to show visual feedback (glowing, outline, etc.)
    /// when the player looks at them.
    /// 
    /// Usage:
    /// public class MyInteractable : MonoBehaviour, IInteractable, IInteractableHoverable
    /// {
    ///     public void OnHover() { /* Show glow, outline, etc. */ }
    ///     public void Interact(GameObject player) { /* Handle interaction */ }
    /// }
    /// </summary>
    public interface IInteractableHoverable : IInteractable
    {
        /// <summary>
        /// Called when the player's camera is looking at this interactable (raycast hit).
        /// Use this to provide visual feedback like glowing, outline, or color change.
        /// </summary>
        void OnHover();
    }
}
