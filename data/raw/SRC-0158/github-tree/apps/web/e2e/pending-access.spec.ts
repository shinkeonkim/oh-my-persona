import { expect, loginApplicant, registerApplicant, test } from "./helpers"

test.describe("Given a pending account", () => {
  test("When opening protected routes — Then approval guidance replaces server errors", async ({
    page,
    request,
    pageErrors,
  }) => {
    const applicant = await registerApplicant(request, "Pending")
    await loginApplicant(page, applicant.email)

    await expect(page).toHaveURL("/")
    await expect(page.getByText("승인 대기", { exact: true })).toBeVisible()
    await expect(page.getByRole("button", { name: "로그아웃" })).toBeVisible()
    await expect(page.getByRole("link", { name: "로그인" })).toBeHidden()
    await expect(page.getByRole("link", { name: "관리자" })).toBeHidden()

    await page.goto("/dashboard")
    await expect(page.getByRole("heading", { name: "계정 승인을 기다리고 있습니다" })).toBeVisible()
    await page.goto("/saa/quiz")
    await expect(page.getByRole("heading", { name: "계정 승인을 기다리고 있습니다" })).toBeVisible()
    await page.goto("/admin")
    await expect(page).toHaveURL("/")
    expect(pageErrors).toEqual([])
  })
})
