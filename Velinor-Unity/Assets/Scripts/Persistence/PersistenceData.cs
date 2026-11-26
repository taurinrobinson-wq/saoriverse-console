using UnityEngine;
using System;
using System.Collections.Generic;

namespace Velinor.Persistence
{
    [Serializable]
    public class GlobalSettings
    {
        public int schemaVersion = 1;
        public float musicVolume = 0.7f;
        public float sfxVolume = 0.7f;
        public int resolutionWidth = 1920;
        public int resolutionHeight = 1080;
        public bool isFullscreen = true;
        public int activeProfileSlot = -1; // -1 for none, 0-2 for slots
    }

    [Serializable]
    public class MetaProgress
    {
        public int schemaVersion = 1;
        public List<string> unlockedAssetIds = new List<string>();
        public List<string> unlockedNpcIds = new List<string>();
        public bool gameCompleted = false;
        public List<string> endingsReached = new List<string>();
    }

    [Serializable]
    public class ProfileData
    {
        public int schemaVersion = 1;
        public string displayName = "New Profile";
        public bool gameStarted = false;
        public bool hasValidContinuePoint = false;
        
        public string lastSavedScene = "";
        public string lastSpawnID = "";

        // Economy
        public int bits = 0;

        // Inventory
        public List<InventoryItemEntry> inventory = new List<InventoryItemEntry>();
        public List<string> learnedSchematics = new List<string>();

        // Stats
        public List<ToneEntry> playerTone = new List<ToneEntry>();
        public List<NpcRemnantEntry> npcRemnants = new List<NpcRemnantEntry>();

        // Narrative
        public List<FlagEntry> gameFlags = new List<FlagEntry>();
        public List<DiaryEntryData> diaryEntries = new List<DiaryEntryData>();
        
        // Codex
        public List<string> codexTags = new List<string>();
        public List<string> resolvedGlyphs = new List<string>();
        public float codexResonance = 0f;

        // Meta
        public double playtimeSeconds = 0;
        public long lastSaveTimestampTicks = 0;
    }

    [Serializable]
    public struct InventoryItemEntry
    {
        public string itemId;
        public int quantity;
    }

    [Serializable]
    public struct ToneEntry
    {
        public int toneType; // Cast to enum
        public float value;
    }

    [Serializable]
    public struct NpcRemnantEntry
    {
        public string npcId;
        public float resolve;
        public float empathy;
        public float memory;
        public float nuance;
        public float authority;
        public float need;
        public float trust;
        public float skepticism;
    }

    [Serializable]
    public struct FlagEntry
    {
        public string key;
        public bool value;
    }

    [Serializable]
    public struct DiaryEntryData
    {
        public string timestamp;
        public string content;
    }
}
