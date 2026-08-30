import { assertNoOverflow, expect, gatherCategoryLinks, test, VIEWPORTS } from "./helpers"

const PUBLIC_ROUTES = ["/", "/aif", "/clf", "/saa", "/aif/services", "/login", "/register"]

test.describe("Given an anonymous visitor on public routes", () => {
  for (const route of PUBLIC_ROUTES) {
    test(`When navigating to ${route} — Then HTTP 200 with zero errors`, async ({
      page,
      pageErrors,
    }) => {
      const response = await page.goto(route)
      expect(response?.status()).toBe(200)
      await expect(page.locator("body")).toBeVisible()
      expect(pageErrors).toEqual([])
    })
  }

  for (const vp of VIEWPORTS) {
    test.describe(`at ${vp.label} (${vp.width}px)`, () => {
      test.use({ viewport: { width: vp.width, height: vp.height } })

      for (const route of PUBLIC_ROUTES) {
        test(`When visiting ${route} — Then no horizontal overflow`, async ({ page }) => {
          await page.goto(route)
          await assertNoOverflow(page)
        })
      }
    })
  }
})

test.describe("Given the responsive site header", () => {
  test("When viewed on desktop — Then the full navigation replaces the menu button", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 1280, height: 800 })
    await page.goto("/")

    await expect(page.getByRole("navigation", { name: "자격증 탐색" })).toBeVisible()
    await expect(page.getByRole("button", { name: "메뉴 열기" })).toBeHidden()
  })

  test("When viewed on mobile — Then the menu button replaces the full navigation", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await page.goto("/")

    await expect(page.getByRole("navigation", { name: "자격증 탐색" })).toBeHidden()
    await expect(page.getByRole("button", { name: "메뉴 열기" })).toBeVisible()
  })
})

test.describe("Given an anonymous visitor on protected routes", () => {
  test("When navigating to /dashboard — Then redirected to /login", async ({ page }) => {
    await page.goto("/dashboard")
    await expect(page).toHaveURL(/\/login/)
  })

  test("When navigating to /aif/quiz — Then redirected to /login", async ({ page }) => {
    await page.goto("/aif/quiz")
    await expect(page).toHaveURL(/\/login/)
  })

  test("When navigating to /clf/quiz — Then redirected to /login", async ({ page }) => {
    await page.goto("/clf/quiz")
    await expect(page).toHaveURL(/\/login/)
  })

  test("When navigating to /saa/quiz — Then redirected to /login", async ({ page }) => {
    await page.goto("/saa/quiz")
    await expect(page).toHaveURL(/\/login/)
  })
})

test.describe("Given an authentication form before hydration", () => {
  for (const route of ["/login", "/register"]) {
    test(`When ${route} renders — Then native fallback never puts credentials in the URL`, async ({
      page,
    }) => {
      await page.goto(route)

      await expect(page.locator("form.form-card")).toHaveAttribute("method", "post")
    })
  }
})

test.describe("Given an anonymous visitor on study notes", () => {
  test("When visiting AIF study notes — Then articles render without login", async ({
    page,
    pageErrors,
  }) => {
    const links = await gatherCategoryLinks(page, "aif")
    expect(links.length).toBeGreaterThan(0)
    for (const href of links) {
      const response = await page.goto(href)
      expect(response?.status(), `${href} returned non-200`).toBe(200)
      await expect(page.locator("article.prose")).toBeVisible()
    }
    expect(pageErrors).toEqual([])
  })
})

test.describe("Given an anonymous visitor on the home page", () => {
  test("When visiting / — Then hero title is 'AWS Study' and no 'Study Hub'", async ({
    page,
    pageErrors,
  }) => {
    await page.goto("/")
    await expect(page.locator(".hero h1")).toHaveText("AWS Study")
    const bodyText = await page.locator("body").textContent()
    expect(bodyText).not.toContain("Study Hub")
    expect(pageErrors).toEqual([])
  })

  test("When visiting / — Then hero has no eyebrow or descriptive paragraph", async ({ page }) => {
    await page.goto("/")
    await expect(page.locator(".hero .eyebrow")).toHaveCount(0)
    await expect(page.locator(".hero .hero-copy")).toHaveCount(0)
  })

  test("When visiting / — Then service map flow is visible with stages", async ({ page }) => {
    await page.goto("/")
    await expect(page.locator(".smap")).toBeVisible()
    const stages = page.locator(".smap-stage")
    expect(await stages.count()).toBe(5)
    const nodes = page.locator(".smap-node")
    await expect(nodes.first()).toBeVisible()
  })
})

test.describe("Given an anonymous visitor on the service map", () => {
  test("When visiting /aif/services — Then 5 stages and 18 nodes render", async ({
    page,
    pageErrors,
  }) => {
    await page.goto("/aif/services")
    const stages = page.locator(".smap-stage")
    expect(await stages.count()).toBe(5)
    const nodes = page.locator(".smap-node")
    expect(await nodes.count()).toBe(18)
    expect(pageErrors).toEqual([])
  })

  test("When clicking a service node — Then navigates to study page", async ({ page }) => {
    await page.goto("/aif/services")
    const firstNode = page.locator(".smap-node").first()
    const href = await firstNode.getAttribute("href")
    expect(href).toMatch(/^\/aif\/study\//)
    await firstNode.click()
    await expect(page).toHaveURL(/\/aif\/study\//)
  })

  test("When checking SageMaker node — Then links to /aif/study/sagemaker", async ({ page }) => {
    await page.goto("/aif/services")
    const smNode = page.locator(".smap-node", { hasText: "SageMaker AI" })
    await expect(smNode).toBeVisible()
    const href = await smNode.getAttribute("href")
    expect(href).toBe("/aif/study/sagemaker")
  })
})
