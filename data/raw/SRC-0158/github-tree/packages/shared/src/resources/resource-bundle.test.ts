import { describe, expect, it } from "bun:test"
import {
  resourceDetailSchema,
  resourceGraphResponseSchema,
  resourceListResponseSchema,
} from "./resource-api"
import { resourceBundleSchema } from "./resource-bundle"

const ec2Resource = {
  slug: "amazon-ec2",
  title: "Amazon EC2",
  summary: "Elastic Compute Cloud",
  difficulty: "foundation",
  order: 1,
  prerequisites: [],
} as const

const s3Resource = {
  slug: "amazon-s3",
  title: "Amazon S3",
  summary: "Simple Storage Service",
  difficulty: "foundation",
  order: 2,
  prerequisites: [],
} as const

const iamResource = {
  slug: "aws-iam",
  title: "AWS IAM",
  summary: "Identity and Access Management",
  difficulty: "foundation",
  order: 0,
  prerequisites: [],
} as const

const validBundle = {
  resources: [iamResource, ec2Resource, s3Resource],
  features: [
    {
      slug: "ec2-auto-scaling",
      parentSlug: "amazon-ec2",
      title: "EC2 Auto Scaling",
      summary: "Automatic scaling",
      order: 0,
    },
  ],
  aliases: [{ alias: "s3", canonicalSlug: "amazon-s3" }],
  edges: [{ from: "amazon-ec2", to: "amazon-s3", type: "stores" }],
  assets: [
    {
      id: "ec2-concept-pdf",
      resourceSlug: "amazon-ec2",
      kind: "pdf",
      access: "public",
      title: "EC2 Concepts",
      checksum: `sha256:${"a".repeat(64)}`,
      sourceIdentity: "concepts/ec2.pdf",
    },
  ],
  certRelevance: [{ resourceSlug: "amazon-ec2", certificationCode: "saa", domainCode: "D1" }],
} as const

describe("resourceBundleSchema: valid bundle", () => {
  it("parses a complete valid bundle when given 3 resources with edges/features/aliases", () => {
    const result = resourceBundleSchema.safeParse(validBundle)
    expect(result.success).toBeTrue()
    if (result.success) {
      expect(result.data.resources).toHaveLength(3)
      expect(result.data.edges).toHaveLength(1)
      expect(result.data.features).toHaveLength(1)
      expect(result.data.aliases).toHaveLength(1)
    }
  })

  it("parses minimal bundle when given single resource with no relations", () => {
    const minimal = {
      resources: [iamResource],
      features: [],
      aliases: [],
      edges: [],
      assets: [],
      certRelevance: [],
    }
    expect(resourceBundleSchema.safeParse(minimal).success).toBeTrue()
  })
})

describe("resourceBundleSchema: duplicate slug rejection", () => {
  it("rejects when given two resources with the same slug", () => {
    const bundle = { ...validBundle, resources: [ec2Resource, ec2Resource, s3Resource] }
    const result = resourceBundleSchema.safeParse(bundle)
    expect(result.success).toBeFalse()
  })

  it("rejects when given an alias slug that matches a resource slug", () => {
    const bundle = {
      ...validBundle,
      aliases: [{ alias: "amazon-ec2", canonicalSlug: "amazon-s3" }],
    }
    const result = resourceBundleSchema.safeParse(bundle)
    expect(result.success).toBeFalse()
  })

  it("rejects when given two aliases with the same slug", () => {
    const bundle = {
      ...validBundle,
      aliases: [
        { alias: "s3", canonicalSlug: "amazon-s3" },
        { alias: "s3", canonicalSlug: "amazon-ec2" },
      ],
    }
    const result = resourceBundleSchema.safeParse(bundle)
    expect(result.success).toBeFalse()
  })
})

describe("resourceBundleSchema: dangling reference rejection", () => {
  it("rejects when given a prerequisite referencing a non-existent resource", () => {
    const danglingPrereq = {
      ...validBundle,
      resources: [{ ...ec2Resource, prerequisites: ["aws-lambda"] }, s3Resource, iamResource],
    }
    const result = resourceBundleSchema.safeParse(danglingPrereq)
    expect(result.success).toBeFalse()
  })

  it("rejects when given an edge with a non-existent 'from' endpoint", () => {
    const danglingEdge = {
      ...validBundle,
      edges: [{ from: "aws-lambda", to: "amazon-s3", type: "stores" }],
    }
    const result = resourceBundleSchema.safeParse(danglingEdge)
    expect(result.success).toBeFalse()
  })

  it("rejects when given an edge with a non-existent 'to' endpoint", () => {
    const danglingEdge = {
      ...validBundle,
      edges: [{ from: "amazon-ec2", to: "aws-lambda", type: "stores" }],
    }
    const result = resourceBundleSchema.safeParse(danglingEdge)
    expect(result.success).toBeFalse()
  })

  it("rejects when given a feature with a non-existent parent slug", () => {
    const danglingFeature = {
      ...validBundle,
      features: [
        {
          slug: "lambda-layers",
          parentSlug: "aws-lambda",
          title: "Lambda Layers",
          summary: "Layers",
          order: 0,
        },
      ],
    }
    const result = resourceBundleSchema.safeParse(danglingFeature)
    expect(result.success).toBeFalse()
  })

  it("rejects when given an alias targeting a non-existent canonical slug", () => {
    const danglingAlias = {
      ...validBundle,
      aliases: [{ alias: "compute", canonicalSlug: "aws-lambda" }],
    }
    const result = resourceBundleSchema.safeParse(danglingAlias)
    expect(result.success).toBeFalse()
  })

  it("rejects when given an asset referencing a non-existent resource slug", () => {
    const danglingAsset = {
      ...validBundle,
      assets: [
        {
          id: "lambda-pdf",
          resourceSlug: "aws-lambda",
          kind: "pdf",
          access: "public",
          title: "Lambda",
          checksum: `sha256:${"b".repeat(64)}`,
          sourceIdentity: "lambda.pdf",
        },
      ],
    }
    const result = resourceBundleSchema.safeParse(danglingAsset)
    expect(result.success).toBeFalse()
  })
})

describe("resourceGraphResponseSchema", () => {
  it("parses a valid graph response when given nodes and edges", () => {
    const graph = {
      nodes: [
        {
          slug: "amazon-ec2",
          title: "Amazon EC2",
          summary: "Compute",
          difficulty: "foundation",
          order: 1,
          certRelevance: [],
        },
      ],
      edges: [{ from: "amazon-ec2", to: "amazon-s3", type: "stores" }],
    }
    const result = resourceGraphResponseSchema.safeParse(graph)
    expect(result.success).toBeTrue()
  })
})

describe("resourceListResponseSchema", () => {
  it("parses a valid list response when given resources and total", () => {
    const list = {
      resources: [
        {
          slug: "amazon-ec2",
          title: "Amazon EC2",
          summary: "Compute",
          difficulty: "foundation",
          order: 1,
          certRelevance: [],
        },
      ],
      total: 1,
    }
    const result = resourceListResponseSchema.safeParse(list)
    expect(result.success).toBeTrue()
    if (result.success) {
      expect(result.data.total).toBe(1)
    }
  })
})

describe("resourceDetailSchema", () => {
  it("parses a valid detail response when given resource with relations", () => {
    const detail = {
      resource: ec2Resource,
      features: [],
      edges: [],
      assets: [],
      certRelevance: [{ resourceSlug: "amazon-ec2", certificationCode: "saa", domainCode: "D1" }],
    }
    const result = resourceDetailSchema.safeParse(detail)
    expect(result.success).toBeTrue()
  })
})
