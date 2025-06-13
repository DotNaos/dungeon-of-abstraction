"""LLM-powered agents using OpenAI chat completions."""

from __future__ import annotations

import os
from collections import defaultdict
from typing import Sequence, Tuple

from openai import OpenAI

from .models import FloorArtifact, Hint, Vote
from .agents import Player, Enemy


class PlayerLLM(Player):
    """Player that delegates artifact creation to an LLM."""

    def __init__(self, goal: str, model: str | None = None) -> None:
        self.goal = goal
        self.model: str = model or os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo"
        self._revs: dict[int, int] = defaultdict(int)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def act(self, floor: int, hints: Sequence[Hint]) -> FloorArtifact:
        hint_text = "\n".join(h.text for h in hints)
        prompt = (
            f"Goal: {self.goal}\n"
            f"Floor: {floor}\n"
            f"Hints:\n{hint_text}\n"
            "Provide the artifact content only."
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        content = resp.choices[0].message.content or ""
        rev = self._revs[floor]
        self._revs[floor] += 1
        return FloorArtifact(floor=floor, revision=rev, content=content, ext=".txt")


class LintEnemyLLM(Enemy):
    """Enemy that asks the LLM to lint code."""

    def __init__(self, model: str | None = None) -> None:
        self.model: str = model or os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo"
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def evaluate(self, artifact: FloorArtifact) -> Tuple[Vote, Sequence[Hint]]:
        prompt = (
            "You are a code reviewer. "
            "Return ACCEPT or REJECT on the first line followed by up to 3 hints.\n" 
            "Focus on style or bugs.\n"
            f"Code:\n{artifact.content}"
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        text = (resp.choices[0].message.content or "").strip().splitlines()
        vote_line = text[0].upper()
        vote = Vote.ACCEPT if "ACCEPT" in vote_line else Vote.REJECT
        hints = [Hint(text=line) for line in text[1:4]]
        return vote, tuple(hints)
