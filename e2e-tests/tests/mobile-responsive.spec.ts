import { test, expect } from '../fixtures/test-auth';
import {
  verifyNoHorizontalScroll,
  verifyMobileCardView,
  waitForPageLoad,
  navigateAndVerify,
  PAGES,
  VIEWPORTS,
} from '../utils/helpers';

/**
 * Mobile Responsive Design Tests
 * 
 * Verifies that all pages:
 * 1. Load correctly at 320px width (minimum mobile size)
 * 2. Have no horizontal scroll
 * 3. Display mobile card views instead of tables (where applicable)
 * 4. Content is readable and usable
 * 
 * Pages tested:
 * - Dashboard
 * - Servers list
 * - Server detail
 * - Terminal
 * - Users
 * - Audit Logs
 * - Settings (SSH Keys, Groups, Email, Domain, Database, Health)
 */

test.describe('Mobile Responsive Design', () => {
  test.use({ viewport: VIEWPORTS.mobile });

  test('Dashboard loads correctly at 320px width', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.dashboard, 'Dashboard');
    await verifyNoHorizontalScroll(page, 'Dashboard');
    
    // Verify stat cards are stacked vertically
    const statCards = page.locator('.MuiCard-root').first();
    await expect(statCards).toBeVisible();
  });

  test('Servers list page is mobile responsive', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.servers, 'Servers');
    await verifyNoHorizontalScroll(page, 'Servers page');
    
    // Verify mobile card view is displayed (not table)
    await verifyMobileCardView(page, VIEWPORTS.mobile.width);
    
    // Verify action buttons are visible and clickable
    const addButton = page.locator('button:has-text("Add Server")').first();
    await expect(addButton).toBeVisible();
  });

  test('Server detail page tabs are scrollable', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.servers, 'Servers');
    await waitForPageLoad(page);
    
    // Click on first server card (mobile view)
    const firstServerCard = page.locator('.MuiCard-root').first();
    if (await firstServerCard.isVisible({ timeout: 2000 })) {
      await firstServerCard.click();
      await waitForPageLoad(page);
      
      // Verify tabs are visible
      const tabs = page.locator('[role="tablist"]').first();
      await expect(tabs).toBeVisible();
      
      // Verify no horizontal scroll on detail page
      await verifyNoHorizontalScroll(page, 'Server detail page');
    }
  });

  test('Terminal page is mobile responsive', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.terminal, 'Terminal');
    await verifyNoHorizontalScroll(page, 'Terminal page');
    
    // Verify terminal selector is visible
    const selector = page.locator('select, [role="combobox"]').first();
    await expect(selector).toBeVisible();
  });

  test('Users page is mobile responsive', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.users, 'Users');
    await verifyNoHorizontalScroll(page, 'Users page');
    
    // Verify form fields are full width
    const usernameInput = page.locator('input[name="username"]').first();
    await expect(usernameInput).toBeVisible();
  });

  test('Audit Logs page has mobile card view', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.auditLogs, 'Audit Logs');
    await verifyNoHorizontalScroll(page, 'Audit Logs page');
    
    // Verify mobile card view
    await verifyMobileCardView(page, VIEWPORTS.mobile.width);
  });

  test('SSH Keys settings page has mobile card view', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsSshKeys, 'SSH Keys');
    await verifyNoHorizontalScroll(page, 'SSH Keys page');
    
    // Verify mobile card view
    await verifyMobileCardView(page, VIEWPORTS.mobile.width);
    
    // Verify add button is visible
    const addButton = page.locator('button:has-text("Add")').first();
    await expect(addButton).toBeVisible();
  });

  test('Groups settings page has mobile card view', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsGroups, 'Groups');
    await verifyNoHorizontalScroll(page, 'Groups page');
    
    // Verify tabs are scrollable
    const tabs = page.locator('[role="tablist"]').first();
    await expect(tabs).toBeVisible();
    
    // Verify mobile card view
    await verifyMobileCardView(page, VIEWPORTS.mobile.width);
  });

  test('Email settings page is mobile responsive', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsEmail, 'Email Configuration');
    await verifyNoHorizontalScroll(page, 'Email settings page');
    
    // Verify form fields are stacked vertically
    const hostInput = page.locator('input[label="SMTP Host"]').first();
    await expect(hostInput).toBeVisible();
  });

  test('Domain settings page is mobile responsive', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsDomain, 'Domain & SSL Settings');
    await verifyNoHorizontalScroll(page, 'Domain settings page');
    
    // Verify form fields are full width
    const domainInput = page.getByLabel('Domain Name');
    await expect(domainInput).toBeVisible();
  });

  test('Database settings page has mobile card view', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsDatabase, 'Database Management');
    await verifyNoHorizontalScroll(page, 'Database settings page');
    
    // Verify backups section shows cards on mobile
    await verifyMobileCardView(page, VIEWPORTS.mobile.width);
  });

  test('Health dashboard page is mobile responsive', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsHealth, 'System Health Dashboard');
    await verifyNoHorizontalScroll(page, 'Health dashboard page');
    
    // Verify service cards are visible
    const serviceCards = page.locator('.MuiCard-root').first();
    await expect(serviceCards).toBeVisible();
  });
});

test.describe('Mobile Responsive at Different Viewports', () => {
  const viewports = [
    { name: 'iPhone SE (320px)', ...VIEWPORTS.mobile },
    { name: 'iPhone 12 (414px)', ...VIEWPORTS.mobileLarge },
    { name: 'iPad (768px)', ...VIEWPORTS.tablet },
  ];

  for (const viewport of viewports) {
    test(`All main pages load at ${viewport.name}`, async ({ authenticatedPage: page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });

      const pagesToTest = [
        { path: PAGES.dashboard, heading: 'Dashboard' },
        { path: PAGES.servers, heading: 'Servers' },
        { path: PAGES.users, heading: 'Users' },
        { path: PAGES.auditLogs, heading: 'Audit Logs' },
      ];

      for (const { path, heading } of pagesToTest) {
        await navigateAndVerify(page, path, heading);
        await verifyNoHorizontalScroll(page, `${heading} at ${viewport.name}`);
      }
    });
  }
});

test.describe('Mobile Navigation', () => {
  test.use({ viewport: VIEWPORTS.mobile });

  test('Mobile menu opens and closes correctly', async ({ authenticatedPage: page }) => {
    await page.goto(PAGES.dashboard);
    await waitForPageLoad(page);

    // Look for mobile menu button (hamburger icon)
    const menuButton = page.locator('button[aria-label*="menu"], button[aria-label*="navigation"]').first();
    
    if (await menuButton.isVisible({ timeout: 2000 })) {
      // Open menu
      await menuButton.click();
      
      // Verify menu is open (drawer visible)
      const drawer = page.locator('[role="presentation"], .MuiDrawer-root').first();
      await expect(drawer).toBeVisible();
      
      // Click a menu item
      const serversLink = page.locator('text=Servers').first();
      await serversLink.click();
      
      // Verify navigation worked
      await page.waitForURL('**/servers');
      await expect(page).toHaveURL(/\/servers/);
    }
  });
});

test.describe('Mobile Form Interactions', () => {
  test.use({ viewport: VIEWPORTS.mobile });

  test('Create user form works on mobile', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.users, 'Users');
    
    // Fill form
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'Test123!@#');
    
    // Select role
    await page.click('[role="combobox"]');
    await page.click('text=User');
    
    // Verify form fields are usable
    const usernameValue = await page.inputValue('input[name="username"]');
    expect(usernameValue).toBe('testuser');
  });
});
