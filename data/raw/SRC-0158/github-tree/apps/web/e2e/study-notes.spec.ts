import { assertNoOverflow, expect, gatherCategoryLinks, test, VIEWPORTS } from "./helpers"

const ALL_CERTS = ["aif", "clf", "saa"] as const

for (const cert of ALL_CERTS) {
  test.describe(`Given ${cert.toUpperCase()} study notes (anonymous, all public)`, () => {
    const studyLinks: string[] = []

    test.beforeAll(async ({ browser }) => {
      const page = await browser.newPage()
      studyLinks.push(...(await gatherCategoryLinks(page, cert)))
      await page.close()
    })

    test("When gathering category links — Then at least one exists", () => {
      expect(studyLinks.length).toBeGreaterThan(0)
    })

    for (const vp of VIEWPORTS) {
      test.describe(`at ${vp.label} (${vp.width}px)`, () => {
        test.use({ viewport: { width: vp.width, height: vp.height } })

        test("When visiting every study route — Then article renders", async ({
          page,
          pageErrors,
        }) => {
          for (const href of studyLinks) {
            const response = await page.goto(href)
            expect(response?.status(), `${href} returned non-200`).toBe(200)
            await expect(page).toHaveURL(href)
            await expect(page.locator("article.prose")).toBeVisible()
            if (vp.width > 1100) {
              const headingCount = await page.locator("article.prose :is(h1, h2, h3, h4)").count()
              expect(
                headingCount,
                `${href} must contain at least one H1-H4 heading`,
              ).toBeGreaterThan(0)
              expect(
                await page.locator('.study-toc a[href^="#"]').count(),
                `${href} TOC must mirror every H1-H4 heading`,
              ).toBe(headingCount)
            }
            await assertNoOverflow(page)
          }
          expect(pageErrors).toEqual([])
        })
      })
    }
  })
}

test.describe("Given a desktop study article", () => {
  test.use({ viewport: { width: 1280, height: 800 } })

  test("When reading the page outline — Then every H1-H4 heading appears in the right TOC", async ({
    page,
  }) => {
    const [href] = await gatherCategoryLinks(page, "aif")
    expect(href).toBeDefined()
    await page.goto(href ?? "/aif")

    const articleHeadings = page.locator("article.prose :is(h1, h2, h3, h4)")
    const tocLinks = page.locator('.study-toc a[href^="#"]')
    expect(await articleHeadings.count()).toBeGreaterThan(0)
    expect(await tocLinks.count()).toBe(await articleHeadings.count())

    for (let index = 0; index < (await articleHeadings.count()); index += 1) {
      const heading = articleHeadings.nth(index)
      const tocLink = tocLinks.nth(index)
      await expect(tocLink).toHaveText((await heading.textContent()) ?? "")
      await expect(tocLink).toHaveAttribute("href", `#${await heading.getAttribute("id")}`)
    }
  })
})
