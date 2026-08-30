import { describe, expect, it } from "bun:test"

import { auditSource, countPureLines } from "./check-file-size"

describe("countPureLines", () => {
  it("ignores blank and comment-only lines", () => {
    // Given
    const source = ["const first = 1", "", "// comment", "  # shell comment", "const second = 2"]

    // When
    const count = countPureLines(source.join("\n"))

    // Then
    expect(count).toBe(2)
  })
})

describe("auditSource", () => {
  it("rejects source above the configured limit", () => {
    // Given
    const source = Array.from({ length: 251 }, (_, index) => `const value${index} = ${index}`)

    // When
    const result = auditSource("src/oversized.ts", source.join("\n"), 250)

    // Then
    expect(result).toEqual({ path: "src/oversized.ts", pureLines: 251, limit: 250 })
  })

  it("accepts source at the configured limit", () => {
    // Given
    const source = Array.from({ length: 250 }, (_, index) => `const value${index} = ${index}`)

    // When
    const result = auditSource("src/allowed.ts", source.join("\n"), 250)

    // Then
    expect(result).toBeNull()
  })
})
