using UnityEngine;
using UnityEditor;
using Velinor.Core;

namespace Velinor.Editor
{
    [CustomEditor(typeof(NPCDialogueDriver))]
    public class NPCDialogueDriverEditor : UnityEditor.Editor
    {
        public override void OnInspectorGUI()
        {
            DrawDefaultInspector();

            NPCDialogueDriver driver = (NPCDialogueDriver)target;

            GUILayout.Space(10);
            GUILayout.Label("Testing & Debugging", EditorStyles.boldLabel);

            if (GUILayout.Button("Reset Dialogue Flags"))
            {
                driver.ResetDialogueFlags();
            }

            if (GUILayout.Button("Reset and Re-enable NPC"))
            {
                driver.ResetAndReenable();
            }

            if (GUILayout.Button("Clear ALL Game Flags"))
{
                if (EditorUtility.DisplayDialog("Clear All Flags", 
                    "Are you sure you want to clear ALL game flags? This will reset dialogue states for all NPCs.", 
                    "Yes", "Cancel"))
                {
                    driver.ClearAllGameFlags();
                }
            }
            
            GUILayout.Space(5);
            if (GUILayout.Button("Force Re-run Awake (Re-init)"))
            {
                // This can help if the NPC was disabled and needs to re-setup
                // Note: Awake is private, so we'd need to make it public or use reflection
                // But generally RefreshState on SceneStateController handles visibility.
            }
        }
    }
}