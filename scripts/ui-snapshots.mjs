#!/usr/bin/env node

/**
 * UI Screenshots Script
 * 
 * Captures screenshots of key UI pages using Playwright for documentation and review purposes.
 * This script is used by the manual-project-review workflow to capture the current state of the UI.
 */

import { chromium } from 'playwright';
import { existsSync, mkdirSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuration
const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:9081';
const AUTH_USER = process.env.AUTH_USER || 'admin';
const AUTH_PASS = process.env.AUTH_PASS || 'admin123';
const OUTPUT_DIR = process.env.OUTPUT_DIR || join(__dirname, '..', 'docs', 'screenshots');
const TIMEOUT = 30000; // 30 seconds

// Pages to screenshot
const PAGES = [
  { path: '/vi', name: 'homepage', description: 'Homepage' },
  { path: '/vi/dashboard', name: 'dashboard', description: 'Dashboard', requiresAuth: true },
  { path: '/vi/servers', name: 'servers', description: 'Server List', requiresAuth: true },
  { path: '/vi/settings/integrations/webhooks', name: 'webhooks', description: 'Webhook Settings', requiresAuth: true },
  { path: '/vi/audit-logs', name: 'audit-logs', description: 'Audit Logs', requiresAuth: true },
  { path: '/vi/settings/profile', name: 'profile', description: 'User Profile', requiresAuth: true },
  { path: '/vi/settings/security', name: 'security', description: 'Security Settings', requiresAuth: true },
];

/**
 * Main function to capture screenshots
 */
async function captureScreenshots() {
  console.log('🖼️  Starting UI screenshot capture...');
  console.log(`📍 Base URL: ${BASE_URL}`);
  console.log(`📁 Output directory: ${OUTPUT_DIR}`);

  // Ensure output directory exists
  if (!existsSync(OUTPUT_DIR)) {
    mkdirSync(OUTPUT_DIR, { recursive: true });
    console.log(`✅ Created output directory: ${OUTPUT_DIR}`);
  }

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) Playwright/1.40.0 Screenshot Bot',
    locale: 'vi-VN',
    timezoneId: 'Asia/Ho_Chi_Minh',
  });

  const page = await context.newPage();
  
  // Set default timeout
  page.setDefaultTimeout(TIMEOUT);

  const results = [];
  let authenticated = false;

  try {
    // Check if server is accessible
    console.log(`🔍 Checking if ${BASE_URL} is accessible...`);
    try {
      const response = await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: TIMEOUT });
      if (!response || !response.ok()) {
        throw new Error(`Server returned status ${response?.status() || 'unknown'}`);
      }
      console.log(`✅ Server is accessible`);
    } catch (error) {
      console.error(`❌ Failed to access ${BASE_URL}: ${error.message}`);
      throw new Error(`Server is not accessible. Please ensure the server is running at ${BASE_URL}`);
    }

    for (const pageInfo of PAGES) {
      const { path, name, description, requiresAuth } = pageInfo;
      
      console.log(`\n📸 Capturing: ${description} (${path})`);
      
      try {
        // Authenticate if needed and not already authenticated
        if (requiresAuth && !authenticated) {
          console.log('🔐 Attempting authentication...');
          
          // Go to login page
          await page.goto(`${BASE_URL}/vi/login`, { waitUntil: 'networkidle', timeout: TIMEOUT });
          
          // Fill in credentials
          await page.fill('input[name="username"], input[type="text"]', AUTH_USER);
          await page.fill('input[name="password"], input[type="password"]', AUTH_PASS);
          
          // Submit form
          await page.click('button[type="submit"]');
          
          // Wait for navigation to complete
          await page.waitForURL(`${BASE_URL}/vi/dashboard`, { timeout: TIMEOUT });
          
          authenticated = true;
          console.log('✅ Authentication successful');
        }
        
        // Navigate to page
        const url = `${BASE_URL}${path}`;
        await page.goto(url, { waitUntil: 'networkidle', timeout: TIMEOUT });
        
        // Wait a bit for any animations or lazy loading
        await page.waitForTimeout(2000);
        
        // Take screenshot
        const filename = `${name}.png`;
        const filepath = join(OUTPUT_DIR, filename);
        await page.screenshot({ 
          path: filepath, 
          fullPage: true,
          timeout: TIMEOUT 
        });
        
        console.log(`✅ Screenshot saved: ${filename}`);
        results.push({
          page: description,
          path,
          filename,
          status: 'success'
        });
        
      } catch (error) {
        console.error(`❌ Failed to capture ${description}: ${error.message}`);
        results.push({
          page: description,
          path,
          filename: null,
          status: 'failed',
          error: error.message
        });
      }
    }
    
  } catch (error) {
    console.error(`\n❌ Critical error: ${error.message}`);
    throw error;
  } finally {
    await browser.close();
  }

  // Generate summary
  console.log('\n📊 Screenshot Capture Summary:');
  console.log('═'.repeat(60));
  
  const successful = results.filter(r => r.status === 'success').length;
  const failed = results.filter(r => r.status === 'failed').length;
  
  console.log(`✅ Successful: ${successful}/${results.length}`);
  console.log(`❌ Failed: ${failed}/${results.length}`);
  
  results.forEach(result => {
    const icon = result.status === 'success' ? '✅' : '❌';
    console.log(`${icon} ${result.page} - ${result.status}`);
    if (result.error) {
      console.log(`   Error: ${result.error}`);
    }
  });
  
  // Generate markdown summary
  const summaryPath = join(OUTPUT_DIR, 'screenshot-summary.md');
  const markdown = generateMarkdownSummary(results);
  writeFileSync(summaryPath, markdown, 'utf-8');
  console.log(`\n📝 Summary saved: ${summaryPath}`);
  
  // Exit with error if any screenshots failed
  if (failed > 0) {
    console.log(`\n⚠️  Warning: ${failed} screenshot(s) failed`);
    process.exit(1);
  }
  
  console.log('\n🎉 All screenshots captured successfully!');
}

/**
 * Generate markdown summary of screenshot results
 */
function generateMarkdownSummary(results) {
  const timestamp = new Date().toISOString();
  
  let markdown = `# UI Screenshots Summary\n\n`;
  markdown += `**Generated:** ${timestamp}\n\n`;
  markdown += `## Results\n\n`;
  
  const successful = results.filter(r => r.status === 'success');
  const failed = results.filter(r => r.status === 'failed');
  
  markdown += `- ✅ Successful: ${successful.length}\n`;
  markdown += `- ❌ Failed: ${failed.length}\n`;
  markdown += `- 📊 Total: ${results.length}\n\n`;
  
  if (successful.length > 0) {
    markdown += `## Captured Screenshots\n\n`;
    successful.forEach(result => {
      markdown += `### ${result.page}\n\n`;
      markdown += `- Path: \`${result.path}\`\n`;
      markdown += `- File: \`${result.filename}\`\n\n`;
      markdown += `![${result.page}](${result.filename})\n\n`;
    });
  }
  
  if (failed.length > 0) {
    markdown += `## Failed Screenshots\n\n`;
    failed.forEach(result => {
      markdown += `### ${result.page}\n\n`;
      markdown += `- Path: \`${result.path}\`\n`;
      markdown += `- Error: ${result.error}\n\n`;
    });
  }
  
  return markdown;
}

// Run the script
captureScreenshots().catch(error => {
  console.error('\n💥 Fatal error:', error);
  process.exit(1);
});
