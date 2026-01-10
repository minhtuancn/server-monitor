import { test, expect } from '@playwright/test';

const E2E_ENABLED = process.env.E2E_RUN === '1';
const basePath = process.env.E2E_BASE_PATH || ''; // e.g., '/en'
const username = process.env.E2E_USER || 'admin';
const password = process.env.E2E_PASS || 'admin123';

// Helper to build localized paths
const path = (p: string) => `${basePath}${p}`;

// Skip entire suite unless explicitly enabled
test.describe.configure({ mode: 'serial' });
test.skip(!E2E_ENABLED, 'Set E2E_RUN=1 to enable E2E tests');

// Clear auth state before each test
test.beforeEach(async ({ page, context }) => {
  // Clear all cookies to ensure clean auth state
  await context.clearCookies();
  // Navigate to login and clear storage after page loads
  await page.goto(path('/login'));
  await page.evaluate(() => {
    try {
      localStorage.clear();
      sessionStorage.clear();
    } catch (e) {
      // Storage may not be available, that's OK
    }
  });
});

test('login → dashboard → logout', async ({ page }) => {
  // Page is already at /login from beforeEach
  await page.waitForLoadState('networkidle');

  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: /login/i }).click();

  await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();

  // Open menu if mobile and tap logout icon
  const logoutButton = page.getByRole('button', { name: /logout/i });
  await logoutButton.click();

  await expect(page.getByRole('button', { name: /login/i })).toBeVisible();
});

test('navigation menu and pages load correctly', async ({ page }) => {
  // Login first (explicit login for this test)
  await page.goto(path('/login'));
  await page.waitForLoadState('networkidle');
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: /login/i }).click();
  
  // Wait for dashboard to load
  await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();

  // Test main navigation pages
  await page.getByRole('link', { name: /settings/i }).first().click();
  await expect(page.getByRole('heading', { name: /settings/i })).toBeVisible();

  // Test Users page (admin only)
  await page.getByRole('link', { name: /users/i }).click();
  await expect(page.getByRole('heading', { name: /user management/i })).toBeVisible();

  // Test System Check page
  await page.getByRole('link', { name: /system check/i }).click();
  await expect(page.getByRole('heading', { name: /system check/i })).toBeVisible();

  // Return to dashboard
  await page.getByRole('link', { name: /dashboard/i }).click();
  await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
});

test('dashboard components load and display', async ({ page }) => {
  // Login and navigate to dashboard (explicit login)
  await page.goto(path('/login'));
  await page.waitForLoadState('networkidle');
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: /login/i }).click();
  await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();

  // Check main dashboard sections are visible
  await expect(page.getByRole('heading', { name: /servers/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: /add server/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: /recent activity/i })).toBeVisible();

  // Check export buttons are present
  await expect(page.getByRole('button', { name: /export csv/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /export json/i })).toBeVisible();

  // Check refresh button is present (use more specific selector)
  await expect(page.getByRole('button', { name: /refresh/i })).toBeVisible();
});

test('responsive design works on mobile viewport', async ({ page }) => {
  // Set mobile viewport
  await page.setViewportSize({ width: 375, height: 667 });
  
  // Login (explicit login with mobile viewport)
  await page.goto(path('/login'));
  await page.waitForLoadState('networkidle');
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: /login/i }).click();
  await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();

  // Check mobile menu button is visible
  const menuButton = page.getByRole('button', { name: /menu/i });
  await expect(menuButton).toBeVisible();

  // Open mobile menu
  await menuButton.click();
  
  // Check navigation items are visible in mobile menu
  await expect(page.getByRole('link', { name: /settings/i })).toBeVisible();
  await expect(page.getByRole('link', { name: /users/i })).toBeVisible();
});

test.skip('add server → view metrics (requires live backend data)', async ({ page }) => {
  await page.goto(path('/dashboard'));
  await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: /servers/i })).toBeVisible();
});

test.skip('terminal page loads (requires SSH backend)', async ({ page }) => {
  await page.goto(path('/terminal'));
  await expect(page.getByRole('heading', { name: /terminal/i })).toBeVisible();
});
