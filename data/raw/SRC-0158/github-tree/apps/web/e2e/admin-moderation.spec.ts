import { ADMIN_EMAIL, ADMIN_PASSWORD, expect, login, registerApplicant, test } from "./helpers"

test.describe("Given an admin with pending account requests", () => {
  test("When approving and rejecting requests — Then each processed row leaves the queue", async ({
    page,
    request,
    pageErrors,
  }) => {
    const approved = await registerApplicant(request, "Approve")
    const rejected = await registerApplicant(request, "Reject")
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)
    await page.goto("/admin")

    const approvedRow = page.locator(".moderation-row", { hasText: approved.email })
    const rejectedRow = page.locator(".moderation-row", { hasText: rejected.email })
    const approveRequestPromise = page.waitForRequest(
      (request) => request.url().endsWith("/approve") && request.method() === "PATCH",
    )
    await approvedRow.getByRole("button", { name: "승인" }).click()
    const approveRequest = await approveRequestPromise
    expect(approveRequest.headers()["content-type"]).toBe("application/json")
    await expect(approvedRow).toHaveCount(0)
    const rejectRequestPromise = page.waitForRequest(
      (request) => request.url().endsWith("/reject") && request.method() === "PATCH",
    )
    await rejectedRow.getByRole("button", { name: "거부" }).click()
    const rejectRequest = await rejectRequestPromise
    expect(rejectRequest.headers()["content-type"]).toBe("application/json")
    await expect(rejectedRow).toHaveCount(0)
    await expect(page.getByRole("status")).toContainText("처리했습니다")
    expect(pageErrors).toEqual([])
  })

  test("When another admin already processed a request — Then the stale row is removed", async ({
    page,
    request,
    pageErrors,
  }) => {
    const applicant = await registerApplicant(request, "AlreadyProcessed")
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)
    await page.route(/\/api\/admin\/users\/[^/]+\/approve$/, async (route) => {
      await route.fulfill({ status: 404, contentType: "application/json", body: "{}" })
    })
    await page.goto("/admin")

    const row = page.locator(".moderation-row", { hasText: applicant.email })
    await row.getByRole("button", { name: "승인" }).click()

    await expect(row).toHaveCount(0)
    await expect(page.getByRole("status")).toContainText("이미 처리되었습니다")
    expect(pageErrors).toEqual([expect.stringContaining("404 (Not Found)")])
  })

  test("When a moderation response is uncertain — Then the queue is refreshed", async ({
    page,
    request,
    pageErrors,
  }) => {
    const applicant = await registerApplicant(request, "Uncertain")
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)
    await page.route(/\/api\/admin\/users\/[^/]+\/reject$/, async (route) => {
      await route.abort("failed")
    })
    await page.goto("/admin")

    const row = page.locator(".moderation-row", { hasText: applicant.email })
    await row.getByRole("button", { name: "거부" }).click()

    await expect(row).toBeVisible()
    await expect(page.locator(".moderation-panel .error-text")).toContainText(
      "신청 목록을 새로 고쳤습니다",
    )
    expect(pageErrors).toEqual([expect.stringContaining("ERR_FAILED")])
  })
})
