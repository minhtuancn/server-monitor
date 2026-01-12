import { test, expect } from '@playwright/test';

/**
 * Quick smoke test - verify app is running
 */

test.describe('Smoke Test', () => {
  test('Login page loads', async ({ page }) => {
    await page.goto('http://172.22.0.103:9081/en/login');
    
    // Check title
    await expect(page).toHaveTitle(/Server Monitor/);
    
    // Check login form exists
    await expect(page.locator('input[name="username"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
    
    console.log('✅ Login page loads correctly');
  });

  test('Can login successfully', async ({ page }) => {
    await page.goto('http://172.22.0.103:9081/en/login');
    
    // Fill credentials
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
    console.log('✅ Login API responded successfully');
    
    // Wait for navigation to dashboard
    await navigationPromise;
    
    // Verify we're on dashboard page
    const url = page.url();
    console.log('Current URL after login:', url);
    expect(url).toContain('/dashboard');
    
    // Verify dashboard content loaded
    await page.waitForSelector('h1, h2, h3, h4, h5, h6', { state: 'visible', timeout: 5000 });
    
    console.log('✅ Login successful and dashboard loaded');
  });
});
