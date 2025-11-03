import { useMemo } from "react";
import { FiActivity, FiCpu, FiZap } from "react-icons/fi";
import type { MetricsSummary, TelemetryRecord } from "../lib/types";
import { Sparkline } from "./Sparkline";

interface TelemetryPanelProps {
  summary?: MetricsSummary;
  records: TelemetryRecord[];
}

const icons = {
  latency_ms: <FiZap className="text-accent-gpu" />,
  value: <FiActivity className="text-emerald-400" />,
  fanout: <FiCpu className="text-sky-400" />
};

export const TelemetryPanel = ({ summary, records }: TelemetryPanelProps) => {
  const latencyPoints = useMemo(
    () => records.filter((record) => record.latency_ms).map((record) => Number(record.latency_ms)),
    [records]
  );

  const overall = summary?.overall;

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl shadow-cyan-900/40 backdrop-blur-xl">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-100 uppercase tracking-[0.3em]">Live Telemetry</h3>
        <span className="text-xs text-slate-400">{records.length} samples</span>
      </div>
      {overall ? (
        <div className="mt-6 grid gap-5 md:grid-cols-3">
          {Object.entries(overall).map(([metric, stats]) => (
            <div key={metric} className="flex flex-col gap-2 rounded-2xl border border-slate-800/80 bg-slate-900/40 p-4">
              <div className="flex items-center justify-between text-slate-300">
                <span className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.2em]">
                  {icons[metric as keyof typeof icons]} {metric.replace("_", " ")}
                </span>
                <span className="text-[10px] text-slate-500">p50 / p95</span>
              </div>
              <div className="text-2xl font-semibold text-slate-100">
                {stats.p50.toFixed(1)}
                <span className="ml-1 text-sm text-slate-500">
                  {metric === "latency_ms" ? "ms" : metric === "value" ? "" : ""}
                </span>
              </div>
              <div className="text-sm text-slate-400">p95: {stats.p95.toFixed(1)}</div>
              <div className="text-xs text-slate-500">samples: {stats.count.toFixed(0)}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="mt-6 rounded-2xl border border-dashed border-slate-700/60 p-6 text-center text-sm text-slate-400">
          Awaiting telemetry… make a move to see live metrics.
        </div>
      )}
      {summary && Object.keys(summary.by_backend).length > 0 && (
        <div className="mt-6 flex flex-col gap-3 text-xs uppercase tracking-[0.2em] text-slate-500">
          {Object.entries(summary.by_backend).map(([backend, metrics]) => (
            <div key={backend} className="flex flex-wrap items-center gap-4 rounded-2xl bg-slate-900/50 p-3">
              <span className="text-slate-300">{backend.toUpperCase()}</span>
              <span className="text-slate-500">
                p50 {metrics.latency_ms.p50.toFixed(1)} ms / p95 {metrics.latency_ms.p95.toFixed(1)} ms
              </span>
            </div>
          ))}
        </div>
      )}
      <div className="mt-8">
        <Sparkline values={latencyPoints} stroke="#f97316" />
        <p className="mt-2 text-xs uppercase tracking-[0.25em] text-slate-500">Latency trend</p>
      </div>
    </div>
  );
};
