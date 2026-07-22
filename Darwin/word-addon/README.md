# Word Add-in: Darwin Formatter

Microsoft Word Add-in for the Darwin text formatting system.

## Features

- Custom text formatting commands
- Task pane interface for formatting controls
- Ribbon integration for quick access
- Real-time text analysis and suggestions

## Tech Stack

- **Framework**: Office JavaScript API (Office.js)
- **Language**: TypeScript
- **Build Tool**: Webpack
- **Testing**: Jest

## Setup

### Prerequisites

- Node.js 16+
- npm or yarn
- Microsoft Office (2016+) or Microsoft 365

### Installation

```bash
cd word-addon
npm install
```

### Development

```bash
npm run dev
```

This starts a local server and opens Word with the add-in loaded.

### Build

```bash
npm run build
```

Creates production-ready bundle in `dist/` folder.

## Project Structure

```
word-addon/
├── src/
│   ├── taskpane.ts       # Main task pane logic
│   ├── commands.ts       # Command implementations
│   └── helpers.ts        # Utility functions
├── taskpane/
│   ├── taskpane.html     # Task pane UI
│   └── taskpane.css
├── manifest.xml          # Add-in manifest
├── package.json
├── tsconfig.json
└── webpack.config.js
```

## Documentation

- [Office Add-in Development Guide](https://learn.microsoft.com/office/dev/add-ins/)
- [Office JavaScript API Reference](https://learn.microsoft.com/javascript/api/overview)
