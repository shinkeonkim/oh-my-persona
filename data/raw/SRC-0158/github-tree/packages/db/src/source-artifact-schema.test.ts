import { describe, expect, it } from "bun:test"
import { getTableName } from "drizzle-orm"

import { sourceArtifacts } from "./schema"

describe("source artifact schema", () => {
  it("uses a stable table name and natural source ID", () => {
    expect(getTableName(sourceArtifacts)).toBe("source_artifacts")
    expect(sourceArtifacts.id.name).toBe("id")
    expect(sourceArtifacts.id.primary).toBeTrue()
  })

  it("stores source namespace, kind, access, and checksum metadata", () => {
    expect(sourceArtifacts.sourceNamespace.notNull).toBeTrue()
    expect(sourceArtifacts.kind.notNull).toBeTrue()
    expect(sourceArtifacts.access.notNull).toBeTrue()
    expect(sourceArtifacts.checksum.notNull).toBeTrue()
    expect(sourceArtifacts.sourceIdentity.notNull).toBeTrue()
  })

  it("allows PDF metadata without Markdown and derived section parents", () => {
    expect(sourceArtifacts.markdown.notNull).toBeFalse()
    expect(sourceArtifacts.parentId.notNull).toBeFalse()
    expect(sourceArtifacts.order.notNull).toBeTrue()
  })
})
