using UnityEngine;
using Velinor.Inventory;
using System;
using System.Collections.Generic;

namespace Velinor.Interactions
{
    /// <summary>
    /// Manages tool equipping and tool-specific interactions.
    /// Tracks which tool is currently equipped.
    /// </summary>
    public class ToolSystem : MonoBehaviour
    {
        public static ToolSystem Instance { get; private set; }

        private string equippedToolId = null;
        private ToolDefinition equippedToolDefinition = null;

        [SerializeField] private List<ToolDefinition> availableTools = new();

        public event Action<string> OnToolEquipped; // toolId
        public event Action OnToolUnequipped;

        public string EquippedToolId => equippedToolId;
        public ToolDefinition EquippedTool => equippedToolDefinition;

        private void Awake()
        {
            if (Instance != null)
            {
                Destroy(gameObject);
                return;
            }

            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        /// <summary>
        /// Check if player has learned/unlocked a specific tool.
        /// </summary>
        public bool HasTool(string toolId)
        {
            // Check if tool is in player's inventory (they learned it via recipe)
            var inventory = InventoryService.Instance;
            if (inventory != null)
            {
                return inventory.Contains(toolId, 1);
            }

            return false;
        }

        /// <summary>
        /// Equip a tool that player has learned.
        /// </summary>
        public bool EquipTool(string toolId)
        {
            if (!HasTool(toolId))
            {
                Debug.LogWarning($"Player doesn't have tool: {toolId}");
                return false;
            }

            var toolDef = GetToolDefinition(toolId);
            if (toolDef == null)
            {
                Debug.LogWarning($"Unknown tool definition: {toolId}");
                return false;
            }

            equippedToolId = toolId;
            equippedToolDefinition = toolDef;
            OnToolEquipped?.Invoke(toolId);
            Debug.Log($"Equipped tool: {toolId}");

            return true;
        }

        /// <summary>
        /// Unequip current tool.
        /// </summary>
        public void UnequipTool()
        {
            if (equippedToolId == null)
                return;

            equippedToolId = null;
            equippedToolDefinition = null;
            OnToolUnequipped?.Invoke();
            Debug.Log("Tool unequipped");
        }

        /// <summary>
        /// Get tool definition by ID.
        /// </summary>
        private ToolDefinition GetToolDefinition(string toolId)
        {
            foreach (var tool in availableTools)
            {
                if (tool != null && tool.ToolId == toolId)
                    return tool;
            }
            return null;
        }

        /// <summary>
        /// Check if a specific tool is currently equipped.
        /// </summary>
        public bool IsToolEquipped(string toolId)
        {
            return equippedToolId == toolId;
        }
    }

    /// <summary>
    /// Defines a tool that can be learned and equipped.
    /// </summary>
    [CreateAssetMenu(menuName = "Velinor/Tools/Tool Definition")]
    public class ToolDefinition : ScriptableObject
    {
        [SerializeField] private string toolId;
        [SerializeField] private string displayName;
        [TextArea] [SerializeField] private string description;
        [SerializeField] private Sprite icon;

        [Header("Interaction")]
        [Tooltip("Types of debris this tool can break (e.g., 'sealed_panel', 'rusted_bolt')")]
        [SerializeField] private List<string> canBreakDebrisTypes = new();

        [Header("Visuals")]
        [SerializeField] private Color equipHighlightColor = Color.yellow;
        [SerializeField] private float highlightIntensity = 1.2f;

        public string ToolId => toolId;
        public string DisplayName => displayName;
        public string Description => description;
        public Sprite Icon => icon;
        public List<string> CanBreakDebrisTypes => canBreakDebrisTypes;
        public Color EquipHighlightColor => equipHighlightColor;
        public float HighlightIntensity => highlightIntensity;

        /// <summary>
        /// Check if this tool can break a specific debris type.
        /// </summary>
        public bool CanBreak(string debrisType)
        {
            return canBreakDebrisTypes.Contains(debrisType);
        }
    }
}
