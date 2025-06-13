from __future__ import annotations

"""Helpers for migrating data from NeuroDungeon 0.2 dataclasses."""

from dataclasses import asdict
import warnings
from typing import Any

from . import dataclasses as dc
from .models import FloorArtifact, Hint, RunConfig
from .sandbox import SandboxResult
from .report import FloorSummary

_warned = False


def v02_to_v03(obj: Any) -> object:
    """Convert a legacy dataclass instance to the equivalent Pydantic model."""
    global _warned
    if not _warned:
        warnings.warn(
            "v02_to_v03() is deprecated and will be removed in 0.4",
            DeprecationWarning,
            stacklevel=2,
        )
        _warned = True

    if isinstance(obj, dc.Hint):
        return Hint(**asdict(obj))
    if isinstance(obj, dc.FloorArtifact):
        return FloorArtifact(**asdict(obj))
    if isinstance(obj, dc.RunConfig):
        return RunConfig(**asdict(obj))
    if isinstance(obj, dc.SandboxResult):
        return SandboxResult(**asdict(obj))
    if isinstance(obj, dc.FloorSummary):
        return FloorSummary(**asdict(obj))
    raise TypeError(f"Unsupported type: {type(obj)!r}")

__all__ = ["v02_to_v03"]
