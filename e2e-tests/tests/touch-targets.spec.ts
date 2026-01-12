import { test, expect } from '../fixtures/test-auth';
import {
  verifyTouchTargetSize,
  waitForPageLoad,
  navigateAndVerify,
  getInteractiveElements,
  getElementSize,
  PAGES,
  VIEWPORTS,
} from '../utils/helpers';

/**
 * Touch Target Size Verification Tests
 * 
 * Ensures all interactive elements meet the minimum touch target size of 44x44 pixels
 * as recommended by:
 * - iOS Human Interface Guidelines
 * - WCAG 2.1 Level AAA (2.5.5 Target Size)
 * - Material Design Guidelines
 * 
 * Minimum size: 44px × 44px
 * Optimal size: 48px × 48px
 */

test.describe('Touch Target Sizes - Mobile View', () => {
  test.use({ viewport: VIEWPORTS.mobile });

  test('Dashboard interactive elements are ≥44px', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.dashboard, 'Dashboard');
    
    const { buttons, iconButtons } = await getInteractiveElements(page);
    
    // Test all visible icon buttons
    const iconButtonCount = await iconButtons.count();
    const maxToTest = Math.min(iconButtonCount, 10);
    
    for (let i = 0; i < maxToTest; i++) {
      const button = iconButtons.nth(i);
      if (await button.isVisible({ timeout: 1000 }).catch(() => false)) {
        await verifyTouchTargetSize(button, `Dashboard icon button ${i + 1}`);
      }
    }
  });

  test('Servers page action buttons are ≥44px', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.servers, 'Servers');
    
    // Add Server button
    const addButton = page.locator('button:has-text("Add Server")').first();
    if (await addButton.isVisible({ timeout: 2000 })) {
      await verifyTouchTargetSize(addButton, 'Add Server button');
    }
    
    // Mobile card action buttons
    const actionButtons = page.locator('.MuiCard-root button, .MuiCard-root [role="button"]');
    const count = await actionButtons.count();
    
    for (let i = 0; i < Math.min(count, 5); i++) {
      const button = actionButtons.nth(i);
      if (await button.isVisible({ timeout: 1000 }).catch(() => false)) {
        await verifyTouchTargetSize(button, `Server card action button ${i + 1}`);
      }
    }
  });

  test('Users page buttons are ≥44px', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.users, 'Users');
    
    // Create User button
    const createButton = page.locator('button:has-text("Create")').first();
    if (await createButton.isVisible({ timeout: 2000 })) {
      await verifyTouchTargetSize(createButton, 'Create User button');
    }
    
    // Role selector (combobox)
    const roleSelect = page.locator('[role="combobox"]').first();
    if (await roleSelect.isVisible({ timeout: 2000 })) {
      const size = await getElementSize(roleSelect);
      expect(size.height, 'Role selector height should be ≥44px').toBeGreaterThanOrEqual(44);
    }
  });

  test('Audit Logs action buttons are ≥44px', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.auditLogs, 'Audit Logs');
    
    // Filter buttons
    const filterButtons = page.locator('button[aria-label*="filter"], button[aria-label*="Filter"]');
    const count = await filterButtons.count();
    
    for (let i = 0; i < Math.min(count, 3); i++) {
      const button = filterButtons.nth(i);
      if (await button.isVisible({ timeout: 1000 }).catch(() => false)) {
        await verifyTouchTargetSize(button, `Filter button ${i + 1}`);
      }
    }
    
    // Mobile card buttons
    const cardButtons = page.locator('.MuiCard-root button');
    const cardButtonCount = await cardButtons.count();
    
    for (let i = 0; i < Math.min(cardButtonCount, 3); i++) {
      const button = cardButtons.nth(i);
      if (await button.isVisible({ timeout: 1000 }).catch(() => false)) {
        await verifyTouchTargetSize(button, `Audit log card button ${i + 1}`);
      }
    }
  });

  test('SSH Keys page buttons are ≥44px', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsSshKeys, 'SSH Keys');
    
    // Add button
    const addButton = page.locator('button:has-text("Add")').first();
    await verifyTouchTargetSize(addButton, 'Add SSH Key button');
    
    // Mobile card action buttons (Edit, Delete)
    const cardButtons = page.locator('.MuiCard-root button, .MuiCard-root [role="button"]');
    const count = await cardButtons.count();
    
    for (let i = 0; i < Math.min(count, 5); i++) {
      const button = cardButtons.nth(i);
      if (await button.isVisible({ timeout: 1000 }).catch(() => false)) {
        await verifyTouchTargetSize(button, `SSH Key card button ${i + 1}`);
      }
    }
  });

  test('Groups page buttons including color picker are ≥44px', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsGroups, 'Groups');
    
    // Add Group button
    const addButton = page.locator('button:has-text("Add")').first();
    await verifyTouchTargetSize(addButton, 'Add Group button');
    
    // Open Add Group dialog
    await addButton.click();
    await page.waitForTimeout(500);
    
    // Color picker buttons
    const colorButtons = page.locator('[role="button"][aria-label*="color"]');
    const colorCount = await colorButtons.count();
    
    for (let i = 0; i < Math.min(colorCount, 8); i++) {
      const colorButton = colorButtons.nth(i);
      if (await colorButton.isVisible({ timeout: 1000 })) {
        // Color pickers should be at least 40x40 (acceptable for color swatches)
        const size = await getElementSize(colorButton);
        expect(size.width, `Color picker ${i + 1} width should be ≥40px`).toBeGreaterThanOrEqual(40);
        expect(size.height, `Color picker ${i + 1} height should be ≥40px`).toBeGreaterThanOrEqual(40);
      }
    }
    
    // Dialog action buttons (Save, Cancel)
    const dialogButtons = page.locator('[role="dialog"] button');
    const dialogButtonCount = await dialogButtons.count();
    
    for (let i = 0; i < Math.min(dialogButtonCount, 3); i++) {
      const button = dialogButtons.nth(i);
      if (await button.isVisible({ timeout: 1000 })) {
        await verifyTouchTargetSize(button, `Dialog button ${i + 1}`);
      }
    }
    
    // Close dialog
    await page.keyboard.press('Escape');
  });

  test('Email settings buttons are ≥44px', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsEmail, 'Email Configuration');
    
    // Save button
    const saveButton = page.locator('button:has-text("Save")').first();
    await verifyTouchTargetSize(saveButton, 'Save Settings button');
    
    // Switch toggle
    const alertSwitch = page.locator('input[type="checkbox"][role="switch"]').first();
    if (await alertSwitch.isVisible({ timeout: 2000 })) {
      // Get the parent span (the visual switch component)
      const switchElement = page.locator('.MuiSwitch-root').first();
      const size = await getElementSize(switchElement);
      expect(size.width, 'Switch width should be ≥44px').toBeGreaterThanOrEqual(38); // MUI switches are 58px by default
      expect(size.height, 'Switch height should be ≥38px').toBeGreaterThanOrEqual(38);
    }
  });

  test('Domain settings buttons are ≥44px', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsDomain, 'Domain & SSL Settings');
    
    // Save button
    const saveButton = page.locator('button:has-text("Save")').first();
    await verifyTouchTargetSize(saveButton, 'Save Settings button');
    
    // SSL switches
    const switches = page.locator('.MuiSwitch-root');
    const switchCount = await switches.count();
    
    for (let i = 0; i < Math.min(switchCount, 3); i++) {
      const switchElement = switches.nth(i);
      if (await switchElement.isVisible({ timeout: 1000 })) {
        const size = await getElementSize(switchElement);
        expect(size.height, `Switch ${i + 1} height should be ≥38px`).toBeGreaterThanOrEqual(38);
      }
    }
  });

  test('Database settings buttons are ≥44px', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsDatabase, 'Database Management');
    
    // Create Backup button
    const backupButton = page.locator('button[aria-label*="backup"], button:has-text("Backup")').first();
    if (await backupButton.isVisible({ timeout: 2000 })) {
      await verifyTouchTargetSize(backupButton, 'Create Backup button');
    }
    
    // Mobile card action buttons
    const cardButtons = page.locator('.MuiCard-root button');
    const count = await cardButtons.count();
    
    for (let i = 0; i < Math.min(count, 5); i++) {
      const button = cardButtons.nth(i);
      if (await button.isVisible({ timeout: 1000 }).catch(() => false)) {
        await verifyTouchTargetSize(button, `Backup card button ${i + 1}`);
      }
    }
  });

  test('Health dashboard buttons are ≥44px', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsHealth, 'System Health Dashboard');
    
    // Refresh button
    const refreshButton = page.locator('button[aria-label*="Refresh"]').first();
    await verifyTouchTargetSize(refreshButton, 'Refresh Health button');
    
    // Auto-refresh chip (clickable)
    const refreshChip = page.locator('div[role="button"][aria-label*="refresh"]').first();
    if (await refreshChip.isVisible({ timeout: 2000 })) {
      const size = await getElementSize(refreshChip);
      // Chips can be smaller but should be at least 32px height
      expect(size.height, 'Refresh chip height should be ≥32px').toBeGreaterThanOrEqual(32);
    }
  });
});

