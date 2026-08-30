import { describe, expect, it } from "bun:test"

import { resourceBundleSchema } from "./resource-bundle"

const VALID_BUNDLE = {
  resources: [
    {
      slug: "aws-iam",
      title: "AWS IAM",
      summary: "Identity and Access Management",
      difficulty: "foundation",
      order: 0,
      prerequisites: [],
    },
    {
      slug: "amazon-ec2",
      title: "Amazon EC2",
      summary: "Elastic Compute Cloud for scalable virtual servers",
      difficulty: "foundation",
      order: 1,
      prerequisites: ["aws-iam"],
    },
    {
      slug: "amazon-s3",
      title: "Amazon S3",
      summary: "Simple Storage Service for object storage",
      difficulty: "foundation",
      order: 2,
      prerequisites: ["aws-iam"],
    },
    {
      slug: "aws-lambda",
      title: "AWS Lambda",
      summary: "Serverless compute service",
      difficulty: "advanced",
      order: 3,
      prerequisites: ["aws-iam", "amazon-s3"],
    },
    {
      slug: "amazon-api-gateway",
      title: "Amazon API Gateway",
      summary: "Managed REST/WebSocket API service",
      difficulty: "applied",
      order: 4,
      prerequisites: ["aws-lambda"],
    },
  ],
  features: [
    {
      slug: "ec2-auto-scaling",
      parentSlug: "amazon-ec2",
      title: "EC2 Auto Scaling",
      summary: "Automatic scaling for EC2 instances",
      order: 0,
    },
    {
      slug: "s3-versioning",
      parentSlug: "amazon-s3",
      title: "S3 Versioning",
      summary: "Object version management",
      order: 0,
    },
  ],
  aliases: [
    { alias: "ec2", canonicalSlug: "amazon-ec2" },
    { alias: "s3", canonicalSlug: "amazon-s3" },
    { alias: "lambda", canonicalSlug: "aws-lambda" },
  ],
  edges: [
    { from: "amazon-ec2", to: "amazon-s3", type: "stores" as const },
    { from: "aws-lambda", to: "amazon-s3", type: "stores" as const },
    { from: "amazon-api-gateway", to: "aws-lambda", type: "integrates-with" as const },
    { from: "aws-iam", to: "amazon-ec2", type: "secures" as const },
    { from: "aws-iam", to: "aws-lambda", type: "secures" as const },
  ],
  assets: [
    {
      id: "ec2-concepts-pdf",
      resourceSlug: "amazon-ec2",
      kind: "pdf" as const,
      access: "public" as const,
      title: "EC2 Concepts Overview",
      checksum: `sha256:${"a".repeat(64)}`,
      sourceIdentity: "content-sources/aws-saa-sutdy-notes/concepts/ec2.pdf",
    },
    {
      id: "s3-questions-pdf",
      resourceSlug: "amazon-s3",
      kind: "pdf" as const,
      access: "protected" as const,
      title: "S3 Practice Questions",
      checksum: `sha256:${"b".repeat(64)}`,
      sourceIdentity: "content-sources/aws-saa-sutdy-notes/questions/s3.pdf",
    },
  ],
  certRelevance: [
    { resourceSlug: "aws-iam", certificationCode: "saa" as const, domainCode: "D1" },
    { resourceSlug: "amazon-ec2", certificationCode: "saa" as const, domainCode: "D2" },
    { resourceSlug: "amazon-s3", certificationCode: "saa" as const, domainCode: "D2" },
    { resourceSlug: "aws-lambda", certificationCode: "saa" as const, domainCode: "D3" },
    { resourceSlug: "amazon-ec2", certificationCode: "clf" as const, domainCode: "D3" },
  ],
}

