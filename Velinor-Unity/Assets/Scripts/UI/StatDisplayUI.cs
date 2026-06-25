using UnityEngine;
using TMPro;

/// <summary>
/// StatDisplayUI: Visual in-game display of TONE/REMNANTS stats
/// Shows player and NPC emotional state during dialogue testing
/// </summary>
public class StatDisplayUI : MonoBehaviour
{
    private Canvas statsCanvas;
    private TextMeshProUGUI playerStatsText;
    private TextMeshProUGUI npcStatsText;
    private PlayerStats playerStats;
    private NPCInteraction currentNPC;

    void Start()
    {
        CreateStatDisplay();
        playerStats = PlayerStats.Get();
    }

    void CreateStatDisplay()
    {
        // Create canvas for stat display (top-left corner)
        GameObject canvasObj = new GameObject("StatDisplayCanvas");
        statsCanvas = canvasObj.AddComponent<Canvas>();
        statsCanvas.renderMode = RenderMode.ScreenSpaceOverlay;
        statsCanvas.sortingOrder = 100;  // Above dialogue

        RectTransform canvasRect = canvasObj.GetComponent<RectTransform>();
        canvasRect.anchorMin = Vector2.zero;
        canvasRect.anchorMax = Vector2.one;
        canvasRect.offsetMin = Vector2.zero;
        canvasRect.offsetMax = Vector2.zero;

        // Player stats display (top-left)
        GameObject playerStatsObj = new GameObject("PlayerStatsText");
        playerStatsObj.transform.SetParent(canvasObj.transform, false);
        playerStatsText = playerStatsObj.AddComponent<TextMeshProUGUI>();
        playerStatsText.text = "PLAYER STATS";
        playerStatsText.fontSize = 24;
        playerStatsText.alignment = TextAlignmentOptions.TopLeft;
        playerStatsText.color = Color.cyan;

        RectTransform playerRect = playerStatsObj.GetComponent<RectTransform>();
        playerRect.anchorMin = new Vector2(0, 1);
        playerRect.anchorMax = new Vector2(0, 1);
        playerRect.pivot = new Vector2(0, 1);
        playerRect.anchoredPosition = new Vector2(10, -10);
        playerRect.sizeDelta = new Vector2(500, 400);

        // NPC stats display (top-right)
        GameObject npcStatsObj = new GameObject("NPCStatsText");
        npcStatsObj.transform.SetParent(canvasObj.transform, false);
        npcStatsText = npcStatsObj.AddComponent<TextMeshProUGUI>();
        npcStatsText.text = "NPC STATS";
        npcStatsText.fontSize = 24;
        npcStatsText.alignment = TextAlignmentOptions.TopRight;
        npcStatsText.color = Color.magenta;

        RectTransform npcRect = npcStatsObj.GetComponent<RectTransform>();
        npcRect.anchorMin = new Vector2(1, 1);
        npcRect.anchorMax = new Vector2(1, 1);
        npcRect.pivot = new Vector2(1, 1);
        npcRect.anchoredPosition = new Vector2(-10, -10);
        npcRect.sizeDelta = new Vector2(500, 400);
    }

    void Update()
    {
        UpdatePlayerStatsDisplay();
        UpdateNPCStatsDisplay();
    }

    void UpdatePlayerStatsDisplay()
    {
        if (playerStats == null || playerStatsText == null) return;

        string display = "<b>PLAYER STATS</b>\n";
        display += $"<size=20>";
        display += $"\n<color=yellow>TONE:</color>\n";
        display += $"  T(rust):        {playerStats.TrustTone:F2}\n";
        display += $"  O(bservation):  {playerStats.ObservationTone:F2}\n";
        display += $"  N(arrative):    {playerStats.NarrativeTone:F2}\n";
        display += $"  E(mpathy):      {playerStats.EmpathyTone:F2}\n";
        
        display += $"\n<color=cyan>REMNANTS:</color>\n";
        display += $"  Resolve:     {playerStats.Resolve:F2}\n";
        display += $"  Empathy:     {playerStats.Empathy:F2}\n";
        display += $"  Memory:      {playerStats.Memory:F2}\n";
        display += $"  Nuance:      {playerStats.Nuance:F2}\n";
        display += $"  Authority:   {playerStats.Authority:F2}\n";
        display += $"  Need:        {playerStats.Need:F2}\n";
        display += $"  Trust:       {playerStats.Trust:F2}\n";
        display += $"  Skepticism:  {playerStats.Skepticism:F2}\n";
        display += $"</size>";

        playerStatsText.text = display;
    }

    void UpdateNPCStatsDisplay()
    {
        if (npcStatsText == null) return;

        // Find the NPC currently in dialogue (if any)
        NPCInteraction npc = FindAnyObjectByType<NPCInteraction>();
        if (npc == null)
        {
            npcStatsText.text = "<b>NPC STATS</b>\n(No NPC in range)";
            return;
        }

        // Get Ravi's stats through reflection (they're private in NPCInteraction)
        // For now, show a placeholder
        string display = "<b>NPC STATS (RAVI)</b>\n";
        display += $"<size=20>";
        display += $"\n<color=magenta>REMNANTS:</color>\n";
        display += $"  Resolve:     ??? \n";
        display += $"  Empathy:     ??? \n";
        display += $"  Memory:      ??? \n";
        display += $"  Nuance:      ??? \n";
        display += $"  Authority:   ??? \n";
        display += $"  Need:        ??? \n";
        display += $"  Trust:       ??? \n";
        display += $"  Skepticism:  ??? \n";
        display += $"</size>\n\n<size=16>(Stats update visible when dialogue starts)</size>";

        npcStatsText.text = display;
    }
}
