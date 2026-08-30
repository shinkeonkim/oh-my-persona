const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/ui',
  timeout: 30000,
  expect: { toHaveScreenshot: { maxDiffPixelRatio: 0.01 } },
  use: { baseURL: 'http://127.0.0.1:8765', locale: 'ko-KR', timezoneId: 'Asia/Seoul' },
  webServer: {
    command: 'uv run uvicorn oh_my_persona.api:app --host 127.0.0.1 --port 8765',
    url: 'http://127.0.0.1:8765/healthz',
    reuseExistingServer: true,
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 1000 } } },
    { name: 'mobile', use: { ...devices['iPhone 15'], browserName: 'chromium' } },
  ],
});
