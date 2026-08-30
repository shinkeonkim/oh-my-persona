import { describe, expect, it } from "bun:test"

import { resourceBundleSchema } from "../resource-bundle"
import { AIF_LABELS } from "./aif-labels"
import { AIF_OBJECTIVE_LABELS } from "./aif-objective-labels"
import { buildCatalogBundle } from "./build-bundle"
import { ALL_CERT_DOMAINS } from "./cert-domains"
import { CLF_LABELS } from "./clf-labels"
import { CATALOG_FEATURES } from "./features-aliases"
import { detectPrerequisiteCycles, findUnreachableResources } from "./graph-validate"
import { collectKnownSlugs, reconcileFixture } from "./reconcile"
import { ADVANCED_RESOURCES } from "./resources-advanced"
import { FOUNDATION_RESOURCES } from "./resources-foundation"
import { SAA_LABELS } from "./saa-labels"
import { parseFeature, parseResource } from "./types"

const ALL_RESOURCE_TUPLES = [...FOUNDATION_RESOURCES, ...ADVANCED_RESOURCES]
const ALL_RESOURCES = ALL_RESOURCE_TUPLES.map(parseResource)
const ALL_FEATURES = CATALOG_FEATURES.map(parseFeature)
const RESOURCE_SLUGS = ALL_RESOURCES.map((r) => r.slug)
const FEATURE_SLUGS = ALL_FEATURES.map((f) => f.slug)
const KNOWN_SLUGS = collectKnownSlugs(RESOURCE_SLUGS, FEATURE_SLUGS, [])
const FEATURE_PARENT = new Map(CATALOG_FEATURES.map((f) => [f[0], f[1]]))

function resolveToCanonical(slug: string): string {
  return FEATURE_PARENT.get(slug) ?? slug
}

describe("Zero omitted official labels", () => {
  it("every AIF in-scope label slug exists as a resource or feature", () => {
    const result = reconcileFixture(AIF_LABELS, KNOWN_SLUGS)
    expect(result.danglingSlugRefs).toEqual([])
    expect(result.unmappedLabels).toEqual([])
  })

  it("every CLF label slug exists as a resource or feature", () => {
    const result = reconcileFixture(CLF_LABELS, KNOWN_SLUGS)
    expect(result.danglingSlugRefs).toEqual([])
    expect(result.unmappedLabels).toEqual([])
  })

  it("every SAA label slug exists as a resource or feature", () => {
    const result = reconcileFixture(SAA_LABELS, KNOWN_SLUGS)
    expect(result.danglingSlugRefs).toEqual([])
    expect(result.unmappedLabels).toEqual([])
  })

  it("every AIF objective-only label slug exists as a resource or feature", () => {
    const result = reconcileFixture(AIF_OBJECTIVE_LABELS, KNOWN_SLUGS)
    expect(result.danglingSlugRefs).toEqual([])
  })
})

describe("Canonical cert relevance (#2)", () => {
  it("every certRelevance resourceSlug is a canonical resource", () => {
    const bundle = buildCatalogBundle()
    const canonicalSlugs = new Set(bundle.resources.map((r) => r.slug))
    const nonCanonical = bundle.certRelevance.filter((cr) => !canonicalSlugs.has(cr.resourceSlug))
    expect(nonCanonical.map((cr) => cr.resourceSlug)).toEqual([])
  })

  it("JumpStart relevance resolves to SageMaker AI parent", () => {
    const bundle = buildCatalogBundle()
    const aifRel = bundle.certRelevance.filter((r) => r.certificationCode === "aif")
    const hasSagemaker = aifRel.some((r) => r.resourceSlug === "amazon-sagemaker-ai")
    const hasJumpstart = aifRel.some((r) => r.resourceSlug === "amazon-sagemaker-jumpstart")
    expect(hasSagemaker).toBeTrue()
    expect(hasJumpstart).toBeFalse()
  })

  it("Guardrails relevance resolves to Bedrock parent", () => {
    const bundle = buildCatalogBundle()
    const aifObjRel = bundle.certRelevance.filter((r) => r.certificationCode === "aif")
    const hasGuardrailsRaw = aifObjRel.some((r) => r.resourceSlug === "bedrock-guardrails")
    expect(hasGuardrailsRaw).toBeFalse()
  })

  it("every label canonical parent has cert relevance", () => {
    const bundle = buildCatalogBundle()
    for (const fixture of [AIF_LABELS, CLF_LABELS, SAA_LABELS]) {
      const relSlugs = new Set(
        bundle.certRelevance
          .filter((r) => r.certificationCode === fixture.certCode)
          .map((r) => r.resourceSlug),
      )
      const canonicalSlugs = new Set(fixture.labels.map(([, , s]) => resolveToCanonical(s)))
      const missing = [...canonicalSlugs].filter((s) => !relSlugs.has(s))
      expect(missing).toEqual([])
    }
  })
})

