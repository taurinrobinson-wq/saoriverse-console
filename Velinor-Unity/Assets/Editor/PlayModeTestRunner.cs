using UnityEditor;
using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using TMPro;
using Velinor.Core;

namespace Unity.AI.Assistant.PlayModeTest
{
[InitializeOnLoad]
    internal static class PlayModeTestRunner
    {
        private const string StateKey = "PlayModeTest.State";
        private const string ResultKey = "PlayModeTest.Result";
        private const string ScriptPathKey = "PlayModeTest.ScriptPath";
        private const string SentinelLog = "PLAY_MODE_TEST_COMPLETE";

        private static readonly int WaitFrames = SessionState.GetInt("PlayModeTest.WaitFrames", 30);
        private static List<string> _capturedLogs = new List<string>();
        private const int MaxCapturedLogs = 100;

        static PlayModeTestRunner()
        {
            string state = SessionState.GetString(StateKey, "Idle");
            switch (state)
            {
                case "WaitingForCompile":
                    EditorApplication.delayCall += () =>
                    {
                        SessionState.SetString(StateKey, "EnteringPlayMode");
                        EditorApplication.playModeStateChanged += OnPlayModeStateChanged;
                        EditorApplication.isPlaying = true;
                    };
                    break;
                case "EnteringPlayMode":
                    EditorApplication.playModeStateChanged += OnPlayModeStateChanged;
                    if (EditorApplication.isPlaying)
                    {
                        EditorApplication.playModeStateChanged -= OnPlayModeStateChanged;
                        SessionState.SetString(StateKey, "InPlayMode");
                        EditorApplication.update += WaitFramesThenRun;
                    }
                    break;
                case "InPlayMode":
                    if (EditorApplication.isPlaying) EditorApplication.update += WaitFramesThenRun;
                    break;
                case "Done":
                    Debug.Log(SentinelLog);
                    EditorApplication.delayCall += SelfDestruct;
                    break;
            }
        }

        private static void OnPlayModeStateChanged(PlayModeStateChange change)
        {
            if (change == PlayModeStateChange.EnteredPlayMode)
            {
                EditorApplication.playModeStateChanged -= OnPlayModeStateChanged;
                SessionState.SetString(StateKey, "InPlayMode");
                EditorApplication.update += WaitFramesThenRun;
            }
        }

        private static int _frameCount = 0;
        private static bool _hasRun = false;

        private static void WaitFramesThenRun()
        {
            _frameCount++;
            if (_frameCount < WaitFrames) return;
            if (_hasRun) return;
            _hasRun = true;
            EditorApplication.update -= WaitFramesThenRun;

            Application.logMessageReceived += OnLogMessage;
            string resultJson;
            try
            {
                resultJson = RunTestLogic();
            }
            catch (System.Exception e)
            {
                resultJson = JsonUtility.ToJson(new TestResult { success = false, error = e.ToString(), logs = _capturedLogs.ToArray() });
            }
            finally
            {
                Application.logMessageReceived -= OnLogMessage;
            }
            SessionState.SetString(ResultKey, resultJson);
            SessionState.SetString(StateKey, "Done");
            EditorApplication.isPlaying = false;
        }

        private static void SelfDestruct()
        {
            string scriptPath = SessionState.GetString(ScriptPathKey, "");
            if (!string.IsNullOrEmpty(scriptPath) && AssetDatabase.AssetPathExists(scriptPath))
                AssetDatabase.DeleteAsset(scriptPath);
            SessionState.EraseString(StateKey);
            SessionState.EraseString(ScriptPathKey);
        }

        private static void OnLogMessage(string message, string stackTrace, LogType type)
        {
            if (_capturedLogs.Count >= MaxCapturedLogs) return;
            _capturedLogs.Add("[" + type + "] " + message);
        }

        [System.Serializable]
        private class TestResult
        {
            public bool success;
            public string error;
            public string[] logs;
            public bool ravi_found;
            public bool interaction_found;
            public bool canvas_found;
        }

        private static string RunTestLogic()
        {
            var ravi = GameObject.Find("Ravi");
            if (ravi == null) return JsonUtility.ToJson(new TestResult { success = false, error = "Ravi not found", logs = _capturedLogs.ToArray() });

            var interaction = ravi.GetComponent<NPCInteraction>();
            if (interaction == null) return JsonUtility.ToJson(new TestResult { success = false, error = "NPCInteraction not found on Ravi", logs = _capturedLogs.ToArray() });

            // Trigger dialogue
            interaction.Invoke("OpenDialogue", 0f);

            // Check if DialogueCanvas was found by NPCInteraction (it's a private field, so reflection)
            var canvasField = interaction.GetType().GetField("dialogueCanvas", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            var canvas = (Canvas)canvasField.GetValue(interaction);

            return JsonUtility.ToJson(new TestResult
            {
                success = true,
                ravi_found = true,
                interaction_found = true,
                canvas_found = canvas != null,
                logs = _capturedLogs.ToArray()
            });
        }
    }
}
