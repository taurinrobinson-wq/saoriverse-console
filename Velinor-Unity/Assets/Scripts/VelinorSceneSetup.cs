using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;
using System.Linq;
using System;
using System.Reflection;

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

        // Ensure UMA infrastructure exists first
        EnsureUMAInfrastructure();

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

        // Find and link ground plane, or create one if it doesn't exist
        Collider groundPlane = FindGroundPlane();
        if (groundPlane == null)
        {
            // Create ground plane
            GameObject groundObj = new GameObject("GroundPlane");
            groundObj.transform.position = Vector3.zero;

            // Add collider
            BoxCollider bc = groundObj.AddComponent<BoxCollider>();
            bc.size = new Vector3(20, 0.1f, 20);

            // Add invisible renderer to avoid visual clutter
            MeshFilter mf = groundObj.AddComponent<MeshFilter>();
            mf.mesh = Resources.GetBuiltinResource<Mesh>("Plane.fbx");

            MeshRenderer mr = groundObj.AddComponent<MeshRenderer>();
            mr.enabled = false;  // Invisible

            groundPlane = bc;
            Debug.Log("✓ Created new ground plane (invisible)");
        }

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

        Debug.Log("\n=== UMA Character Ready! ===");
        Debug.Log("Next steps:");
        Debug.Log("1. Add DynamicCharacterAvatar component to UMACharacter child");
        Debug.Log("2. Customize in DynamicCharacterAvatar inspector");
        Debug.Log("3. Press Play - character should appear and be controllable!");
    }

    private void EnsureUMAInfrastructure()
    {
        // Check if UMAGenerator exists by name
        Transform existingGen = null;
        foreach (Transform root in SceneManager.GetActiveScene().GetRootGameObjects().Select(g => g.transform))
        {
            if (root.gameObject.name == "UMAGenerator")
            {
                existingGen = root;
                break;
            }
        }

        if (existingGen != null)
        {
            Debug.Log("✓ UMAGenerator already exists");
        }
        else
        {
            // Create UMA Generator GameObject
            GameObject umaGenObj = new GameObject("UMAGenerator");
            umaGenObj.transform.position = Vector3.zero;

            // Add UMAGenerator component by type name - search all assemblies
            System.Type umaGenType = GetTypeFromAllAssemblies("UMA.CharacterSystem.UMAGenerator");
            if (umaGenType != null)
            {
                umaGenObj.AddComponent(umaGenType);
                Debug.Log("✓ Created UMAGenerator");
            }
            else
            {
                Debug.LogWarning("⚠ Could not find UMAGenerator type - UMA may not be properly imported");
            }
        }

        // Check if UMAContext exists by name
        Transform existingContext = null;
        foreach (Transform root in SceneManager.GetActiveScene().GetRootGameObjects().Select(g => g.transform))
        {
            if (root.gameObject.name == "UMAContext")
            {
                existingContext = root;
                break;
            }
        }

        if (existingContext != null)
        {
            Debug.Log("✓ UMAContext already exists");
        }
        else
        {
            // Create UMA Context GameObject
            GameObject contextObj = new GameObject("UMAContext");
            contextObj.transform.position = Vector3.zero;

            // Add UMAContext component by type name - search all assemblies
            System.Type umaContextType = GetTypeFromAllAssemblies("UMA.CharacterSystem.UMAContext");
            if (umaContextType != null)
            {
                contextObj.AddComponent(umaContextType);
                Debug.Log("✓ Created UMAContext");
            }
            else
            {
                Debug.LogWarning("⚠ Could not find UMAContext type - UMA may not be properly imported");
            }
        }
    }

    private System.Type GetTypeFromAllAssemblies(string typeName)
    {
        foreach (System.Reflection.Assembly assembly in System.AppDomain.CurrentDomain.GetAssemblies())
        {
            System.Type type = assembly.GetType(typeName, false);
            if (type != null)
                return type;
        }
        return null;
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

// Need to add using for SceneManager

