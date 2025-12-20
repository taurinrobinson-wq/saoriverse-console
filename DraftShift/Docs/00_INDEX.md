# DraftShift Documentation Index

## Overview

Welcome to DraftShift—a civility compliance engine designed for legal professionals navigating California's Rule 9.7 and similar professional ethics requirements.

**Quick Links:**

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [01_PRODUCT_STRATEGY.md](01_PRODUCT_STRATEGY.md) | Market opportunity, positioning, use cases, go-to-market | 15 min |
| [02_ARCHITECTURE.md](02_ARCHITECTURE.md) | System design, tech stack, data flow, component integration | 20 min |
| [03_LOCAL_LLM_STACK.md](03_LOCAL_LLM_STACK.md) | LLM options comparison, selection rationale, integration guide | 20 min |
| [04_API_SPECIFICATION.md](04_API_SPECIFICATION.md) | FastAPI contract, endpoint definitions, request/response schemas | 25 min |
| [05_UI_UX_DESIGN.md](05_UI_UX_DESIGN.md) | Dashboard wireframes (Streamlit, React, HTML/JS), component tree | 20 min |
| [06_DEVELOPMENT_PHASES.md](06_DEVELOPMENT_PHASES.md) | Phased roadmap (MVP→Beta→Enterprise), resource estimates, gates | 25 min |
| [07_MASTER_ROADMAP.md](07_MASTER_ROADMAP.md) | Implementation checklist, task breakdown, milestones, next steps | 30 min |

---

## 🚀 Quick Start: Where to Begin?

### If you're a developer (starting Phase 1):
1. Read [02_ARCHITECTURE.md](02_ARCHITECTURE.md) to understand the current state
2. Read [03_LOCAL_LLM_STACK.md](03_LOCAL_LLM_STACK.md) to choose your LLM
3. Go to [07_MASTER_ROADMAP.md](07_MASTER_ROADMAP.md) → Phase 1 section for task checklist

### If you're a product/business person:
1. Read [01_PRODUCT_STRATEGY.md](01_PRODUCT_STRATEGY.md) for market context
2. Read [06_DEVELOPMENT_PHASES.md](06_DEVELOPMENT_PHASES.md) for timeline + resources
3. Refer to [07_MASTER_ROADMAP.md](07_MASTER_ROADMAP.md) for gates + success metrics

### If you're designing the UI/frontend:
1. Read [05_UI_UX_DESIGN.md](05_UI_UX_DESIGN.md) for wireframes + component tree
2. Read [04_API_SPECIFICATION.md](04_API_SPECIFICATION.md) to understand the backend contract
3. Refer to Phase 1/2/3 descriptions in [06_DEVELOPMENT_PHASES.md](06_DEVELOPMENT_PHASES.md)

### If you're evaluating legal/compliance aspects:
1. Read [01_PRODUCT_STRATEGY.md](01_PRODUCT_STRATEGY.md) for positioning
2. Search for "disclaimer" and "attorney control" in [02_ARCHITECTURE.md](02_ARCHITECTURE.md) and [05_UI_UX_DESIGN.md](05_UI_UX_DESIGN.md)
3. Review compliance checklist in [07_MASTER_ROADMAP.md](07_MASTER_ROADMAP.md)

---

## 📋 Core Principles (Read These First)

### Privacy-First
- All processing happens locally on the attorney's device
- No API calls to external services
- No storage of correspondence by default
- User controls what is saved, shared, or deleted

### Attorney-Centric
- Tool suggests; attorney decides
- Full transparency into why civility score is what it is
- Preserves professional judgment
- Augments expertise, doesn't replace it

### Civility as Measurable Discipline
- Transforms abstract "civility oath" into actionable metrics
- Provides real-time feedback on correspondence tone
- Tracks patterns over time for compliance reporting
- Supports California Rule 9.7 annual declarations

### No Breaking Changes
- Existing DraftShift analysis modules (spaCy, TextBlob, NRC, signals) are **already working**
- All new features layer on top without modifying core
- Backward compatibility maintained across phases

---

## 🏗️ Current State of DraftShift

