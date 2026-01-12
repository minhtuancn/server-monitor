# End-to-End Testing with Playwright

Comprehensive E2E test suite for Server Monitor application covering mobile responsive design, accessibility (ARIA), and touch target verification.

## 📋 Table of Contents

- [Overview](#overview)
- [Test Coverage](#test-coverage)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Writing New Tests](#writing-new-tests)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This test suite verifies:
- **Mobile Responsive Design**: All pages work at 320px-1920px viewports
- **Accessibility (ARIA)**: Interactive elements have proper ARIA labels
- **Keyboard Navigation**: Tab, Enter, Space, Escape key support
- **Touch Targets**: All interactive elements ≥44px × 44px
- **Screen Reader Support**: Proper landmarks and headings

**Total Tests**: 51+ automated tests  
**Browsers**: Chrome, Firefox, Safari  
**Devices**: iPhone SE (320px), iPhone 12, iPad, Desktop (1920px)

---

## 🧪 Test Coverage

### Mobile Responsive (16 tests)
- ✅ All 10 pages load at 320px width
- ✅ No horizontal scroll on any page
- ✅ Mobile cards replace tables on small screens
- ✅ Tabs are scrollable on mobile
- ✅ Forms are full-width and usable
- ✅ Navigation menu works on mobile

### Accessibility (20+ tests)
- ✅ All buttons have ARIA labels
- ✅ All icon buttons have descriptive labels
- ✅ Form inputs have proper ARIA attributes
- ✅ Keyboard navigation (Tab, Enter, Escape)
- ✅ Color picker is keyboard accessible
- ✅ No browser confirm() usage (uses ConfirmDialog)
- ✅ Screen reader support (landmarks, headings)

### Touch Targets (15+ tests)
- ✅ All buttons ≥44px × 44px
- ✅ Icon buttons meet minimum size
- ✅ Form inputs ≥40px height
- ✅ Adequate spacing between interactive elements
- ✅ Switches meet touch-friendly sizes

---

## 📦 Prerequisites

### System Requirements
- Node.js 18+ or 20+
- npm or yarn
- Server Monitor application running on `http://172.22.0.103:9081`

### Login Credentials
- **Username**: `admin`
- **Password**: `admin123`

---

## 🚀 Installation

```bash
# Navigate to e2e-tests directory
cd /opt/server-monitor/e2e-tests

# Install dependencies
npm install

# Install Playwright browsers (Chrome, Firefox, Safari)
npx playwright install

# Optional: Install system dependencies for browsers
npx playwright install-deps
```

---

## 🎮 Running Tests

### Quick Start

```bash
# Run all tests
npm test

# Run with HTML report generation
npm test -- --reporter=html
```

### Test by Category

```bash
# Mobile responsive tests only
npm run test:mobile

# Accessibility tests only
npm run test:accessibility

# Touch target tests only
npm run test:touch

# Specific viewport
npm test -- --project="Mobile Chrome (iPhone SE)"
```

### Debug Mode

```bash
# Interactive UI mode (recommended for development)
npm run test:ui

# Step-through debugger
npm run test:debug

# Run in headed mode (see browser)
npm run test:headed

# Specific test file
npm test tests/mobile-responsive.spec.ts
```

### View Reports

```bash
# Open HTML report (after running tests)
npm run report

# Generate and open report
npx playwright show-report
```

---

## 📁 Test Structure

```
e2e-tests/
├── playwright.config.ts          # Playwright configuration
├── package.json                   # Dependencies and scripts
├── fixtures/
│   └── test-auth.ts              # Authentication helpers
├── utils/
│   └── helpers.ts                # Utility functions
├── tests/
│   ├── mobile-responsive.spec.ts # Mobile responsive tests
│   ├── accessibility.spec.ts     # ARIA + keyboard tests
│   └── touch-targets.spec.ts     # Touch target verification
├── playwright-report/            # HTML test reports (generated)
└── test-results/                 # Test artifacts (generated)
```

### Key Files

#### `playwright.config.ts`
Main configuration file defining:
- Base URL (default: `http://172.22.0.103:9081`)
- Browser projects (Chrome, Firefox, Safari)
- Device viewports (iPhone SE, iPad, Desktop)
- Timeouts and retry settings
- Reporter configuration

#### `fixtures/test-auth.ts`
Authentication helpers:
- `authenticatedPage`: Fixture for logged-in tests
- `login()`: Manual login helper
- `logout()`: Logout helper

#### `utils/helpers.ts`
Utility functions:
- `verifyNoHorizontalScroll()`: Check for horizontal scroll
- `verifyAriaLabel()`: Verify ARIA label exists and is descriptive
- `verifyTouchTargetSize()`: Check element size ≥44px
- `verifyKeyboardAccessible()`: Test Tab and Enter keys
- `navigateAndVerify()`: Navigate and verify page loaded
- `getInteractiveElements()`: Get all buttons, links, inputs
- `PAGES`: Object with all page URLs
- `VIEWPORTS`: Common viewport sizes

---

## ✍️ Writing New Tests

### Example: Mobile Responsive Test

```typescript
import { test, expect } from '../fixtures/test-auth';
import { verifyNoHorizontalScroll, navigateAndVerify, PAGES, VIEWPORTS } from '../utils/helpers';

test.describe('New Page Tests', () => {
  test.use({ viewport: VIEWPORTS.mobile });

  test('New page is mobile responsive', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.newPage, 'Page Title');
    await verifyNoHorizontalScroll(page, 'New page');
    
    // Your assertions here
    const button = page.locator('button:has-text("Action")');
    await expect(button).toBeVisible();
  });
});
```

### Example: Accessibility Test

```typescript
import { test } from '../fixtures/test-auth';
import { verifyAriaLabel, navigateAndVerify, PAGES } from '../utils/helpers';

test('New page has ARIA labels', async ({ authenticatedPage: page }) => {
  await navigateAndVerify(page, PAGES.newPage, 'Page Title');
  
  const actionButton = page.locator('button:has-text("Action")');
  await verifyAriaLabel(actionButton, 'Action button');
});
```

### Example: Touch Target Test

```typescript
import { test } from '../fixtures/test-auth';
import { verifyTouchTargetSize, navigateAndVerify, PAGES, VIEWPORTS } from '../utils/helpers';

test.describe('Touch Targets', () => {
  test.use({ viewport: VIEWPORTS.mobile });

  test('Buttons are touch-friendly', async ({ authenticatedPage: page }) => {
    await navigateAndVerify(page, PAGES.newPage, 'Page Title');
    
    const button = page.locator('button:has-text("Action")');
    await verifyTouchTargetSize(button, 'Action button');
  });
});
```

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install dependencies
        working-directory: e2e-tests
        run: npm ci
      
      - name: Install Playwright browsers
        working-directory: e2e-tests
        run: npx playwright install --with-deps
      
      - name: Start application
        run: ./start-all.sh &
        
      - name: Wait for app to be ready
        run: npx wait-on http://localhost:9081
      
      - name: Run E2E tests
        working-directory: e2e-tests
        run: npm test
      
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: e2e-tests/playwright-report/
```

### Docker Integration

```dockerfile
FROM mcr.microsoft.com/playwright:v1.40.0-jammy

WORKDIR /app
COPY e2e-tests/package*.json ./
RUN npm ci

COPY e2e-tests/ ./
CMD ["npm", "test"]
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Tests Fail to Login
**Problem**: Authentication fails or times out

**Solutions**:
```bash
# Verify app is running
curl http://172.22.0.103:9081

# Check credentials in fixtures/test-auth.ts
# Default: admin / admin123

# Increase timeout in playwright.config.ts
use: {
  actionTimeout: 30 * 1000,
}
```

#### 2. Horizontal Scroll Detected
**Problem**: Page has horizontal scroll at 320px

**Solutions**:
- Check for fixed-width elements (use `max-width` instead)
- Verify images have `max-width: 100%`
- Check for `overflow-x: hidden` on body
- Inspect element with DevTools at 320px width

#### 3. Touch Target Too Small
**Problem**: Element is < 44px

**Solutions**:
```tsx
// Material-UI button fix
<IconButton sx={{ width: 44, height: 44 }}>
  <Icon />
</IconButton>

// Custom element fix
<div style={{ minWidth: 44, minHeight: 44, padding: 8 }}>
  Content
</div>
```

#### 4. Missing ARIA Labels
**Problem**: Test fails on ARIA label check

**Solutions**:
```tsx
// Button with aria-label
<Button aria-label="Descriptive action">Click</Button>

// IconButton with aria-label
<IconButton aria-label="Delete item">
  <DeleteIcon />
</IconButton>

// TextField with aria-label
<TextField
  inputProps={{ 'aria-label': 'Enter username' }}
/>

// Switch with aria-label
<Switch
  inputProps={{ 'aria-label': 'Enable notifications' }}
/>
```

#### 5. Tests are Flaky
**Problem**: Tests pass/fail randomly

**Solutions**:
```typescript
// Add proper waits
await page.waitForLoadState('networkidle');
await page.waitForSelector('button:has-text("Action")', { state: 'visible' });

// Use Playwright's auto-waiting
const button = page.locator('button:has-text("Action")');
await expect(button).toBeVisible(); // Auto-waits

// Increase timeout for slow operations
await page.click('button', { timeout: 30000 });
```

### Debug Tips

```bash
# Run single test with debug output
DEBUG=pw:api npm test tests/mobile-responsive.spec.ts

# Generate trace for failed tests
npm test -- --trace on

# View trace
npx playwright show-trace trace.zip

# Screenshot on failure (already configured)
# Check test-results/ directory for screenshots
```

---

## 📊 Test Reports

### HTML Report

After running tests, open the HTML report:

```bash
npm run report
```

The report shows:
- ✅ Passed tests (green)
- ❌ Failed tests (red)
- ⏭️ Skipped tests (yellow)
- ⏱️ Test duration
- 📸 Screenshots on failure
- 🎬 Videos on failure
- 📝 Test logs

### JSON Report

```bash
# Generate JSON report
npm test -- --reporter=json > test-results.json

# Use for custom reporting/analytics
```

---

## 🎯 Best Practices

### 1. Use Fixtures
```typescript
// Good: Use authenticatedPage fixture
test('Dashboard loads', async ({ authenticatedPage: page }) => {
  await page.goto('/dashboard');
});

// Avoid: Manual login in every test
```

### 2. Use Helper Functions
```typescript
// Good: Use helper
await verifyNoHorizontalScroll(page, 'Dashboard');

// Avoid: Manual check
const scrollWidth = await page.evaluate(() => document.body.scrollWidth);
// ... more code
```

### 3. Descriptive Test Names
```typescript
// Good
test('Servers page displays mobile cards at 320px width', async ({ page }) => {});

// Avoid
test('servers test', async ({ page }) => {});
```

### 4. Independent Tests
```typescript
// Good: Each test is independent
test('Test A', async ({ page }) => {
  await page.goto('/pageA');
  // test logic
});

test('Test B', async ({ page }) => {
  await page.goto('/pageB');
  // test logic
});

// Avoid: Tests depend on each other
```

### 5. Use Page Object Pattern (Optional)
```typescript
// pages/ServersPage.ts
export class ServersPage {
  constructor(private page: Page) {}
  
  async goto() {
    await this.page.goto('/servers');
  }
  
  async clickAddServer() {
    await this.page.click('button:has-text("Add Server")');
  }
}

// In test
const serversPage = new ServersPage(page);
await serversPage.goto();
await serversPage.clickAddServer();
```

---

## 📚 Resources

- [Playwright Documentation](https://playwright.dev)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [iOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Material-UI Accessibility](https://mui.com/material-ui/guides/accessibility/)

---

## 🤝 Contributing

When adding new features to Server Monitor:

1. **Add E2E tests** for new pages/components
2. **Verify mobile responsive** at 320px width
3. **Add ARIA labels** to all interactive elements
4. **Ensure touch targets** are ≥44px
5. **Test keyboard navigation** (Tab, Enter, Escape)
6. **Run full test suite** before committing

```bash
# Before committing
cd e2e-tests
npm test
```

---

## 📞 Support

If tests fail or you need help:

1. Check [Troubleshooting](#troubleshooting) section
2. Review test output and screenshots in `test-results/`
3. Run tests in headed mode: `npm run test:headed`
4. Run tests in debug mode: `npm run test:debug`
5. Check Playwright docs: https://playwright.dev

---

## ✅ Test Checklist

Before releasing new features:

- [ ] All 51+ E2E tests pass
- [ ] New features have E2E tests
- [ ] Mobile responsive at 320px-1920px
- [ ] All interactive elements have ARIA labels
- [ ] Touch targets meet 44px minimum
- [ ] Keyboard navigation works
- [ ] No horizontal scroll on mobile
- [ ] HTML report shows all green ✅

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-12  
**Maintained by**: Server Monitor Team
