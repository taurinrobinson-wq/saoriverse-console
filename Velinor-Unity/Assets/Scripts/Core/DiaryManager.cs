using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

[Serializable]
public class DiaryEntry
{
    public string timestamp;
    public string content;
}

[Serializable]
public class DiaryData
{
    public List<DiaryEntry> entries = new List<DiaryEntry>();
}

public class DiaryManager : MonoBehaviour
{
    public static DiaryManager Instance { get; private set; }
    
    private string diaryPath;
    private DiaryData diaryData = new DiaryData();

    private void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        if (Application.isPlaying) DontDestroyOnLoad(gameObject);
        
        diaryPath = Path.Combine(Application.persistentDataPath, "PlayerDiary.json");
        LoadDiary();
    }

    public void AddEntry(string content)
    {
        var entry = new DiaryEntry
        {
            timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
            content = content
        };
        diaryData.entries.Add(entry);
        SaveDiary();
        Debug.Log($"[DiaryManager] Entry Added: {content}");
    }

    private void SaveDiary()
    {
        try
        {
            string json = JsonUtility.ToJson(diaryData, true);
            File.WriteAllText(diaryPath, json);
        }
        catch (Exception e)
        {
            Debug.LogError($"[DiaryManager] Save Error: {e.Message}");
        }
    }

    private void LoadDiary()
    {
        if (!File.Exists(diaryPath)) return;
        try
        {
            string json = File.ReadAllText(diaryPath);
            diaryData = JsonUtility.FromJson<DiaryData>(json);
        }
        catch (Exception e)
        {
            Debug.LogError($"[DiaryManager] Load Error: {e.Message}");
        }
    }
    
    public List<DiaryEntry> GetEntries() => new List<DiaryEntry>(diaryData.entries);
}
