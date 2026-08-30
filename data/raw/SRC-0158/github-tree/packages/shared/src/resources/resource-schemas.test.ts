import { describe, expect, it } from "bun:test"
import { contentAssetSchema } from "./resource-assets"
import {
  certDomainSchema,
  certResourceRelevanceSchema,
  coverageManifestSchema,
  curriculumEntrySchema,
} from "./resource-curriculum"
import {
  aliasTargetSchema,
  childFeatureSchema,
  edgeTypeSchema,
  resourceEdgeSchema,
} from "./resource-relations"
import { canonicalResourceSchema, canonicalSlugSchema, difficultySchema } from "./resource-root"

describe("canonicalSlugSchema", () => {
  it("accepts a valid lowercase slug when given 2+ alphanumeric/hyphen chars", () => {
    expect(canonicalSlugSchema.parse("amazon-s3")).toBe("amazon-s3")
    expect(canonicalSlugSchema.parse("ec2")).toBe("ec2")
  })

  it("rejects uppercase when given a slug with capitals", () => {
    expect(canonicalSlugSchema.safeParse("Amazon-S3").success).toBeFalse()
  })

  it("rejects single char when given a 1-char string", () => {
    expect(canonicalSlugSchema.safeParse("a").success).toBeFalse()
  })

  it("rejects leading hyphen when given -ec2", () => {
    expect(canonicalSlugSchema.safeParse("-ec2").success).toBeFalse()
  })

  it("rejects trailing hyphen when given ec2-", () => {
    expect(canonicalSlugSchema.safeParse("ec2-").success).toBeFalse()
  })
})

describe("difficultySchema", () => {
  it("accepts all three levels when given foundation/advanced/applied", () => {
    for (const level of ["foundation", "advanced", "applied"] as const) {
      expect(difficultySchema.parse(level)).toBe(level)
    }
  })

  it("rejects unknown difficulty when given 'beginner'", () => {
    expect(difficultySchema.safeParse("beginner").success).toBeFalse()
  })
})

describe("canonicalResourceSchema", () => {
  const validResource = {
    slug: "amazon-ec2",
    title: "Amazon EC2",
    summary: "Elastic Compute Cloud",
    difficulty: "foundation",
    order: 1,
    prerequisites: [],
  } as const

  it("parses a valid resource when given all required fields", () => {
    const result = canonicalResourceSchema.parse(validResource)
    expect(result.slug).toBe("amazon-ec2")
    expect(result.difficulty).toBe("foundation")
  })

  it("parses a resource with prerequisites when given valid prereq slugs", () => {
    const withPrereqs = { ...validResource, prerequisites: ["aws-iam"] }
    const result = canonicalResourceSchema.parse(withPrereqs)
    expect(result.prerequisites).toEqual(["aws-iam"])
  })

  it("rejects invalid difficulty when given 'easy'", () => {
    expect(
      canonicalResourceSchema.safeParse({ ...validResource, difficulty: "easy" }).success,
    ).toBeFalse()
  })

  it("rejects negative order when given -1", () => {
    expect(canonicalResourceSchema.safeParse({ ...validResource, order: -1 }).success).toBeFalse()
  })

  it("rejects empty title when given ''", () => {
    expect(canonicalResourceSchema.safeParse({ ...validResource, title: "" }).success).toBeFalse()
  })
})

describe("edgeTypeSchema", () => {
  it("accepts all valid edge types", () => {
    const types = [
      "uses",
      "integrates-with",
      "secures",
      "observes",
      "stores",
      "computes",
      "delivers",
      "orchestrates",
    ] as const
    for (const t of types) {
      expect(edgeTypeSchema.parse(t)).toBe(t)
    }
  })

  it("rejects unknown edge type when given 'connects'", () => {
    expect(edgeTypeSchema.safeParse("connects").success).toBeFalse()
  })
})

describe("resourceEdgeSchema", () => {
  it("parses a valid edge when given valid from/to/type", () => {
    const edge = { from: "amazon-ec2", to: "amazon-ebs", type: "uses" }
    expect(resourceEdgeSchema.parse(edge).type).toBe("uses")
  })

  it("rejects invalid edge type when given 'links'", () => {
    expect(
      resourceEdgeSchema.safeParse({ from: "amazon-ec2", to: "amazon-ebs", type: "links" }).success,
    ).toBeFalse()
  })
})

