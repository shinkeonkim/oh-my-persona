import { ADMIN_EMAIL, ADMIN_PASSWORD, CERTS, expect, login, test } from "./helpers"

test.describe("Given a logged-in user on quiz pages", () => {
  test.describe.configure({ mode: "serial" })

  test.beforeEach(async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASSWORD)
  })

  for (const cert of CERTS) {
    test(`When visiting /${cert}/quiz — Then the lobby renders before any question`, async ({
      page,
      pageErrors,
    }) => {
      await page.goto(`/${cert}/quiz`)
      await expect(page.getByRole("heading", { name: /문제 유형 연습/ })).toBeVisible()
      await expect(page.getByRole("heading", { name: "학습 진도" })).toBeVisible()
      await expect(page.getByRole("heading", { name: /카테고리/ })).toBeVisible()
      await expect(page.locator(".quiz-option")).toHaveCount(0)
      expect(pageErrors).toEqual([])
    })
  }

  test("When configuring one sequential question — Then the session reaches category results", async ({
    page,
    pageErrors,
  }) => {
    await page.goto("/aif/quiz")
    const selectAll = page.getByRole("button", { name: "전체 선택" })
    if (await selectAll.isVisible()) await selectAll.click()
    await page.getByRole("radio", { name: "순차" }).check()
    await page.getByRole("radio", { name: /커스텀/ }).check()
    await page.getByRole("spinbutton", { name: "커스텀 문항 수" }).fill("1")
    await page.getByRole("button", { name: /시작/ }).click()

    await expect(page.locator(".quiz-option").first()).toBeVisible()
    await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0)
    await expect(page.locator(".quiz-session-header")).toContainText("1 / 1")
    await page.locator(".quiz-option").first().click()
    await page.getByRole("button", { name: /정답 확인/ }).click()
    await expect(page.locator(".quiz-explanation")).toBeVisible()
    await page.getByRole("button", { name: "결과 보기" }).click()
    await expect(page.getByRole("heading", { name: "세션 완료" })).toBeVisible()
    await expect(page.getByRole("heading", { name: "카테고리별 결과" })).toBeVisible()
    expect(pageErrors).toEqual([])
  })

  test("When changing lobby settings — Then they persist after reload", async ({ page }) => {
    await page.goto("/clf/quiz")
    const ten = page.getByRole("radio", { name: "10", exact: true })
    const targetLimit = (await ten.isChecked()) ? 25 : 10
    const saved = page.waitForResponse(
      (response) => response.url().includes("/api/quiz/preferences") && response.status() === 204,
    )
    await page.getByRole("radio", { name: String(targetLimit), exact: true }).check()
    await saved
    await page.reload()
    await expect(page.getByRole("radio", { name: String(targetLimit), exact: true })).toBeChecked()
  })

  test("When all categories are cleared — Then session start is disabled", async ({ page }) => {
    await page.goto("/saa/quiz")
    const selectAll = page.getByRole("button", { name: "전체 선택" })
    if (await selectAll.isVisible()) await selectAll.click()
    await page.getByRole("button", { name: "전체 해제" }).click()
    await expect(page.getByRole("button", { name: /조건에 맞는 문항이 없습니다/ })).toBeDisabled()
  })

  test("When the session API receives invalid input — Then it returns HTTP 400", async ({
    page,
  }) => {
    const responses = await Promise.all([
      page.request.post("http://localhost:3001/api/quiz/sessions", {
        data: {
          certificationCode: "aif",
          mode: "all",
          order: "random",
          questionLimit: 0,
          categorySlugs: [],
          parentSessionId: null,
        },
      }),
      page.request.post("http://localhost:3001/api/quiz/attempts", {
        data: { sessionId: "invalid", questionId: "invalid", selectedAnswers: ["A"] },
      }),
    ])
    expect(responses.map((response) => response.status())).toEqual([400, 400])
  })
})

test.describe("Given an anonymous user on quiz pages", () => {
  for (const cert of CERTS) {
    test(`When navigating to /${cert}/quiz — Then redirected to login`, async ({ page }) => {
      await page.goto(`/${cert}/quiz`)
      await expect(page).toHaveURL(/\/login/)
    })
  }
})
