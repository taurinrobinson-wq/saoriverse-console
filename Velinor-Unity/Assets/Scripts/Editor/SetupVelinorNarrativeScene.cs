using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class SetupVelinorNarrativeScene
{
    [MenuItem("Velinor/Create Narrative Test Scene")]
    public static void CreateNarrativeTestScene()
    {
        // Create new scene
        var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects);
        scene.name = "VelinorNarrativeTest";

        // Get the main camera from default setup
        Camera mainCamera = Camera.main;
        if (mainCamera != null)
        {
            mainCamera.transform.position = new Vector3(0, 1, -5);
            mainCamera.transform.rotation = Quaternion.identity;
        }

        // ===== STEP 1: Create StatManager =====
        GameObject statManagerObj = new GameObject("StatManager");
        statManagerObj.AddComponent<StatManager>();
        Debug.Log("✅ Created StatManager singleton");

        // ===== STEP 2: Create DialogueManager =====
        GameObject dialogueManagerObj = new GameObject("DialogueManager");
        DialogueManager dialogueManager = dialogueManagerObj.AddComponent<DialogueManager>();
        Debug.Log("✅ Created DialogueManager singleton");

        // ===== STEP 3: Create DialogueCanvas =====
        GameObject canvasObj = new GameObject("DialogueCanvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        
        RectTransform canvasRect = canvasObj.GetComponent<RectTransform>();
        canvasRect.anchorMin = Vector2.zero;
        canvasRect.anchorMax = Vector2.one;
        canvasRect.offsetMin = Vector2.zero;
        canvasRect.offsetMax = Vector2.zero;

        canvasObj.AddComponent<GraphicRaycaster>();
        canvasObj.AddComponent<CanvasGroup>();

        // Add Canvas Scaler
        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);

        Debug.Log("✅ Created DialogueCanvas");

        // ===== STEP 4: Create DialoguePanel (background) =====
        GameObject panelObj = new GameObject("DialoguePanel");
        panelObj.transform.SetParent(canvasObj.transform, false);
        Image panelImage = panelObj.AddComponent<Image>();
        panelImage.color = new Color(0, 0, 0, 0.8f); // Semi-transparent black

        RectTransform panelRect = panelObj.GetComponent<RectTransform>();
        panelRect.anchorMin = Vector2.zero;
        panelRect.anchorMax = Vector2.one;
        panelRect.offsetMin = Vector2.zero;
        panelRect.offsetMax = Vector2.zero;

        Debug.Log("✅ Created DialoguePanel");

        // ===== STEP 5: Create NPCNameText =====
        GameObject nameTextObj = new GameObject("NPCNameText");
        nameTextObj.transform.SetParent(panelObj.transform, false);
        TextMeshProUGUI nameText = nameTextObj.AddComponent<TextMeshProUGUI>();
        nameText.text = "[NPC Name]";
        nameText.fontSize = 56;
        nameText.alignment = TextAlignmentOptions.TopLeft;
        nameText.color = Color.white;

        RectTransform nameRect = nameTextObj.GetComponent<RectTransform>();
        nameRect.anchorMin = new Vector2(0, 1);
        nameRect.anchorMax = new Vector2(0, 1);
        nameRect.pivot = new Vector2(0, 1);
        nameRect.anchoredPosition = new Vector2(40, -40);
        nameRect.sizeDelta = new Vector2(400, 80);

        Debug.Log("✅ Created NPCNameText");

        // ===== STEP 6: Create DialogueBody Text =====
        GameObject bodyTextObj = new GameObject("DialogueBodyText");
        bodyTextObj.transform.SetParent(panelObj.transform, false);
        TextMeshProUGUI bodyText = bodyTextObj.AddComponent<TextMeshProUGUI>();
        bodyText.text = "[Dialogue will appear here]";
        bodyText.fontSize = 32;
        bodyText.alignment = TextAlignmentOptions.TopLeft;
        bodyText.color = Color.white;
        bodyText.wordWrappingRatios = 0.3f; // Wrap words naturally

        RectTransform bodyRect = bodyTextObj.GetComponent<RectTransform>();
        bodyRect.anchorMin = new Vector2(0, 1);
        bodyRect.anchorMax = new Vector2(1, 1);
        bodyRect.pivot = new Vector2(0, 1);
        bodyRect.anchoredPosition = new Vector2(40, -140);
        bodyRect.sizeDelta = new Vector2(-80, 400);

        Debug.Log("✅ Created DialogueBodyText");

        // ===== STEP 7: Create ChoiceButtonContainer =====
        GameObject containerObj = new GameObject("ChoiceButtonContainer");
        containerObj.transform.SetParent(panelObj.transform, false);

        VerticalLayoutGroup layoutGroup = containerObj.AddComponent<VerticalLayoutGroup>();
        layoutGroup.spacing = 10;
        layoutGroup.childForceExpandHeight = false;
        layoutGroup.childForceExpandWidth = true;

        RectTransform containerRect = containerObj.GetComponent<RectTransform>();
        containerRect.anchorMin = new Vector2(0, 0);
        containerRect.anchorMax = Vector2.one;
        containerRect.pivot = new Vector2(0, 0);
        containerRect.anchoredPosition = new Vector2(40, 40);
        containerRect.sizeDelta = new Vector2(-80, 150);

        Debug.Log("✅ Created ChoiceButtonContainer");

        // ===== STEP 8: Create Choice Button Prefab =====
        GameObject buttonPrefabObj = new GameObject("ChoiceButtonPrefab");
        buttonPrefabObj.transform.SetParent(containerObj.transform, false);

        Image btnImage = buttonPrefabObj.AddComponent<Image>();
        btnImage.color = new Color(0.2f, 0.2f, 0.2f, 1f);

        Button btn = buttonPrefabObj.AddComponent<Button>();
        ColorBlock colors = btn.colors;
        colors.normalColor = new Color(0.2f, 0.2f, 0.2f, 1f);
        colors.highlightedColor = new Color(0.3f, 0.3f, 0.3f, 1f);
        colors.pressedColor = new Color(0.1f, 0.1f, 0.1f, 1f);
        btn.colors = colors;

        RectTransform btnRect = buttonPrefabObj.GetComponent<RectTransform>();
        btnRect.sizeDelta = new Vector2(0, 50);

        // Add text to button
        GameObject btnTextObj = new GameObject("Text");
        btnTextObj.transform.SetParent(buttonPrefabObj.transform, false);
        TextMeshProUGUI btnText = btnTextObj.AddComponent<TextMeshProUGUI>();
        btnText.text = "[Choice Text]";
        btnText.fontSize = 28;
        btnText.alignment = TextAlignmentOptions.Center;
        btnText.color = Color.white;

        RectTransform btnTextRect = btnTextObj.GetComponent<RectTransform>();
        btnTextRect.anchorMin = Vector2.zero;
        btnTextRect.anchorMax = Vector2.one;
        btnTextRect.offsetMin = Vector2.zero;
        btnTextRect.offsetMax = Vector2.zero;

        // Hide prefab
        buttonPrefabObj.SetActive(false);

        Debug.Log("✅ Created ChoiceButtonPrefab");

        // ===== STEP 9: Wire DialogueManager serialized fields =====
        dialogueManager.NpcNameText = nameText;
        dialogueManager.BodyText = bodyText;
        dialogueManager.ChoiceButtonContainer = containerObj.transform;
        dialogueManager.ChoiceButtonPrefab = buttonPrefabObj;
        dialogueManager.DialogueCanvasGroup = canvasObj.GetComponent<CanvasGroup>();
        dialogueManager.DialogueCanvas = canvas;

        Debug.Log("✅ Wired DialogueManager serialized fields");

        // ===== STEP 10: Create Player =====
        GameObject playerObj = new GameObject("Player");
        playerObj.tag = "Player";
        playerObj.transform.position = new Vector3(0, 0, 0);

        CharacterController charController = playerObj.AddComponent<CharacterController>();
        charController.height = 2f;
        charController.radius = 0.5f;

        // Add a simple body renderer for visualization
        GameObject bodyMesh = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        bodyMesh.name = "PlayerBody";
        bodyMesh.transform.SetParent(playerObj.transform);
        bodyMesh.transform.localPosition = Vector3.zero;
        bodyMesh.transform.localScale = Vector3.one;
        Collider bodyCollider = bodyMesh.GetComponent<Collider>();
        if (bodyCollider != null)
            Object.DestroyImmediate(bodyCollider);

        Renderer bodyRenderer = bodyMesh.GetComponent<Renderer>();
        Material playerMat = new Material(Shader.Find("Standard"));
        playerMat.color = Color.blue;
        bodyRenderer.material = playerMat;

        Debug.Log("✅ Created Player");

        // ===== STEP 11: Create NPCs =====
        CreateTestNPC("Ravi", new Vector3(3, 0, 5), "ravi_dialogue");
        CreateTestNPC("Nima", new Vector3(-3, 0, 5), "nima_dialogue");

        Debug.Log("✅ Created NPCs");

        // ===== STEP 12: Save Scene =====
        EditorSceneManager.SaveScene(scene, "Assets/Scenes/VelinorNarrativeTest.unity");
        Debug.Log("✅ Scene saved as VelinorNarrativeTest.unity");

        Debug.Log("\n" +
            "═══════════════════════════════════════════════════════════\n" +
            "🎭 VELINOR NARRATIVE TEST SCENE CREATED\n" +
            "═══════════════════════════════════════════════════════════\n" +
            "✅ StatManager (singleton) - Auto-loads npc_state.json\n" +
            "✅ DialogueManager (singleton) - Auto-loads sample_story.json\n" +
            "✅ DialogueCanvas with complete UI hierarchy\n" +
            "✅ Player with CharacterController\n" +
            "✅ 2 Test NPCs (Ravi, Nima) with NPCInteraction\n" +
            "\n" +
            "📋 NEXT STEPS:\n" +
            "1. In Inspector, set each NPC's npcId (e.g., 'Ravi', 'Nima')\n" +
            "2. Set each NPC's startingPassageId (e.g., 'ravi_dialogue')\n" +
            "3. Press Play and press 'E' near an NPC to start dialogue\n" +
            "═══════════════════════════════════════════════════════════");
    }

    static void CreateTestNPC(string npcId, Vector3 position, string startingPassageId)
    {
        GameObject npcObj = new GameObject(npcId);
        npcObj.transform.position = position;

        // Add mesh for visibility
        GameObject meshObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
        meshObj.name = "Mesh";
        meshObj.transform.SetParent(npcObj.transform);
        meshObj.transform.localPosition = Vector3.zero;
        meshObj.transform.localScale = new Vector3(1, 2, 1);

        // Remove physics collider, we'll add our own trigger
        Collider meshCollider = meshObj.GetComponent<Collider>();
        if (meshCollider != null)
            Object.DestroyImmediate(meshCollider);

        // Color the NPC
        Renderer meshRenderer = meshObj.GetComponent<Renderer>();
        Material npcMat = new Material(Shader.Find("Standard"));
        npcMat.color = npcId == "Ravi" ? Color.green : Color.yellow;
        meshRenderer.material = npcMat;

        // Add trigger collider
        SphereCollider triggerCollider = npcObj.AddComponent<SphereCollider>();
        triggerCollider.radius = 2f;
        triggerCollider.isTrigger = true;

        // Add rigid body (kinematic, for trigger detection)
        Rigidbody rb = npcObj.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity = false;

        // Add NPCInteraction script
        NPCInteraction interaction = npcObj.AddComponent<NPCInteraction>();
        // Note: npcId and startingPassageId must be set via Inspector or SerializedProperty

        Debug.Log($"✅ Created NPC: {npcId} at {position}");
    }
}
