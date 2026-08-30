import type { CanonicalResource } from "../resource-root"

/** Detect cycles in the prerequisite graph. Returns list of cycle paths. */
export function detectPrerequisiteCycles(resources: readonly CanonicalResource[]): string[][] {
  const bySlug = new Map(resources.map((r) => [r.slug, r]))
  const visited = new Set<string>()
  const inStack = new Set<string>()
  const cycles: string[][] = []

  function dfs(slug: string, path: string[]): void {
    if (inStack.has(slug)) {
      const cycleStart = path.indexOf(slug)
      cycles.push([...path.slice(cycleStart), slug])
      return
    }
    if (visited.has(slug)) return
    visited.add(slug)
    inStack.add(slug)
    const resource = bySlug.get(slug)
    if (resource) {
      for (const prereq of resource.prerequisites) {
        dfs(prereq, [...path, slug])
      }
    }
    inStack.delete(slug)
  }

  for (const r of resources) {
    dfs(r.slug, [])
  }
  return cycles
}

/** Check that every resource is reachable from foundation roots (resources with no prerequisites). */
export function findUnreachableResources(resources: readonly CanonicalResource[]): string[] {
  const bySlug = new Map(resources.map((r) => [r.slug, r]))
  const dependents = new Map<string, string[]>()

  for (const r of resources) {
    for (const prereq of r.prerequisites) {
      const list = dependents.get(prereq) ?? []
      list.push(r.slug)
      dependents.set(prereq, list)
    }
  }

  const reachable = new Set<string>()
  const queue: string[] = []

  for (const r of resources) {
    if (r.prerequisites.length === 0) {
      reachable.add(r.slug)
      queue.push(r.slug)
    }
  }

  while (queue.length > 0) {
    const current = queue.shift()
    if (current === undefined) break
    const deps = dependents.get(current) ?? []
    for (const dep of deps) {
      if (reachable.has(dep)) continue
      const resource = bySlug.get(dep)
      if (resource?.prerequisites.every((p) => reachable.has(p))) {
        reachable.add(dep)
        queue.push(dep)
      }
    }
  }

  return resources.filter((r) => !reachable.has(r.slug)).map((r) => r.slug)
}
