import { describe, expect, it } from "bun:test"

import { contentSourcePaths, PROJECT_ROOT } from "./cli/paths"
import { loadAllContent } from "./source-loader"

describe("loadAllContent", () => {
  it("builds AIF categories for both study notes and quiz questions", async () => {
    // Given
    const paths = contentSourcePaths(PROJECT_ROOT)

    // When
    const bundle = await loadAllContent(paths)
    const categorySlugs = new Set(
      bundle.categories
        .filter((category) => category.certificationCode === "aif")
        .map((category) => category.slug),
    )
    const noteSlugs = bundle.studyNotes
      .filter((note) => note.certificationCode === "aif")
      .map((note) => note.slug)
    const questionSlugs = bundle.questions
      .filter((question) => question.certificationCode === "aif")
      .map((question) => question.categorySlug)

    // Then
    expect(categorySlugs).toEqual(new Set([...noteSlugs, ...questionSlugs]))
  })

  it("loads exactly 412 AIF questions", async () => {
    // Given
    const paths = contentSourcePaths(PROJECT_ROOT)

    // When
    const bundle = await loadAllContent(paths)
    const aifQuestions = bundle.questions.filter((q) => q.certificationCode === "aif")

    // Then
    expect(aifQuestions).toHaveLength(412)
  })

  it("loads 11 AIF study notes (6 source + 5 supplements)", async () => {
    // Given
    const paths = contentSourcePaths(PROJECT_ROOT)

    // When
    const bundle = await loadAllContent(paths)
    const aifNotes = bundle.studyNotes.filter((n) => n.certificationCode === "aif")

    // Then
    expect(aifNotes).toHaveLength(11)
    const slugs = new Set(aifNotes.map((n) => n.slug))
    for (const expected of [
      "bedrock-prompt-management",
      "bedrock-agentic-ai-mcp",
      "bedrock-agentcore",
      "bedrock-evaluation-grounding",
      "security-governance",
    ]) {
      expect(slugs.has(expected)).toBe(true)
    }
  })

  it("marks all study notes as public across certifications", async () => {
    // Given
    const paths = contentSourcePaths(PROJECT_ROOT)

    // When
    const bundle = await loadAllContent(paths)

    // Then
    for (const note of bundle.studyNotes) {
      expect(note.access).toBe("public")
    }
  })

  it("marks all questions as protected across certifications", async () => {
    // Given
    const paths = contentSourcePaths(PROJECT_ROOT)

    // When
    const bundle = await loadAllContent(paths)

    // Then
    for (const question of bundle.questions) {
      expect(question.access).toBe("protected")
    }
  })

  it("produces exactly 2402 total questions", async () => {
    // Given
    const paths = contentSourcePaths(PROJECT_ROOT)

    // When
    const bundle = await loadAllContent(paths)

    // Then
    expect(bundle.questions).toHaveLength(2402)
  })

  it("loads every SAA non-question artifact with exact access counts", async () => {
    const bundle = await loadAllContent(contentSourcePaths(PROJECT_ROOT))
    const byKind = (kind: (typeof bundle.sourceArtifacts)[number]["kind"]) =>
      bundle.sourceArtifacts.filter((artifact) => artifact.kind === kind)
    expect(byKind("study-note")).toHaveLength(24)
    expect(byKind("concept-note")).toHaveLength(8)
    expect(byKind("resource-section")).toHaveLength(51)
    expect(byKind("linked-pdf")).toHaveLength(9)
    expect(byKind("root-pdf")).toHaveLength(2)
    expect(byKind("linked-pdf").every((artifact) => artifact.access === "public")).toBeTrue()
    expect(byKind("root-pdf").every((artifact) => artifact.access === "protected")).toBeTrue()
  })

  it("stores sanitized markdown for SAA note views and metadata only for PDFs", async () => {
    const bundle = await loadAllContent(contentSourcePaths(PROJECT_ROOT))
    const markdownArtifacts = bundle.sourceArtifacts.filter((artifact) =>
      ["study-note", "concept-note", "resource-section"].includes(artifact.kind),
    )
    const pdfArtifacts = bundle.sourceArtifacts.filter((artifact) => artifact.kind.endsWith("pdf"))
    expect(markdownArtifacts).toHaveLength(83)
    expect(markdownArtifacts.every((artifact) => artifact.markdown !== null)).toBeTrue()
    expect(pdfArtifacts).toHaveLength(11)
    expect(pdfArtifacts.every((artifact) => artifact.markdown === null)).toBeTrue()
  })
})
