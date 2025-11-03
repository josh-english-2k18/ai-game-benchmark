# AI Game Benchmark – Working Plan

## Project Thesis
- Deliver a gorgeous, player-facing Connect Four benchmark that demonstrates how CPU, GPU, and TPU inference feel different in practice.
- Keep the stack light and reproducible so new contributors can clone, run, and extend without wrestling complex infra.

## What’s Live Today
- **Frontend (`apps/web/`)**: Vite + React + Tailwind UI with animated board, backend toggle, think meter, telemetry HUD, and on-demand hint shimmer. React Query powers API calls; a websocket stream drives live metrics.
- **Backend (`apps/server/`)**: FastAPI service with a unified `PolicyValueModel` interface, simulated CPU/GPU/TPU adapters, Connect Four rules/encoding, latency instrumentation, and websocket broadcasting. Metrics persist to `bench/logs/telemetry.ndjson`.
- **Testing**: Vitest smoke test for the UI container; pytest coverage for health checks, inference flow, game logic, and metrics summaries. CI-ready commands documented in README.
- **Tooling**: Async load generator (`python -m bench.loadgen`) that writes CSVs and prints percentile tables, plus Plotly report generator (`bench/publish_report.py`) for HTML dashboards. Dockerfiles (CPU/GPU) and Terraform stub ready for deployment work.
- **Docs**: Updated README quickstart, contributor guide (`AGENTS.md`), models README placeholder, benchmarking README.

## Architecture Snapshot
### Frontend (Vite/React)
- Animated Connect Four board (`GameBoard`) with framer-motion effects and backend-aware styling.
- Think meter + telemetry panel components consuming REST + websocket data.
- Telemetry hook reconnects automatically; fetch utilities bubble errors via React Query.

### Backend (FastAPI)
- Router exposes `/health`, `/backends`, `/infer`, `/metrics/summary`, and `/ws/telemetry`.
- Metrics store keeps sliding-window stats, writes NDJSON logs, and pushes summary buckets (overall + per-backend) to clients.
- Simulated backends emulate realistic latency/power profiles using heuristic evaluation; registry ensures singleton lifecycle.

### Benchmark & Reporting
- `bench/loadgen.py` reuses server game logic for deterministic move selection and supports concurrency controls.
- `bench/publish_report.py` ingests telemetry + loadgen artifacts and emits Plotly charts (latency over time + histograms).
- Bench logs ignored from git but folder scaffolded for consistent output.

## Dev Experience & Commands
- Backend: `cd apps/server && source .venv/bin/activate && uvicorn app.api:app --reload --host 127.0.0.1 --port 8000`
- Frontend: `cd apps/web && npm run dev` (proxy routes `/api` + `/ws` to backend).
- Tests: `pytest` in activated virtualenv; `npm run test -- --run` for UI.
- Bench: `source .venv/bin/activate && python -m bench.loadgen --backend gpu --games 20` then `python -m bench.publish_report --telemetry bench/logs/telemetry.ndjson --loadgen <csv>`.

## Near-Term Enhancements
1. Swap simulated adapters for real ONNX/JAX/TFLite backends once models are ready; document hardware requirements.
2. Add power sampling integrations (RAPL, `nvidia-smi`, TPU metrics) and fold into telemetry extras.
3. Introduce WebSocket auth / rate limits before public deployment; formalize config via `.env`.
4. Expand frontend tests (e.g., state reducers, telemetry rendering) and add visual regression screenshots.
5. Harden deployment story: docker-compose for local CPU/GPU, Terraform module for TPU, and optional k8s manifest.

## Stretch Goals (when bandwidth allows)
- WebGPU client-side comparison mode.
- Quantization toggle and accuracy deltas.
- Automated split-screen capture pipeline for marketing assets.
- “Honesty chart” auto-generator in README from telemetry summaries.
