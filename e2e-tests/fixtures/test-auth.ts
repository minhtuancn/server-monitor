import { test as base } from '@playwright/test';
import { Page } from '@playwright/test';

/**
 * Authentication fixture for Server Monitor E2E tests
 * 
 * This fixture handles login and provides an authenticated page context
 * for tests that require authentication.
 */

type AuthFixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // Navigate to login page
    await page.goto('/en/login');
    
    // Wait for login form to be visible
    await page.waitForSelector('input[name="username"]', { state: 'visible' });
    
    // Fill in credentials
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    
    // Click login button
    await page.click('button[type="submit"]');
    
    // Wait for successful login (redirects to dashboard)
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Verify we're on the dashboard
    await page.waitForSelector('text=Dashboard', { state: 'visible' });
    
    // Use the authenticated page
    await use(page);
  },
});

export { expect } from '@playwright/test';

/**
 * Helper function to login manually
 * Use this if you need to login without the fixture
 */
export async function login(page: Page, username = 'admin', password = 'admin123') {
  await page.goto('/en/login');
  await page.waitForSelector('input[name="username"]', { state: 'visible' });
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard', { timeout: 10000 });
}

/**
 * Helper function to logout
 */
export async function logout(page: Page) {
  // Click user menu button
  await page.click('[aria-label*="user menu"]', { timeout: 5000 }).catch(() => {
    // Fallback: try clicking on avatar or profile button
    page.click('button:has-text("admin")').catch(() => {});
  });
  
  // Click logout option
  await page.click('text=Logout', { timeout: 5000 }).catch(() => {
    page.click('text=Sign Out').catch(() => {});
  });
  
  // Wait for redirect to login page
  await page.waitForURL('**/login', { timeout: 10000 });
}
