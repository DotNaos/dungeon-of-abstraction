from pathlib import Path
from neurodungeon.config import load_config


def test_example_config_roundtrip():
    cfg_path = Path("examples/basic.yml")
    data = load_config(cfg_path)
    assert data["lives"] == 3
    assert data["llm_call_limit"] == 20
    assert data["floors"] == [1, 2]
