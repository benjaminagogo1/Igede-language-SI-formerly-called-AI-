"""Test fixtures shared by the test suite."""
import sys
from pathlib import Path

# Make `web` importable from repo root so app.py can be imported.
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from web.MVP import database as dbmod
from web.MVP import app as realmod
