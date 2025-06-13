from pathlib import Path

from neurodungeon.agents import StubBoss, StubEnemy, StubPlayer
from neurodungeon.models import RunConfig, Vote, FloorArtifact, Hint
from neurodungeon.orchestrator import Orchestrator
from hypothesis import given, strategies as st
import pytest


def test_happy_path(tmp_path):
    cfg = RunConfig(run_id=str(tmp_path / "run1"))
    enemies = [[StubEnemy()] for _ in range(8)]
    orch = Orchestrator(StubPlayer(), enemies, StubBoss())
    result = orch.run("goal", cfg)
    assert result is Vote.ACCEPT


def test_life_loss(tmp_path):
    cfg = RunConfig(run_id=str(tmp_path / "run2"), rejection_thresh=1)
    enemies = [[StubEnemy()] for _ in range(2)]
    orch = Orchestrator(StubPlayer(), enemies, StubBoss())
    result = orch.run("goal", cfg)
    assert result is Vote.ACCEPT
    assert orch.lives == cfg.lives - 2


def test_life_exhaustion(tmp_path):
    cfg = RunConfig(run_id=str(tmp_path / "run3"), rejection_thresh=1, lives=2)
    enemies = [[StubEnemy()] for _ in range(8)]
    orch = Orchestrator(StubPlayer(), enemies, StubBoss())
    result = orch.run("goal", cfg)
    assert result is Vote.REJECT
    assert orch.lives == 0


def test_multi_enemy_threshold(tmp_path):
    cfg = RunConfig(run_id=str(tmp_path / "run_multi"), rejection_thresh=0)
    enemies = [[StubEnemy() for _ in range(4)]]
    orch = Orchestrator(StubPlayer(), enemies, StubBoss())
    orch.run("goal", cfg)
    assert orch.lives == cfg.lives - 1


def test_hint_propagation(tmp_path):
    cfg = RunConfig(run_id=str(tmp_path / "hints"), rejection_thresh=1)
    enemies = [[StubEnemy()], [StubEnemy()]]
    player = StubPlayer()
    orch = Orchestrator(player, enemies, StubBoss())
    orch.run("goal", cfg)
    assert "1 hints" in orch.artifacts[1].content


def test_hint_forwarded_on_accept(tmp_path):
    class HintEnemy(StubEnemy):
        def evaluate(self, artifact: FloorArtifact):
            return Vote.ACCEPT, (Hint(text="hi"),)

    cfg = RunConfig(run_id=str(tmp_path / "forward"))
    enemies = [[HintEnemy()], [StubEnemy()]]
    orch = Orchestrator(StubPlayer(), enemies, StubBoss())
    orch.run("goal", cfg)
    assert "1 hints" in orch.artifacts[1].content


@given(lives=st.integers(min_value=1, max_value=4), losses=st.integers(min_value=0, max_value=4))
def test_accept_iff_rejections_lt_lives(tmp_path_factory, lives: int, losses: int) -> None:
    run_dir = tmp_path_factory.mktemp("run_prop")
    cfg = RunConfig(run_id=str(run_dir), rejection_thresh=1, lives=lives)

    class AcceptEnemy(StubEnemy):
        def evaluate(self, artifact: FloorArtifact):
            return Vote.ACCEPT, ()

    enemies: list[list[StubEnemy]] = []
    for _ in range(losses):
        enemies.append([StubEnemy()])
    for _ in range(8 - losses):
        enemies.append([AcceptEnemy()])

    orch = Orchestrator(StubPlayer(), enemies, StubBoss())
    result = orch.run("goal", cfg)
    assert (result is Vote.ACCEPT) == (losses < lives)
