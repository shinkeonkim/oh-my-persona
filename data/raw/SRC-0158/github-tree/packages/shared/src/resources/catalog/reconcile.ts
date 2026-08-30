import type { CertLabelFixture } from "./types"

/** Result of reconciling label fixtures against known slugs. */
export type ReconcileResult = {
  readonly certCode: string
  readonly totalLabels: number
  readonly uniqueLabels: number
  readonly mappedSlugs: number
  /** Official labels whose slug has no resource, feature, or alias definition. */
  readonly unmappedLabels: readonly string[]
  /** Slugs referenced in labels but absent from the known-slug set. */
  readonly danglingSlugRefs: readonly string[]
}

/**
 * Reconcile a cert's label fixture against a set of known slugs.
 * Compares the authoritative expected-label set (the fixture) to the explicit
 * slug definitions. If a label's slug is missing from knownSlugs, both the
 * exact official label text AND the slug are reported.
 */
export function reconcileFixture(
  fixture: CertLabelFixture,
  knownSlugs: ReadonlySet<string>,
): ReconcileResult {
  const uniqueLabels = new Set(fixture.labels.map(([label]) => label))
  const referencedSlugs = new Set(fixture.labels.map(([, , slug]) => slug))
  const unmappedLabels: string[] = []
  const danglingSlugRefs: string[] = []
  const seenDangling = new Set<string>()

  for (const [label, , slug] of fixture.labels) {
    if (!knownSlugs.has(slug) && !seenDangling.has(slug)) {
      seenDangling.add(slug)
      danglingSlugRefs.push(slug)
      unmappedLabels.push(label)
    }
  }

  return {
    certCode: fixture.certCode,
    totalLabels: fixture.labels.length,
    uniqueLabels: uniqueLabels.size,
    mappedSlugs: referencedSlugs.size,
    unmappedLabels,
    danglingSlugRefs,
  }
}

/** Collect all known slugs from resources, features, and aliases. */
export function collectKnownSlugs(
  resourceSlugs: readonly string[],
  featureSlugs: readonly string[],
  aliasSlugs: readonly string[],
): Set<string> {
  return new Set([...resourceSlugs, ...featureSlugs, ...aliasSlugs])
}