### ✅ Complete (Already Implemented)
- Core analysis modules: `enhanced_affect_parser.py`, `tone_signal_parser.py`, `tone_analysis_composer.py`
- Lightweight 7-signal tone detection (α-Ω signals)
- NRC lexicon integration (14,154 words)
- spaCy + TextBlob multi-method analysis
- Constants + legal-specific markers
- Integration tests in `draftshift/Tests/`
- All modules in `draftshift/` folder, consolidated with documentation

### ⏳ Next: Phase 1 (Months 1-3)
- LLM integration (GPT4All + Mistral 7B)
- Civility scoring algorithm
- Risk alert generation
- Streamlit MVP app

### 🔮 Future: Phase 2-3
- Production backend (FastAPI + React)
- Enterprise features (multi-tenant, SAML, analytics)

---

## 📊 Decision Matrix: Which Phase Do You Need?

| Scenario | Phase | Use Case |
|----------|-------|----------|
| **Prototype / Proof-of-Concept** | 1 (MVP) | Validate civility scoring concept with lawyers |
| **Beta / Early Adopters** | 2 (Beta) | Deploy to 20-30 law firms for testing |
| **Production / Scale** | 3 (Enterprise) | Firm-wide deployment, compliance dashboards |

---

## 🔐 Legal & Compliance Notes

### What DraftShift Does NOT Do
- Generate legal advice
- Replace attorney judgment
- Store attorney-client privileged correspondence (unless user opts in)
- Make final decisions about sending correspondence

### What DraftShift DOES Do
- Analyze tone/civility of correspondence
- Suggest alternative phrasings
- Track civility metrics over time
- Support Rule 9.7 compliance documentation

### Disclaimer
All phases include this persistent disclaimer:
> DraftShift does not replace the role of an attorney or ethics consultant. This application is intended only to suggest alternative ways to draft correspondence for different audiences and emotional/professional context. DraftShift highly recommends that any text suggested be thoroughly vetted before sending it to its intended recipient to ensure it accurately and professionally conveys the intended message. No raw text is stored by DraftShift and any learning and improvements made by the system are only with full consent of you, the user.

---

## 📞 Quick Reference

### Repository Structure
```
draftshift/
├── __init__.py                    # Package initialization
├── core.py                        # Main API (detect_tone, shift_tone, etc.)
├── constants.py                   # Legal signals & patterns
├── enhanced_affect_parser.py      # Emotion detection (NRC + TextBlob + spaCy)
├── tone_analysis_composer.py      # Transformation guidance
├── tone_signal_parser.py          # 7-signal detection (α-Ω)
├── Docs/                          # THIS FOLDER (comprehensive guides)
│   ├── 01_PRODUCT_STRATEGY.md     # Market, positioning, value prop
│   ├── 02_ARCHITECTURE.md         # System design, tech stack
│   ├── 03_LOCAL_LLM_STACK.md      # LLM options, selection
│   ├── 04_API_SPECIFICATION.md    # FastAPI endpoints
│   ├── 05_UI_UX_DESIGN.md         # Wireframes, component tree
│   ├── 06_DEVELOPMENT_PHASES.md   # Phased roadmap
│   ├── 07_MASTER_ROADMAP.md       # Implementation checklist
│   └── 00_INDEX.md                # This file
└── Tests/                         # Integration tests
    ├── test_litone_integration.py
    └── verify_setup.py
```

### Key Modules to Know

**draftshift.core**
```python
from draftshift import core
analysis = core.detect_tone("Your correspondence here")
print(analysis['tone'])  # Identified tone
print(analysis['confidence'])  # Confidence level
```

**draftshift.tone_signal_parser**
```python
from draftshift.tone_signal_parser import create_tone_signal_parser
parser = create_tone_signal_parser()
signals = parser.analyze_text("Legal text")
print(signals.primary_signal)  # α-Ω signal detected
```

**draftshift.enhanced_affect_parser**
```python
from draftshift.enhanced_affect_parser import create_enhanced_affect_parser
parser = create_enhanced_affect_parser()
emotions = parser.analyze("Your text")
print(emotions.primary_emotion)  # Joy, anger, trust, etc.
```

---

## 🎓 Learning Paths

### For Developers
1. Start with [02_ARCHITECTURE.md](02_ARCHITECTURE.md)
2. Review core modules in `draftshift/` folder
3. Go to [07_MASTER_ROADMAP.md](07_MASTER_ROADMAP.md) → Phase 1 section
4. Pick your first task from the checklist

