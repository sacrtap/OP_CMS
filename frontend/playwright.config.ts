/**
 * Playwright E2E Test Configuration
 * Epic 1: 客户信息管理模块
 */

import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
const baseURL = process.env.BASE_URL || 'http://localhost:5173';
const environment = process.env.TEST_ENV || 'local';

console.log(`\n✅ Running E2E tests against: ${baseURL}`);
console.log(`📋 Environment: ${environment.toUpperCase()}\n`);

export default defineConfig({
  testDir: './e2e/tests',
  outputDir: './test-results/e2e',
  
  // Timeout settings
  timeout: 60000,
  expect: { timeout: 10000 },
  
  // Parallel execution
  fullyParallel: true,
  workers: environment === 'ci' ? 1 : undefined,
  
  // Retry settings
  retries: environment === 'ci' ? 2 : 0,
  
  // Reporter configuration
  reporter: [
    ['html', { 
      outputFolder: path.resolve(__dirname, '../../playwright-report'),
      open: 'never' 
    }],
    ['junit', { 
      outputFile: path.resolve(__dirname, '../../test-results/e2e/results.xml') 
    }],
    ['list', { printSteps: true }],
  ],
  
  // Shared settings for all browsers
  use: {
    // Timeouts
    actionTimeout: 15000,
    navigationTimeout: 30000,
    
    // Tracing and screenshots
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // Base options
    baseURL,
    headless: true,
  },
  
  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  
  // Web server configuration for local testing
  webServer: environment === 'local' ? {
    command: 'bun run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
    timeout: 120000,
    stdout: 'pipe',
    stderr: 'pipe',
  } : undefined,
});
