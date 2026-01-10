# P1 Feature Gap: User Management UI

## Goal
Allow administrators to manage users (create, edit, delete, change roles) via the web UI instead of requiring API calls or database edits.

## Context
- Backend API is **fully functional** at `/api/users/*` endpoints
- Full CRUD operations with RBAC (admin-only access)
- Frontend UI is **completely missing** - no `/users` route exists
- Admins must currently use API calls or database tools to manage users

## Scope

### Required UI Elements
1. **User Management Page** at `/users` route
2. **User Table** with columns: username, email, role, status, last_login, actions
3. **Add User Button** (opens dialog)
4. **Edit User Button** (per row, opens dialog)
5. **Delete User Button** (per row, confirmation required)
6. **Search/Filter** (by username, email, role)
7. **Create/Edit Dialog** with fields: username, email, password, role, status

### Files to Create
- `frontend-next/src/app/[locale]/(dashboard)/users/page.tsx` - Main page
- `frontend-next/src/components/users/UserTable.tsx` - Data table component
- `frontend-next/src/components/users/UserDialog.tsx` - Create/edit dialog
- `frontend-next/src/components/users/DeleteUserDialog.tsx` - Confirmation dialog
- `frontend-next/src/hooks/use-users.ts` - API hooks using TanStack Query

### Files to Modify
- `frontend-next/src/components/layout/sidebar-navigation.tsx` - Add "Users" link (admin only)
- `frontend-next/middleware.ts` - Ensure /users requires admin role
- `frontend-next/messages/*.json` - Add i18n keys (8 locales)

### Backend Endpoints (Already Implemented)
- `GET /api/users` - List all users (admin only)
- `POST /api/users` - Create user (admin only)
- `GET /api/users/:id` - Get user details (admin only)
- `PUT /api/users/:id` - Update user (admin only)
- `DELETE /api/users/:id` - Delete user (admin only)

## Acceptance Criteria
- [ ] `/users` route accessible only to admin users
- [ ] User table displays all users with pagination
- [ ] Search box filters users by username or email
- [ ] Role filter dropdown (all/admin/operator/user/auditor)
- [ ] Add User button opens dialog with form
- [ ] Edit user form allows changing email, password, role, status
- [ ] Delete user shows confirmation dialog
- [ ] Cannot delete own account (validation)
- [ ] All text internationalized (8 locales)
- [ ] Error handling for validation failures, API errors
- [ ] Success notifications on create/edit/delete

## Priority
**P1 - High** - Admins cannot manage users via UI, critical for RBAC

## Estimated Effort
2-4 hours (Medium complexity)
