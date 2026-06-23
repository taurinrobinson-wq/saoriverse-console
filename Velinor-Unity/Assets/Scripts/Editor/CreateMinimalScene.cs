using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;

public class CreateMinimalScene
{
    [MenuItem("Velinor/Create Minimal Test Scene")]
    public static void Create()
    {
        // Create new scene
        Scene scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);

        // Delete default camera
        GameObject defaultCam = GameObject.Find("Main Camera");
        if (defaultCam != null) Object.DestroyImmediate(defaultCam);

        // Ensure EventSystem exists (for UI click detection)
        if (GameObject.Find("EventSystem") == null)
        {
            GameObject eventSystemGO = new GameObject("EventSystem");
            eventSystemGO.AddComponent<EventSystem>();
            eventSystemGO.AddComponent<StandaloneInputModule>();
        }

        // ===== CREATE GROUND =====
        GameObject ground = new GameObject("Ground");
        ground.transform.position = new Vector3(0, 0, 0);
        
        BoxCollider groundCol = ground.AddComponent<BoxCollider>();
        groundCol.size = new Vector3(20, 2, 20);  // Simple: 20x20 platform, 2 tall
        
        Rigidbody groundRb = ground.AddComponent<Rigidbody>();
        groundRb.isKinematic = true;
        groundRb.useGravity = false;
        
        // Visual: gray cube, no scaling tricks
        GameObject groundVis = GameObject.CreatePrimitive(PrimitiveType.Cube);
        groundVis.name = "Visual";
        groundVis.transform.SetParent(ground.transform);
        groundVis.transform.localPosition = Vector3.zero;
        groundVis.transform.localScale = new Vector3(20, 2, 20);
        Object.DestroyImmediate(groundVis.GetComponent<Collider>());
        Material groundMat = new Material(Shader.Find("Standard"));
        groundMat.color = new Color(0.5f, 0.5f, 0.5f, 1f);
        groundVis.GetComponent<MeshRenderer>().material = groundMat;

        // ===== CREATE PLAYER =====
        GameObject player = new GameObject("Player");
        player.transform.position = new Vector3(0, 1, 0);  // Bottom at y=0 (ground top), top at y=2
        player.tag = "Player";
        
        CharacterController cc = player.AddComponent<CharacterController>();
        cc.height = 2f;
        cc.radius = 0.5f;
        cc.center = new Vector3(0, 1, 0);  // Offset so CC extends from y=0 to y=2
        
        // Trigger collider for interaction detection (separate from CharacterController)
        CapsuleCollider triggerCollider = player.AddComponent<CapsuleCollider>();
        triggerCollider.radius = 0.6f;
        triggerCollider.height = 2f;
        triggerCollider.center = new Vector3(0, 1, 0);
        triggerCollider.isTrigger = true;
        
        // Visual: blue cylinder (2 units tall, 1 unit diameter)
        GameObject playerVis = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        playerVis.name = "Visual";
        playerVis.transform.SetParent(player.transform);
        playerVis.transform.localPosition = new Vector3(0, 1, 0);  // Align with CC
        playerVis.transform.localScale = new Vector3(1f, 1f, 1f);  // Natural size
        Object.DestroyImmediate(playerVis.GetComponent<Collider>());
        Material playerMat = new Material(Shader.Find("Standard"));
        playerMat.color = new Color(0.2f, 0.5f, 0.9f, 1f);
        playerVis.GetComponent<MeshRenderer>().material = playerMat;
        
        // Movement script
        player.AddComponent<SimplePlayerMovement>();

        // ===== CREATE CAMERA =====
        GameObject camObj = new GameObject("Main Camera");
        Camera cam = camObj.AddComponent<Camera>();
        cam.tag = "MainCamera";
        cam.backgroundColor = new Color(0.3f, 0.5f, 0.7f, 1f);
        camObj.AddComponent<AudioListener>();
        camObj.transform.SetParent(player.transform);
        camObj.transform.localPosition = new Vector3(0, 1.2f, -2.5f);

        // ===== CREATE LIGHT =====
        GameObject lightObj = new GameObject("DirectionalLight");
        Light light = lightObj.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.2f;
        lightObj.transform.rotation = Quaternion.Euler(50, -30, 0);

        // ===== CREATE INTERACTIVE GLYPH =====
        GameObject glyph = new GameObject("Glyph_TestObject");
        glyph.transform.position = new Vector3(5, 1.466f, 0);  // Aligned with player center height
        
