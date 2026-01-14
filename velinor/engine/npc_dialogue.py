"""
NPC Dialogue Generation System

Each NPC has:
1. Lexicon: Trait-keyed word pools (vocabulary tied to personality)
2. Temperament: Stylistic decorator that wraps dialogue with unique voice
3. Trait mapping: Which REMNANTS traits define their dialogue style

Example:
- Sera's lexicon uses nature metaphors (bloom, sprout, roots, flicker)
- Sera's temperament adds soft, ephemeral phrasing
- Sera's trait mapping uses empathy as primary dialect shifter
"""

import random
from typing import Dict, List, Tuple


# ============================================================================
# LEXICON POOLS: Vocabulary keyed to NPC personality + traits
# ============================================================================

LEXICONS = {
    "Ravi": {
        "description": "Merchant leader — warmth + pragmatism",
        "trust_high": ["believe in", "stand with", "rely on", "partner with"],
        "trust_low": ["doubt", "hesitate", "question", "distrust"],
        "authority_high": ["lead", "guide", "command", "direct"],
        "authority_low": ["suggest", "propose", "hope for", "wish"],
        "empathy_high": ["understand", "care for", "support", "embrace"],
        "empathy_low": ["overlook", "dismiss", "prioritize profit", "calculate"]
    },
    
    "Nima": {
        "description": "Observer + Skeptic — cunning, perceptive",
        "skepticism_high": ["suspicion", "shadow", "hidden truth", "careful eye"],
        "skepticism_low": ["clarity", "open path", "trust", "transparency"],
        "memory_high": ["recall", "know history", "remember", "weave past"],
        "memory_low": ["forget", "miss", "overlook", "lose track"],
        "nuance_high": ["layers", "complexity", "subtlety", "depth"],
        "nuance_low": ["surface", "simple", "obvious", "plain"]
    },
    
    "Kaelen": {
        "description": "Thief + Potential Redeemer — cunning but conflicted",
        "empathy_high": ["redeem", "listen", "share", "connect", "heal"],
        "empathy_low": ["scheme", "trick", "steal", "deceive", "exploit"],
        "skepticism_high": ["doubt", "whisper", "hidden", "mask", "shadow"],
        "skepticism_low": ["open", "plain", "clear", "direct", "honest"],
        "need_high": ["help", "support", "understand", "accept", "belong"],
        "need_low": ["survive alone", "take what's mine", "trust no one", "self-reliant"],
        "trust_high": ["faith", "belief", "alliance", "bond"],
        "trust_low": ["betrayal", "caution", "wariness", "doubt"]
    },
    
    "Tovren": {
        "description": "Practical merchant — steady, measured",
        "resolve_high": ["firm", "unyielding", "steady", "grounded"],
        "resolve_low": ["uncertain", "hesitant", "fragile", "shaken"],
        "authority_high": ["command respect", "lead by example", "clear path"],
        "authority_low": ["defer", "wait", "listen", "consider"],
        "nuance_high": ["weigh carefully", "balance", "consider all sides"],
        "nuance_low": ["cut through", "direct action", "clear choice"]
    },
    
    "Sera": {
        "description": "Herb Novice + Healer — ephemeral, bubbly, nature-infused",
        "empathy_high": ["bloom", "soften", "sprout", "gentle", "nurture"],
        "empathy_low": ["fragile", "flicker", "fade", "wilt", "wither"],
        "need_high": ["grow", "reach toward", "unfold", "open"],
        "need_low": ["close", "withdraw", "retreat", "hesitate"],
        "trust_high": ["sunlight", "rain", "soil", "rooted"],
        "trust_low": ["shadow", "drought", "barren", "adrift"]
    },
    "Saori": {
        "description": "Oracle — measured, reflective, paradoxical",
        "nuance_high": ["layered", "paradox", "mirror", "rift"],
        "nuance_low": ["plain", "flat", "surface", "simple"],
        "memory_high": ["recall", "echo", "archive", "remember"],
        "memory_low": ["fade", "blank", "slip", "forget"],
        "empathy_high": ["feel", "share", "tend", "hold"],
        "empathy_low": ["withdraw", "harden", "distance", "shut down"],
        "skepticism_high": ["probe", "question", "what if", "shadow"],
        "skepticism_low": ["accept", "trust", "open", "clear"],
        "trust_high": ["believe", "confide", "rely", "root"],
        "trust_low": ["doubt", "hesitate", "step back", "guard"],
        "authority_high": ["declare", "guide", "pronounce", "teach"],
        "authority_low": ["suggest", "offer", "propose", "invite"],
        "need_high": ["seek", "reach", "ask", "need"],
        "need_low": ["sustain", "stand", "alone", "manage"],
        "resolve_high": ["persist", "hold fast", "refuse", "endure"],
        "resolve_low": ["waver", "pause", "consider", "yield"]
    },
    
    "Dalen": {
        "description": "Wanderer + Adventurer — bold, reckless, free-spirited",
        "authority_high": ["bold", "reckless", "charge", "leap", "seize"],
        "authority_low": ["pause", "consider", "wait", "hesitate", "reflect"],
        "resolve_high": ["steel", "fire", "determination", "unstoppable"],
        "resolve_low": ["waver", "falter", "doubt", "tire"],
        "courage_high": ["face the storm", "embrace danger", "ride the wind"],
        "courage_low": ["shelter", "protect", "withdraw", "seek safety"]
    },
    
    "Mariel": {
        "description": "Bridge Figure + Wise Woman — remembers, weaves, binds",
        "memory_high": ["remember", "bind", "weave", "thread", "restore"],
        "memory_low": ["forget", "loosen", "fade", "drift", "scatter"],
        "empathy_high": ["understand", "hold", "honor", "cherish"],
        "empathy_low": ["release", "let go", "move past", "leave behind"],
        "nuance_high": ["layers", "complexity", "interconnected", "woven"],
        "nuance_low": ["simple", "clear", "direct", "straightforward"]
    },
    
    "Korrin": {
        "description": "Gossip + Informant — rumors, layers, alleys",
        "nuance_high": ["whisper", "rumor", "layer upon layer", "intricate"],
        "nuance_low": ["plain", "direct", "simple truth", "straightforward"],
        "memory_high": ["recall every detail", "know everyone's secrets", "never forget"],
        "memory_low": ["forget", "lose track", "miss the details"],
        "skepticism_high": ["question everything", "trust no one", "always watching"],
        "skepticism_low": ["believe", "trust", "open", "accept"]
    },
    
    "Drossel": {
        "description": "Thieves' Leader — Slavic/French hybrid, charming yet dangerous",
        "trust_high": ["mon ami", "deal struck", "coin exchanged", "handshake sealed"],
        "trust_low": ["bratva", "shadow deal", "knife in back", "betrayal looms"],
        "authority_high": ["command respect", "lead from shadow", "organize the chaos"],
        "authority_low": ["defer to", "bow to", "follow orders", "take direction"],
        "memory_high": ["never forget a favor", "remember every debt", "hold grudges long"],
        "memory_low": ["let it pass", "forgive", "move on", "forget"]
    },
    
    "Captain Veynar": {
        "description": "Guard Captain — weary authority, scarred by justice",
        "authority_high": ["law", "duty", "command", "justice", "order"],
        "authority_low": ["doubt", "strain", "weariness", "shadow", "burden"],
        "resolve_high": ["stand firm", "unyielding", "steel", "guard", "defend"],
        "resolve_low": ["hesitate", "fragile", "uncertain", "crack", "falter"],
        "memory_high": ["never forget", "learned hard", "know the cost", "recall"],
        "memory_low": ["lose track", "overlook", "forget", "miss"],
        "empathy_high": ["understand", "shoulder", "recognize", "honor"],
        "empathy_low": ["dismiss", "overlook", "ignore", "pass by"]
    }
#}

# Additional Tier-2 NPC lexicons (concise pools)
LEXICONS.update({
    "Sealina": {
        "description": "Singer of Loss — elegiac, mnemonic",
        "memory_high": ["song", "lament", "echo", "remember"],
        "memory_low": ["quiet", "blank", "hush", "gone"],
        "empathy_high": ["hold", "mourn", "tend", "share"],
        "empathy_low": ["turn away", "harden", "deflect"]
    },
    "Lark": {
        "description": "Ritual keeper — formal, steady",
        "authority_high": ["ceremony", "rite", "order", "bind"],
        "authority_low": ["loose", "open", "invite", "suggest"],
        "memory_high": ["archive", "record", "mark", "inscribe"]
    },
    "Nordia the Mourning Singer": {
        "description": "Mourning singer — melodic grief",
        "empathy_high": ["wail", "lament", "weave", "carry"],
        "nuance_high": ["layered", "tonal", "undertone"]
    },
    "Helia": {
        "description": "Embodied presence — steady, warm",
        "presence_high": ["grounded", "breath", "stance", "footing"],
        "trust_high": ["trust", "open heart", "welcome"]
    },
    "Elka": {
        "description": "Clear, present — plainspoken",
        "nuance_low": ["plain", "simple", "direct"],
        "empathy_high": ["listen", "notice", "attend"]
    },
    "Inodora": {
        "description": "Bridge keeper — story-minded",
        "memory_high": ["recall", "weave", "thread", "archive"],
        "nuance_high": ["layer", "connect", "splice"]
    },
    "Rasha": {
        "description": "Optimist — joyful, trusting",
        "trust_high": ["believe", "welcome", "offer"],
        "empathy_high": ["celebrate", "smile", "share joy"]
    },
    "Coren the Mediator": {
        "description": "Mediator — paradox holder",
        "nuance_high": ["hold both", "paradox", "balance", "weave"],
        "authority_high": ["guide", "hold space", "mediate"]
    },
    "Juria & Korinth": {
        "description": "Pair — cooperative, warm",
        "trust_high": ["together", "us", "partnership", "bond"],
        "joy_high": ["laugh", "share", "play"]
    },
    "Lira": {
        "description": "Boatmaker — practical warmth",
        "authority_high": ["craft", "shape", "measure", "finish"],
        "empathy_high": ["teach", "guide", "show"]
    },
    "Orvak": {
        "description": "Liminal keeper — wary, observant",
        "skepticism_high": ["probe", "watch", "guard"],
        "memory_high": ["map", "track", "trace"]
    },
    "Sanor": {
        "description": "Wound-dweller — hardened, pragmatic",
        "skepticism_high": ["survive", "harden", "endure"],
        "need_high": ["shelter", "supply", "sustain"]
    },
    "Dakrin": {
        "description": "Reclaimer — resolute, restorative",
        "resolve_high": ["reclaim", "restore", "repair", "forge"],
        "authority_high": ["lead", "command", "organize"]
    },
    "Kiv": {
        "description": "Memory-bearer — quiet, intense",
        "memory_high": ["echo", "single note", "anchor", "relic"],
        "nuance_high": ["subtle", "thin thread", "trace"]
    },
    "Seyla": {
        "description": "Archivist of Lineage — formal, exact",
        "memory_high": ["lineage", "record", "register", "chronicle"],
        "authority_high": ["record", "preserve", "codify"]
    },
    "Velka": {
        "description": "Bone Keeper — solemn, ritual",
        "memory_high": ["bones", "remains", "honor", "rest"],
        "nuance_high": ["quiet", "soft edge", "echo"]
    },
    "Tala": {
        "description": "Market cook — warm, jovial",
        "joy_high": ["spice", "share", "warmth", "hearth"],
        "trust_high": ["welcome", "invite", "offer"]
    },
    "Tessa": {
        "description": "Desert widow — resilient, quiet",
        "empathy_high": ["soft sorrow", "tend", "remember"],
        "resolve_high": ["endure", "persist", "stand"]
    }
})


# ============================================================================
# TEMPERAMENT DECORATORS: Stylistic wrappers for each NPC's voice
# ============================================================================

def apply_temperament(npc_name: str, text: str, remnants: Dict[str, float]) -> str:
    """
    Apply NPC-specific stylistic modifications to dialogue.
    Temperament varies slightly based on trait values for dynamic feel.
    """
    
    if npc_name == "Ravi":
        if remnants.get("trust", 0.5) > 0.7:
            return f"{text}, spoken with warm merchant confidence."
        else:
            return f"{text}, spoken with measured merchant caution."
    
    elif npc_name == "Nima":
        if remnants.get("skepticism", 0.8) > 0.75:
            return f"{text} — always watching, always wary."
        else:
            return f"{text} — eyes narrowing with thought."
    
    elif npc_name == "Kaelen":
        if remnants.get("empathy", 0.3) > 0.6:
            return f"{text}... said with genuine remorse."
        else:
            return f"{text}... said with a sly, calculating grin."
    
    elif npc_name == "Tovren":
        return f"{text}, practical as iron and twice as reliable."
    
    elif npc_name == "Sera":
        if remnants.get("empathy", 0.8) > 0.75:
            return f"{text}... like herbs, it blooms so softly."
        else:
            return f"{text}... like herbs, it fades to shadow."
    
    elif npc_name == "Dalen":
        if remnants.get("authority", 0.7) > 0.75:
            return f"{text}! His voice rings bold and reckless."
        else:
            return f"{text}, considered before the next step."
    
    elif npc_name == "Mariel":
        return f"{text}, woven patiently into the tapestry of memory."
    
    elif npc_name == "Korrin":
        return f"{text}, whispered like gossip in the alleys."
    
    elif npc_name == "Drossel":
        if remnants.get("trust", 0.1) > 0.5:
            return f"{text}, mon cher — a deal is a deal."
        else:
            return f"{text}, mon cher — but shadows linger."
    
    elif npc_name == "Captain Veynar":
        if remnants.get("resolve", 0.8) > 0.75:
            return f"{text}. His voice is steady, scarred by years of duty."
        else:
            return f"{text}. His voice carries the weight of impossible choices."

    elif npc_name == "Saori":
        # Saori speaks in layered, patient phrasing — varies by nuance and skepticism
        if remnants.get("nuance", 0.5) > 0.8:
            return f"{text} — Saori's voice echoes, layered and patient."
        if remnants.get("skepticism", 0.5) > 0.65:
            return f"{text} — she tilts her head, measuring each word."
        return f"{text} — spoken with quiet, watchful clarity."
    
    elif npc_name == "Tessa":
        if remnants.get("empathy", 0.5) > 0.7:
            return f"{text} — her voice is soft, carrying long memory."
        return f"{text} — said with desert-worn quiet and steady resolve."

    elif npc_name == "Sealina":
        return f"{text} — sung gently, like a remembered lament."

    elif npc_name == "Coren the Mediator":
        if remnants.get("nuance", 0.5) > 0.8:
            return f"{text} — Coren holds both sides in a single breath."
        return f"{text} — offered as an invitation to see more than one truth."

    elif npc_name == "Lira":
        return f"{text} — practical, warm, and shaped with careful hands."

    elif npc_name == "Orvak":
        return f"{text} — said in a low, watchful tone, as if mapping the room."

    elif npc_name == "Sanor":
        return f"{text} — blunt, survivable, and not given to softness."

    elif npc_name == "Dakrin":
        return f"{text} — resolute and focused on repair; a steady call to action."

    elif npc_name == "Kiv":
        return f"{text} — quiet as an echo, heavy with a single remembered thing."

    elif npc_name == "Tala":
        return f"{text} — offered with a warm laugh and an inviting hand."

    elif npc_name == "Lark":
        return f"{text} — ceremonially stated, as if in a small ritual." 

    elif npc_name == "Nordia the Mourning Singer":
        return f"{text} — carried in a melodic, elegiac cadence."

    elif npc_name == "Helia":
        return f"{text} — steady, present, and quietly grounding."

    elif npc_name == "Elka":
        return f"{text} — plainspoken and clear."

    elif npc_name == "Inodora":
        return f"{text} — told as if weaving a story between past and now."

    elif npc_name == "Rasha":
        return f"{text} — bright, trusting, and likely to smile."

    elif npc_name == "Juria & Korinth":
        return f"{text} — spoken in easy duet, two voices braided together."

    elif npc_name == "Seyla" or npc_name == "Velka":
        return f"{text} — catalogued carefully, said with archival precision."
    
    else:
        return text


# ============================================================================
# DIALOGUE GENERATOR
# ============================================================================

def generate_dialogue(npc_name: str, remnants: Dict[str, float], 
                     context: str = "neutral") -> str:
    """
    Generate contextual dialogue based on NPC personality + current REMNANTS state.
    
    Args:
        npc_name: Name of the NPC
        remnants: Current REMNANTS trait dict
        context: Dialogue context (neutral, greeting, conflict, resolution, etc.)
    
    Returns:
        Generated dialogue string
    """
    
    if npc_name not in LEXICONS:
        return f"{npc_name} looks at you thoughtfully."
    
    lexicon_pool = LEXICONS[npc_name]
    
    # Find dominant trait
    dominant_trait, trait_value = max(remnants.items(), key=lambda x: x[1])
    
    # Map trait to lexicon keys (high/low based on threshold)
    trait_key_high = f"{dominant_trait}_high"
    trait_key_low = f"{dominant_trait}_low"
    
    # Select word from appropriate lexicon pool
    if trait_value > 0.7:
        word_pool = lexicon_pool.get(trait_key_high, [])
    else:
        word_pool = lexicon_pool.get(trait_key_low, [])
    
    if not word_pool:
        # Fallback if trait not in lexicon
        word_pool = ["something", "a path", "a moment"]
    
    word = random.choice(word_pool)
    
    # Build contextual dialogue
    if context == "greeting":
        base_dialogue = f"I see {word} in you."
    elif context == "conflict":
        base_dialogue = f"I feel {word} between us now."
    elif context == "resolution":
        base_dialogue = f"Maybe we've found {word} in each other."
    else:  # neutral
        base_dialogue = f"My {dominant_trait} feels {word}."
    
    # Apply temperament decorator
    return apply_temperament(npc_name, base_dialogue, remnants)


# ============================================================================
# CHOICE POOLS: Player response options by trait
# ============================================================================

CHOICE_POOLS = {
    "resolve": ["Stand firm.", "Don't back down.", "Hold your ground."],
    "empathy": ["Show compassion.", "Listen deeply.", "Share understanding."],
    "memory": ["Recall what happened.", "Remind them of the past.", "Bring history to bear."],
    "nuance": ["Suggest subtly.", "Speak with care.", "Find middle ground."],
    "authority": ["Command directly.", "Lead decisively.", "Take charge."],
    "need": ["Ask for help.", "Admit weakness.", "Seek connection."],
    "trust": ["Offer your faith.", "Build an alliance.", "Show reliance."],
    "skepticism": ["Question their motives.", "Probe for truth.", "Doubt openly."],
    "observation": ["Notice the details.", "Watch carefully.", "Pay close attention."],
    "narrative_presence": ["Tell your story.", "Claim the moment.", "Speak your truth."],
    "wisdom": ["Choose carefully.", "Think it through.", "Reflect deeply."],
    "courage": ["Be brave.", "Face it head-on.", "Embrace the risk."]
}


def generate_choices(npc_name: str, remnants: Dict[str, float], 
                    num_choices: int = 3) -> List[Dict[str, str]]:
    """
    Generate player dialogue choices based on NPC's current REMNANTS state.
    
    Args:
        npc_name: Name of the NPC
        remnants: Current REMNANTS trait dict
        num_choices: How many choices to generate
    
    Returns:
        List of choice dicts: [{"trait": str, "text": str}, ...]
    """
    
    # Sort traits by value (highest first)
    traits_sorted = sorted(remnants.items(), key=lambda x: x[1], reverse=True)
    
    choices = []
    for trait, value in traits_sorted[:num_choices]:
        if trait not in CHOICE_POOLS:
            continue
        
        pool = CHOICE_POOLS[trait]
        
        # High-confidence choice (trait > 0.7)
        if value > 0.7:
            choice_text = random.choice(pool)
        # Moderate choice (0.5-0.7)
        elif value > 0.5:
            base_choice = random.choice(pool).lower()
            choice_text = f"Perhaps {base_choice}"
        # Lower confidence (< 0.5)
        else:
            base_choice = random.choice(pool).lower()
            choice_text = f"Consider: {base_choice}"
        
        choices.append({
            "trait": trait,
            "value": round(value, 2),
            "text": choice_text
        })
    
    return choices
