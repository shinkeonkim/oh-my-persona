import { describe, expect, it } from "bun:test"

import { parseEnvironment } from "./env"

describe("parseEnvironment", () => {
  it("applies safe local defaults", () => {
    // Given
    const input = {
      DATABASE_URL: "postgresql://awsstudy:awsstudy@localhost:5432/awsstudy",
      JWT_SECRET: "01234567890123456789012345678901",
    }

    // When
    const environment = parseEnvironment(input)

    // Then
    expect(environment.PORT).toBe(3001)
    expect(environment.WEB_ORIGIN).toBe("http://localhost:3000")
  })

  it("rejects a short JWT secret", () => {
    // Given
    const input = {
      DATABASE_URL: "postgresql://awsstudy:awsstudy@localhost:5432/awsstudy",
      JWT_SECRET: "short",
    }

    // When
    const result = () => parseEnvironment(input)

    // Then
    expect(result).toThrow()
  })
})
