import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  // WebKit/Chromium font rasterization varies slightly between Apple Silicon
  // and GitHub's Intel macOS runners. Keep a tight whole-page budget while
  // the assertions below continue to validate the layout geometry directly.
  expect: { toHaveScreenshot: { maxDiffPixelRatio: 0.03 } },
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:8765',
    locale: 'ko-KR',
    timezoneId: 'Asia/Seoul',
  },
  webServer: {
    command: 'bun run build && PERSONA_ROOT=.. uv run --project ../backend uvicorn oh_my_persona.presentation.app:app --host 127.0.0.1 --port 8765',
    url: 'http://127.0.0.1:8765/healthz',
    reuseExistingServer: true,
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 1000 } } },
    { name: 'mobile', use: { ...devices['iPhone 15'], browserName: 'chromium' } },
  ],
});