describe("childFeatureSchema", () => {
  it("parses a valid child feature when given all fields", () => {
    const feature = {
      slug: "ec2-auto-scaling",
      parentSlug: "amazon-ec2",
      title: "EC2 Auto Scaling",
      summary: "Automatic scaling for EC2",
      order: 0,
    }
    expect(childFeatureSchema.parse(feature).parentSlug).toBe("amazon-ec2")
  })
})

describe("aliasTargetSchema", () => {
  it("parses a valid alias when given alias and canonical slug", () => {
    const alias = { alias: "s3", canonicalSlug: "amazon-s3" }
    expect(aliasTargetSchema.parse(alias).canonicalSlug).toBe("amazon-s3")
  })
})

describe("contentAssetSchema", () => {
  const validAsset = {
    id: "saa-concept-ec2",
    resourceSlug: "amazon-ec2",
    kind: "pdf",
    access: "public",
    title: "EC2 Concepts",
    checksum: `sha256:${"a".repeat(64)}`,
    sourceIdentity: "content-sources/aws-saa-sutdy-notes/concepts/ec2.pdf",
  } as const

  it("parses a valid asset when given all fields", () => {
    const result = contentAssetSchema.parse(validAsset)
    expect(result.kind).toBe("pdf")
    expect(result.access).toBe("public")
  })

  it("rejects invalid access when given 'private'", () => {
    expect(contentAssetSchema.safeParse({ ...validAsset, access: "private" }).success).toBeFalse()
  })

  it("rejects invalid kind when given 'audio'", () => {
    expect(contentAssetSchema.safeParse({ ...validAsset, kind: "audio" }).success).toBeFalse()
  })

  it("rejects invalid checksum format when given bare hex", () => {
    expect(
      contentAssetSchema.safeParse({ ...validAsset, checksum: "a".repeat(64) }).success,
    ).toBeFalse()
  })
})

describe("certDomainSchema", () => {
  it("parses a valid cert domain when given all fields", () => {
    const domain = {
      certificationCode: "saa",
      domainCode: "D1",
      domainTitle: "Design Secure Architectures",
      weight: 30,
    }
    expect(certDomainSchema.parse(domain).weight).toBe(30)
  })

  it("rejects weight out of range when given 0 or 101", () => {
    const base = { certificationCode: "saa", domainCode: "D1", domainTitle: "T" }
    expect(certDomainSchema.safeParse({ ...base, weight: 0 }).success).toBeFalse()
    expect(certDomainSchema.safeParse({ ...base, weight: 101 }).success).toBeFalse()
  })
})

describe("certResourceRelevanceSchema", () => {
  it("parses valid relevance when given resource/cert/domain", () => {
    const rel = { resourceSlug: "amazon-ec2", certificationCode: "saa", domainCode: "D1" }
    expect(certResourceRelevanceSchema.parse(rel).domainCode).toBe("D1")
  })
})

describe("curriculumEntrySchema", () => {
  it("parses valid entry when given slug, difficulty, order, certRelevance", () => {
    const entry = {
      slug: "amazon-ec2",
      difficulty: "foundation",
      order: 1,
      certRelevance: [{ resourceSlug: "amazon-ec2", certificationCode: "saa", domainCode: "D1" }],
    }
    expect(curriculumEntrySchema.parse(entry).certRelevance).toHaveLength(1)
  })
})

describe("coverageManifestSchema", () => {
  it("parses SAA ground-truth manifest when given filesystem-verified counts", () => {
    // Given: SAA source truth — 24 study-notes/*.md files, 8 concept views,
    //        51 H2-derived resource sections, 1264 questions, 9 linked PDFs, 2 root PDFs
    const saaManifest = {
      certificationCode: "saa",
      counts: {
        "study-note": 24,
        "concept-view": 8,
        "resource-section": 51,
        question: 1264,
        "linked-pdf": 9,
        "root-pdf": 2,
      },
      totalSources: 24,
      totalDerived: 51,
    }

    // When
    const result = coverageManifestSchema.parse(saaManifest)

    // Then
    expect(result.counts["study-note"]).toBe(24)
  })

  it("rejects invalid classification key when given 'essay'", () => {
    const manifest = {
      certificationCode: "saa",
      counts: { essay: 5 },
      totalSources: 5,
      totalDerived: 0,
    }
    expect(coverageManifestSchema.safeParse(manifest).success).toBeFalse()
  })
})
