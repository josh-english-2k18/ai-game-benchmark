import clsx from "clsx";
import type { BackendInfo } from "../lib/types";

interface BackendToggleProps {
  backends: BackendInfo[];
  activeKey: string;
  onChange: (key: string) => void;
  disabled?: boolean;
}

const badgeClass = (backend: string) => {
  switch (backend) {
    case "cpu":
      return "bg-accent-cpu/20 text-accent-cpu border-accent-cpu/60";
    case "gpu":
      return "bg-accent-gpu/20 text-accent-gpu border-accent-gpu/60";
    case "tpu":
      return "bg-accent-tpu/20 text-accent-tpu border-accent-tpu/60";
    default:
      return "bg-slate-700/30 text-slate-100 border-slate-500/50";
  }
};

export const BackendToggle = ({ backends, activeKey, onChange, disabled }: BackendToggleProps) => (
  <div className="flex flex-wrap items-center gap-3">
    {backends.map((backend) => (
      <button
        key={backend.key}
        type="button"
        disabled={disabled}
        onClick={() => onChange(backend.key)}
        className={clsx(
          "rounded-full border px-4 py-2 text-sm font-semibold uppercase tracking-wide transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900",
          badgeClass(backend.key),
          backend.key === activeKey ? "ring-2 ring-white/60 shadow-lg shadow-white/10" : "opacity-70 hover:opacity-100"
        )}
      >
        {backend.name}
      </button>
    ))}
  </div>
);
