using System;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using Velinor.Core;

namespace Velinor.UI.Codex
{
    /// <summary>
    /// Manages the Mind Log 3x3 memory fragment grid, including selection,
    /// synopsis updates, and double-click expansion requests.
    /// </summary>
    public class MemoryGridUI : MonoBehaviour
    {
        [Serializable]
        private sealed class GridCellBinding
        {
            [SerializeField] private Button button;
            [SerializeField] private Image iconImage;
            [SerializeField] private Image selectionHighlight;

            public Button Button => button;
            public Image IconImage => iconImage;
            public Image SelectionHighlight => selectionHighlight;
        }

        [Header("Grid")]
        [SerializeField] private List<GridCellBinding> gridCells = new List<GridCellBinding>(9);
        [SerializeField] private Color defaultCellTint = Color.white;
        [SerializeField] private Color selectedCellTint = new Color(1f, 0.88f, 0.45f, 1f);
        [SerializeField] private float doubleClickThreshold = 0.25f;

        [Header("Display")]
        [SerializeField] private TextMeshProUGUI synopsisText;
        [SerializeField] private MemoryExpandedUI expandedView;
        [SerializeField] private global::CodexViewController codexViewController;

        private readonly List<MemoryFragment> selectedFragments = new List<MemoryFragment>();
        private readonly Dictionary<MemoryFragment, GridCellBinding> cellLookup = new Dictionary<MemoryFragment, GridCellBinding>();
        private readonly List<MemoryFragment> displayedFragments = new List<MemoryFragment>(9);

        private Coroutine pendingSingleClickCoroutine;
        private MemoryFragment pendingClickFragment;
        private float lastClickTime = -1f;

        /// <summary>
        /// Raised whenever the grid selection changes.
        /// </summary>
        public event Action<IReadOnlyList<MemoryFragment>> SelectionChanged;

        /// <summary>
        /// Raised when a fragment is expanded into the secondary view.
        /// </summary>
        public event Action<MemoryFragment> FragmentExpanded;

        private void Awake()
        {
            ConfigureCells();
            ClearGridVisuals();
        }

        private void OnDisable()
        {
            if (pendingSingleClickCoroutine != null)
            {
                StopCoroutine(pendingSingleClickCoroutine);
                pendingSingleClickCoroutine = null;
            }
        }

        /// <summary>
        /// Populates the 3x3 grid with the supplied memory fragments.
        /// </summary>
        /// <param name="fragments">Fragments to display in the grid.</param>
        public void PopulateGrid(List<MemoryFragment> fragments)
        {
            displayedFragments.Clear();
            cellLookup.Clear();
            selectedFragments.RemoveAll(fragment => fragment == null);

            if (fragments == null)
            {
                Debug.LogWarning("[MemoryGridUI] PopulateGrid received a null fragment list. Clearing grid.");
                ClearGridVisuals();
                ClearSelection();
                return;
            }

            int clampedCount = Mathf.Min(fragments.Count, gridCells.Count);
            if (fragments.Count > gridCells.Count)
            {
                Debug.LogWarning($"[MemoryGridUI] Received {fragments.Count} fragments, but only {gridCells.Count} cells are available. Extra fragments will be ignored.");
            }

            for (int index = 0; index < gridCells.Count; index++)
            {
                GridCellBinding cell = gridCells[index];
                if (cell == null || cell.Button == null)
                {
                    Debug.LogWarning($"[MemoryGridUI] Grid cell at index {index} is not configured correctly.");
                    continue;
                }

                bool hasFragment = index < clampedCount && fragments[index] != null;
                ConfigureCellState(cell, hasFragment ? fragments[index] : null);
            }

            for (int index = 0; index < clampedCount; index++)
            {
                MemoryFragment fragment = fragments[index];
                if (fragment == null)
                {
                    Debug.LogWarning($"[MemoryGridUI] Fragment at index {index} is null and will be skipped.");
                    continue;
                }

                displayedFragments.Add(fragment);
                if (!cellLookup.ContainsKey(fragment))
                {
                    cellLookup.Add(fragment, gridCells[index]);
                }
            }

            selectedFragments.RemoveAll(fragment => !displayedFragments.Contains(fragment));
            HighlightSelectedFragments();

            Debug.Log($"[MemoryGridUI] Grid populated with {displayedFragments.Count} memory fragments.");
        }

