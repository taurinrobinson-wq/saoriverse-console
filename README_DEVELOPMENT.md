# Saoriverse Console Development Guide

## 🎯 Active Development Stack

The main application consists of these key files:

1. **Main Entry Point**
   - `main_v2.py` (root directory)

2. **Core Modules** (under `emotional_os/deploy/modules/`)
   - `ui.py` - Core UI rendering and logic
   - `auth.py` - Authentication system
   - Other supporting modules

## 🚫 Deprecated/Archived Files

Previous versions of the UI have been moved to the `deprecated/` directory:
- `emotional_os_ui.py` (old version)
- `emotional_os_ui_v2.py` (old version)

Additional archived files exist in:
- `emotional_os/archive/`
- `src/ui/` (retired stubs)
- `archive/previous_uis/`

⚠️ Do not modify or reference deprecated files. All new development should target the active stack.

## 🏃‍♂️ Running the Application

```bash
# Activate virtual environment (if using one)
source .venv/bin/activate

# Run the main application
streamlit run main_v2.py
```

## 💡 Development Guidelines

1. **Entry Point**: Always use `main_v2.py` as the application entry point
2. **UI Changes**: Make UI modifications in `emotional_os/deploy/modules/ui.py`
3. **Testing**: Test changes by running through `main_v2.py`
4. **Documentation**: Update this guide when making architectural changes