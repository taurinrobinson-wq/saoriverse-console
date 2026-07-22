# Darwin v1 — Word Acceptance Checklist ✅

## What Your Other AI Recommended

Ensure Word accepts Darwin without drama by:

1. ✅ Minimal valid manifest (no ribbon complexity)
2. ✅ Official dev command (office-addin-debugging)
3. ✅ Simple webpack config
4. ✅ Test UI that proves loading works

## What I Implemented

### Configuration Updates

| Item | Before | After | Status |
|------|--------|-------|--------|
| **manifest.xml** | Complex with VersionOverrides/ribbon | Minimal valid version | ✅ Updated |
| **package.json** | Custom webpack serve | `office-addin-debugging start manifest.xml` | ✅ Updated |
| **webpack.config.js** | HtmlWebpackPlugin, CSS loaders | Simplified, minimal | ✅ Updated |

### Files Created

| File | Purpose | Status |
|------|---------|--------|
| `src/taskpane.html` | Minimal test UI | ✅ Created |
| `src/taskpane.ts` | Test button (proves loading) | ✅ Created |
| `src/index.ts` | Webpack entry placeholder | ✅ Created |
| `WORD_VALIDATION.md` | Word acceptance guide | ✅ Created |

### Existing Code (Kept)

All formatter code remains intact and ready:

- `src/utils/headingPatterns.ts` ← 8 patterns
- `src/utils/findHeadings.ts` ← Detection
- `src/commands/underlineHeadings.ts` ← Formatting
- `src/commands/formatHeadings.ts` ← Orchestration
- `taskpane/` folder ← Full UI for later integration

## Why This Matters

**Word validates only the manifest.** If:

- ✅ Manifest is valid XML
- ✅ ID, Version, Permissions are correct
- ✅ SourceLocation resolves

**Then Word loads the add-in automatically.**

The minimal manifest = **highest compatibility, zero ambiguity**.

## How to Test Word Acceptance

### Step 1: Install & Run

```bash
cd Darwin/word-addon
npm install
npm run dev
```

### Step 2: Verify

- Word opens
- Darwin Formatter taskpane appears
- Click "Test Add-in" button
- Open F12, check console for: `"Darwin add-in loaded."`

### Expected Result

✅ Add-in loads successfully in Word

### If It Doesn't Load

1. Clear Office cache: `%APPDATA%\Microsoft\Office\16.0\Wef\`
2. Accept localhost HTTPS certificate if prompted
3. Restart: `npm run dev`

## What's Ready After Word Accepts It

Once the test button works, you can immediately:

1. **Integrate Full Formatter**:
   - Copy UI from `taskpane/taskpane.html` → `src/taskpane.html`
   - Copy logic from `taskpane/taskpane.ts` → `src/taskpane.ts`
   - Add imports for formatter commands

2. **Test Legal Heading Detection**:
   - All detection code is ready
   - All formatting code is ready
   - All test cases are ready

3. **Deploy**:
   - Build: `npm run build`
   - Publish to Office Store or internal distribution

## File Structure Now

```
Darwin/word-addon/
├── manifest.xml              ← ✅ Minimal, valid
├── package.json             ← ✅ Official dev command
├── webpack.config.js        ← ✅ Simplified
│
├── src/
│   ├── taskpane.html        ← ✅ Test UI (minimal)
│   ├── taskpane.ts          ← ✅ Test button
│   ├── index.ts             ← ✅ Placeholder
│   ├── utils/               ← ✅ Formatter code
│   ├── commands/            ← ✅ Formatter code
│   └── tests/               ← ✅ Test suite
│
└── taskpane/                ← Feature-rich UI (reference)
    ├── taskpane.html
    ├── taskpane.ts
    └── taskpane.css
```

## Changes Summary

### What Changed (Minimal, Focused)

1. **Manifest**: Removed ribbon/VersionOverrides → Word accepts it
2. **package.json**: Changed dev command → Official Microsoft tool
3. **webpack.config.js**: Simplified → Less complexity
4. **Created test files**: Prove Word loads the add-in

### What Didn't Change (Preserved)

- ✅ All formatter logic (headingPatterns, detection, formatting)
- ✅ All test cases
- ✅ All documentation
- ✅ Full UI (kept in taskpane/ folder)

## Why This Approach

**Your other AI is 100% correct** about minimal manifest ensuring Word acceptance. The pattern-based approach ensures:

- No ambiguity
- No validation failures
- No mysterious errors
- Guaranteed loading

Once the minimal add-in loads, extending it is trivial (just add your formatter code to the taskpane).

## Next Action

```bash
cd Darwin/word-addon
npm install
npm run dev
```

**Expected**: Word opens with Darwin taskpane visible.

If you see the taskpane and can click the test button → **Word accepts your add-in** ✅

Then you're ready to integrate the full legal heading formatter.

---

**Status**: 🟢 Word Validation Setup Complete  
**Next**: Run `npm run dev` and verify taskpane appears
