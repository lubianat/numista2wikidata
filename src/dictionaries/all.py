import json
import os
from pathlib import Path

HERE = Path(__file__).parent.resolve()

DICTS = {path.stem: json.loads(path.read_text()) for path in HERE.glob("*.json")}
