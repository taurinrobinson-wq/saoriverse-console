using UnityEngine;
using TMPro;

public class StatDisplayUI : MonoBehaviour
{
private TextMeshProUGUI playerStatsText;
        private TextMeshProUGUI npcStatsText;

        void Start()
        {
            CreateStatDisplay();
        }

        void CreateStatDisplay()
        {
            GameObject canvasObj = new GameObject("StatDisplayCanvas");
            var canvas = canvasObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 100;

            GameObject playerStatsObj = new GameObject("PlayerStatsText");
            playerStatsObj.transform.SetParent(canvasObj.transform, false);
            playerStatsText = playerStatsObj.AddComponent<TextMeshProUGUI>();
            playerStatsText.fontSize = 20;
            playerStatsText.color = Color.cyan;
            var pRect = playerStatsText.rectTransform;
            pRect.anchorMin = new Vector2(0, 1); pRect.anchorMax = new Vector2(0, 1);
            pRect.pivot = new Vector2(0, 1); pRect.anchoredPosition = new Vector2(10, -10);
            pRect.sizeDelta = new Vector2(400, 300);

            GameObject npcStatsObj = new GameObject("NPCStatsText");
            npcStatsObj.transform.SetParent(canvasObj.transform, false);
            npcStatsText = npcStatsObj.AddComponent<TextMeshProUGUI>();
            npcStatsText.fontSize = 20;
            npcStatsText.color = Color.magenta;
            npcStatsText.alignment = TextAlignmentOptions.TopRight;
            var nRect = npcStatsText.rectTransform;
            nRect.anchorMin = new Vector2(1, 1); nRect.anchorMax = new Vector2(1, 1);
            nRect.pivot = new Vector2(1, 1); nRect.anchoredPosition = new Vector2(-10, -10);
            nRect.sizeDelta = new Vector2(400, 300);
        }

        void Update()
        {
            if (StatManager.Instance == null) return;

            string pText = "<b>PLAYER TONE</b>\n";
            pText += $"Trust: {StatManager.Instance.GetPlayerTone(ToneType.Trust):F2}\n";
            pText += $"Observation: {StatManager.Instance.GetPlayerTone(ToneType.Observation):F2}\n";
            pText += $"Narrative Presence: {StatManager.Instance.GetPlayerTone(ToneType.NarrativePresence):F2}\n";
            pText += $"Empathy: {StatManager.Instance.GetPlayerTone(ToneType.Empathy):F2}\n";
            playerStatsText.text = pText;

            var npc = FindAnyObjectByType<NPCInteraction>();
            if (npc != null)
            {
                var r = StatManager.Instance.GetNpcRemnants(npc.npcId);
                if (r != null)
                {
                    string nText = $"<b>NPC: {npc.npcId}</b>\n";
                    nText += $"Trust: {r.trust:F2}\n";
                    nText += $"Empathy: {r.empathy:F2}\n";
                    nText += $"Authority: {r.authority:F2}\n";
                    nText += $"Resolve: {r.resolve:F2}\n";
                    npcStatsText.text = nText;
                }
            }
            else
            {
                npcStatsText.text = "No NPC Active";
            }
        }
    }
