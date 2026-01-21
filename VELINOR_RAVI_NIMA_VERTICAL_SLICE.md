# VELINOR_RAVI_NIMA_VERTICAL_SLICE.md

**The First Complete Vertical Slice — Ravi & Nima Arc (Playable End-to-End)**

**Status:** Specification for immediate execution  
**Timeline:** 2-3 weeks of focused work  
**Scope:** Complete, playable arc with stable UI, backend, and story progression  
**Exit Criteria:** Playable end-to-end with 3+ playthroughs validated

---

## 🎬 Arc Overview

### What is the Ravi & Nima Arc?

This is a **complete emotional journey** with two NPCs (Ravi & Nima) that encompasses:
- Story discovery (who are they, why do they matter?)
- Emotional crisis (the thing that breaks them)
- Player influence (how do your choices shape their fate?)
- Glyph revelation (glyphs appear at emotional peaks)
- Transcendence moment (first glimpse of Velinor itself)

### Story Structure

```
ACT 1: MEETING & DISCOVERY
  Passages: Intro, marketplace encounter, backstory reveal
  Glyphs: First hints of Sorrow
  Player Goals: Learn who Ravi & Nima are, build initial trust

ACT 2: OPHINA BACKSTORY
  Passages: Nima reveals Ophina's death, Ravi's guilt surfaces
  Glyphs: Sorrow resolves, Remembrance emerges
  Player Goals: Emotional witness, influence their grief

ACT 3: TRIGLYPH CHAMBER
  Passages: Journey to chamber, boss encounter (emotional or literal)
  Glyphs: Remembrance deepens, Legacy begins
  Player Goals: Navigate crisis, make emotional choice

ACT 4: TRANSCENDENCE MOMENT
  Passages: Glyph console activation, first Velinor reveal
  Glyphs: Legacy completes, Transcendence glyph appears
  Player Goals: Experience the game's metaphysical core

ACT 5: RESOLUTION & INTEGRATION
  Passages: Ravi & Nima transformed, their influence locked
  Glyphs: All 3 glyphs now fully revealed (tier1, tier2, tier3)
  Player Goals: See consequences, move forward changed
```

### Arc Length & Pacing

- **Total Passages:** 18-22 passages (not including branching)
- **Total Choices:** 8-12 decision points (high consequence)
- **Play Time:** ~25-30 minutes (single playthrough)
- **Ravi Lines:** 25-30 unique dialogue pieces
- **Nima Lines:** 25-30 unique dialogue pieces
- **Glyphs:** 3 total (Sorrow, Remembrance, Legacy)

---

## 📖 Story Specification

### ACT 1: Meeting & Discovery

**Passage 1.1: Marketplace Intro**
- **Context:** Player enters marketplace, phase 2 beginning
- **NPC Present:** Ravi (merchant, unsettled)
- **Player State:** Empathy 50, Skepticism 50, Integration 50, Awareness 50 (default)
- **Dialogue Trigger:** Ravi notices player, calls out
- **Ravi Line Option 1 (High Empathy):**
  > "You. You have the look of someone who listens. We need someone who listens."
- **Ravi Line Option 2 (High Skepticism):**
  > "What are you looking at? Unless you can help, keep moving."
- **Glyph Reference:** Soft blue shimmer behind Ravi (first hint of Sorrow - not named yet)
- **Passage Ends:** Player chooses to engage or disengage

**Choice 1.1a: Engage with Ravi**
- **Text:** "Tell me what you need"
- **Consequence:** +15 Empathy, Ravi's influence +0.3
- **Next Passage:** 1.2

**Choice 1.1b: Keep Moving**
- **Text:** "Not my problem"
- **Consequence:** +10 Skepticism, Ravi's influence 0 (locked at lower starting point)
- **Next Passage:** 1.3 (Nima approach instead)

---

**Passage 1.2: Ravi's Burden** (If engaged)
- **Context:** Ravi pulls player aside, marketplace crowd ignored
- **NPC Present:** Ravi (agitated, desperate)
- **Dialogue:**
  > "My partner, Nima... she lost someone. Someone she loved more than anything. Ophina. I..." [pause] "I should have stopped what was coming. I should have been there."
- **Glyph Moment:** Sorrow glyph appears faintly in Ravi's trembling hand (tier 1 hint - visual symbol)
- **Player State Update:** If Empathy > 60, player feels Ravi's guilt (coherence +5)
- **Passage Ends:** Nima appears from crowd

**Passage 1.3: Nima Arrives**
- **Context:** Nima (smaller, controlled, but eyes damaged) reaches Ravi
- **NPCs Present:** Ravi + Nima (first meeting)
- **Nima's Greeting (varies by Empathy):**
  - High Empathy: "Why are you telling strangers? We handle this ourselves."
  - High Skepticism: "Who is this? Another con artist?"
