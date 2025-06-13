"""Generate a Markdown report summarizing a NeuroDungeon run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from pydantic import ConfigDict

from jinja2 import Template

from .models import NDModel, FloorArtifact


class FloorSummary(NDModel):
    model_config = ConfigDict()
    floor: int
    accepts: int
    rejects: int
    lives: int


def render_report(run_id: str, artifacts: List[FloorArtifact], log_path: Path, llm_calls: int, lives_start: int) -> str:
    data = [json.loads(line) for line in log_path.read_text().splitlines()]
    floor_stats: List[FloorSummary] = []
    lives = lives_start
    for rec in data:
        if "floor" in rec and "enemy_idx" in rec:
            floor = rec["floor"]
            while len(floor_stats) <= floor:
                floor_stats.append(FloorSummary(floor=len(floor_stats), accepts=0, rejects=0, lives=lives))
            if rec["vote"] == "REJECT":
                floor_stats[floor].rejects += 1
            else:
                floor_stats[floor].accepts += 1
        if "life_lost" in rec:
            lives -= 1
            if rec["floor"] < len(floor_stats):
                floor_stats[rec["floor"].__int__()].lives = lives
    boss_vote = next((rec["boss_vote"] for rec in data if "boss_vote" in rec), "?")

    tmpl = Template(
        """# Run {{run_id}} Report

| Floor | Accepts | Rejects | Lives |
|-------|---------|---------|-------|
{% for f in floors %}| {{f.floor}} | {{f.accepts}} | {{f.rejects}} | {{f.lives}} |
{% endfor %}

Boss vote: **{{boss_vote}}**  
LLM calls: {{llm_calls}}

## Artifacts
{% for a in artifacts %}- [floor {{a.floor}} rev {{a.revision}}]({{a.path(run_id)}})
{% endfor %}
"""
    )
    return tmpl.render(run_id=run_id, floors=floor_stats, boss_vote=boss_vote, llm_calls=llm_calls, artifacts=artifacts)
