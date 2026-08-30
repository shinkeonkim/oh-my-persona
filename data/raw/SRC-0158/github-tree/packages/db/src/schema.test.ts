import { describe, expect, it } from "bun:test"
import { getTableName } from "drizzle-orm"

import {
  bookmarks,
  categories,
  certResourceRelevance,
  childFeatures,
  contentAssets,
  questionProgress,
  questions,
  resourceAliases,
  resourceEdges,
  resources,
  studyNotes,
  users,
} from "./schema"

describe("database schema", () => {
  it("exposes stable table names for migrations", () => {
    // Given
    const tables = [users, categories, studyNotes, questions, questionProgress, bookmarks]

    // When
    const names = tables.map((table) => getTableName(table))

    // Then
    expect(names).toEqual([
      "users",
      "categories",
      "study_notes",
      "questions",
      "question_progress",
      "bookmarks",
    ])
  })

  it("exposes stable resource table names", () => {
    // Given
    const resourceTables = [
      resources,
      childFeatures,
      resourceAliases,
      resourceEdges,
      certResourceRelevance,
      contentAssets,
    ]

    // When
    const names = resourceTables.map((table) => getTableName(table))

    // Then
    expect(names).toEqual([
      "resources",
      "child_features",
      "resource_aliases",
      "resource_edges",
      "cert_resource_relevance",
      "content_assets",
    ])
  })

  it("resources table uses slug as text primary key", () => {
    // Given / When
    const slugCol = resources.slug

    // Then
    expect(slugCol.name).toBe("slug")
    expect(slugCol.notNull).toBe(true)
    expect(slugCol.primary).toBe(true)
  })

  it("child_features has FK to resources via parent_slug", () => {
    // Given / When
    const parentSlugCol = childFeatures.parentSlug

    // Then
    expect(parentSlugCol.name).toBe("parent_slug")
    expect(parentSlugCol.notNull).toBe(true)
  })

  it("resource_edges has both from_slug and to_slug columns", () => {
    // Given / When
    const fromCol = resourceEdges.fromSlug
    const toCol = resourceEdges.toSlug

    // Then
    expect(fromCol.name).toBe("from_slug")
    expect(toCol.name).toBe("to_slug")
    expect(fromCol.notNull).toBe(true)
    expect(toCol.notNull).toBe(true)
  })

  it("content_assets uses text id as primary key", () => {
    // Given / When
    const idCol = contentAssets.id

    // Then
    expect(idCol.name).toBe("id")
    expect(idCol.notNull).toBe(true)
    expect(idCol.primary).toBe(true)
  })

  it("cert_resource_relevance has composite natural key columns", () => {
    // Given / When
    const cols = [
      certResourceRelevance.resourceSlug,
      certResourceRelevance.certificationCode,
      certResourceRelevance.domainCode,
    ]

    // Then
    expect(cols.map((c) => c.name)).toEqual(["resource_slug", "certification_code", "domain_code"])
    for (const col of cols) {
      expect(col.notNull).toBe(true)
    }
  })
})
