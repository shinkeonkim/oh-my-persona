import { describe, expect, it } from "bun:test"

import { loginDestination } from "./auth-destination"

describe("loginDestination", () => {
  it("returns home when the account is pending", () => {
    const destination = loginDestination("pending", "/dashboard")

    expect(destination).toBe("/")
  })

  it("preserves the requested route when the account is approved", () => {
    const destination = loginDestination("reader", "/saa/quiz")

    expect(destination).toBe("/saa/quiz")
  })

  it("preserves the requested route for administrators", () => {
    const destination = loginDestination("admin", "/admin")

    expect(destination).toBe("/admin")
  })
})
