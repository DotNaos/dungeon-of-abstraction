from neurodungeon.agents import StubBoss, StubEnemy, StubPlayer
from neurodungeon.models import RunConfig, Vote, FloorArtifact, Hint
from neurodungeon.orchestrator import Orchestrator
from datetime import datetime
import json
import pytest


def test_artifact_size_limit(tmp_path):
    cfg = RunConfig(run_id=str(tmp_path / "run4"), max_artifact_bytes=10)

    class BigPlayer(StubPlayer):
        def act(self, floor: int, hints: list[Hint]):
            return FloorArtifact(floor=floor, revision=0, content="X" * 20, ext=".txt")

    enemies = [StubEnemy()]
    orch = Orchestrator(BigPlayer(), [enemies], StubBoss())
    with pytest.raises(ValueError):
        orch.run("goal", cfg)


def test_llm_call_limit(tmp_path):
    cfg = RunConfig(run_id=str(tmp_path / "limit"), llm_call_limit=2)
    enemies = [[] for _ in range(2)]
    orch = Orchestrator(StubPlayer(), enemies, StubBoss())
    with pytest.raises(RuntimeError):
        orch.run("goal", cfg)
    cfg_ok = RunConfig(run_id=str(tmp_path / "ok"), llm_call_limit=2)
    orch_ok = Orchestrator(StubPlayer(), [[]], StubBoss())
    orch_ok.run("goal", cfg_ok)


def test_call_count(tmp_path):
    cfg = RunConfig(run_id=str(tmp_path / "calls"), rejection_thresh=1)
    enemies = [[StubEnemy()], [StubEnemy(), StubEnemy()]]
    orch = Orchestrator(StubPlayer(), enemies, StubBoss())
    orch.run("goal", cfg)
    expected = sum(1 + len(e) for e in enemies) + 1
    assert orch.llm_calls == expected


def test_audit_log(tmp_path):
    cfg = RunConfig(run_id=str(tmp_path / "log"), rejection_thresh=1)
    enemies = [[StubEnemy()], [StubEnemy()]]
    orch = Orchestrator(StubPlayer(), enemies, StubBoss())
    orch.run("goal", cfg)
    log = (cfg.persist_dir / "log.jsonl").read_text().strip().splitlines()
    data = [json.loads(line) for line in log]
    assert any("life_lost" in d for d in data)
    assert data[-1]["boss_vote"] == "ACCEPT"
    for rec in data:
        assert "timestamp" in rec
        # ensure valid ISO-8601, Z suffix
        assert rec["timestamp"].endswith("Z")
        datetime.fromisoformat(rec["timestamp"].replace("Z", "+00:00"))


def test_stub_enemy_hints_tuple() -> None:
    vote, hints = StubEnemy().evaluate(
        FloorArtifact(floor=0, revision=0, content="", ext=".txt")
    )
    assert isinstance(hints, tuple)
