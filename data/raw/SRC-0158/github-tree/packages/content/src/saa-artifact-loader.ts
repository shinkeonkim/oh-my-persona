import { sanitizeStudyNote } from "./copyright-filter"
import { splitByH2 } from "./saa-h2-splitter"
import { buildSaaManifest, type SourceArtifact as ManifestArtifact } from "./saa-manifest"
import { type SourceArtifact, sourceArtifactSchema } from "./types"

async function loadMarkdown(
  root: string,
  artifact: ManifestArtifact,
  sectionsByPath: Map<string, readonly string[]>,
): Promise<string | null> {
  switch (artifact.kind) {
    case "linked-pdf":
    case "root-pdf":
      return null
    case "study-note":
    case "concept-note":
      return sanitizeStudyNote(await Bun.file(`${root}/${artifact.relativePath}`).text())
    case "resource-section": {
      let sections = sectionsByPath.get(artifact.relativePath)
      if (sections === undefined) {
        const source = await Bun.file(`${root}/${artifact.relativePath}`).text()
        sections = splitByH2(source).map((section) => sanitizeStudyNote(section.markdown))
        sectionsByPath.set(artifact.relativePath, sections)
      }
      const markdown = sections[artifact.order - 1]
      if (markdown === undefined) {
        throw new SourceArtifactLoadError(artifact.id)
      }
      return markdown
    }
  }
}

export class SourceArtifactLoadError extends Error {
  readonly artifactId: string

  constructor(artifactId: string) {
    super(`Missing derived Markdown for ${artifactId}`)
    this.name = "SourceArtifactLoadError"
    this.artifactId = artifactId
  }
}

export async function loadSaaSourceArtifacts(root: string): Promise<readonly SourceArtifact[]> {
  const manifest = await buildSaaManifest(root)
  const sectionsByPath = new Map<string, readonly string[]>()
  const artifacts: SourceArtifact[] = []
  for (const artifact of manifest.artifacts) {
    artifacts.push(
      sourceArtifactSchema.parse({
        id: artifact.id,
        sourceNamespace: "saa",
        certificationCode: "saa",
        kind: artifact.kind,
        access: artifact.access,
        title: artifact.title,
        markdown: await loadMarkdown(root, artifact, sectionsByPath),
        checksum: artifact.checksum,
        sourceIdentity: artifact.relativePath,
        ...(artifact.parentId === undefined ? {} : { parentId: artifact.parentId }),
        order: artifact.order,
      }),
    )
  }
  return artifacts
}
