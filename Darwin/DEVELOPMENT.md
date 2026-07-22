# Darwin Development Guide

## Getting Started

### 1. Initial Setup

Clone or navigate to the Darwin project:

```bash
cd Darwin
```

### 2. Word Add-in Development

#### Prerequisites

- Node.js 16+
- npm or yarn
- Microsoft 365 or Office 2016+

#### Setup

```bash
cd word-addon
npm install
npm run dev
```

This will:

- Install dependencies
- Start webpack dev server
- Open Word with the add-in side-loaded
- Enable hot-reload during development

#### Testing in Word

- The add-in will appear in Word's ribbon
- Click "Show Taskpane" to open the formatting interface
- Make changes to code in `src/` folder
- Changes auto-reload in running Word instance

### 3. Scanner Module Development

#### Prerequisites

- Python 3.9+
- pip or poetry

#### Setup

```bash
cd scanner
python -m venv venv
.\venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

#### Running Tests

```bash
pytest tests/ -v
```

#### Development Workflow

1. Modify adapter or detector logic
2. Run tests to verify
3. Integration testing with running applications

### 4. Core Module Development

#### Setup

```bash
cd core
python -m venv venv
.\venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

#### Running Tests

```bash
pytest tests/ -v
```

## Development Workflow

### Code Organization

Follow these patterns:

**Python:**

```python
# Clear imports
from core.formatting import TextTransformer
from core.utils import logger

# Well-documented functions
def format_text(text: str, rules: dict) -> str:
    """
    Apply formatting rules to text.
    
    Args:
        text: Input text to format
        rules: Dict of formatting rules to apply
        
    Returns:
        Formatted text string
    """
    pass
```

**TypeScript:**

```typescript
// Clear typing
interface FormattingOptions {
  caseTo?: 'upper' | 'lower' | 'title';
  removeExtraSpaces?: boolean;
}

// Well-documented functions
async function applyFormatting(
  text: string, 
  options: FormattingOptions
): Promise<string> {
  // Implementation
}
```

### Testing Requirements

- All new features require tests
- Maintain >80% code coverage
- Run tests before committing
- Use descriptive test names

### Debugging

#### Word Add-in

- Open F12 developer tools in Word
- Check browser console for errors
- Use VS Code debugger with office-addin-debugging extension

#### Scanner/Core

- Use Python logging module
- Add debug prints with logger
- Use pytest with `-s` flag for output visibility

```python
from core.utils import logger

logger.debug(f"Detected environment: {env}")
logger.info("Formatting applied successfully")
logger.error("Failed to apply formatting", exc_info=True)
```

## Commit Guidelines

- Write clear, descriptive commit messages
- Reference issue numbers when applicable
- Keep commits focused and atomic
- Test before committing

Example:

```
git commit -m "feat: Add title case formatter to TextTransformer

- Implements title case conversion logic
- Adds comprehensive unit tests
- Fixes #42"
```

## Performance Considerations

- Profile code with heavy text operations
- Cache environment detection results
- Minimize round-trips between components
- Use async operations where possible

## Common Issues

### Issue: Word Add-in not loading

**Solution**:

- Check manifest.xml syntax
- Verify localhost port in dev server
- Clear Office cache: Delete files in `%APPDATA%\Microsoft\Office\16.0\Wef\`

### Issue: Scanner not detecting applications

**Solution**:

- Run as Administrator
- Check window class names with Window Detective tool
- Review detector logs

### Issue: Import errors in Python

**Solution**: (Reference from user memory)

- Install packages with exact interpreter: `python -m pip install package`
- Verify venv is activated
- Check Python path: `python -c "import sys; print(sys.executable)"`

## Next Steps

1. Set up your development environment for your primary module
2. Review existing code structure
3. Create a feature branch for your work
4. Follow code style and testing guidelines
5. Submit PR for review

## Resources

- [Office Add-in Development](https://learn.microsoft.com/office/dev/add-ins/)
- [Office JavaScript API](https://learn.microsoft.com/javascript/api/overview)
- [Python Best Practices](https://pep8.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
