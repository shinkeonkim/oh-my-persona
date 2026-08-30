import { ADMIN_EMAIL, ADMIN_PASSWORD, expect, login, test } from "./helpers"

test.describe("Given authentication-aware navigation", () => {
  test("When a visitor has a malformed session cookie — Then public pages remain available", async ({
    page,
    pageErrors,
  }) => {
    await page.context().addCookies([
      {
        name: "aws_study_session",
        value: "malformed-token",
        domain: "localhost",
        path: "/",
      },
    ])

    const response = await page.goto("/")
    expect(response?.status()).toBe(200)
    await expect(page.getByRole("link", { name: "로그인" })).toBeVisible()
    expect(pageErrors).toEqual([])
  })

  test("When an admin logs out — Then protected links disappear and Login returns", async ({
    page,
    pageErrors,
  }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)

    await expect(page.getByRole("link", { name: "관리자" })).toBeVisible()
    await expect(page.getByRole("link", { name: "로그인" })).toBeHidden()
    const logoutRequestPromise = page.waitForRequest(
      (request) => request.url().endsWith("/api/auth/logout") && request.method() === "POST",
    )
    await page.getByRole("button", { name: "로그아웃" }).click()
    const logoutRequest = await logoutRequestPromise

    expect(logoutRequest.headers()["content-type"]).toBe("application/json")
    await expect(page).toHaveURL("/")
    await expect(page.getByRole("link", { name: "로그인" })).toBeVisible()
    await expect(page.getByRole("link", { name: "대시보드" })).toBeHidden()
    expect(pageErrors).toEqual([])
  })
})
