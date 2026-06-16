using UnityEngine;
using Velinor.Core;

namespace StarterAssets
{
    /// <summary>
    /// Trigger-based interaction zone. Shows prompt when player enters.
    /// </summary>
    public class InteractionZone : MonoBehaviour
    {
        [SerializeField] private IInteractable _interactable;
        private InteractionPrompt _prompt;
        private bool _playerInZone = false;

        private void Start()
        {
            // Get the interactable from this object
            _interactable = GetComponent<IInteractable>();
            
            // Find the prompt UI
            _prompt = FindObjectOfType<InteractionPrompt>();
            
            if (_interactable == null)
            {
                Debug.LogWarning($"InteractionZone on {gameObject.name} has no IInteractable component!");
            }
        }

        private void OnTriggerEnter(Collider other)
        {
            if (other.CompareTag("Player") && _interactable != null)
            {
                _playerInZone = true;
                if (_prompt != null)
                {
                    _prompt.Show(gameObject.name);
                }
                Debug.Log($"Player entered {gameObject.name} interaction zone");
            }
        }

        private void OnTriggerExit(Collider other)
        {
            if (other.CompareTag("Player"))
            {
                _playerInZone = false;
                if (_prompt != null)
                {
                    _prompt.Hide();
                }
                Debug.Log($"Player left {gameObject.name} interaction zone");
            }
        }

        private void Update()
        {
            // Check for E key when player is in zone
            if (_playerInZone && Input.GetKeyDown(KeyCode.E) && _interactable != null)
            {
                Debug.Log($"Interacting with {gameObject.name}");
                _interactable.Interact(GameObject.FindGameObjectWithTag("Player"));
            }
        }
    }
}