describe("Manual QA: valid complete fixture", () => {
  it("parses and prints stable summary for a complete 5-resource bundle", () => {
    // Given: a complete valid bundle with 5 resources, 2 features, 3 aliases, 5 edges, 2 assets
    const input = VALID_BUNDLE

    // When: parsing through the bundle schema
    const result = resourceBundleSchema.safeParse(input)

    // Then: parse succeeds with exact counts
    expect(result.success).toBeTrue()
    if (!result.success) return

    const summary = {
      resources: result.data.resources.length,
      features: result.data.features.length,
      aliases: result.data.aliases.length,
      edges: result.data.edges.length,
      assets: result.data.assets.length,
      certRelevance: result.data.certRelevance.length,
      difficulties: {
        foundation: result.data.resources.filter((r) => r.difficulty === "foundation").length,
        advanced: result.data.resources.filter((r) => r.difficulty === "advanced").length,
        applied: result.data.resources.filter((r) => r.difficulty === "applied").length,
      },
      publicAssets: result.data.assets.filter((a) => a.access === "public").length,
      protectedAssets: result.data.assets.filter((a) => a.access === "protected").length,
    }

    console.log("=== VALID BUNDLE SUMMARY ===")
    console.log(JSON.stringify(summary, null, 2))

    expect(summary.resources).toBe(5)
    expect(summary.features).toBe(2)
    expect(summary.aliases).toBe(3)
    expect(summary.edges).toBe(5)
    expect(summary.assets).toBe(2)
    expect(summary.certRelevance).toBe(5)
    expect(summary.difficulties.foundation).toBe(3)
    expect(summary.difficulties.advanced).toBe(1)
    expect(summary.difficulties.applied).toBe(1)
    expect(summary.publicAssets).toBe(1)
    expect(summary.protectedAssets).toBe(1)
  })
})

describe("Manual QA: malformed duplicate/dangling fixture rejection", () => {
  it("rejects a bundle with duplicate resource slugs", () => {
    // Given: bundle with amazon-ec2 duplicated
    const duped = {
      ...VALID_BUNDLE,
      resources: [...VALID_BUNDLE.resources, VALID_BUNDLE.resources[1]],
    }

    // When
    const result = resourceBundleSchema.safeParse(duped)

    // Then
    expect(result.success).toBeFalse()
    if (!result.success) {
      console.log("=== DUPLICATE SLUG REJECTION ===")
      console.log(result.error.issues.map((i) => i.message).join("; "))
    }
  })

  it("rejects a bundle with dangling prerequisite", () => {
    // Given: ec2 references non-existent 'aws-kms' as prerequisite
    const dangling = {
      ...VALID_BUNDLE,
      resources: VALID_BUNDLE.resources.map((r) =>
        r.slug === "amazon-ec2" ? { ...r, prerequisites: ["aws-kms"] } : r,
      ),
    }

    // When
    const result = resourceBundleSchema.safeParse(dangling)

    // Then
    expect(result.success).toBeFalse()
    if (!result.success) {
      console.log("=== DANGLING PREREQUISITE REJECTION ===")
      console.log(result.error.issues.map((i) => i.message).join("; "))
    }
  })

  it("rejects a bundle with dangling edge endpoint", () => {
    // Given: edge references non-existent 'amazon-rds'
    const dangling = {
      ...VALID_BUNDLE,
      edges: [...VALID_BUNDLE.edges, { from: "amazon-ec2", to: "amazon-rds", type: "stores" }],
    }

    // When
    const result = resourceBundleSchema.safeParse(dangling)

    // Then
    expect(result.success).toBeFalse()
    if (!result.success) {
      console.log("=== DANGLING EDGE REJECTION ===")
      console.log(result.error.issues.map((i) => i.message).join("; "))
    }
  })

  it("rejects alias colliding with resource slug", () => {
    // Given: alias 'amazon-ec2' collides with existing resource
    const collision = {
      ...VALID_BUNDLE,
      aliases: [{ alias: "amazon-ec2", canonicalSlug: "amazon-s3" }],
    }

    // When
    const result = resourceBundleSchema.safeParse(collision)

    // Then
    expect(result.success).toBeFalse()
    if (!result.success) {
      console.log("=== ALIAS COLLISION REJECTION ===")
      console.log(result.error.issues.map((i) => i.message).join("; "))
    }
  })
})
