from __future__ import annotations

import time
from typing import Dict, List

import numpy as np

from .base import PolicyValueModel, softmax_masked
from ..core.game import COLS, GameState
from .cpu_adapter import HeuristicCpuModel


class SimulatedGpuModel(PolicyValueModel):
    name = "sim-gpu"

    def __init__(self, warmup_delay: float = 0.001) -> None:
        super().__init__(backend="gpu")
        self._cpu_delegate = HeuristicCpuModel()
        self._warmup_delay = warmup_delay
        self._invocations = 0

    def load(self) -> None:
        # Emulate CUDA context spin-up cost just once.
        time.sleep(self._warmup_delay)

    def _infer_impl(self, game: GameState) -> tuple[List[float], float, Dict[str, float]]:
        self._invocations += 1
        # Simulate kernel execution latency trending lower after warmup.
        time.sleep(0.008 + np.random.random() * 0.004)
        base = self._cpu_delegate._infer_impl(game)  # pylint: disable=protected-access
        policy, value, extras = base
        jitter = np.random.default_rng().normal(0, 0.005, size=len(policy))
        policy = softmax_masked(np.array(policy) + jitter, range(COLS))
        extras = {
            **extras,
            "gpu_warm": float(self._invocations > 1),
            "simulated_power_w": 70.0 + 5.0 * np.random.random(),
        }
        return policy, value, extras


__all__ = ["SimulatedGpuModel"]
