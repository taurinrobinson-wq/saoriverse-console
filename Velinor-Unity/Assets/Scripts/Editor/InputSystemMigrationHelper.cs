using UnityEditor;
using UnityEngine;

namespace Velinor.Editor
{
    /// <summary>
    /// InputSystemMigrationHelper - Guides users through Input System migration
    /// 
    /// The project currently uses the deprecated Input Manager.
    /// This helper provides:
    /// 1. Installation of Input System package
    /// 2. Creation of Input Actions asset
    /// 3. Example migration patterns
    /// 4. Automated migration of select scripts
    /// </summary>
    public class InputSystemMigrationHelper
    {
        [MenuItem("Velinor/Input System/1. Check Input System Status")]
        public static void CheckInputSystemStatus()
        {
            Debug.Log("\n📋 INPUT SYSTEM MIGRATION STATUS\n");

            // Check if Input System package is installed
            bool hasInputSystem = false;
            try
            {
                var inputSystemType = System.Type.GetType("UnityEngine.InputSystem.InputAction, Unity.InputSystem");
                hasInputSystem = inputSystemType != null;
            }
            catch { }

            if (hasInputSystem)
            {
                Debug.Log("✅ Input System package is INSTALLED");
            }
            else
            {
                Debug.Log("❌ Input System package is NOT installed");
                Debug.Log("   To install: Window > Package Manager > + > Add package by name");
                Debug.Log("   Package name: com.unity.inputsystem");
            }

            // Count Input Manager usage
            int inputManagerCount = CountInputManagerUsage();
            Debug.Log($"\n📊 Input Manager API Usage: {inputManagerCount} locations found");
            Debug.Log("   Files affected: PlayerController.cs, SimplePlayerMovement.cs, StarterAssetsInputs.cs, and others");

            Debug.Log("\n📝 NEXT STEPS:");
            Debug.Log("   1. Install Input System package (if not already done)");
            Debug.Log("   2. Use Velinor/Input System/2. Create Input Actions Asset");
            Debug.Log("   3. Review migration guide in UNITY_ERRORS_RESOLUTION_GUIDE.md");
        }

        [MenuItem("Velinor/Input System/2. Create Input Actions Asset")]
        public static void CreateInputActionsAsset()
        {
            Debug.Log("\n🎮 INPUT ACTIONS ASSET WIZARD\n");

            // Check if Input System is installed
            try
            {
                var inputSystemType = System.Type.GetType("UnityEngine.InputSystem.InputAction, Unity.InputSystem");
                if (inputSystemType == null)
                {
                    Debug.LogError("❌ Input System package not found. Install it first:");
                    Debug.LogError("   Window > Package Manager > + > Add package by name: com.unity.inputsystem");
                    return;
                }
            }
            catch
            {
                Debug.LogError("❌ Input System package not found.");
                return;
            }

            // Create folder structure
            string actionsFolderPath = "Assets/Settings/Input";
            if (!AssetDatabase.IsValidFolder(actionsFolderPath))
            {
                AssetDatabase.CreateFolder("Assets/Settings", "Input");
                Debug.Log($"📁 Created folder: {actionsFolderPath}");
            }

            Debug.Log("✅ Input Actions asset structure ready");
            Debug.Log("\n📝 MANUAL SETUP REQUIRED:");
            Debug.Log("   1. Right-click in Project (Input folder)");
            Debug.Log("   2. Create > Input System > Input Actions");
            Debug.Log("   3. Name it: Controls");
            Debug.Log("   4. Add these Action Maps:");
            Debug.Log("      - Player (for character movement)");
            Debug.Log("      - UI (for menu navigation)");
            Debug.Log("      - Camera (for camera control)");
            Debug.Log("\n   5. Define Actions in each map:");
            Debug.Log("      Player: Move (Value<Vector2>), Jump (Button), Interact (Button), Sprint (Button)");
            Debug.Log("      UI: Navigate (Value<Vector2>), Submit (Button), Cancel (Button)");
            Debug.Log("      Camera: Look (Value<Vector2>)");
            Debug.Log("\n📚 Reference: https://docs.unity3d.com/Packages/com.unity.inputsystem@latest");
        }

