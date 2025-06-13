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


def render_report_html(run_id: str, artifacts: List[FloorArtifact], log_path: Path, llm_calls: int, lives_start: int) -> str:
    """Render an HTML report for browser display."""
    data = [json.loads(line) for line in log_path.read_text().splitlines()]
    floor_stats: List[FloorSummary] = []
    lives = lives_start
    for rec in data:
        if "floor" in rec and "enemy_idx" in rec:
            floor = rec["floor"]
            while len(floor_stats) <= floor:
                floor_stats.append(
                    FloorSummary(floor=len(floor_stats), accepts=0, rejects=0, lives=lives)
                )
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
        """<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>Run {{run_id}} Report</title>
  <style>
    table {border-collapse: collapse;}
    th, td {border: 1px solid #ccc; padding: 4px 8px;}
  </style>
</head>
<body>
  <h1>Run {{run_id}} Report</h1>
  <table>
    <tr><th>Floor</th><th>Accepts</th><th>Rejects</th><th>Lives</th></tr>
    {% for f in floors %}
    <tr><td>{{f.floor}}</td><td>{{f.accepts}}</td><td>{{f.rejects}}</td><td>{{f.lives}}</td></tr>
    {% endfor %}
  </table>
  <p>Boss vote: <strong>{{boss_vote}}</strong></p>
  <p>LLM calls: {{llm_calls}}</p>
  <h2>Artifacts</h2>
  <ul>
  {% for a in artifacts %}
    <li><a href="{{a.path(run_id)}}">floor {{a.floor}} rev {{a.revision}}</a></li>
  {% endfor %}
  </ul>
</body>
</html>"""
    )
    return tmpl.render(run_id=run_id, floors=floor_stats, boss_vote=boss_vote, llm_calls=llm_calls, artifacts=artifacts)
