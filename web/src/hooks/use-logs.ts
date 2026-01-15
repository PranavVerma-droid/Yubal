import { useCallback, useEffect, useRef, useState } from "react";

const SSE_URL = "/api/logs/sse";

export interface UseLogsResult {
  lines: string[];
  isConnected: boolean;
  clear: () => void;
}

export function useLogs(): UseLogsResult {
  const [lines, setLines] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  const clear = useCallback(() => {
    setLines([]);
  }, []);

  useEffect(() => {
    const eventSource = new EventSource(SSE_URL);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
    };

    eventSource.onmessage = (event) => {
      setLines((prev) => [...prev, event.data]);
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      // Reconnect is handled automatically by EventSource
    };

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, []);

  return { lines, isConnected, clear };
}
