import { type APIRequestContext, test as base, expect, type Page } from "@playwright/test"

export const ADMIN_EMAIL = process.env["ADMIN_EMAIL"] ?? "admin@example.com"
export const ADMIN_PASSWORD = process.env["ADMIN_PASSWORD"] ?? "local-admin-password"
export const APPLICANT_PASSWORD = "applicant-password"

export const CERTS = ["aif", "clf", "saa"] as const

export const VIEWPORTS = [
  { width: 375, height: 812, label: "mobile" },
  { width: 768, height: 1024, label: "tablet" },
  { width: 1280, height: 800, label: "desktop" },
] as const

export const test = base.extend<{ pageErrors: string[] }>({
  pageErrors: async ({ page }, use) => {
    const errors: string[] = []
    page.on("pageerror", (error) => errors.push(`[page] ${error.message}`))
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(`[console] ${msg.text()}`)
    })
    await use(errors)
  },
})

export async function login(page: Page, email: string, password: string): Promise<void> {
  await page.goto("/login")
  await page.getByLabel("이메일").fill(email)
  await page.getByLabel("비밀번호").fill(password)
  await page.getByRole("button", { name: "로그인" }).click()
  await page.waitForURL("/dashboard")
}

export async function registerApplicant(
  request: APIRequestContext,
  label: string,
): Promise<{ readonly email: string; readonly displayName: string }> {
  const unique = crypto.randomUUID()
  const applicant = {
    email: `${label}-${unique}@example.com`,
    displayName: `${label} ${unique.slice(0, 8)}`,
  }
  const response = await request.post("http://localhost:3001/api/auth/register", {
    data: { ...applicant, password: APPLICANT_PASSWORD },
  })
  expect(response.status()).toBe(201)
  return applicant
}

export async function loginApplicant(page: Page, email: string): Promise<void> {
  await page.goto("/login")
  await page.getByLabel("이메일").fill(email)
  await page.getByLabel("비밀번호").fill(APPLICANT_PASSWORD)
  await page.getByRole("button", { name: "로그인" }).click()
}

export async function assertNoOverflow(page: Page): Promise<void> {
  const overflows = await page.evaluate(() => {
    return document.documentElement.scrollWidth > document.documentElement.clientWidth
  })
  expect(overflows).toBe(false)
}

export async function gatherCategoryLinks(page: Page, cert: string): Promise<string[]> {
  await page.goto(`/${cert}`)
  await page.waitForSelector(".category-link")
  return page.$$eval(".category-link", (anchors) =>
    anchors.map((a) => a.getAttribute("href")).filter((h): h is string => h !== null),
  )
}

export { expect }
