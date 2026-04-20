# DraftShift Architecture: System Design & Stack

## 🏗️ System Architecture Overview

DraftShift is built as a **modular, privacy-first** civility analysis engine. The system flows from
analysis → transformation → compliance scoring, with the attorney always in control at the final
decision point.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Attorney's Device                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  1. INPUT LAYER                                          │   │
│  │  - Correspondence textarea                               │   │
│  │  - Mode selector (civility/litigation/client-friendly)   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  2. ANALYSIS LAYER (Local, No Cloud)                     │   │
│  │  ├─ spaCy: Tokenization, entity recognition, syntax      │   │
│  │  ├─ TextBlob: Sentiment polarity, subjectivity           │   │
│  │  ├─ NRC Lexicon: Emotion detection (14,154 words)        │   │
│  │  └─ Lightweight signal parser: 7 tone signals (α-Ω)     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  3. LOCAL LLM TRANSFORMATION LAYER                        │   │
│  │  - GPT4All / Mistral / Llama 3 (quantized)               │   │
│  │  - Generates civility-compliant rewrites                 │   │
│  │  - No per-token fees; runs locally                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  4. GLYPH MAPPING LAYER                                  │   │
│  │  - Converts analysis signals into symbolic glyphs        │   │
│  │  - ⚖️ Integrity, 🌿 Courtesy, ⚠️ Aggression              │   │
│  │  - Visual overlays for dashboard                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  5. CIVILITY DASHBOARD                                   │   │
│  │  - Civility Score (0-100)                                │   │
│  │  - Risk alerts, glyph map, suggested rewrites            │   │
│  │  - Disclaimer banner (persistent)                        │   │
│  │  - Attorney review & approval before sending             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│                    [Attorney Final Decision]                      │
│                    ✅ Send / ❌ Revise / 🔄 Regenerate           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

                        NO EXTERNAL CALLS
                        NO CLOUD STORAGE
                        ATTORNEY CONTROL
```

---

## 📦 Technology Stack

### Analysis Layer (Linguistic Foundation)
| Component | Purpose | Why It Fits |
|-----------|---------|------------|
| **spaCy** | Tokenization, POS tagging, entity recognition | Fast, accurate, no server dependency. |
| **TextBlob** | Sentiment polarity (-1 to +1), subjectivity (0-1) | Pure Python, lightweight, perfect for quick sentiment checks. |
| **NRC Lexicon** | Emotion detection (anger, joy, trust, sadness, etc.) | 14,154 word-emotion associations; supports detailed emotion analysis. |
| **Lightweight Signal Parser** | 7-signal tone detection (α-Ω) | Custom pattern-based; no DB dependency; <50ms per analysis. |

### Transformation Layer (Local LLM)
| Option | Strengths | Use Case in DraftShift |
|--------|-----------|----------------------|
| **GPT4All** | Simple installer, quantized models, Python bindings | Quick prototyping, MVP deployment. |
| **LM Studio** | GUI-based, OpenAI-compatible API, GGUF model support | Development & testing of rewrites. |
| **text-generation-webui** | Flexible backends, supports multiple quantization formats | Experimentation with different models. |
| **KoboldCPP** | Lightweight C++ backend, efficient GGUF execution | Production deployment on modest hardware. |
| **Mistral 7B Instruct** (quantized) | Excellent instruction-following, 7B param size (4GB quantized) | Recommended model for civility transformations. |

### Frontend (Phase-Based)
| Phase | Technology | Purpose |
|-------|-----------|---------|
| **Phase 1 (MVP)** | Streamlit | Rapid prototyping; focus on logic, not UI. |
| **Phase 2 (Beta)** | FastAPI backend + React frontend | Production-ready, scalable, maintainable. |
| **Phase 3 (Scale)** | Full HTML/JS + Electron/PWA | Desktop/web app with advanced dashboard. |

### Data & Privacy
- **No external APIs**: All processing local.
- **No storage by default**: Correspondence analyzed in-memory only.
- **Optional local persistence**: User can opt-in to archive (stored encrypted locally only).
- **No telemetry**: Zero tracking or analytics collection.

---

## 🔄 Data Flow Pipeline

### Step 1: Input & Preprocessing
```
Raw Correspondence
       ↓
Character encoding normalization
       ↓
Sentence tokenization (spaCy)
       ↓
Ready for analysis
```

### Step 2: Multi-Method Analysis
```
Tokenized Text
  ├─→ spaCy Linguistic Analysis
  │   ├─ Part-of-speech tags
  │   ├─ Entity recognition
  │   └─ Dependency parsing
  │
  ├─→ TextBlob Sentiment
  │   ├─ Polarity (-1 to +1)
  │   └─ Subjectivity (0-1)
  │
  ├─→ NRC Emotion Detection
  │   ├─ Word-level emotion scores
  │   └─ Aggregate emotion profile
  │
  └─→ Lightweight Signal Parser
      ├─ 7 tone signals (α-Ω)
      ├─ Marker detection
      └─ Tone profile synthesis
