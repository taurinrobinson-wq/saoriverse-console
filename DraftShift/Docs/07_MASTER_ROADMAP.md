# DraftShift Master Implementation Roadmap

## 📋 Executive Summary

This document synthesizes all DraftShift architecture, design, and phasing guidance into a single master roadmap. It details exactly what to build, in what order, with dependencies clearly mapped.

**Current State:** DraftShift core modules (analysis, signal parsing, affect parsing) are **working and tested** in draftshift/ folder.

**Next Steps:** Integrate local LLM + build Phase 1 Streamlit app → validate concept → Phase 2 React/FastAPI → Phase 3 enterprise.

---

## 🎯 Strategic Context

**Market Opportunity:**
- California Rule 9.7 requires attorneys to annually declare civility commitment.
- No existing tool maps correspondence against professional ethics.
- DraftShift fills this gap: civility compliance engine for legal professionals.

**Product Promise:**
- Real-time analysis of correspondence civility
- Actionable suggestions for improvement
- Privacy-preserving (all processing local)
- Attorney always in control

**Success Metric:**
- Adoption: 50+ users in Year 1 (California)
- Validation: Civility score improvements proven in law firm case studies
- Expansion: Multi-state + cross-professional rollout by Year 2

---

## 🏗️ Architecture at a Glance

```
┌─ ANALYSIS LAYER (Ready) ─────────────┐
│ spaCy + TextBlob + NRC + Signals     │
│ (All modules working in draftshift/)  │
└─────────────────────────────────────┘
              ↓
┌─ LLM TRANSFORMATION (Phase 1) ──────┐
│ GPT4All / Mistral 7B (local)         │
└─────────────────────────────────────┘
              ↓
┌─ CIVILITY SCORING (Phase 1) ────────┐
│ Weighted algorithm (analysis + glyphs│
└─────────────────────────────────────┘
              ↓
┌─ UI LAYER ──────────────────────────┐
│ Phase 1: Streamlit                   │
│ Phase 2: React + FastAPI             │
│ Phase 3: Electron + Full Dashboard   │
└─────────────────────────────────────┘
```

---

## 📅 Phase 1 Implementation: MVP (Months 1-3)

### Goal
Prove civility scoring + transformation works. Build Streamlit prototype. Validate concept with 5-10 beta users.

### What to Build

#### 1.1 LLM Integration Module
**File:** `draftshift/llm_transformer.py`

```python
from gpt4all import GPT4All

class LLMTransformer:
    def __init__(self, model_name="mistral-7b-instruct-v0.1.Q4_0.gguf"):
        self.model = GPT4All(model_name, device='cpu')
    
    def transform(self, text, mode="civility", max_tokens=500):
        """
        Transform text to target mode.
        
        Modes:
        - "civility": Generally more respectful
        - "litigation": Assertive, legally protective
        - "client-friendly": Empathetic, clear
        - "neutral-negotiation": Balanced, fair
        """
        prompts = {
            "civility": f"Rewrite this legal correspondence to be more respectful and professional while maintaining its core message:\n\n{text}",
            "litigation": f"Rewrite this to be more assertive and legally protective:\n\n{text}",
            "client-friendly": f"Rewrite this to be clear and empathetic for a client:\n\n{text}",
            "neutral-negotiation": f"Rewrite this to be balanced and fair-minded:\n\n{text}"
        }
        
        result = self.model.generate(prompts[mode], max_tokens=max_tokens)
        return result.strip()
```

**Tasks:**
- [ ] Install GPT4All: `pip install gpt4all`
- [ ] Test model download and inference
- [ ] Implement LLMTransformer class with prompt engineering
- [ ] Validate output quality (readable, legally sound)
- [ ] Add error handling for model not found

**Time Estimate:** 12 hours

---

#### 1.2 Civility Scoring Algorithm
**File:** Update `draftshift/core.py`

Add a `calculate_civility_score()` function:

