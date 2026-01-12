import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration for Server Monitor v2.4.0
 * 
 * Test Coverage:
 * - Mobile responsive design (320px - 1920px viewports)
 * - Accessibility (ARIA labels, keyboard navigation)
 * - Touch target verification (≥44px)
 * - Visual regression testing
 */

export default defineConfig({
  testDir: './tests',
  
  // Maximum time one test can run for
  timeout: 60 * 1000,
  
  // Run tests in files in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Reporter to use
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['list']
  ],
  
  // Shared settings for all the projects below
  use: {
    // Base URL for the application
    baseURL: process.env.BASE_URL || 'http://172.22.0.103:9081',
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video on failure
    video: 'retain-on-failure',
    
    // Maximum time each action can take
    actionTimeout: 15 * 1000,
    
    // Ignore HTTPS errors (for local development)
    ignoreHTTPSErrors: true,
  },

  // Configure projects for major browsers and viewports
  projects: [
    // Desktop browsers
    {
      name: 'Desktop Chrome',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 }
      },
    },
    {
      name: 'Desktop Firefox',
      use: { 
        ...devices['Desktop Firefox'],
        viewport: { width: 1920, height: 1080 }
      },
    },
    {
      name: 'Desktop Safari',
      use: { 
        ...devices['Desktop Safari'],
        viewport: { width: 1920, height: 1080 }
      },
    },

    // Mobile devices - Critical for mobile responsive testing
    {
      name: 'Mobile Chrome (iPhone SE)',
      use: {
        ...devices['iPhone SE'],
        // iPhone SE has 375x667 viewport, but we test at 320px minimum
        viewport: { width: 320, height: 568 }
      },
    },
    {
      name: 'Mobile Chrome (iPhone 12)',
      use: { ...devices['iPhone 12'] },
    },
    {
      name: 'Mobile Chrome (Pixel 5)',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari (iPad)',
      use: { ...devices['iPad Pro'] },
    },

    // Tablet viewports
    {
      name: 'Tablet (768px)',
      use: {
        ...devices['iPad Mini'],
        viewport: { width: 768, height: 1024 }
      },
    },
    {
      name: 'Tablet (900px)',
      use: {
        viewport: { width: 900, height: 1200 },
        userAgent: 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
      },
    },
  ],

  // Run your local dev server before starting the tests
  webServer: process.env.CI ? undefined : {
    command: 'cd ../frontend-next && npm run dev',
    url: 'http://172.22.0.103:9081',
    reuseExistingServer: true,
    timeout: 120 * 1000,
  },
});
