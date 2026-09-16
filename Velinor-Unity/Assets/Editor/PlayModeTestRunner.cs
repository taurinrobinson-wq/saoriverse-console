using UnityEditor;
using UnityEngine;
using System.Collections.Generic;
using System.Reflection;

[InitializeOnLoad]
internal static class PlayModeTestRunner
{
    private const string StateKey = "PlayModeTest.State";
    private const string ResultKey = "PlayModeTest.Result";
    private const string ScriptPathKey = "PlayModeTest.ScriptPath";
    private const string LogKey = "PlayModeTest.Logs";
    private const string SentinelLog = "PLAY_MODE_TEST_COMPLETE";

    private static void AddLog(string msg)
    {
        string logs = SessionState.GetString(LogKey, "");
        logs += "[" + System.DateTime.Now.ToString("HH:mm:ss") + "] " + msg + "\n";
        SessionState.SetString(LogKey, logs);
        Debug.Log("[Test] " + msg);
    }

    static PlayModeTestRunner()
    {
        string state = SessionState.GetString(StateKey, "Idle");
        AddLog("Constructor Fired. State: " + state + ", isPlaying: " + EditorApplication.isPlaying);

        switch (state)
        {
            case "WaitingForCompile":
                SessionState.SetString(StateKey, "EnteringPlayMode");
                EditorApplication.delayCall += () => {
                    AddLog("Setting isPlaying = true");
                    EditorApplication.isPlaying = true;
                };
                break;

            case "EnteringPlayMode":
                if (EditorApplication.isPlaying)
                {
                    AddLog("Entered Play Mode. Starting Test.");
                    SessionState.SetString(StateKey, "InPlayMode");
                    EditorApplication.update += WaitFramesThenRun;
                }
                break;

            case "InPlayMode":
                EditorApplication.update += WaitFramesThenRun;
                break;

            case "Done":
                EditorApplication.delayCall += SelfDestruct;
                break;
        }
    }

    private static int _frameCount = 0;
    private static bool _setupDone = false;
    private static bool _testDone = false;
    private static double _testStartTime = 0;
    
    private static GameObject _player;
    private static GameObject _targetStone;
    private static List<GameObject> _allStones = new List<GameObject>();
    private static object _inputComponent;
    private static FieldInfo _moveInputPath;

    private static void WaitFramesThenRun()
    {
        _frameCount++;
        if (_frameCount < 60) return; // Wait 60 frames
        if (_testDone) return;

        if (!_setupDone)
        {
            _setupDone = true;
            _testStartTime = EditorApplication.timeSinceStartup;
            Setup();
            return;
        }

        float elapsed = (float)(EditorApplication.timeSinceStartup - _testStartTime);
        if (Tick(elapsed) || elapsed >= 15.0f)
        {
            FinishTest(elapsed >= 15.0f, elapsed >= 15.0f ? "Timeout" : null);
        }
    }

    private static void Setup()
    {
        AddLog("Setup started");
        _player = GameObject.Find("Player");
        if (_player == null) { AddLog("Player not found"); return; }

        var all = GameObject.FindObjectsOfType<GameObject>();
        foreach (var go in all) if (go.name.Contains("SM_Medium_02_Sample")) _allStones.Add(go);
        
        if (_allStones.Count == 0) { AddLog("No stones found"); return; }
        
        float minDist = float.MaxValue;
        foreach (var stone in _allStones)
        {
            float d = Vector3.Distance(_player.transform.position, stone.transform.position);
            if (d < minDist) { minDist = d; _targetStone = stone; }
        }
        
        AddLog("Target: " + _targetStone.name);

        _inputComponent = _player.GetComponent("VelinorStarterAssetsInputs");
        if (_inputComponent != null)
        {
             _moveInputPath = _inputComponent.GetType().GetField("moveInput", BindingFlags.Public | BindingFlags.Instance);
             if (_moveInputPath == null) _moveInputPath = _inputComponent.GetType().GetField("_moveInput", BindingFlags.NonPublic | BindingFlags.Instance);
        }

        Vector3 dir = (_targetStone.transform.position - _player.transform.position).normalized;
        _player.transform.position = _targetStone.transform.position - dir * 2f;
    }

    private static bool Tick(float elapsed)
    {
        if (_player == null || _targetStone == null) return true;
        if (_inputComponent != null && _moveInputPath != null) _moveInputPath.SetValue(_inputComponent, new Vector2(0, 1)); 

        float dist = Vector3.Distance(_player.transform.position, _targetStone.transform.position);
        if (Time.frameCount % 60 == 0)
        {
            var colliders = _targetStone.GetComponentsInChildren<Collider>();
            foreach (var col in colliders) AddLog(col.name + ": enabled=" + col.enabled + ", trigger=" + col.isTrigger);
        }

        if (dist < 0.2f) { AddLog("Inside stone!"); return true; }
        return false;
    }

    private static void FinishTest(bool isError, string error)
    {
        _testDone = true;
        EditorApplication.update -= WaitFramesThenRun;
        SessionState.SetString(ResultKey, isError ? "Error: " + error : "Success");
        SessionState.SetString(StateKey, "Done");
        EditorApplication.isPlaying = false;
    }

    private static void SelfDestruct()
    {
        string scriptPath = SessionState.GetString(ScriptPathKey, "");
        if (!string.IsNullOrEmpty(scriptPath) && AssetDatabase.AssetPathExists(scriptPath))
            AssetDatabase.DeleteAsset(scriptPath);
        SessionState.EraseString(StateKey);
    }

    private class TestResult { public bool success; public string error; public string[] logs; }
}
