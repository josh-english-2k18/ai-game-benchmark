from __future__ import annotations

import time
from typing import Dict, List

import numpy as np

from .base import PolicyValueModel, softmax_masked
from ..core.game import COLS, GameState, ROWS


class HeuristicCpuModel(PolicyValueModel):
    name = "heuristic-cpu"

    def __init__(self) -> None:
        super().__init__(backend="cpu")

    def load(self) -> None:
        # Nothing to load for heuristic model, but keep consistent interface.
        return

    def _infer_impl(self, game: GameState) -> tuple[List[float], float, Dict[str, float]]:
        legal = game.legal_moves()
        scores = np.full(COLS, -1e9, dtype=np.float32)
        for column in range(COLS):
            if column not in legal:
                continue
            scores[column] = self._score_column(game, column)
        # Simulate slower CPU-bound inference by accounting for vectorized compute.
        time.sleep(0.035 + np.random.random() * 0.01)
        policy = softmax_masked(scores, legal)
        value_estimate = self._estimate_value(game)
        extras: Dict[str, float] = {
            "fanout": float(len(legal)),
            "max_score": float(np.max(scores[legal])),
        }
        return policy, value_estimate, extras

    def _score_column(self, game: GameState, column: int) -> float:
        clone = game.clone()
        clone.drop_disc(column)
        winner = clone.winner()
        if winner == 1:
            return 100.0
        if winner == -1:
            return -100.0
        center_bonus = 5.0 - abs(3 - column)
        open_threes = self._count_patterns(clone.board, clone.current_player * -1, length=3)
        opp_threats = self._count_patterns(clone.board, clone.current_player, length=3)
        return center_bonus + 2.0 * open_threes - 3.0 * opp_threats

    def _estimate_value(self, game: GameState) -> float:
        winner = game.winner()
        if winner == 1:
            return 1.0
        if winner == -1:
            return -1.0
        return float(np.clip(self._count_patterns(game.board, 1, 3) - self._count_patterns(game.board, -1, 3), -1, 1))

    @staticmethod
    def _count_patterns(board: np.ndarray, player: int, length: int) -> int:
        count = 0
        for row in range(ROWS):
            for col in range(COLS - length + 1):
                window = board[row, col : col + length]
                if np.count_nonzero(window == player) == length - 1 and np.count_nonzero(window == 0) == 1:
                    count += 1
        for col in range(COLS):
            for row in range(ROWS - length + 1):
                window = board[row : row + length, col]
                if (
                    np.count_nonzero(window == player) == length - 1
                    and np.count_nonzero(window == 0) == 1
                ):
                    count += 1
        for row in range(ROWS - length + 1):
            for col in range(COLS - length + 1):
                window = [board[row + i, col + i] for i in range(length)]
                if window.count(player) == length - 1 and window.count(0) == 1:
                    count += 1
                window = [board[row + length - 1 - i, col + i] for i in range(length)]
                if window.count(player) == length - 1 and window.count(0) == 1:
                    count += 1
        return count


__all__ = ["HeuristicCpuModel"]