        // Visual: cyan sphere (0.67 scale = 1/3 of player height)
        GameObject glyphVis = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        glyphVis.name = "Visual";
        glyphVis.transform.SetParent(glyph.transform);
        glyphVis.transform.localPosition = Vector3.zero;
        glyphVis.transform.localScale = new Vector3(0.67f, 0.67f, 0.67f);
        Object.DestroyImmediate(glyphVis.GetComponent<Collider>());
        Material glyphMat = new Material(Shader.Find("Standard"));
        glyphMat.color = new Color(0, 1, 1, 1);  // Cyan
        glyphVis.GetComponent<MeshRenderer>().material = glyphMat;
        
        // Trigger collider for interaction detection
        SphereCollider glyphCollider = glyph.AddComponent<SphereCollider>();
        glyphCollider.radius = 1f;  // Extends beyond visual
        glyphCollider.isTrigger = true;
        
        // Add interaction script
        glyph.AddComponent<GlyphObject>();

        // ===== CREATE INTERACTION UI =====
        GameObject canvasGO = new GameObject("InteractionCanvas");
        Canvas canvas = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        
        CanvasScaler scaler = canvasGO.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        
        GraphicRaycaster raycaster = canvasGO.AddComponent<GraphicRaycaster>();
        
        InteractionUI interactionUI = canvasGO.AddComponent<InteractionUI>();

        // ===== CREATE NPC WITH DIALOGUE =====
        GameObject npc = new GameObject("NPC_MaleVillager");
        npc.transform.position = new Vector3(-5, 1.97f, 0);  // Fixed height to spawn above ground

        // Visual: purple capsule
        GameObject npcVis = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        npcVis.name = "Visual";
        npcVis.transform.SetParent(npc.transform);
        npcVis.transform.localPosition = Vector3.zero;
        npcVis.transform.localScale = new Vector3(1f, 1f, 1f);
        Object.DestroyImmediate(npcVis.GetComponent<Collider>());
        Material npcMat = new Material(Shader.Find("Standard"));
        npcMat.color = new Color(0.8f, 0.2f, 0.8f, 1f);
        npcVis.GetComponent<MeshRenderer>().material = npcMat;

        // SOLID collider for physics blocking (prevents player walking through)
        CapsuleCollider npcSolidCollider = npc.AddComponent<CapsuleCollider>();
        npcSolidCollider.radius = 0.5f;
        npcSolidCollider.height = 2f;
        npcSolidCollider.isTrigger = false;  // SOLID - blocks player

        // TRIGGER collider for wider interaction detection (larger radius)
        CapsuleCollider npcTriggerCollider = npc.AddComponent<CapsuleCollider>();
        npcTriggerCollider.radius = 0.8f;
        npcTriggerCollider.height = 2.5f;
        npcTriggerCollider.isTrigger = true;  // TRIGGER - for OnTriggerStay detection

        // Rigidbody for physics collision
        Rigidbody npcRb = npc.AddComponent<Rigidbody>();
        npcRb.isKinematic = true;
        npcRb.useGravity = false;

        // Create dialogue canvas (bottom-anchored, Screen Space Overlay)
        GameObject dialogueCanvasGO = new GameObject("DialogueCanvas");
        Canvas dialogueCanvas = dialogueCanvasGO.AddComponent<Canvas>();
        dialogueCanvas.renderMode = RenderMode.ScreenSpaceOverlay;
        dialogueCanvasGO.AddComponent<CanvasScaler>();
        dialogueCanvasGO.AddComponent<GraphicRaycaster>();

        // Dialogue panel at CENTER of screen (easier to see and interact with)
        GameObject panelGO = new GameObject("DialoguePanel");
        panelGO.transform.SetParent(dialogueCanvasGO.transform);
        RectTransform panelRect = panelGO.AddComponent<RectTransform>();
        panelRect.anchorMin = new Vector2(0.5f, 0.5f);
        panelRect.anchorMax = new Vector2(0.5f, 0.5f);
        panelRect.anchoredPosition = new Vector2(0, -150);  // Below center
        panelRect.sizeDelta = new Vector2(700, 200);  // Larger for better visibility
        Image panelImage = panelGO.AddComponent<Image>();
        panelImage.color = new Color(0.1f, 0.1f, 0.15f, 0.95f);

        // Dialogue text
        GameObject textGO = new GameObject("DialogueText");
        textGO.transform.SetParent(panelGO.transform);
        RectTransform textRect = textGO.AddComponent<RectTransform>();
        textRect.anchorMin = Vector2.zero;
        textRect.anchorMax = Vector2.one;
        textRect.offsetMin = new Vector2(10, 50);
        textRect.offsetMax = new Vector2(-10, -10);
        TextMeshProUGUI dialogueText = textGO.AddComponent<TextMeshProUGUI>();
        dialogueText.text = "";
        dialogueText.fontSize = 32;
        dialogueText.alignment = TextAlignmentOptions.TopLeft;
        dialogueText.color = Color.white;

