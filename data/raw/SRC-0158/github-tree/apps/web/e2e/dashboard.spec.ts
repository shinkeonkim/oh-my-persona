import { ADMIN_EMAIL, ADMIN_PASSWORD, expect, login, test } from "./helpers"

test.describe("Given admin credentials", () => {
  test("When logging in — Then redirected to dashboard", async ({ page, pageErrors }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)
    await expect(page).toHaveURL("/dashboard")
    expect(pageErrors).toEqual([])
  })
})

test.describe("Given a logged-in admin on the dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)
  })

  test("When visiting /dashboard — Then progress metrics render", async ({ page, pageErrors }) => {
    await page.goto("/dashboard")
    await expect(page.locator(".metric-strip")).toBeVisible()
    await expect(page.getByText("풀이 기록", { exact: true })).toBeVisible()
    await expect(page.getByText("최근 정답", { exact: true })).toBeVisible()
    await expect(page.getByText("정확도", { exact: true })).toBeVisible()
    expect(pageErrors).toEqual([])
  })

  test("When visiting /dashboard — Then certification records section renders", async ({
    page,
    pageErrors,
  }) => {
    await page.goto("/dashboard")
    await expect(page.getByText("자격증별 기록")).toBeVisible()
    expect(pageErrors).toEqual([])
  })
})
