import sys
from pathlib import Path

# Let the tests import the function code from backend/api.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))
