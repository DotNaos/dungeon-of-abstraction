# Changelog

## v0.1 - 2025-06-13
- Initial release implementing NeuroDungeon Protocol v0.1
- Refined orchestrator API and improved tests
- Added property-based tests
- Added audit-log JSONL with ISO-8601 ``timestamp`` field
- CLI prints absolute log path on completion
- Dynamic ``ceil(E * 0.5)`` threshold when ``rejection_thresh`` is ``0``
- Documented inclusive ``llm_call_limit`` and wheel building
- Added basic GitHub Actions workflow

## v0.2 - 2025-06-13
- Bumped project version to **0.2.0**
- LLM-backed player and lint enemy via OpenAI
- Docker-based sandbox and runtime enemy
- YAML dungeon configuration with `--config` flag
- Markdown report generation stored next to each run
- Optional extras reorganised (`llm` includes PyYAML & Jinja2)
- CI installs docker-cli and sets `DOCKER_HOST` for sandbox tests

## v0.2-rc1 - 2025-06-13
- Move `jinja2` to core dependency so reports work without extras
- Added `examples/basic.yml` configuration sample
- Added MIT `LICENSE`
- Report file now tested for creation
- Docker job uses `docker info` instead of installing the CLI
- CI compiles sources to catch stray `__pycache__` files
