# Scene Setup Reference - WORKING TEMPLATE

This document defines the canonical scaling and positioning patterns for all test scenes. Use this as the reference when creating new scenes to avoid physics/collision issues.

## Ground Physics (CANONICAL)

```csharp
static void CreateGround()
{
    GameObject groundObj = new GameObject("Ground");
    groundObj.transform.position = new Vector3(0, 0, 0);

    // Create ground mesh (20×20)
    MeshFilter mf = groundObj.AddComponent<MeshFilter>();
    MeshRenderer mr = groundObj.AddComponent<MeshRenderer>();
    
    Mesh groundMesh = new Mesh();
    groundMesh.vertices = new Vector3[]
    {
        new Vector3(-10, 0, -10),
        new Vector3(10, 0, -10),
        new Vector3(10, 0, 10),
        new Vector3(-10, 0, 10)
    };
    groundMesh.triangles = new int[] { 0, 2, 1, 0, 3, 2 };
    groundMesh.RecalculateNormals();
    mf.mesh = groundMesh;

    Material groundMat = new Material(Shader.Find("Standard"));
    groundMat.color = new Color(0.6f, 0.5f, 0.4f, 1f);
    mr.material = groundMat;

    // Collider positioned slightly above ground
    BoxCollider groundCollider = groundObj.AddComponent<BoxCollider>();
    groundCollider.size = new Vector3(20, 0.01f, 20);
    groundCollider.center = new Vector3(0, -0.005f, 0);

    Rigidbody groundRb = groundObj.AddComponent<Rigidbody>();
    groundRb.isKinematic = true;
    groundRb.useGravity = false;
}
```

## Player Setup (CANONICAL)

**KEY RULE: Root at scale (1,1,1), visual child scaled to (0.66, 0.66, 0.66)**

```csharp
static void CreatePlayer()
{
    GameObject playerObj = new GameObject("Player");
    playerObj.tag = "Player";
    playerObj.transform.position = new Vector3(0, 0.66f, 0f);  // y=0.66 puts feet on ground
    playerObj.transform.localScale = Vector3.one;              // NEVER scale root

    // CharacterController on root with UNSCALED dimensions
    CharacterController charController = playerObj.AddComponent<CharacterController>();
    charController.height = 1.8f;      // Unscaled
    charController.radius = 0.3f;      // Unscaled
    charController.center = new Vector3(0, 0.33f, 0);

    playerObj.AddComponent<SimplePlayerController>();
    playerObj.AddComponent<PlayerStats>();
    
    // VISUAL ONLY - scaled child (does NOT affect physics)
    GameObject visualObj = GameObject.CreatePrimitive(PrimitiveType.Capsule);
    visualObj.name = "Visual";
    visualObj.transform.SetParent(playerObj.transform);
    visualObj.transform.localPosition = Vector3.zero;
    visualObj.transform.localScale = new Vector3(0.66f, 0.66f, 0.66f);  // ONLY scale visual

    Object.DestroyImmediate(visualObj.GetComponent<Collider>());
    Material playerMat = new Material(Shader.Find("Standard"));
    playerMat.color = Color.blue;
    visualObj.GetComponent<MeshRenderer>().material = playerMat;

    Rigidbody rb = playerObj.AddComponent<Rigidbody>();
    rb.isKinematic = true;
    rb.useGravity = false;

    // Camera
    GameObject cameraObj = new GameObject("MainCamera");
    cameraObj.tag = "MainCamera";
    cameraObj.transform.SetParent(playerObj.transform);
    cameraObj.transform.localPosition = new Vector3(0, 1.03f, -1.65f);
    Camera cam = cameraObj.AddComponent<Camera>();
    cam.clearFlags = CameraClearFlags.Skybox;
}
```

## NPC Setup (CANONICAL)

**KEY RULE: Root at scale (1,1,1), visual child scaled, TWO SEPARATE COLLIDERS**

```csharp
static void CreateNPC(string npcName, Vector3 position, Color color)
{
    GameObject npcObj = new GameObject($"NPC_{npcName}");
    npcObj.transform.position = position;          // e.g., (0, 0.66f, 5f)
    npcObj.transform.localScale = Vector3.one;    // NEVER scale root

    // VISUAL ONLY - scaled child
    GameObject visualObj = GameObject.CreatePrimitive(PrimitiveType.Capsule);
    visualObj.name = "Visual";
    visualObj.transform.SetParent(npcObj.transform);
    visualObj.transform.localPosition = Vector3.zero;
    visualObj.transform.localScale = new Vector3(0.66f, 0.66f, 0.66f);

    Object.DestroyImmediate(visualObj.GetComponent<Collider>());
    Material mat = new Material(Shader.Find("Standard"));
    mat.color = color;
    visualObj.GetComponent<MeshRenderer>().material = mat;

    // COLLIDER 1: Solid collider on root (blocks movement)
    CapsuleCollider solidCollider = npcObj.AddComponent<CapsuleCollider>();
    solidCollider.isTrigger = false;  // NOT a trigger - blocks movement
    solidCollider.radius = 0.3f;      // Unscaled
    solidCollider.height = 1.8f;      // Unscaled
    solidCollider.center = new Vector3(0, 0.33f, 0);

    // COLLIDER 2: Trigger collider (detects E key interaction)
    GameObject triggerObj = new GameObject("InteractionTrigger");
    triggerObj.transform.SetParent(npcObj.transform);
    triggerObj.transform.localPosition = Vector3.zero;

    CapsuleCollider triggerCollider = triggerObj.AddComponent<CapsuleCollider>();
    triggerCollider.isTrigger = true;  // THIS IS a trigger - just for detection
    triggerCollider.radius = 0.3f;     // Match solid collider
    triggerCollider.height = 1.8f;     // Match solid collider
    triggerCollider.center = new Vector3(0, 0.33f, 0);

    Rigidbody rb = npcObj.AddComponent<Rigidbody>();
    rb.isKinematic = true;
    rb.useGravity = false;

    // Attach interaction system
    NPCInteraction npcInteraction = npcObj.AddComponent<NPCInteraction>();
    npcInteraction.GetType().GetField("npcId", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(npcInteraction, npcName);

    // Attach dialogue sequences and evaluators as needed
    // (depends on npc type - Ravi vs Malrik vs Elenya, etc)
}
```

## Positioning Guide

| Role | Position | Purpose |
|------|----------|---------|
| Player | (0, 0.66, 0) | Center, can move in all directions |
| NPC 1 | (0, 0.66, 5) | Behind player (relative to camera look) |
| NPC 2 | (0, 0.66, -5) | Ahead of player (relative to camera look) |
| NPC 3 | (5, 0.66, 0) | Right side |
| NPC 4 | (-5, 0.66, 0) | Left side |

## Critical Physics Rules

1. **Never scale root GameObject** - Always use y=0.66f positioning
2. **Scale only visual children** - Physics colliders must use unscaled dimensions
3. **Use two colliders per NPC**: One solid (blocks movement), one trigger (detects interaction)
4. **Ground collider height = 0.01** with center offset -0.005 to prevent z-fighting
5. **CharacterController dimensions**: height=1.8, radius=0.3, center=(0, 0.33, 0)

## Testing Checklist

- [ ] Player stands on ground (not sinking)
- [ ] Can walk with WASD without falling
- [ ] Can look around with mouse
- [ ] NPCs stand on ground
- [ ] Press E near NPC triggers dialogue box
- [ ] Dialogue box shows NPC name and text
- [ ] Can select choices with T/O/N/E keys
