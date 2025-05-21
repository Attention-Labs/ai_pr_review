import sys
from pathlib import Path

# Add the src directory to sys.path for tests
SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
