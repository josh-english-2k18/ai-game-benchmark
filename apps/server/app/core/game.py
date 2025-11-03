from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

import numpy as np

ROWS = 6
COLS = 7


@dataclass
class GameState:
    """Represents a Connect Four board with helper utilities."""

    board: np.ndarray = field(
        default_factory=lambda: np.zeros((ROWS, COLS), dtype=np.int8)
    )  # 0 empty, 1 player, -1 opponent
    current_player: int = 1

    @classmethod
    def from_list(cls, cells: Sequence[Sequence[int]], current_player: int) -> "GameState":
        array = np.array(cells, dtype=np.int8)
        if array.shape != (ROWS, COLS):
            raise ValueError(f"Board must be {ROWS}x{COLS}, got {array.shape}")
        if current_player not in (1, -1):
            raise ValueError("current_player must be 1 or -1")
        return cls(board=array, current_player=current_player)

    def clone(self) -> "GameState":
        return GameState(board=self.board.copy(), current_player=self.current_player)

    def legal_moves(self) -> List[int]:
        return [col for col in range(COLS) if self.board[0, col] == 0]

    def drop_disc(self, column: int) -> bool:
        if column < 0 or column >= COLS:
            return False
        for row in range(ROWS - 1, -1, -1):
            if self.board[row, column] == 0:
                self.board[row, column] = self.current_player
                self.current_player *= -1
                return True
        return False

    def is_full(self) -> bool:
        return not any(self.board[0, :] == 0)

    def winner(self) -> Optional[int]:
        for row in range(ROWS):
            for col in range(COLS):
                player = self.board[row, col]
                if player == 0:
                    continue
                if col <= COLS - 4 and np.all(self.board[row, col : col + 4] == player):
                    return player
                if row <= ROWS - 4 and np.all(self.board[row : row + 4, col] == player):
                    return player
                if row <= ROWS - 4 and col <= COLS - 4:
                    if all(self.board[row + i, col + i] == player for i in range(4)):
                        return player
                if row >= 3 and col <= COLS - 4:
                    if all(self.board[row - i, col + i] == player for i in range(4)):
                        return player
        return None

    def encode_planes(self) -> np.ndarray:
        me_plane = (self.board == self.current_player).astype(np.float32)
        opp_plane = (self.board == -self.current_player).astype(np.float32)
        turn_plane = np.full_like(me_plane, 1.0 if self.current_player == 1 else 0.0)
        return np.stack([me_plane, opp_plane, turn_plane], axis=0)
