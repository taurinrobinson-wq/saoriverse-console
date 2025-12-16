# NPC Sphere of Influence System

## Overview

The NPC Sphere of Influence System models how relationships ripple across Velinor's communities. Each NPC belongs to a sphere—a web of emotional connections, family ties, and shared resonance. When the player fractures trust or deepens empathy with one NPC, it affects not just that character, but their entire network.

##

## Core Mechanics

### Sphere Structure

- **Every NPC belongs to at least one sphere** (Marketplace, Shrine, Wanderers, etc.).
- **NPCs within a sphere have weighted connections** to each other (0.1–1.0 strength).
- **Player actions with one NPC ripple outward** through the network based on connection strength.

### Weighted Ripple System

| Weight Range | Impact Type | Examples |
|---|---|---|
| **0.7–1.0 (Strong)** | Immediate, noticeable impact | Ravi ↔ Nima (partners), Parent ↔ Child |
| **0.4–0.6 (Medium)** | Subtle shifts in dialogue, glyph access | Ravi ↔ Merchants, Nima ↔ Shrine Keepers |
| **0.1–0.3 (Weak)** | Background changes, NPC tone | Merchants ↔ Wanderers (minimal overlap) |

##

## Marketplace Sphere of Influence

### Network Map

```text
```

                    Ravi (0.8) ← → Nima
                    /  \              /  \
              (0.4)/    \(0.2)    (0.5)/   \(0.3)
                  /        \          /       \
            Merchants    Shrine Keepers    Merchants
          (0.4 ripple)   (0.5 ripple)     (0.3 ripple)
              |              |                |
        Tovren (Cartwright)  Sera (Novice)    Korrin (Gossip)
        Mariel (Weaver)      [Others]        [Others]
        Kaelen (Cloaked)*

- Hidden sphere: Thieves' Gang (0.6 counter-sphere with Veynar)

