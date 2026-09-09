/// <summary>
/// Represents the type of dialogue interaction in a beat.
/// </summary>
public enum DialogueMode
{
    NPCToNPC,          // Shared dialogue, no player choices
    NPCToPlayer,       // NPC speaks, player chooses, NPC responds
    PlayerInnerThought,// Player monologue, no choices, no NPC response
    PlayerActionChoice // Player acts, sees result_text, optional NPC response
}
