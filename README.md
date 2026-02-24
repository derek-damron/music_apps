# music_apps

AI-powered music applications: guitar practice sheets (PDF export), metronome, and wave sequencer (sound files from frequencies and durations).

## Setup

1. **Install [uv](https://docs.astral.sh/uv/)** (Python package manager).

2. **From repo root, install dependencies:**

   ```bash
   uv sync
   ```

   This creates a virtualenv (if needed) and installs all dependencies from `pyproject.toml` and `uv.lock`.

3. **Optional: API keys for AI apps**

   Copy `.env.example` to `.env` and set any keys your apps need (e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`). Never commit `.env`.

## Running apps

From the repo root:

- **Practice sheets:**  
  `uv run python -m apps.practice_sheets.main`  
  or `uv run music-practice-sheets --help`

- **Metronome:**  
  `uv run python -m apps.metronome.main --bpm 120`  
  or `uv run music-metronome --bpm 120`

- **Wave sequencer:**  
  `uv run python -m apps.wave_sequencer.main`  
  or `uv run music-wave-sequencer --help`

`uv run` uses the project virtualenv and dependencies automatically; you don’t need to activate the venv first.

## Project layout

- `apps/` — Applications: `practice_sheets`, `metronome`, `wave_sequencer`
- `lib/` — Shared code (e.g. `lib.config` for API keys and env)
- `infra/` — AWS deployment (SAM/CloudFormation) placeholder
- `scripts/` — Dev helpers placeholder

## Deploying to AWS

Use `infra/template.yaml` as a starting point. Build Lambda packages with deps from `uv.lock` (e.g. `uv export --no-dev -o requirements.txt` then install into the deployment package). For ECS, use a Dockerfile that runs `uv sync --frozen` and `uv run python -m apps.<name>.main` (or `serve`). API keys: use AWS Secrets Manager and set `AWS_SECRET_NAME_FOR_KEYS` (or inject env in the task/Lambda).
