using UnityEngine;
using TMPro;
using Velinor.Core;

namespace StarterAssets
{
    /// <summary>
    /// InteractionPromptUI - Shows "Press E to Interact" when player looks at IInteractable.
    /// Attach this to a Canvas in the scene.
    /// </summary>
    public class InteractionPromptUI : MonoBehaviour
    {
        [SerializeField] private TextMeshProUGUI promptText;
        [SerializeField] private float rayCastDistance = 5f;

        private Camera _mainCamera;
        private IInteractable _currentInteractable;
        private bool _isLooking = false;

        private void Start()
        {
            _mainCamera = Camera.main;

            // Create prompt text if not assigned
            if (promptText == null)
            {
                Debug.LogWarning("[InteractionPromptUI] No prompt text assigned. Creating one...");
                CreatePromptText();
            }

            if (promptText != null)
            {
                promptText.enabled = false;
            }
        }

        private void Update()
        {
            if (_mainCamera == null)
                return;

            CheckForInteractables();
            UpdatePromptDisplay();
        }

        private void CheckForInteractables()
        {
            _currentInteractable = null;
            _isLooking = false;

            // Raycast from camera center
            Ray ray = new Ray(_mainCamera.transform.position, _mainCamera.transform.forward);
            RaycastHit hit;

            if (Physics.Raycast(ray, out hit, rayCastDistance))
            {
                IInteractable interactable = hit.collider.GetComponent<IInteractable>();
                if (interactable != null)
                {
                    _currentInteractable = interactable;
                    _isLooking = true;
                }
            }
        }

        private void UpdatePromptDisplay()
        {
            if (promptText == null)
                return;

            if (_isLooking && _currentInteractable != null)
            {
                promptText.enabled = true;
                promptText.text = "Press E to Interact";
            }
            else
            {
                promptText.enabled = false;
            }
        }

        private void CreatePromptText()
        {
            GameObject promptGO = new GameObject("InteractionPrompt");
            promptGO.transform.SetParent(transform);
            promptGO.transform.localPosition = Vector3.zero;

            promptText = promptGO.AddComponent<TextMeshProUGUI>();
            promptText.text = "Press E to Interact";
            promptText.alignment = TextAlignmentOptions.Center;
            promptText.fontSize = 36;

            RectTransform rectTransform = promptGO.GetComponent<RectTransform>();
            rectTransform.sizeDelta = new Vector2(400, 100);
            rectTransform.anchoredPosition = new Vector2(0, -300);

            promptText.enabled = false;
        }
    }
}
