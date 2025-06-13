"""Load dungeon configuration from YAML or JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_config(path: Path) -> Dict[str, Any]:
    """Return configuration dictionary from a YAML or JSON file."""
    if path.suffix in {".yml", ".yaml"}:
        import yaml  # type: ignore

        with path.open() as f:
            data = yaml.safe_load(f) or {}
    else:
        with path.open() as f:
            data = json.load(f)
    assert isinstance(data, dict)
    return data
