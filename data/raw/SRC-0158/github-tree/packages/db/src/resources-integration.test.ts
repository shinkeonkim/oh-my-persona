import { afterAll, beforeAll, describe, expect, it } from "bun:test"
import { rmSync } from "node:fs"
import { migrate } from "drizzle-orm/postgres-js/migrator"
import postgres from "postgres"

import { createDatabase } from "./client"
import {
  connectionUrl,
  createDb,
  execSql,
  expectConstraintViolation,
  makeMigrationDir,
  queryTableNames,
  removeContainerIfExists,
  startContainer,
} from "./test-helpers"

const CONTAINER = "task3-test-postgres"
const PORT = 5433
const PW = "task3test"
const DRIZZLE_DIR = new URL("../drizzle", import.meta.url).pathname
const MIGRATION_0000 = "0000_nifty_infant_terrible"

function url(db: string): string {
  return connectionUrl(PORT, PW, db)
}

const tempDirs: string[] = []

describe("resource schema integration", () => {
  beforeAll(async () => {
    await removeContainerIfExists(CONTAINER)
    await startContainer(CONTAINER, PORT, PW)
    await createDb(url("postgres"), "test_fresh")
    await createDb(url("postgres"), "test_incr")
  }, 60_000)

  afterAll(async () => {
    for (const dir of tempDirs) {
      rmSync(dir, { recursive: true, force: true })
    }
    await removeContainerIfExists(CONTAINER)
  })

  it("fresh migration applies both 0000 and 0001 from scratch", async () => {
    const db = createDatabase(url("test_fresh"))
    await migrate(db, { migrationsFolder: DRIZZLE_DIR })

    const names = await queryTableNames(url("test_fresh"))
    for (const t of [
      "resources",
      "child_features",
      "resource_aliases",
      "resource_edges",
      "cert_resource_relevance",
      "content_assets",
    ]) {
      expect(names).toContain(t)
    }
  }, 30_000)

  it("incremental: 0000 alone has legacy tables but no resource tables", async () => {
    const onlyZero = makeMigrationDir([MIGRATION_0000])
    tempDirs.push(onlyZero)

    const db = createDatabase(url("test_incr"))
    await migrate(db, { migrationsFolder: onlyZero })

    const names = await queryTableNames(url("test_incr"))
    expect(names).toContain("categories")
    expect(names).toContain("users")
    expect(names).not.toContain("resources")
    expect(names).not.toContain("content_assets")
  }, 30_000)

  it("incremental: applying 0001 adds resource tables without harming legacy rows", async () => {
    await execSql(
      url("test_incr"),
      `INSERT INTO categories (id, certification_code, slug, "order", title)
       VALUES (gen_random_uuid(), 'saa', 'networking', 1, 'Networking')`,
    )

    const db = createDatabase(url("test_incr"))
    await migrate(db, { migrationsFolder: DRIZZLE_DIR })

    const names = await queryTableNames(url("test_incr"))
    expect(names).toContain("resources")
    expect(names).toContain("content_assets")

    const client = postgres(url("test_incr"), { max: 1 })
    try {
      const rows = await client`SELECT slug FROM categories WHERE slug = 'networking'`
      expect(rows).toHaveLength(1)
    } finally {
      await client.end()
    }
  }, 30_000)

  it("rejects duplicate canonical resource slug", async () => {
    await execSql(
      url("test_fresh"),
      `INSERT INTO resources (slug, title, summary, difficulty, "order")
       VALUES ('amazon-s3', 'Amazon S3', 'Object storage', 'foundation', 1)`,
    )
    const code = await expectConstraintViolation(
      url("test_fresh"),
      `INSERT INTO resources (slug, title, summary, difficulty, "order")
       VALUES ('amazon-s3', 'Duplicate S3', 'Dup', 'foundation', 2)`,
    )
    expect(code).toBe("23505")
  }, 10_000)

  it("rejects alias referencing non-existent resource", async () => {
    const code = await expectConstraintViolation(
      url("test_fresh"),
      `INSERT INTO resource_aliases (alias, canonical_slug)
       VALUES ('s3-alias', 'non-existent-resource')`,
    )
    expect(code).toBe("23503")
  }, 10_000)

  it("rejects edge with dangling from_slug", async () => {
    const code = await expectConstraintViolation(
      url("test_fresh"),
      `INSERT INTO resource_edges (from_slug, to_slug, edge_type)
       VALUES ('ghost-resource', 'amazon-s3', 'uses')`,
    )
    expect(code).toBe("23503")
  }, 10_000)

  it("rejects edge with dangling to_slug", async () => {
    const code = await expectConstraintViolation(
      url("test_fresh"),
      `INSERT INTO resource_edges (from_slug, to_slug, edge_type)
       VALUES ('amazon-s3', 'ghost-resource', 'uses')`,
    )
    expect(code).toBe("23503")
  }, 10_000)

  it("rejects content asset referencing non-existent resource", async () => {
    const code = await expectConstraintViolation(
      url("test_fresh"),
      `INSERT INTO content_assets (id, resource_slug, kind, access, title, checksum, source_identity)
       VALUES ('asset-1', 'ghost-resource', 'pdf', 'public', 'Test', 'sha256:abc', 'src')`,
    )
    expect(code).toBe("23503")
  }, 10_000)

  it("rejects child feature referencing non-existent parent", async () => {
    const code = await expectConstraintViolation(
      url("test_fresh"),
      `INSERT INTO child_features (slug, parent_slug, title, summary, "order")
       VALUES ('child-1', 'ghost-parent', 'Child', 'Summary', 1)`,
    )
    expect(code).toBe("23503")
  }, 10_000)

  it("rejects duplicate cert_resource_relevance composite key", async () => {
    await execSql(
      url("test_fresh"),
      `INSERT INTO cert_resource_relevance (resource_slug, certification_code, domain_code)
       VALUES ('amazon-s3', 'saa', 'domain-3')`,
    )
    const code = await expectConstraintViolation(
      url("test_fresh"),
      `INSERT INTO cert_resource_relevance (resource_slug, certification_code, domain_code)
       VALUES ('amazon-s3', 'saa', 'domain-3')`,
    )
    expect(code).toBe("23505")
  }, 10_000)
})