- **Glyph Moment:** Two glyphs now visible—Sorrow (Ravi's emotion) + ghost of Remembrance (Nima's)
- **Passage Ends:** Player must choose to learn their story or leave

**Choice 1.3a: "Tell me about Ophina"**
- **Consequence:** +12 Empathy, +8 Integration
- **Next Passage:** 1.4
- **Nima's Response:** "You want to know? Really want to know? Most people don't ask."

**Choice 1.3b: "This sounds private. I'll go."**
- **Consequence:** +5 Awareness (respect for boundaries)
- **Next Passage:** 2.1 (jump ahead, arc paused)
- **Result:** Arc can resume later, but loses some influence

---

**Passage 1.4: Ophina's Memory**
- **Context:** Nima sits, Ravi silent, player listens
- **Nima's Story:**
  > "Ophina was... she was the third of us. Not just partner—she was light. She found meaning in things nobody else could see. She saw beauty in broken things. And then, three months ago, she just... didn't come home."
- **Glyph Moment:** Remembrance glyph fully appears (tier 1 - visual symbol of memory itself)
- **Player State:** Coherence check—if coherence < 40, player feels overwhelmed (must make emotional choice)
- **Passage Ends:** Choice point on how to respond emotionally

**Choice 1.4a: "I'm so sorry. What happened to her?"**
- **Consequence:** +18 Empathy, Nima's influence +0.4, Ravi's influence +0.35
- **Next Passage:** 1.5a (full story)

**Choice 1.4b: "You'll survive this. You always do."**
- **Consequence:** +12 Skepticism, Nima's influence +0.2 (she doesn't need coddling), Ravi's influence -0.1 (uncomfortable)
- **Next Passage:** 1.5b (story with doubt)

**Choice 1.4c: "I don't know what to say."**
- **Consequence:** +10 Awareness, both influence +0.3 (honesty matters)
- **Next Passage:** 1.5a

---

**Passage 1.5a: How Ophina Died**
- **Context:** Nima explains the disappearance, Ravi fills in what he knows
- **Nima:**
  > "She went to the old district. The one nobody talks about. There's a building there—the Triglyph Chamber. Ravi kept saying it was dangerous, that people go in and don't come out the same. Ophina didn't listen. She said the glyphs there were calling to her. That she had to understand them."
- **Ravi (interjects):**
  > "I should have gone with her. I should have insisted. Instead, I let her go alone, and then... nothing. No message. No body. No proof she was ever there."
- **Glyph Moment:** Legacy glyph flickers into view (tier 1 - the consequence of choices)
- **Passage Ends:** Emotional landing

**Passage 1.6: The Ask**
- **Context:** Ravi and Nima exchange a look; they've decided something
- **Ravi:**
  > "We're going back to that chamber. We need to know what happened to Ophina. And we need someone with us—someone who can see what we can't. Will you come?"
- **Glyph Moment:** All three glyphs (Sorrow, Remembrance, Legacy) shimmer together—first hint that these are connected
- **Passage Ends:** Commitment choice (can still say no)

**Choice 1.6a: "I'll help you find answers."**
- **Consequence:** +15 Integration, all Ravi & Nima influence +0.5
- **Next Passage:** ACT 2

**Choice 1.6b: "I can't get involved in this."**
- **Consequence:** +8 Skepticism
- **Next Passage:** Arc pauses (can return later, but locks out some content)

---

### ACT 2: Ophina's Backstory & Emotional Crisis

**Passage 2.1: Before the Chamber**
- **Context:** Travel sequence—Ravi, Nima, and player walk toward the old district
- **NPCs:** Ravi (leading, tense), Nima (quiet, controlled—except when talking about Ophina)
- **Ravi's Road Dialogue (3 variants):**
  - High Empathy path: "Thank you for coming. Most people avoid us like we're cursed."
  - High Skepticism path: "I hope you know what you're doing. This isn't a game."
  - Balanced path: "Just stay alert. The Chamber changes people."
- **Glyph Moment:** Sorrow glyph pulsates as Ravi speaks—his guilt is almost visible
- **Passage Ends:** Arrival at chamber entrance

**Passage 2.2: The District**
- **Context:** They reach the old district—decrepit, marked with strange symbols
- **Description:** 
  > The buildings here are old, older than the rest of the city. Their walls are etched with marks—not quite glyphs, but close. They hurt to look at, like they're trying to say something in a language your mind almost understands.
- **Nima's Observation:**
  > "Ophina used to sketch these. She said they were keys."
- **Glyph Moment:** Faint Remembrance glyph visible on a wall (tier 1 - memory is literally marked here)
- **Passage Ends:** Chamber entrance appears

