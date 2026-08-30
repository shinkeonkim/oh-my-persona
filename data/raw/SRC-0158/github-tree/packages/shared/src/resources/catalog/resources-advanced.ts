import { ADVANCED_COMPUTE_ML } from "./res-advanced-compute-ml"
import { ADVANCED_ML_MIGRATION } from "./res-advanced-ml-migration"
import { ADVANCED_NETWORKING_SECURITY } from "./res-advanced-networking-security"
import { APPLIED_RESOURCES } from "./res-applied"
import type { ResourceTuple } from "./types"

/**
 * All advanced and applied canonical resources combined.
 * Split across sub-files to stay under 250 pure LOC.
 */
export const ADVANCED_RESOURCES: readonly ResourceTuple[] = [
  ...ADVANCED_NETWORKING_SECURITY,
  ...ADVANCED_COMPUTE_ML,
  ...ADVANCED_ML_MIGRATION,
  ...APPLIED_RESOURCES,
]
