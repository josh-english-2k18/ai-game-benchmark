from __future__ import annotations

import json
import threading
import time
from collections import deque
from pathlib import Path
from statistics import mean
from typing import Deque, Dict, Iterable, List

import numpy as np
from loguru import logger

DEFAULT_MAX_RECORDS = 512


class MetricsStore:
    """Thread-safe sliding window telemetry store with percentile helpers."""

    def __init__(self, max_records: int = DEFAULT_MAX_RECORDS, log_path: Path | None = None) -> None:
        self._max_records = max_records
        self._records: Deque[Dict] = deque(maxlen=max_records)
        self._lock = threading.Lock()
        self._log_path = log_path
        if log_path:
            log_path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, record: Dict) -> None:
        ts = time.time()
        record = {**record, "ts": ts}
        with self._lock:
            self._records.append(record)
        if self._log_path:
            try:
                with self._log_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(record) + "\n")
            except Exception as exc:  # pragma: no cover
                logger.warning("Failed to persist telemetry record: {}", exc)

    def snapshot(self) -> List[Dict]:
        with self._lock:
            return list(self._records)

    def summarize(self, metric: str, records: List[Dict] | None = None) -> Dict[str, float]:
        source = records if records is not None else self.snapshot()
        data = [rec[metric] for rec in source if metric in rec]
        if not data:
            return {"p50": 0.0, "p95": 0.0, "avg": 0.0, "count": 0.0}
        arr = np.array(data, dtype=np.float32)
        return {
            "p50": float(np.percentile(arr, 50)),
            "p95": float(np.percentile(arr, 95)),
            "avg": float(mean(arr)),
            "count": float(len(arr)),
        }

    def summarize_all(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        metrics = ["latency_ms", "value", "fanout"]
        snapshot = self.snapshot()
        overall = {metric: self.summarize(metric, snapshot) for metric in metrics}
        by_backend: Dict[str, Dict[str, float]] = {}
        for backend in {rec["backend"] for rec in snapshot if "backend" in rec}:
            backend_records = [rec for rec in snapshot if rec.get("backend") == backend]
            by_backend[backend] = {
                metric: self.summarize(metric, backend_records) for metric in metrics
            }
        return {"overall": overall, "by_backend": by_backend}


class SubscriberSet:
    """Maintains connected websocket subscribers."""

    def __init__(self) -> None:
        self._subs: set = set()
        self._lock = threading.Lock()

    async def register(self, websocket) -> None:
        with self._lock:
            self._subs.add(websocket)

    async def unregister(self, websocket) -> None:
        with self._lock:
            self._subs.discard(websocket)

    async def broadcast(self, payload: Dict) -> None:
        with self._lock:
            subscribers = list(self._subs)
        for ws in subscribers:
            try:
                await ws.send_json(payload)
            except Exception:
                await self.unregister(ws)


def window_percentiles(records: Iterable[Dict], metric: str, percentiles: Iterable[int]) -> Dict[str, float]:
    values = [rec[metric] for rec in records if metric in rec]
    if not values:
        return {f"p{p}": 0.0 for p in percentiles}
    arr = np.array(values, dtype=np.float32)
    return {f"p{p}": float(np.percentile(arr, p)) for p in percentiles}
