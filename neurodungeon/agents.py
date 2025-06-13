"""Agent base classes and simple stubs."""

from __future__ import annotations

import abc
from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

from .models import Hint, Vote, FloorArtifact


class Player(abc.ABC):
    """Abstract player generating floor artifacts."""

    @abc.abstractmethod
    def act(self, floor: int, hints: Sequence[Hint]) -> FloorArtifact:
        """Return artifact for given floor based on hints."""
        raise NotImplementedError


class Enemy(abc.ABC):
    """Abstract enemy critic."""

    @abc.abstractmethod
    def evaluate(self, artifact: FloorArtifact) -> Tuple[Vote, Sequence[Hint]]:
        """Evaluate artifact and provide hints."""
        raise NotImplementedError


class Boss(abc.ABC):
    """Final holistic critic."""

    @abc.abstractmethod
    def judge(self, artifacts: Sequence[FloorArtifact]) -> Vote:
        """Return final run vote given all artifacts."""
        raise NotImplementedError


class StubPlayer(Player):
    """Player stub that increments revision per floor."""

    def __init__(self) -> None:
        self._revs: Dict[int, int] = defaultdict(int)

    def act(self, floor: int, hints: Sequence[Hint]) -> FloorArtifact:
        rev = self._revs[floor]
        self._revs[floor] += 1
        content = f"artifact floor {floor} rev {rev} ({len(hints)} hints)"
        return FloorArtifact(floor=floor, revision=rev, content=content, ext=".txt")


class StubEnemy(Enemy):
    """Enemy stub that accepts on revision > 0."""

    def evaluate(self, artifact: FloorArtifact) -> Tuple[Vote, Sequence[Hint]]:
        if artifact.revision > 0:
            return Vote.ACCEPT, tuple()
        return Vote.REJECT, (Hint(text="improve"),)


class StubBoss(Boss):
    """Boss stub that always accepts."""

    def judge(self, artifacts: Sequence[FloorArtifact]) -> Vote:
        return Vote.ACCEPT
