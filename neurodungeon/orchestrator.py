"""Core orchestrator for NeuroDungeon runs."""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import List, Sequence, Any

from .agents import Boss, Enemy, Player
from .models import FloorArtifact, Hint, RunConfig, Vote


class Orchestrator:
    """State machine managing floors, lives, and persistence."""

    def __init__(self, player: Player, enemies_per_floor: Sequence[Sequence[Enemy]], boss: Boss) -> None:
        self.player = player
        self.enemies_per_floor = list(enemies_per_floor)
        self.boss = boss
        self.llm_calls = 0
        self.artifacts: List[FloorArtifact] = []
        self.lives = 0

    def _check_limits(self, cfg: RunConfig, artifact: FloorArtifact | None = None) -> None:
        if artifact is not None and len(artifact.content.encode()) > cfg.max_artifact_bytes:
            raise ValueError("Artifact too large")
        if self.llm_calls > cfg.llm_call_limit:
            raise RuntimeError("LLM call limit exceeded")

    def _persist(self, cfg: RunConfig, artifact: FloorArtifact) -> None:
        persist_base = cfg.persist_dir
        assert persist_base is not None
        path = persist_base / f"floor_{artifact.floor}"
        path.mkdir(parents=True, exist_ok=True)
        (path / f"rev_{artifact.revision}{artifact.ext}").write_text(artifact.content)

    def _log(self, log_path: Path, record: dict[str, Any]) -> None:
        """Append a JSON record with timestamp to the audit log."""
        record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        with log_path.open("a") as log_f:
            log_f.write(json.dumps(record) + "\n")

    def run(self, goal: str, cfg: RunConfig) -> Vote:
        """Execute the full NeuroDungeon protocol."""
        lives = cfg.lives
        self.lives = lives
        prev_hints: List[Hint] = []
        assert cfg.persist_dir is not None
        log_path = cfg.persist_dir / "log.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        for floor_index, enemies in enumerate(self.enemies_per_floor):
            self.llm_calls += 1
            artifact = self.player.act(floor_index, prev_hints)
            self._check_limits(cfg, artifact)
            self._persist(cfg, artifact)
            self.artifacts.append(artifact)

            votes: List[Vote] = []
            hints: List[Hint] = []
            for enemy_idx, enemy in enumerate(enemies):
                self.llm_calls += 1
                vote, enemy_hints = enemy.evaluate(artifact)
                self._log(
                    log_path,
                    {
                        "floor": floor_index,
                        "enemy_idx": enemy_idx,
                        "vote": vote.value,
                        "hints": [h.text for h in enemy_hints],
                    },
                )
                self._check_limits(cfg)
                votes.append(vote)
                hints.extend(enemy_hints)

            reject_count = votes.count(Vote.REJECT)
            if cfg.rejection_thresh == 0:
                threshold = math.ceil(len(enemies) * 0.5)
            else:
                threshold = cfg.rejection_thresh
            if reject_count >= threshold:
                lives -= 1
                self.lives = lives
                self._log(log_path, {"floor": floor_index, "life_lost": True})
                if lives <= 0:
                    return Vote.REJECT
            prev_hints = hints

        self.llm_calls += 1
        result = self.boss.judge(self.artifacts)
        self._check_limits(cfg)
        self.lives = lives
        self._log(log_path, {"boss_vote": result.value})
        return result
