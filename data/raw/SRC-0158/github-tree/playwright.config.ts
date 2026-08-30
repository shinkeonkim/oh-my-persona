import { defineConfig, devices } from "@playwright/test"

const isCI = Boolean(process.env["CI"])

export default defineConfig({
  testDir: "apps/web/e2e",
  timeout: 120_000,
  fullyParallel: true,
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
  workers: isCI ? 1 : undefined,
  reporter: "list",
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: [
    {
      command: "bun --env-file=.env.example --env-file=.env run --filter '@aws-study/api' dev",
      url: "http://localhost:3001/healthz",
      reuseExistingServer: !isCI,
      timeout: 120_000,
    },
    {
      command: "bun --env-file=.env.example --env-file=.env run --filter '@aws-study/web' dev",
      url: "http://localhost:3000",
      reuseExistingServer: !isCI,
      timeout: 120_000,
    },
  ],
})
