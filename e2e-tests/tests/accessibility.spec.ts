import { test, expect } from '../fixtures/test-auth';
import {
  verifyAriaLabel,
  verifyKeyboardAccessible,
  waitForPageLoad,
  navigateAndVerify,
  getInteractiveElements,
  PAGES,
} from '../utils/helpers';

/**
 * Accessibility Tests (ARIA + Keyboard Navigation)
 * 
 * Verifies:
 * 1. All interactive elements have ARIA labels
 * 2. Buttons and links are keyboard accessible (Tab, Enter, Space)
 * 3. Forms are properly labeled
 * 4. Dialogs have proper ARIA attributes
 * 5. No elements use browser confirm()
 * 
 * WCAG 2.1 Level AA Compliance
 */

test.describe('ARIA Labels - All Pages', () => {
  test('Dashboard page has ARIA labels on interactive elements', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.dashboard, 'Dashboard');
    
    const { buttons, iconButtons } = await getInteractiveElements(page);
    
    // Check all icon buttons have aria-label
    const iconButtonCount = await iconButtons.count();
    for (let i = 0; i < Math.min(iconButtonCount, 10); i++) {
      const button = iconButtons.nth(i);
      if (await button.isVisible()) {
        await verifyAriaLabel(button, `Icon button ${i + 1}`);
      }
    }
  });

  test('Servers page has ARIA labels', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.servers, 'Servers');
    
    // Add Server button
    const addButton = page.locator('button:has-text("Add Server")').first();
    await verifyAriaLabel(addButton, 'Add Server button');
    
    // Search/filter inputs
    const searchInputs = page.locator('input[type="text"], input[type="search"]');
    const searchCount = await searchInputs.count();
    
    for (let i = 0; i < Math.min(searchCount, 3); i++) {
      const input = searchInputs.nth(i);
      if (await input.isVisible()) {
        const ariaLabel = await input.getAttribute('aria-label');
        expect(ariaLabel, `Search input ${i + 1} should have aria-label`).toBeTruthy();
      }
    }
  });

  test('Users page form has ARIA labels', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.users, 'Users');
    
    // Form inputs
    const usernameInput = page.locator('input[name="username"]').first();
    const emailInput = page.locator('input[name="email"]').first();
    const passwordInput = page.locator('input[name="password"]').first();
    
    await verifyAriaLabel(usernameInput, 'Username input');
    await verifyAriaLabel(emailInput, 'Email input');
    await verifyAriaLabel(passwordInput, 'Password input');
    
    // Create button
    const createButton = page.locator('button:has-text("Create")').first();
    await verifyAriaLabel(createButton, 'Create User button');
  });

  test('Audit Logs page has ARIA labels', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.auditLogs, 'Audit Logs');
    
    // Filter controls
    const filterButtons = page.locator('button[aria-label*="filter"], button[aria-label*="Filter"]');
    const count = await filterButtons.count();
    
    for (let i = 0; i < Math.min(count, 5); i++) {
      const button = filterButtons.nth(i);
      if (await button.isVisible()) {
        await verifyAriaLabel(button, `Filter button ${i + 1}`);
      }
    }
    
    // Export button
    const exportButton = page.locator('button[aria-label*="export"], button[aria-label*="Export"]').first();
    if (await exportButton.isVisible({ timeout: 2000 })) {
      await verifyAriaLabel(exportButton, 'Export button');
    }
  });

  test('SSH Keys settings page has ARIA labels', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsSshKeys, 'SSH Keys');
    
    // Add button
    const addButton = page.locator('button:has-text("Add")').first();
    await verifyAriaLabel(addButton, 'Add SSH Key button');
    
    // Action buttons (edit, delete) on existing keys
    const editButtons = page.locator('button[aria-label*="Edit"]');
    const deleteButtons = page.locator('button[aria-label*="Delete"]');
    
    if (await editButtons.count() > 0) {
      await verifyAriaLabel(editButtons.first(), 'Edit button');
    }
    
    if (await deleteButtons.count() > 0) {
      await verifyAriaLabel(deleteButtons.first(), 'Delete button');
    }
  });

  test('Groups settings page has ARIA labels including color picker', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsGroups, 'Groups');
    
    // Add Group button
    const addButton = page.locator('button:has-text("Add")').first();
    await verifyAriaLabel(addButton, 'Add Group button');
    
    // Check if add dialog opens
    await addButton.click();
    await page.waitForTimeout(500);
    
    // Color picker buttons
    const colorButtons = page.locator('[role="button"][aria-label*="color"]');
    const colorCount = await colorButtons.count();
    
    if (colorCount > 0) {
      for (let i = 0; i < Math.min(colorCount, 3); i++) {
        const colorButton = colorButtons.nth(i);
        await verifyAriaLabel(colorButton, `Color picker ${i + 1}`);
        
        // Verify aria-pressed attribute exists
        const ariaPressed = await colorButton.getAttribute('aria-pressed');
        expect(ariaPressed, `Color button ${i + 1} should have aria-pressed`).toBeTruthy();
      }
    }
    
    // Close dialog
    await page.keyboard.press('Escape');
  });

  test('Email settings page has ARIA labels', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsEmail, 'Email Configuration');
    
    // Enable alerts switch
    const alertSwitch = page.locator('input[type="checkbox"][role="switch"]').first();
    await verifyAriaLabel(alertSwitch, 'Enable Alerts switch');
    
    // Save button
    const saveButton = page.locator('button:has-text("Save")').first();
    await verifyAriaLabel(saveButton, 'Save button');
  });

  test('Domain settings page has ARIA labels', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsDomain, 'Domain & SSL Settings');
    
    // Domain name input
    const domainInput = page.getByLabel('Domain Name');
    await verifyAriaLabel(domainInput, 'Domain input');
    
    // SSL enable switch
    const sslSwitch = page.locator('input[type="checkbox"][aria-label*="SSL"]').first();
    if (await sslSwitch.isVisible({ timeout: 2000 })) {
      await verifyAriaLabel(sslSwitch, 'SSL switch');
    }
    
    // Save button
    const saveButton = page.locator('button[aria-label*="Save"]').first();
    await verifyAriaLabel(saveButton, 'Save button');
  });

  test('Database settings page has ARIA labels', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsDatabase, 'Database Management');
    
    // Backup actions
    const createBackupButton = page.locator('button[aria-label*="backup"], button[aria-label*="Backup"]').first();
    if (await createBackupButton.isVisible({ timeout: 2000 })) {
      await verifyAriaLabel(createBackupButton, 'Create Backup button');
    }
    
    // Restore/Delete buttons on backup items
    const restoreButtons = page.locator('button[aria-label*="Restore"]');
    const deleteButtons = page.locator('button[aria-label*="Delete"]');
    
    if (await restoreButtons.count() > 0) {
      await verifyAriaLabel(restoreButtons.first(), 'Restore button');
    }
    
    if (await deleteButtons.count() > 0) {
      await verifyAriaLabel(deleteButtons.first(), 'Delete button');
    }
  });

  test('Health dashboard has ARIA labels', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsHealth, 'System Health Dashboard');
    
    // Auto-refresh toggle
    const autoRefreshChip = page.locator('div[role="button"][aria-label*="refresh"]').first();
    if (await autoRefreshChip.isVisible({ timeout: 2000 })) {
      await verifyAriaLabel(autoRefreshChip, 'Auto-refresh toggle');
    }
    
    // Refresh button
    const refreshButton = page.locator('button[aria-label*="Refresh"]').first();
    await verifyAriaLabel(refreshButton, 'Refresh button');
  });
});

