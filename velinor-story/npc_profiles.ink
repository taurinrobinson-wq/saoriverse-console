// ============================================================================
// NPC PROFILES: Dialogue Blocks for Saori, Ravi, Nima
// ============================================================================
//
// Each NPC has multiple dialogue variations based on:
//   - Player's TONE stats
//   - Coherence level
//   - Influence with this NPC
//   - Story progression flags
//
// ============================================================================

// ============================================================================
// SAORI: Co-Architect, Guilt-Driven
// She's trying to restart the Corelink system (obsessively)
// Appears at story start
// ============================================================================

=== saori_encounter ===
You wake in the ruins of Velhara, disoriented.

The city is broken. Collapsed structures everywhere. But something is different—there's no electricity hum, no ambient consciousness. The Corelink is silent.

A figure emerges from the shadows: an older woman, face weathered by decades of burden.

-> saori_intro

=== saori_intro ===
"You're awake," she says. No surprise in her voice, only efficiency. "I've been waiting."

She extends a small device—crystalline, warm to the touch. A codex.

"I'm Saori. Twenty-five years ago, my partner Velinor and I built the Corelink. We tried to preserve emotional memory across humanity. It was supposed to heal us."

She pauses. "It destroyed us instead."

* [Listen carefully] 
    ~ adjust_tone("observation", 5)
    ~ coherence = calculate_coherence()
    -> saori_explains
    
* [Question her motives]
    ~ adjust_tone("observation", 8)
    ~ coherence = calculate_coherence()
    -> saori_defensive
    
* [Feel the weight of this]
    ~ adjust_tone("empathy", 8)
    ~ coherence = calculate_coherence()
    -> saori_seen

=== saori_explains ===
Saori nods as you settle into that quiet listening space.

"The Corelink overloaded. Millions died when the system tried to unify everyone's emotions at once. Velinor sacrificed herself. She shattered, actually. Broke herself into seventy emotional fragments we call glyphs. It's the only reason anyone survived."

She holds the codex closer to you.

"I need someone to help me rebuild. To understand what went wrong. The glyphs are scattered through Velhara now, and if we can gather them, we can restart safely."