describe("Official exam domain validity (#3)", () => {
  it("every certRelevance domainCode exists in ALL_CERT_DOMAINS for that cert", () => {
    const bundle = buildCatalogBundle()
    const validDomains = new Map<string, Set<string>>()
    for (const d of ALL_CERT_DOMAINS) {
      const set = validDomains.get(d.certificationCode) ?? new Set()
      set.add(d.domainCode)
      validDomains.set(d.certificationCode, set)
    }
    const invalid = bundle.certRelevance.filter((cr) => {
      const domains = validDomains.get(cr.certificationCode)
      return !domains?.has(cr.domainCode)
    })
    expect(invalid.map((cr) => `${cr.certificationCode}:${cr.domainCode}`)).toEqual([])
  })
})

describe("AIF v1.1 coverage (#4)", () => {
  const allAifSlugs = new Set(AIF_LABELS.labels.map(([, , s]) => s))

  it("MemoryDB is absent from AIF labels", () => {
    const labels = AIF_LABELS.labels.map(([l]) => l)
    expect(labels.some((l) => l.toLowerCase().includes("memorydb"))).toBeFalse()
  })

  it("v1.1 additions are present", () => {
    const expected = [
      "amazon-aurora",
      "amazon-bedrock-agentcore",
      "kiro",
      "strands-agents",
      "amazon-q",
      "amazon-sagemaker-jumpstart",
      "aws-transform",
    ]
    for (const slug of expected) {
      expect(allAifSlugs.has(slug)).toBeTrue()
    }
  })

  it("objective-only labels are distinct from in-scope 55", () => {
    expect(AIF_LABELS.labels.length).toBe(55)
    expect(AIF_OBJECTIVE_LABELS.labels.length).toBe(8)
  })

  it("preserves exact objective-only AWS labels", () => {
    const labels = AIF_OBJECTIVE_LABELS.labels.map(([label]) => label)
    expect(labels).toContain("Amazon Bedrock Guardrails")
    expect(labels).toContain("Amazon Bedrock AgentCore Identity")
    expect(labels).toContain("Amazon SageMaker Model Cards")
  })
})

describe("Unique article target per node", () => {
  it("no duplicate canonical resource slugs", () => {
    expect(new Set(RESOURCE_SLUGS).size).toBe(RESOURCE_SLUGS.length)
  })

  it("no feature slug collides with a resource slug", () => {
    const resourceSet = new Set(RESOURCE_SLUGS)
    expect(FEATURE_SLUGS.filter((s) => resourceSet.has(s))).toEqual([])
  })
})

describe("Prerequisite graph integrity", () => {
  it("no cycles in prerequisite graph", () => {
    expect(detectPrerequisiteCycles(ALL_RESOURCES)).toEqual([])
  })

  it("all resources reachable from foundation roots", () => {
    expect(findUnreachableResources(ALL_RESOURCES)).toEqual([])
  })
})

describe("Bundle schema validation", () => {
  it("complete catalog bundle passes resourceBundleSchema", () => {
    const result = resourceBundleSchema.safeParse(buildCatalogBundle())
    if (!result.success) {
      console.error(
        "Bundle errors:",
        result.error.issues.map((i) => i.message),
      )
    }
    expect(result.success).toBeTrue()
  })

  it("bundle has all three difficulty levels", () => {
    const difficulties = new Set(buildCatalogBundle().resources.map((r) => r.difficulty))
    expect(difficulties.has("foundation")).toBeTrue()
    expect(difficulties.has("advanced")).toBeTrue()
    expect(difficulties.has("applied")).toBeTrue()
  })
})

describe("No duplicate feature/alias roots", () => {
  it("no alias slug collides with a resource or feature slug", () => {
    const bundle = buildCatalogBundle()
    const all = new Set([
      ...bundle.resources.map((r) => r.slug),
      ...bundle.features.map((f) => f.slug),
    ])
    expect(bundle.aliases.filter((a) => all.has(a.alias)).map((a) => a.alias)).toEqual([])
  })
})
