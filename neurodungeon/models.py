"""Data models for NeuroDungeon Protocol v0.1."""

from __future__ import annotations

import enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


from typing import Any


class NDModel(BaseModel):
    """Base model with JSON dump helper."""

    def model_dump_json(self, *args: Any, **kwargs: Any) -> str:
        kwargs.setdefault("indent", 2)
        return super().model_dump_json(*args, **kwargs)


class Vote(enum.Enum):
    """Evaluation result for a floor or run."""

    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


class Hint(NDModel):
    """Short suggestion from an enemy critic."""

    model_config = ConfigDict(frozen=True)

    text: str


class FloorArtifact(NDModel):
    """Artifact produced at a floor."""

    model_config = ConfigDict(frozen=True)

    floor: int
    revision: int
    content: str
    ext: str

    @field_validator("floor", "revision")
    @classmethod
    def _non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("must be >= 0")
        return v

    @field_validator("ext")
    @classmethod
    def _validate_ext(cls, v: str) -> str:
        if not v.startswith(".") or len(v) > 8:
            raise ValueError("ext must start with '.' and be <= 8 chars")
        return v

    def path(self, run_id: str) -> Path:
        """Compute storage path for the artifact."""
        return Path(run_id) / f"floor_{self.floor}" / f"rev_{self.revision}{self.ext}"


class RunConfig(NDModel):
    """Configuration for a NeuroDungeon run.

    ``persist_dir`` may be an absolute or relative path. The ``run_id`` is
    automatically nested inside it so multiple runs do not clobber each other.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    run_id: str
    lives: int = 3
    rejection_thresh: int = 3
    llm_call_limit: int = 50
    max_artifact_bytes: int = 32 * 1024 * 1024
    persist_dir: Optional[Path] = None
    sandbox_cpu: float = 1.0
    sandbox_memory_mb: int = 256
    sandbox_timeout_s: int = 10

    @model_validator(mode="after")
    def _set_persist_dir(self) -> "RunConfig":
        pd = Path(self.run_id) if self.persist_dir is None else Path(self.persist_dir)
        if pd.name != self.run_id:
            pd = pd / self.run_id
        object.__setattr__(self, "persist_dir", pd)
        pd.mkdir(parents=True, exist_ok=True)
        return self

    @field_validator("lives", "llm_call_limit", "sandbox_memory_mb", "sandbox_timeout_s")
    @classmethod
    def _positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("must be > 0")
        return v
