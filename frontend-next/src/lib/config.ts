/**
 * Configuration for API and WebSocket endpoints
 * Supports both development (localhost:PORT) and custom domain deployments (mon.go7s.net)
 */

export const API_BASE_URL =
  process.env.API_PROXY_TARGET ||
  process.env.NEXT_PUBLIC_API_BASE ||
  "http://localhost:9083";

export const MONITORING_WS_URL =
  process.env.NEXT_PUBLIC_MONITORING_WS_URL || "ws://localhost:9085";

export const TERMINAL_WS_URL =
  process.env.NEXT_PUBLIC_TERMINAL_WS_URL || "ws://localhost:9084";

export const API_PROXY_PREFIX = "/api/proxy";

// Current domain (for dynamic endpoint configuration)
export const CURRENT_DOMAIN = process.env.NEXT_PUBLIC_DOMAIN || "localhost";
