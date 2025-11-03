from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Sequence

import numpy as np

from ..core.game import GameState


@dataclass
class InferenceResult:
    policy: List[float]
    value: float
    latency_ms: float
    backend: str
    model: str
    extras: Dict[str, float]


class PolicyValueModel(ABC):
    name: str = "base"

    def __init__(self, backend: str) -> None:
        self.backend = backend
        self.loaded = False

    def ensure_loaded(self) -> None:
        if not self.loaded:
            self.load()
            self.loaded = True

    @abstractmethod
    def load(self) -> None:
        ...

    def infer(self, game: GameState) -> InferenceResult:
        self.ensure_loaded()
        start = time.perf_counter()
        policy, value, extras = self._infer_impl(game)
        latency_ms = (time.perf_counter() - start) * 1000.0
        return InferenceResult(
            policy=policy, value=value, latency_ms=latency_ms, backend=self.backend, model=self.name, extras=extras
        )

    @abstractmethod
    def _infer_impl(self, game: GameState) -> tuple[List[float], float, Dict[str, float]]:
        ...


def softmax_masked(logits: Sequence[float], legal_moves: Sequence[int]) -> List[float]:
    mask = np.full(len(logits), -np.inf, dtype=np.float32)
    mask[list(legal_moves)] = np.array([logits[i] for i in legal_moves], dtype=np.float32)
    max_logit = np.max(mask)
    exp = np.exp(mask - max_logit)
    exp[np.isinf(mask)] = 0.0
    denom = np.sum(exp)
    if denom == 0:
        return [1.0 / len(legal_moves) if i in legal_moves else 0.0 for i in range(len(logits))]
    probs = exp / denom
    return probs.tolist()
