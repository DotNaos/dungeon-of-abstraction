"""NeuroDungeon package entry point."""

__version__ = "0.3.0.dev0"

from .models import Vote, Hint, FloorArtifact, RunConfig
from . import dataclasses as dataclasses
from .migrate import v02_to_v03
from .agents import Player, Enemy, Boss
from .sandbox import Sandbox, RuntimeEnemy
from .config import load_config
from .report import render_report, render_report_html
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
    "Sandbox",
    "RuntimeEnemy",
    "load_config",
    "render_report",
    "render_report_html",
    "Orchestrator",
    "cli",
    "dataclasses",
    "v02_to_v03",
]

try:
    from .agents_llm import PlayerLLM, LintEnemyLLM
except ModuleNotFoundError:
    # openai dependency is optional; avoid import error when extras are missing
    pass
else:
    __all__ += ["PlayerLLM", "LintEnemyLLM"]
