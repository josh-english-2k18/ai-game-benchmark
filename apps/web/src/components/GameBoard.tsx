import { motion } from "framer-motion";
import clsx from "clsx";
import type { Board, Player } from "../lib/types";
import { COLS, ROWS } from "../lib/game";

interface GameBoardProps {
  board: Board;
  currentPlayer: Player;
  isInteractive: boolean;
  legalMoves: number[];
  hintColumn?: number;
  onColumnSelect: (column: number) => void;
}

const columnVariants = {
  initial: { opacity: 0, y: 40 },
  animate: { opacity: 1, y: 0 }
};

const discVariants = {
  drop: { scale: [0.6, 1.05, 1], y: [ -30, 10, 0 ], transition: { duration: 0.35, ease: "easeOut" } }
};

const colorForValue = (value: number) => {
  if (value === 1) return "from-sky-400 to-sky-600";
  if (value === -1) return "from-amber-300 to-amber-500";
  return "from-slate-600 to-slate-800";
};

export const GameBoard = ({
  board,
  currentPlayer,
  isInteractive,
  legalMoves,
  hintColumn,
  onColumnSelect
}: GameBoardProps) => (
  <div className="relative mx-auto w-full max-w-2xl">
    <div className="absolute inset-0 -z-10 blur-3xl bg-gradient-to-br from-blue-500/30 via-cyan-400/20 to-slate-900 opacity-80" />
    <div className="grid grid-cols-7 gap-3 rounded-[32px] border border-slate-700/60 bg-gradient-to-br from-board-light/80 via-board-dark/90 to-board-dark/95 p-6 shadow-2xl shadow-blue-900/30 backdrop-blur-xl">
      {Array.from({ length: COLS }).map((_, colIdx) => {
        const playable = legalMoves.includes(colIdx);
        const hint = isInteractive && hintColumn === colIdx;
        return (
          <motion.button
            key={`col-${colIdx}`}
            type="button"
            className={clsx(
              "group relative flex flex-col gap-3 rounded-full transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400/80",
              playable ? "cursor-pointer" : "cursor-not-allowed opacity-40"
            )}
            style={{ gridRow: "span 6 / span 6" }}
            variants={columnVariants}
            initial="initial"
            animate="animate"
            transition={{ delay: colIdx * 0.05 }}
            disabled={!playable || !isInteractive}
            onClick={() => onColumnSelect(colIdx)}
          >
            <div
              className={clsx(
                "absolute inset-0 rounded-full bg-gradient-to-b opacity-0 transition-opacity duration-300 group-hover:opacity-40",
                currentPlayer === 1 ? "from-sky-500/60" : "from-amber-400/50"
              )}
            />
            {hint && (
              <span className="absolute -top-9 left-1/2 -translate-x-1/2 rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-sky-200 shadow-glow">
                Suggested
              </span>
            )}
            {Array.from({ length: ROWS }).map((_, rowIdx) => {
              const value = board[rowIdx][colIdx];
              return (
                <div key={`cell-${rowIdx}-${colIdx}`} className="relative flex aspect-square items-center justify-center">
                  <motion.div
                    key={`${value}-${rowIdx}-${colIdx}`}
                    variants={discVariants}
                    animate="drop"
                    className={clsx(
                      "h-14 w-14 rounded-full border border-white/5 bg-gradient-to-br shadow-lg shadow-black/40 transition-all duration-500",
                      colorForValue(value)
                    )}
                  >
                    <div className="absolute inset-[18%] rounded-full bg-gradient-to-b from-white/20 to-transparent" />
                  </motion.div>
                </div>
              );
            })}
          </motion.button>
        );
      })}
    </div>
  </div>
);
