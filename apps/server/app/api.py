from __future__ import annotations

import asyncio
from typing import Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .config import settings
from .core.game import COLS, ROWS, GameState
from .core.registry import registry
from .telemetry.metrics import MetricsStore, SubscriberSet

app = FastAPI(default_response_class=JSONResponse, title="AI Game Benchmark API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

metrics_store = MetricsStore(max_records=settings.metrics_window, log_path=settings.telemetry_log_path)
subscribers = SubscriberSet()


class InferRequest(BaseModel):
    board: List[List[int]] = Field(..., description="6x7 board with -1, 0, 1 values")
    current_player: Literal[-1, 1] = Field(1, description="Player to move (1 or -1)")
    backend: Optional[str] = Field(None, description="cpu | gpu | tpu")

    def to_game(self) -> GameState:
        return GameState.from_list(self.board, self.current_player)


class InferResponse(BaseModel):
    backend: str
    model: str
    policy: List[float]
    value: float
    latency_ms: float
    extras: Dict[str, float]


class BackendInfo(BaseModel):
    key: str
    name: str


class MetricStats(BaseModel):
    p50: float
    p95: float
    avg: float
    count: float


class SummaryBuckets(BaseModel):
    latency_ms: MetricStats
    value: MetricStats
    fanout: MetricStats


class MetricsSummaryResponse(BaseModel):
    overall: SummaryBuckets
    by_backend: Dict[str, SummaryBuckets]


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/backends", response_model=List[BackendInfo])
async def available_backends() -> List[BackendInfo]:
    return [BackendInfo(key=key, name=name) for key, name in registry.available().items()]


@app.post("/infer", response_model=InferResponse)
async def infer(request: InferRequest) -> InferResponse:
    backend_key = (request.backend or settings.default_backend).lower()
    try:
        model = registry.get(backend_key)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    game = request.to_game()
    if len(game.board) != ROWS or len(game.board[0]) != COLS:
        raise HTTPException(status_code=400, detail="Board must be 6x7")
    if not game.legal_moves():
        raise HTTPException(status_code=400, detail="No legal moves available")

    result = model.infer(game)
    record = {
        "backend": result.backend,
        "latency_ms": result.latency_ms,
        "value": result.value,
        **result.extras,
    }
    metrics_store.add(record)
    await subscribers.broadcast({"type": "telemetry", "record": record})

    return InferResponse(
        backend=result.backend,
        model=result.model,
        policy=result.policy,
        value=result.value,
        latency_ms=result.latency_ms,
        extras=result.extras,
    )


@app.get("/metrics/summary", response_model=MetricsSummaryResponse)
async def metrics_summary() -> MetricsSummaryResponse:
    data = metrics_store.summarize_all()
    return MetricsSummaryResponse.model_validate(data)


@app.websocket("/ws/telemetry")
async def telemetry_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    await subscribers.register(websocket)
    try:
        while True:
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        await subscribers.unregister(websocket)
