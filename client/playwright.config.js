// RMIT University Vietnam
// Course: COSC2767 Systems Deployment and Operations
// Semester: 2026B
// Assessment: Assignment 2
// Author: Ngo Hoang Long
// ID: s4142456
// Created date: 03/09/2026
// Last modified: 03/09/2026
// Acknowledgement: Playwright documentation.

// import helpers
import { defineConfig, devices } from '@playwright/test'

// define test configurations
export default defineConfig({
  testDir: './tests/e2e', // location of end-to-end test files
  timeout: 30_000,
  use: {
    baseURL: 'http://localhost:5173', // address of locally run Vue app
    trace: 'on-first-retry',    // record a trace - detailed test information only when test fail and retry
    screenshot: 'only-on-failure', // screenshot broswer screens only when test fail
  },
  // test results format
  reporter: [
    ['list'],
    ['html', { outputFolder: 'reports/playwright-report' }], //.html report for visual inspection
    ['junit', { outputFile: 'reports/playwright-junit.xml' }], // junit for Jenkins test results publish
  ],
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})