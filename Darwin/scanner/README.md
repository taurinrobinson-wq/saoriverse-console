# Scanner Module: Environment Detection & Adaptation

The scanner module provides adaptive capability detection and automatic adjustment across different document editing environments.

## Purpose

- Detect active application (Word, Notepad, Excel, etc.)
- Identify available APIs and capabilities for each environment
- Route formatting commands to appropriate adapters
- Handle environment-specific quirks and limitations

## Architecture

### Adapters

Each supported application has an adapter that translates formatting operations:

- **WordAdapter** - Direct Office.js API calls
- **NotepadAdapter** - Clipboard + system clipboard operations
- **ExcelAdapter** - Cell-based formatting operations
- **UniversalAdapter** - Fallback for unsupported applications

### Environment Detection

- Window title analysis
- Process name detection
- API capability probing
- Feature availability mapping

## Tech Stack

- **Language**: Python 3.9+
- **Window Management**: pywin32, ctypes
- **Clipboard**: pyperclip

## Setup

### Installation

```bash
cd scanner
pip install -r requirements.txt
```

## Project Structure

```
scanner/
├── src/
│   ├── detector.py       # Environment detection engine
│   ├── adapters/
│   │   ├── base.py       # Base adapter interface
│   │   ├── word.py       # Word adapter
│   │   ├── notepad.py    # Notepad adapter
│   │   ├── excel.py      # Excel adapter
│   │   └── universal.py  # Universal fallback
│   └── monitor.py        # Active window monitoring
├── tests/
├── requirements.txt
└── README.md
```

## Usage

```python
from src.detector import EnvironmentDetector

detector = EnvironmentDetector()
current_env = detector.detect_active_environment()
adapter = detector.get_adapter_for_environment(current_env)
```

## Development

Run tests:

```bash
pytest tests/
```
