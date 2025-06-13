"""Command-line interface for quick NeuroDungeon runs."""

from argparse import ArgumentParser
from pathlib import Path

import os
from .agents import StubBoss, StubEnemy, StubPlayer
from .agents_llm import PlayerLLM, LintEnemyLLM
from .models import RunConfig
from .orchestrator import Orchestrator
from .config import load_config
from .report import render_report


def cli() -> None:
    parser = ArgumentParser(description="Run NeuroDungeon with stub or LLM-backed agents")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--lives", type=int, default=3)
    parser.add_argument("--persist-dir", type=Path, default=None)
    parser.add_argument("--enemies", type=int, default=8)
    parser.add_argument("--config", type=Path, default=None)
    args = parser.parse_args()

    if args.config:
        cfg_data = load_config(args.config)
        lives = cfg_data.get("lives", args.lives)
        enemies_num = cfg_data.get("enemies", args.enemies)
        floors = cfg_data.get("floors")
        llm_limit = cfg_data.get("llm_call_limit", 50)
    else:
        lives = args.lives
        enemies_num = args.enemies
        floors = None
        llm_limit = 50

    use_llm = bool(args.config and os.getenv("OPENAI_API_KEY"))
    if floors:
        enemies = [
            [LintEnemyLLM() if use_llm else StubEnemy() for _ in range(n)]
            for n in floors
        ]
    else:
        enemies = [
            [LintEnemyLLM() if use_llm else StubEnemy()] for _ in range(enemies_num)
        ]
    player = PlayerLLM(args.goal) if use_llm else StubPlayer()
    orch = Orchestrator(player, enemies, StubBoss())
    cfg = RunConfig(
        run_id="cli_run",
        lives=lives,
        persist_dir=args.persist_dir,
        llm_call_limit=llm_limit,
    )
    orch.run(args.goal, cfg)
    log_path = cfg.persist_dir / "log.jsonl" if cfg.persist_dir else Path(cfg.run_id) / "log.jsonl"
    print(f"Run {cfg.run_id} complete — log: {log_path.resolve()}")
    report_md = render_report(cfg.run_id, orch.artifacts, log_path, orch.llm_calls, cfg.lives)
    run_dir = cfg.persist_dir
    assert run_dir is not None
    (run_dir / "report.md").write_text(report_md)


if __name__ == "__main__":
    cli()
