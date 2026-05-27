from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PHASE4 = ROOT / "phase4-integration"
sys.path.insert(0, str(PHASE4))

from pipeline import main


if __name__ == "__main__":
    main()
