using UnityEngine;
using Velinor.Core;
using Velinor.Management;
using System.Collections.Generic;

namespace Velinor.Testing
{
    /// <summary>
    /// Quick setup helper to create and load the Saori encounter memory for testing.
    /// This demonstrates how to create memories at runtime and add them to the system.
    /// </summary>
    public class SaoriMemorySetup : MonoBehaviour
    {
        [SerializeField] private Sprite saoriIcon;  // Assign the icon sprite in Inspector
        [SerializeField] private bool autoCreateOnStart = true;

        private void Start()
        {
            if (autoCreateOnStart)
            {
                CreateSaoriMemory();
            }
        }

        /// <summary>
        /// Create the Saori encounter memory and add it to the manager.
        /// Call this manually or let it auto-run on Start.
        /// </summary>
        public void CreateSaoriMemory()
        {
            if (MindLogManager.Instance == null)
            {
                Debug.LogError("[SaoriMemorySetup] MindLogManager not found!");
                return;
            }

            // Create the memory entry
            var saoriMemory = new MindLogEntry(
                logID: "memory_saori_desert_encounter",
                icon: saoriIcon,
                summaryText: "Mysterious Encounter",
                fullText: "I met an older woman on the way to the marketplace. I didn't get her name, but she handed me this strange device without much explanation. There was something knowing in her eyes—as if she recognized me, or perhaps knew something about me that I didn't know myself. The device she gave me feels important, though I can't explain why."
            );

            // Add tags for combination matching
            saoriMemory.AddCombineTag("saori");
            saoriMemory.AddCombineTag("marketplace");
            saoriMemory.AddCombineTag("device");
            saoriMemory.AddCombineTag("mystery");

            // Add to manager
            MindLogManager.Instance.AddLog(saoriMemory);
            Debug.Log("[SaoriMemorySetup] Created Saori memory: memory_saori_desert_encounter");
        }
    }
}
