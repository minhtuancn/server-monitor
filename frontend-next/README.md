# Server Monitor Frontend (Next.js + TypeScript)

Modern replacement for the legacy static frontend. Built with Next.js App Router, TypeScript, MUI, React Query, React Hook Form, Zod, `next-intl`, and secure BFF proxying to the existing Python backend.

## Quick start

```bash
cd frontend-next
npm install
npm run dev    # listens on :9081 to match existing deployment
```

Production build:

```bash
npm run build
npm run start  # serves optimized build on :9081
```

## Environment variables

Create `.env.local` in `frontend-next/`:

```
API_PROXY_TARGET=http://localhost:9083   # Backend API base (Python)
NEXT_PUBLIC_API_BASE=http://localhost:9083
NEXT_PUBLIC_MONITORING_WS_URL=ws://localhost:9085
NEXT_PUBLIC_TERMINAL_WS_URL=ws://localhost:9084
```

Defaults match the documented backend ports (API 9083, monitoring WS 9085, terminal WS 9084). Override for production/Nginx as needed.

## Architecture highlights

- App Router with locale prefix (`/en`, `/vi`, `/fr`, `/es`, `/de`, `/ja`, `/ko`, `/zh-CN`) via `next-intl`.
- Auth guard through middleware + BFF auth routes: `/api/auth/login`, `/api/auth/logout`, `/api/auth/session`, `/api/auth/token`.
- All backend calls proxied through `/api/proxy/*` preserving the existing API contract.
- WebSockets: monitoring (`/ws`) and terminal (`/terminal`) rewrites defined in `next.config.ts`.
- UI stack: MUI (light/dark), React Query caching, React Hook Form + Zod validation, xterm.js terminal.

## Key routes

- `/{locale}/login` – JWT login
- `/{locale}/dashboard` – stats, servers, exports, live metrics
- `/{locale}/servers/{id}` – server detail + notes
- `/{locale}/terminal?server={id}` – web terminal (xterm.js)
- `/{locale}/settings/*` – system, domain, email, SSH keys
- `/{locale}/notifications`, `/{locale}/users`, `/{locale}/system-check`, `/{locale}/test-cors`

See [`MIGRATION.md`](./MIGRATION.md) for the full legacy → Next.js mapping.

## Reverse proxy expectations

- `/` → Next.js frontend (port 9081)
- `/api/` → Python API (port 9083) — accessed via Next BFF proxy
- `/ws/` → Monitoring WebSocket (port 9085)
- `/terminal/` → Terminal WebSocket (port 9084)

## CI/testing

- `npm run lint` – Next.js lint
- React Query devtools available in development.
