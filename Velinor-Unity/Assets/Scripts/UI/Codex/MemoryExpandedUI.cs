using System;
using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using Velinor.Core;

namespace Velinor.UI.Codex
{
    /// <summary>
    /// Displays an expanded memory fragment overlay for the Mind Log UI.
    /// </summary>
    public class MemoryExpandedUI : MonoBehaviour
    {
        [Header("Panel")]
        [SerializeField] private CanvasGroup panelCanvasGroup;
        [SerializeField] private Image memoryIcon;
        [SerializeField] private TextMeshProUGUI titleText;
        [SerializeField] private TextMeshProUGUI expandedText;
        [SerializeField] private ScrollRect textScrollRect;
        [SerializeField] private Button backButton;
        [SerializeField] private float fadeDuration = 0.2f;
        [SerializeField] private global::CodexViewController codexViewController;

        private Coroutine fadeCoroutine;

        /// <summary>
        /// Gets the fragment currently shown in the expanded overlay.
        /// </summary>
        public MemoryFragment CurrentFragment { get; private set; }

        /// <summary>
        /// Raised when the user leaves the expanded overlay.
        /// </summary>
        public event Action BackRequested;

        private void Awake()
        {
            if (panelCanvasGroup == null)
            {
                panelCanvasGroup = GetComponent<CanvasGroup>();
            }

            if (panelCanvasGroup == null)
            {
                Debug.LogError("[MemoryExpandedUI] CanvasGroup is required for fade transitions.");
                return;
            }

            panelCanvasGroup.alpha = 0f;
            panelCanvasGroup.blocksRaycasts = false;
            panelCanvasGroup.interactable = false;
            gameObject.SetActive(false);
        }

        private void OnEnable()
        {
            if (backButton != null)
            {
                backButton.onClick.AddListener(OnBackButtonClicked);
            }
        }

        private void OnDisable()
        {
            if (backButton != null)
            {
                backButton.onClick.RemoveListener(OnBackButtonClicked);
            }
        }

        /// <summary>
        /// Displays the supplied memory fragment in the expanded overlay.
        /// </summary>
        /// <param name="fragment">The fragment to display.</param>
        public void DisplayMemory(MemoryFragment fragment)
        {
            if (fragment == null)
            {
                Debug.LogWarning("[MemoryExpandedUI] DisplayMemory called with a null fragment.");
                return;
            }

            CurrentFragment = fragment;

            if (memoryIcon != null)
            {
                memoryIcon.sprite = fragment.icon;
                memoryIcon.enabled = fragment.icon != null;
                memoryIcon.preserveAspect = true;
            }

            if (titleText != null)
            {
                titleText.text = string.IsNullOrWhiteSpace(fragment.displayName)
                    ? fragment.fragmentID
                    : fragment.displayName;
            }

            if (expandedText != null)
            {
                expandedText.text = string.IsNullOrWhiteSpace(fragment.expandedText)
                    ? "No memory details are available for this fragment."
                    : fragment.expandedText;
            }

            if (textScrollRect != null)
            {
                Canvas.ForceUpdateCanvases();
                textScrollRect.verticalNormalizedPosition = 1f;
            }

            Debug.Log($"[MemoryExpandedUI] Displaying expanded memory '{fragment.fragmentID}'.");
            Show();

            if (codexViewController != null)
            {
                codexViewController.SendMessage("OnExpandedMemoryShown", fragment, SendMessageOptions.DontRequireReceiver);
            }
        }

        /// <summary>
        /// Handles the Back button and returns to the grid view.
        /// </summary>
        public void OnBackButtonClicked()
        {
            Debug.Log("[MemoryExpandedUI] Back button clicked. Returning to memory grid.");
            Hide();
            BackRequested?.Invoke();

            if (codexViewController != null)
            {
                codexViewController.SendMessage("OnExpandedMemoryClosed", CurrentFragment, SendMessageOptions.DontRequireReceiver);
            }
        }

        /// <summary>
        /// Sets the overlay active state using the configured fade transition.
        /// </summary>
        /// <param name="active">True to show the overlay; otherwise false.</param>
        public void SetActive(bool active)
        {
            if (active)
            {
                Show();
                return;
            }

            Hide();
        }

        /// <summary>
        /// Shows the expanded overlay using a fade-in animation.
        /// </summary>
        public void Show()
        {
            if (panelCanvasGroup == null)
            {
                Debug.LogError("[MemoryExpandedUI] Cannot show overlay because CanvasGroup is missing.");
                return;
            }

            gameObject.SetActive(true);
            StartFade(1f, deactivateOnComplete: false);
        }

        /// <summary>
        /// Hides the expanded overlay using a fade-out animation.
        /// </summary>
        public void Hide()
        {
            if (panelCanvasGroup == null)
            {
                Debug.LogError("[MemoryExpandedUI] Cannot hide overlay because CanvasGroup is missing.");
                return;
            }

            StartFade(0f, deactivateOnComplete: true);
        }

        private void StartFade(float targetAlpha, bool deactivateOnComplete)
        {
            if (fadeCoroutine != null)
            {
                StopCoroutine(fadeCoroutine);
            }

            fadeCoroutine = StartCoroutine(FadeTo(targetAlpha, deactivateOnComplete));
        }

        private IEnumerator FadeTo(float targetAlpha, bool deactivateOnComplete)
        {
            float startAlpha = panelCanvasGroup.alpha;
            float elapsed = 0f;

            panelCanvasGroup.blocksRaycasts = true;
            panelCanvasGroup.interactable = false;

            if (Mathf.Approximately(fadeDuration, 0f))
            {
                panelCanvasGroup.alpha = targetAlpha;
            }
            else
            {
                while (elapsed < fadeDuration)
                {
                    elapsed += Time.unscaledDeltaTime;
                    panelCanvasGroup.alpha = Mathf.Lerp(startAlpha, targetAlpha, elapsed / fadeDuration);
                    yield return null;
                }

                panelCanvasGroup.alpha = targetAlpha;
            }

            bool isVisible = targetAlpha > 0.99f;
            panelCanvasGroup.blocksRaycasts = isVisible;
            panelCanvasGroup.interactable = isVisible;

            if (!isVisible && deactivateOnComplete)
            {
                gameObject.SetActive(false);
            }

            fadeCoroutine = null;
            Debug.Log($"[MemoryExpandedUI] Fade completed. Visible={isVisible}.");
        }
    }
}
