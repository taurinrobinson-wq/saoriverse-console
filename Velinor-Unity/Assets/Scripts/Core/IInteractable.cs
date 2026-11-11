using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// Interface for objects that can be interacted with by the player.
    /// Implement this interface to make an object interactable.
    /// 
    /// Usage:
    /// public class MyInteractable : MonoBehaviour, IInteractable
    /// {
    ///     public void Interact(GameObject player) { /* Handle interaction */ }
    /// }
    /// </summary>
    public interface IInteractable
    {
        /// <summary>
        /// Called when the player interacts with this object.
        /// </summary>
        /// <param name="player">The player GameObject that initiated the interaction.</param>
        void Interact(GameObject player);
    }
}