        // Option button 1 (left side, bottom of panel)
        GameObject btn1GO = new GameObject("OptionButton1");
        btn1GO.transform.SetParent(panelGO.transform);
        RectTransform btn1Rect = btn1GO.AddComponent<RectTransform>();
        btn1Rect.anchorMin = new Vector2(0, 0);
        btn1Rect.anchorMax = new Vector2(0.5f, 0);
        btn1Rect.offsetMin = new Vector2(20, 20);
        btn1Rect.offsetMax = new Vector2(-10, 70);
        Image btn1Image = btn1GO.AddComponent<Image>();
        btn1Image.color = new Color(0.2f, 0.6f, 0.2f, 1f);
        Button btn1Button = btn1GO.AddComponent<Button>();
        btn1Button.targetGraphic = btn1Image;
        btn1Button.interactable = true;
        // Set navigation to None so button responds to clicks properly
        Navigation nav1 = new Navigation();
        nav1.mode = Navigation.Mode.None;
        btn1Button.navigation = nav1;
        GameObject btn1TextGO = new GameObject("Text");
        btn1TextGO.transform.SetParent(btn1GO.transform);
        RectTransform btn1TextRect = btn1TextGO.AddComponent<RectTransform>();
        btn1TextRect.anchorMin = Vector2.zero;
        btn1TextRect.anchorMax = Vector2.one;
        btn1TextRect.offsetMin = Vector2.zero;
        btn1TextRect.offsetMax = Vector2.zero;
        TextMeshProUGUI btn1Text = btn1TextGO.AddComponent<TextMeshProUGUI>();
        btn1Text.text = "Option 1";
        btn1Text.fontSize = 28;
        btn1Text.alignment = TextAlignmentOptions.Center;
        btn1Text.color = Color.white;

        // Option button 2 (right side, bottom of panel)
        GameObject btn2GO = new GameObject("OptionButton2");
        btn2GO.transform.SetParent(panelGO.transform);
        RectTransform btn2Rect = btn2GO.AddComponent<RectTransform>();
        btn2Rect.anchorMin = new Vector2(0.5f, 0);
        btn2Rect.anchorMax = new Vector2(1f, 0);
        btn2Rect.offsetMin = new Vector2(10, 20);
        btn2Rect.offsetMax = new Vector2(-20, 70);
        Image btn2Image = btn2GO.AddComponent<Image>();
        btn2Image.color = new Color(0.6f, 0.2f, 0.2f, 1f);
        Button btn2Button = btn2GO.AddComponent<Button>();
        btn2Button.targetGraphic = btn2Image;
        btn2Button.interactable = true;
        // Set navigation to None so button responds to clicks properly
        Navigation nav2 = new Navigation();
        nav2.mode = Navigation.Mode.None;
        btn2Button.navigation = nav2;
        GameObject btn2TextGO = new GameObject("Text");
        btn2TextGO.transform.SetParent(btn2GO.transform);
        RectTransform btn2TextRect = btn2TextGO.AddComponent<RectTransform>();
        btn2TextRect.anchorMin = Vector2.zero;
        btn2TextRect.anchorMax = Vector2.one;
        btn2TextRect.offsetMin = Vector2.zero;
        btn2TextRect.offsetMax = Vector2.zero;
        TextMeshProUGUI btn2Text = btn2TextGO.AddComponent<TextMeshProUGUI>();
        btn2Text.text = "Option 2";
        btn2Text.fontSize = 28;
        btn2Text.alignment = TextAlignmentOptions.Center;
        btn2Text.color = Color.white;

        // Add NPC interaction script
        NPCInteraction npcInteraction = npc.AddComponent<NPCInteraction>();
        npcInteraction.npcName = "Ravi";
        npcInteraction.dialogueCanvas = dialogueCanvas;
        npcInteraction.dialogueText = dialogueText;
        npcInteraction.optionButton1 = btn1GO;
        npcInteraction.optionButton2 = btn2GO;

        // Hide dialogue UI initially (will show via InteractionUI when in range)
        panelGO.SetActive(false);

        EditorSceneManager.SaveScene(scene, "Assets/Scenes/GamplayScene.unity");
        Debug.Log("✅ Scene created - Simple 20x20 platform");
        Debug.Log("🎮 Press Space to jump!");
        Debug.Log("✨ Cyan glyph at (5, 1.466, 0) - press E to interact!");
        Debug.Log("🟣 Purple NPC at (-5, 1.97, 0) - press E to talk!");
    }
}
