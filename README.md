# NeuroDungeon

`neurodungeon` is a reference implementation of the NeuroDungeon Protocol v0.1.

## Installation

```bash
pip install -e .
```

## Usage

Run the demo script:

```bash
python demo_neurodungeon.py
```

You can also invoke the stubbed CLI directly and choose where artifacts are stored:

```bash
neurodungeon --goal "build a web app" --persist-dir runs
```
After the run completes, the CLI prints the run ID and the path to the generated
`log.jsonl` file for easy inspection.

## Extending

Implement custom `Player`, `Enemy`, and `Boss` agents and create an
`Orchestrator` with a nested list of enemies per floor:

```python
enemies_per_floor = [[Enemy1(), Enemy2()], [Enemy3()], ...]
orch = Orchestrator(player, enemies_per_floor, boss)
result = orch.run("build a web app", RunConfig(run_id="my_run"))
```

The orchestrator compares the number of rejections on a floor against
`max(rejection_thresh, ceil(len(enemies) * 0.5))`. Set
`rejection_thresh` to `0` to use the default `ceil(E * 0.5)` value.
If the threshold is met, one life is lost. Hints gathered on each floor are always passed to
the next `Player.act()` call, even if the floor was accepted. The
`llm_call_limit` is inclusive, so a value of `50` allows exactly 50
calls. Only one attempt is made per floor. `persist_dir` may be an
absolute path—in all cases the `run_id` is nested inside it.

### Design Rationale

Limiting to a single attempt per floor keeps the number of LLM calls and
token usage predictable, which is critical when runs are chained or
budgeted.

### Building a wheel

To create a distributable wheel for local testing:

```bash
python -m build
```
