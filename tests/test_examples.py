from pathlib import Path
from neurodungeon.config import load_config
from neurodungeon.models import RunConfig


def test_example_config_roundtrip():
    cfg_path = Path("examples/basic.yml")
    data = load_config(cfg_path)
    assert data["lives"] == 3
    assert data["llm_call_limit"] == 20
    assert data["floors"] == [1, 2]
    cfg = RunConfig(run_id="x", **data)
    json_data = cfg.model_dump_json()
    cfg2 = RunConfig.model_validate_json(json_data)
    assert cfg == cfg2
