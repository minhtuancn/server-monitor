# Frontend Migration Map (Legacy HTML → Next.js App Router)

| Legacy HTML (frontend/) | New Next.js Route | Access Level | Key Features / API calls |
| --- | --- | --- | --- |
| `index.html` | `/{locale}/dashboard` | authenticated (public view limited by backend) | Stats (`/api/stats/overview`), server list (`/api/servers`), exports (`/api/export/servers/*`), live WebSocket (`/ws`) |
| `login.html` | `/{locale}/login` | public | JWT login via `/api/auth/login` (BFF sets HttpOnly cookie) |
| `dashboard.html` | `/{locale}/dashboard` | authenticated | Multi-server cards, quick actions, exports, live metrics WebSocket |
| `server-detail.html` | `/{locale}/servers/{id}` | authenticated | Server detail (`/api/servers/:id`), notes CRUD (`/api/servers/:id/notes`) |
| `server-notes.html` | `/{locale}/server-notes` → links to detail pages | authenticated | Notes list per server |
| `terminal.html` | `/{locale}/terminal?server={id}` | authenticated | xterm.js client, WebSocket to `/terminal` sending `{token, server_id}` |
| `settings.html` | `/{locale}/settings` | authenticated/admin | System settings (`/api/settings`, `/api/settings/:key`) |
| `domain-settings.html` | `/{locale}/settings/domain` | admin | Domain/SSL (`/api/domain/settings`) |
| `email-settings.html` | `/{locale}/settings/email` | admin | Email config (`/api/email/config`) |
| `ssh-keys.html` | `/{locale}/settings/ssh-keys` | authenticated | SSH key CRUD (`/api/ssh-keys`) |
| `notifications.html` | `/{locale}/notifications` | authenticated | Alerts feed (`/api/alerts`) |
| `users.html` | `/{locale}/users` | admin | User CRUD (`/api/users`, `/api/users/{id}`) |
| `system-check.html` | `/{locale}/system-check` | authenticated | API probe, WebSocket checks (`/ws`, `/terminal`) |
| `test_cors.html` | `/{locale}/test-cors` | authenticated | CORS probe (`/api/stats/overview`) |

**Routing notes**
- Locale prefix uses `next-intl` (`en`, `vi`, `fr`, `es`, `de`, `ja`, `ko`, `zh-CN`).
- Auth guard enforced via middleware (redirects unauthenticated users to `/{locale}/login`).
- All backend calls go through the BFF proxy `/api/proxy/*` to keep the legacy API contract intact.
