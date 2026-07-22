# Darwin - Adaptive Text Formatting Tool

Darwin is an intelligent text formatting tool designed to adapt across multiple document editing environments. It starts with native Microsoft Word integration and evolves to support Notepad, Excel, and other text-based applications through its adaptive scanning engine.

## Project Goal

Build a dynamic formatting system that:

- Provides powerful text formatting capabilities in Microsoft Word
- Automatically detects and adapts to different editing environments
- Applies consistent formatting logic across Word, Notepad, Excel, and other programs
- Learns and optimizes based on usage patterns

## Architecture

### Core Components

1. **word-addon/** - Microsoft Word add-in implementation
   - Office JavaScript API integration
   - Word-specific formatting operations
   - Task pane UI for formatting controls
   - Event handlers and ribbon integration

2. **scanner/** - Environment detection and adaptation layer
   - Program detection (Word, Notepad, Excel, etc.)
   - Active window monitoring
   - Environment capability mapping
   - API bridging between environments

3. **core/** - Shared formatting logic and utilities
   - Formatting engines (text transformation, styling, etc.)
   - Configuration management
   - Logging and debugging
   - Common utilities and helpers

4. **docs/** - Documentation and specifications
   - Architecture diagrams
   - API documentation
   - User guides
   - Development setup

## Project Structure

```
Darwin/
├── word-addon/          # Word Add-in (TypeScript/JavaScript)
│   ├── src/
│   ├── taskpane/
│   ├── manifest.xml
│   └── package.json
├── scanner/             # Environment Detection (Python)
│   ├── src/
│   ├── adapters/
│   └── requirements.txt
├── core/                # Shared Logic (Python/TypeScript)
│   ├── formatting/
│   ├── config/
│   └── utils/
├── docs/                # Documentation
└── README.md
```

## Getting Started

- [Word Add-in Setup](word-addon/README.md)
- [Scanner Module Setup](scanner/README.md)
- [Core Module Setup](core/README.md)

## Current Status

Project initialization phase. Structure and foundational architecture being established.
