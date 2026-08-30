import { describe, expect, it } from "bun:test"

import { resourceBundleSchema } from "../resource-bundle"
import { AIF_LABELS } from "./aif-labels"
import { buildCatalogBundle } from "./build-bundle"
import { CatalogDomainMappingError, resolveRequiredExamDomain } from "./category-to-domain"
import { detectPrerequisiteCycles } from "./graph-validate"
import { collectKnownSlugs, reconcileFixture } from "./reconcile"
import { ADVANCED_RESOURCES } from "./resources-advanced"
import { FOUNDATION_RESOURCES } from "./resources-foundation"
import { parseResource } from "./types"

const RESOURCES = [...FOUNDATION_RESOURCES, ...ADVANCED_RESOURCES].map(parseResource)
const KNOWN_SLUGS = collectKnownSlugs(
  RESOURCES.map((resource) => resource.slug),
  buildCatalogBundle().features.map((feature) => feature.slug),
  [],
)

describe("catalog mutation rejection", () => {
  it("reports the official label when its catalog mapping is deleted", () => {
    const withoutS3 = new Set([...KNOWN_SLUGS].filter((slug) => slug !== "amazon-s3"))
    const result = reconcileFixture(AIF_LABELS, withoutS3)
    expect(result.unmappedLabels).toContain("Amazon S3")
    expect(result.danglingSlugRefs).toContain("amazon-s3")
  })

  it("detects a prerequisite cycle", () => {
    const ec2 = RESOURCES.find((resource) => resource.slug === "amazon-ec2")
    const lambda = RESOURCES.find((resource) => resource.slug === "aws-lambda")
    expect(ec2).toBeDefined()
    expect(lambda).toBeDefined()
    if (ec2 === undefined || lambda === undefined) return
    const mutated = [
      ...RESOURCES.filter(
        (resource) => resource.slug !== "amazon-ec2" && resource.slug !== "aws-lambda",
      ),
      { ...ec2, prerequisites: ["aws-lambda"] },
      { ...lambda, prerequisites: ["amazon-ec2"] },
    ]
    expect(detectPrerequisiteCycles(mutated).length).toBeGreaterThan(0)
  })

  it("rejects a dangling edge endpoint", () => {
    const bundle = buildCatalogBundle()
    const mutated = {
      ...bundle,
      edges: [
        ...bundle.edges,
        { from: "amazon-ec2", to: "nonexistent-svc", type: "uses" as const },
      ],
    }
    expect(resourceBundleSchema.safeParse(mutated).success).toBeFalse()
  })

  it("rejects duplicate resource and alias slugs", () => {
    const bundle = buildCatalogBundle()
    expect(
      resourceBundleSchema.safeParse({
        ...bundle,
        resources: [...bundle.resources, bundle.resources[0]],
      }).success,
    ).toBeFalse()
    expect(
      resourceBundleSchema.safeParse({
        ...bundle,
        aliases: [...bundle.aliases, { alias: "ec2", canonicalSlug: "amazon-s3" }],
      }).success,
    ).toBeFalse()
  })

  it("rejects feature duplicates and canonical collisions", () => {
    const bundle = buildCatalogBundle()
    expect(
      resourceBundleSchema.safeParse({
        ...bundle,
        features: [...bundle.features, bundle.features[0]],
      }).success,
    ).toBeFalse()
    expect(
      resourceBundleSchema.safeParse({
        ...bundle,
        features: [
          ...bundle.features,
          {
            slug: "amazon-s3",
            parentSlug: "amazon-s3",
            title: "Collision",
            summary: "Invalid duplicate identity",
            order: 99,
          },
        ],
      }).success,
    ).toBeFalse()
  })

  it("rejects a missing category-to-domain assignment", () => {
    expect(() => resolveRequiredExamDomain("aif", "missing-category")).toThrow(
      CatalogDomainMappingError,
    )
  })
})