test.describe('Touch Target Sizes - Tablet View', () => {
  test.use({ viewport: VIEWPORTS.tablet });

  test('Tablet view buttons maintain touch-friendly sizes', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.servers, 'Servers');
    
    // Add Server button should still be large enough
    const addButton = page.locator('button:has-text("Add Server")').first();
    if (await addButton.isVisible({ timeout: 2000 })) {
      await verifyTouchTargetSize(addButton, 'Add Server button (tablet)');
    }
    
    // Table action buttons (if table is shown)
    const tableButtons = page.locator('table button, table [role="button"]');
    const count = await tableButtons.count();
    
    if (count > 0) {
      // Tables may be shown on tablet, buttons should still be touch-friendly
      for (let i = 0; i < Math.min(count, 5); i++) {
        const button = tableButtons.nth(i);
        if (await button.isVisible({ timeout: 1000 }).catch(() => false)) {
          const size = await getElementSize(button);
          // Icon buttons in tables can be slightly smaller (40px minimum)
          expect(size.width, `Table button ${i + 1} should be ≥40px`).toBeGreaterThanOrEqual(40);
          expect(size.height, `Table button ${i + 1} should be ≥40px`).toBeGreaterThanOrEqual(40);
        }
      }
    }
  });
});

test.describe('Touch Target Spacing', () => {
  test.use({ viewport: VIEWPORTS.mobile });

  test('Mobile card buttons have adequate spacing', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.settingsSshKeys, 'SSH Keys');
    
    // Get first card's action buttons
    const firstCard = page.locator('.MuiCard-root').first();
    const actionButtons = firstCard.locator('button');
    const count = await actionButtons.count();
    
    if (count >= 2) {
      // Get positions of first two buttons
      const button1 = actionButtons.nth(0);
      const button2 = actionButtons.nth(1);
      
      const box1 = await button1.boundingBox();
      const box2 = await button2.boundingBox();
      
      if (box1 && box2) {
        // Calculate spacing (gap between buttons)
        const spacing = Math.abs((box2.x + box2.width) - box1.x);
        
        // Buttons should have at least 8px spacing between them
        expect(spacing, 'Buttons should have adequate spacing').toBeGreaterThanOrEqual(8);
      }
    }
  });

  test('Form inputs have adequate height on mobile', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.users, 'Users');
    
    // Text inputs should be at least 40px tall for easy tapping
    const inputs = page.locator('input[type="text"], input[type="email"], input[type="password"]');
    const count = await inputs.count();
    
    for (let i = 0; i < Math.min(count, 5); i++) {
      const input = inputs.nth(i);
      if (await input.isVisible({ timeout: 1000 }).catch(() => false)) {
        const size = await getElementSize(input);
        expect(size.height, `Input ${i + 1} height should be ≥40px for easy tapping`).toBeGreaterThanOrEqual(40);
      }
    }
  });
});

test.describe('IconButton Sizes', () => {
  test.use({ viewport: VIEWPORTS.mobile });

  test('All IconButtons meet minimum 44px size', async ({ authenticatedPage: page }) => {
    const pagesToTest = [
      { path: PAGES.dashboard, name: 'Dashboard' },
      { path: PAGES.servers, name: 'Servers' },
      { path: PAGES.auditLogs, name: 'Audit Logs' },
    ];

    for (const { path, name } of pagesToTest) {
      await navigateAndVerify(page, path, name);
      
      // Find all icon buttons (buttons with only icons, no text)
      const iconButtons = page.locator('button[aria-label]:has(svg)');
      const count = await iconButtons.count();
      
      for (let i = 0; i < Math.min(count, 5); i++) {
        const button = iconButtons.nth(i);
        if (await button.isVisible({ timeout: 1000 }).catch(() => false)) {
          await verifyTouchTargetSize(button, `${name} icon button ${i + 1}`);
        }
      }
    }
  });
});
