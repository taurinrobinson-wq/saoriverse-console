using UnityEditor;
using UnityEngine;

public class AddSimpleMovement
{
    [MenuItem("Velinor/Add Simple Movement")]
    public static void Setup()
    {
        GameObject player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogError("❌ Player object not found");
            return;
        }

        // Add simple movement script
        if (player.GetComponent<SimplePlayerMovement>() == null)
        {
            player.AddComponent<SimplePlayerMovement>();
            Debug.Log("✅ Added SimplePlayerMovement to Player");
        }

        // Ensure CharacterController exists
        if (player.GetComponent<CharacterController>() == null)
        {
            CharacterController cc = player.AddComponent<CharacterController>();
            cc.height = 2f;
            cc.radius = 0.5f;
            Debug.Log("✅ Added CharacterController");
        }

        Debug.Log("Ready to play!");
        Debug.Log("Controls:");
        Debug.Log("  WASD = Move");
        Debug.Log("  SPACE = Jump");
        Debug.Log("  MOUSE = Look around");
    }
}
