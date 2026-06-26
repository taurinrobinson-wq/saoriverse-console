using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// NPCRemnantData: Static repository of REMNANTS trait values for all NPCs.
/// This mirrors the npc_manager.py data and provides a C# source of truth.
/// 
/// REMNANTS Traits:
/// - Resolve: Firmness, conviction, backbone
/// - Empathy: Emotional openness, compassion  
/// - Memory: Recall of past, context awareness
/// - Nuance: Subtlety, shades of gray, complexity
/// - Authority: Command presence, decisiveness
/// - Need: Vulnerability, dependence, connection desire
/// - Trust: Confidence in others
/// - Skepticism: Doubt, caution, suspicion
/// </summary>
public static class NPCRemnantData
{
    /// <summary>
    /// Get REMNANTS traits for a specific NPC
    /// </summary>
    public static NPCStats GetNPCStats(string npcName)
    {
        return npcStatsDatabase.ContainsKey(npcName) 
            ? npcStatsDatabase[npcName] 
            : GetDefaultStats();
    }

    static NPCStats GetDefaultStats()
    {
        return new NPCStats
        {
            Resolve = 0.5f,
            Empathy = 0.5f,
            Memory = 0.5f,
            Nuance = 0.5f,
            Authority = 0.5f,
            Need = 0.5f,
            Trust = 0.5f,
            Skepticism = 0.5f
        };
    }

    // Master database of all NPC REMNANTS values from npc_manager.py
    static Dictionary<string, NPCStats> npcStatsDatabase = new Dictionary<string, NPCStats>()
    {
        // Ravi: Warm, open, trusting but cautious due to thieves
        { "Ravi", new NPCStats {
            Resolve = 0.6f, Empathy = 0.7f, Memory = 0.6f, Nuance = 0.4f,
            Authority = 0.5f, Need = 0.5f, Trust = 0.7f, Skepticism = 0.2f
        }},

        // Nima: Suspicious, observant, deeply empathetic once trust is earned
        { "Nima", new NPCStats {
            Resolve = 0.6f, Empathy = 0.6f, Memory = 0.7f, Nuance = 0.8f,
            Authority = 0.4f, Need = 0.5f, Trust = 0.3f, Skepticism = 0.8f
        }},

        // Kaelen: Shifty, nimble, untrustworthy but redeemable
        { "Kaelen", new NPCStats {
            Resolve = 0.4f, Empathy = 0.3f, Memory = 0.6f, Nuance = 0.5f,
            Authority = 0.3f, Need = 0.7f, Trust = 0.2f, Skepticism = 0.8f
        }},

        // Tovren: Practical, distrustful, values observation over dreaming
        { "Tovren", new NPCStats {
            Resolve = 0.7f, Empathy = 0.3f, Memory = 0.6f, Nuance = 0.3f,
            Authority = 0.6f, Need = 0.2f, Trust = 0.4f, Skepticism = 0.7f
        }},

        // Sera: Gentle, shy, responds to empathy
        { "Sera", new NPCStats {
            Resolve = 0.3f, Empathy = 0.8f, Memory = 0.5f, Nuance = 0.6f,
            Authority = 0.2f, Need = 0.8f, Trust = 0.6f, Skepticism = 0.3f
        }},

        // Dalen: Bold, reckless, values narrative presence
        { "Dalen", new NPCStats {
            Resolve = 0.8f, Empathy = 0.4f, Memory = 0.5f, Nuance = 0.2f,
            Authority = 0.7f, Need = 0.3f, Trust = 0.5f, Skepticism = 0.4f
        }},

        // Mariel: Patient, wise, bridges merchants and shrine keepers
        { "Mariel", new NPCStats {
            Resolve = 0.6f, Empathy = 0.8f, Memory = 0.8f, Nuance = 0.7f,
            Authority = 0.5f, Need = 0.4f, Trust = 0.7f, Skepticism = 0.2f
        }},

        // Korrin: Gossip, suspicious, loves information
        { "Korrin", new NPCStats {
            Resolve = 0.4f, Empathy = 0.3f, Memory = 0.8f, Nuance = 0.7f,
            Authority = 0.3f, Need = 0.5f, Trust = 0.3f, Skepticism = 0.8f
        }},

        // Drossel: Thieves' Leader - Charming yet Dangerous
        { "Drossel", new NPCStats {
            Resolve = 0.8f, Empathy = 0.2f, Memory = 0.8f, Nuance = 0.8f,
            Authority = 0.8f, Need = 0.3f, Trust = 0.1f, Skepticism = 0.9f
        }},

        // Captain Veynar: Guard Captain - Weary Authority
        { "Captain Veynar", new NPCStats {
            Resolve = 0.8f, Empathy = 0.4f, Memory = 0.7f, Nuance = 0.5f,
            Authority = 0.9f, Need = 0.3f, Trust = 0.6f, Skepticism = 0.5f
        }},

        // Archivist Malrik: Skeptics' leader - guardian of records, high memory and skepticism
        { "Malrik", new NPCStats {
            Resolve = 0.7f, Empathy = 0.3f, Memory = 0.9f, Nuance = 0.6f,
            Authority = 0.7f, Need = 0.3f, Trust = 0.3f, Skepticism = 0.7f
        }},

        // High Seer Elenya: Mystics' leader - communal seer, high empathy and trust
        { "Elenya", new NPCStats {
            Resolve = 0.5f, Empathy = 0.9f, Memory = 0.7f, Nuance = 0.8f,
            Authority = 0.6f, Need = 0.4f, Trust = 0.8f, Skepticism = 0.2f
        }},

        // Saori: Oracle — measured, reflective, paradoxical (persistent presence)
        { "Saori", new NPCStats {
            Resolve = 0.8f, Empathy = 0.6f, Memory = 0.85f, Nuance = 0.9f,
            Authority = 0.75f, Need = 0.35f, Trust = 0.4f, Skepticism = 0.7f
        }},

        // Coren the Mediator: bridges opposing factions, high nuance and trust
        { "Coren the Mediator", new NPCStats {
            Resolve = 0.6f, Empathy = 0.65f, Memory = 0.6f, Nuance = 0.8f,
            Authority = 0.6f, Need = 0.4f, Trust = 0.75f, Skepticism = 0.2f
        }},

        // Additional Tier-2 NPCs
        { "Sealina", new NPCStats {
            Resolve = 0.65f, Empathy = 0.85f, Memory = 0.9f, Nuance = 0.75f,
            Authority = 0.55f, Need = 0.8f, Trust = 0.6f, Skepticism = 0.6f
        }},
        { "Lark", new NPCStats {
            Resolve = 0.7f, Empathy = 0.6f, Memory = 0.8f, Nuance = 0.65f,
            Authority = 0.75f, Need = 0.45f, Trust = 0.65f, Skepticism = 0.5f
        }},
        { "Nordia the Mourning Singer", new NPCStats {
            Resolve = 0.7f, Empathy = 0.9f, Memory = 0.9f, Nuance = 0.8f,
            Authority = 0.6f, Need = 0.85f, Trust = 0.55f, Skepticism = 0.6f
        }},
        { "Helia", new NPCStats {
            Resolve = 0.8f, Empathy = 0.75f, Memory = 0.5f, Nuance = 0.6f,
            Authority = 0.55f, Need = 0.6f, Trust = 0.75f, Skepticism = 0.5f
        }},
        { "Elka", new NPCStats {
            Resolve = 0.75f, Empathy = 0.65f, Memory = 0.45f, Nuance = 0.5f,
            Authority = 0.5f, Need = 0.55f, Trust = 0.7f, Skepticism = 0.5f
        }},
    };
}
