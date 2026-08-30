import type { ResourceBundle } from "../resource-bundle"
import { resourceBundleSchema } from "../resource-bundle"
import type { CertResourceRelevance } from "../resource-curriculum"
import { AIF_LABELS } from "./aif-labels"
import { AIF_OBJECTIVE_LABELS } from "./aif-objective-labels"
import { resolveRequiredExamDomain } from "./category-to-domain"
import { CLF_LABELS } from "./clf-labels"
import { CATALOG_EDGES } from "./edges"
import { CATALOG_ALIASES, CATALOG_FEATURES } from "./features-aliases"
import { ADVANCED_RESOURCES } from "./resources-advanced"
import { FOUNDATION_RESOURCES } from "./resources-foundation"
import { SAA_LABELS } from "./saa-labels"
import type { CertLabelFixture, FeatureTuple } from "./types"
import { parseAlias, parseEdge, parseFeature, parseResource } from "./types"

/** Build slug→canonical-parent lookup from features and aliases. */
function buildCanonicalResolver(
  features: readonly FeatureTuple[],
  aliases: readonly (readonly [string, string])[],
): ReadonlyMap<string, string> {
  const map = new Map<string, string>()
  for (const f of features) map.set(f[0], f[1])
  for (const a of aliases) map.set(a[0], a[1])
  return map
}

/** Resolve a slug to its canonical resource root. */
function toCanonical(slug: string, resolver: ReadonlyMap<string, string>): string {
  return resolver.get(slug) ?? slug
}

/** Derive cert relevance, resolving features/aliases to canonical parents. */
function deriveCertRelevance(
  fixtures: readonly CertLabelFixture[],
  resolver: ReadonlyMap<string, string>,
): CertResourceRelevance[] {
  const seen = new Set<string>()
  const result: CertResourceRelevance[] = []
  for (const fixture of fixtures) {
    for (const [, serviceCategory, slug, explicitExamDomain] of fixture.labels) {
      const canonicalSlug = toCanonical(slug, resolver)
      const domainCode =
        explicitExamDomain ?? resolveRequiredExamDomain(fixture.certCode, serviceCategory)
      const key = `${canonicalSlug}:${fixture.certCode}:${domainCode}`
      if (!seen.has(key)) {
        seen.add(key)
        result.push({
          resourceSlug: canonicalSlug,
          certificationCode: fixture.certCode,
          domainCode,
        })
      }
    }
  }
  return result
}

/** Build the complete resource bundle from catalog data. */
export function buildCatalogBundle(): ResourceBundle {
  const allResourceTuples = [...FOUNDATION_RESOURCES, ...ADVANCED_RESOURCES]
  const resources = allResourceTuples.map(parseResource)
  const features = CATALOG_FEATURES.map(parseFeature)
  const aliases = CATALOG_ALIASES.map(parseAlias)
  const edges = CATALOG_EDGES.map(parseEdge)
  const resolver = buildCanonicalResolver(CATALOG_FEATURES, CATALOG_ALIASES)
  const allFixtures = [AIF_LABELS, CLF_LABELS, SAA_LABELS, AIF_OBJECTIVE_LABELS]
  const certRelevance = deriveCertRelevance(allFixtures, resolver)

  return resourceBundleSchema.parse({
    resources,
    features,
    aliases,
    edges,
    assets: [],
    certRelevance,
  })
}
