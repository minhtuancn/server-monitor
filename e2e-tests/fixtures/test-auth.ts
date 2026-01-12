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
    
    // Wait for API response BEFORE clicking (setup listener first)
    const responsePromise = page.waitForResponse(
      response => response.url().includes('/api/auth/login') && response.status() === 200,
      { timeout: 10000 }
    );
    
    // Wait for URL change (hard refresh with window.location.href)
    const navigationPromise = page.waitForURL(url => url.pathname.includes('/dashboard'), { 
      timeout: 15000 
    });
    
    // Click login button
    await page.click('button[type="submit"]');
    
    // Wait for login API to succeed
    await responsePromise;
    
    // Wait for navigation to dashboard
    await navigationPromise;
    
    // Verify we're on dashboard page
    const url = page.url();
    if (!url.includes('/dashboard')) {
      throw new Error(`Login navigation failed. Expected URL to contain '/dashboard', got: ${url}`);
    }
    
    // Verify dashboard content loaded
    await page.waitForSelector('h1, h2, h3, h4, h5, h6', { state: 'visible', timeout: 5000 });
    
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
