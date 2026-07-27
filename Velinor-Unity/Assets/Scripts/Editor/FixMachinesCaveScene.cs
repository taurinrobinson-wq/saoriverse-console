using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

/// <summary>
/// FixMachinesCaveScene - Comprehensive repair for MachinesCave playability issues.
/// Usage: Go to Velinor > Fix MachinesCave Scene in the menu.
/// </summary>
public class FixMachinesCaveScene
{
    [MenuItem("Velinor/Fix MachinesCave Scene")]
    public static void FixScene()
    {
        Debug.Log("=== Fixing MachinesCave Scene ===\n");

        // 1. Remove stale scene objects with missing scripts
        RemoveStaleObjects();

        // 2. Clean up missing scripts
        CleanupMissingScripts();

        // 3. Fix ground
        FixGround();

        // 4. Fix player
        FixPlayer();

        // Mark scene as dirty so changes are saved
        Scene scene = UnityEditor.SceneManagement.EditorSceneManager.GetActiveScene();
        UnityEditor.SceneManagement.EditorSceneManager.MarkSceneDirty(scene);

        Debug.Log("\n✅ MachinesCave scene repair complete!");
        Debug.Log("Try pressing Play now. The player should spawn on the ground and be controllable.");
    }

    private static void RemoveStaleObjects()
    {
        Debug.Log("Step 1: Removing stale scene objects...");
        string[] staleNames = { "PlayerFollowCamera", "cm", "CinemachineCamera", "VirtualCamera" };
        int removed = 0;

        foreach (string name in staleNames)
        {
            GameObject obj = GameObject.Find(name);
            if (obj != null)
            {
                Debug.LogWarning($"  Removing stale object: {obj.name}");
                Object.DestroyImmediate(obj);
                removed++;
            }
        }

        if (removed > 0)
        {
            Debug.Log($"  ✓ Removed {removed} stale objects");
        }
    }

    private static void CleanupMissingScripts()
    {
        Debug.Log("Step 2: Removing missing script components...");
        Scene scene = UnityEditor.SceneManagement.EditorSceneManager.GetActiveScene();
        GameObject[] allGameObjects = scene.GetRootGameObjects();

        int count = 0;
        foreach (GameObject root in allGameObjects)
        {
            count += RemoveMissingScriptsRecursive(root);
        }

        if (count > 0)
        {
            Debug.Log($"  ✓ Removed {count} missing script components");
        }
    }

    private static int RemoveMissingScriptsRecursive(GameObject gameObject)
    {
        int removed = 0;
        Component[] components = gameObject.GetComponents<Component>();

        foreach (Component component in components)
        {
            if (component == null)
            {
                Object.DestroyImmediate(component, true);
                removed++;
            }
        }

        foreach (Transform child in gameObject.transform)
        {
            removed += RemoveMissingScriptsRecursive(child.gameObject);
        }

        return removed;
    }

    private static void FixGround()
    {
        Debug.Log("Step 3: Setting up ground collider...");
        GameObject ground = GameObject.Find("GroundPlane");
        if (ground == null)
        {
            ground = GameObject.Find("Ground");
        }

        if (ground == null)
        {
            Debug.LogWarning("  ⚠ Could not find ground plane in scene (looked for 'GroundPlane' or 'Ground')");
            return;
        }

        BoxCollider collider = ground.GetComponent<BoxCollider>();
        if (collider == null)
        {
            collider = ground.AddComponent<BoxCollider>();
        }

        collider.isTrigger = false;
        collider.size = new Vector3(20, 0.1f, 20);
        collider.center = new Vector3(0, -0.05f, 0);

        // Remove any Rigidbody from ground (it shouldn't have one)
        Rigidbody rbGround = ground.GetComponent<Rigidbody>();
        if (rbGround != null)
        {
            Object.DestroyImmediate(rbGround);
        }

        Debug.Log("  ✓ Ground plane collider configured");
    }

    private static void FixPlayer()
    {
        Debug.Log("Step 4: Setting up player character controller...");
        GameObject player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogError("  ❌ Cannot find Player GameObject in scene!");
            return;
        }

        // Remove any existing Rigidbody (CharacterController handles physics)
        Rigidbody rbPlayer = player.GetComponent<Rigidbody>();
        if (rbPlayer != null)
        {
            Object.DestroyImmediate(rbPlayer);
        }

        // Ensure CharacterController exists
        CharacterController charController = player.GetComponent<CharacterController>();
        if (charController == null)
        {
            charController = player.AddComponent<CharacterController>();
        }

        charController.height = 1.8f;
        charController.radius = 0.3f;
        charController.center = new Vector3(0, 0.9f, 0);
        charController.slopeLimit = 45f;
        charController.stepOffset = 0.3f;

        // Ensure input component exists
        StarterAssets.VelinorStarterAssetsInputs input = player.GetComponent<StarterAssets.VelinorStarterAssetsInputs>();
        if (input == null)
        {
            input = player.AddComponent<StarterAssets.VelinorStarterAssetsInputs>();
        }

        // Ensure ThirdPersonController exists
        StarterAssets.ThirdPersonController tpc = player.GetComponent<StarterAssets.ThirdPersonController>();
        if (tpc == null)
        {
            tpc = player.AddComponent<StarterAssets.ThirdPersonController>();
        }

        tpc.MoveSpeed = 3f;
        tpc.SprintSpeed = 5.5f;
        tpc.GroundLayers = LayerMask.GetMask("Default");

        // Ensure camera target exists
        Transform camTarget = player.transform.Find("CinemachineCameraTarget");
        if (camTarget == null)
        {
            GameObject camTargetObj = new GameObject("CinemachineCameraTarget");
            camTargetObj.transform.SetParent(player.transform);
            camTargetObj.transform.localPosition = new Vector3(0, 0.6f, 0);
            camTargetObj.transform.localRotation = Quaternion.identity;
            camTarget = camTargetObj.transform;
        }

        if (tpc.CinemachineCameraTarget == null || tpc.CinemachineCameraTarget.GetComponent<Transform>() == null)
        {
            tpc.CinemachineCameraTarget = camTarget.gameObject;
        }

        // Ensure main camera exists
        GameObject mainCam = GameObject.FindGameObjectWithTag("MainCamera");
        if (mainCam == null)
        {
            mainCam = new GameObject("Main Camera");
            mainCam.tag = "MainCamera";
            mainCam.transform.SetParent(player.transform);
            mainCam.transform.localPosition = new Vector3(0, 0.6f, 0);
            mainCam.AddComponent<Camera>();
            mainCam.AddComponent<AudioListener>();
        }

        // Remove any "Basic Rigid Body Push" or other stale components
        Component[] allComponents = player.GetComponents<Component>();
        foreach (Component comp in allComponents)
        {
            if (comp == null || comp.GetType().Name.Contains("Unknown") || comp.GetType().Name == "BasicRigidBodyPush")
            {
                if (comp != null)
                {
                    Object.DestroyImmediate(comp);
                }
            }
        }

        Debug.Log("  ✓ Player character controller configured");
        Debug.Log($"  ✓ Player position: {player.transform.position}");
    }
}
