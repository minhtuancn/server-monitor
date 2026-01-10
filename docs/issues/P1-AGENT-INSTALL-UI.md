# P1 Feature Gap: Remote Agent Install UI

## Goal
Allow administrators to install and manage remote agents via the web UI instead of requiring SSH/CLI access.

## Context
- Backend API is **fully functional** at `/api/remote/agent/*` endpoints
- Deploy, install, start, stop, uninstall, and info endpoints all working
- Frontend UI is **completely missing** - no UI components exist
- Users must currently use CLI scripts or direct API calls

## Scope

### Required UI Elements
1. **Agent Management Tab** in `/servers/:id` page
2. **Install Agent Button** (admin/operator only, RBAC enforced)
3. **Agent Status Indicator** (installed/running/stopped/error)
4. **Control Buttons** (start/stop/restart/uninstall)
5. **Installation Log Viewer** (real-time via polling or WebSocket)
6. **Confirmation Dialogs** (uninstall, reinstall)

### Files to Create
- `frontend-next/src/components/server/AgentManagement.tsx` - Main component
- `frontend-next/src/hooks/use-agent-management.ts` - API hooks using TanStack Query

### Files to Modify
- `frontend-next/src/app/[locale]/(dashboard)/servers/[id]/page.tsx` - Add Agent tab
- `frontend-next/messages/*.json` - Add i18n keys (8 locales)

### Backend Endpoints (Already Implemented)
- `POST /api/remote/agent/deploy/:id` - Copy agent script to server
- `POST /api/remote/agent/install/:id` - Install as systemd service
- `POST /api/remote/agent/start/:id` - Start agent service
- `POST /api/remote/agent/stop/:id` - Stop agent service
- `POST /api/remote/agent/info/:id` - Get agent status
- `POST /api/remote/agent/uninstall/:id` - Remove agent

## Acceptance Criteria
- [ ] Agent tab visible in `/servers/:id` page
- [ ] Install button visible only for admin/operator roles
- [ ] Installation shows real-time progress
- [ ] Agent status indicator updates in real-time
- [ ] Uninstall shows confirmation dialog
- [ ] All text internationalized (8 locales)
- [ ] Error handling for SSH failures
- [ ] Loading states for all async operations

## Priority
**P1 - High** - Users cannot manage agents via UI, must use CLI

## Estimated Effort
2-4 hours (Medium complexity)
