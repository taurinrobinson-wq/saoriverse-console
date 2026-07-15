using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using System.Linq;

namespace Velinor.UI
{
    /// <summary>
    /// OverworldMapUI - Manages the fast-travel map system
    /// 
    /// Displays the overworld map as an interactive fast-travel interface
    /// Shows regions, travel times, and player's current position
    /// </summary>
    public class OverworldMapUI : MonoBehaviour
    {
        [SerializeField] private Image mapImage;
        [SerializeField] private Canvas mapCanvas;
        [SerializeField] private Button closeButton;
        [SerializeField] private Text regionNameText;
        [SerializeField] private Text regionDescriptionText;
        [SerializeField] private Text travelTimeText;

        private Dictionary<string, RegionButton> regionButtons = new();
        private string currentRegion = "market_basin";
        private bool isMapOpen = false;

        private void Start()
        {
            InitializeMap();
            setupRegionButtons();
            closeButton.onClick.AddListener(CloseMap);
        }

        /// <summary>
        /// Initialize the map display
        /// </summary>
        private void InitializeMap()
        {
            // Load map image
            mapImage.sprite = Resources.Load<Sprite>(
                "DesignDocs/OverworldMap_Labeled"
            );

            if (mapImage.sprite == null)
            {
                Debug.LogError("OverworldMap_Labeled sprite not found in Resources/DesignDocs/");
            }
        }

        /// <summary>
        /// Setup interactive region buttons on the map
        /// </summary>
        private void setupRegionButtons()
        {
            // Create buttons for each region at map positions
            // This would be done either programmatically or via prefab
            // For now, this is a placeholder for the architecture

            var regions = new[]
            {
                "archive_district", "shrine_ridge", "market_basin",
                "desert_expanse", "harbor_lowlands", "swamp_lowlands",
                "buried_archives", "concourse_ruins"
            };

            foreach (var regionId in regions)
            {
                var button = CreateRegionButton(regionId);
                regionButtons[regionId] = button;
            }
        }

        /// <summary>
        /// Create a button for a region
        /// </summary>
        private RegionButton CreateRegionButton(string regionId)
        {
            var buttonGO = new GameObject($"Btn_{regionId}");
            buttonGO.transform.SetParent(mapCanvas.transform, false);

            var button = buttonGO.AddComponent<Button>();
            var image = buttonGO.AddComponent<Image>();
            image.color = new Color(0.54f, 0.45f, 0.33f, 0.5f); // Semi-transparent brown

            var regionButton = buttonGO.AddComponent<RegionButton>();
            regionButton.Initialize(regionId, this);

            return regionButton;
        }

        /// <summary>
        /// Display region information when hovering
        /// </summary>
        public void ShowRegionInfo(string regionId, string regionName,
            string description, string climate, string npc)
        {
            regionNameText.text = regionName;
            regionDescriptionText.text = description;

            // Calculate travel time if different from current region
            if (regionId != currentRegion)
            {
                var travelTime = CalculateTravelTime(currentRegion, regionId);
                travelTimeText.text = $"Travel time: {travelTime} minutes";
                travelTimeText.gameObject.SetActive(true);
            }
            else
            {
                travelTimeText.text = "Current Location";
                travelTimeText.gameObject.SetActive(true);
            }
        }

        /// <summary>
        /// Initiate fast-travel to a region
        /// </summary>
        public void FastTravelTo(string regionId, string regionName)
        {
            if (regionId == currentRegion)
            {
                Debug.Log($"Already in {regionName}");
                return;
            }

            var travelTime = CalculateTravelTime(currentRegion, regionId);
            Debug.Log($"Traveling to {regionName}... ({travelTime} minutes)");

            // Trigger fade transition
            StartCoroutine(ExecuteFastTravel(regionId, travelTime));
        }

        /// <summary>
        /// Calculate travel time between two regions
        /// </summary>
        private int CalculateTravelTime(string fromRegion, string toRegion)
        {
            // This would load from the fast_travel_config.json
            // For now, return a base value
            var route = $"{fromRegion}_{toRegion}";

            return route switch
            {
                "desert_expanse_market_basin" => 15,
                "market_basin_archive_district" => 20,
                "market_basin_shrine_ridge" => 18,
                "market_basin_swamp_lowlands" => 22,
                "market_basin_harbor_lowlands" => 25,
                "concourse_ruins_archive_district" => 8,
                "concourse_ruins_market_basin" => 10,
                _ => 12 // Default travel time
            };
        }

        /// <summary>
        /// Execute the fast-travel sequence
        /// </summary>
        private System.Collections.IEnumerator ExecuteFastTravel(
            string destinationRegion, int travelTimeMinutes)
        {
            // Fade out
            yield return FadeOut(0.5f);

            // Update player location
            currentRegion = destinationRegion;

            // Trigger scene/location change
            // This would integrate with your scene management system

            // Fade in
            yield return FadeIn(0.5f);

            // Close map
            CloseMap();
        }

