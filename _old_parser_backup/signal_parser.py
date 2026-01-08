import json
from typing import Dict, List, Tuple

def load_signal_map(base_path: str, learned_path: str = None) -> Dict[str, Dict]:
    try:
        with open(base_path, 'r', encoding='utf8') as f:
            data = json.load(f)
            return data
    except Exception:
        return {}


def parse_signals(text: str) -> List[Tuple[str, float]]:
    # Very small stub: return empty list
    return []
