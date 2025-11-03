import type { Board, Player } from "./types";

export const ROWS = 6;
export const COLS = 7;

export const createBoard = (): Board => Array.from({ length: ROWS }, () => Array(COLS).fill(0));

export const cloneBoard = (board: Board): Board => board.map((row) => [...row]);

export const dropDisc = (board: Board, column: number, player: Player): Board => {
  const next = cloneBoard(board);
  for (let row = ROWS - 1; row >= 0; row -= 1) {
    if (next[row][column] === 0) {
      next[row][column] = player;
      break;
    }
  }
  return next;
};

export const isColumnPlayable = (board: Board, column: number): boolean => board[0][column] === 0;

export const legalMoves = (board: Board): number[] =>
  Array.from({ length: COLS }, (_, idx) => idx).filter((idx) => isColumnPlayable(board, idx));

export const checkWinner = (board: Board): Player | 0 => {
  const lines = [
    ...generateRows(board),
    ...generateColumns(board),
    ...generateDiagonals(board)
  ];
  for (const line of lines) {
    for (let i = 0; i <= line.length - 4; i += 1) {
      const window = line.slice(i, i + 4);
      if (window.every((cell) => cell === 1)) return 1;
      if (window.every((cell) => cell === -1)) return -1;
    }
  }
  return 0;
};

const generateRows = (board: Board) => board;

const generateColumns = (board: Board) =>
  Array.from({ length: COLS }, (_, col) => board.map((row) => row[col]));

const generateDiagonals = (board: Board) => {
  const diagonals: Board[number][] = [];
  for (let row = 0; row <= ROWS - 4; row += 1) {
    for (let col = 0; col <= COLS - 4; col += 1) {
      const diag1 = [];
      const diag2 = [];
      for (let i = 0; i < 4 && row + i < ROWS && col + i < COLS; i += 1) {
        diag1.push(board[row + i][col + i]);
      }
      diagonals.push(diag1);
      for (let i = 0; i < 4 && row + 3 - i >= 0 && col + i < COLS; i += 1) {
        diag2.push(board[row + 3 - i][col + i]);
      }
      diagonals.push(diag2);
    }
  }
  return diagonals;
};