```python
def calculate_civility_score(analysis):
    """
    Calculate civility score (0-100) from analysis results.
    
    Weighted algorithm:
    - Polarity: 30% (more positive = more civil)
    - Emotion profile: 30% (lower anger/fear = more civil)
    - Signal balance: 20% (balance aggression vs courtesy)
    - Subjectivity: 10% (lower = more professional/civil)
    - Modifiers: 10% (negation, sarcasm penalties)
    """
    
    polarity_score = (analysis['polarity'] + 1) / 2 * 100  # -1..1 → 0..100
    
    emotion_anger_penalty = analysis['emotions']['anger'] * 30
    emotion_fear_penalty = analysis['emotions']['fear'] * 15
    emotion_trust_bonus = analysis['emotions']['trust'] * 10
    emotion_joy_bonus = analysis['emotions']['joy'] * 10
    
    signal_aggression_penalty = analysis['signals']['aggression_strength'] * 20
    signal_courtesy_bonus = analysis['signals']['courtesy_strength'] * 15
    
    subjectivity_penalty = analysis['subjectivity'] * 10
    
    modifier_penalty = 0
    if analysis.get('has_negation_softening'):
        modifier_penalty -= 5
    if analysis.get('has_sarcasm'):
        modifier_penalty -= 15
    if analysis.get('has_all_caps'):
        modifier_penalty -= 10
    
    score = (
        polarity_score * 0.30 +
        (100 - emotion_anger_penalty - emotion_fear_penalty + emotion_trust_bonus + emotion_joy_bonus) * 0.30 +
        (100 - signal_aggression_penalty + signal_courtesy_bonus) * 0.20 +
        (100 - subjectivity_penalty) * 0.10 +
        (100 + modifier_penalty) * 0.10
    )
    
    return max(0, min(100, score))  # Clamp to 0-100
```

**Tasks:**
- [ ] Design weighting system (consult legal experts for validation)
- [ ] Implement calculation function
- [ ] Validate with test sentences (high civility vs. low civility)
- [ ] Tune weights based on beta feedback
- [ ] Document algorithm rationale

**Time Estimate:** 20 hours

---

#### 1.3 Risk Alert Logic
**File:** Add `draftshift/risk_alerts.py`

```python
class RiskAlertGenerator:
    def __init__(self):
        self.alert_rules = [
            {
                "name": "Aggressive_Phrasing",
                "patterns": ["strongly object", "demand", "must", "unacceptable"],
                "severity": "high",
                "suggestion": "Use respectful alternatives"
            },
            {
                "name": "Dismissive_Tone",
                "emotion_trigger": {"anger": 0.6},
                "severity": "high",
                "suggestion": "Soften emotional language"
            },
            # ... more rules
        ]
    
    def generate_alerts(self, text, analysis):
        """Generate list of risk alerts."""
        alerts = []
        
        # Pattern matching
        for rule in self.alert_rules:
            if "patterns" in rule:
                for pattern in rule["patterns"]:
                    if pattern.lower() in text.lower():
                        alerts.append({
                            "severity": rule["severity"],
                            "message": f"Phrase '{pattern}' detected",
                            "trigger": pattern,
                            "suggestion": rule.get("suggestion")
                        })
        
        # Emotion-based alerts
        if analysis['emotions']['anger'] > 0.6:
            alerts.append({
                "severity": "high",
                "message": "High anger emotion detected",
                "suggestion": "Review for overly aggressive tone"
            })
        
        return alerts
```

**Tasks:**
- [ ] Define alert rules (working with attorney advisors)
- [ ] Implement pattern matching + emotion triggers
- [ ] Add suggestion generation
- [ ] Test with real correspondence samples
- [ ] Refine based on false positives

**Time Estimate:** 16 hours

---

#### 1.4 Streamlit App
**File:** `draftshift/streamlit_app.py`

