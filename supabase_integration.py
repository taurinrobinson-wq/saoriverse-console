#!/usr/bin/env python3

import requests
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

@dataclass
class SaoriResponse:
    reply: str
    glyph: Optional[Dict]
    from tools.supabase_integration import *
