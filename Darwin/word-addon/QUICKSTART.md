# Darwin v1 — Quick Start

**Status**: ✅ Implementation Complete  
**Goal**: Format legal headings in Word with one click

## 30-Second Setup

```bash
cd Darwin/word-addon
npm install
npm run dev
```

That's it. Word opens with Darwin loaded.

## What You Get

**Button in Word Ribbon**: "Format Legal Headings"

Click it → Darwin:

1. Scans document for all legal headings
2. Applies single underline
3. Preserves everything else

## What Gets Detected

- `Interrogatory No. 1`
- `Request for Production No. 3`
- `Topic No. 12`
- `INTRODUCTION` (all caps headings)
- 8 total pattern types

## Built & Ready

✅ TypeScript source code  
✅ Unit tests (5 test cases)  
✅ Professional UI  
✅ Webpack build configured  
✅ Jest testing ready  
✅ Manifest for Word ready  

## Commands

```bash
npm run dev          # Start dev server (localhost:3000)
npm run build        # Production build
npm test            # Run tests
npm run lint        # Check code style
npm run format      # Format code
```

## File Structure

```
Darwin/word-addon/
├── src/
│   ├── utils/headingPatterns.ts    # Pattern library
│   ├── utils/findHeadings.ts       # Detection
│   └── commands/
│       ├── underlineHeadings.ts    # Formatting
│       └── formatHeadings.ts       # Main command
├── taskpane/
│   ├── taskpane.html              # UI
│   ├── taskpane.ts                # Events
│   └── taskpane.css               # Styling
├── tests/headingFormatter.test.ts  # Tests
└── [config files]
```

## Next Feature

**Option B**: Add spacing presets

- "Apply Pleading Spacing (24 pt)"
- "Apply Legal Spacing (12 pt)"

---

**Start now**: `npm run dev`
