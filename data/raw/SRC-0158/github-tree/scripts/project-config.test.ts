import { describe, expect, it } from "bun:test"

import apiPackage from "../apps/api/package.json"
import nextConfig from "../apps/web/next.config"
import rootPackage from "../package.json"

describe("development command", () => {
  it("loads safe defaults and optional local overrides before starting workspaces", () => {
    // Given
    const command = rootPackage.scripts.dev

    // When
    const tokens = command.split(" ")

    // Then
    expect(tokens).toContain("--env-file=.env.example")
    expect(tokens).toContain("--env-file=.env")
  })
})

describe("API development command", () => {
  it("builds legacy decorators with TypeScript before Bun watches compiled output", () => {
    // Given
    const scripts = apiPackage.scripts

    // When
    const developmentCommand = scripts.dev

    // Then
    expect(developmentCommand).toContain("tsc -p tsconfig.json")
    expect(scripts["dev:serve"]).toBe("bun --watch dist/main.js")
  })
})

describe("production ingress policy", () => {
  it("allows Cloudflare Tunnel to reach the web workload", async () => {
    // Given
    const policy = await Bun.file(
      "deploy/charts/aws-study-site/templates/networkpolicy.yaml",
    ).text()

    // When
    const tunnelNamespaceIsAllowed = policy.includes(
      "kubernetes.io/metadata.name: cloudflare-tunnel",
    )

    // Then
    expect(tunnelNamespaceIsAllowed).toBe(true)
  })
})

describe("production API proxy", () => {
  it("routes public API paths to the internal API service", async () => {
    // Given
    const previousApiUrl = process.env["API_INTERNAL_URL"]
    process.env["API_INTERNAL_URL"] = "http://api.internal:3001/api/"

    try {
      // When
      const rewrites = await nextConfig.rewrites?.()

      // Then
      expect(rewrites).toEqual([
        {
          source: "/api/:path*",
          destination: "http://api.internal:3001/api/:path*",
        },
        {
          source: "/healthz",
          destination: "http://api.internal:3001/healthz",
        },
        {
          source: "/readyz",
          destination: "http://api.internal:3001/readyz",
        },
      ])
    } finally {
      if (previousApiUrl === undefined) delete process.env["API_INTERNAL_URL"]
      else process.env["API_INTERNAL_URL"] = previousApiUrl
    }
  })

  it("builds the web image with the production API service name", async () => {
    // Given
    const dockerfile = await Bun.file("docker/Dockerfile.web").text()

    // When
    const serviceReferences = dockerfile.match(/aws-study-site-api/g) ?? []

    // Then
    expect(serviceReferences).toHaveLength(2)
  })
})
