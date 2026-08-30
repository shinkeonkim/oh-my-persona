import { FOUNDATION_CORE } from "./res-foundation-core"
import { FOUNDATION_DATA_ML } from "./res-foundation-data-ml"
import { FOUNDATION_INFRA } from "./res-foundation-infra"
import type { ResourceTuple } from "./types"

/**
 * All foundation-level canonical resources combined.
 * Split across sub-files to stay under 250 pure LOC.
 */
export const FOUNDATION_RESOURCES: readonly ResourceTuple[] = [
  ...FOUNDATION_CORE,
  ...FOUNDATION_INFRA,
  ...FOUNDATION_DATA_ML,
]
