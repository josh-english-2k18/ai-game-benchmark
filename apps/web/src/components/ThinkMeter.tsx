import { motion } from "framer-motion";

interface ThinkMeterProps {
  latencyMs: number | null;
  backend: string;
}

const meterColors: Record<string, string> = {
  cpu: "from-blue-500 to-blue-300",
  gpu: "from-orange-500 to-orange-300",
  tpu: "from-emerald-500 to-emerald-300"
};

const backendLabels: Record<string, string> = {
  cpu: "CPU",
  gpu: "GPU",
  tpu: "TPU"
};

export const ThinkMeter = ({ latencyMs, backend }: ThinkMeterProps) => {
  const normalized = latencyMs ? Math.min(latencyMs / 300, 1) : 0.1;
  return (
    <div className="rounded-3xl border border-slate-800/80 bg-slate-900/60 p-6 shadow-xl shadow-indigo-900/20 backdrop-blur-md">
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase tracking-[0.3em] text-slate-400">Think Meter</span>
        <span className="text-sm font-semibold text-slate-100">{backendLabels[backend] ?? backend}</span>
      </div>
      <div className="mt-6 h-4 w-full overflow-hidden rounded-full bg-slate-800/80">
        <motion.div
          className={`h-full bg-gradient-to-r ${meterColors[backend] ?? "from-slate-500 to-slate-300"}`}
          animate={{ width: `${Math.max(10, normalized * 100)}%` }}
          transition={{ type: "spring", stiffness: 120, damping: 20 }}
        />
      </div>
      <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
        <span>Fast</span>
        <span>{latencyMs ? `${latencyMs.toFixed(1)} ms` : "warming"}</span>
        <span>Slow</span>
      </div>
    </div>
  );
};
