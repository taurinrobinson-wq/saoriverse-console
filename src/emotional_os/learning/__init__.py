# Re-export from sibling module
import sys
from pathlib import Path
import importlib.util

# Add parent to path
parent_path = str(Path(__file__).parent.parent)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

# Set up a module finder to handle the namespace translation
class EmotionalOSLearningFinder:
    """Finder that maps emotional_os.learning.* to emotional_os_learning.*"""
    
    def find_module(self, fullname, path=None):
        if fullname.startswith('emotional_os.learning.') and fullname != 'emotional_os.learning':
            # Extract the submodule name
            submodule = fullname.replace('emotional_os.learning.', '')
            actual_fullname = f'emotional_os_learning.{submodule}'
            
            try:
                spec = importlib.util.find_spec(actual_fullname)
                if spec:
                    return self
            except (ModuleNotFoundError, ValueError):
                pass
        return None
    
    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        
        submodule = fullname.replace('emotional_os.learning.', '')
        actual_fullname = f'emotional_os_learning.{submodule}'
        
        # Import the actual module
        actual_module = __import__(actual_fullname, fromlist=[submodule])
        
        # Register it under the emotional_os namespace
        sys.modules[fullname] = actual_module
        return actual_module

# Install the finder
if not any(isinstance(finder, EmotionalOSLearningFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, EmotionalOSLearningFinder())

# Import the sibling module
try:
    import emotional_os_learning as _sibling_module
    
    # Register all submodules from the sibling in sys.modules under emotional_os namespace
    for key, module in list(sys.modules.items()):
        if key.startswith('emotional_os_learning'):
            # Map sibling.X to emotional_os.learning.X
            new_key = key.replace('emotional_os_learning', 'emotional_os.learning')
            sys.modules[new_key] = module
    
    # Re-export all public attributes from sibling
    for _attr in dir(_sibling_module):
        if not _attr.startswith('_'):
            globals()[_attr] = getattr(_sibling_module, _attr)
except ImportError as e:
    # Only warn about critical import errors, not about submodule lookup failures
    error_str = str(e)
    if 'conversation_archetype' not in error_str:
        import warnings
        warnings.warn(f"Failed to import emotional_os_learning: {e}")

from .proto_glyph_manager import *  # noqa: F401,F403
from .subordinate_bot_responder import *  # noqa: F401,F403
from .dominant_bot_orchestrator import *  # noqa: F401,F403
from .glyph_synthesizer import *  # noqa: F401,F403
from .learning_pipeline import *  # noqa: F401,F403
