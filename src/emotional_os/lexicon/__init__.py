# Re-export from sibling module
import sys
from pathlib import Path

# Add parent to path
parent_path = str(Path(__file__).parent.parent)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

# Import the sibling module
try:
    import emotional_os_lexicon as _sibling_module
    
    # Register all submodules from the sibling in sys.modules under emotional_os namespace
    for key, module in list(sys.modules.items()):
        if key.startswith('emotional_os_lexicon'):
            # Map sibling.X to emotional_os.lexicon.X
            new_key = key.replace('emotional_os_lexicon', 'emotional_os.lexicon')
            sys.modules[new_key] = module
    
    # Re-export all public attributes from sibling
    for _attr in dir(_sibling_module):
        if not _attr.startswith('_'):
            globals()[_attr] = getattr(_sibling_module, _attr)
except ImportError as e:
    import warnings
    warnings.warn(f"Failed to import emotional_os_lexicon: {e}")
