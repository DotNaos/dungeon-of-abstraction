"""NeuroDungeon package entry point."""

from .models import Vote, Hint, FloorArtifact, RunConfig
from .agents import Player, Enemy, Boss
from .agents_llm import PlayerLLM, LintEnemyLLM
from .sandbox import Sandbox, RuntimeEnemy
from .config import load_config
from .report import render_report
from .orchestrator import Orchestrator
from .run import cli

__all__ = [
    "Vote",
    "Hint",
    "FloorArtifact",
    "RunConfig",
    "Player",
    "Enemy",
    "Boss",
    "PlayerLLM",
    "LintEnemyLLM",
    "Sandbox",
    "RuntimeEnemy",
    "load_config",
    "render_report",
    "Orchestrator",
    "cli",
]

try:
    from .agents_llm import PlayerLLM, LintEnemyLLM
except ModuleNotFoundError:
    # openai dependency is optional; avoid import error when extras are missing
    pass
else:
    __all__ += ["PlayerLLM", "LintEnemyLLM"]
