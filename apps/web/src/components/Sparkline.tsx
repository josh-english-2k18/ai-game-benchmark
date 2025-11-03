import { memo } from "react";

interface SparklineProps {
  values: number[];
  stroke?: string;
  height?: number;
}

const SparklineComponent = ({ values, stroke = "#38bdf8", height = 48 }: SparklineProps) => {
  if (values.length <= 1) {
    return <div className="h-12" />;
  }
  const max = Math.max(...values);
  const min = Math.min(...values);
  const normalize = (val: number) => ((val - min) / (max - min || 1)) * 100;
  const points = values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * 100;
      const y = 100 - normalize(value);
      return `${x},${y}`;
    })
    .join(" ");
  return (
    <svg viewBox="0 0 100 100" className="w-full" style={{ height }}>
      <polyline fill="none" stroke={stroke} strokeWidth="6" strokeLinecap="round" points={points} opacity={0.7} />
      <polyline
        fill="url(#fill)"
        stroke="none"
        points={`0,100 ${points} 100,100`}
        opacity={0.15}
      />
    </svg>
  );
};

export const Sparkline = memo(SparklineComponent);