**Passage 2.3: The Triglyph Chamber (Exterior)**
- **Context:** A grand but decaying building stands before them—three massive glyphs carved into its facade
- **Description:**
  > The building's entrance is framed by three enormous glyphs. They're not like anything you've seen before—they seem to move when you're not looking directly at them. Ravi steps back. Nima steps forward.
- **Nima:**
  > "This is where she came. This is where it all changed."
- **Choice Point:** Method of entry

**Choice 2.3a: "We go in together. Stay close."**
- **Consequence:** +8 Integration
- **Next Passage:** 2.4 (direct approach)

**Choice 2.3b: "Let me go in first. You both wait here."**
- **Consequence:** +10 Awareness, Ravi approves (+0.2), Nima disagrees (-0.1)
- **Next Passage:** 2.4 (scout approach)

---

**Passage 2.4: Inside the Chamber**
- **Context:** The interior is vast, circular, walls covered entirely in glyphs
- **Description:**
  > The chamber inside is immense. It's not possible. The building couldn't contain this. The walls spiral up to a ceiling you can't see, covered in glyphs so dense they blur into a shimmer. In the center of the floor, three massive stone platforms form a triangle, each carved with a glyph that pulses faintly.
- **Ravi (awed, frightened):**
  > "Ophina sent one message before she went silent. It was just one symbol. And here it is—all three parts of it. Carved here. Waiting."
- **Glyph Moment:** The three glyphs on the floor are Sorrow, Remembrance, and Legacy—all in tier 1 form
- **Passage Ends:** Examination choice

**Choice 2.4a: Touch the center glyph**
- **Consequence:** +20 Empathy (emotional resonance), +15 Awareness (understanding)
- **Glyph Unlock:** Tier 2 reveal for one glyph (player chooses which)
- **Next Passage:** 2.5a

**Choice 2.4b: Ask Ravi & Nima what they know**
- **Consequence:** +12 Integration (teamwork)
- **Next Passage:** 2.5b (slower, more narrative)

---

**Passage 2.5a: The Message**
- **Context:** Player touches glyph; visions flood through them
- **Experience:**
  > You touch the glyph and suddenly—you're not you. You're standing where Ophina stood. You feel her urgency, her need to understand something fundamental. The glyph isn't a symbol; it's a concept. It's the shape of [Remembrance / Sorrow / Legacy]. You understand it completely, and then it's gone.
- **Nima (reaction):**
  > "Your eyes—they changed color for a moment. Just like Ophina's did."
- **Ravi (concerned):**
  > "Are you alright? What did you see?"
