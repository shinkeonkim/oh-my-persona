/**
 * SAA source-coverage manifest — enumerates all canonical source artifacts
 * from the SAA content-source submodule without persisting them.
 *
 * Canonical sources are Markdown/PDF files under study-notes/, notes/, and root.
 * Generated files under system/ (bank.js, notes.js) are explicitly excluded.
 */
import { computeFileChecksum } from "./saa-checksum"
import { splitByH2 } from "./saa-h2-splitter"
import { noteTitle } from "./slug"

const SOURCE_KINDS = [
  "study-note",
  "concept-note",
  "resource-section",
  "linked-pdf",
  "root-pdf",
] as const
export type SourceKind = (typeof SOURCE_KINDS)[number]

const ACCESS_POLICIES = ["public", "protected"] as const
export type AccessPolicy = (typeof ACCESS_POLICIES)[number]

export type SourceArtifact = {
  readonly id: string
  readonly kind: SourceKind
  readonly access: AccessPolicy
  readonly relativePath: string
  readonly title: string
  readonly checksum: string
  readonly parentId?: string
  readonly linkedPdfPath?: string
  readonly order: number
}

export type SaaSourceManifest = {
  readonly artifacts: readonly SourceArtifact[]
  readonly counts: {
    readonly questions: number
    readonly studyNotes: number
    readonly conceptNotes: number
    readonly resourceSections: number
    readonly linkedPdfs: number
    readonly rootPdfs: number
  }
}

const RESOURCE_DOC_STEM = "AWS_SAA-C03_\uB9AC\uC18C\uC2A4_\uC644\uC804\uC815\uB9AC"

