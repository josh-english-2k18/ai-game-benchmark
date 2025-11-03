import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { FiInfo, FiRefreshCcw } from "react-icons/fi";
import { motion } from "framer-motion";

import { GameBoard } from "./components/GameBoard";
import { BackendToggle } from "./components/BackendToggle";
import { ThinkMeter } from "./components/ThinkMeter";
import { TelemetryPanel } from "./components/TelemetryPanel";
import { createBoard, dropDisc, legalMoves, checkWinner } from "./lib/game";
import type { BackendInfo, Board, Player } from "./lib/types";
import { fetchBackends, fetchSummary, postInfer, useTelemetryStream } from "./lib/hooks";

const INTRO_COPY = [
  "One board.",
  "Three backends.",
  "Feel the silicon difference."
];

const IS_TEST_ENV = import.meta.env.MODE === "test";

const useInference = () => {
  const mutation = useMutation({
    mutationFn: postInfer
  });
  return mutation;
};

const chooseColumnFromPolicy = (policy: number[], board: Board) => {
  const legal = legalMoves(board);
  let bestIdx = legal[0] ?? 0;
  let bestScore = -Infinity;
  legal.forEach((idx) => {
    if (policy[idx] > bestScore) {
      bestScore = policy[idx];
      bestIdx = idx;
    }
  });
  return bestIdx;
};

const initialBoard = () => createBoard();

