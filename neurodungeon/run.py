"""Command-line interface for quick NeuroDungeon runs."""

from argparse import ArgumentParser
from pathlib import Path

from .agents import StubBoss, StubEnemy, StubPlayer
from .models import RunConfig
from .orchestrator import Orchestrator


def cli() -> None:
    parser = ArgumentParser(description="Run NeuroDungeon with stub agents")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--lives", type=int, default=3)
    parser.add_argument("--persist-dir", type=Path, default=None)
    args = parser.parse_args()

    enemies = [[StubEnemy()] for _ in range(8)]
    orch = Orchestrator(StubPlayer(), enemies, StubBoss())
    cfg = RunConfig(run_id="cli_run", lives=args.lives, persist_dir=args.persist_dir)
    result = orch.run(args.goal, cfg)
    log_path = (cfg.persist_dir / "log.jsonl") if cfg.persist_dir else Path(cfg.run_id) / "log.jsonl"
    print(result.value)
    print(f"Run ID: {cfg.run_id}")
    print(f"Audit log: {log_path.resolve()}")


if __name__ == "__main__":
    cli()
