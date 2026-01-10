# P1 Feature Gap: Theme Persistence to Database

## Goal
Persist user theme preference (light/dark/auto) to the database so it syncs across devices and survives browser data clearing.

## Context
- Theme toggle **works** but only saves to `localStorage`
- Theme preference lost when:
  - Switching devices
  - Clearing browser data
  - Using incognito mode
- Backend user management API can store user preferences
- Need to add `theme_preference` column to `users` table

## Scope

### Backend Changes
1. **Database Migration:** Add `theme_preference` column to `users` table
   - Values: 'light', 'dark', 'auto' (default: 'auto')
2. **API Update:** Modify `PUT /api/users/:id` to accept `theme_preference` field
3. **API Update:** Include `theme_preference` in `GET /api/auth/session` response

### Frontend Changes
1. **Theme Provider:** Update to sync theme changes to backend
2. **Session Hook:** Load theme from `/api/auth/session` on app start
3. **Theme Toggle:** Call API when theme changes (debounced)

### Files to Modify
**Backend:**
- `backend/database.py` - Add column to users table schema
- `backend/user_management.py` - Update user model, add theme_preference field
- `backend/central_api.py` - Update PUT /api/users/:id to handle theme_preference
- `backend/migrations/migrate.py` - Add migration script

**Frontend:**
- `frontend-next/src/components/providers/ThemeProvider.tsx` - Add API sync logic
- `frontend-next/src/hooks/use-theme-sync.ts` - New hook for syncing theme
- `frontend-next/src/hooks/use-session.ts` - Load theme from session

## Acceptance Criteria
- [ ] Database has `theme_preference` column (light/dark/auto, default: auto)
- [ ] PUT /api/users/:id accepts theme_preference field
- [ ] GET /api/auth/session returns theme_preference
- [ ] Theme toggle syncs to backend (debounced 1 second)
- [ ] On app load, theme loaded from session API
- [ ] Theme persists across device switches
- [ ] Theme persists after browser data clear (if logged in)
- [ ] Migration script works on existing databases

## How to Test
1. Login as user
2. Toggle theme to dark mode
3. Wait 1 second (debounce)
4. Check database: `SELECT theme_preference FROM users WHERE username='testuser'` → should be 'dark'
5. Logout, clear localStorage
6. Login again from same browser → theme still dark
7. Login from different device/browser → theme still dark
8. API call: `GET /api/auth/session` → includes `theme_preference: 'dark'`
9. Toggle to light mode → database updated to 'light'
10. Toggle to auto mode → database updated to 'auto', follows system preference

## Priority
**P1 - High** - Users lose theme preference when switching devices

## Estimated Effort
2-3 hours (Medium complexity)

## Dependencies
- Backend user management API (already exists)
- Database migration system (already exists)
- Theme provider (already exists)

## Related Issues
- Feature Parity Report: `docs/audit/FEATURE_PARITY_REPORT.md` section 2.5
