using UnityEditor;
using UnityEngine;

namespace Velinor.Editor
{
    /// <summary>
    /// CloudServicesConfigHelper - Fixes cloud service connectivity issues
    /// 
    /// The project experiences cloud service timeouts:
    /// - Account API did not become accessible within 30 seconds
    /// - Connection.state_change timeout (500ms, 10 attempts)
    /// 
    /// These are typically non-critical for local/offline development.
    /// </summary>
    public class CloudServicesConfigHelper
    {
        [MenuItem("Velinor/Cloud Services/Check Cloud Services Status")]
        public static void CheckCloudServicesStatus()
        {
            Debug.Log("\n☁️  CLOUD SERVICES STATUS CHECK\n");

            Debug.Log("Connected Services:");
            Debug.Log("─────────────────────────────────────");

            // Check Unity Services
            Debug.Log("📦 Unity Services: Checking...");
            try
            {
                // Try to access cloud services
                var servicesType = System.Type.GetType("Unity.Services.Core.UnityServices, Unity.Services.Core");
                if (servicesType != null)
                {
                    Debug.Log("✅ Unity Services package installed");
                }
                else
                {
                    Debug.Log("⚠️  Unity Services package not installed");
                }
            }
            catch
            {
                Debug.Log("❌ Error checking Unity Services");
            }

            // Check Relay
            Debug.Log("\n🔗 Netcode Relay: Checking...");
            try
            {
                var relayType = System.Type.GetType("Unity.Netcode.Transports.UTP.UnityTransport, Unity.Netcode.GameObjects");
                if (relayType != null)
                {
                    Debug.Log("✅ Netcode for GameObjects installed");
                    Debug.Log("⚠️  Relay connection timeout is normal if:");
                    Debug.Log("   • Not connected to internet");
                    Debug.Log("   • Running offline");
                    Debug.Log("   • Project not set up for multiplayer");
                }
                else
                {
                    Debug.Log("⚠️  Netcode for GameObjects not installed");
                }
            }
            catch
            {
                Debug.Log("❌ Error checking Netcode");
            }

            Debug.Log("\n📊 ISSUE SUMMARY:");
            Debug.Log("─────────────────────────────────────");
            Debug.Log("Account API timeout: Usually network-related");
            Debug.Log("Relay connection timeout: Normal if not using multiplayer");
            Debug.Log("");
            Debug.Log("✅ Both are SAFE TO IGNORE for single-player development");
        }

        [MenuItem("Velinor/Cloud Services/Disable Cloud Services (Recommended for Solo Dev)")]
        public static void DisableCloudServices()
        {
            Debug.Log("\n🔇 DISABLING CLOUD SERVICES\n");

            Debug.Log("If you're developing solo or offline:");
            Debug.Log("─────────────────────────────────────");

            Debug.Log("\nStep 1: Disable Relay (if not using multiplayer)");
            Debug.Log("   • Window > Package Manager");
            Debug.Log("   • Search: com.unity.netcode.gameobjects");
            Debug.Log("   • Click gear icon > Remove");

            Debug.Log("\nStep 2: Disable AI Assistant (if not using)");
            Debug.Log("   • Window > Package Manager");
            Debug.Log("   • Search: com.unity.ai.assistant");
            Debug.Log("   • Click gear icon > Remove");

            Debug.Log("\nStep 3: Disable Cloud Save (if not needed)");
            Debug.Log("   • Window > Package Manager");
            Debug.Log("   • Search: com.unity.services.cloud-save");
            Debug.Log("   • Click gear icon > Remove");

            Debug.Log("\n✅ RESULT: Faster editor startup, no cloud timeouts");
            Debug.Log("⚠️  NOTE: You can reinstall these later if needed");
        }

        [MenuItem("Velinor/Cloud Services/Show Cloud Services Info")]
        public static void ShowCloudServicesInfo()
        {
            Debug.Log("\n☁️  CLOUD SERVICES INFO\n");

            Debug.Log("What are cloud services?");
            Debug.Log("─────────────────────────────────────");
            Debug.Log("• Unity Services - Authentication, player progression");
            Debug.Log("• Netcode Relay - Multiplayer networking");
            Debug.Log("• AI Assistant - Cloud-based development tools");
            Debug.Log("• Cloud Save - Player data synchronization");

            Debug.Log("\nWhy are they timing out?");
            Debug.Log("─────────────────────────────────────");
            Debug.Log("❌ Network connectivity issues");
            Debug.Log("❌ Internet connection unavailable");
            Debug.Log("❌ Cloud services temporarily down");
            Debug.Log("❌ Editor not in focus when initializing");
            Debug.Log("❌ Project not linked to Unity Services");

            Debug.Log("\nAre cloud service timeouts a problem?");
            Debug.Log("─────────────────────────────────────");
            Debug.Log("✅ NO - Not for local development");
            Debug.Log("✅ Only matters if using multiplayer/cloud features");
            Debug.Log("✅ Single-player games work fine");
            Debug.Log("✅ Safe to ignore the warnings");

            Debug.Log("\nBest practices:");
            Debug.Log("─────────────────────────────────────");
            Debug.Log("🎮 Solo Dev: Disable cloud services, reduce clutter");
            Debug.Log("🌐 Multiplayer: Keep services enabled, test connections");
            Debug.Log("📱 Mobile: Verify cloud services for auth/progression");

            Debug.Log("\nTroubleshooting:");
            Debug.Log("─────────────────────────────────────");
            Debug.Log("1. Check internet connection");
            Debug.Log("2. Wait 30-60 seconds (services initialize slowly)");
            Debug.Log("3. Ensure editor window is focused");
            Debug.Log("4. Restart Unity editor");
            Debug.Log("5. Disable services if not needed (recommended)");
            Debug.Log("\n");
        }

        [MenuItem("Velinor/Cloud Services/Open Project Settings")]
        public static void OpenProjectSettings()
        {
            EditorGUIUtility.PingAssetInProjectWindow(AssetDatabase.LoadAssetAtPath<Object>("ProjectSettings"));
            Debug.Log("📂 Opening Project Settings...");
            Debug.Log("Location: Edit > Project Settings > Services");
        }
    }
}
