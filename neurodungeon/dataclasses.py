from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


_DEF_MSG = (
    "Dataclass-based models are deprecated and will be removed in neurodungeon 0.4. "
    "Use pydantic models from neurodungeon.models instead."
)

_warned: set[str] = set()


def _warn(name: str) -> None:
    if name not in _warned:
        warnings.warn(
            f"{name} dataclass is deprecated; use neurodungeon.models.{name}",
            DeprecationWarning,
            stacklevel=2,
        )
        _warned.add(name)


@dataclass
class Hint:
    text: str

    def __post_init__(self) -> None:
        _warn("Hint")


@dataclass
class FloorArtifact:
    floor: int
    revision: int
    content: str
    ext: str

    def path(self, run_id: str) -> Path:
        return Path(run_id) / f"floor_{self.floor}" / f"rev_{self.revision}{self.ext}"

    def __post_init__(self) -> None:
        _warn("FloorArtifact")


@dataclass
class RunConfig:
    run_id: str
    lives: int = 3
    rejection_thresh: int = 3
    llm_call_limit: int = 50
    max_artifact_bytes: int = 32 * 1024 * 1024
    persist_dir: Optional[Path] = None
    sandbox_cpu: float = 1.0
    sandbox_memory_mb: int = 256
    sandbox_timeout_s: int = 10

    def __post_init__(self) -> None:
        if self.persist_dir is None:
            self.persist_dir = Path(self.run_id)
        else:
            self.persist_dir = Path(self.persist_dir) / self.run_id
        _warn("RunConfig")


@dataclass
class SandboxResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool

    def __post_init__(self) -> None:
        _warn("SandboxResult")


@dataclass
class FloorSummary:
    floor: int
    accepts: int
    rejects: int
    lives: int

    def __post_init__(self) -> None:
        _warn("FloorSummary")


__all__ = [
    "Hint",
    "FloorArtifact",
    "RunConfig",
    "SandboxResult",
    "FloorSummary",
]
