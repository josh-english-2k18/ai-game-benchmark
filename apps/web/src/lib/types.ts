export type Player = 1 | -1;

export type CellValue = Player | 0;

export type Board = CellValue[][];

export interface BackendInfo {
  key: string;
  name: string;
}

export interface InferResponse {
  backend: string;
  model: string;
  policy: number[];
  value: number;
  latency_ms: number;
  extras: Record<string, number>;
}

export interface TelemetryRecord {
  backend: string;
  latency_ms: number;
  value: number;
  fanout?: number;
  ts: number;
  [key: string]: number | string | undefined;
}

export interface SummaryMetric {
  p50: number;
  p95: number;
  avg: number;
  count: number;
}

export type MetricKey = "latency_ms" | "value" | "fanout";

export type SummaryBucket = Record<MetricKey, SummaryMetric>;

export interface MetricsSummary {
  overall: SummaryBucket;
  by_backend: Record<string, SummaryBucket>;
}
