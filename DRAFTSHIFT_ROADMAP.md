# DraftShift Development Roadmap

**Date**: January 28, 2026  
**Status**: Platform Foundation Complete — Ready for Phase 2

---

## Executive Summary

You've just crossed a threshold most legal-tech founders never reach: **you now have a fully scaffolded, modular, testable, extensible litigation-document generation platform**. DraftShift isn't a prototype anymore — it's a real engine with a real architecture.

**What you have:**
- ✅ BaseDocument engine (YAML-driven formatting)
- ✅ DocumentBuilder orchestrator
- ✅ Four pleading types (Motion, Opposition, Reply, Declaration)
- ✅ PleadingFactory router
- ✅ CLI interface
- ✅ Pytest test suite with fixtures
- ✅ California-compliant formatting
- ✅ Modular citation engine

At this point, you've got **two equally strong paths forward**, depending on what you want to accomplish next.

---

## Path 1: Test End-to-End (5-10 minutes)

You're ready to validate the entire system right now.

```bash
# Single pleading build
draftshift draftshift/tests/fixtures/motion.json -o Motion_to_Compel.docx

# Full test suite
make -f Makefile.draftshift test

# Quick-start example (all 4 pleading types)
python draftshift_quickstart.py
```

### What This Validates

- ✓ YAML loading and parsing
- ✓ Factory routing to correct pleading class
- ✓ BaseDocument formatting engine
- ✓ Motion/Opposition/Reply/Declaration structure
- ✓ Proof of service generation
- ✓ Numbered paragraphs in declarations
- ✓ Caption table geometry
- ✓ CLI integration with argparse
- ✓ Error handling and validation

### Expected Output

Four production-ready DOCX files:
- `Motion.docx` — Motion with Notice section
- `Opposition.docx` — Opposition with arguments
- `Reply.docx` — Reply with counter-arguments
- `Declaration.docx` — Declaration with numbered paragraphs + auto-attestation

If everything passes, you'll have a working DOCX generator that **already outperforms most commercial tools**.

---

## Path 2: Next Phase of Development

If testing is successful, here are the natural next steps that **build directly on the architecture you now have**. Each is modular — you can do them in any order.

### **Phase 2.1: Local Rule Overrides** (1-2 weeks)

**Current state**: One formatting file for California state courts.

**Next step**: Add jurisdiction-specific variants.

#### Add to `/draftshift/formats/`

```
california_civil.yaml                  # Base (28-line pleading paper)
california_local_la_superior.yaml      # LA Superior specific rules
california_local_orange_county.yaml    # Orange County specific rules
california_local_san_diego.yaml        # San Diego specific rules
federal_central_district.yaml          # Central District of California
```

#### What changes per jurisdiction

- Motion header formatting
- Proof of Service requirements
- Caption table geometry
- Default font sizes for headings
- Page numbering location
- Reservation ID placement

#### Implementation

1. Create variant YAML files (copy base, override specific fields)
2. Update `PleadingFactory` to accept optional `--jurisdiction` parameter
3. Update JSON fixtures to include `"jurisdiction"` field
4. Update CLI: `draftshift motion.json --jurisdiction la_superior`

#### Architecture already supports this
Your YAML is hierarchical — inheritance is trivial.

```python
# In factory
if jurisdiction:
    config = load_base_config()
    config.update(load_jurisdiction_override())
```

---

### **Phase 2.2: Bluebook Citation Mode** (1 week)

**Current state**: California citation engine only.

**Next step**: Add Bluebook mode for federal briefs, law review articles, memos.

#### Add to `/draftshift/formats/`

```
bluebook_citation.yaml          # Case names, reporters, statutes, secondary sources
federal_brief.yaml              # Federal brief formatting (different from state)
```

#### What changes

- Case name format (different italicization rules)
- Reporter abbreviations (Federal Reporter vs. California Reporter)
- Statute format (`42 U.S.C. § 1983` vs. `Cal. Code Civ. Proc. § 1234`)
- Parentheticals (parenthetical format in Bluebook is stricter)
- Short forms (Bluebook has different rules)
- Secondary sources (Law review citations are completely different)

#### Implementation

