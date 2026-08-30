import { afterAll, beforeAll, describe, expect, it } from "bun:test"
import { createDatabase, questions, sourceArtifacts } from "@aws-study/db"
import { eq, sql } from "drizzle-orm"
import { migrate } from "drizzle-orm/postgres-js/migrator"

import {
  connectionUrl,
  createDb,
  execSql,
  removeContainerIfExists,
  startContainer,
} from "../../db/src/test-helpers"
import { contentSourcePaths, PROJECT_ROOT } from "./cli/paths"
import { persistContent } from "./persist"
import { buildSaaManifest } from "./saa-manifest"
import { loadAllContent } from "./source-loader"

const CONTAINER = "task7-test-postgres"
const PORT = 5435
const PASSWORD = "task7test"
const DATABASE = "task7"
const MIGRATIONS = new URL("../../db/drizzle", import.meta.url).pathname

function url(database: string): string {
  return connectionUrl(PORT, PASSWORD, database)
}

const database = createDatabase(url(DATABASE))

async function artifactCounts(): Promise<Record<string, number>> {
  const rows = await database
    .select({ kind: sourceArtifacts.kind, count: sql<number>`count(*)::int` })
    .from(sourceArtifacts)
    .where(eq(sourceArtifacts.sourceNamespace, "saa"))
    .groupBy(sourceArtifacts.kind)
    .orderBy(sourceArtifacts.kind)
  return Object.fromEntries(rows.map((row) => [row.kind, row.count]))
}

async function persistenceSnapshot(): Promise<string> {
  const rows = await database
    .select({
      id: sourceArtifacts.id,
      kind: sourceArtifacts.kind,
      access: sourceArtifacts.access,
      checksum: sourceArtifacts.checksum,
      sourceIdentity: sourceArtifacts.sourceIdentity,
      parentId: sourceArtifacts.parentId,
      order: sourceArtifacts.order,
    })
    .from(sourceArtifacts)
    .where(eq(sourceArtifacts.sourceNamespace, "saa"))
    .orderBy(sourceArtifacts.id)
  return JSON.stringify(rows)
}

describe("complete SAA persistence", () => {
  beforeAll(async () => {
    await removeContainerIfExists(CONTAINER)
    await startContainer(CONTAINER, PORT, PASSWORD)
    await createDb(url("postgres"), DATABASE)
    await migrate(database, { migrationsFolder: MIGRATIONS })
  }, 60_000)

  afterAll(async () => {
    await removeContainerIfExists(CONTAINER)
  })

  it("is idempotent, exact, stale-safe, and source-read-only", async () => {
    const paths = contentSourcePaths(PROJECT_ROOT)
    const beforeManifest = await buildSaaManifest(paths.saa)
    const bundle = await loadAllContent(paths)

    await persistContent(url(DATABASE), bundle)
    const firstSnapshot = await persistenceSnapshot()
    await persistContent(url(DATABASE), bundle)
    expect(await persistenceSnapshot()).toBe(firstSnapshot)

    expect(await artifactCounts()).toEqual({
      "concept-note": 8,
      "linked-pdf": 9,
      "resource-section": 51,
      "root-pdf": 2,
      "study-note": 24,
    })
    const assetAccess = await database
      .select({
        kind: sourceArtifacts.kind,
        access: sourceArtifacts.access,
        count: sql<number>`count(*)::int`,
      })
      .from(sourceArtifacts)
      .where(eq(sourceArtifacts.sourceNamespace, "saa"))
      .groupBy(sourceArtifacts.kind, sourceArtifacts.access)
    expect(assetAccess).toContainEqual({ kind: "linked-pdf", access: "public", count: 9 })
    expect(assetAccess).toContainEqual({ kind: "root-pdf", access: "protected", count: 2 })

    const questionCount = await database
      .select({ count: sql<number>`count(*)::int` })
      .from(questions)
      .where(eq(questions.certificationCode, "saa"))
    expect(questionCount[0]?.count).toBe(1264)

    await execSql(
      url(DATABASE),
      `INSERT INTO source_artifacts
       (id, source_namespace, certification_code, kind, access, title, checksum, source_identity, "order")
       VALUES ('saa:concept-note:stale', 'saa', 'saa', 'concept-note', 'public', 'Stale',
               repeat('a', 64), 'notes/stale.md', 999)`,
    )
    await persistContent(url(DATABASE), bundle)
    expect((await persistenceSnapshot()).includes("saa:concept-note:stale")).toBeFalse()

    const afterManifest = await buildSaaManifest(paths.saa)
    expect(afterManifest.artifacts.map((artifact) => artifact.checksum)).toEqual(
      beforeManifest.artifacts.map((artifact) => artifact.checksum),
    )
  }, 60_000)
})
