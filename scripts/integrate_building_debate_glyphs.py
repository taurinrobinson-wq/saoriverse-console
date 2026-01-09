#!/usr/bin/env python3
"""
Integrate the archive building debate and love story into key glyphs.
Modifies 5 glyphs for Malrik, Elenya, and Coren to weave in:
- The shared archive building debate
- Philosophical conflict (preservation vs activation)
- Love story subtext
"""

import json
from pathlib import Path

# Path to JSON
GLYPH_JSON = Path(__file__).parent.parent / "velinor" / "markdowngameinstructions" / "Glyph_Organizer.json"

def update_glyphs():
    """Update glyphs with building debate integration."""
    
    with open(GLYPH_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find and update the 5 key glyphs
    glyph_updates = {
        24: {  # Glyph of Boundary Stone
            "location": "The Shared Archive Building (Marketplace)",
            "storyline_summary": "Malrik stands at the archive building's entrance, inscribing preservation boundaries. He argues that records must be sealed and organized—that structure is the only way to honor memory. But Elenya's voices echo from within: arguing for spiritual activation. Malrik's boundaries are firm, even rigid. The player senses his fear beneath: that if they open this space to ritual and ambiguity, the records will be lost. The glyph manifests when the player helps Malrik mark the building's preservation zones, but also recognizes the cost of his rigidity.",
            "story_seed": "Malrik and Elenya argue over how to use the newly reclaimed archive building.",
            "tone_integration": ["contemplative", "tense", "personal"],
            "remnants_integration": ["reclaimed_structure", "shared_resource", "corelink_archive"],
            "player_choices": ["support_malrik", "challenge_malrik", "mediate_tension", "observe_silently"],
            "narrative_triggers": ["archive_discovered", "elenya_arrives", "conflict_escalates"],
            "memory_fragments": ["malrik_inscription_photo.png"],
            "tags": ["boundaries", "choice", "clarity", "sovereignty", "building", "debate", "love-story", "fear", "preservation"],
            "alignment_paths": {"path_a": "Support Malrik's preservation logic", "path_b": "Question whether boundaries must be so absolute"},
            "original_storyline_text": "Malrik stands at the archive building's entrance, inscribing preservation boundaries into stone. He argues that records must be sealed and organized—that structure is the only way to honor memory. But Elenya's voices echo from within: arguing for spiritual activation. Malrik's boundaries are firm, even rigid. The player senses his fear beneath: that if they open this space to ritual and ambiguity, the records will be lost. His dedication to memory-keeping masks a deeper fear: fear of losing her vision, of watching her dismiss his life's work. The glyph manifests when the player helps Malrik mark the building's preservation zones, but recognizes the cost of his rigidity. This is sovereignty as the painful act of saying 'no,' without understanding that every 'no' pushes her further away."
        },
        23: {  # Glyph of Measured Step
            "location": "The Shared Archive Building (Inside Chambers)",
            "storyline_summary": "Malrik navigates the archive building's interior with the player, each step deliberate and measured. He catalogs, he pauses, he explains the logic of placement. Meanwhile, Elenya's presence is felt: dried flowers left on shelves, ritual marks on walls, evidence of her trying to sanctify what he's trying to organize. Malrik moves with discipline through this contested space, but the player notices where his eyes linger on her offerings. He doesn't remove them. The glyph manifests when the player moves through the building with Malrik and realizes his measured pace isn't just method—it's a way of holding her vision at arm's length while never quite letting it go.",
            "story_seed": "Malrik walks the player through the archive building, demonstrating his archival precision. The tension with Elenya's spiritual approach becomes visible.",
            "tone_integration": ["contemplative", "tense", "yearning"],
            "remnants_integration": ["reclaimed_structure", "dual_use_space", "corelink_archive"],
            "player_choices": ["follow_his_method", "ask_about_elenya", "suggest_compromise", "observe_his_choices"],
            "narrative_triggers": ["archive_interior_explored", "elenya_offerings_noticed", "malrik_hesitation_observed"],
            "memory_fragments": ["dried_flowers.png", "ritual_marks.png"],
            "tags": ["boundaries", "choice", "clarity", "sovereignty", "building", "debate", "love-story", "desire", "method"],
            "alignment_paths": {"path_a": "Affirm Malrik's archival discipline as valid", "path_b": "Point out that his method is slowly breaking him"},
            "original_storyline_text": "Malrik navigates the archive building's interior with the player, each step deliberate and measured. He catalogs, he pauses, he explains the logic of placement. But as they walk, the player sees evidence of Elenya everywhere: dried flowers left on shelves, ritual marks on walls, songs scratched into corners, spaces where she's tried to sanctify what he's trying to organize. Malrik moves with discipline through this contested space. His jaw is tight. His explanations are precise. But the player notices something: where his eyes linger on her offerings. He never removes them. In the quiet chambers, Malrik's measured step becomes visible as what it truly is: a way of loving someone while refusing to admit it. The glyph manifests when the player walks through the building and recognizes that his discipline isn't just method—it's a cage he built to contain his own longing. This is sovereignty as the power to move forward while holding someone else's vision close to your chest, even as you argue against it."
        },
        22: {  # Glyph of Held Ache (Coren)
            "location": "The Shared Archive Building (Concourse)",
            "storyline_summary": "Coren stands in the archive building's central chamber, between Malrik and Elenya. They are locked in debate: preservation vs. activation. Malrik speaks of disciplined records; Elenya speaks of spiritual belonging. Coren does not choose. Instead, she holds both truths without collapsing them into compromise. She teaches the player that co-witnessing means accepting that both people are right, and that integration requires holding the paradox. The glyph manifests when the player recognizes that Coren's gift isn't solving the conflict—it's refusing to let it fracture the city. Both visions have validity. The building can hold both.",
            "story_seed": "Coren mediates between Malrik and Elenya's competing visions for the shared archive building.",
            "tone_integration": ["contemplative", "paradoxical", "holding"],
            "remnants_integration": ["reclaimed_structure", "dual_purpose_space", "shared_resource"],
            "player_choices": ["support_malrik_or_elenya", "embrace_paradox", "mediate_with_coren", "observe_without_choosing"],
            "narrative_triggers": ["archive_building_debate", "both_sides_present", "coren_intervenes"],
            "memory_fragments": ["malrik_standing_firm.png", "elenya_arms_open.png", "coren_between_them.png"],
            "tags": ["boundaries", "choice", "clarity", "memory-loss", "sovereignty", "mediation", "paradox", "building", "debate", "integration"],
            "alignment_paths": {"path_a": "Coren's way: hold both truths simultaneously", "path_b": "Choose one vision over the other"},
            "original_storyline_text": "Coren stands in the archive building's central chamber, between Malrik and Elenya. They are locked in debate: preservation versus activation. Malrik speaks of disciplined records, of history that must be sealed against the chaos of interpretation. Elenya speaks of spiritual belonging, of community gathering in spaces that breathe with ritual and song. They are not wrong. Both are necessary. Coren does not choose sides. Instead, she holds both truths without collapsing them into false compromise. She teaches the player that mediation isn't about finding the middle ground—it's about accepting that some paradoxes cannot be resolved, only honored. The building can preserve records AND serve as a shrine. Both functions strengthen each other. The glyph manifests when the player recognizes that Coren's gift isn't solving the conflict—it's refusing to let it fracture the city. She shows that holding paradox is not weakness but the deepest strength. This is sovereignty as the power to stand between opposing truths and refuse to betray either one."
        },
        51: {  # Glyph of Covenant Flame (Elenya)
            "location": "The Shared Archive Building (Central Chamber with Shrine Space)",
            "storyline_summary": "Elenya gathers the community in the archive building's central chamber to light the Covenant Flame—a fire that will only survive through collective tending. She argues this is why the building matters: not as a sealed vault, but as a gathering place where the community tends the flame of shared memory and ritual. Each person adds fuel; each guards it against wind. But Malrik's shadow is felt: his worry that fire and records cannot coexist. Elenya's frustration is visible: her hurt that he refuses to see beauty in what she's building. The glyph manifests when the player joins the ritual and recognizes that activation isn't destruction—it's honoring memory through presence.",
            "story_seed": "Elenya transforms the archive building into a ritual space, lighting the Covenant Flame to demonstrate that spiritual use strengthens rather than threatens preservation.",
            "tone_integration": ["hopeful", "mythic", "tender", "hurt"],
            "remnants_integration": ["abandoned_rituals", "environmental_scars", "reclaimed_structure"],
            "player_choices": ["observe_or_participate", "join_or_watch", "tend_the_flame", "acknowledge_elenya_vision"],
            "narrative_triggers": ["covenant_flame_lit", "community_gathering", "elenya_explains_vision"],
            "memory_fragments": ["elenya_lighting_flame.png", "community_tending.png"],
            "tags": ["community", "interdependence", "restoration", "trust", "building", "ritual", "love-story", "activation", "covenant"],
            "alignment_paths": {"path_a": "Support Elenya's vision of shared activation", "path_b": "Question whether the building can truly serve both purposes"},
            "original_storyline_text": "Elenya gathers the community in the archive building's central chamber to light the Covenant Flame—a fire that will only survive through collective tending. She argues passionately: this is why the building matters. Not as a sealed vault of dead records, but as a living gathering place where the community tends the flame of shared memory and ritual. Each person adds fuel; each guards it against wind. Each shares its warmth. But Malrik's shadow is felt throughout: his worry that fire and paper cannot coexist, his conviction that spiritual use will compromise the records. And Elenya's hurt is visible too: the way her shoulders tense, the way she avoids looking at him. She's tried so hard to show him that her vision doesn't diminish his. That activation and preservation can strengthen each other. The glyph manifests when the player joins the ritual and recognizes that Elenya's activation isn't destruction—it's the deepest form of honoring memory: through presence, through gathering, through the willingness to tend what matters collectively. This is trust as the faith that shared care makes things sacred, not fragile."
        },
        52: {  # Glyph of Shared Survival (Elenya)
            "location": "The Shared Archive Building (During Crisis or Time-Sharing Arrangement)",
            "storyline_summary": "After the building debate deepens, Elenya proposes a survival rite: both communities must tend the space together. Some hours belong to the archive keepers; some hours belong to the shrine-tenders. Each must contribute their best effort; each must rely on the other's care. The player participates in this negotiated coexistence, watching Malrik and Elenya navigate mutual dependence. There are moments of resistance, moments of grace. The glyph manifests when the player recognizes that Shared Survival means giving up the fantasy of total control—both must sacrifice for the space to live.",
            "story_seed": "Elenya and Malrik negotiate a shared use agreement for the archive building, requiring both communities to invest in mutual care.",
            "tone_integration": ["hopeful", "mythic", "difficult", "mature"],
            "remnants_integration": ["abandoned_rituals", "environmental_scars", "reclaimed_structure", "dual_purpose_space"],
            "player_choices": ["observe_or_participate", "help_negotiate_terms", "tend_shared_space", "witness_both_communities"],
            "narrative_triggers": ["agreement_negotiated", "shared_tending_begins", "both_sides_contributing"],
            "memory_fragments": ["shared_schedule.png", "both_communities_tending.png"],
            "tags": ["community", "interdependence", "restoration", "trust", "building", "shared_use", "negotiation", "sacrifice", "integration"],
            "alignment_paths": {"path_a": "Support the time-sharing arrangement", "path_b": "Question whether integration can truly work"},
            "original_storyline_text": "After the building debate deepens and neither side will concede, Elenya proposes a survival rite: both communities must learn to tend the space together. Some hours belong to the archive keepers (sealed, quiet, ordered); some hours belong to the shrine-tenders (open, vocal, ritualized). Each community must contribute their best effort; each must genuinely rely on the other's care and respect. The player participates in this negotiated coexistence, watching Malrik and Elenya navigate the strange alchemy of mutual dependence. There are moments of resistance—a shelf moved without permission, a ritual disrupting carefully organized sections. There are moments of grace—Malrik preserving a sacred space for Elenya's ceremonies, Elenya protecting an archive section when a new collapse threatens. The glyph manifests when the player recognizes that Shared Survival means surrendering the fantasy of total control. Both must sacrifice; both must trust. Neither vision is diminished by sharing space with the other. If anything, they deepen each other. This is the most mature form of integration: not compromise, but genuine interdependence built through daily, visible acts of care."
        }
    }
    
    updated_count = 0
    for glyph in data["glyphs"]:
        if glyph["id"] in glyph_updates:
            updates = glyph_updates[glyph["id"]]
            for key, value in updates.items():
                glyph[key] = value
            updated_count += 1
            print(f"✓ Updated glyph {glyph['id']}: {glyph['glyph_name']}")
    
    # Write back to file
    with open(GLYPH_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Successfully updated {updated_count} glyphs with building debate integration")
    print(f"✓ File saved: {GLYPH_JSON}")

if __name__ == "__main__":
    update_glyphs()
