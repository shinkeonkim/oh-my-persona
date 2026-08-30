/**
 * SAA source-coverage manifest tests — verifies exact artifact counts,
 * source classification, checksums, access policies, duplicate identity,
 * and generated system/* exclusion.
 */
import { describe, expect, it } from "bun:test"

import { contentSourcePaths, PROJECT_ROOT } from "./cli/paths"
import { splitByH2 } from "./saa-h2-splitter"
import { buildSaaManifest } from "./saa-manifest"

const SAA_ROOT = contentSourcePaths(PROJECT_ROOT).saa

describe("buildSaaManifest", () => {
  it("enumerates exactly 1264 questions", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    expect(manifest.counts.questions).toBe(1264)
  })

  it("enumerates exactly 24 study-note Markdown sources", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    expect(manifest.counts.studyNotes).toBe(24)
  })

  it("enumerates exactly 8 regular concept notes", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    expect(manifest.counts.conceptNotes).toBe(8)
  })

  it("enumerates exactly 51 H2 resource sections from the resource note", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    expect(manifest.counts.resourceSections).toBe(51)
  })

  it("enumerates exactly 9 linked PDFs from notes/files/", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    expect(manifest.counts.linkedPdfs).toBe(9)
  })

  it("enumerates exactly 2 root question PDFs", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    expect(manifest.counts.rootPdfs).toBe(2)
  })
})

describe("source classification", () => {
  it("classifies study-notes as kind=study-note with access=public", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    const studyNotes = manifest.artifacts.filter((a) => a.kind === "study-note")
    expect(studyNotes.length).toBe(24)
    for (const note of studyNotes) {
      expect(note.access).toBe("public")
      expect(note.relativePath).toMatch(/^study-notes\//)
    }
  })

  it("classifies concept notes as kind=concept-note with access=public", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    const concepts = manifest.artifacts.filter((a) => a.kind === "concept-note")
    expect(concepts.length).toBe(8)
    for (const note of concepts) {
      expect(note.access).toBe("public")
      expect(note.relativePath).toMatch(/^notes\//)
    }
  })

  it("classifies linked PDFs as kind=linked-pdf with access=public", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    const pdfs = manifest.artifacts.filter((a) => a.kind === "linked-pdf")
    expect(pdfs.length).toBe(9)
    for (const pdf of pdfs) {
      expect(pdf.access).toBe("public")
      expect(pdf.relativePath).toMatch(/^notes\/files\//)
    }
  })

  it("classifies root PDFs as kind=root-pdf with access=protected", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    const rootPdfs = manifest.artifacts.filter((a) => a.kind === "root-pdf")
    expect(rootPdfs.length).toBe(2)
    for (const pdf of rootPdfs) {
      expect(pdf.access).toBe("protected")
    }
  })
})

describe("source identity and checksums", () => {
  it("produces no duplicate artifact IDs", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    const ids = manifest.artifacts.map((a) => a.id)
    expect(new Set(ids).size).toBe(ids.length)
  })

  it("every artifact has a non-empty SHA-256 checksum (64 hex chars)", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    for (const artifact of manifest.artifacts) {
      expect(artifact.checksum).toMatch(/^[0-9a-f]{64}$/)
    }
  })

  it("checksums are deterministic across two builds", async () => {
    const m1 = await buildSaaManifest(SAA_ROOT)
    const m2 = await buildSaaManifest(SAA_ROOT)
    for (let i = 0; i < m1.artifacts.length; i++) {
      expect(m1.artifacts[i]?.checksum).toBe(m2.artifacts[i]?.checksum)
    }
  })
})

describe("generated system/* exclusion", () => {
  it("no artifact references system/ paths", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    for (const artifact of manifest.artifacts) {
      expect(artifact.relativePath).not.toMatch(/^system\//)
    }
  })

  it("no artifact ID references bank or notes.js", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    for (const artifact of manifest.artifacts) {
      expect(artifact.id).not.toContain("bank")
      expect(artifact.id).not.toContain("notes.js")
    }
  })
})

describe("resource section H2 splitting", () => {
  it("concept notes do NOT include the resource document", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    const concepts = manifest.artifacts.filter((a) => a.kind === "concept-note")
    for (const c of concepts) {
      expect(c.id).not.toContain("\uB9AC\uC18C\uC2A4_\uC644\uC804\uC815\uB9AC")
      expect(c.id).not.toContain("resources")
    }
  })

  it("resource sections have sequential order 1..51", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    const sections = manifest.artifacts
      .filter((a) => a.kind === "resource-section")
      .sort((a, b) => a.order - b.order)
    expect(sections.length).toBe(51)
    for (let i = 0; i < sections.length; i++) {
      expect(sections[i]?.order).toBe(i + 1)
    }
  })

  it("resource sections all share the same parent ID", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    const sections = manifest.artifacts.filter((a) => a.kind === "resource-section")
    const parentIds = new Set(sections.map((s) => s.parentId))
    expect(parentIds.size).toBe(1)
  })
})

describe("concept note PDF linkage", () => {
  it("each concept note has a linked PDF path", async () => {
    const manifest = await buildSaaManifest(SAA_ROOT)
    const concepts = manifest.artifacts.filter((a) => a.kind === "concept-note")
    for (const c of concepts) {
      expect(c.linkedPdfPath).toBeDefined()
      expect(c.linkedPdfPath).toMatch(/^notes\/files\/.*\.pdf$/)
    }
  })
})

describe("splitByH2 unit", () => {
  it("splits markdown into sections at H2 boundaries", () => {
    const md = "# Title\nIntro\n## First\nContent 1\n## Second\nContent 2\n"
    const sections = splitByH2(md)
    expect(sections).toHaveLength(2)
    expect(sections[0]?.title).toBe("First")
    expect(sections[0]?.order).toBe(1)
    expect(sections[1]?.title).toBe("Second")
  })

  it("returns empty array for markdown without H2", () => {
    expect(splitByH2("# Only H1\nNo sections")).toHaveLength(0)
  })

  it("generates numbered slugs from titles like '1. Foo'", () => {
    const md = "## 1. Computing\nA\n## 2. Storage\nB\n## 10. Network\nC\n"
    const sections = splitByH2(md)
    expect(sections[0]?.slug).toBe("section-01")
    expect(sections[1]?.slug).toBe("section-02")
    expect(sections[2]?.slug).toBe("section-10")
  })
})
