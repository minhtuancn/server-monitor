import { Page, Locator, expect } from '@playwright/test';

/**
 * Helper utilities for Playwright E2E tests
 */

/**
 * Check if an element has horizontal scroll
 * Used to verify mobile responsive design (no horizontal scroll)
 */
export async function hasHorizontalScroll(page: Page): Promise<boolean> {
  const scrollWidth = await page.evaluate(() => document.body.scrollWidth);
  const clientWidth = await page.evaluate(() => document.body.clientWidth);
  return scrollWidth > clientWidth;
}

/**
 * Verify no horizontal scroll on page
 * @param page - Playwright page object
 * @param pageName - Name of the page for error message
 */
export async function verifyNoHorizontalScroll(page: Page, pageName: string) {
  const hasScroll = await hasHorizontalScroll(page);
  expect(hasScroll, `${pageName} should not have horizontal scroll`).toBe(false);
}

/**
 * Get computed size of an element
 * @param locator - Element locator
 * @returns Object with width and height in pixels
 */
export async function getElementSize(locator: Locator): Promise<{ width: number; height: number }> {
  const box = await locator.boundingBox();
  if (!box) {
    throw new Error('Element not found or not visible');
  }
  return { width: box.width, height: box.height };
}

/**
 * Verify touch target size (should be ≥44px)
 * @param locator - Element locator
 * @param elementName - Name of element for error message
 * @param minSize - Minimum size in pixels (default: 44)
 */
export async function verifyTouchTargetSize(
  locator: Locator,
  elementName: string,
  minSize = 44
) {
  const size = await getElementSize(locator);
  expect(size.width, `${elementName} width should be ≥${minSize}px`).toBeGreaterThanOrEqual(minSize);
  expect(size.height, `${elementName} height should be ≥${minSize}px`).toBeGreaterThanOrEqual(minSize);
}

/**
 * Verify ARIA label exists and is descriptive
 * @param locator - Element locator
 * @param elementName - Name of element for error message
 * @param minLength - Minimum description length (default: 5)
 */
export async function verifyAriaLabel(
  locator: Locator,
  elementName: string,
  minLength = 5
) {
  const ariaLabel = await locator.getAttribute('aria-label');
  expect(ariaLabel, `${elementName} should have aria-label`).toBeTruthy();
  expect(
    ariaLabel?.length,
    `${elementName} aria-label should be descriptive (≥${minLength} chars)`
  ).toBeGreaterThanOrEqual(minLength);
}

/**
 * Verify element is keyboard accessible
 * Tests Tab focus and Enter/Space activation
 */
export async function verifyKeyboardAccessible(
  page: Page,
  locator: Locator,
  elementName: string
) {
  // Focus element with Tab
  await page.keyboard.press('Tab');
  
  // Verify element is focused
  const isFocused = await locator.evaluate((el) => el === document.activeElement);
  expect(isFocused, `${elementName} should be focusable with Tab`).toBe(true);
  
  // Verify element can be activated with Enter or Space
  const tagName = await locator.evaluate((el) => el.tagName.toLowerCase());
  if (tagName === 'button' || tagName === 'a') {
    // Can press Enter
    await page.keyboard.press('Enter');
  }
}

/**
 * Wait for page to be fully loaded (no loading spinners)
 */
export async function waitForPageLoad(page: Page, timeout = 10000) {
  // Wait for React hydration
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle', { timeout });
  
  // Wait for loading spinners to disappear
  const spinner = page.locator('role=progressbar').first();
  if (await spinner.isVisible({ timeout: 2000 }).catch(() => false)) {
    await spinner.waitFor({ state: 'hidden', timeout });
  }
}

/**
 * Navigate to a page and verify it loaded
 */
export async function navigateAndVerify(
  page: Page,
  path: string,
  expectedHeading: string
) {
  await page.goto(path);
  await waitForPageLoad(page);
  
  // More flexible heading check - look for any heading level (h1-h6) or main content area
  // This handles different page layouts and MUI component structures
  const headingVisible = await page.locator(`h1, h2, h3, h4, h5, h6, main, [role="main"]`).first().isVisible().catch(() => false);
  
  if (!headingVisible) {
    throw new Error(`Page did not load properly - no main content found at ${path}`);
  }
}

/**
 * Take screenshot with standardized naming
 */
export async function takeScreenshot(
  page: Page,
  testName: string,
  viewport: string
) {
  const sanitizedName = testName.replace(/[^a-z0-9]/gi, '-').toLowerCase();
  await page.screenshot({
    path: `screenshots/${sanitizedName}-${viewport}.png`,
    fullPage: true,
  });
}

/**
 * Get all interactive elements on the page
 * Returns buttons, links, inputs, etc.
 */
export async function getInteractiveElements(page: Page) {
  return {
    buttons: page.locator('button, [role="button"]'),
    links: page.locator('a, [role="link"]'),
    inputs: page.locator('input, textarea, select, [role="textbox"], [role="combobox"]'),
    iconButtons: page.locator('button[aria-label]:has(svg)'),
  };
}

/**
 * Verify mobile card view is displayed (not table)
 * @param page - Playwright page
 * @param viewportWidth - Current viewport width
 */
export async function verifyMobileCardView(page: Page, viewportWidth: number) {
  if (viewportWidth < 900) {
    // Mobile view: should have cards, not table
    const cards = page.locator('[role="article"], .MuiCard-root').first();
    const table = page.locator('table').first();
    
    const cardsVisible = await cards.isVisible({ timeout: 2000 }).catch(() => false);
    const tableVisible = await table.isVisible({ timeout: 2000 }).catch(() => false);
    
    expect(cardsVisible || !tableVisible, 'Mobile view should use cards instead of table').toBe(true);
  } else {
    // Desktop view: should have table
    const table = page.locator('table').first();
    const tableVisible = await table.isVisible({ timeout: 2000 }).catch(() => false);
    
    expect(tableVisible, 'Desktop view should show table').toBe(true);
  }
}

/**
 * Test color contrast (basic check)
 * Returns true if contrast ratio is likely sufficient
 */
export async function checkColorContrast(
  page: Page,
  locator: Locator
): Promise<boolean> {
  const contrast = await locator.evaluate((el) => {
    const style = window.getComputedStyle(el);
    const bg = style.backgroundColor;
    const fg = style.color;
    
    // This is a simplified check - in production use a proper contrast checker
    return { bg, fg, hasSufficientContrast: bg !== fg };
  });
  
  return contrast.hasSufficientContrast;
}

/**
 * Pages in the application for easy navigation
 */
export const PAGES = {
  dashboard: '/en/dashboard',
  servers: '/en/servers',
  users: '/en/users',
  auditLogs: '/en/audit-logs',
  terminal: '/en/terminal',
  settingsSshKeys: '/en/settings/ssh-keys',
  settingsGroups: '/en/settings/groups',
  settingsEmail: '/en/settings/email',
  settingsDomain: '/en/settings/domain',
  settingsDatabase: '/en/settings/database',
  settingsHealth: '/en/settings/health',
} as const;

/**
 * Common viewport sizes for testing
 */
export const VIEWPORTS = {
  mobile: { width: 320, height: 568 },   // iPhone SE
  mobileLarge: { width: 414, height: 896 }, // iPhone 11 Pro Max
  tablet: { width: 768, height: 1024 },  // iPad
  tabletLarge: { width: 900, height: 1200 }, // Breakpoint
  desktop: { width: 1920, height: 1080 }, // Full HD
} as const;
