/**
 * Baseline characterization tests — proves the current bundle has the expected
 * SAA question/study-note counts and that concept/resource/PDF artifacts are
 * NOT yet covered by the existing loadAllContent pipeline.
 */
import { describe, expect, it } from "bun:test"

import { contentSourcePaths, PROJECT_ROOT } from "./cli/paths"
import { loadAllContent } from "./source-loader"

describe("SAA baseline characterization", () => {
  it("current bundle contains exactly 1264 SAA questions", async () => {
    // Given
    const paths = contentSourcePaths(PROJECT_ROOT)

    // When
    const bundle = await loadAllContent(paths)
    const saaQuestions = bundle.questions.filter((q) => q.certificationCode === "saa")

    // Then
    expect(saaQuestions).toHaveLength(1264)
  })

  it("current bundle contains exactly 24 SAA study notes", async () => {
    // Given
    const paths = contentSourcePaths(PROJECT_ROOT)

    // When
    const bundle = await loadAllContent(paths)
    const saaNotes = bundle.studyNotes.filter((n) => n.certificationCode === "saa")

    // Then
    expect(saaNotes).toHaveLength(24)
  })

  it("current bundle does NOT include concept notes from notes/ directory", async () => {
    // Given
    const paths = contentSourcePaths(PROJECT_ROOT)

    // When
    const bundle = await loadAllContent(paths)
    const saaNoteSlugs = new Set(
      bundle.studyNotes.filter((n) => n.certificationCode === "saa").map((n) => n.slug),
    )

    // Then — concept note slugs should be absent
    expect(saaNoteSlugs.has("api-gateway")).toBe(false)
    expect(saaNoteSlugs.has("iam-governance")).toBe(false)
    expect(saaNoteSlugs.has("rds-aurora-\uC2A4\uD1A0\uB9AC\uC9C0")).toBe(false)
  })

  it("current bundle does NOT include resource sections or PDFs", async () => {
    // Given
    const paths = contentSourcePaths(PROJECT_ROOT)

    // When
    const bundle = await loadAllContent(paths)

    // Then — bundle has no concept of resource sections or PDF artifacts
    const allSlugs = new Set(bundle.studyNotes.map((n) => n.slug))
    expect(allSlugs.has("section-01")).toBe(false)
    expect(allSlugs.has("resources")).toBe(false)
  })
})