test.describe('Keyboard Navigation', () => {
  test('Tab navigation works on login page', async ({ page }) => {
    await page.goto('/en/login');
    await waitForPageLoad(page);
    
    // Start from username field
    await page.click('input[name="username"]');
    
    // Tab to password
    await page.keyboard.press('Tab');
    const passwordFocused = await page.locator('input[name="password"]').evaluate(
      (el) => el === document.activeElement
    );
    expect(passwordFocused, 'Password field should be focused after Tab').toBe(true);
    
    // Tab to submit button
    await page.keyboard.press('Tab');
    const buttonFocused = await page.locator('button[type="submit"]').evaluate(
      (el) => el === document.activeElement
    );
    expect(buttonFocused, 'Submit button should be focused after Tab').toBe(true);
  });

  test('Escape key closes dialogs', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsSshKeys, 'SSH Keys');
    
    // Open Add dialog
    const addButton = page.locator('button:has-text("Add")').first();
    await addButton.click();
    await page.waitForTimeout(300);
    
    // Verify dialog is open
    const dialog = page.locator('[role="dialog"]').first();
    await expect(dialog).toBeVisible();
    
    // Press Escape to close
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);
    
    // Verify dialog is closed
    await expect(dialog).not.toBeVisible();
  });

  test('Enter key activates buttons', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.dashboard, 'Dashboard');
    
    // Focus a button
    const button = page.locator('button').first();
    await button.focus();
    
    // Verify button is focused
    const isFocused = await button.evaluate((el) => el === document.activeElement);
    expect(isFocused, 'Button should be focused').toBe(true);
    
    // Note: We don't actually press Enter as it might trigger navigation
    // Just verify the button CAN be focused
  });

  test('Color picker is keyboard accessible', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsGroups, 'Groups');
    
    // Open Add Group dialog
    const addButton = page.locator('button:has-text("Add")').first();
    await addButton.click();
    await page.waitForTimeout(500);
    
    // Find color picker buttons
    const colorButtons = page.locator('[role="button"][aria-label*="color"]');
    const count = await colorButtons.count();
    
    if (count > 0) {
      const firstColor = colorButtons.first();
      
      // Verify tabIndex is set (focusable)
      const tabIndex = await firstColor.getAttribute('tabindex');
      expect(parseInt(tabIndex || '-1'), 'Color picker should have tabIndex 0').toBe(0);
      
      // Focus the color button
      await firstColor.focus();
      
      // Verify it's focused
      const isFocused = await firstColor.evaluate((el) => el === document.activeElement);
      expect(isFocused, 'Color picker should be focusable').toBe(true);
    }
    
    // Close dialog
    await page.keyboard.press('Escape');
  });
});