function slugifyNoteStem(stem: string): string {
  let s = stem
  for (const prefix of ["AWS_SAA_", "AWS_SAA-", "AWS_\uAC1C\uB150_", "AWS_"]) {
    if (s.startsWith(prefix)) {
      s = s.slice(prefix.length)
      break
    }
  }
  for (const suffix of ["_\uC815\uB9AC", "-\uC815\uB9AC"]) {
    if (s.endsWith(suffix)) {
      s = s.slice(0, -suffix.length)
      break
    }
  }
  return (
    s
      .toLowerCase()
      .replaceAll("_", "-")
      .replaceAll(" ", "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "") || stem.toLowerCase()
  )
}

export async function buildSaaManifest(saaRoot: string): Promise<SaaSourceManifest> {
  const artifacts: SourceArtifact[] = []

  const studyNotes = await enumerateStudyNotes(saaRoot)
  const { conceptNotes, resourceSections } = await enumerateNotes(saaRoot)
  const linkedPdfs = await enumerateLinkedPdfs(saaRoot)
  const rootPdfs = await enumerateRootPdfs(saaRoot)
  const questionCount = await countQuestions(saaRoot)

  artifacts.push(...studyNotes, ...conceptNotes, ...resourceSections, ...linkedPdfs, ...rootPdfs)

  return {
    artifacts,
    counts: {
      questions: questionCount,
      studyNotes: studyNotes.length,
      conceptNotes: conceptNotes.length,
      resourceSections: resourceSections.length,
      linkedPdfs: linkedPdfs.length,
      rootPdfs: rootPdfs.length,
    },
  }
}

async function enumerateStudyNotes(root: string): Promise<SourceArtifact[]> {
  const dir = `${root}/study-notes`
  const glob = new Bun.Glob("*.md")
  const results: SourceArtifact[] = []
  for await (const filename of glob.scan({ cwd: dir })) {
    const filePath = `${dir}/${filename}`
    const markdown = await Bun.file(filePath).text()
    const stem = filename.replace(/\.md$/i, "")
    const orderMatch = stem.match(/^(\d{2})-/)?.[1]
    const order = orderMatch ? Number.parseInt(orderMatch, 10) : 99
    results.push({
      id: `saa:study-note:${stem}`,
      kind: "study-note",
      access: "public",
      relativePath: `study-notes/${filename}`,
      title: noteTitle(markdown, stem),
      checksum: await computeFileChecksum(filePath),
      order,
    })
  }
  return results.sort((a, b) => a.order - b.order)
}

async function enumerateNotes(root: string): Promise<{
  readonly conceptNotes: SourceArtifact[]
  readonly resourceSections: SourceArtifact[]
}> {
  const dir = `${root}/notes`
  const glob = new Bun.Glob("*.md")
  const conceptNotes: SourceArtifact[] = []
  const resourceSections: SourceArtifact[] = []

  for await (const filename of glob.scan({ cwd: dir })) {
    const filePath = `${dir}/${filename}`
    const markdown = await Bun.file(filePath).text()
    const stem = filename.replace(/\.md$/i, "")
    const normalizedStem = stem.normalize("NFC")

    if (normalizedStem === RESOURCE_DOC_STEM) {
      const parentId = `saa:resource-note:${slugifyNoteStem(normalizedStem)}`
      const sections = splitByH2(markdown)
      for (const section of sections) {
        resourceSections.push({
          id: `saa:resource-section:${section.slug}`,
          kind: "resource-section",
          access: "public",
          relativePath: `notes/${filename}`,
          title: section.title,
          checksum: await computeFileChecksum(filePath),
          parentId,
          order: section.order,
        })
      }
    } else {
      const slug = slugifyNoteStem(normalizedStem)
      const pdfFilename = await findLinkedPdf(root, normalizedStem)
      conceptNotes.push({
        id: `saa:concept-note:${slug}`,
        kind: "concept-note",
        access: "public",
        relativePath: `notes/${filename}`,
        title: noteTitle(markdown, stem),
        checksum: await computeFileChecksum(filePath),
        ...(pdfFilename ? { linkedPdfPath: `notes/files/${pdfFilename}` } : {}),
        order: conceptNotes.length + 1,
      })
    }
  }
  return {
    conceptNotes: conceptNotes.sort((a, b) => a.title.localeCompare(b.title)),
    resourceSections: resourceSections.sort((a, b) => a.order - b.order),
  }
}

async function findLinkedPdf(root: string, noteStem: string): Promise<string | undefined> {
  const pdfDir = `${root}/notes/files`
  const glob = new Bun.Glob("*.pdf")
  for await (const filename of glob.scan({ cwd: pdfDir })) {
    const pdfStem = filename.replace(/\.pdf$/i, "").normalize("NFC")
    if (pdfStem === noteStem) return filename
  }
  return undefined
}

async function enumerateLinkedPdfs(root: string): Promise<SourceArtifact[]> {
  const dir = `${root}/notes/files`
  const glob = new Bun.Glob("*.pdf")
  const results: SourceArtifact[] = []
  let order = 1
  for await (const filename of glob.scan({ cwd: dir })) {
    const filePath = `${dir}/${filename}`
    const stem = filename.replace(/\.pdf$/i, "")
    results.push({
      id: `saa:linked-pdf:${slugifyNoteStem(stem.normalize("NFC"))}`,
      kind: "linked-pdf",
      access: "public",
      relativePath: `notes/files/${filename}`,
      title: stem,
      checksum: await computeFileChecksum(filePath),
      order: order++,
    })
  }
  return results.sort((a, b) => a.title.localeCompare(b.title))
}

async function enumerateRootPdfs(root: string): Promise<SourceArtifact[]> {
  const glob = new Bun.Glob("*.pdf")
  const results: SourceArtifact[] = []
  let order = 1
  for await (const filename of glob.scan({ cwd: root })) {
    const filePath = `${root}/${filename}`
    results.push({
      id: `saa:root-pdf:${order}`,
      kind: "root-pdf",
      access: "protected",
      relativePath: filename,
      title: filename.replace(/\.pdf$/i, ""),
      checksum: await computeFileChecksum(filePath),
      order: order++,
    })
  }
  return results
}

async function countQuestions(root: string): Promise<number> {
  const categoryGlob = new Bun.Glob("[0-9][0-9]-*")
  const questionGlob = new Bun.Glob("*.md")
  let count = 0
  for await (const directory of categoryGlob.scan({ cwd: root, onlyFiles: false })) {
    for await (const _filename of questionGlob.scan({ cwd: `${root}/${directory}` })) {
      count++
    }
  }
  return count
}
