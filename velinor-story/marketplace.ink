// ============================================================================
// MARKETPLACE: Hub Scenes & Locations
// ============================================================================
//
// The marketplace is the central hub where players encounter NPCs,
// make choices, and gradually build understanding of the world.
//
// Locations:
//   - Marketplace Hub (central decision point)
//   - Market Stalls (commerce, Ravi)
//   - Shrine Area (spiritual space, Nordia/Sealina)
//   - Collapsed Building (physical reminder of collapse)
//   - Archive Entrance (deeper dive into knowledge)
//
// ============================================================================

=== marketplace_hub ===
~ marketplace_visited = true

You stand in the heart of Velhara's marketplace.

The space is organized despite the ruins around it. Merchants have set up stalls, children play, people gather in small circles. There's an intentionality to it—this community has chosen to rebuild here, together.

Several paths diverge before you:

* [Market Stalls (Ravi's territory)] -> market_stalls
* [Shrine Area (spiritual center)] -> shrine_area
* [The Collapsed Building (reminder)] -> collapsed_building
* [Archive Entrance (knowledge)] -> archive_entrance
* [Rest and reflect] -> marketplace_rest
* [Check my emotional state] -> marketplace_self_check

=== market_stalls ===
You approach the market stalls where Ravi arranges bright bolts of fabric.

The air smells like earth, food, and the leather goods Nima crafts. This is the heart of practical survival and care.

Ravi looks up with warmth.

* [Talk to Ravi] -> ravi_dialogue
* [Look around the stalls] -> stalls_exploration
* [Return to hub] -> marketplace_hub

=== stalls_exploration ===
You walk through the marketplace, observing.

Merchants sell: preserved food, hand-crafted tools, healing herbs, fabric, leather goods. The prices are negotiated based on need, not scarcity. This marketplace runs on reciprocity, not profit.

Everyone seems to know each other. Kids call out to adults by name. Adults stop to help with heavy loads.

~ adjust_tone("empathy", 3)
~ adjust_tone("observation", 2)
~ coherence = calculate_coherence()

"Beautiful, isn't it?" 

You turn to see Rasha, a younger person with bright eyes.

"Ravi created this. Built it from nothing after the collapse. Everyone came because they needed each other."

* [Ask about pre-collapse times] -> rasha_memories
* [Return to stalls] -> market_stalls

=== rasha_memories ===
Rasha's expression grows distant.

"I was young. I remember the Corelink—the feeling of being connected to everyone at once. It felt safe."

"Then it broke."

"And we learned that safety doesn't come from systems. It comes from showing up. From choosing each other."

Rasha smiles.

"That's better, I think."

~ adjust_tone("narrative_presence", 5)
~ cascade_influence("ravi", 0.1)  // Learning from Ravi's apprentice

* [Return to marketplace] -> marketplace_hub

=== shrine_area ===
You enter a quieter space—the shrine area.

Even in ruins, humans create sacred spaces. Here, flowers grow from cracks in stone. A circular clearing with benches suggests meditation and gathering.

An older woman tends the space: Nordia, the grief transformer.

* [Approach Nordia] -> nordia_encounter
* [Sit in silence] -> shrine_silence
* [Return to hub] -> marketplace_hub

=== nordia_encounter ===
Nordia looks up as you step into her space.

"Welcome," she says simply. "This place holds grief."

She gestures to flowers blooming through stone.

"Grief and life, together. Not one then the other. Both at once."

* [Tell her you're grieving something] 
    ~ adjust_tone("empathy", 8)
    ~ adjust_tone("observation", 6)
    ~ coherence = calculate_coherence()
    -> nordia_witness
    
* [Observe quietly]
    ~ adjust_tone("observation", 5)
    -> shrine_silence

=== nordia_witness ===
Nordia listens without trying to fix anything.

"Grief is love extended into time," she says finally. "The more you grieve, the more you loved."

She returns to her flowers.

"Your grief is noble. Carry it."

~ cascade_influence("nordia", 0.15)

* [Return to shrine] -> shrine_area

=== shrine_silence ===
You sit. The sounds of the marketplace fade. You hear wind, leaves, water somewhere.

Your mind quiets. Your TONE stats shift slightly toward balance.

~ adjust_tone("observation", 4)
~ adjust_tone("narrative_presence", 3)
~ coherence = calculate_coherence()

After a while, you feel ready to continue.

* [Return to marketplace] -> marketplace_hub

=== collapsed_building ===
You approach the structure that first caught your attention.

A building—three stories—has collapsed partially. But people are working on it. Clearing rubble. Salvaging materials. Planning reconstruction.

This is not abandoned. It's being transformed.

A woman with engineering focus oversees the work: Vera (salvage leader).

* [Help with the work]
    ~ adjust_tone("narrative_presence", 5)
    ~ adjust_tone("empathy", 5)
    ~ coherence = calculate_coherence()
    -> collapsed_help
    
* [Question the building's stability]
    ~ adjust_tone("observation", 6)
    -> collapsed_question
    
* [Observe the process]
    ~ adjust_tone("observation", 4)
    -> collapsed_observe

=== collapsed_help ===
You work alongside Vera's team, moving rubble, organizing salvage.

It's hard work. But it's also clarifying—taking something broken and making it useful again.

"Thank you," Vera says as you work. "This building will become a school. Kids will learn here instead of buildings standing empty."

~ collapse_witnessed = true

* [That's powerful] -> marketplace_hub
* [Ask about the original collapse] -> vera_history

=== collapsed_question ===
"Fair question," Vera says, not defensive. "We're not rebuilding exactly. We're redesigning. Stronger foundation. Better weight distribution. Not repeating the same structure that failed."

She looks at the building with affection.

"Systems fail. We learn. We build differently."

~ collapse_witnessed = true

* [Continue working] -> marketplace_hub
* [Ask more] -> vera_systems

=== collapsed_observe ===
You watch the team work. There's rhythm to it. People move with purpose. Equipment is maintained. Progress is tracked.

This is not chaotic. This is intentional reconstruction.

~ collapse_witnessed = true

* [Ask Vera about the process] -> vera_systems
* [Return to hub] -> marketplace_hub

=== vera_history ===
Vera sits down, taking a water break.

"The original building was designed in the early Corelink era. Efficiency over resilience. We optimized for cost, not stability."

She looks at the ruins with regret.

"When the system failed, the infrastructure failed. Both literally and mechanically. We learned the hard way."

* [And now you're rebuilding?] -> vera_systems
* [Return to marketplace] -> marketplace_hub

=== vera_systems ===
"Yes," Vera says. "But differently. We're teaching people to understand systems—how they fail, what makes them resilient, how to maintain them."

She points to blueprints on the ground.

"That's the real infrastructure. Not the building. The knowledge. The practice. The choice to maintain it."

* [That's wise] 
    ~ adjust_tone("narrative_presence", 6)
    -> marketplace_hub
    
* [Return to marketplace] -> marketplace_hub

=== archive_entrance ===
You stand at what looks like a library entrance—partially buried in rubble, but clearly the Archive.

The door is guarded by someone watchful: Malrik, the archivist.

He looks at you with intensity.

"Do you come seeking knowledge?" he asks. "Or do you come to understand why knowledge matters?"

* [Both]
    ~ adjust_tone("observation", 5)
    ~ adjust_tone("observation", 3)
    -> malrik_dialogue
    
* [I want to know what was lost]
    ~ adjust_tone("empathy", 5)
    -> malrik_compassion
    
* [I don't know yet]
    ~ adjust_tone("awareness", 6)
    -> malrik_uncertain

=== malrik_dialogue ===
Malrik nods with approval.

"Good. Knowledge without care becomes coldness. Care without knowledge becomes folly."

He gestures to the archive.

"Inside, we preserve the records of what Velhara was. Not to repeat it—to learn from it."

* [Can I enter?] -> archive_explore
* [Return to marketplace] -> marketplace_hub

=== malrik_compassion ===
Malrik's expression softens.

"Yes. Much was lost. Knowledge, people, relationships preserved by the Corelink."

He pauses.

"But something was gained too. The choice to remember consciously. The work of preservation instead of automatic recording."

~ cascade_influence("malrik", 0.1)

* [I want to understand what's saved] -> archive_explore
* [Return] -> marketplace_hub

=== malrik_uncertain ===
"Then you're in the right place," Malrik says. "Archives are where we find out who we are by learning who we were."

* [Can I explore?] -> archive_explore
* [Return to marketplace] -> marketplace_hub

=== archive_explore ===
You enter the archive.

Shelves line the walls—records, books, recovered documents. Some are newer (handwritten since the collapse). Some are ancient (pre-Corelink paper).

People work here carefully: Nordia cataloging, Sealina singing songs to preserve them, young scholars copying texts by hand.

This is not just a library. It's a testimony office. A place where knowledge is treated as sacred.

* [Talk to the workers] -> archive_workers
* [Browse the records] -> archive_browse
* [Return to marketplace] -> marketplace_hub

=== archive_workers ===
You find Sealina—the songs keeper—recording oral histories.

"Every voice that remembers something is an archive," she says. "We're trying to gather them all before they're lost."

* [Listen to a story] -> sealina_story
* [Return to marketplace] -> marketplace_hub

=== sealina_story ===
Sealina sings a song—old and beautiful and mournful.

"This is the song of the collapse. We sing it so we remember without letting the remembering destroy us."

~ coherence = calculate_coherence()

The melody hangs with you.

* [Return to marketplace] -> marketplace_hub

=== archive_browse ===
You look through the records.

Pre-collapse photographs. Documents about the Corelink design. Letters from people who died in the disaster. New records about rebuilding.

History. Real, messy history.

~ adjust_tone("awareness", 5)

* [Return to marketplace] -> marketplace_hub

=== marketplace_rest ===
You find a quiet corner of the marketplace and sit.

The buzz of commerce and conversation fades to background. You feel the weight of the day. The weight of understanding.

~ adjust_tone("awareness", 3)
~ adjust_tone("integration", 2)
~ coherence = calculate_coherence()

A moment of rest. A moment of integration.

* [Continue] -> marketplace_hub

=== marketplace_self_check ===
You pause and take inventory of your emotional state.

Current TONE Stats:
  Trust: {tone_trust}
  Observation: {tone_observation}
  Empathy: {tone_empathy}
  Narrative Presence: {tone_narrative_presence}
  
Coherence: {coherence}

{describe_coherence_level()}

Influence Map:
  Saori: {influence_saori}
  Ravi: {influence_ravi}
  Nima: {influence_nima}
  Malrik: {influence_malrik}

Glyphs Revealed: {glyphs_revealed}

* [Continue marketplace exploration] -> marketplace_hub
* [End this session and view final stats] -> STORY_END
