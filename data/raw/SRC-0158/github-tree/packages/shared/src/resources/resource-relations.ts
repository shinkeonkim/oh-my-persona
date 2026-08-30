import { z } from "zod"

import { canonicalSlugSchema } from "./resource-root"

export const edgeTypeSchema = z.enum([
  "uses",
  "integrates-with",
  "secures",
  "observes",
  "stores",
  "computes",
  "delivers",
  "orchestrates",
])

export const resourceEdgeSchema = z.object({
  from: canonicalSlugSchema,
  to: canonicalSlugSchema,
  type: edgeTypeSchema,
})

export const childFeatureSchema = z.object({
  slug: canonicalSlugSchema,
  parentSlug: canonicalSlugSchema,
  title: z.string().min(1).max(200),
  summary: z.string().min(1).max(1000),
  order: z.number().int().nonnegative(),
})

export const aliasTargetSchema = z.object({
  alias: canonicalSlugSchema,
  canonicalSlug: canonicalSlugSchema,
})

export type EdgeType = z.infer<typeof edgeTypeSchema>
export type ResourceEdge = z.infer<typeof resourceEdgeSchema>
export type ChildFeature = z.infer<typeof childFeatureSchema>
export type AliasTarget = z.infer<typeof aliasTargetSchema>
