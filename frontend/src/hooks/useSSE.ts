import { useEffect, useRef, useCallback, useState } from "react";
import type { SSEEvent } from "@/lib/types";

interface UseSSEOptions {
  onMessage: (event: SSEEvent) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  enabled?: boolean;
}

export function useSSE(url: string, options: UseSSEOptions) {
  const { onMessage, onError, onOpen, enabled = true } = options;
  const eventSourceRef = useRef<EventSource | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  // Stable callback refs
  const onMessageRef = useRef(onMessage);
  const onErrorRef = useRef(onError);
  const onOpenRef = useRef(onOpen);

  useEffect(() => {
    onMessageRef.current = onMessage;
    onErrorRef.current = onError;
    onOpenRef.current = onOpen;
  }, [onMessage, onError, onOpen]);

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      setConnectionError(null);
      onOpenRef.current?.();
    };

    eventSource.onmessage = (event) => {
      try {
        const sseEvent: SSEEvent = JSON.parse(event.data);
        onMessageRef.current(sseEvent);
      } catch (err) {
        console.error("Failed to parse SSE event:", err);
      }
    };

    eventSource.onerror = (error) => {
      setIsConnected(false);
      setConnectionError("Connection lost");
      onErrorRef.current?.(error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [url]);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    if (!enabled) {
      disconnect();
      return;
    }

    const cleanup = connect();
    return () => {
      cleanup?.();
    };
  }, [enabled, connect, disconnect]);

  return {
    isConnected,
    connectionError,
    reconnect: connect,
    disconnect,
  };
}