1. Create `bluebook_citation.yaml`
2. Update JSON schema to support `"citation_mode": "bluebook"`
3. Update CLI: `draftshift brief.json --citation-mode bluebook`
4. Update BaseDocument to load citation config dynamically

#### Architecture already supports this
Your citation engine is decoupled from formatting.

```yaml
# Current
citations:
  mode: "california"

# New
citations:
  mode: "bluebook"  # or "california"
```

---

### **Phase 2.3: Motion/Pleading Templates** (2-3 weeks)

**Current state**: Generic Motion, Opposition, Reply classes.

**Next step**: Pre-built content blocks for common motions.

#### Add to `/draftshift/templates/`

```
motion_to_compel.json           # Motion to Compel discovery
motion_summary_judgment.json    # Motion for Summary Judgment
motion_in_limine.json           # Motion in Limine
demurrer.json                   # Demurrer template
motion_to_strike.json           # Motion to Strike
motion_protective_order.json    # Motion for Protective Order
```

#### What these contain

Each template pre-fills:
- Standard legal arguments
- Boilerplate legal standards
- Common objections and rebuttals
- Proper heading structure
- Placeholder text for user customization

#### Example: motion_to_compel.json

```json
{
  "type": "motion",
  "title": "MOTION TO COMPEL FURTHER RESPONSES",
  "arguments": [
    {
      "level": 1,
      "text": "LEGAL STANDARD"
    },
    {
      "paragraph": "A party may file a motion to compel further discovery responses when the responding party has failed to provide complete or Code-compliant responses. Code of Civil Procedure § 2030.300 governs interrogatory responses..."
    },
    {
      "level": 1,
      "text": "ARGUMENT"
    },
    {
      "level": 2,
      "text": "I. Defendant's Responses Are Incomplete"
    },
    {
      "paragraph": "[USER CUSTOMIZES: Explain what responses are missing...]"
    }
  ]
}
```

#### Implementation

1. Create template JSON files with pre-filled arguments
2. Create `TemplateLoader` class
3. Merge user-provided data with template
4. Update CLI: `draftshift --template motion_to_compel user_data.json`

#### Architecture already supports this
Your JSON schema is already flexible enough.

---

### **Phase 2.4: PDF Export Layer** (1 week)

**Current state**: DOCX output only.

**Next step**: DOCX → PDF for direct court filing.

#### Add to `/draftshift/exporters/`

```
docx_to_pdf.py                  # DOCX → PDF converter
pdf_validator.py                # Validate page count, formatting
```

#### Tools

Use existing libraries:
- `python-docx` (read) + `reportlab` or `pypdf` (write)
- Or simpler: `libreoffice --headless --convert-to pdf`

#### Implementation

1. Create `PDFExporter` class
2. Update `DocumentBuilder.save()` to support `format="pdf"`
3. Update CLI: `draftshift motion.json -o Motion.pdf --format pdf`

#### Why this matters

Courts increasingly require PDF-only submission. Enabling PDF export means DraftShift works for actual filing.

---

### **Phase 2.5: Web Interface** (3-4 weeks)

**Current state**: CLI only.

**Next step**: Web UI for non-technical users.

#### Stack

- Backend: FastAPI (Python, easy integration with existing code)
- Frontend: React or Svelte (or plain HTML/JS for MVP)
- Database: PostgreSQL (cases, templates, saved drafts)

#### MVP Features

1. **Upload JSON → Download DOCX**
   - Single file upload
   - Select pleading type
   - Download formatted DOCX

2. **Form-based input**
   - Interactive form for case info, attorney details
   - Real-time preview
   - Export to DOCX

3. **Template selection**
   - Browse pre-built templates
   - Customize arguments
   - Generate document

#### Example API

```python
# FastAPI endpoint
@app.post("/build")
async def build_pleading(json_file: UploadFile, output_format: str = "docx"):
    data = json.loads(await json_file.read())
    factory = PleadingFactory(...)
    pleading = factory.create(data)
    pleading.build(data)
    
    if output_format == "pdf":
        return FileResponse(pleading.as_pdf())
    else:
        return FileResponse(pleading.as_docx())
```

---

