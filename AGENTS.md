# Repository Guidelines

## Project Structure & Module Organization
- `apps/web/`: Vite + React front end with Connect Four UI, backend selector, and telemetry HUD. Reuse shared hooks from `apps/web/src/lib`.
- `apps/server/`: FastAPI inference service, including the router (`api.py`) and backend adapters under `apps/server/adapters/`.
- `models/`: Placeholder for ONNX/Flax/TFLite weights; store large binaries with Git LFS.
- `bench/`: Async load generator, telemetry report tooling, and regression game cases.
- `deploy/`: Dockerfiles (CPU, GPU) and cloud/terraform assets for TPU provisioning.

## Build, Test, and Development Commands
- `cd apps/web && npm install && npm run dev`: install client deps and launch the local web UI at `http://localhost:3000`.
- `cd apps/server && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.api:app --reload`: run the FastAPI server locally.
- `source apps/server/.venv/bin/activate && python -m bench.loadgen --backend gpu --games 50`: generate load + CSV/NDJSON telemetry.
- `docker build -f deploy/docker/GPU.Dockerfile -t ai-game-benchmark-gpu .`: build CUDA-enabled image; requires `nvidia-docker` runtime.

## Coding Style & Naming Conventions
- TypeScript/React: 2-space indentation, prefer function components, camelCase for vars, PascalCase for components, kebab-case for filenames.
- Python: follow `black` (line length 88) and `isort` import grouping; snake_case modules/functions, UpperCamelCase classes.
- Keep adapters named `<backend>_adapter.py` and expose a `PolicyValueModel` subclass; export registries via `__all__`.
- Run `npm run lint`, `npm run test`, and `ruff check apps/server` before sending PRs; ensure loadgen/report docs stay synced.

## Testing Guidelines
- Front end: `npm run test -- --run` executes Vitest + React Testing Library suites; mock network calls as needed.
- Backend: `source apps/server/.venv/bin/activate && pytest` runs FastAPI + game model tests; add fixtures to `tests/conftest.py` when extending coverage.
- Maintain regression games in `bench/cases/`; loadgen runs should stay within 5% latency regression versus main.

## Commit & Pull Request Guidelines
- Commits follow `<area>: <imperative>` (e.g., `server: add gpu adapter metrics`). Keep history focused and rebase before pushing.
- PRs need: summary of behavior change, linked issue (if any), test evidence (`pytest`, `npm run test`, loadgen snippet), and updated docs when interfaces shift.
- Include screenshots or GIFs for visible HUD changes and attach benchmark diffs when latency or throughput shifts by >5%.
