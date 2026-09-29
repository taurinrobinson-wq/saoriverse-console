using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

/// <summary>
/// Manages loading and displaying NPC portrait expressions in the dialogue UI.
/// Loads sprites from Resources/Portraits/{npcName}/{npcName}_{expression}.png
/// Falls back to neutral expression if specific expression not found.
/// </summary>
public class PortraitManager : MonoBehaviour
{
    [SerializeField] private Image portraitImage;
    private Dictionary<string, Sprite> portraitCache = new Dictionary<string, Sprite>();

    /// <summary>
    /// Maps display names (active_speaker) to portrait asset folder names.
    /// Allows showing "Lioren" in UI while loading portraits from "Player" folder.
    /// Add mappings here if character names differ from portrait folder names.
    /// </summary>
    private static readonly Dictionary<string, string> CharacterNameToPorfolioName = new Dictionary<string, string>
    {
        { "Lioren", "Player" },  // Player character - display as "Lioren" but load from Player folder
        // Add more mappings as needed: { "DisplayName", "PortraitFolderName" }
    };

    private void Awake()
    {
        if (portraitImage == null)
        {
            // Try to find the portrait image in DialoguePanel
            Canvas[] canvases = FindObjectsByType<Canvas>();
            foreach (Canvas c in canvases)
            {
                if (c.gameObject.name == "UI_Canvas")
                {
                    Transform dialoguePanelT = FindPanelRecursive(c.transform, "DialoguePanel");
                    if (dialoguePanelT != null)
                    {
                        portraitImage = dialoguePanelT.Find("NPCImage")?.GetComponent<Image>();
                        if (portraitImage == null)
                            portraitImage = dialoguePanelT.Find("NPC Image")?.GetComponent<Image>();
                        if (portraitImage == null)
                            portraitImage = dialoguePanelT.Find("Portrait")?.GetComponent<Image>();
                    }
                    break;
                }
            }
        }

        DontDestroyOnLoad(gameObject);
    }

    /// <summary>
    /// Load and display a portrait expression for an NPC.
    /// </summary>
    public void ShowPortrait(string npcName, string expression = "neutral")
    {
        if (portraitImage == null)
        {
            Debug.LogWarning("[PortraitManager] portraitImage not found");
            return;
        }

        // Try to load the specific expression first
        Sprite sprite = LoadPortraitSprite(npcName, expression);

        // Fall back to neutral if expression not found
        if (sprite == null && expression != "neutral")
        {
            Debug.LogWarning($"[PortraitManager] Portrait not found for {npcName}_{expression}, falling back to neutral");
            sprite = LoadPortraitSprite(npcName, "neutral");
        }

        if (sprite != null)
        {
            portraitImage.sprite = sprite;
            portraitImage.gameObject.SetActive(true);
            Debug.Log($"[PortraitManager] Displaying portrait: {npcName}_{expression}");
        }
        else
        {
            Debug.LogWarning($"[PortraitManager] Could not load portrait for {npcName} (no neutral fallback found either)");
            portraitImage.gameObject.SetActive(false);
        }
    }

    /// <summary>
    /// Clear the current portrait.
    /// </summary>
    public void HidePortrait()
    {
        if (portraitImage != null)
        {
            portraitImage.sprite = null;
            portraitImage.gameObject.SetActive(false);
        }
    }

    /// <summary>
    /// Load a portrait sprite, using cache if available.
    /// Loads from: Resources/Portraits/{portraitFolderName}/{portraitFolderName}_{expression}
    /// Uses CharacterNameToPorfolioName mapping to resolve display name to folder name.
    /// </summary>
    private Sprite LoadPortraitSprite(string npcName, string expression)
    {
        // Resolve display name to portrait folder name using mapping
        string portraitFolderName = npcName;
        if (CharacterNameToPorfolioName.ContainsKey(npcName))
        {
            portraitFolderName = CharacterNameToPorfolioName[npcName];
            Debug.Log($"[PortraitManager] Mapped '{npcName}' -> '{portraitFolderName}' for portrait loading");
        }

        string key = $"{npcName}_{expression}";

        // Check cache first
        if (portraitCache.ContainsKey(key))
            return portraitCache[key];

        // Try to load from Resources
        string resourcePath = $"Portraits/{portraitFolderName}/{portraitFolderName}_{expression}";
        Sprite sprite = Resources.Load<Sprite>(resourcePath);

        if (sprite != null)
        {
            portraitCache[key] = sprite;
            Debug.Log($"[PortraitManager] Loaded portrait: {resourcePath}");
        }
        else
        {
            // Try loading as Texture2D and converting to Sprite (fallback)
            Texture2D tex = Resources.Load<Texture2D>(resourcePath);
            if (tex != null)
            {
                Debug.LogWarning($"[PortraitManager] Portrait loaded as Texture2D (not Sprite): {resourcePath}. Importing as Sprite requires TextureType setting in .meta file.");
                sprite = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f));
                portraitCache[key] = sprite;
                return sprite;
            }
            Debug.LogWarning($"[PortraitManager] Portrait not found at: {resourcePath}");
        }

        return sprite;
    }

    private Transform FindPanelRecursive(Transform parent, string panelName)
    {
        if (parent.name == panelName)
            return parent;

        foreach (Transform child in parent)
        {
            Transform result = FindPanelRecursive(child, panelName);
            if (result != null)
                return result;
        }
        return null;
    }
}