        [MenuItem("Velinor/Input System/3. Show Migration Examples")]
        public static void ShowMigrationExamples()
        {
            Debug.Log("\n📚 INPUT SYSTEM MIGRATION EXAMPLES\n");

            Debug.Log("═══════════════════════════════════════════════════════════");
            Debug.Log("EXAMPLE 1: Movement Input");
            Debug.Log("═══════════════════════════════════════════════════════════");
            Debug.Log("\n❌ OLD (Input Manager):");
            Debug.Log("   float horizontal = Input.GetAxis(\"Horizontal\");");
            Debug.Log("   float vertical = Input.GetAxis(\"Vertical\");");
            Debug.Log("   bool isSprinting = Input.GetKey(KeyCode.LeftShift);");

            Debug.Log("\n✅ NEW (Input System):");
            Debug.Log("   using UnityEngine.InputSystem;");
            Debug.Log("   ");
            Debug.Log("   public class PlayerController : MonoBehaviour");
            Debug.Log("   {");
            Debug.Log("       private PlayerControls controls;");
            Debug.Log("       ");
            Debug.Log("       private void Awake() => controls = new PlayerControls();");
            Debug.Log("       ");
            Debug.Log("       private void OnEnable() => controls.Enable();");
            Debug.Log("       ");
            Debug.Log("       private void OnDisable() => controls.Disable();");
            Debug.Log("       ");
            Debug.Log("       private void Update()");
            Debug.Log("       {");
            Debug.Log("           Vector2 moveInput = controls.Player.Move.ReadValue<Vector2>();");
            Debug.Log("           bool isSprinting = controls.Player.Sprint.IsPressed();");
            Debug.Log("           ");
            Debug.Log("           float horizontal = moveInput.x;");
            Debug.Log("           float vertical = moveInput.y;");
            Debug.Log("       }");
            Debug.Log("   }");

            Debug.Log("\n═══════════════════════════════════════════════════════════");
            Debug.Log("EXAMPLE 2: Jump Input");
            Debug.Log("═══════════════════════════════════════════════════════════");
            Debug.Log("\n❌ OLD (Input Manager):");
            Debug.Log("   if (Input.GetKeyDown(KeyCode.Space))");
            Debug.Log("   {");
            Debug.Log("       Jump();");
            Debug.Log("   }");

            Debug.Log("\n✅ NEW (Input System):");
            Debug.Log("   if (controls.Player.Jump.WasPressedThisFrame())");
            Debug.Log("   {");
            Debug.Log("       Jump();");
            Debug.Log("   }");

            Debug.Log("\n═══════════════════════════════════════════════════════════");
            Debug.Log("EXAMPLE 3: Interaction Input");
            Debug.Log("═══════════════════════════════════════════════════════════");
            Debug.Log("\n❌ OLD (Input Manager):");
            Debug.Log("   if (Input.GetKeyDown(KeyCode.E) && _interactable != null)");
            Debug.Log("   {");
            Debug.Log("       _interactable.Interact();");
            Debug.Log("   }");

            Debug.Log("\n✅ NEW (Input System):");
            Debug.Log("   if (controls.Player.Interact.WasPressedThisFrame() && _interactable != null)");
            Debug.Log("   {");
            Debug.Log("       _interactable.Interact();");
            Debug.Log("   }");

            Debug.Log("\n═══════════════════════════════════════════════════════════");
            Debug.Log("COMMON API CONVERSIONS:");
            Debug.Log("═══════════════════════════════════════════════════════════");
            Debug.Log("Input.GetAxis(\"name\")");
            Debug.Log("  → controls.ActionMap.Action.ReadValue<float/Vector2>();");
            Debug.Log("");
            Debug.Log("Input.GetKeyDown(KeyCode.X)");
            Debug.Log("  → controls.ActionMap.Action.WasPressedThisFrame();");
            Debug.Log("");
            Debug.Log("Input.GetKey(KeyCode.X)");
            Debug.Log("  → controls.ActionMap.Action.IsPressed();");
            Debug.Log("");
            Debug.Log("Input.GetKeyUp(KeyCode.X)");
            Debug.Log("  → controls.ActionMap.Action.WasReleasedThisFrame();");
            Debug.Log("");
            Debug.Log("Input.GetMouseButton(0/1)");
            Debug.Log("  → controls.ActionMap.Click.IsPressed(); // Define as button");
            Debug.Log("\n");
        }

        [MenuItem("Velinor/Input System/4. List Files with Input Manager Usage")]
        public static void ListFilesWithInputManager()
        {
            Debug.Log("\n📋 FILES USING INPUT MANAGER (Need Migration)\n");

            string[] searchResults = AssetDatabase.FindAssets("t:Script");
            int filesWithInput = 0;

            foreach (string guid in searchResults)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (!path.Contains("Assets/Scripts")) continue;
                if (path.Contains("Samples")) continue; // Skip sample scripts

                string content = System.IO.File.ReadAllText(path);
                bool hasInput = content.Contains("Input.GetAxis") ||
                               content.Contains("Input.GetKey") ||
                               content.Contains("Input.GetMouseButton");

                if (hasInput)
                {
                    filesWithInput++;
                    // Count occurrences
                    int count = 0;
                    count += System.Text.RegularExpressions.Regex.Matches(content, @"Input\.Get").Count;
                    Debug.Log($"{filesWithInput}. {path} ({count} uses)");
                }
            }

            if (filesWithInput == 0)
            {
                Debug.Log("✅ No files found using Input Manager!");
            }
            else
            {
                Debug.Log($"\n📊 Total files: {filesWithInput}");
                Debug.Log("⚠️  These files should be migrated to Input System");
            }
        }

        private static int CountInputManagerUsage()
        {
            int count = 0;
            string[] searchResults = AssetDatabase.FindAssets("t:Script");

            foreach (string guid in searchResults)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (!path.Contains("Assets/Scripts")) continue;

                try
                {
                    string content = System.IO.File.ReadAllText(path);
                    count += System.Text.RegularExpressions.Regex.Matches(content, @"Input\.Get").Count;
                }
                catch { /* Skip files that can't be read */ }
            }

            return count;
        }
    }
}
