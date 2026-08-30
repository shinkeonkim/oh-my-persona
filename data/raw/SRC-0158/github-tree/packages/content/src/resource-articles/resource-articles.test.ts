import { describe, expect, it } from "bun:test"
import { buildCatalogBundle } from "@aws-study/shared"

import { auditStudyNote } from "../copyright-filter"
import { buildResourceArticles } from "./build"
import { resourceArticleSchema } from "./types"

const bundle = buildCatalogBundle()
const articles = buildResourceArticles()
const bySlug = new Map(articles.map((article) => [article.slug, article]))

describe("canonical resource articles", () => {
  it("covers every canonical root exactly once", () => {
    expect(articles).toHaveLength(bundle.resources.length)
    expect(new Set(articles.map((article) => article.slug)).size).toBe(articles.length)
    expect([...bySlug.keys()].sort()).toEqual(
      bundle.resources.map((resource) => resource.slug).sort(),
    )
  })

  it("parses typed 3-8 minute articles with official AWS references", () => {
    for (const article of articles) {
      expect(resourceArticleSchema.safeParse(article).success).toBeTrue()
      expect(new URL(article.officialUrl).hostname).toBe("docs.aws.amazon.com")
      expect(article.markdown.startsWith(`# ${article.title}\n`)).toBeTrue()
      expect(article.markdown.replace(/\s/g, "").length).toBeGreaterThanOrEqual(1_800)
      expect(article.markdown).not.toMatch(/AIF-C01|CLF-C02|SAA-C03/)
      expect(article.readingMinutes).toBeGreaterThanOrEqual(3)
      expect(article.readingMinutes).toBeLessThanOrEqual(8)
    }
  })

  it("links every prerequisite and feature from its single shared body", () => {
    for (const resource of bundle.resources) {
      const article = bySlug.get(resource.slug)
      expect(article).toBeDefined()
      if (article === undefined) continue
      for (const prerequisite of resource.prerequisites) {
        expect(article.markdown).toContain(`/resources/${prerequisite}`)
      }
      for (const feature of bundle.features.filter((item) => item.parentSlug === resource.slug)) {
        expect(article.markdown).toContain(feature.title)
      }
    }
  })

  it("gives every applied resource an operational relation and applied step", () => {
    for (const article of articles.filter((item) => item.difficulty === "applied")) {
      const related = bundle.edges.some(
        (edge) => edge.from === article.slug || edge.to === article.slug,
      )
      expect(related).toBeTrue()
      expect(article.markdown).toContain("## 적용 단계")
    }
  })

  it("uses valid H1-H2-H3 hierarchy and passes copyright audit", () => {
    for (const article of articles) {
      const headings = article.markdown
        .split("\n")
        .filter((line) => /^#{1,3}\s/.test(line))
        .map((line) => line.match(/^(#+)/)?.[1]?.length ?? 0)
      expect(headings[0]).toBe(1)
      expect(headings.slice(1).every((level) => level === 2 || level === 3)).toBeTrue()
      expect(auditStudyNote(article.markdown)).toEqual([])
    }
  })
})
