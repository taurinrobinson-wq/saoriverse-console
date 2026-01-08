# DraftShift UI/UX Design: Dashboard & Components

## 🎨 Design Philosophy

- **Clean, legal professional aesthetic**: No unnecessary visual clutter.
- **Attorney-centric**: All controls serve attorney workflow, not system needs.
- **Transparency**: Clearly explain *why* civility score is what it is.
- **Action-oriented**: Every screen leads to a decision or action.
- **Disclaimer-always-visible**: Legal responsibility is persistent, not buried.

---

## 📐 Dashboard Wireframe

### Phase 1: Streamlit (MVP)
Simple, functional prototype focused on proving civility scoring logic.

```
┌────────────────────────────────────────────────────────────────┐
│  DraftShift Civility Analyzer                       [Settings]  │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📝 CORRESPONDENCE INPUT                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Paste or type your correspondence here...               │  │
│  │                                                          │  │
│  │ We strongly object to your position and demand          │  │
│  │ immediate compliance with our demands. Your lack of     │  │
│  │ cooperation has forced us to escalate this matter...     │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│  (120 words, 650 chars)                                        │
│                                                                  │
│  DRAFT MODE: [ Civility | Litigation | Client-Friendly ]      │
│                                                                  │
│  [ Analyze Draft ]        [ Clear ]                            │
│                                                                  │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 RESULTS (Post-Analysis)                                    │
│                                                                  │
│  ┌─ CIVILITY SCORE ────────────────────────────────────────┐  │
│  │                                                          │  │
│  │              Civility Score: 42 / 100                   │  │
│  │              Status: ⚠️ REVIEW RECOMMENDED              │  │
│  │                                                          │  │
│  │  Color: 🔴 RED (0-59): Major changes recommended        │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ GLYPH MAP ──────────────────────────────────────────────┐  │
│  │                                                          │  │
│  │  Detected Tone Signals:                                 │  │
│  │  ⚖️ Boundary/Protective (82% confident)                 │  │
│  │  ⚠️ Aggression (68% confident)                          │  │
│  │  λ Confidence/Assertiveness (65% confident)             │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ ANALYSIS BREAKDOWN ─────────────────────────────────────┐  │
│  │                                                          │  │
│  │  Sentiment Polarity:  -0.45 (negative)                  │  │
│  │  Subjectivity:        0.72 (highly subjective)          │  │
│  │  Primary Emotion:     Anger (68%)                       │  │
│  │  Valence:             -0.35 (negative)                  │  │
│  │  Arousal:             0.82 (intense)                    │  │
│  │                                                          │  │
│  │  [+ Show All Emotions]                                  │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ RISK ALERTS ────────────────────────────────────────────┐  │
│  │                                                          │  │
│  │  ⚠️ HIGH SEVERITY                                        │  │
│  │  "Tone may be perceived as dismissive."                 │  │
│  │  Triggered by: "We strongly object"                     │  │
│  │  Suggestion: "We respectfully disagree with your        │  │
│  │              position"                                  │  │
│  │                                                          │  │
│  │  ⚠️ MEDIUM SEVERITY                                      │  │
│  │  "Demand language may escalate tension."                │  │
│  │  Triggered by: "demand immediate compliance"            │  │
│  │  Suggestion: "request your prompt response"             │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ SUGGESTED REWRITE ──────────────────────────────────────┐  │
│  │                                                          │  │
│  │  We respectfully disagree with your position and        │  │
│  │  request your prompt response to our concerns. Your     │  │
│  │  cooperation on this matter is important to us...       │  │
│  │                                                          │  │
│  │  📊 Civility Score: 78 / 100 (Yellow - Good)            │  │
│  │                                                          │  │
│  │  [📋 Copy to Clipboard]  [🔄 Regenerate]  [✅ Use This] │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
├────────────────────────────────────────────────────────────────┤
│  DISCLAIMER (Sticky Footer)                                     │
│  DraftShift does not replace the role of an attorney. This    │
│  application suggests alternative ways to draft correspondence │
│  for different audiences. Thoroughly vet any suggested text   │
│  before sending. No correspondence is stored by DraftShift.   │
└────────────────────────────────────────────────────────────────┘
```

---

### Phase 2: FastAPI + React (Production)

More sophisticated interface with persistent state, history, and compliance dashboard.

