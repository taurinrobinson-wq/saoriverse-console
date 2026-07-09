using UnityEditor;
using UnityEngine;
using System.Collections.Generic;

namespace Unity.AI.Assistant.PlayModeTest
{
    [InitializeOnLoad]
    internal static class PlayModeTestRunner
    {
        private const string StateKey = "PlayModeTest.State";
        private const string ResultKey = "PlayModeTest.Result";
        private const string ScriptPathKey = "PlayModeTest.ScriptPath";

        static PlayModeTestRunner()
        {
            string state = SessionState.GetString(StateKey, "Idle");
            switch (state)
            {
                case "WaitingForCompile":
                    EditorApplication.delayCall += () =>
                    {
                        SessionState.SetString(StateKey, "EnteringPlayMode");
                        EditorApplication.isPlaying = true;
                    };
                    break;
                case "EnteringPlayMode":
                    if (EditorApplication.isPlaying)
                    {
                        SessionState.SetString(StateKey, "InPlayMode");
                        EditorApplication.update += WaitAndRun;
                    }
                    break;
            }
        }

        private static int _frames = 0;
        private static void WaitAndRun()
        {
            _frames++;
            if (_frames < 30) return; // Wait 30 frames for things to settle
            EditorApplication.update -= WaitAndRun;

            string result = RunTestLogic();
            SessionState.SetString(ResultKey, result);
            SessionState.SetString(StateKey, "Done");
            EditorApplication.isPlaying = false;
        }

        private static string RunTestLogic()
        {
            var res = new TestResult();
            
            var player = GameObject.Find("Player");
            if (player != null)
            {
                res.playerActive = player.activeInHierarchy;
                res.playerPosition = player.transform.position;
                var rb = player.GetComponent<Rigidbody>();
                if (rb != null) res.playerVelocity = rb.linearVelocity;
                
                var scm = player.GetComponent("SimpleCharacterMovement");
                if (scm != null)
                {
                    var field = scm.GetType().GetField("isGrounded", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                    if (field != null) res.playerGrounded = (bool)field.GetValue(scm);
                }
            }

            var npsParent = GameObject.Find("NPCs");
            if (npsParent != null)
            {
                res.npcPositions = new List<Vector3>();
                for (int i = 0; i < npsParent.transform.childCount; i++)
                {
                    res.npcPositions.Add(npsParent.transform.GetChild(i).position);
                }
            }

            var ground = GameObject.Find("Ground");
            if (ground != null)
            {
                res.groundPosition = ground.transform.position;
                var col = ground.GetComponent<Collider>();
                if (col != null) res.groundBounds = col.bounds;
            }

            return JsonUtility.ToJson(res);
        }

        [System.Serializable]
        private class TestResult
        {
            public bool playerActive;
            public Vector3 playerPosition;
            public Vector3 playerVelocity;
            public bool playerGrounded;
            public List<Vector3> npcPositions;
            public Vector3 groundPosition;
            public Bounds groundBounds;
        }
    }
}