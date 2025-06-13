from __future__ import annotations

import os
import time
from pathlib import Path

from flask import Flask, request, render_template_string

from .agents import StubBoss, StubEnemy, StubPlayer
from .agents_llm import PlayerLLM, LintEnemyLLM
from .models import RunConfig
from .orchestrator import Orchestrator
from .report import render_report_html

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        goal = request.form.get('goal', 'build a web app')
        enemies_count = int(request.form.get('enemies', 2))
        run_id = f"web_{int(time.time())}"
        cfg = RunConfig(run_id=run_id, persist_dir=Path('runs'))
        use_llm = bool(os.getenv('OPENAI_API_KEY'))
        enemies = [
            [LintEnemyLLM() if use_llm else StubEnemy()]
            for _ in range(enemies_count)
        ]
        player = PlayerLLM(goal) if use_llm else StubPlayer()
        orch = Orchestrator(player, enemies, StubBoss())
        orch.run(goal, cfg)
        log_path = cfg.persist_dir / 'log.jsonl'
        report_html = render_report_html(
            cfg.run_id, orch.artifacts, log_path, orch.llm_calls, cfg.lives
        )
        (cfg.persist_dir / 'report.html').write_text(report_html)
        return render_template_string(report_html)
    return '''
    <form method="post">
      Goal: <input name="goal" size="40" placeholder="build something"><br>
      Enemies: <input name="enemies" type="number" value="2"><br>
      <input type="submit" value="Run">
    </form>
    '''


def main() -> None:
    app.run(debug=True)


if __name__ == '__main__':
    main()