* [I'll help you rebuild]
    ~ cascade_influence("saori", 0.15)
    ~ adjust_tone("narrative_presence", 5)
    ~ coherence = calculate_coherence()
    -> saori_gratitude
    
* [First, I need to understand the city]
    ~ cascade_influence("saori", 0.05)
    -> saori_skeptical_ok

=== saori_defensive ===
"Fair question," she says, not defensively. Just factual. "I failed once before. Velinor warned me to wait. I didn't. I pushed for unification without consent."

Her hands shake slightly.

"I'm not asking for trust. I'm asking for help. If you want to leave, go. But the glyphs are still scattered. The city is still fractured."

* [I'll stay and learn]
    ~ cascade_influence("saori", 0.1)
    -> saori_relief
    
* [You seem to blame yourself]
    ~ adjust_tone("empathy", 6)
    ~ adjust_tone("observation", 4)
    ~ coherence = calculate_coherence()
    ~ cascade_influence("saori", 0.2)
    -> saori_breaks

=== saori_seen ===
Saori's expression shifts. For a moment, her efficiency cracks.

"Thank you," she says quietly. "No one has said that in a very long time."

She takes a breath, steadies herself.

"Velinor is still in the Corelink system, fragmented. I can hear her sometimes in the machinery. She's been waiting for someone to help me. To help everyone."

* [Then I'll help]
    ~ cascade_influence("saori", 0.2)
    -> saori_partnership
    
* [What do you need specifically?]
    ~ adjust_tone("observation", 8)
    ~ coherence = calculate_coherence()
    -> saori_mission

=== saori_gratitude ===
Relief washes across her face.

"Thank you. That means—" She stops herself. "No. There's no time for sentiment. The city is unstable. People are struggling without the Corelink's support. We need to move."

She stands, offering her hand.

"Come. The marketplace is where people still gather. That's where we start."

~ has_met_saori = true
~ marketplace_visited = false

* [Follow her] -> marketplace_hub

=== saori_relief ===
"That's all I can ask," Saori says.

She looks at you with something like hope, though grief still lingers at the edges of her eyes.

"The codex will guide you. It shows you the glyphs as you encounter them. Each one is a piece of Velinor's consciousness—her understanding of emotion. If you can attune to them, you'll understand how to synthesize what's broken."

* [I'm ready] -> marketplace_hub

=== saori_breaks ===
She sits down heavily, and for the first time, you see the weight she carries.

"I do blame myself. Every day. Twenty-five years of it." Her voice wavers. "Velinor told me no. And I pushed anyway. I thought I knew better."

She looks up at you.

"The glyphs—they're fragments of her consciousness, trying to tell us something. What went wrong. What we lost. What we might become."

* [That's why you need to rebuild] -> saori_partnership
* [Maybe it's not about rebuilding] -> saori_alternative

=== saori_partnership ===
Saori stands, steadied by your understanding.

"Yes. Exactly. To restore what we can. To honor what was sacrificed."

She extends the codex.

"You'll understand as you go. The glyphs will reveal themselves to you, each one carrying a piece of wisdom."

-> marketplace_hub

=== saori_mission ===
"The glyphs," Saori says clearly. "We need to gather them. Understand them. And—if we can—use what Velinor learned to rebuild the Corelink, but differently. Safely. With consent this time."

She hands you the codex.

"The marketplace is where that journey begins."

-> marketplace_hub

=== saori_alternative ===
~ adjust_tone("observation", 5)
~ adjust_tone("narrative_presence", 10)
~ coherence = calculate_coherence()

Saori looks at you with new attention.

"Go on."

"Maybe..." you say slowly, "...the glyphs aren't asking us to rebuild the system. Maybe they're asking us to learn from its failure. To understand what Velinor sacrificed, and what humanity needs to become without technological mediation."

Saori is quiet for a long moment.

"That's..." she pauses. "That's different from what I've been planning."

* [We should explore both options] 
    -> saori_both_paths

=== saori_both_paths ===
~ coherence = calculate_coherence()

"Yes," Saori says finally. "Yes, we should."

She looks almost peaceful for the first time.

"Come. The marketplace will show us what's possible."

-> marketplace_hub

=== saori_skeptical_ok ===
"The city will teach you," Saori says. "Come when you're ready."

~ has_met_saori = true

-> marketplace_hub

// ============================================================================
// RAVI: Marketplace Merchant, Grieving Parent
// ============================================================================

=== ravi_dialogue ===
{has_met_ravi:
    -> ravi_return
- else:
    -> ravi_first_meeting
}

=== ravi_first_meeting ===
You find the marketplace surprisingly alive. Vendors are arranging goods, children playing between stalls. The community is functioning, even without the Corelink.

A tall figure is organizing bright bolts of fabric. He looks up as you approach. His smile is warm, but there's a weight beneath it.

"Welcome," he says. "I'm Ravi. I run the marketplace. You're new here."

~ has_met_ravi = true

* [I'm looking for something]
    ~ adjust_tone("observation", 2)
    -> ravi_guide
    
* [Tell me about this place]
    ~ adjust_tone("empathy", 3)
    -> ravi_explain
    
* [You seem sad]
    ~ adjust_tone("empathy", 5)
    ~ adjust_tone("observation", 5)
    ~ coherence = calculate_coherence()
    -> ravi_vulnerable

=== ravi_guide ===
Ravi nods, ready to help.

"I can show you where things are. What do you need? Food? Tools? Information?"

* [I'm trying to understand what happened here]
    ~ cascade_influence("ravi", 0.1)
    -> ravi_history
    
* [I'm with Saori]
    ~ cascade_influence("ravi", 0.15)
    -> ravi_saori_reaction

=== ravi_explain ===
"This marketplace," Ravi gestures around, "is what kept us human when the Corelink failed."

He picks up a piece of fabric—soft blue.

"My daughter Ophina loved colors like this. When the system went down, we all had to learn how to be together without the connection net. And here... here we found each other. Slowly."

He looks at you.

"That's the real strength of Velhara. Not the technology. The people. The care."

* [That's beautiful]
    ~ cascade_influence("ravi", 0.2)
    ~ adjust_tone("empathy", 8)
    ~ coherence = calculate_coherence()
    ~ glyphs_revealed = glyphs_revealed + 1
    ~ promise_held_unlocked = true
    -> ravi_glyph_moment
    
* [People are resilient, but something was lost]
    ~ cascade_influence("ravi", 0.1)
    -> ravi_acknowledge_loss

=== ravi_history ===
Ravi sits on a bench, inviting you to do the same.

"Twenty-five years ago, when the Corelink overloaded, we felt connected to everyone at once. Then it broke, and that connection snapped. Millions died. The city collapsed."

He pauses.

"We're still learning what it means to choose connection instead of being forced into it."

* [How do you live with that?]
    ~ adjust_tone("empathy", 8)
    -> ravi_resilience

=== ravi_saori_reaction ===
Ravi's expression becomes more careful.

"Saori," he says. "I haven't seen her in years. She was living underground, trying to fix what broke."

He looks at you with new intensity.

"Tell me—is she trying to restart it? The Corelink?"

* [I think so]
    ~ adjust_tone("observation", 3)
    -> ravi_worried
    
* [She's looking for the glyphs]
    ~ adjust_tone("observation", 4)
    -> ravi_glyphs_question

=== ravi_vulnerable ===
Ravi's hands pause on the fabric.

"I—yes. Yes, I am," he says quietly.

He sits down, and after a moment, so do you.

"My daughter Ophina... she died when the Corelink failed. She was connected to it more deeply than most. When it overloaded..."

He trails off. Grief is plain on his face.

"It's been twenty-five years, and I still measure time from that moment. Before she died. After."

* [I'm sorry]
    ~ adjust_tone("empathy", 10)
    ~ coherence = calculate_coherence()
    -> ravi_connection
    
* [That must have been devastating]
    ~ adjust_tone("empathy", 8)
    ~ adjust_tone("observation", 5)
    ~ coherence = calculate_coherence()
    -> ravi_deepens

=== ravi_glyph_moment ===
As you listen to Ravi speak about the marketplace, about choosing connection, you feel something shift.

A glyph appears in your peripheral vision, soft and glowing: ◈ (interlocking circles, soft blue).

"The Promise Held," Ravi says, as if seeing the same thing. "That's what we hold onto. Each other. Steadily."

-> ravi_closing

=== ravi_acknowledge_loss ===
"True," Ravi agrees. "The Corelink was supposed to help us know each other. Instead, it became a crutch. And when it broke..."

He looks at the bright fabrics.

"We had to learn to weave connection ourselves again. Without the net. Just... attention. Presence. Choice."

-> ravi_closing

=== ravi_resilience ===
Ravi looks up at you, and you see it—the way grief becomes wisdom.

"You grieve what was lost. You honor the person. And then... you notice that people are still here. Still trying. Still caring."

He gestures to the marketplace.

"Nima, my partner, helped me through it. Just by being present. Not trying to fix it. Just... being there."

* [Is she here?]
    ~ adjust_tone("empathy", 3)
    -> ravi_introduces_nima

=== ravi_worried ===
"Be careful with Saori," Ravi says. His tone is protective, but not unkind. "She comes from a good place, but her guilt runs deep. Deep enough to break things again."

He looks directly at you.

"The glyphs—if that's what she's after—there might be a reason they scattered instead of staying whole."

-> ravi_closing

=== ravi_glyphs_question ===
Ravi nods thoughtfully.

"The emotional fragments. Yes. In a way, that makes sense. When Velinor shattered, she probably fragmented for a reason. To distribute understanding instead of concentrating it."

He looks at you more carefully.

"If Saori gathers them, make sure you understand what she plans to do with them."

-> ravi_closing

=== ravi_connection ===
Your empathy reaches him, and Ravi's grief settles into something gentler.

"Thank you," he says. "I don't carry it alone anymore, but it's still heavy."

He stands and extends his hand.

"Come. I want you to meet Nima. She lost Ophina too, in her own way. And she's learned something about holding grief alongside joy."

~ cascade_influence("ravi", 0.15)

-> ravi_introduces_nima

=== ravi_deepens ===
Ravi nods slowly, seeing that you understand something real.

"Yes. Devastating. But also... it was the catalyst for everything good that came after. Nima and I learned to really look at each other. The community had to choose to gather, not be forced together."

He pauses.

"Loss taught us the value of what we have."

* [I want to meet Nima]
    ~ cascade_influence("ravi", 0.1)
    -> ravi_introduces_nima

=== ravi_introduces_nima ===
"Come with me," Ravi says.

He leads you through the market to a quiet corner where a sharp-eyed woman is working with leather goods. She looks up, assessing you quickly.

"This is Nima. My partner. And my anchor."

Nima studies you carefully.

"So," Nima says. "You're with Ravi. That means something."

-> nima_dialogue

=== ravi_closing ===
Ravi smiles—a small, genuine thing.

"Thank you for listening. That matters more than you know."

* [I should explore the marketplace] -> marketplace_hub
* [Tell me more about the glyphs] -> ravi_glyphs_question
* [Can I meet Nima?] -> ravi_introduces_nima

=== ravi_return ===
Ravi waves as you approach again.

"Welcome back," he says warmly. "You're becoming part of the marketplace now."

* [How are you feeling today?]
    -> ravi_check_in
    
* [I want to see Nima]
    -> nima_dialogue

=== ravi_check_in ===
~ temp tone_shift = (tone_empathy - tone_observation) / 2
Ravi considers you.

{influence_ravi >= 0.7:
    "Better, actually. Having you here helps."
- else:
    "Day by day. That's all any of us can manage."
}

* [Back] -> marketplace_hub

// ============================================================================
// NIMA: Ravi's Partner, Warrior & Guardian
// ============================================================================

=== nima_dialogue ===
{has_met_nima:
    -> nima_return
- else:
    -> nima_first_meeting
}

=== nima_first_meeting ===
Nima's eyes are sharp, assessing. She doesn't smile immediately.

"I'm Nima," she says. "I work security for the marketplace. Which means I notice when people are trustworthy or not."

She pauses.

"I'm still deciding about you."

~ has_met_nima = true

* [I'm here to help, if I can]
    ~ adjust_tone("narrative_presence", 5)
    ~ adjust_tone("empathy", 3)
    -> nima_cautious_open
    
* [I don't need your approval]
    ~ adjust_tone("observation", 8)
    -> nima_challenged
    
* [Tell me what you see]
    ~ adjust_tone("observation", 8)
    -> nima_reads_you

=== nima_cautious_open ===
Nima relaxes slightly.

"At least you're honest. Ravi sees the best in everyone. I try to see what's actually there."

She extends her hand.

"If you're with Saori, and Ravi trusts you, then I'll give you a chance."

* [Thank you]
    ~ cascade_influence("nima", 0.1)
    ~ adjust_tone("empathy", 3)
    -> nima_backstory
    
* [I appreciate the cautious trust]
    ~ cascade_influence("nima", 0.15)
    ~ adjust_tone("observation", 3)
    -> nima_honest_beginning

=== nima_challenged ===
Nima smirks—not unkind, but testing.

"Good. You shouldn't need it. Approval is just a comfort."

She leans against her workbench.

"So tell me then—what are you actually doing here? Not the easy answer. The real one."

* [Trying to understand what happened]
    ~ adjust_tone("observation", 6)
    ~ adjust_tone("empathy", 4)
    ~ coherence = calculate_coherence()
    -> nima_respects_honesty
    
* [I'm helping Saori rebuild]
    ~ adjust_tone("narrative_presence", 3)
    -> nima_rebuilding_reaction

=== nima_reads_you ===
Nima studies you carefully.

"You're grieving something," she says. "Not recently. Older. And you're learning how to hold it without it consuming you."

She nods once.

"That's mature. Ravi was right about you."

~ cascade_influence("nima", 0.2)

* [You can tell all that from looking?]
    ~ adjust_tone("observation", 5)
    -> nima_explains
    
* [I lost someone too]
    ~ adjust_tone("empathy", 8)
    -> nima_shared_sorrow

=== nima_backstory ===
"We lost our daughter," Nima says. Not soft, just factual. "Ophina. When the Corelink crashed. She was connected to it more deeply. When it overloaded..."

She's quiet for a moment.

"Ravi and I grieved differently. He looked inward. I looked outward—to protection, to making sure no one else lost someone."

* [That's why you're careful about who enters]
    ~ adjust_tone("empathy", 8)
    -> nima_protective
    
* [You're still grieving]
    ~ adjust_tone("observation", 8)
    ~ coherence = calculate_coherence()
    -> nima_grief_ongoing

=== nima_honest_beginning ===
"That's fair," Nima says. She actually smiles now, small but genuine. "We can work with that."

She gestures toward Ravi.

"He told you about Ophina?"

* [He did]
    ~ adjust_tone("empathy", 4)
    -> nima_backstory
    
* [Your daughter]
    ~ adjust_tone("empathy", 8)
    ~ adjust_tone("observation", 4)
    ~ coherence = calculate_coherence()
    -> nima_shared_sorrow

=== nima_respects_honesty ===
Nima nods—respect in her sharp eyes.

"Understanding. Good. Better than trying to fix things."

She softens infinitesimally.

"You can help. Come back when you know more. We'll talk then."

-> nima_closing

=== nima_rebuilding_reaction ===
Nima's expression hardens slightly.

"Rebuilding with Saori," she repeats. "Be careful that you're not just rebuilding the same mistake."

She's not hostile, just protective.

"The Corelink broke because of how it was built. Saori wants to fix it. But maybe it needed to break."

* [That's why I need to understand]
    ~ adjust_tone("observation", 6)
    -> nima_understanding
    
* [Maybe you're right]
    ~ adjust_tone("narrative_presence", 5)
    -> nima_alliance

=== nima_explains ===
"My partner lost a daughter to the Corelink," Nima says. "And I learned to read grief. To see what people are trying to hide or carry alone."

She looks at you directly.

"You're learning something hard about yourself. And you're doing it without needing to fix it right away. That's strength."

-> nima_closing

=== nima_shared_sorrow ===
Nima's expression opens—grief meeting grief.

"Then you understand," she says. "That it's not one moment of loss. It's decades of carrying the shape of them. The weight."

She pauses.

"But also... it becomes lighter. Somehow. When you keep living with it instead of trying to make it go away."

~ cascade_influence("nima", 0.2)

* [How did you learn that?]
    -> nima_resilience

=== nima_protective ===
"Yes," Nima says simply. "The marketplace is our community now. I protect it because nothing else is protecting us."

She looks at you with intensity.

"If you're going to move through this city with Saori, gathering things, changing things—you need to understand that every choice ripples through people like us."

-> nima_closing

=== nima_grief_ongoing ===
Nima is quiet.

"Yes," she finally says. "Twenty-five years later, and I still wake up some mornings and think: Ophina should be here. She should be grown now. She should be making her own choices."

She looks up.

"But then I look around and see the community we've built instead. And I think: Maybe this is what grief becomes when you don't try to heal too fast."

-> nima_closing

=== nima_understanding ===
"Yes," Nima agrees. "You understand things before trying to fix them. That's rare."

She extends her hand.

"When you know more, come back. We'll know what to do next."

~ cascade_influence("nima", 0.15)

-> nima_closing

=== nima_alliance ===
Nima nods—something like relief in her expression.

"Good. We need more people thinking clearly about what we're doing."

She turns back to her work, but with less guardedness.

"Stay safe out there."

-> nima_closing

=== nima_resilience ===
"Ravi," Nima says simply. "He taught me that grief doesn't require fixing. Just... presence. Attention. Love."

She looks back at her work—leather goods, practical and beautiful.

"Every thing I make is stronger for the space Ophina left."

-> nima_closing

=== nima_closing ===
Nima returns to her work, but you feel less like an outsider now.

* [I should continue exploring] -> marketplace_hub
* [Return to Ravi] -> ravi_dialogue
* [Leave the marketplace] -> STORY_END

=== nima_return ===
Nima looks up as you approach.

"You're back," she says. It might be approval.

{influence_nima >= 0.7:
    "I'm starting to trust you."
    
    * [That means something] -> nima_closing
}

* [Back to work] -> nima_closing
