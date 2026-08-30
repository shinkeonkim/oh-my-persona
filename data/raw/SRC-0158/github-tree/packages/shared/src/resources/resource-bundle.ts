import { z } from "zod"
import { contentAssetSchema } from "./resource-assets"
import { certResourceRelevanceSchema } from "./resource-curriculum"
import {
  aliasTargetSchema,
  childFeatureSchema,
  edgeTypeSchema,
  resourceEdgeSchema,
} from "./resource-relations"
import { canonicalResourceSchema } from "./resource-root"

export const resourceBundleSchema = z
  .object({
    resources: z.array(canonicalResourceSchema).readonly(),
    features: z.array(childFeatureSchema).readonly(),
    aliases: z.array(aliasTargetSchema).readonly(),
    edges: z.array(resourceEdgeSchema).readonly(),
    assets: z.array(contentAssetSchema).readonly(),
    certRelevance: z.array(certResourceRelevanceSchema).readonly(),
  })
  .check(
    z.refine((bundle) => {
      const slugs = bundle.resources.map((r) => r.slug)
      return new Set(slugs).size === slugs.length
    }, "Duplicate canonical resource slugs detected"),
  )
  .check(
    z.refine((bundle) => {
      const aliasSlugs = bundle.aliases.map((a) => a.alias)
      const resourceSlugs = new Set(bundle.resources.map((r) => r.slug))
      return aliasSlugs.every((alias) => !resourceSlugs.has(alias))
    }, "Alias slug collides with a canonical resource slug"),
  )
  .check(
    z.refine((bundle) => {
      const aliasSlugs = bundle.aliases.map((a) => a.alias)
      return new Set(aliasSlugs).size === aliasSlugs.length
    }, "Duplicate alias slugs detected"),
  )
  .check(
    z.refine((bundle) => {
      const featureSlugs = bundle.features.map((feature) => feature.slug)
      return new Set(featureSlugs).size === featureSlugs.length
    }, "Duplicate child feature slugs detected"),
  )
  .check(
    z.refine((bundle) => {
      const resourceSlugs = new Set(bundle.resources.map((resource) => resource.slug))
      return bundle.features.every((feature) => !resourceSlugs.has(feature.slug))
    }, "Child feature slug collides with a canonical resource slug"),
  )
  .check(
    z.refine((bundle) => {
      const featureSlugs = new Set(bundle.features.map((feature) => feature.slug))
      return bundle.aliases.every((alias) => !featureSlugs.has(alias.alias))
    }, "Alias slug collides with a child feature slug"),
  )
  .check(
    z.refine((bundle) => {
      const knownSlugs = new Set(bundle.resources.map((r) => r.slug))
      return bundle.resources.every((r) =>
        r.prerequisites.every((prereq) => knownSlugs.has(prereq)),
      )
    }, "Dangling prerequisite: references a non-existent resource slug"),
  )
  .check(
    z.refine((bundle) => {
      const knownSlugs = new Set(bundle.resources.map((r) => r.slug))
      return bundle.edges.every((e) => knownSlugs.has(e.from) && knownSlugs.has(e.to))
    }, "Dangling edge endpoint: references a non-existent resource slug"),
  )
  .check(
    z.refine((bundle) => {
      const knownSlugs = new Set(bundle.resources.map((r) => r.slug))
      return bundle.features.every((f) => knownSlugs.has(f.parentSlug))
    }, "Child feature references a non-existent parent resource slug"),
  )
  .check(
    z.refine((bundle) => {
      const knownSlugs = new Set(bundle.resources.map((r) => r.slug))
      return bundle.aliases.every((a) => knownSlugs.has(a.canonicalSlug))
    }, "Alias references a non-existent canonical resource slug"),
  )
  .check(
    z.refine((bundle) => {
      const knownSlugs = new Set(bundle.resources.map((r) => r.slug))
      return bundle.assets.every((a) => knownSlugs.has(a.resourceSlug))
    }, "Asset references a non-existent resource slug"),
  )
  .check(
    z.refine((bundle) => {
      return bundle.edges.every((e) => edgeTypeSchema.safeParse(e.type).success)
    }, "Invalid edge type"),
  )
  .check(
    z.refine((bundle) => {
      const canonicalSlugs = new Set(bundle.resources.map((r) => r.slug))
      return bundle.certRelevance.every((cr) => canonicalSlugs.has(cr.resourceSlug))
    }, "certRelevance.resourceSlug must reference a canonical resource, not a feature or alias"),
  )

export type ResourceBundle = z.infer<typeof resourceBundleSchema>
