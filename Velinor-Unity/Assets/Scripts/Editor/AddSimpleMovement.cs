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

        // Ensure CharacterController exists
        if (player.GetComponent<CharacterController>() == null)
        {
            CharacterController cc = player.AddComponent<CharacterController>();
            cc.height = 2f;
            cc.radius = 0.5f;
            Debug.Log("✅ Added CharacterController");
        }

        // Find Main Camera and make it a child of Player
        GameObject cameraObj = GameObject.Find("Main Camera");
        if (cameraObj != null)
        {
            cameraObj.transform.SetParent(player.transform);
            cameraObj.transform.localPosition = new Vector3(0, 0.6f, 0);
            cameraObj.transform.localRotation = Quaternion.identity;
            Debug.Log("✅ Made Camera child of Player");
        }

        // Add simple movement script
        if (player.GetComponent<SimplePlayerMovement>() == null)
        {
            player.AddComponent<SimplePlayerMovement>();
            Debug.Log("✅ Added SimplePlayerMovement to Player");
        }

        Debug.Log("Ready to play!");
        Debug.Log("Controls:");
        Debug.Log("  WASD = Move");
        Debug.Log("  SPACE = Jump");
        Debug.Log("  MOUSE = Free look (full 360)");
    }
}