```
┌────────────────────────────────────────────────────────────────┐
│ DraftShift         Civility Dashboard    Settings    Sign Out   │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [New Analysis]  [History]  [Archive]  [Compliance Report]    │
│                                                                  │
├──────────────────────────────────────────────────────────────┬─┤
│                          MAIN CONTENT                       │S│
│                                                             │I│
│ ┌─ INPUT PANEL ────────────────────────────────────────┐  │D│
│ │ Correspondence Mode: ◀ Civility ▶                   │  │E│
│ │ ┌─────────────────────────────────────────────────┐ │  │B│
│ │ │ [Paste text, compose, or upload from file]      │ │  │A│
│ │ └─────────────────────────────────────────────────┘ │  │R│
│ │                                                       │  │ │
│ │ [ Analyze ] [ Clear ] [ Load From History ]         │  │ │
│ └───────────────────────────────────────────────────────┘  │ │
│                                                             │ │
│ ┌─ RESULTS PANEL (Left Column) ──────────────────────┐   │ │
│ │                                                     │   │ │
│ │  CIVILITY SCORE CARD                              │   │ │
│ │  ╭─────────────╮                                  │   │ │
│ │  │  42 / 100   │  ⚠️ Review Recommended           │   │ │
│ │  │   🔴 RED    │                                  │   │ │
│ │  ╰─────────────╯                                  │   │ │
│ │                                                     │   │ │
│ │  GLYPH MAP                                         │   │ │
│ │  ⚖️ Boundary ..................... 82%             │   │ │
│ │  ⚠️ Aggression ................... 68%             │   │ │
│ │  λ Assertiveness ................. 65%             │   │ │
│ │                                                     │   │ │
│ │  EMOTION PROFILE                                  │   │ │
│ │  Anger:  ████████░░░░░░░░░░  68%                 │   │ │
│ │  Fear:   ██░░░░░░░░░░░░░░░░░░  12%                │   │ │
│ │  Trust:  ██░░░░░░░░░░░░░░░░░░   8%                │   │ │
│ │  Joy:    █░░░░░░░░░░░░░░░░░░░░   2%                │   │ │
│ │                                                     │   │ │
│ └─────────────────────────────────────────────────────┘   │ │
│                                                             │ │
│ ┌─ DETAILED ANALYSIS (Right Column) ────────────────┐   │ │
│ │                                                     │   │ │
│ │  RISK ALERTS (with severity badges)               │   │ │
│ │                                                     │   │ │
│ │  🔴 HIGH                                           │   │ │
│ │  Dismissive tone detected                         │   │ │
│ │  "We strongly object" → "We respectfully         │   │ │
│ │   disagree"                                        │   │ │
│ │                                                     │   │ │
│ │  🟡 MEDIUM                                         │   │ │
│ │  Escalatory language                             │   │ │
│ │  "demand immediate" → "request prompt"            │   │ │
│ │                                                     │   │ │
│ │  [More Details ▼]                                 │   │ │
│ │                                                     │   │ │
│ └─────────────────────────────────────────────────────┘   │ │
│                                                             │ │
│ ┌─ SUGGESTED REWRITE ──────────────────────────────┐   │ │
│ │                                                   │   │ │
│ │ [Read-Only Text Box with Suggested Rewrite]     │   │ │
│ │ We respectfully disagree with your position and │   │ │
│ │ request your prompt response to our concerns... │   │ │
│ │                                                   │   │ │
│ │ Civility Score: 78/100 (Yellow - Good)          │   │ │
│ │                                                   │   │ │
│ │ [📋 Copy]  [🔄 Regen]  [▶ Use]  [📊 Compare]   │   │ │ │
│ │                                                   │   │ │
│ └───────────────────────────────────────────────────┘   │ │
│                                                             │ │
├─────────────────────────────────────────────────────────────┤
│ DISCLAIMER (Persistent Footer)                              │
│ DraftShift does not replace attorney/ethics consultant role │
│ All suggestions must be thoroughly vetted before sending.   │
└──────────────────────────────────────────────────────────────┘
```

---

### Phase 3: HTML/JS (Enterprise)

Full dashboard with compliance reporting, history, and firm-wide civility metrics.

