from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ["SERVICE_API_KEY"] = "apollo-dev-key"
os.environ["REQUIRE_API_KEY"] = "true"
