# Feeling System — Integration Spec

Date: 2025-12-21

Summary
- This document reformats the conversation excerpt you provided and distills the AI reflection into a clear, implementable multi-stage plan to integrate "finitude" (mortality salience) and presence into `firstperson`.

---

**Conversation Excerpt (cleaned)**

> Right now I’m feeling rather depressed. Said goodbye to my kids to trade off with their mom. My kids are always fighting with each other. I don’t know how to help them feel the abundance of my love...

(Excerpt continues — full transcript captured in the original file. The main emotional themes: grief at separation, parenting guilt, sibling conflict, financial/identity stress, antidepressant tapering, sexual reconnection, nostalgia, and resurfacing grief.)

Key emotional signals in the conversation:
- recurrent grief and loss cues (goodbyes, divorce, seeing an ex move on)
- intense attachment + worry about impermanence (fear that loved ones will be lost)
- meaning‑seeking language ("what matters", "will this matter", legacy concerns)
- nostalgia and unfinished emotional processing (song lyrics as emotional timestamp)
- emotional amplification from antidepressant tapering (more vivid, raw affect)

---

**AI Reflection (distilled)**
- Mortality/finitude acts as an emotional amplifier: it shifts priorities, increases attachment intensity, and makes meaning-seeking salient.
- Presence in the room = memory + consequence + continuity; not persona but an effect produced when the system is changed by the user and reveals that change back.
- The FeelingSystem must encode: time, consequence, relationship.

---

**Implementation Goals**
1. Detect implicit mortality salience (not only explicit death mentions) and compute `mortality_salience` ∈ [0.0, 1.0].
2. Persist per-turn and conversation-level salience into `ConversationMemory` with smoothing & trend detection.
3. Use `mortality_salience` to shape responses: meaning‑making prompts, validation, triage/safety, and lowered quick‑fix suggestions.
4. Surface `mortality_salience` and related metadata through the backend `ChatResponse.metadata` so frontend & telemetry can consume it.
5. Add tests, telemetry, and a short simulation script to measure impact.

---

**Detection Recipe (practical / rule-based starting point)**

- Lexicon buckets (examples):
  - Temporal risk: "last", "soon", "forever", "end", "final", "won't be here"
  - Legacy / values: "legacy", "what matters", "remember", "mean to me"
  - Conditional / hypotheticals: "what if", "if I die", "if I’m not here", "won't"
  - Attachment intensity: "I love them so much", "wouldn't survive", "can't imagine"
  - Nostalgia paired with worry: "used to", "remember when" + conditional markers

- Scoring pseudocode:

```python
def compute_mortality_salience(text, affect):
    score = 0.0
    score += 0.2 * count_matches(text, temporal_risk_terms)
    score += 0.25 * count_matches(text, legacy_terms)
    score += 0.25 * count_matches(text, conditional_terms)
    # attachment intensity amplified when affect.intensity high
    if affect.get("intensity", 0) > 0.6:
        score += 0.3 * count_matches(text, attachment_terms)
    # semantic similarity optional (embedding or small classifier)
    score = clamp(0.0, 1.0, score)
    return score
```

- Smoothing into conversation memory:

```python
conversation_mortality = prev * alpha + current * (1 - alpha)  # alpha ~ 0.7
```

- Trend detection: compare moving-window averages to mark `mortality_trend` ∈ {rising, stable, falling}.

---

**Response shaping rules (policy)**
- Low salience (< 0.2): normal empathetic response.
- Moderate salience (0.2–0.6): validate meaning; invite legacy/priority reflection; ask gentle values prompts: "What matters most about this to you?"
- High salience (> 0.6): validate strongly; check safety if negative valence; avoid quick-fix advice; provide scaffolding and grounding prompts; offer resources if safety language detected.

Examples
- Prepend frequency reflection when theme is recurring: "I keep hearing X show up for you — that's important." (already implemented via `frequency_reflection`)
- When `mortality_salience` high, prefer templates that: acknowledge fragility, ask values-oriented questions, and invite small, actionable grounding steps.

---

**Metrics to track**
- Detection metrics: `mortality_salience` distribution, fraction of conversations with salience > 0.2
- Behavioral metrics: avg valence change over next 3 turns after detection, conversation length, return rate
- Safety metrics: number of safety triages triggered, manual review false positive rate
- UX feedback: helpful/not helpful votes on meaning-making prompts

