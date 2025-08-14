import sys
from pathlib import Path


# Ensure src/ is importable when running pytest from backend/
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