function App() {
  const [board, setBoard] = useState<Board>(initialBoard);
  const [currentPlayer, setCurrentPlayer] = useState<Player>(1);
  const [backend, setBackend] = useState<string>("cpu");
  const [hintColumn, setHintColumn] = useState<number | undefined>(undefined);
  const [statusMessage, setStatusMessage] = useState<string>("You play first. Drop a disc to begin.");
  const [lastLatency, setLastLatency] = useState<number | null>(null);
  const [lastBackend, setLastBackend] = useState<string>("cpu");
  const [isAiThinking, setIsAiThinking] = useState<boolean>(false);
  const [introLine, setIntroLine] = useState(0);

  const telemetryRecords = useTelemetryStream();

  const { data: summary, refetch: refetchSummary } = useQuery({
    queryKey: ["summary"],
    queryFn: fetchSummary,
    refetchInterval: 5000,
    suspense: false
  });

  const { data: backends } = useQuery<BackendInfo[]>({
    queryKey: ["backends"],
    queryFn: fetchBackends,
    initialData: []
  });

  useEffect(() => {
    if (backends.length && !backends.some((b) => b.key === backend)) {
      setBackend(backends[0].key);
    }
  }, [backends, backend]);

  useEffect(() => {
    const timer = setInterval(() => {
      setIntroLine((prev) => (prev + 1) % INTRO_COPY.length);
    }, 2800);
    return () => clearInterval(timer);
  }, []);

  const inference = useInference();

  const resetGame = () => {
    setBoard(initialBoard);
    setCurrentPlayer(1);
    setHintColumn(undefined);
    setStatusMessage("Fresh board. You play first.");
    setLastLatency(null);
  };

  const handlePlayerMove = async (column: number) => {
    if (isAiThinking) return;
    const legal = legalMoves(board);
    if (!legal.includes(column)) return;
    const withPlayerMove = dropDisc(board, column, currentPlayer);
    const winner = checkWinner(withPlayerMove);
    setBoard(withPlayerMove);
    setCurrentPlayer(-1);
    setStatusMessage("AI thinking…");

    if (winner === 1) {
      setStatusMessage("You win! Reset to play again.");
      return;
    }
    if (legalMoves(withPlayerMove).length === 0) {
      setStatusMessage("Stalemate! No more moves.");
      return;
    }
    setIsAiThinking(true);
    try {
      const response = await inference.mutateAsync({
        board: withPlayerMove,
        current_player: -1,
        backend
      });
      const aiColumn = chooseColumnFromPolicy(response.policy, withPlayerMove);
      setHintColumn(aiColumn);
      const withAiMove = dropDisc(withPlayerMove, aiColumn, -1);
      const aiWinner = checkWinner(withAiMove);
      setBoard(withAiMove);
      setCurrentPlayer(1);
      setLastLatency(response.latency_ms);
      setLastBackend(response.backend);
      setStatusMessage(aiWinner === -1 ? "AI wins this round." : "Your move.");
      if (aiWinner === -1) {
        setHintColumn(undefined);
      }
      setTimeout(() => {
        setHintColumn(undefined);
      }, 400);
      setTimeout(() => {
        refetchSummary();
      }, 150);
    } catch (error) {
      console.error(error);
      setStatusMessage(error instanceof Error ? error.message : "Inference failed");
    } finally {
      setIsAiThinking(false);
    }
  };

  const subtitle = useMemo(() => INTRO_COPY[introLine], [introLine]);

  useEffect(() => {
    if (IS_TEST_ENV) {
      setHintColumn(undefined);
      return () => undefined;
    }

    let cancelled = false;
    const runHint = async () => {
      if (currentPlayer !== 1 || isAiThinking) return;
      if (legalMoves(board).length === 0) {
        setHintColumn(undefined);
        return;
      }
      try {
        const response = await postInfer({ board, current_player: 1, backend });
        if (!cancelled) {
          const suggested = chooseColumnFromPolicy(response.policy, board);
          setHintColumn(suggested);
        }
      } catch (error) {
        if (!cancelled) {
          console.error("failed to fetch hint", error);
        }
      }
    };
    runHint();
    return () => {
      cancelled = true;
    };
  }, [backend, board, currentPlayer, isAiThinking]);

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-10 px-6 py-12 text-slate-100">
      <header className="flex flex-col gap-6 rounded-3xl border border-slate-800/80 bg-slate-900/70 p-8 shadow-2xl shadow-indigo-900/30 backdrop-blur-xl md:flex-row md:items-center md:justify-between">
        <div className="max-w-xl">
          <motion.h1
            className="font-display text-4xl font-semibold leading-tight md:text-5xl"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            Silicon Showdown: Connect Four Benchmark
          </motion.h1>
          <motion.p
            className="mt-3 text-lg text-slate-300"
            key={subtitle}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            {subtitle}
          </motion.p>
        </div>
        <div className="flex flex-col items-start gap-4 md:items-end">
          <BackendToggle
            backends={backends}
            activeKey={backend}
            onChange={(key) => {
              setBackend(key);
              setLastBackend(key);
              setLastLatency(null);
              setStatusMessage(`Routing moves to ${key.toUpperCase()} backend.`);
            }}
            disabled={isAiThinking}
          />
          <button
            type="button"
            onClick={resetGame}
            className="flex items-center gap-2 rounded-full bg-gradient-to-r from-slate-700 to-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-[0.3em] text-slate-200 transition hover:from-slate-600 hover:to-slate-700"
          >
            <FiRefreshCcw /> Reset Board
          </button>
        </div>
      </header>

      <section className="grid gap-8 md:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <div className="flex flex-col gap-6">
          <GameBoard
            board={board}
            currentPlayer={currentPlayer}
            isInteractive={currentPlayer === 1 && !isAiThinking}
            legalMoves={legalMoves(board)}
            hintColumn={hintColumn}
            onColumnSelect={handlePlayerMove}
          />
          <div className="rounded-3xl border border-slate-800/70 bg-slate-900/60 p-6 text-sm text-slate-300 backdrop-blur-md">
            <div className="flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-slate-500">
              <FiInfo /> Match State
            </div>
            <p className="mt-2 text-lg font-semibold text-slate-100">{statusMessage}</p>
            <p className="text-xs text-slate-500">
              Tip: Toggle backends mid-game to feel latency shifts in hints and response cadence.
            </p>
          </div>
        </div>
        <div className="flex flex-col gap-6">
          <ThinkMeter latencyMs={lastLatency} backend={lastBackend} />
          <TelemetryPanel summary={summary} records={telemetryRecords} />
        </div>
      </section>
    </main>
  );
}

export default App;