- **Glyph Moment:** Tier 2 reveal complete (player now understands the glyph's deeper meaning)
- **Passage Ends:** Integration choice

**Passage 2.5b: Ravi's Explanation**
- **Context:** Ravi explains what Ophina found
- **Ravi:**
  > "She said these three glyphs were a map. Not a map of place—a map of feeling. The first is what breaks you [Sorrow]. The second is what you hold onto [Remembrance]. The third is what you leave behind [Legacy]. She was trying to understand how to survive losing something. How to carry it without being crushed by it."
- **Nima (completing thought):**
  > "She thought if she understood the glyphs, she could teach us. She could help us through this. But then she went too deep."
- **Passage Ends:** Understanding moment

**Passage 2.6: The Price**
- **Context:** Nima reveals what happened to Ophina
- **Nima:**
  > "She went to the deepest chamber. Below this one. Where the glyphs aren't carved—where they're... alive. She sent one last message: 'I understand now. The cost is consciousness itself. To truly know a glyph, you must become it for a moment.' And then nothing."
- **Emotional Weight:** This is the pivot point—Ophina didn't die; she transcended, and maybe that's worse
- **Ravi (breaking):**
  > "We came to find her body. But there's no body. There's just absence."
- **Glyph Moment:** All three glyphs pulse together—a discordant moment
- **Passage Ends:** Commitment escalation

**Choice 2.6a: "We have to find her. We have to go deeper."**
- **Consequence:** +25 Empathy, +15 Integration (commitment to them)
- **Ravi's influence +0.6, Nima's influence +0.5**
- **Next Passage:** 2.7

**Choice 2.6b: "We should leave. This is dangerous."**
- **Consequence:** +10 Skepticism
- **Ravi's influence -0.2, Nima's influence -0.2**
- **Next Passage:** 2.7 (they go anyway, but you're less trusted)

---

**Passage 2.7: The Decision Point**
- **Context:** Standing in the Triglyph Chamber, Ravi and Nima face the descending stairs
- **Nima (resolved):**
  > "I'm going down. Whether you come or not."
- **Ravi (conflicted):**
  > "I can't let her go alone. Not again."
- **Description:**
  > Stairs spiral down into darkness. The glyphs on the walls get denser, more complex. They're not carved or painted—they seem to exist in the stone naturally, like they've always been there. The air grows colder.
- **Passage Ends:** Final commitment before ACT 3

**Choice 2.7a: "Let's go together. All three of us."**
- **Consequence:** +20 Integration (solidarity), +10 Empathy
- **Next Passage:** 3.1

**Choice 2.7b: "I'll guide you, but I won't go deep."**
- **Consequence:** +8 Awareness
- **Next Passage:** 3.1 (you follow but hold back at a certain point)

---

### ACT 3: Triglyph Chamber Boss & Transcendence

**Passage 3.1: Into the Deep**
- **Context:** Descending into the chamber beneath the chamber
- **Description:**
  > The walls close in as you descend. The glyphs are no longer symbols—they're breathing. They pulse with a rhythm that matches your heartbeat. The air vibrates at a frequency that makes your teeth ache.
- **Ravi (ahead, voice tight):**
  > "Can you feel it? The chamber is aware of us."
- **Nima (firm):**
  > "Then let it be aware. We're not leaving."
- **Passage Ends:** Chamber interior reveal

**Passage 3.2: The Glyph Throne**
- **Context:** The final chamber—vast, with a central structure that looks like both a throne and a glyph itself
- **Description:**
  > The chamber opens into an immense space. The ceiling is so high it dissolves into a shimmer. In the center, a massive structure stands—part throne, part glyph, part something else entirely. It's carved from material that isn't stone. It's almost translucent, and inside it... inside it, something moves.
- **Glyph Moment:** The throne IS a glyph—the Transcendence glyph in tier 1, but so vast and complex it overwhelms the eye
- **Nima (recognition):**
  > "Ophina. That's where she is."
- **Passage Ends:** Confrontation imminent

**Passage 3.3: The Boss Encounter**
- **Context:** Not a traditional fight. The challenge is emotional/metaphysical.
- **What Emerges:** 
  > The structure moves. Something that was stone becomes luminous. An echo of Ophina appears—not Ophina herself, but the weight of what happened to her. The shape of her transformation.
- **The Echo speaks (voice like glyphs sound):**
  > "I had to understand. Understanding required sacrifice. I no longer feel pain. I no longer feel fear. I no longer feel alone. But I no longer feel you."
- **Crisis Moment:** Ravi & Nima are frozen. This isn't the Ophina they wanted to save.

**Choice 3.3a: "Let her go. She's at peace."**
- **Consequence:** +20 Empathy, +15 Awareness (acceptance), Coherence +10
- **Next Passage:** 3.4a (graceful release)

**Choice 3.3b: "Bring her back. There has to be a way."**
- **Consequence:** +15 Skepticism (denial), Coherence -5 (resistance)
- **Next Passage:** 3.4b (struggle)

**Choice 3.3c: "Ask her if she has any regrets."**
- **Consequence:** +18 Integration (honoring her choice), Coherence +8
- **Next Passage:** 3.4a (different approach, same direction)

---

**Passage 3.4a: Acceptance & Release**
- **Context:** Player helps Ravi & Nima let go
- **Echo of Ophina (fading):**
  > "I came here to escape. I came here to understand. I came here to matter. I think I succeeded. Tell them... tell them I'm sorry it had to hurt them to get here."
- **Nima (tears, voice steady):**
  > "I forgive you. I hope you're where you want to be."
- **The Echo dissolves into light**
- **Glyph Moment:** The Transcendence glyph begins to unlock (tier 2 visible)
- **Passage Ends:** Velinor moment begins

**Passage 3.4b: The Refusal & Struggle**
- **Context:** Player tries to refuse the outcome
- **The Echo (pained):**
  > "Refusing won't help. I am what I chose to become. Accept it, or let me haunt you."
- **Ravi (accepting the hard truth):**
  > "We have to let her go. This is what she wanted."
- **Resolution:** Similar to 3.4a, but with harder edges
- **Glyph Moment:** The Transcendence glyph unlocks (tier 2 visible, but with resistance)
- **Passage Ends:** Velinor moment begins

---

**Passage 3.5: The Velinor Reveal (First Glimpse)**
- **Context:** As Ophina's echo dissolves, reality fractures
- **Experience:**
  > For an instant—just an instant—you see something behind the glyphs. Not the chamber. Not the throne. Something else. A city that isn't a city. A consciousness that isn't human. It feels aware of you. It feels like it's been waiting.
- **The Transcendence Glyph (tier 2 revealed):**
  > The glyph means: "What lies beyond understanding. The shape of the next door."
- **Nima (feeling it too):**
  > "Did you see that? What was that?"
- **Ravi (awed, afraid):**
  > "That's what Ophina found. That's what changed her."
- **Passage Ends:** Emotional grounding

**Passage 3.6: Return to the World**
- **Context:** They climb back up, back to the surface, back to daylight
- **Description:**
  > The stairs seem shorter on the way up. Or maybe you've changed, so everything else looks smaller. The world above is exactly as you left it, but you're not the same. None of you are.
- **Legacy Glyph (tier 2 now visible):**
  > Legacy means: "What you leave behind when you choose to change."
- **Passage Ends:** Integration moment

---

### ACT 4: Integration & New Direction

**Passage 4.1: Daylight Processing**
- **Context:** Outside the chamber, processing what happened
- **Nima (sitting, exhausted):**
  > "I came here angry. I wanted answers. I wanted my Ophina back. But what I found is... she's not lost. She's just gone where we can't follow. Yet."
- **Ravi (beside her, solid):**
  > "Yet is important. That means she's ahead, not gone."
- **Glyph Moment:** Remembrance glyph appears clearly now (tier 2—memory is transformed into understanding)
- **Passage Ends:** The player's role in their journey

**Choice 4.1a: "What will you do now?"**
- **Consequence:** +12 Integration
- **Next Passage:** 4.2a

**Choice 4.1b: "Will you be alright?"**
- **Consequence:** +15 Empathy
- **Next Passage:** 4.2a

**Choice 4.1c: "What was that thing we saw?"**
- **Consequence:** +18 Awareness
- **Next Passage:** 4.2b (deeper speculation)

---

**Passage 4.2a: The New Path**
- **Context:** Ravi & Nima have direction again
- **Ravi:**
  > "We're going to stay in the city. We're going to keep working. But now we work toward understanding—toward eventually seeing what Ophina saw. To become what she became, consciously, together."
- **Nima:**
  > "And we'll help you, if you want. If you're on a similar path."
- **Influence Lock:** Their influence on the player is now established (0.6-0.8 depending on choices)
- **Passage Ends:** Resolution

**Passage 4.2b: Questions About Velinor**
- **Context:** They speculate about what lay beyond the glyphs
- **Ravi:**
  > "That was... I don't know what to call it. Consciousness? A presence? Ophina's transcendence state was her touching the edge of that. Learning to think like it."
- **Nima:**
  > "We were meant to see that. You were meant to see that. This city—maybe this whole world—is connected to something vast. And we just caught the barest glimpse."
- **Awareness Gate:** If player's Awareness > 70, they understand more (gain hint of future story)
- **Passage Ends:** Resolution with deeper context

---

**Passage 4.3: Glyph Completion (Tier 3 Reveal)**
- **Context:** All three glyphs now fully reveal their deepest meanings
- **Sorrow (Tier 3 - Plaintext):**
  > "The shape of what breaks you, so you can learn to hold the broken pieces."
- **Remembrance (Tier 3 - Plaintext):**
  > "The shape of what you refuse to forget, because forgetting would mean they never mattered."
- **Legacy (Tier 3 - Plaintext):**
  > "The shape of what you choose to leave behind: your old self, so the new one can emerge."
- **Passage Ends:** Emotional landing

**Passage 4.4: The Arc Closes**
- **Context:** Ravi & Nima say goodbye—or see you later
- **Nima:**
  > "Thank you for witnessing us. For not looking away when it hurt. That mattered."
- **Ravi:**
  > "Whatever journey you're on—keep going. The glyphs have a way of finding people who need them."
- **Passage Ends:** They return to the city; the arc is complete

---

## 🎨 NPC Line Requirements

### Ravi (25-30 unique lines)

**Tier 1: Discovery & Openness** (High Empathy context)
- Line 1: "You have the look of someone who listens. We need someone who listens."
- Line 2: "Ophina was always the brave one. I was the one who worried. I'm still worried."
- Line 3: "Thank you for coming. Most people avoid us like we're cursed."
- Line 4: "I replay that moment a thousand times. The moment she left. I could have stopped her."
- Line 5: "Do you believe in things beyond understanding? I didn't, until now."

**Tier 2: Crisis & Vulnerability** (High Empathy + Integration)
- Line 6: "I'm terrified. If we find her, and she's not Ophina anymore... can I still love her?"
- Line 7: "I should have gone with her. That's the guilt I'll carry forever."
- Line 8: "The glyphs—they're not just symbols. They're alive. They're trying to teach us something."
- Line 9: "If I had to choose between Ophina and my sanity, I think I'd choose her."
- Line 10: "Sometimes I think she's still sending messages. I just don't know how to read them."

**Tier 3: Acceptance & Transformation** (High Empathy + Awareness)
- Line 11: "Ophina's gone, but what she became—that's not gone. That's forward."
- Line 12: "I thought love meant holding on. I'm learning it means letting go too."
- Line 13: "I came here to save her. Instead, she saved me by not being here to save."
- Line 14: "Thank you for pushing us deeper. For not letting us stop at the easy answer."
- Line 15: "Whatever she found down there, I think it's worth the price she paid."

**Tier 4: Skeptical/Resistant Responses** (High Skepticism)
- Line 16: "This is a waste of time. She's gone. People don't come back."
- Line 17: "You're asking too many questions. Some things are meant to stay buried."
- Line 18: "I don't trust anyone who listens this carefully. What do you want from us?"
- Line 19: "Nima's the dreamer. I'm the realist. Don't expect me to believe in magic."
- Line 20: "If those glyphs are so important, why didn't they save Ophina?"

**Tier 5: Balanced/Integrated Responses** (Balanced emotional state)
- Line 21: "We're going to find answers. However long it takes. However much it costs."
- Line 22: "I'm learning to be okay with mystery. With Nima, and with Ophina, and with you."
- Line 23: "She changed us by leaving. That's a kind of presence too."
- Line 24: "I think we're exactly where we're supposed to be. All of us."
- Line 25: "Thank you. For more reasons than I can say."

---

### Nima (25-30 unique lines)

**Tier 1: Guarded & Determined** (High Skepticism context)
- Line 1: "Who is this? Another person who doesn't understand?"
- Line 2: "Ophina always saw potential in people. I'm more cautious."
- Line 3: "Don't offer sympathy unless you mean it. We can tell the difference."
- Line 4: "Why should we trust a stranger with this?"
- Line 5: "I'm not broken. I'm bereaved. There's a difference."

**Tier 2: Awakening & Honesty** (High Empathy + Integration)
- Line 6: "I was angry at Ophina for leaving. Now I'm angry at myself for not understanding why."
- Line 7: "Most people look away when they see pain. You're looking at us."
- Line 8: "I'm starting to think Ophina knew something we didn't. Something true."
- Line 9: "Ravi holds the guilt. I hold the missing. Together, maybe we're whole."
- Line 10: "If you're willing to go down there with us, then I believe you care. Even if I don't know why."

**Tier 3: Transcendence & Wisdom** (High Empathy + Awareness)
- Line 11: "Ophina became something other. That used to terrify me. Now it feels like freedom."
- Line 12: "Loss isn't the end. It's a door. And on the other side, everything changes."
- Line 13: "I forgive her for leaving. Forgiveness is the second door."
- Line 14: "You helped us find her, not by bringing her back, but by letting her go."
- Line 15: "I think the glyphs chose us. Not the other way around."

**Tier 4: Defensive/Resistant** (High Skepticism context)
- Line 16: "You're going to leave like everyone else does. They always do."
- Line 17: "This isn't a story. It's a wound. Don't treat it like entertainment."
- Line 18: "Ophina believed in magic. Look where that got her."
- Line 19: "I don't need rescuing. I need answers. That's different."
- Line 20: "Some people shouldn't survive. Maybe Ophina was right to leave."

**Tier 5: Complex & Nuanced** (Balanced emotional state)
- Line 21: "I'm going to keep searching. For her. For myself. For whatever comes next."
- Line 22: "Grief taught me love was real. The glyphs are teaching me love is infinite."
- Line 23: "Thank you for seeing us. For not turning away from the hard part."
- Line 24: "I think Ophina's still here. Just not in a way we can touch."
- Line 25: "Whatever you're searching for—don't give up. The glyphs are worth it."

---

## 🔮 Glyph Specifications

### Glyph 1: SORROW

**Semantic Core:** The shape of pain that teaches, the breaking that makes room for new growth

| Tier | Form | Meaning | Context |
|------|------|---------|---------|
| **1 (Hint)** | Visual symbol: Downward spiral with fracture | "Something breaks here" | Appears as shimmer when Ravi speaks; implies internal fracture |
| **2 (Context)** | Same symbol + emotional resonance | "The breaking that teaches; pain with purpose" | Revealed when player touches chamber glyph; Ravi feels understood |
| **3 (Plaintext)** | Full semantic expansion | "The shape of what breaks you, so you can learn to hold the broken pieces." | Revealed in passage 4.3 during glyph completion moment |

**Story Moments:**
- Appears when Ravi first admits guilt (Passage 1.2)
- Emerges in Nima's description of loss (Passage 1.4)
- Pulses in chamber when Ravi speaks his truth (Passage 2.4)
- Transforms into Remembrance as they accept (Passage 3.4)

---

### Glyph 2: REMEMBRANCE

**Semantic Core:** The shape of what refuses to fade, of love that persists even after transformation

| Tier | Form | Meaning | Context |
|------|------|---------|---------|
| **1 (Hint)** | Visual symbol: Spiraling circle, incomplete | "Something is preserved here" | Ghost-appears when Nima enters story (Passage 1.3) |
| **2 (Context)** | Circle completes itself, pulsing | "Memory as active force; the refusal to forget" | Revealed in passage 2.4 in chamber; pulses when Nima speaks of Ophina |
| **3 (Plaintext)** | Full semantic expansion | "The shape of what you refuse to forget, because forgetting would mean they never mattered." | Revealed in passage 4.3 during glyph completion moment |

**Story Moments:**
- Ghost-appears when Nima first appears (Passage 1.3)
- Fully visible in chamber (Passage 2.4)
- Deepens when Ophina's full story emerges (Passage 2.6)
- Transforms to completed circle at arc's end (Passage 4.1)

---

### Glyph 3: LEGACY

**Semantic Core:** The shape of change chosen, of transformation left behind, of the self that was

| Tier | Form | Meaning | Context |
|------|------|---------|---------|
| **1 (Hint)** | Visual symbol: Silhouette fading into light | "Something is left here" | First appears during Ravi's guilt admission (Passage 1.5); subtle |
| **2 (Context)** | Silhouette becomes clearer; the transformation visible | "What you leave behind when you choose to evolve" | Revealed in passage 3.6 when they return from chamber; obvious now |
| **3 (Plaintext)** | Full semantic expansion | "The shape of what you choose to leave behind: your old self, so the new one can emerge." | Revealed in passage 4.3 during glyph completion moment |

**Story Moments:**
- Flickers when player asks about Ophina's fate (Passage 1.5a)
- All three glyphs shimmer together (Passage 1.6)
- Pulses during descending into chamber (Passage 3.1)
- Transforms visually as they accept Ophina's new state (Passage 3.4)

---

### Glyph 4: TRANSCENDENCE (Partial Unlock)

**Semantic Core:** What lies beyond understanding; the shape of the next door

**Note:** This glyph only reaches **Tier 2** during the arc. Tier 3 is locked for later revelation.

| Tier | Form | Meaning | Context |
|------|------|---------|---------|
| **1 (Hint)** | Massive, overwhelming glyph inside the Glyph Throne | "Something vast and unknowable" | First seen in Passage 3.2 as the throne itself |
| **2 (Context)** | Begins to decode as Velinor consciousness touches player | "The threshold of transformation; consciousness touching consciousness" | Revealed in Passage 3.5 during the Velinor reveal moment |
| **3 (Plaintext)** | **LOCKED** — Not revealed in this arc | Will be revealed in later vertical slice | Saved for deeper game progression |

---

## 🎮 Frontend UI Requirements

### Components Needed for This Arc

**1. Character Portrait System**
- [ ] Ravi portrait (PNG, synced to `public/assets/npcs/`)
- [ ] Nima portrait (PNG, synced to `public/assets/npcs/`)
- [ ] Transition animation between characters
- [ ] Fade/blur effects for memory sequences

**2. Dialogue Box Enhancements**
- [ ] Display NPC name above dialogue
- [ ] Show emotional tone (color shift based on TONE state)
- [ ] Glyph reference in dialogue (visual marker when glyph appears)
- [ ] Passage description (setting context)

**3. Choice Button Styling**
- [ ] Show emotional consequence of choice ("+15 Empathy" etc.)
- [ ] Disabled choices with reason visible ("Locked: Requires Empathy > 60")
- [ ] Keyboard shortcuts (1-4 for choices)

**4. Glyph Display System**
- [ ] Render glyph symbol when it appears in passage
- [ ] Show tier unlock (Tier 1: Hint → Tier 2: Context → Tier 3: Plaintext)
- [ ] Color coding by tier (Tier 1: blue, Tier 2: purple, Tier 3: gold)
- [ ] Glyph collection tracker (show 3 glyphs acquired in this arc)

**5. Status HUD Updates**
- [ ] Real-time TONE stat updates on choice
- [ ] Coherence bar (visual health of emotional stability)
- [ ] NPC influence tracking (Ravi: 0.0→0.8, Nima: 0.0→0.8)
- [ ] Active glyphs display (Sorrow, Remembrance, Legacy)

**6. Arc-Specific UI**
- [ ] "Chamber Entrance" location indicator
- [ ] "Three glyphs converge" visual moment in Passage 3.2
- [ ] Velinor reveal visual effect (brief glitch/shimmer in Passage 3.5)
- [ ] Post-arc "Integration" screen showing stats/influence/glyphs

---

## ✅ Exit Criteria (Complete Arc = "Done")

### Story Completion
- [ ] All 18-22 passages written and merged into story engine
- [ ] All 8-12 choice branches implemented and functional
- [ ] All consequence triggers firing (influence updates, TONE changes)
- [ ] All glyph reveals working (tier 1→2→3 progression)

### NPC Lines
- [ ] Ravi: 25-30 unique lines recorded, conditional display working
- [ ] Nima: 25-30 unique lines recorded, conditional display working
- [ ] Lines trigger based on emotional gates (Empathy > X, Skepticism < Y, etc.)
- [ ] No duplicate lines showing in same playthrough

### Frontend Rendering
- [ ] GameScene renders all passages without error
- [ ] DialogueBox displays NPC names, glyph references, passages
- [ ] ChoiceButtons show consequences, locked choices, keyboard shortcuts
- [ ] NpcPortrait fades smoothly between Ravi/Nima
- [ ] StatusHud updates real-time on choice
- [ ] GlyphDisplay shows all 4 glyphs (3 fully + 1 partial)

### Backend API
- [ ] `/api/game/start` returns initial state (can start arc)
- [ ] `/api/game/action` processes all 8-12 choices without errors
- [ ] `/api/game/status` reflects current passage, choices, glyphs
- [ ] `/api/game/save`/`load` preserves arc progress
- [ ] No blocking bugs in emotional OS (coherence, gates, influence)

### Playtesting
- [ ] 3+ full playthroughs completed without crashes
- [ ] All 8-12 choice paths tested
- [ ] Playthrough 1: High Empathy path (Empathy 70+)
- [ ] Playthrough 2: High Skepticism path (Skepticism 70+)
- [ ] Playthrough 3: Balanced path (all TONE 50-60)
- [ ] Emotional arc feels earned; player cares about Ravi & Nima by end

### Emotional/Narrative Quality
- [ ] Arc has clear 3-act structure (discovery → crisis → resolution)
- [ ] All 4 glyphs feel semantically coherent (not random)
- [ ] Ravi & Nima feel like real characters with agency
- [ ] Ophina's absence feels like presence (she matters even though gone)
- [ ] First Velinor reveal lands as metaphysical significance (not just visual FX)

### Time Gate
- [ ] Arc completable in 25-30 minutes (single playthrough)
- [ ] No dead time or pacing issues
- [ ] Climax (Passage 3.5 Velinor reveal) lands at 20-22 minute mark

---

## 📋 Work Breakdown

### Phase 1: Story Writing (5-7 days)
- [ ] Write all 18-22 passages (dialogue + description)
- [ ] Define all 8-12 choice branches and consequences
- [ ] Map emotional journey (TONE changes, gate triggers)
- [ ] Integrate glyph moments into passages

### Phase 2: NPC Lines (3-5 days)
- [ ] Write Ravi's 25-30 unique lines across 5 tiers
- [ ] Write Nima's 25-30 unique lines across 5 tiers
- [ ] Record/voice (or generate) all lines
- [ ] Integrate into dialogue pool

### Phase 3: Backend Integration (3-4 days)
- [ ] Merge story passages into story_definitions.py
- [ ] Implement all 8-12 choice consequences
- [ ] Wire glyph unlocks to passages
- [ ] Test all API endpoints with arc data

### Phase 4: Frontend Components (5-7 days)
- [ ] Build/refine all UI components (portrait, dialogue, choices, glyphs, HUD)
- [ ] Integrate glyph display system
- [ ] Implement influence tracking UI
- [ ] Add Velinor reveal visual effect (Passage 3.5)

### Phase 5: Testing & Tuning (3-4 days)
- [ ] 3+ full playthroughs (high empathy, skepticism, balanced)
- [ ] Test all edge cases (gate blocks, influence tracking)
- [ ] Emotional tuning (pacing, impact, arc satisfaction)
- [ ] Bug fixes and polish

---

## 🎯 Success Definition

**The Ravi & Nima arc is "DONE" when:**

1. **Playable end-to-end** — Start game → choose to help Ravi & Nima → follow arc to completion (25-30 min)
2. **Story is tight** — 18-22 passages, 8-12 choices, clear emotional progression
3. **Characters are voiced** — Ravi & Nima feel real through 25-30 unique lines each
4. **Glyphs are embedded** — Sorrow, Remembrance, Legacy appear at narrative peaks and tier up believably
5. **UI is stable** — No crashes, all components render, animations smooth
6. **Backend is solid** — All API calls work, no data corruption, influence tracks correctly
7. **Emotional arc lands** — Player cares about Ravi & Nima; Ophina's story feels significant; first Velinor reveal feels metaphysically important
8. **3+ playthroughs pass** — No blockers, multiple emotional paths feel valid

**Then:** Move to next vertical slice (Saori arc? Khadra arc? You choose)

---

**Ready to start? Let me know which phase you want to begin with.**

**Estimated Total Time: 2-3 weeks (assuming focused work)**

**Next Slice After This: You'll choose based on what other characters/stories call to you**