```python
import streamlit as st
from draftshift import core
from draftshift.llm_transformer import LLMTransformer
from draftshift.risk_alerts import RiskAlertGenerator

st.set_page_config(page_title="DraftShift", layout="wide")

st.title("DraftShift - Civility Analyzer for Legal Correspondence")

# Sidebar settings
mode = st.sidebar.selectbox("Draft Mode", ["civility", "litigation", "client-friendly", "neutral-negotiation"])
include_rewrite = st.sidebar.checkbox("Include Suggested Rewrite", value=True)

# Main input
text = st.text_area("Enter your correspondence:", height=200)

if st.button("Analyze"):
    # Run analysis
    analysis = core.detect_tone(text)
    civility_score = core.calculate_civility_score(analysis)
    alerts = RiskAlertGenerator().generate_alerts(text, analysis)
    
    # Display civility score
    col1, col2 = st.columns([1, 2])
    with col1:
        color = "🟢" if civility_score >= 80 else "🟡" if civility_score >= 60 else "🔴"
        st.metric("Civility Score", f"{civility_score}/100", delta=color)
    
    # Display alerts
    with col2:
        st.subheader("Risk Alerts")
        for alert in alerts:
            st.warning(f"**{alert['severity'].upper()}**: {alert['message']}\n\n*Suggestion*: {alert['suggestion']}")
    
    # Display glyphs
    st.subheader("Tone Signals Detected")
    signals_text = ", ".join([f"{sig['glyph']} {sig['name']} ({sig['confidence']:.0%})" 
                              for sig in analysis['glyphs']])
    st.write(signals_text)
    
    # Suggested rewrite
    if include_rewrite:
        st.subheader("Suggested Rewrite")
        transformer = LLMTransformer()
        rewrite = transformer.transform(text, mode=mode)
        st.text_area("Suggested version:", value=rewrite, height=150, disabled=True)
        
        # Re-analyze rewrite
        rewrite_score = core.calculate_civility_score(core.detect_tone(rewrite))
        st.success(f"✅ Civility score improved to {rewrite_score}/100")

# Disclaimer
st.info("""
**DraftShift Disclaimer:**
DraftShift does not replace the role of an attorney or ethics consultant. 
This application suggests alternative ways to draft correspondence.
Thoroughly vet any suggested text before sending.
No correspondence is stored by DraftShift.
""")
```

**Tasks:**
- [ ] Build Streamlit UI following Phase 1 wireframe
- [ ] Integrate all modules (analysis, scoring, alerts, LLM)
- [ ] Add mode selector
- [ ] Add result display (score, glyphs, alerts, rewrite)
- [ ] Add disclaimer
- [ ] Test with sample correspondence

**Time Estimate:** 16 hours

---

#### 1.5 Requirements & Setup
**File:** `requirements-phase1.txt`

```
spacy==3.7.2
textblob==0.17.1
nrclex==0.0.85
gpt4all==3.0.0
torch==2.0.0
transformers==4.30.0
streamlit==1.28.0
```

**Tasks:**
- [ ] Create requirements file
- [ ] Document installation steps
- [ ] Create README with setup + usage instructions
- [ ] Add `.env` example for settings

**Time Estimate:** 4 hours

---

### Phase 1 Rollout Checklist

| Task | Owner | ETA | Status |
|------|-------|-----|--------|
| LLM Integration (1.1) | Dev | Week 1-2 | ⏳ Not started |
| Civility Scoring (1.2) | Dev | Week 2-3 | ⏳ Not started |
| Risk Alerts (1.3) | Dev | Week 3 | ⏳ Not started |
| Streamlit App (1.4) | Dev | Week 3-4 | ⏳ Not started |
| Requirements & Setup (1.5) | Dev | Week 4 | ⏳ Not started |
| Beta User Recruitment | PM | Week 1-4 | ⏳ Not started |
| Beta Testing (5-10 users) | Users | Week 4-8 | ⏳ Not started |
| Feedback Integration | Dev | Week 8 | ⏳ Not started |
| Phase 1 Release | Dev | Week 12 | ⏳ Not started |

**Total Effort:** ~80 hours (2-3 weeks for 1-2 devs)

---

## 📅 Phase 2 Implementation: Beta (Months 4-6)

### Goal
Production-ready backend + polished React frontend. Deploy to 20-30 beta users.

### What to Build (Summary)
1. **FastAPI Backend** - Full API endpoints, database layer (SQLite)
2. **React Frontend** - Component tree from UI design, TypeScript + Tailwind
3. **Docker Deployment** - Containerized setup
4. **Compliance Reporting** - Basic PDF export
5. **Authentication** - JWT-based auth
6. **Automated Testing** - Unit + integration tests

### Architecture
```
┌─ Frontend Layer ─────────┐
│ React + TypeScript       │
│ (draftshift/frontend/)   │
└──────────┬───────────────┘
           │ API calls (http://localhost:8000)
           ↓
┌─ Backend Layer ──────────┐
│ FastAPI + SQLAlchemy     │
│ (draftshift/api/)        │
└──────────┬───────────────┘
           │
           ↓
┌─ Data Layer─────────────┐
│ SQLite (or PostgreSQL)   │
└──────────────────────────┘
```