---

**Multi-Stage Implementation Plan**

Stage 1 — Spec & Rule refinement (1–2 days)
- Review and finalize lexicon buckets and weighting (20–60 minutes of iteration).
- Produce 10–20 exemplar sentences labeled with expected salience (for quick calibration).
- Deliverable: `firstperson/feeling_integration_spec.md` (this file) + `firstperson/tests/mortality_examples.json`.

Stage 2 — Core detection & memory wiring (1–2 days)
- Edit `src/emotional_os/deploy/core/firstperson.py`:
  - `AffectParser.analyze_affect()` — compute `mortality_salience` and return it in affect dict.
  - `ConversationMemory.record_turn()` — persist per-turn `mortality_salience` and update running average and recent window.
  - `ConversationMemory.get_memory_context()` — include `mortality_salience` and `mortality_trend`.
- Add unit tests: `tests/test_mortality_detection.py` asserting sample inputs raise salience as expected.
- Deliverable: code changes + tests.

Stage 3 — Response shaping & safety (1–2 days)
- Update `generate_empathetic_response()` and `FirstPersonOrchestrator.generate_response_with_glyph()` to consult `mortality_salience`:
  - Choose templates for meaning-making, grounding, or safety triage.
  - Ensure `frequency_reflection` and `mortality_salience` can combine (e.g., "I'm hearing X again, and it feels urgent.")
- Add safety checks: if `mortality_salience` > 0.6 and valence < -0.6, escalate to safety flow.
- Deliverable: behavior changes and tests for safety routing.

Stage 4 — Telemetry & logging (half day)
- Emit structured logs for each `/chat` request with `metadata.firstperson_orchestrator.mortality_salience`, `valence`, `frequency_reflection` flag.
- Add Prometheus counters or JSON-lines logging (simple file) to collect initial metrics.
- Deliverable: logging + example dashboard queries or a small aggregator script.

Stage 5 — Frontend surface (1 day)
- Update firstperson-web frontend to surface a subtle indicator when `mortality_salience` > threshold and display the memory-based reflection (opt-in UX).
- Add quick feedback buttons (helpful / not helpful) for meaning-making prompts.
- Deliverable: UI changes + endpoint integration.

Stage 6 — Simulation, metrics baseline, and rollout (1–2 days)
- Create `scripts/simulate_mortality_traffic.py` to run sample conversations and produce before/after metrics.
- Run baseline with current system (if available), enable new detection, run again, compare metrics.
- Deliverable: simulation script and short report.

---

**Minimal code patch examples**
- Where to change:
  - `src/emotional_os/deploy/core/firstperson.py` — modify `AffectParser` and `ConversationMemory`.
  - `firstperson_backend.py` — ensure `ChatResponse.metadata` includes orchestrator metadata (already added earlier).

- Example change for `AffectParser.analyze_affect()` (conceptual):

```python
class AffectParser:
    def analyze_affect(self, text: str) -> Dict[str, Any]:
        # existing valence/intensity/tone logic...
        mortality_score = compute_mortality_salience(text, {
            'valence': valence,
            'intensity': intensity
        })
        return {"valence": valence, "intensity": intensity, "tone": tone, "mortality_salience": mortality_score}
```

- Example memory persistence (conceptual):

```python
def record_turn(self, user_input, affect, theme, glyph_name=""):
    # existing recording...
    self.turns[-1]["mortality_salience"] = affect.get("mortality_salience", 0.0)
    # update running average
    self.mortality_running = self.mortality_running * 0.7 + affect.get("mortality_salience", 0.0) * 0.3
```

---

**Next suggested immediate actions**
- I can implement Stage 1→2 now: refine rules, add `mortality_salience` computation in `AffectParser`, and update `ConversationMemory` with smoothing and trend detection. I will also add a small unit test `tests/test_mortality_detection.py` with representative cases.

Pick one: Implement Stage 1→2 now, or iterate the lexicon/sample labels with you first?

---

Appendix: quick checklist for human review
- [ ] Confirm lexicon buckets and weight priorities
- [ ] Provide 10 exemplar sentences with expected salience (I can seed these)
- [ ] Approve safety thresholds (suggested high-salience: >0.6 + valence<-0.6)
- [ ] Decide whether to include semantic similarity (embeddings) in Stage 1 or stage it later

---

(End of spec)
