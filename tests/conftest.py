import sys
from pathlib import Path


# Ensure backend/src is importable when running tests from repo root
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "backend" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

