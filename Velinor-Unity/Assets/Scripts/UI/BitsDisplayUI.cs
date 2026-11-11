using UnityEngine;
using TMPro;
using Velinor.Economy;

namespace Velinor.UI
{
    /// <summary>
    /// Displays current Bits balance on screen.
    /// Updates whenever CurrencySystem changes.
    /// </summary>
    public class BitsDisplayUI : MonoBehaviour
    {
        [SerializeField] private TextMeshProUGUI bitsLabel;
        [SerializeField] private bool showPrefix = true;
        [SerializeField] private string prefix = "Bits: ";
        [SerializeField] private Color normalColor = Color.white;
        [SerializeField] private Color earnColor = Color.green;
        [SerializeField] private Color spendColor = Color.red;

        private CurrencySystem currencySystem;
        private CanvasGroup canvasGroup;

        private void OnEnable()
        {
            currencySystem = CurrencySystem.Instance;
            if (currencySystem != null)
            {
                currencySystem.OnBitsChanged += OnBitsChanged;
                currencySystem.OnBitsEarned += OnBitsEarned;
                currencySystem.OnBitsSpent += OnBitsSpent;
                
                // Initial update
                UpdateDisplay(currencySystem.CurrentBits);
            }
        }

        private void OnDisable()
        {
            if (currencySystem != null)
            {
                currencySystem.OnBitsChanged -= OnBitsChanged;
                currencySystem.OnBitsEarned -= OnBitsEarned;
                currencySystem.OnBitsSpent -= OnBitsSpent;
            }
        }

        private void UpdateDisplay(int amount)
        {
            if (bitsLabel == null)
                return;

            bitsLabel.text = showPrefix ? $"{prefix}{amount}" : $"{amount}";
        }

        private void OnBitsChanged(int newAmount)
        {
            UpdateDisplay(newAmount);
            bitsLabel.color = normalColor;
        }

        private void OnBitsEarned(int amount, string reason)
        {
            StartCoroutine(FlashColor(earnColor, 0.5f));
        }

        private void OnBitsSpent(int amount, string reason)
        {
            StartCoroutine(FlashColor(spendColor, 0.5f));
        }

        private System.Collections.IEnumerator FlashColor(Color flashColor, float duration)
        {
            bitsLabel.color = flashColor;
            yield return new WaitForSeconds(duration);
            bitsLabel.color = normalColor;
        }
    }
}
