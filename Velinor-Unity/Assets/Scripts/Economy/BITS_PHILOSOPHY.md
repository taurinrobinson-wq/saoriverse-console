# Bits: Intentional Abstraction, Not Simulation

## Why We Don't Answer Certain Questions

The temptation in game design is to build *consistent simulation* – to answer "how does the banking system work?" or "what are coins made of?" until you have a complete economic model.

**For Velinor, we deliberately don't.**

Bits are simple, abstract currency because the *story doesn't need currency simulation*. The story needs:

1. **A unit of exchange** – "Bits" is sufficient
2. **Motivation to trade** – NPCs want specific things
3. **Growth through contribution** – Lioren earns bits through work

That's it. Everything else is scope creep disguised as worldbuilding.

---

## What Bits Are

### Established in Dialogue
```
Willy: "Got any bits?"
Lioren: "Bits?"
Willy: "Money. Stuff people'll actually take around here."
```

That single exchange tells the player:
- Bits are money
- Bits are accepted in the marketplace
- Bits are how the post-collapse economy works

Nothing else needs to be said.

### Stored as an Integer
```csharp
int bits = 14;  // Not a complex object, not coins, not accounts
```

Bits don't occupy inventory slots. They're a resource displayed at the top:

```
━━━━━━━━━━━━━━━━━
    BITS  37
━━━━━━━━━━━━━━━━━
Copper Wire        8
Motor Parts        3
```

---

## What Bits Are NOT

### Not Physical Coins
- No denominations (1-bit, 5-bit, 20-bit)
- No minting mechanics
- No how-they-were-made explanation
- No "find 4 bits lying around" pickups

**Why:** Coins require answering questions about metallurgy, historical origin, counterfeiting, storage, loss, and a hundred other things the story doesn't care about.

### Not Digital Currency
- No ledger system
- No account tracking
- No double-spend prevention
- No cryptocurrency mechanics

**Why:** Digital currency requires explaining how the technology works in a broken infrastructure. That's worldbuilding work with zero story payoff.

### Not a Simulation
- No inflation/deflation
- No supply/demand curves
- No NPC wealth pools
- No interest rates

**Why:** Players don't experience or care about macroeconomics. They care about *this trade* with *this person right now*.

---

## What Actually Matters

### Rule 1: Bits Are the Unit of Exchange
Everyone uses bits. No barter. No credit systems. Just bits.

This removes complexity. A copper wire is worth 4 bits to a neutral merchant, 6 bits to Willy (because he wants electrical salvage), and 0 bits to someone who refuses to buy metal.

### Rule 2: Lioren Earns Bits Through Work
- Trade salvage with NPCs
- Complete tasks
- Provide services
- Receive payment in bits

No "loot coins from corpses." No "break pots for currency." Bits are *earned*, making them narratively significant. Lioren's first bits aren't just game resources – they're her first money in this community.

### Rule 3: Bits Are Exchanged for Goods, Services, and Tools
Willy pays bits. Tala trades bits for meals. A tool costs bits.

That's the complete economy.

---

## The Elegant Part: Who Values What

The interesting economy isn't *how bits work*.

It's **who wants what** and **why**.

```
Copper Wire

Base Value: 4 bits

Willy (scrapper):           6 bits (he wants electrical salvage)
Tala (cook):                2 bits (not useful to her)
Electrician:               10 bits (she specifically needs this)
Random stranger:            4 bits (standard rate)
```

Same object. Different value to different people.

This expresses **community** far better than realistic economic simulation ever could.

It says: *"Your salvage matters to this person because it solves their problem."*

Later, someone might give Lioren a skill instead of bits. Another NPC might repay her later. Someone she helped might say, "Take it. You earned it."

**That's the economy that matters.**

---

## Design Rules

1. **Only model what the story uses**
   - Currency? Yes (NPCs trade items for bits)
   - Denominations? No (story never references them)
   - Historical origin? No (Willy's explanation is enough)

2. **Never create mechanics for worldbuilding questions**
   - "How are bits backed?" is not a gameplay question
   - "Who controls the money supply?" doesn't affect gameplay
   - "How many bits exist?" doesn't matter

3. **Keep currency simple**
   - One data type: `int bits`
   - One rule: earn through trade, spend on goods
   - One UI element: "BITS 37"

4. **Make NPC preferences tell the story**
   - Willy wants salvage → he's a scrapper
   - Tala wants food ingredients → she's a cook
   - Someone wants old tech → they're rebuilding infrastructure
   - Someone wants medicine → they're a healer

Let preferences do the characterization. Don't explain it in a tutorial or quest log.

---

## What This Enables

### Simplicity
- One integer to track
- No slot management for currency
- No denomination math
- No conversion tables

### Flexibility
- Easy to adjust NPC prices for balancing
- Easy to add new NPCs with different preferences
- Easy to change what things are worth
- Zero lock-in from prior economic decisions

### Narrative Clarity
- Bits are introduced diegetically (in dialogue)
- They're used naturally (trade with Willy)
- They're never explained mechanically
- Player never wonders about the system

### Scalability
- Works for 2 NPCs or 20
- Works if every item has a value or only some
- Works if Lioren earns 1 bit or 1000
- Works whether game is 2 hours or 20

---

## Common Question: Won't Players Wonder About X?

**Q: Won't they wonder where Bits come from?**

A: Willy tells them: "Money. Stuff people'll actually take." That's enough. Players accept currency in games without detailed explanation.

**Q: What if they find loose bits lying around?**

A: Don't have pickups be "5 bits lying in the rubble." Instead, break down a machine and receive specific items (gear, wire, metal). Trade those items for bits. The bits come from work, not luck.

**Q: Why doesn't everyone just take what they want?**

A: Because the story doesn't explore that. If the game wanted to address scarcity and theft, it would. It doesn't, so we don't model it. Assumptions don't need to be answered.

**Q: Shouldn't NPCs run out of money?**

A: Only if the story requires it. No NPC budget tracking. If Willy needs to be unavailable, use story/dialogue reasons, not "he spent all his bits."

---

## Implementation Checklist

✓ CurrencySystem tracks `int bits`  
✓ Earn/Spend fire events  
✓ PlayerPrefs persistence  
✓ NPCTradeProfile multiplies prices by preference  
✓ Bits UI shows integer balance  
✓ No denominations  
✓ No physical coin model  
✓ No "bits lying around" pickups  
✓ Documentation reflects: Bits are abstract, preference-driven  

---

## The Bottom Line

**Bits are not a system to simulate. They're a tool to express what NPCs want.**

When Lioren trades wire to Willy and gets 6 bits instead of 4, the player learns:

*"Willy specifically values what I just found. This community recognizes its value through him."*

That's the interesting economy. Not ledgers. Not denominations. Not the Central Bank of Velinor.

Just: **Who values what. And why.**

Everything else is a distraction.
