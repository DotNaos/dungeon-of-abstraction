"""Demo script for NeuroDungeon Protocol v0.1."""

from neurodungeon.agents import StubBoss, StubEnemy, StubPlayer
from neurodungeon.models import RunConfig, Vote
from neurodungeon.orchestrator import Orchestrator


def run_demo(cfg: RunConfig, enemies) -> None:
    orch = Orchestrator(StubPlayer(), enemies, StubBoss())
    result = orch.run("demo goal", cfg)
    if result is Vote.ACCEPT:
        print("PASS")
    else:
        print("FAIL")


def main() -> None:
    run_demo(RunConfig(run_id="demo_success"), [[StubEnemy()] for _ in range(8)])
    run_demo(RunConfig(run_id="demo_life_loss", rejection_thresh=1), [[StubEnemy()] for _ in range(2)])
    run_demo(RunConfig(run_id="demo_fail", lives=1, rejection_thresh=1), [[StubEnemy()] for _ in range(2)])


if __name__ == "__main__":
    main()
