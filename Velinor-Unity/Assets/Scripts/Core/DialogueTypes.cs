using System;

public enum BeatType
{
    Interactive,
    Shared
}

[System.Serializable]
public class DialogueChoice
{
    public ToneType tone;
    public string playerLine;
    public string npcResponse;
}
