using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public class NPCSetup : EditorWindow
{
    [MenuItem("Tools/Setup NPC - Add Mesh and Collider")]
    public static void SetupNPC()
    {
        Scene activeScene = EditorSceneManager.GetActiveScene();
        
        // Find all NPCs
        var allGameObjects = FindObjectsByType<GameObject>();
        int setupCount = 0;

        foreach (GameObject go in allGameObjects)
        {
            // Look for NPCs (containing "NPC" in name or matching specific names)
            if (go.name.Contains("NPC") || go.name == "SaoriNPC" || go.name.Contains("Character"))
            {
                if (SetupNPCGameObject(go))
                {
                    setupCount++;
                }
            }
        }

        if (setupCount > 0)
        {
            EditorSceneManager.MarkSceneDirty(activeScene);
            EditorUtility.DisplayDialog("Success", $"NPC setup complete!\n\nSet up {setupCount} NPC(s) with mesh and collider.", "OK");
            Debug.Log($"✅ NPC setup complete! ({setupCount} NPCs configured)");
        }
        else
        {
            EditorUtility.DisplayDialog("No NPCs Found", "Could not find any NPCs to set up.", "OK");
        }
    }

    private static bool SetupNPCGameObject(GameObject npc)
    {
        bool changed = false;

        // Add CapsuleCollider if missing
        if (npc.GetComponent<CapsuleCollider>() == null)
        {
            CapsuleCollider capsule = npc.AddComponent<CapsuleCollider>();
            capsule.height = 2f;
            capsule.radius = 0.5f;
            EditorUtility.SetDirty(npc);
            changed = true;
            Debug.Log($"✓ Added CapsuleCollider to {npc.name}");
        }

        // Add mesh and renderer if missing
        if (npc.GetComponent<MeshFilter>() == null)
        {
            MeshFilter meshFilter = npc.AddComponent<MeshFilter>();
            
            // Create a temporary capsule primitive to get its mesh
            GameObject tempCapsule = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            Mesh capsuleMesh = tempCapsule.GetComponent<MeshFilter>().mesh;
            meshFilter.mesh = capsuleMesh;
            
            // Destroy the collider from the temp capsule (we have our own)
            DestroyImmediate(tempCapsule.GetComponent<Collider>());
            DestroyImmediate(tempCapsule);
            
            EditorUtility.SetDirty(npc);
            changed = true;
            Debug.Log($"✓ Added MeshFilter with capsule mesh to {npc.name}");
        }

        if (npc.GetComponent<MeshRenderer>() == null)
        {
            MeshRenderer renderer = npc.AddComponent<MeshRenderer>();
            
            // Create a simple material
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = new Color(0.8f, 0.6f, 0.8f, 1f);  // Light purple/mauve for NPCs
            
            renderer.material = mat;
            EditorUtility.SetDirty(npc);
            changed = true;
            Debug.Log($"✓ Added MeshRenderer to {npc.name}");
        }

        return changed;
    }
}
