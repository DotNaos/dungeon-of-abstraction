"""Data models for NeuroDungeon Protocol v0.1."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Optional


class Vote(enum.Enum):
    """Evaluation result for a floor or run."""

    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


@dataclass(frozen=True)
class Hint:
    """Short suggestion from an enemy critic."""

    text: str


@dataclass
class FloorArtifact:
    """Artifact produced at a floor."""

    floor: int
    revision: int
    content: str
    ext: str

    def path(self, run_id: str) -> Path:
        """Compute storage path for the artifact."""
        return Path(run_id) / f"floor_{self.floor}" / f"rev_{self.revision}{self.ext}"


@dataclass
class RunConfig:
    """Configuration for a NeuroDungeon run.

    ``persist_dir`` may be an absolute or relative path. The ``run_id`` is
    automatically nested inside it so multiple runs do not clobber each other.
    """

    run_id: str
    lives: int = 3
    rejection_thresh: int = 3
    llm_call_limit: int = 50
    max_artifact_bytes: int = 32 * 1024 * 1024
    persist_dir: Optional[Path] = None

    def __post_init__(self) -> None:
        if self.persist_dir is None:
            self.persist_dir = Path(self.run_id)
        else:
            self.persist_dir = Path(self.persist_dir) / self.run_id
