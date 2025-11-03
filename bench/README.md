# Benchmarking Toolkit

- `python -m bench.loadgen`: fire concurrent simulated games against a backend and persist metrics.
- `python -m bench.publish_report`: turn telemetry and loadgen outputs into Plotly HTML dashboards.
- Log files live under `bench/logs/` (ignored from git).

Populate `bench/cases/` with deterministic board states for regression comparisons.