```



### Core NPCs and Their Connections

#### Ravi — The Open Watcher

- **Role**: Merchant, community hub, Trust anchor
- **Sphere Strength**:
  - Ravi ↔ Nima: **0.8 (Strong)** — his trust/suspicion directly mirrors hers
  - Ravi ↔ Tovren: **0.4 (Medium)** — fellow merchants, cautious respect
  - Ravi ↔ Mariel: **0.5 (Medium)** — elder respect, wisdom exchange
  - Ravi ↔ Kaelen: **0.2 (Weak)** — aware of him, maintains distance
  - Ravi ↔ Veynar: **0.3 (Weak)** — respects guard, but distrusts authority

#### Nima — The Guarded Flame

- **Role**: Shrine guardian, Empathy anchor, Ravi's partner
- **Sphere Strength**:
  - Nima ↔ Ravi: **0.8 (Strong)** — partnership, emotional mirror
  - Nima ↔ Sera: **0.5 (Medium)** — mentor-like, spiritual kinship
  - Nima ↔ Shrine Keepers: **0.5 (Medium)** — shared spiritual practice
  - Nima ↔ Mariel: **0.4 (Medium)** — elder wisdom, shared loss
  - Nima ↔ Merchants: **0.3 (Weak)** — skeptical of trade

#### Tovren the Cartwright

- **Role**: Practical merchant, tool-giver, Observation-aligned
- **Sphere Strength**:
  - Tovren ↔ Ravi: **0.4 (Medium)** — fellow merchants
  - Tovren ↔ Other Merchants: **0.6 (Medium)** — trade network
  - Tovren ↔ Mariel: **0.4 (Medium)** — both value craftsmanship
  - Tovren ↔ Wanderers: **0.3 (Weak)** — sells to travelers

#### Sera the Herb Novice

- **Role**: Shrine acolyte, Empathy-aligned, ritual keeper
- **Sphere Strength**:
  - Sera ↔ Nima: **0.5 (Medium)** — student-mentor relationship
  - Sera ↔ Shrine Keepers: **0.7 (Strong)** — shared order
  - Sera ↔ Mariel: **0.3 (Weak)** — different generations

#### Dalen the Rusted Guide

- **Role**: Wanderer, Narrative Presence-aligned, risk-taker
- **Sphere Strength**:
  - Dalen ↔ Ravi: **0.3 (Weak)** — Ravi cautious of boldness
  - Dalen ↔ Nima: **0.2 (Weak)** — Nima fears his recklessness
  - Dalen ↔ Wanderers: **0.7 (Strong)** — community leader
  - Dalen ↔ Hidden Shrines: **0.4 (Medium)** — knows secret paths

#### Mariel the Weaver

- **Role**: Elder, Trust + Empathy anchor, community bridge
- **Sphere Strength**:
  - Mariel ↔ Ravi: **0.5 (Medium)** — mutual respect
  - Mariel ↔ Nima: **0.4 (Medium)** — shared loss, wisdom
  - Mariel ↔ Tovren: **0.4 (Medium)** — craftsmanship kinship
  - Mariel ↔ Sera: **0.3 (Weak)** — different generations
  - Mariel ↔ Shrine Keepers: **0.5 (Medium)** — community elder

#### Korrin the Gossip

- **Role**: Informant, Observation-aligned, rumor spreader
- **Sphere Strength**:
  - Korrin ↔ Merchants: **0.6 (Medium)** — market gossip network
  - Korrin ↔ Ravi: **0.3 (Weak)** — Ravi distrusts gossip
  - Korrin ↔ Kaelen: **0.4 (Medium)** — aware of thefts, spreads rumors
  - Korrin ↔ Veynar: **0.2 (Weak)** — guards distrust informants

#### Kaelen the Cloaked

- **Role**: Suspected thief, Test of vigilance, Trust breaker
- **Sphere Strength**:
  - Kaelen ↔ Thieves' Gang: **0.9 (Strong)** — hidden hierarchy
  - Kaelen ↔ Merchants: **0.2 (Weak)** — feared but not integrated
  - Kaelen ↔ Korrin: **0.4 (Medium)** — gossip spreads his shadow
  - Kaelen ↔ Ravi: **0.2 (Weak)** — maintained distance until player interferes

#### Captain Veynar

- **Role**: Market Guard, Authority figure, Counter-sphere to Kaelen
- **Sphere Strength**:
  - Veynar ↔ Merchants: **0.5 (Medium)** — sworn to protect
  - Veynar ↔ Ravi: **0.3 (Weak)** — respects openness, wary of judgment
  - Veynar ↔ Kaelen: **0.6 (Counter)** — direct opposition
  - Veynar ↔ Guards: **0.8 (Strong)** — authority network
  - Veynar ↔ Shrine Keepers: **0.2 (Weak)** — spiritual distrust of law
##

## Ripple Effect Examples

### Example 1: Player Fractures Trust with Ravi

**Action**: Player betrays Ravi's confidence or steals from him.

**Immediate Ripple** (0.8 weight):

- Nima's suspicion rises. She becomes guarded again.
- Dialogue shift: "I thought you listened like he did. I was wrong."

**Secondary Ripples** (0.4 weight):

- Tovren and other merchants grow wary. Trade becomes harder.
- Prices rise slightly, glyph fragments harder to access.

**Tertiary Ripples** (0.2 weight):

- Kaelen notices the fracture. He becomes bolder.
- Shrine keepers remain neutral, but watch the player more carefully.

**Timeline**: The closer the player is to other marketplace encounters, the faster the ripple spreads.

### Example 2: Player Earns Nima's Deep Trust

**Action**: Player demonstrates high Empathy and makes vulnerable choices.

**Immediate Ripple** (0.8 weight):

- Ravi's trust deepens further. He feels validated in trusting the player.
- Dialogue shift: "She sees you clearly. So do I now."

**Secondary Ripples** (0.5 weight):

- Shrine keepers soften. Sera begins to trust more quickly.
- Glyph chambers near shrines open more easily.

**Tertiary Ripples** (0.4 weight):

- Mariel notices the player's emotional maturity. She shares deeper lore.
- Access to Elder Memories unlocks.

### Example 3: Player Sides with Kaelen Against Veynar

**Action**: Player withholds intel from Captain Veynar, protecting Kaelen.

**Immediate Ripples**:

- Kaelen's trust rises (0.9 sphere). He offers optional quest: Hunt the Thieves' Gang Leader.
- Veynar's trust drops. Guards become suspicious.

**Secondary Ripples**:

- Merchants become anxious. Theft rumors spread.
- Korrin's gossip network activates. Reputation shifts.
- Ravi becomes torn—he trusts the player, but fears Kaelen's influence.

**Tertiary Ripples**:

- Shrine keepers approve of defiance against authority.
- Dalen the Guide respects the player's boldness.
##

## Repair Mechanics: Sphere Healing

### Minor Ruptures (Easy Repair)

**Example**: Ignoring Ravi's warnings, failing to listen to Nima.

**Repair Path**:

- Show consistency: return items, listen actively, demonstrate restraint.
- Timeline: 1-2 marketplace encounters.
- Outcome: Partial trust restoration. Ravi opens dialogue, Nima softens slightly.

### Major Ruptures (Difficult Repair)

**Example**: Betraying Ravi to guards, coldly dismissing Nima's fears.

**Repair Path**:

- Requires sacrifice: player must prove sincerity through costly choice.
- For Ravi: Sacrifice a valuable glyph fragment to honor marketplace trust.
- For Nima: Risk resonance loss in another encounter to show vulnerability.
- Timeline: 3-4 encounters, significant emotional investment.
- Outcome: Trust restored, but dialogue shifts: "I'll trust you, but I'll never forget."

### Ripple Healing

**Mechanic**: Repairing trust with one NPC can heal ripples across their sphere.

**Example**: Reconciling with Nima (0.8 weight) can automatically soften Sera and shrine keepers (0.5 ripple). Healing spreads like trust itself.
##

## Dynamic Sphere Shifts

### Seasonal Shifts (In-Game Time)

Sphere weights can shift based on in-game time and events:

- After market collapses: Veynar's authority weakens (weight 0.4), Dalen's influence rises (0.5).
- After player defeats Drossel: Kaelen's sphere dissolves, guard sphere strengthens.
- After emotional breakthroughs: Mariel's sphere expands as elder wisdom spreads.

### Event-Triggered Shifts

- **Kaelen's Theft**: Korrin's gossip network activates, merchant sphere fractures.
- **Nima's Breakdown**: Ravi's concern rises, his ripple to merchants increases (0.5 → 0.6).
- **Dalen's Challenge**: Ravi's caution rises, his weight to Dalen lowers (0.3 → 0.1).
##

## Implementation Notes

- [ ] Track NPC resonance scores separately (hidden from player).
- [ ] Calculate ripple effects whenever a major choice affects a sphere.
- [ ] Show visual/audio cues when sphere shifts (NPC dialogue changes, ambient soundscape shifts).
- [ ] Design merchant prices to rise/fall based on sphere trust.
- [ ] Create "sphere stability" meter (dev tool) to test cascade effects.
- [ ] Test repair paths for each major NPC.
- [ ] Ensure ripple effects feel organic, not mechanical.
##

## Sphere Philosophy

The sphere system exists to make the world feel alive, interconnected, and responsive to player choices. An NPC is never isolated—they're always part of a web of relationships. Breaking one thread can unravel an entire tapestry, or healing one thread can mend many others.

This models real human communities: trust spreads, betrayal ripples, and repair is communal, not individual.
