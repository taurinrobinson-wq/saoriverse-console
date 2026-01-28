# DraftShift Web UI

A modern web interface for the DraftShift litigation document automation platform. Built with React, Vite, and FastAPI.

## Features

- **Fixture Selector**: Load pre-built test pleadings (Motion, Opposition, Reply, Declaration)
- **JSON Editor**: Edit document configuration directly in the browser
- **Type Selection**: Choose document type from dropdown
- **One-Click Build**: Generate DOCX from JSON with progress indicator
- **Direct Download**: Download generated pleadings immediately to your device
- **Responsive Design**: Works on desktop and tablet

## Quick Start

### Local Development

1. Install dependencies:
```bash
npm install
pip install -r requirements-api.txt
```

2. Start development servers in separate terminals:

**Terminal 1 - React Dev Server:**
```bash
npm run dev
```
Runs on `http://localhost:5173`

**Terminal 2 - FastAPI Backend:**
```bash
python -m uvicorn draftshift_web.api:app --reload --host 0.0.0.0 --port 8000
```
Runs on `http://localhost:8000`

3. Open browser to `http://localhost:5173`

### Production Build

Build React frontend for deployment:
```bash
npm run build
```

Outputs optimized files to `dist/` directory.

## Architecture

### Frontend (`src/`)

- `main.jsx` — React DOM entry point
- `App.jsx` — Main application component with state management
- `App.css` — Comprehensive styling (dark theme with purple gradient)
- `components/`
  - `FixtureSelector.jsx` — Load test fixtures
  - `JSONEditor.jsx` — Edit document JSON
  - `BuildButton.jsx` — Trigger document build
  - `DownloadButton.jsx` — Download generated DOCX

### Backend (`api.py`)

FastAPI application with three endpoints:

- `GET /api/health` — Health check & factory status
- `POST /api/build` — Build pleading from JSON
- `GET /api/fixtures/{name}` — Load test fixture JSON
- `GET /` — Serve React static files

## API Reference

### POST /api/build

Generate a pleading document.

**Request Body (JSON):**
```json
{
  "type": "motion|opposition|reply|declaration",
  "title": "MOTION FOR NEW TRIAL",
  "body": ["Section 1 text", "Section 2 text", ...],
  "signature_block": ["Attorney Name", "State Bar #123456"],
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

**Response (JSON):**
```json
{
  "success": true,
  "filename": "Motion.docx",
  "data": "UEsDBBQACAAI..."  // base64-encoded DOCX
}
```

### GET /api/fixtures/{name}

Load a test fixture JSON.

**Paths:**
- `/api/fixtures/motion` — Motion template
- `/api/fixtures/opposition` — Opposition template
- `/api/fixtures/reply` — Reply template
- `/api/fixtures/declaration` — Declaration template

**Response:** JSON fixture data

## Configuration

### Vite Configuration

`vite.config.js` configures:
- React Fast Refresh plugin
- Dev server proxy to localhost:8000
- Build output directory: `dist/`

### Replit Deployment

The `.replit` file configures Replit to:
- Run FastAPI backend on port 8000
- Auto-reload on file changes
- Expose port 8000 externally

### replit.nix

Specifies runtime dependencies:
- Python 3.11
- Node.js 20
- Yarn package manager

## Deployment

### Deploy to Replit

1. Push repository to GitHub
2. Go to [replit.com](https://replit.com) and create new Replit
3. Import from GitHub repository
4. Replit auto-configures from `.replit` and `replit.nix`
5. Application runs at `https://draftshift.replit.dev`

**Automated steps on Replit:**
1. Install Python dependencies: `pip install -r requirements-api.txt`
2. Install Node dependencies: `npm install`
3. Build React: `npm run build`
4. Start FastAPI server: `python -m uvicorn draftshift_web.api:app --host 0.0.0.0 --port 8000`
5. FastAPI serves built React files from `dist/`

## File Structure

```
draftshift-web/
├── api.py                 # FastAPI backend
├── package.json          # Node dependencies
├── vite.config.js        # Vite configuration
├── index.html            # HTML entry point
├── .replit               # Replit configuration
├── replit.nix            # Replit dependencies
├── .gitignore           # Git ignore rules
├── src/
│   ├── main.jsx          # React entry point
│   ├── App.jsx           # Main app component
│   ├── App.css           # App styling
│   ├── index.css         # Global styling
│   └── components/
│       ├── FixtureSelector.jsx
│       ├── JSONEditor.jsx
│       ├── BuildButton.jsx
│       └── DownloadButton.jsx
└── dist/                 # Built React (generated)
```

## Styling

The UI features:
- **Color Scheme**: Dark theme with purple/cyan accents
- **Gradient Background**: Dynamic linear gradient
- **Responsive Layout**: Flexbox-based two-column design
- **Interactive Elements**: Hover effects, loading states
- **Accessibility**: Proper contrast ratios, keyboard navigation

## Troubleshooting

### CORS Errors

If you see CORS errors:
1. Ensure FastAPI backend is running on `http://localhost:8000`
2. Check `vite.config.js` proxy configuration
3. Verify `api.py` has CORS middleware enabled

### Fixture Loading Fails

If fixtures don't load:
1. Ensure `draftshift/tests/fixtures/` directory exists
2. Check JSON files are properly formatted
3. Verify relative paths in `api.py`

### Build Errors

If document generation fails:
1. Check JSON format matches schema
2. Review `api.py` logs for validation errors
3. Ensure `draftshift` package is installed

### Port Conflicts

If port 8000 is in use:
```bash
python -m uvicorn draftshift_web.api:app --port 8001
# Then update vite.config.js proxy target
```

## Performance Optimization

- **React Fast Refresh** for development
- **Vite code splitting** for production bundles
- **Base64 encoding** for efficient file transfer
- **Lazy static file serving** via FastAPI

## Future Enhancements

- [ ] Form-based JSON editor (replace textarea)
- [ ] Template library with custom rules
- [ ] Batch document generation
- [ ] Citation auto-formatter
- [ ] PDF export option
- [ ] Real-time document preview
- [ ] User authentication & saved drafts
- [ ] Version history/collaboration

## License

Part of the DraftShift platform. See main repository for license.

## Support

For issues or feature requests, see the main DraftShift repository.