        /// <summary>
        /// Processes a single-click interaction for a fragment.
        /// </summary>
        /// <param name="fragment">The clicked memory fragment.</param>
        public void OnGridCellClicked(MemoryFragment fragment)
        {
            if (fragment == null)
            {
                Debug.LogWarning("[MemoryGridUI] OnGridCellClicked called with a null fragment.");
                return;
            }

            if (selectedFragments.Contains(fragment))
            {
                selectedFragments.Remove(fragment);
                Debug.Log($"[MemoryGridUI] Deselected fragment '{fragment.fragmentID}'.");
            }
            else
            {
                selectedFragments.Add(fragment);
                Debug.Log($"[MemoryGridUI] Selected fragment '{fragment.fragmentID}'.");
            }

            if (synopsisText != null)
            {
                synopsisText.text = string.IsNullOrWhiteSpace(fragment.shortSynopsis)
                    ? fragment.displayName
                    : fragment.shortSynopsis;
            }

            HighlightSelectedFragments();
            NotifySelectionChanged();
        }

        /// <summary>
        /// Processes a double-click interaction for a fragment.
        /// </summary>
        /// <param name="fragment">The fragment to expand.</param>
        public void OnGridCellDoubleClicked(MemoryFragment fragment)
        {
            if (fragment == null)
            {
                Debug.LogWarning("[MemoryGridUI] OnGridCellDoubleClicked called with a null fragment.");
                return;
            }

            if (!selectedFragments.Contains(fragment))
            {
                selectedFragments.Add(fragment);
                HighlightSelectedFragments();
                NotifySelectionChanged();
            }

            if (synopsisText != null)
            {
                synopsisText.text = string.IsNullOrWhiteSpace(fragment.shortSynopsis)
                    ? fragment.displayName
                    : fragment.shortSynopsis;
            }

            Debug.Log($"[MemoryGridUI] Double-clicked fragment '{fragment.fragmentID}'. Opening expanded view.");

            if (expandedView != null)
            {
                expandedView.DisplayMemory(fragment);
            }
            else
            {
                Debug.LogWarning("[MemoryGridUI] Expanded view reference is missing. Double-click will only notify listeners.");
            }

            FragmentExpanded?.Invoke(fragment);

            if (codexViewController != null)
            {
                codexViewController.SendMessage("OnMemoryFragmentExpanded", fragment, SendMessageOptions.DontRequireReceiver);
            }
        }

        /// <summary>
        /// Returns a copy of the currently selected fragments.
        /// </summary>
        /// <returns>A new list containing the selected fragments.</returns>
        public List<MemoryFragment> GetSelectedFragments()
        {
            return new List<MemoryFragment>(selectedFragments);
        }

        /// <summary>
        /// Clears the current grid selection and visual highlights.
        /// </summary>
        public void ClearSelection()
        {
            if (selectedFragments.Count == 0 && synopsisText != null && string.IsNullOrEmpty(synopsisText.text))
            {
                return;
            }

            selectedFragments.Clear();

            if (synopsisText != null)
            {
                synopsisText.text = string.Empty;
            }

            HighlightSelectedFragments();
            NotifySelectionChanged();
            Debug.Log("[MemoryGridUI] Cleared memory grid selection.");
        }

        /// <summary>
        /// Updates visual selection highlights for all displayed fragments.
        /// </summary>
        public void HighlightSelectedFragments()
        {
            for (int index = 0; index < gridCells.Count; index++)
            {
                GridCellBinding cell = gridCells[index];
                if (cell == null || cell.Button == null)
                {
                    continue;
                }

                bool isSelected = false;
                if (index < displayedFragments.Count)
                {
                    MemoryFragment fragment = displayedFragments[index];
                    isSelected = fragment != null && selectedFragments.Contains(fragment);
                }

                if (cell.SelectionHighlight != null)
                {
                    cell.SelectionHighlight.enabled = isSelected;
                }

                Graphic graphic = cell.Button.targetGraphic;
                if (graphic != null)
                {
                    graphic.color = isSelected ? selectedCellTint : defaultCellTint;
                }
            }
        }

