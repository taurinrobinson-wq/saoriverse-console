using UnityEngine;
using TMPro;
using Velinor.Core;
using Velinor.UI.Codex;
using Velinor.Management;
using System.Collections.Generic;

namespace Velinor.Core
{
    /// <summary>
    /// Controller for the Memory Grid using the slot-based system.
    /// Manages memory display, selection, and interaction with the Mind Log views.
    /// Supports both direct MemoryFragment population (test mode) and MindLogManager (real data).
    /// </summary>
    public class MemoryGridController : MonoBehaviour
    {
        [SerializeField] private Transform gridContainer;
        [SerializeField] private TextMeshProUGUI synopsisText;
        [SerializeField] private MemoryExpandedUI expandedView;

        private List<MemorySlot> memorySlots = new List<MemorySlot>();
        private Dictionary<MemorySlot, MemoryFragment> slotToFragment = new Dictionary<MemorySlot, MemoryFragment>();

        private void Start()
        {
            // Auto-find all MemorySlots in the container
            if (gridContainer == null)
            {
                gridContainer = transform;
            }

            MemorySlot[] slots = gridContainer.GetComponentsInChildren<MemorySlot>();
            memorySlots.AddRange(slots);

            Debug.Log($"[MemoryGridController] Found {memorySlots.Count} memory slots");
        }

        /// <summary>
        /// Populate the grid from MindLogManager (real data).
        /// </summary>
        public void PopulateFromManager()
        {
            if (MindLogManager.Instance == null)
            {
                Debug.LogError("[MemoryGridController] MindLogManager instance not found!");
                return;
            }

            var logs = MindLogManager.Instance.GetAllLogs();
            var logList = new List<MindLogEntry>(logs);

            // Clear existing selections
            foreach (MemorySlot slot in memorySlots)
            {
                slot.Unhighlight();
                slot.Clear();
            }

            slotToFragment.Clear();

            // Populate slots with logs from manager
            int index = 0;
            foreach (var log in logList)
            {
                if (index >= memorySlots.Count) break;

                if (log != null && log.Icon != null)
                {
                    // Create a temporary MemoryFragment wrapper for the log
                    var fragment = ScriptableObject.CreateInstance<MemoryFragment>();
                    fragment.fragmentID = log.LogID;
                    fragment.displayName = log.LogID;
                    fragment.icon = log.Icon;
                    fragment.shortSynopsis = log.SummaryText;
                    fragment.expandedText = log.FullText;
                    fragment.tags = new List<string>(log.CombineTags);

                    memorySlots[index].SetMemory(fragment);
                    slotToFragment[memorySlots[index]] = fragment;
                    index++;
                }
            }

            // Clear remaining slots
            for (int i = index; i < memorySlots.Count; i++)
            {
                memorySlots[i].Clear();
            }

            Debug.Log($"[MemoryGridController] Populated grid with {index} memories from MindLogManager");
        }

        /// <summary>
        /// Populate the grid with memory fragments (test mode / backward compatibility).
        /// </summary>
        public void PopulateGrid(List<MemoryFragment> fragments)
        {
            // Clear existing selections
            foreach (MemorySlot slot in memorySlots)
            {
                slot.Unhighlight();
                slot.Clear();
            }

            slotToFragment.Clear();

            // Populate slots with memories
            for (int i = 0; i < memorySlots.Count && i < fragments.Count; i++)
            {
                if (fragments[i] != null)
                {
                    memorySlots[i].SetMemory(fragments[i]);
                    slotToFragment[memorySlots[i]] = fragments[i];
                }
            }

            // Clear remaining slots
            for (int i = fragments.Count; i < memorySlots.Count; i++)
            {
                memorySlots[i].Clear();
            }

            Debug.Log($"[MemoryGridController] Populated grid with {Mathf.Min(fragments.Count, memorySlots.Count)} memories");
        }

        /// <summary>
        /// Called when a memory is single-clicked.
        /// Updates the synopsis display.
        /// </summary>
        public void OnMemorySingleClicked(MemorySlot slot, MemoryFragment fragment)
        {
            if (fragment == null)
                return;

            // Update synopsis text
            if (synopsisText != null)
            {
                synopsisText.text = string.IsNullOrWhiteSpace(fragment.shortSynopsis)
                    ? fragment.displayName
                    : fragment.shortSynopsis;
            }

            Debug.Log($"[MemoryGridController] Synopsis updated: {fragment.shortSynopsis}");
        }

        /// <summary>
        /// Called when a memory is double-clicked.
        /// Opens the expanded view.
        /// </summary>
        public void OnMemoryDoubleClicked(MemorySlot slot, MemoryFragment fragment)
        {
            if (fragment == null)
                return;

            Debug.Log($"[MemoryGridController] Double-clicked memory '{fragment.fragmentID}', expandedView is null? {expandedView == null}");

            if (expandedView != null)
            {
                // Switch to secondary view FIRST to activate the container
                var codexViewController = FindAnyObjectByType<CodexViewController>();
                if (codexViewController != null)
                {
                    Debug.Log("[MemoryGridController] Switching to mind_log_secondary view");
                    codexViewController.SwitchView("mind_log_secondary");
                }
                else
                {
                    Debug.LogError("[MemoryGridController] CodexViewController not found!");
                }

                // THEN display the memory (after container is active)
                expandedView.DisplayMemory(fragment);
            }
            else
            {
                Debug.LogError("[MemoryGridController] Expanded view is not assigned! Assign MemoryExpandedUI in the inspector.");
            }
        }
    }
}