### Key Files to Create
- `draftshift/api/main.py` - FastAPI app
- `draftshift/api/routes/` - Endpoint implementations
- `draftshift/api/models/` - SQLAlchemy ORM models
- `draftshift/frontend/src/` - React components
- `Dockerfile` + `docker-compose.yml`
- Tests in `tests/` directory

### Success Criteria
- [ ] 20-30 beta users test for 4 weeks
- [ ] >80% user satisfaction
- [ ] Civility score improvements validated (avg +10 points)
- [ ] Zero data loss incidents
- [ ] <30 min deployment time

**Time Estimate:** 200-250 hours (3-4 weeks for 2-3 devs)

---

## 📅 Phase 3 Implementation: Enterprise (Months 7+)

### Goal
Full-featured enterprise platform with multi-tenant, SAML/SSO, advanced analytics, integrations.

### What to Build (Summary)
1. **Electron App** - Cross-platform desktop wrapper
2. **Multi-Tenant Backend** - Org isolation, permissions
3. **Advanced Dashboard** - Compliance analytics, trends
4. **SAML/SSO** - Enterprise authentication
5. **Archive Analysis** - AnythingLLM + RAG
6. **Glyph Visualization** - Symbolic overlays
7. **Integrations** - Outlook, Gmail, case management
8. **Admin Console** - User/org management

### Key Features
- Firm-wide civility dashboards
- Historical compliance reporting
- Integration with legal workflows
- Fine-tuned civility models (optional)
- On-premises deployment option

### Success Criteria
- [ ] SOC 2 Type II audit passed
- [ ] GDPR/CCPA compliance
- [ ] 100+ enterprise beta users
- [ ] Positive case studies (3+ law firms)
- [ ] NPS score >50

**Time Estimate:** 300-400 hours (5-6 weeks for 3-4 devs)

---

## 🔄 Dependencies & Sequencing

### Critical Path (Minimum to Ship Phase 1)
1. ✅ Analysis modules (already done)
2. → LLM Integration (1.1)
3. → Civility Scoring (1.2)
4. → Risk Alerts (1.3)
5. → Streamlit App (1.4)
6. → Phase 1 Release

### Phase 1 → Phase 2 Transition
- Phase 1 must be validated with beta users first
- Phase 2 development can start in Month 2 (overlap)
- Phase 1 production support continues during Phase 2

### Phase 2 → Phase 3 Transition
- Phase 2 must reach GA with customer case studies
- Phase 3 development can start in Month 5 (overlap)
- Phase 2 production support continues during Phase 3

---

## 📊 Resource Requirements

### Phase 1
- **1 Backend Dev** (Python, LLM integration)
- **1 Frontend Dev** (Streamlit)
- **1 QA** (testing + beta management)
- **Total:** 2-3 people, 12 weeks

### Phase 2
- **2 Backend Devs** (FastAPI, database, testing)
- **2 Frontend Devs** (React, Tailwind, TypeScript)
- **1 DevOps** (Docker, CI/CD)
- **1 QA** (automated testing)
- **Total:** 4-5 people, 12 weeks

### Phase 3
- **3 Backend Devs** (multi-tenant, integrations, scaling)
- **2 Frontend Devs** (Electron, advanced UI, admin)
- **1 DevOps** (Kubernetes, monitoring, on-prem support)
- **1 Security** (SOC 2, audit prep)
- **1 QA/Release** (automated testing, release mgmt)
- **Total:** 5-6 people, 16 weeks

---

## 🎯 Milestones & Gates

| Milestone | Target | Gate Criteria |
|-----------|--------|---------------|
| Phase 1 MVP | Month 3 | Streamlit works, 5-10 users validate |
| Phase 1 Production | Month 4 | >70% satisfaction, no data loss, lawyer review |
| Phase 2 Alpha | Month 5 | React+FastAPI deployed, internal testing |
| Phase 2 Beta Release | Month 6 | 20-30 users, >80% satisfaction |
| Phase 2 GA | Month 7 | Case studies, compliance validated |
| Phase 3 Alpha | Month 8 | Electron, multi-tenant MVP |
| Phase 3 Beta Release | Month 9 | 100+ enterprise beta users |
| Phase 3 GA | Month 12 | SOC 2 certified, >50 NPS |

---

## 🔐 Security & Compliance Checklist

### Phase 1
- [ ] Local-only (no external APIs)
- [ ] No PII/correspondence stored by default
- [ ] DISCLAIMER prominently displayed
- [ ] Lawyer review of transformations for legal accuracy

