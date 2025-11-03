from __future__ import annotations

import time
from typing import Dict, List

import numpy as np

from .base import PolicyValueModel, softmax_masked
from ..core.game import COLS, GameState
from .cpu_adapter import HeuristicCpuModel


class SimulatedTpuModel(PolicyValueModel):
    name = "sim-tpu"

    def __init__(self, batch_size: int = 1) -> None:
        super().__init__(backend="tpu")
        self._delegate = HeuristicCpuModel()
        self._batch_size = batch_size

    def load(self) -> None:
        # TPU compilation emulator.
        time.sleep(0.05)

    def _infer_impl(self, game: GameState) -> tuple[List[float], float, Dict[str, float]]:
        # Pretend to batch by repeating state and averaging.
        time.sleep(0.015 + np.random.random() * 0.005)
        legal = game.legal_moves()
        base_policy = np.zeros(COLS, dtype=np.float32)
        base_value = 0.0
        for _ in range(max(1, self._batch_size)):
            policy, value, extras = self._delegate._infer_impl(game.clone())  # pylint: disable=protected-access
            base_policy += np.array(policy, dtype=np.float32)
            base_value += value
        base_policy /= max(1, self._batch_size)
        base_value /= max(1, self._batch_size)
        noise = np.random.default_rng().normal(0, 0.01, size=COLS)
        policy = softmax_masked(base_policy + noise, legal)
        extras = {
            **extras,
            "batched": float(self._batch_size),
            "simulated_power_w": 40.0 + 10.0 * np.random.random(),
        }
        return policy, base_value, extras


__all__ = ["SimulatedTpuModel"]