        /// <summary>
        /// Fade screen to black
        /// </summary>
        private System.Collections.IEnumerator FadeOut(float duration)
        {
            // Implementation would depend on your UI system
            yield return new WaitForSeconds(duration);
        }

        /// <summary>
        /// Fade screen from black
        /// </summary>
        private System.Collections.IEnumerator FadeIn(float duration)
        {
            // Implementation would depend on your UI system
            yield return new WaitForSeconds(duration);
        }

        /// <summary>
        /// Open the map UI
        /// </summary>
        public void OpenMap()
        {
            mapCanvas.gameObject.SetActive(true);
            isMapOpen = true;
        }

        /// <summary>
        /// Close the map UI
        /// </summary>
        public void CloseMap()
        {
            mapCanvas.gameObject.SetActive(false);
            isMapOpen = false;
        }

        /// <summary>
        /// Toggle map visibility
        /// </summary>
        public void ToggleMap()
        {
            if (isMapOpen)
                CloseMap();
            else
                OpenMap();
        }

        /// <summary>
        /// Check if map is currently open
        /// </summary>
        public bool IsMapOpen => isMapOpen;

        /// <summary>
        /// Get player's current region
        /// </summary>
        public string GetCurrentRegion() => currentRegion;

        /// <summary>
        /// Set player's current region
        /// </summary>
        public void SetCurrentRegion(string regionId) => currentRegion = regionId;
    }

    /// <summary>
    /// RegionButton - Individual button for a region on the map
    /// </summary>
    public class RegionButton : MonoBehaviour
    {
        private string regionId;
        private OverworldMapUI mapUI;
        private Button button;
        private Image image;

        public void Initialize(string id, OverworldMapUI ui)
        {
            regionId = id;
            mapUI = ui;
            button = GetComponent<Button>();
            image = GetComponent<Image>();

            button.onClick.AddListener(OnClick);

            // Add event triggers for hover
            var eventTrigger = gameObject.AddComponent<EventTrigger>();

            // OnPointerEnter
            EventTrigger.Entry pointerEnter = new();
            pointerEnter.eventID = EventTriggerType.PointerEnter;
            pointerEnter.callback.AddListener(_ => OnPointerEnter());
            eventTrigger.triggers.Add(pointerEnter);

            // OnPointerExit
            EventTrigger.Entry pointerExit = new();
            pointerExit.eventID = EventTriggerType.PointerExit;
            pointerExit.callback.AddListener(_ => OnPointerExit());
            eventTrigger.triggers.Add(pointerExit);
        }

        private void OnPointerEnter()
        {
            // Highlight region
            image.color = new Color(0.83f, 0.65f, 0.45f, 0.7f); // Lighter brown

            // Show region info (would load from config)
            mapUI.ShowRegionInfo(
                regionId,
                GetRegionName(),
                GetRegionDescription(),
                GetRegionClimate(),
                GetPrimaryNPC()
            );
        }

        private void OnPointerExit()
        {
            // Restore normal color
            image.color = new Color(0.54f, 0.45f, 0.33f, 0.5f);
        }

        private void OnClick()
        {
            mapUI.FastTravelTo(regionId, GetRegionName());
        }

        // These would load from fast_travel_config.json in production
        private string GetRegionName() => regionId switch
        {
            "archive_district" => "Archive District",
            "shrine_ridge" => "Shrine Ridge",
            "market_basin" => "Market Basin",
            "desert_expanse" => "Desert & Mountain Expanse",
            "harbor_lowlands" => "Harbor Air Lowlands",
            "swamp_lowlands" => "Swamid Swamps & Lowlands",
            "buried_archives" => "Buried Tomb Archives",
            "concourse_ruins" => "Concourse Ruins",
            _ => "Unknown Region"
        };

        private string GetRegionDescription() => regionId switch
        {
            "archive_district" => "Ruins of past Velhara - towering structures crumble with age",
            "shrine_ridge" => "Ancient temples cling to northern cliffs - sacred and haunted",
            "market_basin" => "The living heart of Velhara - bustling with survivors and traders",
            "desert_expanse" => "Vast emptiness where the journey began - sandy dunes meet rocky peaks",
            _ => "A region of Velhara"
        };

        private string GetRegionClimate() => regionId switch
        {
            "archive_district" => "Dry, dusty winds sweep through broken architecture",
            "shrine_ridge" => "Cool, thin air - whispers carry far",
            "market_basin" => "Variable, sheltered by surrounding structures",
            _ => "Unknown climate"
        };

        private string GetPrimaryNPC() => regionId switch
        {
            "archive_district" => "Archivist Malrik",
            "shrine_ridge" => "High Seer Elenya",
            "market_basin" => "Ravi & Nima",
            "desert_expanse" => "Saori",
            _ => "Unknown NPC"
        };
    }
}