```
┌────────────────────────────────────────────────────────────────────┐
│  DraftShift™ Civility Compliance Engine     ⚙️ Settings  👤 Profile │
├────────────────────────────────────────────────────────────────────┤
│  [New Draft] [Dashboard] [History] [Reports] [Archive] [Help]      │
│                                                                      │
├──────────────────────────────────────────────────────────────────┬──┤
│  TWO-COLUMN LAYOUT                                             │SA│
│                                                                │DE│
│  ┌─ QUICK STATS (Top) ──────────────────────────────────┐   │B│
│  │ This Month: Avg Civility 74.2%  |  Docs: 24  |  Alerts: 12  │A│
│  │ Trend: ↗ +3.2% from last month                       │   │R│
│  └───────────────────────────────────────────────────────┘   │  │
│                                                                │  │
│  ┌─ INPUT COLUMN ────────────────────────────────────────┐   │  │
│  │                                                        │   │  │
│  │  Draft Mode:  [ ✓ Civility | Litigation | Client ]   │   │  │
│  │                                                        │   │  │
│  │  ┌────────────────────────────────────────────────┐   │   │  │
│  │  │ Paste or drag correspondence here...            │   │   │  │
│  │  │                                                  │   │   │  │
│  │  │ [Include from:] [📧 Outlook] [📎 File] [✂️ Paste] │   │   │  │
│  │  │                                                  │   │   │  │
│  │  └────────────────────────────────────────────────┘   │   │  │
│  │                                                        │   │  │
│  │  [ Analyze ]  [ Clear ]  [ Save as Draft ]           │   │  │
│  │                                                        │   │  │
│  └────────────────────────────────────────────────────────┘   │  │
│                                                                │  │
│  ┌─ RESULTS COLUMN ──────────────────────────────────────┐   │  │
│  │                                                        │   │  │
│  │  CIVILITY GAUGE                                       │   │  │
│  │  ╭──────────────────────────────────╮                │   │  │
│  │  │    CIVILITY: 42 / 100            │                │   │  │
│  │  │    STATUS: 🔴 REVIEW             │                │   │  │
│  │  │    ACTION: Revise Recommended    │                │   │  │
│  │  ╰──────────────────────────────────╯                │   │  │
│  │                                                        │   │  │
│  │  GLYPH ANALYSIS                                       │   │  │
│  │  ┌─ Emotional Tone ──────────────────────────────┐   │   │  │
│  │  │ ⚠️ Aggression: 68% (High alert)              │   │   │  │
│  │  │ ⚖️ Boundary:   82% (Strong protective)       │   │   │  │
│  │  │ λ Assertiveness: 65% (Firm)                  │   │   │  │
│  │  │ 🌿 Courtesy:  18% (Minimal)  ⚠️ CONCERN     │   │   │  │
│  │  └──────────────────────────────────────────────┘   │   │  │
│  │                                                        │   │  │
│  │  RISK ALERTS                                          │   │  │
│  │  🔴 HIGH: "strongly object"  → "respectfully disagree"  │   │  │
│  │  🟡 MED:  "demand immediate" → "request prompt"    │   │  │
│  │  🟢 LOW:  Consider softening "Your lack of..."     │   │  │
│  │  [Dismiss All] [Review Suggestions]                │   │  │
│  │                                                        │   │  │
│  │  SUGGESTED REWRITE                                    │   │  │
│  │  ┌────────────────────────────────────────────────┐   │   │  │
│  │  │ We respectfully disagree with your position    │   │   │  │
│  │  │ and request your prompt response to our        │   │   │  │
│  │  │ concerns. We look forward to working together  │   │   │  │
│  │  │ to resolve this matter...                      │   │   │  │
│  │  │                                                │   │   │  │
│  │  │ Civility Score: 78/100 🟡                      │   │   │  │
│  │  │ [Copy] [Regenerate] [Compare] [Use This]      │   │   │  │
│  │  └────────────────────────────────────────────────┘   │   │  │
│  │                                                        │   │  │
│  │  VERSION COMPARE                                      │   │  │
│  │  ┌────────────────────────────────────────────────┐   │   │  │
│  │  │ ORIGINAL (42/100)      │  SUGGESTED (78/100)  │   │   │  │
│  │  │                                                │   │   │  │
│  │  │ We strongly object...  │  We respectfully...  │   │   │  │
│  │  │ (red highlights)       │  (green highlights)  │   │   │  │
│  │  └────────────────────────────────────────────────┘   │   │  │
│  │                                                        │   │  │
│  └────────────────────────────────────────────────────────┘   │  │
│                                                                │  │
├────────────────────────────────────────────────────────────────┤  │
│  PERSISTENT FOOTER — DISCLAIMER & ACTIONS                      │  │
│  ⚖️ DraftShift does not replace attorney judgment. All texts │  │
│  suggested must be thoroughly vetted before sending.           │  │
│                                                                │  │
│  [✅ Send] [📋 Save Draft] [📧 Forward to Colleague] [❌ Cancel] │  │
│                                                                │  │
└────────────────────────────────────────────────────────────────┘──┘
```

---