### Phase 2
- [ ] HTTPS enforced
- [ ] JWT authentication
- [ ] Encrypted password storage (bcrypt)
- [ ] Input validation + SQL injection protection
- [ ] GDPR consent + data export capability
- [ ] Audit logs for all actions

### Phase 3
- [ ] SAML/SSO support
- [ ] Role-based access control (RBAC)
- [ ] Multi-tenant data isolation
- [ ] SOC 2 Type II audit
- [ ] GDPR/CCPA compliance certification
- [ ] Encryption at rest + in transit
- [ ] Regular security audits

---

## 📈 Success Metrics & KPIs

### Phase 1
- Users: 5-10 beta
- Avg civility score improvement: >5 points
- User satisfaction: >70%
- Concept validation: ✅

### Phase 2
- Users: 20-30 beta
- Avg civility score improvement: >10 points
- User satisfaction: >80%
- NPS score: >30
- Uptime: >99%

### Phase 3
- Users: 100+ beta (law firm decision-makers)
- Avg civility score improvement: >10 points
- User satisfaction: >85%
- NPS score: >50
- Paying customers: 10+
- Uptime: >99.5%

---

## 🚀 Launch Checklist

### Phase 1 Launch
- [ ] Streamlit app runs locally
- [ ] All modules integrated
- [ ] 5-10 beta users recruited
- [ ] Documentation complete
- [ ] Lawyer review + legal approval
- [ ] GitHub repo set to public (optional)

### Phase 2 Launch
- [ ] React + FastAPI deployed
- [ ] Docker image published
- [ ] 20-30 users onboarded
- [ ] Case studies collected
- [ ] API documentation finalized
- [ ] Support process established

### Phase 3 Launch
- [ ] Electron app published
- [ ] Multi-tenant infrastructure ready
- [ ] 100+ users beta testing
- [ ] SOC 2 audit complete
- [ ] Enterprise sales materials prepared
- [ ] Pricing & packaging finalized

---

## 📖 Documentation to Create

### Phase 1
- [ ] README (setup + quick start)
- [ ] User guide (how to use app)
- [ ] Architecture overview
- [ ] Troubleshooting guide

### Phase 2
- [ ] API documentation (Swagger)
- [ ] Deployment guide (Docker)
- [ ] Developer setup guide
- [ ] Database schema documentation
- [ ] Admin guide

### Phase 3
- [ ] Enterprise deployment guide (on-prem, Kubernetes)
- [ ] Integration guides (Outlook, Gmail, etc.)
- [ ] Admin console guide
- [ ] Compliance documentation (SOC 2, GDPR)
- [ ] Troubleshooting + support runbook

---

## 🎓 Next Action Items (Start Phase 1)

### Week 1
- [ ] Recruit 5-10 beta users (lawyers, law students)
- [ ] Finalize LLM integration plan (GPT4All setup)
- [ ] Design civility scoring algorithm with lawyer advisors
- [ ] Begin development of (1.1) LLM Integration

### Week 2-3
- [ ] Complete LLM Integration module
- [ ] Implement civility scoring algorithm
- [ ] Start Streamlit app skeleton

### Week 3-4
- [ ] Complete Risk Alert logic
- [ ] Complete Streamlit app
- [ ] Internal testing

### Week 4-8
- [ ] Beta user testing
- [ ] Feedback collection + iteration
- [ ] Prepare Phase 1 release

### Month 3-4
- [ ] Phase 1 production release
- [ ] Begin Phase 2 architecture design
- [ ] Collect case studies + testimonials

---

## Summary

DraftShift is positioned to become **the civility compliance engine for legal professionals**. By following this phased roadmap:

1. **Phase 1** validates the concept and builds a functional MVP
2. **Phase 2** scales to early customers with a production system
3. **Phase 3** enables enterprise deployment with advanced features

**Current advantage:** All core analysis modules are already built and working. The path forward is clear: integrate an LLM, build the Streamlit prototype, validate with users, then systematically build toward enterprise.

**Timeline:** MVP by Month 3, Beta platform by Month 6, Enterprise-ready by Month 12.

**Key success factor:** Maintain the "attorney always in control" philosophy throughout all phases. DraftShift augments judgment, never replaces it.

---

*Last Updated: December 19, 2025*  
*Prepared for: DraftShift Development Team*  
*Status: Ready for Phase 1 Implementation*