```

### Step 3: Local LLM Transformation
```
Analysis Results + Original Text
       ↓
Prompt Engineering (mode-specific)
       ↓
Local LLM Generation (Mistral 7B)
       ↓
Civility-Compliant Rewrite
```

### Step 4: Glyph Mapping
```
Analysis Signals
       ↓
Signal-to-Glyph Encoding
  ├─ High aggression → ⚠️ (red)
  ├─ Balanced assertiveness → ⚖️ (yellow)
  ├─ Courtesy indicators → 🌿 (green)
  └─ Integrity signals → ✓ (blue)
       ↓
Visual Dashboard Overlay
```

### Step 5: Civility Scoring & Dashboard
```
Analysis + Glyphs + Sentiment + Emotions
       ↓
Weighted Civility Algorithm
  ├─ Polarity weight (30%)
  ├─ Emotion profile weight (30%)
  ├─ Signal balance weight (20%)
  ├─ Subjectivity weight (10%)
  └─ Modifier weight (10%)
       ↓
Civility Score (0-100)
       ↓
Risk Alert Classification
  ├─ Green (80-100): Compliant, send
  ├─ Yellow (60-79): Review suggested rewrites
  └─ Red (0-59): Major changes recommended
       ↓
Display Dashboard + Attorney Decision
```

---

## 🎯 Design Philosophy

### Privacy-First
- **All processing local**: No API calls, no cloud dependencies.
- **No persistent storage by default**: In-memory analysis only.
- **User control**: Attorney decides what to save, share, or delete.
- **Compliance-ready**: Zero risk of attorney-client privilege violation.

### Attorney-Centric
- **Suggestion, not mandate**: All recommendations are optional.
- **Full transparency**: Explains why civility score is what it is.
- **Preserves judgment**: Attorney always makes final decision.
- **Respects expertise**: Tool augments legal skill, doesn't replace it.

### Performance-First
- **Sub-100ms analysis**: Fast enough for real-time feedback.
- **Lightweight models**: Quantized, no GPU required.
- **Graceful degradation**: Works even if components fail.
- **Scalable**: Can handle 1000+ documents without performance loss.

---

## 🔌 Component Integration Points

### How Modules Talk to Each Other

```
┌─────────────────────────────────┐
│  Core (litone/draftshift)       │
│  - detect_tone()                │
│  - shift_tone()                 │
│  - get_tool_status()            │
└──────────────┬──────────────────┘
               │
       ┌───────┴────────┬──────────────┬─────────────────┐
       ↓                ↓              ↓                 ↓
   ┌────────────┐  ┌──────────┐  ┌──────────────┐  ┌──────────────┐
   │ Enhanced   │  │ Tone     │  │ Constants &  │  │ Signal       │
   │ Affect     │  │ Analysis │  │ Signals      │  │ Parser       │
   │ Parser     │  │ Composer │  │              │  │              │
   └────────────┘  └──────────┘  └──────────────┘  └──────────────┘
       │                │              │                 │
       └────────────────┴──────────────┴─────────────────┘
                       ↓
            ┌──────────────────────┐
            │ Dashboard / UI Layer │
            └──────────────────────┘
```

### Module Responsibilities
- **Enhanced Affect Parser**: Multi-source emotion & valence analysis.
- **Tone Analysis Composer**: Contextual transformation guidance.
- **Signal Parser**: 7-signal tone detection.
- **Constants**: Centralized signal/tone/pattern definitions.
- **Core**: Orchestrates analysis, coordinates modules, exposes public API.

---

## 📊 Performance Characteristics

| Operation | Time (ms) | Notes |
|-----------|-----------|-------|
| Tokenization (spaCy) | 5-10 | Per 100 words |
| Sentiment (TextBlob) | 2-5 | Per 100 words |
| Emotion detection (NRC) | 10-20 | Per 100 words |
| Signal parsing | 5-15 | Per 100 words |
| Local LLM inference | 500-2000 | Depends on model & hardware |
| **Total Analysis** | 22-50 | All methods, no LLM |
| **Full Pipeline** | 500-2050 | Includes transformation |

---

## 🔐 Security & Privacy Model

### Data Handling
- **In Transit**: Not applicable (local only).
- **At Rest**: Optional encrypted local storage only.
- **Processing**: All analysis in-memory, never written to disk unless user chooses.
- **Sharing**: Attorney controls export; no automatic uploads.

### Threat Model
| Threat | Mitigation |
|--------|-----------|
| Malware accessing correspondence | Local firewall; user OS security. |
| Data exfiltration | No network calls; code is open-source for audit. |
| Privilege compromise | Requires local system access; same as any app. |
| Supply chain attack | Curated dependencies; regular audits recommended. |

### Compliance
- **Attorney-Client Privilege**: Never violated (no external APIs).
- **GDPR/Privacy Laws**: User has full data control.
- **Bar Association Rules**: Complies with legal ethics tech guidelines.

---

This architecture ensures DraftShift is **fast, private, and attorney-controlled**—exactly what
legal professionals need.
