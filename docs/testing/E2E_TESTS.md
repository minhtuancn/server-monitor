# E2E Tests (Playwright)

How to run Playwright end-to-end tests for Server Monitor.

## Prerequisites

- Node.js 18+
- Dependencies installed: `cd frontend-next && npm install`
- Playwright browsers installed (optional for CI: use `npx playwright install --with-deps`)
- App running locally:
  - Frontend: http://localhost:9081/en
  - Backend API: http://localhost:9083

## Environment

Set these when running E2E locally or in CI:

```bash
# Required to actually run (otherwise tests are skipped)
E2E_RUN=1

# Base URL and locale path
E2E_BASE_URL=http://localhost:9081
E2E_BASE_PATH=/en

# Credentials (use non-default in real deployments)
E2E_USER=admin
E2E_PASS=admin123

# Optional
E2E_HEADLESS=true  # set false to watch the browser
```

## Commands

```bash
cd frontend-next
npm run test:e2e            # runs Playwright tests (requires E2E_RUN=1)
E2E_RUN=1 npx playwright test --headed  # example with headed mode
```

## Tests Included

- `auth-and-dashboard.spec.ts`
  - login → dashboard → logout (enabled when E2E_RUN=1)
  - add server → view metrics (skipped until backend data/fixtures added)
  - terminal page loads (skipped until SSH backend fixture available)

## CI Guidance

- Gate execution with `E2E_RUN=1` to avoid failures when environment isn’t ready.
- Ensure backend + frontend are running before tests start (use docker-compose or start-all.sh).
- Collect artifacts: traces (`trace.zip`), screenshots, videos on failure (already enabled in config).
- Typical CI steps:
  1. `npm ci`
  2. `npx playwright install --with-deps`
  3. start services (backend on 9083, frontend on 9081)
  4. `E2E_RUN=1 E2E_BASE_URL=http://localhost:9081 E2E_BASE_PATH=/en npm run test:e2e`

## Known Gaps / TODO

- Add fixtures/mocks for server creation and metrics
- Add terminal mock/fixture to verify terminal page rendering
- Add first-run setup flow test when a clean DB fixture is available
- Wire CI workflow to run on PRs once fixtures are stable
