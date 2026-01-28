# DraftShift Quick Start Guide

Get DraftShift up and running in 5 minutes (local) or 10 minutes (Replit).

---

## Option A: Local Development (5 minutes)

### Requirements

- Python 3.8+
- Node.js 16+
- Git

### Steps

1. **Clone Repository**
```bash
git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
cd saoriverse-console
```

2. **Install DraftShift Engine**
```bash
cd draftshift
pip install -r ../requirements-backend.txt
pip install -e .
cd ..
```

3. **Test Engine**
```bash
pytest draftshift/tests/test_pleadings.py -v
```
Should show 10/10 tests passing.

4. **Install Web UI Dependencies**
```bash
cd draftshift-web
npm install
cd ..
```

5. **Start Both Servers** (in separate terminals)

**Terminal 1 — React Dev Server:**
```bash
cd draftshift-web
npm run dev
# Output: http://localhost:5173
```

**Terminal 2 — FastAPI Backend:**
```bash
cd draftshift-web
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
# Output: Uvicorn running on http://0.0.0.0:8000
```

6. **Open Browser**
Go to `http://localhost:5173` and start building pleadings!

---

## Option B: Replit Cloud Deployment (10 minutes)

### Requirements

- GitHub account (already have code committed)
- Replit account (free: replit.com)
- No credit card needed

### Steps

1. **Visit Replit**
Go to https://replit.com

2. **Create Project**
- Click "Create" → "Import from GitHub"
- Paste: `https://github.com/taurinrobinson-wq/saoriverse-console`
- Click "Import"

3. **Wait for Setup**
Replit automatically:
- Detects `.replit` configuration
- Installs Python 3.11
- Installs Node.js 20
- Installs all dependencies

4. **Build React Frontend**
In Replit Shell (bottom panel):
```bash
cd draftshift-web
npm run build
```
Wait ~30 seconds for build to complete.

5. **Start Application**
Click "Run" button (top of editor)

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

6. **Access Live URL**
Replit shows a "Webview" panel with your live URL:
- **Format**: `https://[your-replit-name].replit.dev`
- **Example**: `https://draftshift.replit.dev`

Click the link to see your live DraftShift UI! 🎉

---

## Using DraftShift

### Quick Workflow

1. **Load Template**
   - Click "Load Motion" (or Opposition/Reply/Declaration)
   - Fixture loads into JSON editor

2. **Edit Configuration**
   - Modify JSON as needed (or leave as-is to test)
   - Real-time validation

3. **Build Document**
   - Click "Build Document"
   - Watch status update
   - Generates production DOCX in seconds

4. **Download**
   - Click "Download DOCX"
   - File saves to Downloads folder
   - Open in Word to verify

### Example JSON Structure

```json
{
  "type": "motion",
  "title": "MOTION FOR NEW TRIAL",
  "body": [
    "This is Section 1 of the motion",
    "This is Section 2 with more arguments"
  ],
  "signature_block": [
    "Jane Smith",
    "Attorney for Defendant"
  ],
  "caption": {
    "case_name": "Brown v. Norris",
    "case_no": "123456",
    "court": "Superior Court of California",
    "county": "Alameda County"
  },
  "attorney": {
    "name": "Jane Smith",
    "bar_number": "123456",
    "firm": "Smith & Associates",
    "address": "123 Main St, Oakland, CA 94612",
    "phone": "510-555-1234",
    "email": "jane@smith.law"
  }
}
```

### Features

- **Fixture Presets** — 4 built-in examples (Motion, Opposition, Reply, Declaration)
- **Live JSON Editor** — Edit configuration directly
- **One-Click Build** — Generate DOCX instantly
- **Direct Download** — Save to computer with one click
- **Error Messages** — Clear feedback if something goes wrong
- **Responsive Design** — Works on desktop, tablet, mobile

---

## API Endpoints (If Using Directly)

### Health Check
```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "factory_ready": true,
  "supported_types": ["motion", "opposition", "reply", "declaration"]
}
```

### Build Pleading
```bash
curl -X POST http://localhost:8000/api/build \
  -H "Content-Type: application/json" \
  -d @fixture.json
```

**Response:**
```json
{
  "success": true,
  "filename": "Motion.docx",
  "data": "UEsDBBQACAAI..."  // base64-encoded DOCX
}
```

### Get Fixture
```bash
curl http://localhost:8000/api/fixtures/motion
```

**Response:** JSON fixture data

---

## Troubleshooting

### "Failed to load fixture"
**Solution**: Ensure `draftshift/tests/fixtures/` directory exists with JSON files.

### "Port 8000 already in use"
**Solution**: Close other apps using port 8000, or change port in start command:
```bash
python -m uvicorn api:app --port 8001
```

### "npm not found"
**Solution**: Install Node.js from nodejs.org

### "python not found"
**Solution**: Install Python 3.8+ from python.org

### "Module 'draftshift' not found"
**Solution**: Install engine properly:
```bash
cd draftshift
pip install -e .
cd ..
```

### React dev server won't start
**Solution**: Clear cache and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Replit says "Permission denied" when building
**Solution**: Make setup scripts executable:
```bash
chmod +x draftshift-web/setup.sh
```

---

## Next Steps

1. **Explore Documentation**
   - [DraftShift Engine README](draftshift/DRAFTSHIFT_README.md) — Full API docs
   - [Web UI README](draftshift-web/README.md) — UI architecture
   - [Deployment Guide](draftshift-web/DEPLOY_REPLIT.md) — Advanced Replit setup

2. **Customize**
   - Modify YAML configs in `draftshift/formats/`
   - Update React components in `draftshift-web/src/`
   - Add new pleading types in `draftshift/pleadings/`

3. **Extend**
   - Add local rules library (Phase 2)
   - Implement case database (Phase 3)
   - Add user authentication (Phase 4)
   - See [DRAFTSHIFT_ROADMAP.md](draftshift/DRAFTSHIFT_ROADMAP.md) for full plan

---

## Key Directories

```
saoriverse-console/
├── draftshift/                    # Core engine
│   ├── pleadings/                 # Pleading classes
│   ├── formats/                   # YAML configurations
│   └── tests/                     # Test suite + fixtures
├── draftshift-web/                # Web UI
│   ├── api.py                     # FastAPI backend
│   ├── src/                       # React components
│   ├── index.html                 # HTML entry
│   └── dist/                      # Built production
├── DRAFTSHIFT_PLATFORM_SUMMARY.md # Complete overview
└── README.md                      # Main repo docs
```

---

## Support & Contact

- **Issues**: Check troubleshooting section above
- **Documentation**: See references section in main README
- **Examples**: Check `draftshift/tests/fixtures/` for sample JSON
- **Tests**: Run `pytest draftshift/tests/` for comprehensive test suite

---

## What's Next?

You now have a fully functional litigation document automation system!

### To test it:
1. Load a fixture
2. Build a pleading
3. Download the DOCX
4. Open in Word
5. Verify formatting matches California pleading paper

### To deploy it:
1. Push to GitHub (already done!)
2. Create Replit project from GitHub
3. Click "Run"
4. Share the URL

### To extend it:
1. Add new pleading types
2. Customize YAML configs
3. Add form-based editor
4. Implement user authentication
5. Build case database
6. Add e-filing integration

---

**Ready to automate your litigation workflow?**

DraftShift turns 2-3 hours of manual work into 20 minutes of automation.

Let's go! 🚀