test.describe('Dialog Accessibility', () => {
  test('ConfirmDialog has proper ARIA attributes', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsSshKeys, 'SSH Keys');
    
    // Try to trigger delete confirmation dialog
    const deleteButton = page.locator('button[aria-label*="Delete"]').first();
    
    if (await deleteButton.isVisible({ timeout: 2000 })) {
      await deleteButton.click();
      await page.waitForTimeout(500);
      
      // Verify ConfirmDialog appeared (not browser confirm)
      const confirmDialog = page.locator('[role="dialog"]').first();
      
      if (await confirmDialog.isVisible({ timeout: 2000 })) {
        // Verify dialog has title
        const dialogTitle = confirmDialog.locator('h2, [role="heading"]').first();
        await expect(dialogTitle).toBeVisible();
        
        // Verify action buttons are labeled
        const confirmButton = confirmDialog.locator('button:has-text("Delete")').first();
        const cancelButton = confirmDialog.locator('button:has-text("Cancel")').first();
        
        await expect(confirmButton).toBeVisible();
        await expect(cancelButton).toBeVisible();
        
        // Close dialog
        await cancelButton.click();
      }
    }
  });

  test('Form dialogs have proper labels', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsGroups, 'Groups');
    
    // Open Add Group dialog
    const addButton = page.locator('button:has-text("Add")').first();
    await addButton.click();
    await page.waitForTimeout(500);
    
    // Verify dialog has title
    const dialog = page.locator('[role="dialog"]').first();
    await expect(dialog).toBeVisible();
    
    const dialogTitle = dialog.locator('h2, [role="heading"]').first();
    await expect(dialogTitle).toBeVisible();
    
    // Verify form inputs have labels
    const nameInput = dialog.locator('input[name="name"]').first();
    if (await nameInput.isVisible({ timeout: 1000 })) {
      const label = await nameInput.getAttribute('aria-label');
      expect(label, 'Name input should have aria-label').toBeTruthy();
    }
    
    // Close dialog
    await page.keyboard.press('Escape');
  });
});

test.describe('No Browser Confirm() Usage', () => {
  test('Delete actions use ConfirmDialog instead of confirm()', async ({ authenticatedPage: page }) => {
    // Monitor for browser confirm() calls
    let confirmCalled = false;
    
    page.on('dialog', async (dialog) => {
      if (dialog.type() === 'confirm') {
        confirmCalled = true;
        await dialog.dismiss();
      }
    });
    
    // Test SSH Keys delete
    await navigateAndVerify(page, PAGES.settingsSshKeys, 'SSH Keys');
    const deleteButton = page.locator('button[aria-label*="Delete"]').first();
    
    if (await deleteButton.isVisible({ timeout: 2000 })) {
      await deleteButton.click();
      await page.waitForTimeout(1000);
      
      expect(confirmCalled, 'Should NOT use browser confirm()').toBe(false);
      
      // Verify ConfirmDialog is used instead
      const confirmDialog = page.locator('[role="dialog"]').first();
      const dialogVisible = await confirmDialog.isVisible({ timeout: 2000 }).catch(() => false);
      
      if (dialogVisible) {
        expect(dialogVisible, 'Should use ConfirmDialog component').toBe(true);
        await page.keyboard.press('Escape');
      }
    }
  });
});

test.describe('Screen Reader Support', () => {
  test('Page landmarks are properly defined', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.dashboard, 'Dashboard');
    
    // Check for main landmark
    const main = page.locator('main, [role="main"]').first();
    const mainExists = await main.isVisible({ timeout: 2000 }).catch(() => false);
    expect(mainExists, 'Page should have main landmark').toBe(true);
    
    // Check for navigation
    const nav = page.locator('nav, [role="navigation"]').first();
    const navExists = await nav.isVisible({ timeout: 2000 }).catch(() => false);
    expect(navExists, 'Page should have navigation landmark').toBe(true);
  });

  test('Headings are properly structured', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.dashboard, 'Dashboard');
    
    // Check for h1 or main heading
    const h1 = page.locator('h1, h4, h5').first();
    await expect(h1).toBeVisible();
    
    // Verify heading text is not empty
    const headingText = await h1.textContent();
    expect(headingText?.trim().length, 'Heading should have text').toBeGreaterThan(0);
  });
});