### For Product Managers
1. Read [01_PRODUCT_STRATEGY.md](01_PRODUCT_STRATEGY.md)
2. Review [06_DEVELOPMENT_PHASES.md](06_DEVELOPMENT_PHASES.md) for timelines
3. Check gates/milestones in [07_MASTER_ROADMAP.md](07_MASTER_ROADMAP.md)
4. Coordinate with dev team on Phase 1 kickoff

### For Designers
1. Review [05_UI_UX_DESIGN.md](05_UI_UX_DESIGN.md) wireframes
2. Study component tree (Phase 2 section)
3. Read [04_API_SPECIFICATION.md](04_API_SPECIFICATION.md) to understand data
4. Design Phase 1 Streamlit mockups or Phase 2 React Figma file

### For Legal/Compliance Review
1. Read [01_PRODUCT_STRATEGY.md](01_PRODUCT_STRATEGY.md) for market context
2. Review all references to "disclaimer" and "attorney control"
3. Check "Legal & Compliance Checklist" in [07_MASTER_ROADMAP.md](07_MASTER_ROADMAP.md)
4. Flag any concerns for product/dev team

---

## 🚦 Status & Next Steps

**Current Status:** Core modules complete; ready to begin Phase 1 (LLM integration + Streamlit).

**Next Immediate Steps:**
1. ✅ Understand the architecture ([02_ARCHITECTURE.md](02_ARCHITECTURE.md))
2. ✅ Choose your LLM backend ([03_LOCAL_LLM_STACK.md](03_LOCAL_LLM_STACK.md))
3. → Recruit Phase 1 beta users (5-10 lawyers)
4. → Begin LLM integration task (from [07_MASTER_ROADMAP.md](07_MASTER_ROADMAP.md) Phase 1)
5. → Build Streamlit MVP

**Timeline to Launch:**
- Phase 1 MVP: Month 3
- Phase 2 Production: Month 6
- Phase 3 Enterprise: Month 12

---

## ❓ FAQ

**Q: Is the core analysis working now?**
A: Yes! All modules (spaCy, TextBlob, NRC, signals) are implemented and tested. Go to [02_ARCHITECTURE.md](02_ARCHITECTURE.md) for architecture overview.

**Q: What do I build first?**
A: LLM integration (Phase 1). See [07_MASTER_ROADMAP.md](07_MASTER_ROADMAP.md) Phase 1 section for exact tasks.

**Q: Can we skip Phase 1 and go straight to Phase 2?**
A: Not recommended. Phase 1 validates the concept quickly. Skip it only if you have strong user demand + resources for full Phase 2 (200+ hours).

**Q: How do we handle attorney-client privilege?**
A: All processing is local; no external APIs. No storage by default. See [02_ARCHITECTURE.md](02_ARCHITECTURE.md) "Privacy Model."

**Q: What's the civility scoring based on?**
A: Weighted algorithm combining sentiment polarity (30%), emotion profile (30%), signal balance (20%), subjectivity (10%), modifiers (10%). See [07_MASTER_ROADMAP.md](07_MASTER_ROADMAP.md) Phase 1.2 for details.

**Q: Can we deploy to the cloud?**
A: Phase 1-2 are local-only or single-tenant cloud. Phase 3 adds multi-tenant cloud support. See [06_DEVELOPMENT_PHASES.md](06_DEVELOPMENT_PHASES.md).

---

## 📞 Contact / Support

- **Architecture Questions**: Review [02_ARCHITECTURE.md](02_ARCHITECTURE.md)
- **Task Breakdown**: Check [07_MASTER_ROADMAP.md](07_MASTER_ROADMAP.md)
- **UI/Design Questions**: Read [05_UI_UX_DESIGN.md](05_UI_UX_DESIGN.md)
- **Market/Business Questions**: See [01_PRODUCT_STRATEGY.md](01_PRODUCT_STRATEGY.md)

---

**Welcome to DraftShift. Let's build civility compliance into every attorney's workflow.**

*Documentation Version: 1.0*  
*Last Updated: December 19, 2025*  
*Status: Ready for Phase 1 Implementation*
