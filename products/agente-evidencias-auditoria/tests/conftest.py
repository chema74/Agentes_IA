from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ["MOCK_AUTH_ENABLED"] = "true"
os.environ["DEMO_AUTH_PASSWORD"] = "demo"
