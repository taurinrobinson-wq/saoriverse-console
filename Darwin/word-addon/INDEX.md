# Darwin v1: Legal Heading Formatter

## 🚀 Quick Links

**Start Here**: [QUICKSTART.md](./QUICKSTART.md) — 30 seconds to running Darwin  
**Overview**: [IMPLEMENTATION.md](./IMPLEMENTATION.md) — Complete technical guide  
**Checklist**: [CHECKLIST.md](./CHECKLIST.md) — What's done, what's next  
**README**: [README.md](./README.md) — Feature overview  

## What Is Darwin?

Darwin is an intelligent text formatting tool for Microsoft Word that:

1. **Detects legal headings** automatically (interrogatories, requests, sections, etc.)
2. **Applies consistent formatting** with one click
3. **Preserves all document content** — no regeneration, no spacing changes
4. **Adapts to other programs** through a scanning module (future phases)

## v1 Focus: Legal Heading Formatter

### One Button. One Click. Perfect Formatting

Click "Format Legal Headings" → Darwin:

```
✓ Scans entire document
✓ Finds all legal headings (8 pattern types)
✓ Applies single underline
✓ Preserves everything else
```

### Heading Types Detected

- Interrogatory No. 1, 2, 3...
- Special Interrogatory No. X
- Form Interrogatory No. X
- Request for Production No. X
- Request for Admission No. X
- Topic No. X
- Document Request No. X
- ALL CAPS section headings

## Built & Ready to Run

```bash
cd word-addon
npm install
npm run dev
```

**That's it.** Word opens with Darwin loaded.

## Architecture

**Deterministic formatting engine:**

```
User Click
  ↓
Ribbon Command
  ↓
Pattern Detection (headingPatterns.ts)
  ↓
Paragraph Matching (findHeadings.ts)
  ↓
Underline Formatting (underlineHeadings.ts)
  ↓
Word Document Updated
```

## File Structure

```
Darwin/word-addon/
├── src/
│   ├── utils/
│   │   ├── headingPatterns.ts    ← 8 heading patterns
│   │   └── findHeadings.ts       ← Detection engine
│   └── commands/
│       ├── underlineHeadings.ts  ← Formatting engine
│       └── formatHeadings.ts     ← Main command
├── taskpane/
│   ├── taskpane.html            ← UI button + description
│   ├── taskpane.ts              ← Event handlers
│   └── taskpane.css             ← Professional styling
├── tests/
│   └── headingFormatter.test.ts  ← 5 test cases
├── manifest.xml                  ← Word add-in config
├── package.json                  ← Dependencies
├── tsconfig.json                 ← TypeScript config
├── webpack.config.js            ← Build config
├── jest.config.js               ← Test config
├── QUICKSTART.md                ← This file's sibling
├── IMPLEMENTATION.md            ← Deep dive guide
└── CHECKLIST.md                 ← Progress tracking
```

## Key Files Explained

| File | Purpose | Status |
|------|---------|--------|
| `src/utils/headingPatterns.ts` | Pattern library (RegExp array) | ✅ Complete |
| `src/utils/findHeadings.ts` | Detects headings in paragraphs | ✅ Complete |
| `src/commands/underlineHeadings.ts` | Applies underline formatting | ✅ Complete |
| `src/commands/formatHeadings.ts` | Orchestrates the full flow | ✅ Complete |
| `taskpane/taskpane.html` | UI with button & instructions | ✅ Complete |
| `taskpane/taskpane.ts` | Button click handler | ✅ Complete |
| `taskpane/taskpane.css` | Professional styling | ✅ Complete |
| `tests/headingFormatter.test.ts` | 5 comprehensive test cases | ✅ Complete |
| `manifest.xml` | Word add-in configuration | ✅ Complete |
| `package.json` | Dependencies & build scripts | ✅ Complete |

## Test Cases

All 5 test cases pass:

1. **Discovery Set** — Interrogatory + Response headings
2. **Pleading Sections** — ALL CAPS section headings
3. **PMK Notice** — Topic + Document Request headings
4. **Mixed Legal Document** — Complex multi-heading document
5. **Edge Cases** — Case variations, boundary conditions

## Commands

```bash
npm run dev              # Start development server
npm run build            # Production build
npm test                # Run tests
npm run lint            # Check code style
npm run format          # Format code
```

## Next Feature: Spacing Presets (Option B)

After legal heading formatter:

- **"Apply Pleading Spacing (24 pt)"**
- **"Apply Legal Spacing (12 pt)"**

Uses the same deterministic engine.

## Design Philosophy

✅ **Zero Regeneration** — Text is never modified  
✅ **Preserve Structure** — All spacing and layout preserved  
✅ **Case Insensitive** — Matches all case variations  
✅ **Deterministic** — Same input = same output, always  
✅ **One Click** — Ribbon button + taskpane  
✅ **Professional** — Enterprise-grade UI  

## Technology Stack

- **Language**: TypeScript
- **Framework**: Office JavaScript API
- **Build**: Webpack 5
- **Testing**: Jest
- **Linting**: ESLint
- **Formatting**: Prettier

## Getting Started

### For Development

```bash
cd Darwin/word-addon
npm install
npm run dev
```

Opens Word with Darwin loaded. Changes auto-reload.

### For Testing

```bash
npm test
npm run test:watch
```

### For Production

```bash
npm run build
```

Creates optimized bundle in `dist/`.

## Documentation Map

```
Darwin/word-addon/
├── README.md              ← Feature overview
├── QUICKSTART.md          ← 30-second setup
├── IMPLEMENTATION.md      ← Technical deep dive
├── CHECKLIST.md           ← Progress & next steps
├── INDEX.md               ← This file (navigation)
├── src/                   ← Source code
├── tests/                 ← Test suite
└── [config files]
```

## Success Metrics

✅ All 8 heading patterns detected  
✅ Single underline applied correctly  
✅ No text modification  
✅ No spacing changes  
✅ All tests pass  
✅ One-click operation  
✅ Professional UI  
✅ TypeScript strict mode  
✅ Production-ready build  
✅ Zero dependencies on Word document structure  

## Ready to Deploy

Darwin v1 is **complete and ready for**:

- ✅ Local development (`npm run dev`)
- ✅ Integration testing with real legal documents
- ✅ User acceptance testing
- ✅ Production deployment
- ✅ Feature extension (spacing presets, etc.)

## Questions?

Refer to:

1. [QUICKSTART.md](./QUICKSTART.md) for setup
2. [IMPLEMENTATION.md](./IMPLEMENTATION.md) for technical details
3. [CHECKLIST.md](./CHECKLIST.md) for status and next steps

---

**Status**: 🟢 Implementation Complete  
**Version**: 1.0.0  
**Date**: 2026-07-22  

**Next Move**: Run `npm run dev`
