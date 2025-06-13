from unittest import mock

import pytest

from neurodungeon.agents_llm import PlayerLLM, LintEnemyLLM
from neurodungeon.models import Hint, FloorArtifact, Vote
from neurodungeon.sandbox import Sandbox, docker_available, RuntimeEnemy


def test_player_llm(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    fake_resp = mock.Mock()
    fake_resp.choices = [mock.Mock(message=mock.Mock(content="artifact"))]
    fake_client = mock.Mock()
    fake_client.chat.completions.create.return_value = fake_resp
    monkeypatch.setattr("neurodungeon.agents_llm.OpenAI", lambda api_key=None: fake_client)
    player = PlayerLLM(goal="goal")
    art = player.act(0, [Hint(text="h")])
    assert art.content == "artifact"


def test_lint_enemy_llm(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    fake_resp = mock.Mock()
    fake_resp.choices = [mock.Mock(message=mock.Mock(content="ACCEPT\nhi"))]
    fake_client = mock.Mock()
    fake_client.chat.completions.create.return_value = fake_resp
    monkeypatch.setattr("neurodungeon.agents_llm.OpenAI", lambda api_key=None: fake_client)
    enemy = LintEnemyLLM()
    vote, hints = enemy.evaluate(FloorArtifact(0, 0, "code", ".py"))
    assert vote is Vote.ACCEPT
    assert hints[0].text == "hi"


@pytest.mark.docker
def test_sandbox_exec():
    if not docker_available():
        pytest.xfail("docker not available")
    sandbox = Sandbox(cpu=1, memory_mb=256, timeout_s=10)
    code = "def add(a, b):\n    return a + b\n"
    tests = "from code import add\n\ndef test_add():\n    assert add(1, 2) == 3\n"
    result = sandbox.run(code, tests)
    assert result.exit_code == 0 and not result.timed_out
    enemy = RuntimeEnemy(sandbox, tests)
    vote, _ = enemy.evaluate(FloorArtifact(0, 0, code, ".py"))
    assert vote is Vote.ACCEPT
