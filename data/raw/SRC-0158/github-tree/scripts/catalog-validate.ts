import {
  ADVANCED_RESOURCES,
  AIF_LABELS,
  AIF_OBJECTIVE_LABELS,
  ALL_CERT_DOMAINS,
  buildCatalogBundle,
  CATALOG_ALIASES,
  CATALOG_FEATURES,
  CLF_LABELS,
  collectKnownSlugs,
  detectPrerequisiteCycles,
  FOUNDATION_RESOURCES,
  findUnreachableResources,
  parseFeature,
  parseResource,
  reconcileFixture,
  SAA_LABELS,
} from "../packages/shared/src/resources/catalog/index"

function check(label: string, ok: boolean, detail?: string): boolean {
  const tag = ok ? "OK" : "FAIL"
  console.log(`  ${label}: [${tag}]${detail ? ` ${detail}` : ""}`)
  return ok
}

function main(): void {
  console.log("=== AWS Resource Catalog Validator ===\n")
  const bundle = buildCatalogBundle()
  console.log(
    `Resources: ${bundle.resources.length}  Features: ${bundle.features.length}  Aliases: ${bundle.aliases.length}`,
  )
  console.log(`Edges: ${bundle.edges.length}  CertRelevance: ${bundle.certRelevance.length}`)
  const d = { f: 0, a: 0, p: 0 }
  for (const r of bundle.resources) {
    if (r.difficulty === "foundation") d.f++
    else if (r.difficulty === "advanced") d.a++
    else d.p++
  }
  console.log(`Difficulty: foundation=${d.f} advanced=${d.a} applied=${d.p}`)

  let pass = true
  const allTuples = [...FOUNDATION_RESOURCES, ...ADVANCED_RESOURCES]
  const rSlugs = allTuples.map((t) => t[0])
  const fSlugs = CATALOG_FEATURES.map((t) => t[0])
  const aSlugs = CATALOG_ALIASES.map((t) => t[0])
  const known = collectKnownSlugs(rSlugs, fSlugs, aSlugs)

  // 1. Service-list reconciliation
  console.log("\n--- Service-List Reconciliation ---")
  for (const fix of [AIF_LABELS, CLF_LABELS, SAA_LABELS]) {
    const r = reconcileFixture(fix, known)
    const ok = r.danglingSlugRefs.length === 0 && r.unmappedLabels.length === 0
    if (
      !check(
        `${fix.certCode.toUpperCase()} (${r.totalLabels} entries, ${r.uniqueLabels} unique)`,
        ok,
      )
    ) {
      console.log(`    Omitted labels: ${r.unmappedLabels.join(", ")}`)
      pass = false
    }
  }

  // 2. Objective-only reconciliation
  console.log("\n--- Objective-Only Reconciliation ---")
  const objR = reconcileFixture(AIF_OBJECTIVE_LABELS, known)
  if (
    !check(`AIF objective-only (${objR.totalLabels} labels)`, objR.danglingSlugRefs.length === 0)
  ) {
    console.log(`    Omitted: ${objR.unmappedLabels.join(", ")}`)
    pass = false
  }

  // 3. Canonicalized relevance
  console.log("\n--- Canonicalized Cert Relevance ---")
  const canonical = new Set(bundle.resources.map((r) => r.slug))
  const nonCanon = bundle.certRelevance.filter((cr) => !canonical.has(cr.resourceSlug))
  if (!check("All relevance slugs canonical", nonCanon.length === 0)) {
    console.log(`    Non-canonical: ${nonCanon.map((c) => c.resourceSlug).join(", ")}`)
    pass = false
  }

  // 4. Official-domain validity
  console.log("\n--- Official Domain Validity ---")
  const validDomains = new Map<string, Set<string>>()
  for (const dom of ALL_CERT_DOMAINS) {
    const s = validDomains.get(dom.certificationCode) ?? new Set()
    s.add(dom.domainCode)
    validDomains.set(dom.certificationCode, s)
  }
  const badDomain = bundle.certRelevance.filter((cr) => {
    const s = validDomains.get(cr.certificationCode)
    return !s?.has(cr.domainCode)
  })
  if (!check("All domainCodes in ALL_CERT_DOMAINS", badDomain.length === 0)) {
    console.log(
      `    Invalid: ${badDomain.map((c) => `${c.certificationCode}:${c.domainCode}`).join(", ")}`,
    )
    pass = false
  }

  // 5. Graph validation
  console.log("\n--- Graph Validation ---")
  const resources = allTuples.map(parseResource)
  const cycles = detectPrerequisiteCycles(resources)
  if (!check("No prerequisite cycles", cycles.length === 0)) {
    for (const c of cycles) console.log(`    Cycle: ${c.join(" -> ")}`)
    pass = false
  }
  const unreach = findUnreachableResources(resources)
  if (!check("All nodes reachable", unreach.length === 0)) {
    console.log(`    Unreachable: ${unreach.join(", ")}`)
    pass = false
  }
  const features = CATALOG_FEATURES.map(parseFeature)
  const rSet = new Set(rSlugs)
  const orphans = features.filter((f) => !rSet.has(f.parentSlug))
  if (!check("No orphan features", orphans.length === 0)) {
    pass = false
  }

  console.log(`\n=== Result: ${pass ? "PASS" : "FAIL"} ===`)
  process.exit(pass ? 0 : 1)
}

main()
