# Darwin Architecture

## System Overview

Darwin is a multi-layered text formatting system designed for cross-platform compatibility.

```
┌─────────────────────────────────────────────────────────┐
│           User Interface Layer                          │
│  (Word Task Pane / App-Specific UI)                    │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│         Word Add-in Layer                              │
│  (Office.js API Integration)                           │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│      Scanner & Adapter Layer                           │
│  (Environment Detection & Capability Mapping)          │
│  • Detect active application                           │
│  • Route to appropriate adapter                        │
│  • Handle environment-specific logic                   │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│       Adapter Implementations                          │
│  • WordAdapter → Office.js API calls                   │
│  • NotepadAdapter → Clipboard operations               │
│  • ExcelAdapter → Cell operations                      │
│  • UniversalAdapter → Generic operations               │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│        Core Formatting Layer                           │
│  • TextTransformer (case, whitespace, etc.)            │
│  • StyleFormatter (bold, italic, color, etc.)          │
│  • StructureFormatter (indent, align, lists, etc.)     │
│  • PatternMatcher (regex-based rules)                  │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│       Utilities & Infrastructure                       │
│  • Configuration Management                            │
│  • Logging & Debugging                                 │
│  • Error Handling                                      │
│  • Caching & Performance                               │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

### Typical Operation

1. **User Input** → Word Add-in task pane
2. **Add-in** → Routes to Core formatter (for Word-specific operations)
3. **Core Formatter** → Applies transformation logic
4. **Result** → Applied to Word document via Office.js

### Cross-Application Operation

1. **System Monitor** → Detects active application change
2. **Scanner** → Identifies environment capabilities
3. **Adapter Selection** → Chooses appropriate adapter
4. **Command Translation** → Converts to environment-specific operations
5. **Execution** → Applies formatting in detected application

## Component Details

### Word Add-in (TypeScript/JavaScript)

- Entry point for Word users
- Provides UI via task pane
- Calls core formatting engine
- Integrates with Office ribbon
- Real-time document analysis

### Scanner Module (Python)

- Continuously monitors active window
- Detects program type and capabilities
- Routes operations to appropriate adapters
- Handles inter-process communication
- Maintains environment state

### Core Formatting Engine (Python/TypeScript)

- Implements actual formatting logic
- Language-agnostic transformation algorithms
- Supports custom rules and presets
- Provides logging and debugging

### Adapters (Python)

- Environment-specific implementations
- Translate generic operations to platform APIs
- Handle platform limitations gracefully
- Provide fallback strategies

## Communication

- **Word Add-in ↔ Core**: Direct JavaScript/Python bridge or IPC
- **Scanner ↔ Adapters**: Direct Python imports
- **Scanner ↔ Core**: Shared library imports
- **Word Add-in ↔ Scanner**: Background service communication (WebSocket/HTTP)

## Configuration

- Environment detection rules
- Adapter capability mappings
- Formatting presets and templates
- Logging levels and output targets
- Performance optimization settings

## Future Extensibility

- Plugin system for custom formatters
- Machine learning for adaptive rules
- Multi-language support
- Browser-based web app version
- Integration with other Microsoft Office apps (Excel, PowerPoint)
