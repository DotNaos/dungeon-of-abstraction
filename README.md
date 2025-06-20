# NeuroDungeon

`neurodungeon` is a reference implementation of the NeuroDungeon Protocol v0.2.

## Installation

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # once per machine
uv sync --all-extras --dev              # creates .venv/ and installs all dependencies
```

`jinja2` is installed by default so report generation works out of the box.

Optional dependencies:

| Extra | Description |
|-------|-------------|
| `dev` | Tools for testing and type checking |
| `llm` | OpenAI client for LLM-powered agents |

## Usage

Run the demo script:

```bash
python demo_neurodungeon.py
```

You can also invoke the CLI directly and choose where artifacts are stored:

```bash
uv run neurodungeon --goal "build a web app" --persist-dir runs --enemies 2
```
After the run completes the CLI prints

```
Run cli_run complete — log: /abs/path/to/runs/cli_run/log.jsonl
```
with the absolute path to the `log.jsonl` file for easy inspection.

### Running with real LLMs

Install the dev tools and the `llm` extra (which pulls in the OpenAI client)
then set `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`):

```bash
uv sync --all-extras --dev
export OPENAI_API_KEY=sk-...
uv run neurodungeon --goal "build a web app" --persist-dir runs --config dungeon.yml
```

The LLM-backed agents will use these credentials to generate artifacts.

### Dungeon config

Provide a YAML file to control lives and floors:

```yaml
lives: 3
llm_call_limit: 20
floors: [1, 2]
```

Invoke with `--config dungeon.yml` to override CLI flags. See
`examples/basic.yml` for a ready-to-use template.

## Extending

Implement custom `Player`, `Enemy`, and `Boss` agents and create an
`Orchestrator` with a nested list of enemies per floor:

```python
enemies_per_floor = [[Enemy1(), Enemy2()], [Enemy3()], ...]
orch = Orchestrator(player, enemies_per_floor, boss)
result = orch.run("build a web app", RunConfig(run_id="my_run"))
```

Pydantic models provide convenient JSON helpers:

```python
data = cfg.model_dump_json()
cfg2 = RunConfig.model_validate_json(data)
assert cfg == cfg2
```

The orchestrator compares the number of rejections on a floor against a
threshold. If ``rejection_thresh`` is greater than ``0`` that value is used
directly. Passing ``rejection_thresh=0`` enables the dynamic rule
``ceil(E * 0.5)`` where ``E`` is the number of enemies on the floor.
If the threshold is met, one life is lost. Hints gathered on each floor are always passed to
the next `Player.act()` call, even if the floor was accepted. The
`llm_call_limit` is inclusive, so a value of `50` allows exactly 50
calls. Only one attempt is made per floor. `persist_dir` may be an
absolute path—in all cases the `run_id` is nested inside it.

### Design Rationale

Limiting to a single attempt per floor keeps the number of LLM calls and
token usage predictable, which is critical when runs are chained or
budgeted.

## Upgrading from 0.2

Version 0.3 replaces the dataclass-based models with Pydantic models. The
legacy dataclasses remain available under ``neurodungeon.dataclasses`` and
emit ``DeprecationWarning`` on use. Convert existing objects with
``neurodungeon.migrate.v02_to_v03``.

### Building a wheel

To create a distributable wheel for local testing:

```bash
python -m build
```
