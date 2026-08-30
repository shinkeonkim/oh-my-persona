import { describe, expect, it } from "bun:test"

import { isContentReadRequest } from "./throttle-policy"

describe("isContentReadRequest", () => {
  it("skips content reads but keeps answer submissions throttled", () => {
    // Given
    const contentRead = ["GET", "/api/content/categories/aif"] as const
    const answerSubmission = ["POST", "/api/content/questions/id/answer"] as const

    // When
    const readResult = isContentReadRequest(...contentRead)
    const writeResult = isContentReadRequest(...answerSubmission)

    // Then
    expect(readResult).toBe(true)
    expect(writeResult).toBe(false)
  })
})