## 🧩 React Component Tree (Phase 2+)

```
<App>
 ├── <TopNav>
 │    ├── Logo
 │    ├── Navigation Links
 │    └── User Menu
 │
 ├── <SideBar>
 │    ├── Quick Stats
 │    ├── Navigation Tabs
 │    └── Settings Link
 │
 ├── <MainContent>
 │    ├── <InputPanel>
 │    │    ├── <ModeSelector>
 │    │    ├── <TextAreaInput>
 │    │    ├── <FileUpload>
 │    │    └── <AnalyzeButton>
 │    │
 │    └── <ResultsPanel>
 │         ├── <CivilityScoreCard>
 │         │    ├── Gauge/Progress Bar
 │         │    ├── Status Badge
 │         │    └── Action Label
 │         │
 │         ├── <GlyphMap>
 │         │    ├── <GlyphIcon>
 │         │    ├── <GlyphLabel>
 │         │    └── <ConfidenceBar>
 │         │
 │         ├── <EmotionProfile>
 │         │    └── Emotion Bars
 │         │
 │         ├── <RiskAlerts>
 │         │    ├── <RiskAlert> (severity badge)
 │         │    └── <Suggestion>
 │         │
 │         ├── <SuggestedRewrite>
 │         │    ├── Read-only Text
 │         │    ├── Civility Score
 │         │    ├── <CopyButton>
 │         │    ├── <RegenerateButton>
 │         │    └── <UseButton>
 │         │
 │         └── <VersionCompare>
 │              ├── Original Version
 │              └── Suggested Version
 │
 └── <DisclaimerFooter>
      └── Sticky disclaimer + action buttons

```

---

## 🎨 Color & Typography

### Color Scheme
- **Green (#22C55E)**: Compliant, safe (80-100 civility score)
- **Yellow (#EAB308)**: Review recommended (60-79)
- **Red (#EF4444)**: Major revision needed (0-59)
- **Neutral Gray (#64748B)**: Informational, neutral phrasing

### Typography
- **Headings**: Sans-serif (Inter, Roboto), bold, high contrast
- **Body**: Sans-serif, 14-16px, comfortable reading
- **Monospace**: Code/legal language (when displaying extracted phrases)
- **Emphasis**: Bold or highlight on actionable items

### Accessibility
- WCAG 2.1 AA compliant
- Color-blind safe palette
- Keyboard navigation support
- Screen reader friendly

---

## 🔄 User Workflows

### Workflow 1: Analyze & Accept Suggestion
1. **Input**: Paste correspondence
2. **Analyze**: Click "Analyze"
3. **Review**: See civility score, glyph map, alerts
4. **Decide**: Read suggested rewrite
5. **Act**: Click "Use This" or "Copy to Clipboard"

### Workflow 2: Review Multiple Versions
1. **Input**: Correspondence
2. **Analyze**: Get initial result
3. **Regenerate**: Click "Regenerate" for alternative rewrites
4. **Compare**: Side-by-side view of versions
5. **Choose**: Select best version
6. **Export**: Copy or save

### Workflow 3: Compliance Reporting (Phase 3)
1. **Navigate**: Click "Reports"
2. **Filter**: Date range, document type, civility threshold
3. **Generate**: Export as PDF/markdown
4. **Review**: Compliance metrics, trends, alerts
5. **Submit**: Use for Rule 9.7 declaration

---

## ✨ Interactive Elements

### Hover States
- Buttons lighten/darken on hover
- Cards lift slightly with subtle shadow
- Text selections are highlighted

### Loading States
- Spinner overlay during analysis
- Disabled input while processing
- Progress indication for slow operations

### Feedback
- Toast notifications for copy, save, send actions
- Error messages for validation failures
- Confirmation dialogs for destructive actions

---

## 📱 Responsive Design

### Desktop (1200px+)
- Two-column layout (input + results)
- Full sidebar visible
- All controls accessible

### Tablet (768px-1200px)
- Stacked layout (input, then results below)
- Sidebar collapses to drawer
- Touch-friendly button sizing

### Mobile (< 768px)
- Full-width input/results
- Bottom drawer for settings
- Disclaimer always visible at bottom

---

## 🎓 Next Steps

1. **Phase 1**: Streamlit prototype (all above layouts translate 1:1 to st.* components).
2. **Phase 2**: React components + FastAPI backend (use component tree as guide).
3. **Phase 3**: Full HTML/JS with Electron or PWA wrapper (ready for enterprise).

The same UX philosophy and information architecture apply across all phases; only the implementation technology changes.
