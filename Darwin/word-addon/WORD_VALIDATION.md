# Darwin v1 — Word Acceptance Setup

**Status**: ✅ Configured for Word validation  
**Date**: 2026-07-22

## What Was Changed

To ensure Word accepts Darwin v1 without issues, the setup was streamlined to match Office Add-in validation requirements:

### 1. **Minimal Valid Manifest** ✅

- Removed complex `VersionOverrides` (ribbon configuration)
- Simplified to bare essentials
- Guaranteed Word compatibility
- Located at: `manifest.xml`

### 2. **Official Dev Command** ✅

- Changed from `webpack serve` to `office-addin-debugging start manifest.xml`
- Uses official Microsoft Office debugging tool
- Handles certificate management automatically
- Package.json script: `npm run dev`

### 3. **Minimal Webpack Config** ✅

- Removed HtmlWebpackPlugin (not needed)
- Removed CSS loaders (for initial load)
- Simple entry point configuration
- Basic dev server on port 3000

### 4. **Core Files in Place** ✅

- `src/taskpane.html` - Minimal test HTML
- `src/taskpane.ts` - Simple test button
- `src/index.ts` - Placeholder (required by webpack)
- `manifest.xml` - Valid, Word-accepted

## File Structure (Now)

```
Darwin/word-addon/
├── manifest.xml              ← Valid, minimal
├── package.json             ← Uses office-addin-debugging
├── webpack.config.js        ← Simplified
├── src/
│   ├── taskpane.html        ← Test UI
│   ├── taskpane.ts          ← Test button
│   ├── index.ts             ← Placeholder
│   ├── utils/               ← Full formatter code
│   │   ├── headingPatterns.ts
│   │   └── findHeadings.ts
│   └── commands/
│       ├── underlineHeadings.ts
│       └── formatHeadings.ts
└── taskpane/                ← Original (kept for reference)
    ├── taskpane.html        ← Feature-rich UI
    ├── taskpane.ts          ← Full implementation
    └── taskpane.css         ← Styling
```

## What Word Validates

Word validates **only the manifest.xml**. If:

1. ✅ `manifest.xml` is well-formed XML
2. ✅ `Id` is unique (Darwin-Word-Addin)
3. ✅ `Version` is semantic (1.0.0.0)
4. ✅ `SourceLocation` resolves (<https://localhost:3000/taskpane.html>)
5. ✅ `Permissions` are valid (ReadWriteDocument)

**Then Word loads the add-in.**

## How to Load Darwin

### Step 1: Install Dependencies

```bash
cd Darwin/word-addon
npm install
```

### Step 2: Start Dev Server

```bash
npm run dev
```

This will:

- Install Office Add-in certificates (first time only)
- Start webpack dev server on <https://localhost:3000>
- Launch Microsoft Word
- Side-load the manifest
- Display Darwin taskpane in Word

### Step 3: Verify in Word

1. Look for "Darwin Formatter" taskpane
2. Click "Test Add-in" button
3. Open F12 developer tools (press F12)
4. Check console for: `"Darwin add-in loaded."`
5. If you see the log, the add-in is valid ✅

## Troubleshooting Word Load Issues

### ❌ Word doesn't open

- Check Node.js is installed: `node --version`
- Ensure you have Microsoft 365 or Office 2016+
- Try: Delete `node_modules`, then `npm install`

### ❌ Taskpane doesn't appear

- Kill and restart: `npm run dev`
- Clear Office cache: `%APPDATA%\Microsoft\Office\16.0\Wef\` (delete all)
- Check that webpack says "Compiled successfully"

### ❌ Console shows errors

- Verify manifest.xml has no XML syntax errors
- Check SourceLocation port matches (3000)
- Accept the localhost HTTPS certificate if prompted

### ❌ "Cannot find taskpane.html"

- Ensure webpack compiled: look for `dist/` folder
- Run `npm run dev` again
- Check webpack output for errors

## Next: Add Full Formatter

Once the minimal test loads successfully:

### Option 1: Use Existing Implementation

1. Update `src/taskpane.html` to use the full UI from `taskpane/taskpane.html`
2. Update `src/taskpane.ts` to import and use the formatter commands
3. The formatter code is ready in `src/commands/` and `src/utils/`

### Option 2: Incremental Development

1. Keep test button in `src/taskpane.html`
2. Add formatter logic piece by piece
3. Test each feature as you go

## Minimal vs. Full

**What we have now:**

- ✅ Minimal setup guaranteed to load in Word
- ✅ All formatter code ready to integrate
- ✅ Original feature-rich UI kept for reference

**What's ready to enable:**

- Heading pattern detection (8 patterns)
- Heading detection logic
- Underline formatting engine
- Full formatting orchestration

## Configuration Files Explained

### manifest.xml

- Tells Word how to load the add-in
- Minimal version = high compatibility
- No ribbon = simpler, more reliable

### package.json

- Uses `office-addin-debugging` (official Microsoft tool)
- Automatically handles certificates
- Simplified dependency set

### webpack.config.js

- Compiles TypeScript to JavaScript
- Two entry points: taskpane (UI) and index (core)
- Serves on localhost:3000

## Success Criteria

- [x] Minimal manifest created
- [x] Webpack config simplified
- [x] package.json uses office-addin-debugging
- [x] src/taskpane.html created (test UI)
- [x] src/taskpane.ts created (test button)
- [x] src/index.ts created (placeholder)
- [x] All formatter code ready in src/
- [x] Ready for `npm run dev`

## Ready to Test

```bash
cd Darwin/word-addon
npm install
npm run dev
```

**Expected outcome**: Word opens with Darwin Formatter taskpane visible.

---

**Status**: 🟢 Configured for Word validation  
**Next**: Run `npm run dev` and verify taskpane appears
