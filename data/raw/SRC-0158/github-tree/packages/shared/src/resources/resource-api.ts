import { z } from "zod"
import { contentAssetSchema } from "./resource-assets"
import { certResourceRelevanceSchema, coverageManifestSchema } from "./resource-curriculum"
import { childFeatureSchema, resourceEdgeSchema } from "./resource-relations"
import { canonicalResourceSchema } from "./resource-root"

export const resourceListItemSchema = z.object({
  slug: canonicalResourceSchema.shape.slug,
  title: canonicalResourceSchema.shape.title,
  summary: canonicalResourceSchema.shape.summary,
  difficulty: canonicalResourceSchema.shape.difficulty,
  order: canonicalResourceSchema.shape.order,
  certRelevance: z.array(certResourceRelevanceSchema).readonly(),
})

export const resourceDetailSchema = z.object({
  resource: canonicalResourceSchema,
  features: z.array(childFeatureSchema).readonly(),
  edges: z.array(resourceEdgeSchema).readonly(),
  assets: z.array(contentAssetSchema).readonly(),
  certRelevance: z.array(certResourceRelevanceSchema).readonly(),
})

export const resourceGraphResponseSchema = z.object({
  nodes: z.array(resourceListItemSchema).readonly(),
  edges: z.array(resourceEdgeSchema).readonly(),
})

export const resourceListResponseSchema = z.object({
  resources: z.array(resourceListItemSchema).readonly(),
  total: z.number().int().nonnegative(),
})

export const coverageResponseSchema = z.object({
  manifests: z.array(coverageManifestSchema).readonly(),
})

export type ResourceListItem = z.infer<typeof resourceListItemSchema>
export type ResourceDetail = z.infer<typeof resourceDetailSchema>
export type ResourceGraphResponse = z.infer<typeof resourceGraphResponseSchema>
export type ResourceListResponse = z.infer<typeof resourceListResponseSchema>
export type CoverageResponse = z.infer<typeof coverageResponseSchema>
