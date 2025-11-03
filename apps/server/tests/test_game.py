import numpy as np

from app.core.game import COLS, ROWS, GameState


def test_drop_disc_and_winner():
    state = GameState()
    for _ in range(4):
        state.drop_disc(0)
        state.drop_disc(1)
    assert state.winner() == 1


def test_encode_planes_shape():
    state = GameState()
    planes = state.encode_planes()
    assert planes.shape == (3, ROWS, COLS)
    assert np.all(planes[2] == 1.0)
