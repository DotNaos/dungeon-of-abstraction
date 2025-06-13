from pathlib import Path

from neurodungeon.config import load_config


def test_load_yaml(tmp_path):
    cfg_path = tmp_path / "dungeon.yml"
    cfg_path.write_text("lives: 2\nllm_call_limit: 5\n")
    cfg = load_config(cfg_path)
    assert cfg["lives"] == 2
    assert cfg["llm_call_limit"] == 5
