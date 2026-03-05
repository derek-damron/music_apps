# Dev helpers

Placeholder for scripts such as run-all-tests, lint, or deploy helpers.

Suggested:
- `run_tests.sh` — run pytest across apps
- `lint.sh` — run ruff

## App entrypoints

Generate a daily planner PDF:

- `uv run python -m apps.daily_planner.main --output daily_planner.pdf`

If `--output` is omitted, the file `daily_planner.pdf` is written in the current directory.

