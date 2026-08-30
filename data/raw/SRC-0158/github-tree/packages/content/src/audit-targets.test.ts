import { describe, expect, it } from "bun:test"
import { selectCopyrightAuditNotes } from "./audit-targets"
import { contentSourcePaths, PROJECT_ROOT } from "./cli/paths"
import { loadAllContent } from "./source-loader"

describe("selectCopyrightAuditNotes", () => {
  it("selects sanitized CLF and SAA notes after notes become public", async () => {
    // Given
    const bundle = await loadAllContent(contentSourcePaths(PROJECT_ROOT))

    // When
    const notes = selectCopyrightAuditNotes(bundle.studyNotes)

    // Then
    expect(notes).toHaveLength(49)
    expect(notes.every((note) => note.certificationCode !== "aif")).toBe(true)
  })
})