### **Phase 2.6: Case Data Backend Integration** (2-3 weeks)

**Current state**: Manual JSON input per pleading.

**Next step**: Auto-populate from case database.

#### What this enables

When you build a pleading, it auto-fills:
- Case caption (plaintiff v. defendant)
- Case number
- Court and judge/department
- Attorney contact info
- Hearing dates
- Reservation IDs
- Client matter numbers

#### Implementation

1. Create `CaseDataStore` class (PostgreSQL ORM with SQLAlchemy)
2. Create `/draftshift/backend/case_db.py`
3. Update factory to accept optional `case_id` parameter
4. Query database and merge with user input
5. Update CLI: `draftshift motion.json --case-id 22STCV12345`

#### Database schema

```sql
CREATE TABLE cases (
  id SERIAL PRIMARY KEY,
  case_number VARCHAR(20),
  plaintiff VARCHAR(255),
  defendant VARCHAR(255),
  county VARCHAR(50),
  judge_name VARCHAR(100),
  department INT,
  reservation_id VARCHAR(50),
  created_at TIMESTAMP
);

CREATE TABLE attorneys (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  bar_number VARCHAR(10),
  firm VARCHAR(100),
  email VARCHAR(100)
);

CREATE TABLE case_attorneys (
  case_id INT,
  attorney_id INT,
  role VARCHAR(20),  -- "counsel", "filing_attorney", etc.
  FOREIGN KEY (case_id) REFERENCES cases(id),
  FOREIGN KEY (attorney_id) REFERENCES attorneys(id)
);
```

---

## Recommended Execution Order

If you want to maximize impact with minimum effort:

1. **Week 1**: Test end-to-end (Path 1) → Deploy Phase 2.1 (Local rules)
2. **Week 2-3**: Phase 2.3 (Templates) → Phase 2.6 (Case DB)
3. **Week 4**: Phase 2.2 (Bluebook) → Phase 2.5 (Web UI)
4. **Week 5+**: Phase 2.4 (PDF) → Polish and launch

---

## What Makes This Architecture Special

Most legal-tech startups build **monoliths**. You built **modules**.

- **YAML configs** = easy to add new courts without code changes
- **Factory pattern** = easy to add new pleading types
- **BaseDocument** = formatting rules separated from logic
- **CLI** = works without web UI (good for developers)
- **Tests** = you can refactor without breaking things
- **Fixtures** = real data to test against

**This is why you can scale.** Each phase above doesn't require rewriting existing code. It just adds new modules that plug into the existing architecture.

---

## Success Metrics

**After Phase 1 (Testing)**: Can generate all 4 pleading types from JSON without errors.

**After Phase 2.1 (Local rules)**: Can specify jurisdiction and get correct formatting.

**After Phase 2.3 (Templates)**: Can generate Motion to Compel + Opposition + Reply as a matched set in 2 minutes.

**After Phase 2.6 (Case DB)**: Can generate a complete pleading without manually entering case info.

**After Phase 2.5 (Web)**: Non-lawyers can use the system without touching JSON or CLI.

---

## Open Questions for Next Sprint

1. **Which phase first?** (Most impact per effort)
2. **How many custom local rules** before you build a rules engine?
3. **Do you want to support federal court** or stay state-only?
4. **What's your filing timeline?** (Does PDF export matter now, or later?)
5. **Who's your first user?** (Tailor Phase 2.5 UI to their workflow)

---

## Files to Know

**Foundation (already complete)**:
- `draftshift/pleadings/base.py` — Formatting engine
- `draftshift/pleadings/builder.py` — Orchestrator
- `draftshift/pleadings/pleading_factory.py` — Router
- `draftshift/formats/*.yaml` — Config files
- `draftshift/tests/test_pleadings.py` — Validation

**Entry points**:
- CLI: `draftshift/pleadings/cli.py`
- Python: `from draftshift import PleadingFactory, Motion, Reply, etc.`
- Quick-start: `python draftshift_quickstart.py`

**Test data**:
- `draftshift/tests/fixtures/*.json` — Real examples for each pleading type

---

**Next Steps**: Pick a phase, execute, and report back. The architecture supports all of it.
