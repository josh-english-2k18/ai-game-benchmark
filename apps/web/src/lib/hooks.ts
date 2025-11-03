import { useCallback, useEffect, useRef, useState } from "react";

import type { MetricsSummary, TelemetryRecord } from "./types";

const API_BASE = "/api";

export const fetchSummary = async (): Promise<MetricsSummary> => {
  const res = await fetch(`${API_BASE}/metrics/summary`);
  if (!res.ok) {
    throw new Error("Failed to load metrics summary");
  }
  return res.json();
};

export const fetchBackends = async () => {
  const res = await fetch(`${API_BASE}/backends`);
  if (!res.ok) throw new Error("Failed to load backends");
  return res.json();
};

export const postInfer = async (payload: unknown) => {
  const res = await fetch(`${API_BASE}/infer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail?.detail ?? "Inference failed");
  }
  return res.json();
};

export const useTelemetryStream = () => {
  const [records, setRecords] = useState<TelemetryRecord[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${protocol}://${window.location.host}/ws/telemetry`);
    wsRef.current = ws;
    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === "telemetry") {
          setRecords((prev) => [...prev.slice(-127), payload.record]);
        }
      } catch (err) {
        console.error("Failed to parse websocket message", err);
      }
    };
    ws.onclose = () => {
      setTimeout(connect, 2000);
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  return records;
};
