/**
 * One-shot script to dump the SAA source manifest as JSON to stdout.
 * Usage: bun run src/cli/dump-manifest.ts
 */
import { buildSaaManifest } from "../saa-manifest"
import { contentSourcePaths, PROJECT_ROOT } from "./paths"

const saaRoot = contentSourcePaths(PROJECT_ROOT).saa
const manifest = await buildSaaManifest(saaRoot)

const summary = {
  timestamp: new Date().toISOString(),
  counts: manifest.counts,
  artifacts: manifest.artifacts.map((a) => ({
    id: a.id,
    kind: a.kind,
    access: a.access,
    relativePath: a.relativePath,
    title: a.title,
    checksum: a.checksum,
    ...(a.parentId ? { parentId: a.parentId } : {}),
    ...(a.linkedPdfPath ? { linkedPdfPath: a.linkedPdfPath } : {}),
    order: a.order,
  })),
}

console.log(JSON.stringify(summary, null, 2))