        internal void RegisterGridCellClick(MemoryFragment fragment)
        {
            if (fragment == null)
            {
                Debug.LogWarning("[MemoryGridUI] RegisterGridCellClick called with a null fragment.");
                return;
            }

            float clickTime = Time.unscaledTime;
            bool isDoubleClick = pendingClickFragment == fragment && clickTime - lastClickTime <= doubleClickThreshold;

            if (isDoubleClick)
            {
                if (pendingSingleClickCoroutine != null)
                {
                    StopCoroutine(pendingSingleClickCoroutine);
                    pendingSingleClickCoroutine = null;
                }

                pendingClickFragment = null;
                lastClickTime = -1f;
                OnGridCellDoubleClicked(fragment);
                return;
            }

            pendingClickFragment = fragment;
            lastClickTime = clickTime;

            if (pendingSingleClickCoroutine != null)
            {
                StopCoroutine(pendingSingleClickCoroutine);
            }

            pendingSingleClickCoroutine = StartCoroutine(ProcessSingleClickAfterDelay(fragment, clickTime));
        }

        private void ConfigureCells()
        {
            for (int index = 0; index < gridCells.Count; index++)
            {
                GridCellBinding cell = gridCells[index];
                if (cell == null || cell.Button == null)
                {
                    Debug.LogWarning($"[MemoryGridUI] Unable to configure cell at index {index}. Button reference is missing.");
                    continue;
                }

                MemoryGridCellRelay relay = cell.Button.GetComponent<MemoryGridCellRelay>();
                if (relay == null)
                {
                    relay = cell.Button.gameObject.AddComponent<MemoryGridCellRelay>();
                }

                relay.Configure(this, null);
            }
        }

        private void ConfigureCellState(GridCellBinding cell, MemoryFragment fragment)
        {
            MemoryGridCellRelay relay = cell.Button.GetComponent<MemoryGridCellRelay>();
            if (relay == null)
            {
                relay = cell.Button.gameObject.AddComponent<MemoryGridCellRelay>();
            }

            relay.Configure(this, fragment);

            bool hasFragment = fragment != null;
            cell.Button.interactable = hasFragment;

            if (cell.IconImage != null)
            {
                cell.IconImage.enabled = hasFragment;
                cell.IconImage.sprite = hasFragment ? fragment.icon : null;
                cell.IconImage.color = hasFragment ? Color.white : Color.clear;
                cell.IconImage.preserveAspect = true;
            }

            if (cell.SelectionHighlight != null)
            {
                cell.SelectionHighlight.enabled = false;
            }

            Graphic graphic = cell.Button.targetGraphic;
            if (graphic != null)
            {
                graphic.color = defaultCellTint;
            }
        }

        private void ClearGridVisuals()
        {
            displayedFragments.Clear();
            cellLookup.Clear();

            foreach (GridCellBinding cell in gridCells)
            {
                if (cell == null || cell.Button == null)
                {
                    continue;
                }

                ConfigureCellState(cell, null);
            }
        }

        private IEnumerator ProcessSingleClickAfterDelay(MemoryFragment fragment, float clickTimestamp)
        {
            yield return new WaitForSecondsRealtime(doubleClickThreshold);

            if (pendingClickFragment == fragment && Mathf.Approximately(lastClickTime, clickTimestamp))
            {
                pendingClickFragment = null;
                lastClickTime = -1f;
                OnGridCellClicked(fragment);
            }

            pendingSingleClickCoroutine = null;
        }

        private void NotifySelectionChanged()
        {
            List<MemoryFragment> selectionSnapshot = GetSelectedFragments();
            SelectionChanged?.Invoke(selectionSnapshot);

            if (codexViewController != null)
            {
                codexViewController.SendMessage("OnMemorySelectionChanged", selectionSnapshot, SendMessageOptions.DontRequireReceiver);
            }
        }
    }

    [RequireComponent(typeof(Button))]
    internal sealed class MemoryGridCellRelay : MonoBehaviour
    {
        private MemoryGridUI parent;
        private MemoryFragment fragment;
        private Button button;

        private void Awake()
        {
            button = GetComponent<Button>();
        }

        private void OnEnable()
        {
            if (button == null)
            {
                button = GetComponent<Button>();
            }

            if (button != null)
            {
                button.onClick.AddListener(HandleButtonClicked);
            }
        }

        private void OnDisable()
        {
            if (button != null)
            {
                button.onClick.RemoveListener(HandleButtonClicked);
            }
        }

        public void Configure(MemoryGridUI owner, MemoryFragment assignedFragment)
        {
            parent = owner;
            fragment = assignedFragment;
        }

        private void HandleButtonClicked()
        {
            if (parent == null)
            {
                Debug.LogWarning("[MemoryGridCellRelay] Click ignored because the parent grid is missing.");
                return;
            }

            parent.RegisterGridCellClick(fragment);
        }
    }
}
