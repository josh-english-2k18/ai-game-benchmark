"""Generate interactive HTML reports from telemetry and loadgen outputs."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from rich.console import Console

console = Console()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Publish HTML telemetry report")
    parser.add_argument("--telemetry", type=Path, default=Path("bench/logs/telemetry.ndjson"), help="Telemetry NDJSON path")
    parser.add_argument("--loadgen", type=Path, help="Optional loadgen CSV path")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("bench/logs") / f"report-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.html",
        help="Output HTML path",
    )
    return parser


def read_telemetry(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Telemetry file not found: {path}")
    df = pd.read_json(path, lines=True)
    df["ts"] = pd.to_datetime(df.ts, unit="s")
    return df


def build_report(telemetry: pd.DataFrame, loadgen: pd.DataFrame | None) -> go.Figure:
    fig = go.Figure()

    for backend, group in telemetry.groupby("backend"):
        fig.add_trace(
            go.Scatter(
                x=group["ts"],
                y=group["latency_ms"],
                mode="lines+markers",
                name=f"Latency ({backend})",
                hovertemplate="Backend=%{text}<br>Latency=%{y:.2f} ms<extra></extra>",
                text=[backend] * len(group),
            )
        )

    fig.update_layout(
        title="Latency Over Time",
        xaxis_title="Timestamp",
        yaxis_title="Latency (ms)",
        template="plotly_dark",
        legend_orientation="h",
    )

    if loadgen is not None and not loadgen.empty:
        hist = px.histogram(loadgen, x="latency_ms", color="backend", nbins=40, template="plotly_dark")
        hist.update_layout(title="Latency Distribution (Loadgen)")
        for trace in hist.data:
            fig.add_trace(trace)

    return fig


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    telemetry_df = read_telemetry(args.telemetry)
    loadgen_df = pd.read_csv(args.loadgen) if args.loadgen and args.loadgen.exists() else None
    fig = build_report(telemetry_df, loadgen_df)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(args.out)
    console.print(f"[bold green]Report generated:[/bold green] {args.out}")


if __name__ == "__main__":
    main()
