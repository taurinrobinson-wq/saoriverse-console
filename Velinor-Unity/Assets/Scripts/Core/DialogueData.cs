using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// DialogueData: Defines a single dialogue round with TONE choices and REMNANTS effects.
/// Supports dialogue sequences like Ravi's 3-round encounter.
/// </summary>
[System.Serializable]
public class DialogueRound
{
    public string npcLine;  // What the NPC says at the start of this round
    public List<DialogueChoice> choices;  // 4 TONE-based choices (T/O/N/E)

    public DialogueRound()
    {
        choices = new List<DialogueChoice>(4);
    }
}

[System.Serializable]
public class DialogueChoice
{
    public char toneType;  // 'T', 'O', 'N', or 'E'
    public string toneName;  // "Trust", "Observation", "NarrativePresence", "Empathy"
    public string playerLine;  // What the player says
    public string npcResponse;  // What the NPC says in response
    public Dictionary<string, float> remnantEffects;  // Which REMNANTS this affects

    public DialogueChoice(char toneType, string toneName, string playerLine, string npcResponse, Dictionary<string, float> effects)
    {
        this.toneType = toneType;
        this.toneName = toneName;
        this.playerLine = playerLine;
        this.npcResponse = npcResponse;
        this.remnantEffects = effects;
    }
}

/// <summary>
/// RaviDialogueSequence: The canonical 3-round dialogue for Ravi.
/// - Name reveal on NarrativePresence choice
/// - TONE/REMNANTS stat progression
/// - Sorrow Glyph foreshadowing in Round 3
/// </summary>
public class RaviDialogueSequence
{
    public List<DialogueRound> rounds;
    public bool playerKnowsName = false;

    public RaviDialogueSequence()
    {
        rounds = new List<DialogueRound>();
        BuildRounds();
    }

    void BuildRounds()
    {
        // ========== ROUND 1: Establish Contact ==========
        DialogueRound round1 = new DialogueRound();
        round1.npcLine = "Oh… hello. I did not expect anyone to approach. What do you need?";
        round1.choices = new List<DialogueChoice>
        {
            new DialogueChoice(
                'T', "Trust",
                "I'm new here, but I want to understand this place and the people in it.",
                "Understanding is rare these days. Outsiders usually want something.",
                new Dictionary<string, float> { { "Trust", 1 }, { "Resolve", 1 }, { "Skepticism", -1 } }
            ),
            new DialogueChoice(
                'O', "Observation",
                "You seem approachable. I wouldn't have come over otherwise.",
                "Approachable? Hmph. I suppose I haven't pushed you away yet.",
                new Dictionary<string, float> { { "Nuance", 1 }, { "Memory", 1 }, { "Authority", -1 } }
            ),
            new DialogueChoice(
                'N', "NarrativePresence",
                "You seem like you know your way around this place. What should I call you?",
                "My name… is Ravi. I do not share it easily.",
                new Dictionary<string, float> { { "Authority", 1 }, { "Resolve", 1 }, { "Nuance", -1 } }
            ),
            new DialogueChoice(
                'E', "Empathy",
                "You look weighed down. I'm not here to take anything from you.",
                "Please… do not look at me like that. I am fine. I have to be.",
                new Dictionary<string, float> { { "Empathy", 1 }, { "Need", 1 }, { "Resolve", -1 } }
            )
        };
        rounds.Add(round1);

        // ========== ROUND 2: Reveal the Wound ==========
        DialogueRound round2 = new DialogueRound();
        round2.npcLine = "People come and go. They ask questions. They take what they want. Why are you really here?";
        round2.choices = new List<DialogueChoice>
        {
            new DialogueChoice(
                'T', "Trust",
                "Because I want to understand what happened here. I'm not afraid of the truth.",
                "Truth? The truth is a building fell and took my daughter with it.",
                new Dictionary<string, float> { { "Trust", 1 }, { "Resolve", 1 }, { "Skepticism", -1 } }
            ),
            new DialogueChoice(
                'O', "Observation",
                "Your eyes go distant when you talk. Like you're somewhere else.",
                "I see her everywhere. In the corner of my eye. In the dust.",
                new Dictionary<string, float> { { "Nuance", 1 }, { "Memory", 1 }, { "Authority", -1 } }
            ),
            new DialogueChoice(
                'N', "NarrativePresence",
                "You feel connected to this place… and to something painful. What's your name?",
                "My name is Ravi. I… I do not say it often anymore.",
                new Dictionary<string, float> { { "Authority", 1 }, { "Resolve", 1 }, { "Nuance", -1 } }
            ),
            new DialogueChoice(
                'E', "Empathy",
                "You lost someone. I can feel it. You don't have to tell me everything.",
                "Please… do not speak her name. I cannot bear it.",
                new Dictionary<string, float> { { "Empathy", 1 }, { "Need", 1 }, { "Resolve", -1 } }
            )
        };
        rounds.Add(round2);

        // ========== ROUND 3: Call to Action (Sorrow Glyph Foreshadowing) ==========
        DialogueRound round3 = new DialogueRound();
        round3.npcLine = "Sometimes… I feel something. A pull. Like the air itself remembers her. It sounds mad, I know.";
        round3.choices = new List<DialogueChoice>
        {
            new DialogueChoice(
                'T', "Trust",
                "You're not mad. Something here is calling out. I can feel it too.",
                "If you feel it too… then follow it. Maybe it will show you what I cannot.",
                new Dictionary<string, float> { { "Trust", 1 }, { "Resolve", 1 }, { "Skepticism", -1 } }
            ),
            new DialogueChoice(
                'O', "Observation",
                "When you said that, something on my device flickered. Like it reacted.",
                "Your device reacts? Then go. Whatever it senses… it is near where she… where it happened.",
                new Dictionary<string, float> { { "Nuance", 1 }, { "Memory", 1 }, { "Authority", -1 } }
            ),
            new DialogueChoice(
                'N', "NarrativePresence",
                "Some places hold echoes. Some moments leave marks. Maybe this one wants to be found.",
                "If an echo remains… then perhaps it is meant for someone stronger than me.",
                new Dictionary<string, float> { { "Authority", 1 }, { "Resolve", 1 }, { "Nuance", -1 } }
            ),
            new DialogueChoice(
                'E', "Empathy",
                "Grief leaves traces. Sometimes they lead us somewhere we need to go.",
                "If these traces guide you… then let them. I cannot follow them anymore.",
                new Dictionary<string, float> { { "Empathy", 1 }, { "Need", 1 }, { "Resolve", -1 } }
            )
        };
        rounds.Add(round3);
    }
}
