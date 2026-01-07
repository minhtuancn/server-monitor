export type WebSocketMessageHandler<T = unknown> = (data: T) => void;

export function createReconnectingWebSocket(
  url: string,
  handlers: {
    onMessage?: WebSocketMessageHandler;
    onOpen?: () => void;
    onClose?: () => void;
    onError?: (error: Event) => void;
  },
  options: { maxRetries?: number; retryDelayMs?: number } = {},
) {
  const { maxRetries = 5, retryDelayMs = 1500 } = options;
  let retries = 0;
  let ws: WebSocket | null = null;
  let closed = false;

  const connect = () => {
    if (closed) return;
    ws = new WebSocket(url);

    ws.onopen = () => {
      retries = 0;
      handlers.onOpen?.();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handlers.onMessage?.(data);
      } catch {
        handlers.onMessage?.(event.data);
      }
    };

    ws.onerror = (error) => {
      handlers.onError?.(error);
    };

    ws.onclose = () => {
      handlers.onClose?.();
      if (!closed && retries < maxRetries) {
        retries += 1;
        setTimeout(connect, retryDelayMs * retries);
      }
    };
  };

  connect();

  return {
    send: (data: unknown) => {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(typeof data === "string" ? data : JSON.stringify(data));
      }
    },
    close: () => {
      closed = true;
      ws?.close();
    },
    get socket() {
      return ws;
    },
  };
}
