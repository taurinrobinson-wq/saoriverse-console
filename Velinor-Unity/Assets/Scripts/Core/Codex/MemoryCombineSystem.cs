using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// Handles Mind Log fragment combination logic, deduction creation,
    /// transition timing, and success notifications.
    /// </summary>
    public class MemoryCombineSystem : MonoBehaviour
    {
        [Header("Resources")]
        [SerializeField] private string validCombinationsResourcePath = "Data/ValidMemoryCombinations";

        [Header("Dependencies")]
        [SerializeField] private Velinor.UI.Codex.MemoryGridUI memoryGridUI;
        [SerializeField] private CanvasGroup combinationAnimationCanvasGroup;
        [SerializeField] private float combinationAnimationDuration = 0.35f;
        [SerializeField] private global::CodexViewController codexViewController;

        [Header("Notifications")]
        [SerializeField] private string successNotificationFormat = "New deduction discovered: {0}";

        private readonly Dictionary<string, MemoryFragment> fragmentPrototypeCache = new Dictionary<string, MemoryFragment>(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, MemoryFragment> runtimeDeductionCache = new Dictionary<string, MemoryFragment>(StringComparer.OrdinalIgnoreCase);

        private ValidMemoryCombinations validMemoryCombinations;
        private global::NotificationPanelController notificationPanel;

        /// <summary>
        /// Raised when a deduction fragment is created successfully.
        /// </summary>
        public event Action<MemoryFragment> DeductionCreated;

        private void Awake()
        {
            LoadCombinationData();
            CacheMemoryFragments();
            notificationPanel = FindAnyObjectByType<global::NotificationPanelController>();

            if (notificationPanel == null)
            {
                Debug.LogWarning("[MemoryCombineSystem] NotificationPanelController was not found. Combination notifications will be skipped.");
            }
        }

        /// <summary>
        /// Returns true when the selected fragments exactly match a configured combination.
        /// </summary>
        /// <param name="fragments">The selected fragments.</param>
        /// <returns>True if a valid combination exists; otherwise false.</returns>
        public bool CanCombine(List<MemoryFragment> fragments)
        {
            bool canCombine = GetCombination(fragments) != null;
            Debug.Log($"[MemoryCombineSystem] CanCombine evaluated to {canCombine}.");
            return canCombine;
        }

        /// <summary>
        /// Finds a configured combination matching the supplied fragments.
        /// </summary>
        /// <param name="fragments">The selected fragments to evaluate.</param>
        /// <returns>The matching combination, or null when no match exists.</returns>
        public MemoryCombinationPair GetCombination(List<MemoryFragment> fragments)
        {
            List<MemoryFragment> sanitizedFragments = SanitizeSelection(fragments);
            if (sanitizedFragments.Count < 2)
            {
                Debug.Log("[MemoryCombineSystem] At least two fragments are required to evaluate a combination.");
                return null;
            }

            if (validMemoryCombinations == null || validMemoryCombinations.combinations == null || validMemoryCombinations.combinations.Count == 0)
            {
                Debug.LogWarning("[MemoryCombineSystem] No valid memory combinations are loaded.");
                return null;
            }

            HashSet<string> selectedIds = new HashSet<string>(
                sanitizedFragments
                    .Where(fragment => !string.IsNullOrWhiteSpace(fragment.fragmentID))
                    .Select(fragment => fragment.fragmentID.Trim()),
                StringComparer.OrdinalIgnoreCase);

            foreach (MemoryCombinationPair combination in validMemoryCombinations.combinations)
            {
                if (combination == null)
                {
                    continue;
                }

                HashSet<string> requiredIds = GetRequiredFragmentIds(combination);
                if (requiredIds.Count < 2)
                {
                    Debug.LogWarning($"[MemoryCombineSystem] Combination '{combination.resultFragmentID}' is invalid because it does not define at least two source fragments.");
                    continue;
                }

                if (requiredIds.SetEquals(selectedIds))
                {
                    Debug.Log($"[MemoryCombineSystem] Found combination '{combination.resultFragmentID}' for fragments: {string.Join(", ", selectedIds)}");
                    return combination;
                }
            }

            Debug.Log($"[MemoryCombineSystem] No combination found for fragments: {string.Join(", ", selectedIds)}");
            return null;
        }

        /// <summary>
        /// Creates or reuses a deduction fragment for the provided combination result.
        /// </summary>
        /// <param name="combination">The matching memory combination.</param>
        /// <returns>The created deduction fragment, or null if creation fails.</returns>
        public MemoryFragment CreateDeduction(MemoryCombinationPair combination)
        {
            if (combination == null)
            {
                Debug.LogWarning("[MemoryCombineSystem] CreateDeduction was called with a null combination.");
                return null;
            }

            if (string.IsNullOrWhiteSpace(combination.resultFragmentID))
            {
                Debug.LogError("[MemoryCombineSystem] Cannot create a deduction because the result fragment ID is missing.");
                return null;
            }

            string resultId = combination.resultFragmentID.Trim();
            if (runtimeDeductionCache.TryGetValue(resultId, out MemoryFragment existingDeduction) && existingDeduction != null)
            {
                Debug.Log($"[MemoryCombineSystem] Reusing cached deduction '{resultId}'.");
                return existingDeduction;
            }

            MemoryFragment deduction = null;
            if (fragmentPrototypeCache.TryGetValue(resultId, out MemoryFragment prototype) && prototype != null)
            {
                deduction = Instantiate(prototype);
                Debug.Log($"[MemoryCombineSystem] Created deduction '{resultId}' from Resources prototype.");
            }
            else
            {
                deduction = ScriptableObject.CreateInstance<MemoryFragment>();
                deduction.fragmentID = resultId;
                deduction.displayName = ToDisplayName(resultId);
                deduction.shortSynopsis = deduction.displayName;
                deduction.expandedText = string.IsNullOrWhiteSpace(combination.combinationLogic)
                    ? $"{deduction.displayName} was inferred by combining related memory fragments."
                    : combination.combinationLogic;
                Debug.LogWarning($"[MemoryCombineSystem] No MemoryFragment asset found for '{resultId}'. Created a runtime fallback deduction instead.");
            }

            deduction.name = resultId;
            deduction.isDeduction = true;
            runtimeDeductionCache[resultId] = deduction;
            return deduction;
        }

        /// <summary>
        /// Combines the supplied fragments, plays the configured animation,
        /// clears the current selection, and announces the resulting deduction.
        /// </summary>
        /// <param name="fragments">The selected fragments to combine.</param>
        /// <returns>An enumerator for coroutine execution.</returns>
        public IEnumerator CombineFragments(List<MemoryFragment> fragments)
        {
            List<MemoryFragment> sanitizedFragments = SanitizeSelection(fragments);
            if (sanitizedFragments.Count < 2)
            {
                Debug.LogWarning("[MemoryCombineSystem] CombineFragments requires at least two selected fragments.");
                yield break;
            }

            MemoryCombinationPair combination = GetCombination(sanitizedFragments);
            if (combination == null)
            {
                Debug.LogWarning("[MemoryCombineSystem] The selected fragments do not form a valid combination.");
                yield break;
            }

            Debug.Log($"[MemoryCombineSystem] Combining fragments into '{combination.resultFragmentID}'.");
            yield return PlayCombinationAnimation();

            MemoryFragment deduction = CreateDeduction(combination);
            if (deduction == null)
            {
                Debug.LogError("[MemoryCombineSystem] Failed to create deduction fragment after a valid combination match.");
                yield break;
            }

            memoryGridUI?.ClearSelection();

            string notificationText = string.Format(
                CultureInfo.InvariantCulture,
                string.IsNullOrWhiteSpace(successNotificationFormat) ? "New deduction discovered: {0}" : successNotificationFormat,
                string.IsNullOrWhiteSpace(deduction.displayName) ? deduction.fragmentID : deduction.displayName);

            if (notificationPanel != null)
            {
                notificationPanel.ShowNotification(notificationText, 4f);
            }

            DeductionCreated?.Invoke(deduction);

            if (codexViewController != null)
            {
                codexViewController.SendMessage("OnMemoryDeductionCreated", deduction, SendMessageOptions.DontRequireReceiver);
            }

            Debug.Log($"[MemoryCombineSystem] Successfully created deduction '{deduction.fragmentID}'.");
        }

        private List<MemoryFragment> SanitizeSelection(List<MemoryFragment> fragments)
        {
            if (fragments == null)
            {
                return new List<MemoryFragment>();
            }

            return fragments
                .Where(fragment => fragment != null)
                .GroupBy(fragment => fragment.fragmentID ?? string.Empty, StringComparer.OrdinalIgnoreCase)
                .Select(group => group.First())
                .Where(fragment => !string.IsNullOrWhiteSpace(fragment.fragmentID))
                .ToList();
        }

        private void LoadCombinationData()
        {
            validMemoryCombinations = Resources.Load<ValidMemoryCombinations>(validCombinationsResourcePath);
            if (validMemoryCombinations == null)
            {
                Debug.LogError($"[MemoryCombineSystem] Unable to load ValidMemoryCombinations from Resources path '{validCombinationsResourcePath}'.");
                return;
            }

            Debug.Log($"[MemoryCombineSystem] Loaded {validMemoryCombinations.combinations.Count} memory combinations from '{validCombinationsResourcePath}'.");
        }

        private void CacheMemoryFragments()
        {
            fragmentPrototypeCache.Clear();

            MemoryFragment[] loadedFragments = Resources.LoadAll<MemoryFragment>(string.Empty);
            foreach (MemoryFragment fragment in loadedFragments)
            {
                if (fragment == null || string.IsNullOrWhiteSpace(fragment.fragmentID))
                {
                    continue;
                }

                if (fragmentPrototypeCache.ContainsKey(fragment.fragmentID))
                {
                    Debug.LogWarning($"[MemoryCombineSystem] Duplicate MemoryFragment resource detected for id '{fragment.fragmentID}'. Keeping the first occurrence.");
                    continue;
                }

                fragmentPrototypeCache.Add(fragment.fragmentID, fragment);
            }

            Debug.Log($"[MemoryCombineSystem] Cached {fragmentPrototypeCache.Count} MemoryFragment assets from Resources.");
        }

        private HashSet<string> GetRequiredFragmentIds(MemoryCombinationPair combination)
        {
            HashSet<string> requiredIds = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (string rawValue in new[] { combination.firstFragmentID, combination.secondFragmentID })
            {
                if (string.IsNullOrWhiteSpace(rawValue))
                {
                    continue;
                }

                string[] splitValues = rawValue.Split(new[] { '+', ',', ';', '|' }, StringSplitOptions.RemoveEmptyEntries);
                foreach (string splitValue in splitValues)
                {
                    string normalizedValue = splitValue.Trim();
                    if (!string.IsNullOrWhiteSpace(normalizedValue))
                    {
                        requiredIds.Add(normalizedValue);
                    }
                }
            }

            return requiredIds;
        }

        private IEnumerator PlayCombinationAnimation()
        {
            if (combinationAnimationCanvasGroup == null)
            {
                if (combinationAnimationDuration > 0f)
                {
                    yield return new WaitForSeconds(combinationAnimationDuration);
                }

                yield break;
            }

            combinationAnimationCanvasGroup.gameObject.SetActive(true);
            combinationAnimationCanvasGroup.alpha = 0f;

            float halfDuration = Mathf.Max(0.01f, combinationAnimationDuration * 0.5f);
            yield return FadeCanvasGroup(combinationAnimationCanvasGroup, 0f, 1f, halfDuration);
            yield return FadeCanvasGroup(combinationAnimationCanvasGroup, 1f, 0f, halfDuration);

            combinationAnimationCanvasGroup.gameObject.SetActive(false);
        }

        private IEnumerator FadeCanvasGroup(CanvasGroup canvasGroup, float startAlpha, float endAlpha, float duration)
        {
            if (canvasGroup == null)
            {
                yield break;
            }

            float elapsed = 0f;
            canvasGroup.alpha = startAlpha;

            while (elapsed < duration)
            {
                elapsed += Time.unscaledDeltaTime;
                canvasGroup.alpha = Mathf.Lerp(startAlpha, endAlpha, elapsed / duration);
                yield return null;
            }

            canvasGroup.alpha = endAlpha;
        }

        private static string ToDisplayName(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return "Unnamed Deduction";
            }

            string spacedValue = value.Replace('_', ' ').Replace('-', ' ').Trim();
            return CultureInfo.InvariantCulture.TextInfo.ToTitleCase(spacedValue);
        }
    }
}
