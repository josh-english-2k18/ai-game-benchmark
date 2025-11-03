"""Async load generator for AI Game Benchmark backends.

Usage:
    python -m bench.loadgen --backend gpu --games 50 --out bench/logs/run.csv
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import httpx
import numpy as np
from rich.console import Console
from rich.table import Table
from tenacity import retry, stop_after_attempt, wait_fixed

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "apps" / "server"))

from app.core.game import GameState  # type: ignore  # noqa: E402

console = Console()


@dataclass
class LoadgenResult:
    backend: str
    latency_ms: float
    move_index: int
    game_index: int
    fanout: float
    value: float


def choose_column(policy: List[float], state: GameState) -> int:
    legal = state.legal_moves()
    if not legal:
        raise ValueError("No legal moves available")
    scores = np.array([policy[idx] for idx in legal], dtype=np.float32)
    return legal[int(np.argmax(scores))]


@retry(wait=wait_fixed(1.0), stop=stop_after_attempt(3))
async def infer_once(client: httpx.AsyncClient, state: GameState, backend: str) -> dict:
    response = await client.post(
        "/infer",
        json={
            "board": state.board.tolist(),
            "current_player": state.current_player,
            "backend": backend,
        },
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


async def play_game(client: httpx.AsyncClient, backend: str, game_index: int, max_moves: int) -> List[LoadgenResult]:
    state = GameState()
    results: List[LoadgenResult] = []
    for move in range(max_moves):
        if not state.legal_moves():
            break
        payload = await infer_once(client, state, backend)
        column = choose_column(payload["policy"], state)
        state.drop_disc(column)
        results.append(
            LoadgenResult(
                backend=backend,
                latency_ms=float(payload["latency_ms"]),
                move_index=move,
                game_index=game_index,
                fanout=float(payload["extras"].get("fanout", 0.0)),
                value=float(payload.get("value", 0.0)),
            )
        )
        if state.winner() is not None:
            break
    return results


async def run_loadgen(backend: str, games: int, concurrency: int, max_moves: int, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        semaphore = asyncio.Semaphore(concurrency)

        async def wrapped_game(index: int) -> List[LoadgenResult]:
            async with semaphore:
                return await play_game(client, backend, index, max_moves)

        tasks = [asyncio.create_task(wrapped_game(i)) for i in range(games)]
        results_nested = await asyncio.gather(*tasks)

    results = [item for sublist in results_nested for item in sublist]

    if not results:
        console.print("[bold red]No results recorded. Was the server running?[/bold red]")
        return output

    import pandas as pd  # pylint: disable=import-outside-toplevel

    df = pd.DataFrame([r.__dict__ for r in results])
    df.to_csv(output, index=False)

    table = Table(title=f"Benchmark results for backend '{backend}'")
    table.add_column("Metric", justify="left", style="bold cyan")
    table.add_column("Value", justify="right", style="bold white")

    table.add_row("samples", f"{len(results):,}")
    table.add_row("p50 latency", f"{df.latency_ms.quantile(0.5):.2f} ms")
    table.add_row("p95 latency", f"{df.latency_ms.quantile(0.95):.2f} ms")
    table.add_row("avg latency", f"{df.latency_ms.mean():.2f} ms")
    table.add_row("avg fanout", f"{df.fanout.mean():.1f}")
    table.add_row("avg value", f"{df.value.mean():.3f}")

    console.print(table)
    return output


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Load generator for AI Game Benchmark")
    parser.add_argument("--backend", default="cpu", help="Backend key (cpu, gpu, tpu)")
    parser.add_argument("--games", type=int, default=20, help="Number of games to simulate")
    parser.add_argument("--concurrency", type=int, default=4, help="Concurrent games in flight")
    parser.add_argument("--max-moves", type=int, default=42, help="Max moves per game")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("bench/logs") / f"loadgen-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.csv",
        help="Output CSV path",
    )
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    console.print(
        f"[bold]Running loadgen[/bold] backend={args.backend} games={args.games} concurrency={args.concurrency}"
    )
    try:
        asyncio.run(run_loadgen(args.backend, args.games, args.concurrency, args.max_moves, args.out))
    except httpx.HTTPError as exc:
        console.print(f"[bold red]HTTP error during load generation: {exc}[/bold red]")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
