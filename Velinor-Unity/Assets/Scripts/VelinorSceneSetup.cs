using UnityEngine;
using UnityEditor;

/// <summary>
/// Velinor character setup helper.
/// Provides one-click context menu to add a complete UMA character to your scene.
/// 
/// Usage:
/// 1. Select any GameObject in your scene
/// 2. Add this script to it (or add to any existing GameObject)
/// 3. Right-click component in Inspector → "Add UMA Character to Scene"
/// 4. Done! UMA character spawns at origin with all components wired up
/// 
/// © 2026 Saoriverse Console. All rights reserved.
/// This code is proprietary and confidential. Unauthorized copying, modification, or distribution
/// is strictly prohibited. See LICENSE_COMMERCIAL.md and NDA_TEMPLATE.md for licensing information.
/// </summary>
public class VelinorSceneSetup : MonoBehaviour
{
    [ContextMenu("Add UMA Character to Scene")]
    public void AddUMACharacterToScene()
    {
        Debug.Log("=== Creating UMA Character ===");

        // Create Player root
        GameObject playerRoot = new GameObject("Player");
        playerRoot.transform.position = new Vector3(0, 0.5f, 0);
        playerRoot.tag = "Player";
        Debug.Log("✓ Created Player GameObject");

        // Add CharacterController
        CharacterController cc = playerRoot.AddComponent<CharacterController>();
        cc.height = 2f;
        cc.radius = 0.4f;
        cc.center = new Vector3(0, 1f, 0);
        Debug.Log("✓ Added CharacterController");

        // Add PlayerCharacterSetup
        PlayerCharacterSetup pcs = playerRoot.AddComponent<PlayerCharacterSetup>();
        Debug.Log("✓ Added PlayerCharacterSetup");

        // Create UMA character child
        GameObject umaObj = new GameObject("UMACharacter");
        umaObj.transform.SetParent(playerRoot.transform);
        umaObj.transform.localPosition = Vector3.zero;
        umaObj.transform.localRotation = Quaternion.identity;
        Debug.Log("✓ Created UMACharacter child GameObject");

        // Link references
        SerializedObject so = new SerializedObject(pcs);
        SerializedProperty umaCharTransform = so.FindProperty("umaCharacterTransform");
        if (umaCharTransform != null)
        {
            umaCharTransform.objectReferenceValue = umaObj.transform;
        }
        so.ApplyModifiedProperties();
        Debug.Log("✓ Linked UMA character reference");

        // Find and link ground plane if it exists
        Collider groundPlane = FindGroundPlane();
        if (groundPlane != null)
        {
            so = new SerializedObject(pcs);
            SerializedProperty groundPlaneCol = so.FindProperty("groundPlaneCollider");
            if (groundPlaneCol != null)
            {
                groundPlaneCol.objectReferenceValue = groundPlane;
            }
            so.ApplyModifiedProperties();
            Debug.Log($"✓ Linked ground plane: {groundPlane.gameObject.name}");
        }
        else
        {
            Debug.LogWarning("⚠ No ground plane found - you'll need to assign it manually in Inspector");
        }

        Debug.Log("\n=== UMA Character Ready! ===");
        Debug.Log("Next steps:");
        Debug.Log("1. Add DynamicCharacterAvatar component to UMACharacter child");
        Debug.Log("2. Configure character in DynamicCharacterAvatar inspector");
        Debug.Log("3. Press Play to test!");
    }

    private Collider FindGroundPlane()
    {
        Collider[] allColliders = FindObjectsByType<Collider>(FindObjectsInactive.Exclude);
        foreach (var col in allColliders)
        {
            string name = col.gameObject.name.ToLower();
            if (name.Contains("ground") || name.Contains("plane") || name.Contains("floor"))
            {
                return col;
            }
        }
        return null;
    }
}
