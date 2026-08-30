import type { CertificationCode } from "../../certifications"
import type { AliasTarget, ChildFeature, ResourceEdge } from "../resource-relations"
import type { CanonicalResource, Difficulty } from "../resource-root"

/**
 * Compact tuple for official label fixtures.
 * [officialLabel, serviceCategory, mappedSlug, explicitExamDomain?]
 */
export type ExamDomainCode = "D1" | "D2" | "D3" | "D4" | "D5"

export type OfficialLabelTuple = readonly [
  label: string,
  serviceCategory: string,
  slug: string,
  explicitExamDomain?: ExamDomainCode,
]

/**
 * Compact tuple for canonical resources.
 * [slug, title, summary, difficulty, order, prerequisites]
 */
export type ResourceTuple = readonly [
  slug: string,
  title: string,
  summary: string,
  difficulty: Difficulty,
  order: number,
  prerequisites: readonly string[],
]

/**
 * Compact tuple for child features.
 * [slug, parentSlug, title, summary, order]
 */
export type FeatureTuple = readonly [
  slug: string,
  parentSlug: string,
  title: string,
  summary: string,
  order: number,
]

/** Parse a ResourceTuple into a CanonicalResource. */
export function parseResource(t: ResourceTuple): CanonicalResource {
  return {
    slug: t[0],
    title: t[1],
    summary: t[2],
    difficulty: t[3],
    order: t[4],
    prerequisites: [...t[5]],
  }
}

/** Parse a FeatureTuple into a ChildFeature. */
export function parseFeature(t: FeatureTuple): ChildFeature {
  return { slug: t[0], parentSlug: t[1], title: t[2], summary: t[3], order: t[4] }
}

/** Per-cert label fixture with metadata. */
export type CertLabelFixture = {
  readonly certCode: CertificationCode
  readonly sourceUrl: string
  readonly fetchDate: string
  readonly labels: readonly OfficialLabelTuple[]
}

/** Parse alias shorthand [alias, canonicalSlug] into AliasTarget. */
export function parseAlias(t: readonly [string, string]): AliasTarget {
  return { alias: t[0], canonicalSlug: t[1] }
}

/** Parse edge shorthand [from, to, type] into ResourceEdge. */
export function parseEdge(t: readonly [string, string, ResourceEdge["type"]]): ResourceEdge {
  return { from: t[0], to: t[1], type: t[2] }
}
